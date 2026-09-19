# Build every evidence layer the atlas renders, from the sources
# fetch-sources.sh downloads. Run after build-tree.py, from this directory.
# Emits out/*.bin.txt (base64 packed points/lines), out/*.txt (metadata
# sidecars) and out/manifest.json. Copy out/ to the page's d/ directory.
import csv,json,math,re,struct,collections,sys,os
csv.field_size_limit(10**8)
OUT="out"
def num(v):
    try:
        f=float(v); return f if f==f else None
    except: return None
def w(name,b):
    # Artifact hosting serves no application/octet-stream, so binary payloads
    # ship base64-encoded in .txt and are decoded with atob() in the page.
    enc=base64.b64encode(b).decode()
    open(os.path.join(OUT,name+'.txt'),'w').write(enc); return len(enc)
def wt(name,s):
    open(os.path.join(OUT,name),'w',encoding='utf-8').write(s); return len(s.encode())
def esc(s): return (s or '').replace('\t',' ').replace('\n',' ').replace('\r',' ').strip()
def demojibake(s):
    # p3k14c site names come out of the .rda decoded as cp1252 over UTF-8 bytes
    # ("Jedrzychowice" -> "J\u00c4\u2122drzychowice"). Round-trip repairs them.
    if not isinstance(s,str): return s
    try: return s.encode('cp1252').decode('utf-8')
    except (UnicodeEncodeError,UnicodeDecodeError): return s

REC=struct.Struct('<iiiHB')         # lat*1e5, lon*1e5, BP, uncertainty, flags  = 15 bytes
def pack_points(recs):
    b=bytearray()
    for la,lo,bp,u,f in recs:
        b+=REC.pack(max(-9000000,min(9000000,round(la*1e5))),
                    max(-18000000,min(18000000,round(lo*1e5))),
                    max(-2000000000,min(2000000000,int(bp))),
                    min(65535,max(0,int(u))), f&0xFF)
    return bytes(b)

man={}
def note(key,**kw): man[key]=kw

# ---------------- 1. ancient genomes (AADR v66 via Poseidon) ----------------
J="clones/aadr-archive/AADR_v66_p1_1240K/AADR_v66_p1_1240K.janno"
ASMT={'Pass':0,'PROVISIONAL_PASS':1,'MERGE_PASS':1,'Questionable':2,'CRITICAL':3}
def cleanh(v):
    v=(v or '').strip()
    return '' if (not v or v.lower().startswith('n/a') or v in ('..','.','nan','NA')) else v
g_recs=[];g_txt=[]
for r in csv.DictReader(open(J,encoding='utf-8'),delimiter='\t'):
    bp=num(r.get('AADR_Date_Mean_BP')); la=num(r.get('Latitude')); lo=num(r.get('Longitude'))
    if not bp or bp<=0 or la is None or lo is None: continue
    if not(-90<=la<=90 and -180<=lo<=180): continue
    y=cleanh(r.get('AADR_Y_Haplogroup_ISOGG')); mt=cleanh(r.get('AADR_mtDNA_Haplogroup'))
    f=(1 if r.get('Date_Type')=='C14' else 0) | (ASMT.get((r.get('AADR_Assessment') or '').strip(),2)<<1) \
      | (4 if y else 0)<<1 | 0
    f=(1 if r.get('Date_Type')=='C14' else 0) | (ASMT.get((r.get('AADR_Assessment') or '').strip(),2)<<1) \
      | (8 if y else 0) | (16 if mt else 0)
    g_recs.append((la,lo,round(bp),round(num(r.get('AADR_Date_SD')) or 0),f))
    g_txt.append("\t".join(esc(x) for x in [r.get('Poseidon_ID'),r.get('AADR_Group_ID') or r.get('Group_Name'),
        r.get('AADR_Locality'),r.get('AADR_Political_Entity'),y,mt,r.get('AADR_Publication'),r.get('AADR_Publication_DOI')]))
nb=w('genomes.bin',pack_points(g_recs)); nt=wt('genomes.txt',"\n".join(g_txt))
note('genomes',n=len(g_recs),bin=nb,txt=nt,name='Ancient genomes',
     source='Allen Ancient DNA Resource v66 (via Poseidon aadr-archive)',license='see AADR terms; cite release DOI',
     url='https://doi.org/10.7910/DVN/FFIDCW',
     fields=['poseidon_id','group_id','locality','polity','y_haplogroup','mt_haplogroup','publication','doi'])
print(f"genomes {len(g_recs)}  bin={nb/1e6:.2f}MB txt={nt/1e6:.2f}MB",file=sys.stderr)

# ---------------- 2. radiocarbon (p3k14c) ----------------
import pyreadr
df=pyreadr.read_r('raw/p3k14c_data.rda')['p3k14c_data']
c_recs=[];c_txt=[]
for t in df.itertuples(index=False):
    la=num(t.Lat); lo=num(t.Long); age=num(t.Age); err=num(t.Error)
    if la is None or lo is None or age is None: continue
    if not(-90<=la<=90 and -180<=lo<=180): continue
    acc=num(t.LocAccuracy); acc=0 if acc is None else int(max(0,min(9,acc)))
    c_recs.append((la,lo,round(age),round(err or 0),acc))
    c_txt.append("\t".join(esc(demojibake(str(x))) if x==x and x is not None else '' for x in
        [t.LabID,t.SiteName,t.Country,t.Continent,t.Material,t.Source]))
nb=w('c14.bin',pack_points(c_recs)); nt=wt('c14.txt',"\n".join(c_txt))
note('c14',n=len(c_recs),bin=nb,txt=nt,name='Radiocarbon dates',
     source='p3k14c (PEOPLE 3000)',license='see tDAR collection',
     url='https://doi.org/10.48512/XCV8459173',
     fields=['lab_id','site_name','country','continent','material','source_db'])
print(f"c14 {len(c_recs)}  bin={nb/1e6:.2f}MB txt={nt/1e6:.2f}MB",file=sys.stderr)

# ---------------- 3. ancient places (Pleiades) ----------------
types=collections.defaultdict(set)
for r in csv.DictReader(open('raw/pl_places_place_types.csv',newline='',encoding='utf-8-sig')):
    types[r['place_id']].add(r['place_type'])
CLASSES=[("settlement",{"settlement","settlement-modern","city-wall","urban"}),
 ("sacred",{"temple","temple-2","sanctuary","church","church-2","abbey","abbey-church","synagogue","mosque","shrine","oracle","altar","monastery"}),
 ("military",{"fort","fort-2","fortress","tower","wall","camp","military-installation"}),
 ("funerary",{"cemetery","tomb","tumulus","mausoleum","necropolis","catacomb"}),
 ("infrastructure",{"road","bridge","station","aqueduct","port","harbor","canal","mine","quarry","lighthouse","dam","well","kiln","production"}),
 ("other site",{"archaeological-site","villa","ruin","find-spot","estate","bath","theatre","amphitheatre","circus","stadium","forum","agora","market","palace"})]
SKIP={"unlocated","label","unlabeled","people","region","province","ethnos"}
p_recs=[];p_txt=[]
for r in csv.DictReader(open('raw/pl_places.csv',newline='',encoding='utf-8-sig')):
    la=num(r.get('representative_latitude')); lo=num(r.get('representative_longitude'))
    if la is None or lo is None or not(-90<=la<=90 and -180<=lo<=180): continue
    ts=types.get(r['id'],set()); cls=None
    for i,(nm,s) in enumerate(CLASSES):
        if ts&s: cls=i;break
    if cls is None: cls=5 if (ts-SKIP) else None
    if cls is None: continue
    prec=(r.get('location_precision') or '').strip()
    if prec=='unlocated': continue
    p_recs.append((la,lo,0,0,cls|(8 if prec=='rough' else 0)))
    p_txt.append(esc(r['id'])+"\t"+esc(r.get('title')))
nb=w('places.bin',pack_points(p_recs)); nt=wt('places.txt',"\n".join(p_txt))
note('places',n=len(p_recs),bin=nb,txt=nt,name='Ancient places',
     source='Pleiades gazetteer v4.1',license='CC BY 3.0',url='https://pleiades.stoa.org/downloads',
     classes=[c[0] for c in CLASSES],fields=['pleiades_id','title'])
print(f"places {len(p_recs)}  bin={nb/1e6:.2f}MB txt={nt/1e6:.2f}MB",file=sys.stderr)

# ---------------- 4. languages (Glottolog) ----------------
LVL={'language':0,'family':1,'dialect':2}
l_recs=[];l_txt=[]
for r in csv.DictReader(open('raw/glottolog.csv',encoding='utf-8')):
    la=num(r.get('Latitude')); lo=num(r.get('Longitude'))
    if la is None or lo is None: continue
    lv=LVL.get(r.get('Level',''),2)
    l_recs.append((la,lo,0,0,lv))
    l_txt.append("\t".join(esc(x) for x in [r.get('Glottocode'),r.get('Name'),r.get('Macroarea'),r.get('Family_ID'),r.get('ISO639P3code')]))
nb=w('lang.bin',pack_points(l_recs)); nt=wt('lang.txt',"\n".join(l_txt))
note('lang',n=len(l_recs),bin=nb,txt=nt,name='Languages',source='Glottolog (CLDF)',license='CC BY 4.0',
     url='https://glottolog.org',classes=['language','family','dialect'],
     fields=['glottocode','name','macroarea','family_id','iso639p3'])
print(f"lang {len(l_recs)}  bin={nb/1e6:.2f}MB txt={nt/1e6:.2f}MB",file=sys.stderr)

# ---------------- 5. societies (D-PLACE EA) ----------------
s_recs=[];s_txt=[]
for r in csv.DictReader(open('raw/dplace_soc.csv',encoding='utf-8')):
    la=num(r.get('Lat')); lo=num(r.get('Long'))
    if la is None or lo is None: continue
    yr=num(r.get('main_focal_year'))
    bp=round(1950-yr) if yr else 0
    s_recs.append((la,lo,max(0,bp),0,0))
    s_txt.append("\t".join(esc(x) for x in [r.get('id'),r.get('pref_name_for_society'),r.get('glottocode'),r.get('main_focal_year')]))
nb=w('soc.bin',pack_points(s_recs)); nt=wt('soc.txt',"\n".join(s_txt))
note('soc',n=len(s_recs),bin=nb,txt=nt,name='Documented societies',source='D-PLACE (Ethnographic Atlas)',
     license='CC BY 4.0',url='https://d-place.org',fields=['society_id','name','glottocode','focal_year'])
print(f"soc {len(s_recs)}  bin={nb/1e6:.2f}MB txt={nt/1e6:.2f}MB",file=sys.stderr)

# ---------------- 6. ancient pathogens / metagenomes ----------------
CT={}
a_recs=[];a_txt=[]
for fn,kind in (('raw/amd_host.tsv',0),('raw/amd_env.tsv',1),('raw/amd_single.tsv',2)):
    if not os.path.exists(fn): continue
    for r in csv.DictReader(open(fn,encoding='utf-8'),delimiter='\t'):
        la=num(r.get('latitude')); lo=num(r.get('longitude'))
        if la is None or lo is None or not(-90<=la<=90 and -180<=lo<=180): continue
        age=num(r.get('sample_age')) or 0
        a_recs.append((la,lo,round(age),0,kind))
        a_txt.append("\t".join(esc(x) for x in [r.get('sample_name'),r.get('site_name'),r.get('geo_loc_name'),
            r.get('community_type') or r.get('sample_host'),r.get('project_name'),r.get('publication_doi')]))
nb=w('patho.bin',pack_points(a_recs)); nt=wt('patho.txt',"\n".join(a_txt))
note('patho',n=len(a_recs),bin=nb,txt=nt,name='Ancient metagenomes',source='AncientMetagenomeDir (SPAAM)',
     license='CC BY 4.0',url='https://github.com/SPAAM-community/AncientMetagenomeDir',
     classes=['host-associated','environmental','single-genome'],
     fields=['sample','site','location','type','project','doi'])
print(f"patho {len(a_recs)}  bin={nb/1e6:.2f}MB txt={nt/1e6:.2f}MB",file=sys.stderr)

# ---------------- 7. routes: roads, canals, aqueducts, walls (AWMC) ----------------
LINE=[('roads',0),('canals',1),('aqueducts',2),('walls',3)]
b=bytearray(); nlines=0; names=[]
for nm,cls in LINE:
    p=f"clones/awmc-geodata/Cultural-Data/{nm}/{nm}.geojson"
    if not os.path.exists(p): continue
    d=json.load(open(p,encoding='utf-8'))
    for f in d['features']:
        pr=f.get('properties',{}) or {}
        known=1 if str(pr.get('Known_or_a','')).strip() in ('1','Known','known') else 0
        geom=f['geometry']['coordinates']
        if f['geometry']['type']=='LineString': geom=[geom]
        for ls in geom:
            pts=[(x[1],x[0]) for x in ls if len(x)>=2 and -90<=x[1]<=90 and -180<=x[0]<=180]
            if len(pts)<2: continue
            if len(pts)>4000: pts=pts[:4000]
            b+=struct.pack('<HBB',len(pts),cls,known)
            for la,lo in pts: b+=struct.pack('<ii',round(la*1e5),round(lo*1e5))
            nlines+=1
            names.append(esc(pr.get('Name') or pr.get('en_name') or ''))
out=struct.pack('<I',nlines)+bytes(b)
nb=w('routes.bin',out); nt=wt('routes.txt',"\n".join(names))
note('routes',n=nlines,bin=nb,txt=nt,name='Roads & routes',source='Ancient World Mapping Center (Barrington Atlas derived)',
     license='ODbL 1.0',url='https://github.com/AWMC/geodata',classes=['road','canal','aqueduct','wall'],
     fields=['name'])
print(f"routes {nlines} polylines  bin={nb/1e6:.2f}MB",file=sys.stderr)

# ---------------- trees + manifest ----------------
for m in ('y','mt'):
    src=json.load(open(f'out/tree_{m}.json'))
    wt(f'tree_{m}.json',json.dumps(src,separators=(',',':')))
    note(f'tree_{m}',n=len(src),name=f'{"Y-DNA" if m=="y" else "mtDNA"} observed clades',
         source='derived from AADR v66 haplogroup calls')
man['_built']={'aadr':'v66_p1_1240K','pleiades':'v4.1','glottolog':'CLDF master','p3k14c':'179,689 raw',
               'note':'node positions are spherical centroids of member samples; node dates are OLDEST OBSERVED sample, not TMRCA'}
wt('manifest.json',json.dumps(man,separators=(',',':')))
tot=sum(os.path.getsize(os.path.join(OUT,f)) for f in os.listdir(OUT))
print(f"\nTOTAL {tot/1e6:.2f} MB across {len(os.listdir(OUT))} files",file=sys.stderr)
