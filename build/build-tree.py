# Derive Y-DNA and mtDNA clade trees from AADR v66 haplogroup calls.
# Nomenclature IS the topology: 'R1b1a1' nests inside 'R1b1' inside 'R1b'...
# A node's date is its OLDEST OBSERVED member - a lower bound, never a TMRCA.
# Run after fetch-sources.sh, from this directory.
import os; os.makedirs('out',exist_ok=True)
import csv,json,math,re,struct,base64,collections,sys
csv.field_size_limit(10**8)
J="clones/aadr-archive/AADR_v66_p1_1240K/AADR_v66_p1_1240K.janno"

def num(v):
    try: return float(v)
    except: return None
def clean(v):
    v=(v or '').strip()
    if not v or v.lower().startswith('n/a') or v in ('..','.','nan','NA'): return ''
    return v

rows=[]
for r in csv.DictReader(open(J,encoding='utf-8'),delimiter='\t'):
    bp=num(r.get('AADR_Date_Mean_BP')); la=num(r.get('Latitude')); lo=num(r.get('Longitude'))
    if not bp or bp<=0 or la is None or lo is None: continue
    if not(-90<=la<=90 and -180<=lo<=180): continue
    rows.append({
      'id':r.get('Poseidon_ID','').strip(),
      'lat':la,'lon':lo,'bp':bp,'sd':num(r.get('AADR_Date_SD')) or 0,
      'c14': 1 if r.get('Date_Type')=='C14' else 0,
      'grp':(r.get('AADR_Group_ID') or r.get('Group_Name') or '').strip(),
      'loc':(r.get('AADR_Locality') or '').strip(),
      'pol':(r.get('AADR_Political_Entity') or '').strip(),
      'y':clean(r.get('AADR_Y_Haplogroup_ISOGG')),
      'mt':clean(r.get('AADR_mtDNA_Haplogroup')),
      'pub':(r.get('AADR_Publication') or '').strip(),
      'doi':(r.get('AADR_Publication_DOI') or '').strip(),
      'asmt':(r.get('AADR_Assessment') or '').strip(),
    })
print("ancient georeferenced:",len(rows),file=sys.stderr)

TOK=re.compile(r"[A-Za-z]+|\d+(?:'\d+)*")
def path(h):
    h=h.split('+')[0].split('@')[0].strip().rstrip('~').rstrip('*')
    if not h: return []
    toks=TOK.findall(h)
    if not toks: return []
    out=[];cur=''
    for t in toks:
        cur+=t; out.append(cur)
    return out

def spherical_mean(pts):
    x=y=z=0.0
    for la,lo in pts:
        p=math.radians(la); t=math.radians(lo)
        x+=math.cos(p)*math.sin(t); y+=math.sin(p); z+=math.cos(p)*math.cos(t)
    n=len(pts); x/=n;y/=n;z/=n
    r=math.hypot(x,math.hypot(y,z))
    if r<1e-9: return (0.0,0.0)
    return (math.degrees(math.asin(y/r)), math.degrees(math.atan2(x/r,z/r)))

def build(marker, minn, maxnodes):
    sub=collections.defaultdict(list)          # node -> sample indices
    for i,r in enumerate(rows):
        p=path(r[marker])
        for node in p: sub[node].append(i)
    keep={k:v for k,v in sub.items() if len(v)>=minn}
    # cap by subtree size, keeping all ancestors of anything kept
    if len(keep)>maxnodes:
        ranked=sorted(keep.items(),key=lambda kv:-len(kv[1]))[:maxnodes]
        keep=dict(ranked)
        for k in list(keep):
            for i in range(1,len(k)):
                pre=k[:i]
                if pre in sub and pre not in keep: keep[pre]=sub[pre]
    def parent_of(k):
        for i in range(len(k)-1,0,-1):
            if k[:i] in keep: return k[:i]
        return None
    out=[]
    for k,idxs in keep.items():
        pts=[(rows[i]['lat'],rows[i]['lon']) for i in idxs]
        clat,clon=spherical_mean(pts)
        oi=max(idxs,key=lambda i:rows[i]['bp'])
        out.append({'id':k,'parent':parent_of(k),'n':len(idxs),
                    'bp':round(rows[oi]['bp']),
                    'clat':round(clat,3),'clon':round(clon,3),
                    'olat':round(rows[oi]['lat'],3),'olon':round(rows[oi]['lon'],3),
                    'ogrp':rows[oi]['grp'],'oid':rows[oi]['id']})
    out.sort(key=lambda d:(len(d['id']),d['id']))
    return out

for marker,minn,cap in (('y',4,700),('mt',4,700)):
    t=build(marker,minn,cap)
    roots=[n for n in t if not n['parent']]
    print(f"{marker}: nodes={len(t)} roots={len(roots)} ({[r['id'] for r in roots][:14]})",file=sys.stderr)
    big=sorted(t,key=lambda d:-d['n'])[:6]
    for n in big: print(f"   {n['id']:12s} n={n['n']:5d} oldest={n['bp']:7.0f}BP centroid=({n['clat']:.1f},{n['clon']:.1f})",file=sys.stderr)
    json.dump(t,open(f'out/tree_{marker}.json','w'),separators=(',',':'))
json.dump({'n':len(rows)},open('out/aadr_count.json','w'))
