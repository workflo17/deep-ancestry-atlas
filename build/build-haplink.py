# Link each ancient genome to its deepest clade in each tree, so the page can
# filter the evidence layer down to the carriers of a selected lineage.
# Emits out/genomes_hap.bin.txt: per genome, int16 Y node index and int16 mtDNA
# node index into the FULL tree arrays (-1 where no usable call survives).
# Uses the same janno order and filter as build-layers.py, so the arrays align.
# Run after build-tree.py, from this directory.
import csv,json,re,struct,base64,sys,os
csv.field_size_limit(10**8)
os.makedirs('out',exist_ok=True)
J="clones/aadr-archive/AADR_v66_p1_1240K/AADR_v66_p1_1240K.janno"
TOK=re.compile(r"[A-Za-z]+|\d+(?:'\d+)*")

def path(h):
    """Tokenised ancestry of a haplogroup name. Letter/digit alternation matters:
    H11's ancestors are H and H11, NOT H1 - a plain startswith() gets that wrong."""
    h=(h or '').split('+')[0].split('@')[0].strip().rstrip('~').rstrip('*')
    if not h: return []
    out=[];cur=''
    for t in TOK.findall(h): cur+=t; out.append(cur)
    return out

def num(v):
    try:
        f=float(v); return f if f==f else None
    except: return None

def cleanh(v):
    v=(v or '').strip()
    return '' if (not v or v.lower().startswith('n/a') or v in ('..','.','nan','NA')) else v

idx={}
for m in ('y','mt'):
    t=json.load(open(f'out/tree_{m}.json'))
    idx[m]={d['id']:i for i,d in enumerate(t)}

buf=bytearray(); n=0; hit={'y':0,'mt':0}
for r in csv.DictReader(open(J,encoding='utf-8'),delimiter='\t'):
    bp=num(r.get('AADR_Date_Mean_BP')); la=num(r.get('Latitude')); lo=num(r.get('Longitude'))
    if not bp or bp<=0 or la is None or lo is None: continue
    if not(-90<=la<=90 and -180<=lo<=180): continue
    out=[]
    for m,col in (('y','AADR_Y_Haplogroup_ISOGG'),('mt','AADR_mtDNA_Haplogroup')):
        best=-1
        for node in path(cleanh(r.get(col))):   # deepest clade that survived the tree cut
            if node in idx[m]: best=idx[m][node]
        out.append(best)
        if best>=0: hit[m]+=1
    buf+=struct.pack('<hh',out[0],out[1]); n+=1

open('out/genomes_hap.bin.txt','w').write(base64.b64encode(bytes(buf)).decode())
print(f"{n} genomes | placed: Y {hit['y']} ({100*hit['y']/n:.1f}%) "
      f"mt {hit['mt']} ({100*hit['mt']/n:.1f}%)",file=sys.stderr)
