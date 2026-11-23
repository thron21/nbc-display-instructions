import sys,json,numpy as np,collections,random
sys.path.insert(0,'/home/claude/thron21/moc-instruction-kit')
from mockit import ldraw
random.seed(7)
lib=ldraw.Library('lib'); t,P=ldraw.read_model('v4.ldr',lib)
V=json.load(open('vis_v4.json')); V={n:{int(k):v for k,v in d.items()} for n,d in V.items()}
B=[lib.bbox(p) for p in P]
S=2
def topfrac(i):
    lo,hi=B[i]; area=max(1,(hi[0]-lo[0])*(hi[2]-lo[2])*S*S)
    return V['top'].get(i,0)/area
def anyvis(i): return sum(V[n].get(i,0) for n in V)
lines=open('v4.ldr').read().split('\n')
def setcol(i,c):
    ln=int(P[i]['src'].rsplit(':',1)[1])-1
    tk=lines[ln].split(' '); assert tk[0]=='1'; tk[1]=str(c); lines[ln]=' '.join(tk)
    P[i]['color']=c
ANG={136,139,142,161,162,180,197,213,216,4568}
grey=lambda: 72 if random.random()<0.6 else 71
ch=collections.Counter()
for i,p in enumerate(P):
    st=p['step']; c=p['color']
    if st>=21:   # mountains
        h=-B[i][0][1]; tf=topfrac(i)
        if c==15:
            if tf<0.3: setcol(i,grey()); ch['white side->grey']+=1
            else:
                keep=0.9 if h>=200 else 0.55 if h>=100 else 0.3
                if random.random()>keep: setcol(i,grey()); ch['white low ledge->grey']+=1
        elif c==0 and anyvis(i)>0 and random.random()<0.5: setcol(i,72); ch['black->dark grey']+=1
    if 18<=st<21 and p['part'] in ('98283','3005') and c in (320,70,71,72):   # courtyard pavers
        r=random.random(); n=71 if r<0.5 else 72 if r<0.87 else 320 if r<0.97 else 70
        if n!=c: setcol(i,n); ch['paver recolour']+=1
    if c==27 and (anyvis(i)>40 or i in ANG):
        n=15 if st<18 else 72
        setcol(i,n); ch[f'visible lime->{n}']+=1
open('v4_recol.ldr','w').write('\n'.join(lines))
print(dict(ch))
cnt=lambda Q:collections.Counter(p['color'] for p in Q)
print('colours now',cnt(P))
