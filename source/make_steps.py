"""Re-group mountains_v3_full.ldr into booklet steps of ~30-55 pieces (same 4,456 lines, new STEP order).
Sections and STEP ranges are written to sections.json for the kit config."""
import json, math, collections, sys
SRC='/workspace/courtyard_mountains_v5_hollow/src/v5.json'
P=json.load(open(SRC))['parts']
HID=json.load(open('/workspace/courtyard_mountains_v5_hollow/lime/lime.json'))   # pieces with no visible face (lime/hidden.py)
for i in HID: P[i]['color']=27                                               # Lime = hidden filler, any colour works
OX,OZ=-640,-480
def line(p):
    x,y,z=p['pos']; r=p['rot']; r=(-r[0],-r[1],-r[2],r[3],r[4],r[5],-r[6],-r[7],-r[8])
    return '1 %d %g %g %g %s %s.dat'%(p['color'],-(x+OX),y,-(z+OZ),' '.join('%g'%v for v in r),p['id'])
# check: same lines as the published model
orig=collections.Counter(l.strip() for l in open('/workspace/courtyard_mountains_v5_hollow/mountains_v5_hollow_lime.ldr') if l.startswith('1 '))
mine=collections.Counter(line(p) for p in P); assert orig==mine, 'line mismatch'
def cen(p): b=p['body'][0]; return ((b[0]+b[3])/2,(b[1]+b[4])/2,(b[2]+b[5])/2)
def cell(p): x,_,z=cen(p); return (63-int(x//20), int(z//20))      # plan coords: px to the viewer's right, z from the back
def layer(p): return int((-24-p['body'][0][4]+0.1)//24)             # v4: first mountain course sits at -24 (no plate layer)
C={(px,z) for px in range(21,37) for z in range(14,26)}
PEAKS=[('left peaks',1.5,36.5),('left peaks',6.0,28.5),('left of the niche',16.5,17.5),('right of the niche',38.0,16.5),("right peak, behind Jack's house",58.5,18.0)]
REG=['left peaks','left of the niche','niche and spiral platform','right of the niche',"right peak, behind Jack's house"]
def region(p):
    c=cell(p)
    if c in C: return 'niche and spiral platform'
    return min(PEAKS,key=lambda k:math.hypot(c[0]-k[1],c[1]-k[2]))[0]
def bottom(p): return -p['body'][0][1]
def sweep(ps):  # lower pieces first, then left to right in 4-stud bands, back to front
    return sorted(ps,key=lambda p:(round(bottom(p)),cell(p)[0]//4,cell(p)[1],cell(p)[0]))
role=lambda p:p['role']
steps=[]   # (section, title, pieces)
def add(sec,title,ps): steps.append((sec,title,ps))
S1='Foundation: Technic bricks and pins'; S2='Snow, road and anchors'; S3='Courtyard paving'
bricks={tuple(int(v) for v in p['role'].split('(')[1].rstrip(')').split(',')):p for p in P if p['id']=='65803'}
pins=[p for p in P if p['id']=='2780']
def owner(pin):   # the brick the pin sticks out of, towards the camera (left / front side)
    (a,_,b),ax=pin['pinends'][0]
    return (int(a//320),int(b//320))
for p in pins: assert owner(p) in bricks
nI=max(i for i,j in bricks)+1; nJ=max(j for i,j in bricks)+1
ROW=['back','middle','front']
for j in range(nJ):
    for i in range(nI):
        mine=[p for p in pins if owner(p)==(i,j)]
        side=[p for p in mine if p['pinends'][0][1]=='x']; front=[p for p in mine if p['pinends'][0][1]=='z']
        what=[]
        if side: what.append(f'{len(side)} pins in its left side')
        if front: what.append(f'{len(front)} pins in its front edge')
        t=f'{ROW[j].capitalize()} row, brick {i+1} of {nI} (from the right)' + (': '+' and '.join(what) if what else '')
        if j>0 and i==0: t=f'{ROW[j].capitalize()} row (put it together next to the base): brick 1 of {nI}' + (': '+' and '.join(what) if what else '')
        if j>0 and i==nI-1: t+=f'. Then push the whole {ROW[j]} row onto the pins along the front of the {ROW[j-1]} row'
        add(S1,t,[bricks[(i,j)]]+sorted(side,key=lambda p:p['pos'][2])+sorted(front,key=lambda p:p['pos'][0]))
l2=sweep([p for p in P if role(p).startswith('L2 reserved') or (role(p).startswith('hollow') and layer(p)<0)])
third=lambda p:min(2,int((63-cell(p)[0])/64*3))
for i,n in enumerate(['left','middle','right']):
    add(S2,f'Plates on top of the Technic bricks: {n} part',[p for p in l2 if third(p)==2-i])
add(S2,'Snow strip plates',sweep([p for p in P if role(p)=='L2 snow']))
add(S2,'Road plates and road tiles',sweep([p for p in P if role(p).startswith('road')]))
add(S2,'Side-stud anchor bricks for the paving',sweep([p for p in P if role(p).startswith('anchor')]))
pav=[p for p in P if role(p).startswith('paver')]
# pavers hang on each other sideways (studs to the front): place each column of pavers back to front from its anchor
for i,n in enumerate(['left','middle','right']):
    ps=[p for p in pav if third(p)==2-i]
    add(S3,f'Sideways paving: {n} part',sorted(ps,key=lambda p:(cen(p)[2],cen(p)[0])))
mtn=[p for p in P if not (role(p).startswith('hollow') and layer(p)<0) and not any(role(p).startswith(r) for r in ('65803','Technic pin','baseplate','L1','L2','road','anchor','paver','SPIRAL'))]
by=collections.defaultdict(list)
for p in mtn: by[layer(p)].append(p)
BANDS=[(0,4,'Mountains: layers 1-4'),(4,8,'Mountains: layers 5-8'),(8,12,'Mountains: layers 9-12'),(12,16,'Mountains: layers 13-16, niche span and spiral platform'),(16,30,'Mountains: layers 17-25, the peaks')]
def band(n): return next(t for a,b,t in BANDS if a<=n<b)
top=max(by)
NC=min(layer(p) for p in P if role(p).startswith('niche ceiling'))
for n in sorted(by):
    if n>=top-2:      # the last few summit layers are tiny: one step
        if n==top-2: add(band(n),f'Layers {n+1}-{top+1}: the summits',sweep([p for m in range(n,top+1) for p in by[m]]))
        continue
    ps=by[n]
    if len(ps)<=60: add(band(n),f'Layer {n+1}: all peaks',sweep(ps)); continue
    g=collections.OrderedDict((r,[]) for r in REG)
    for p in ps: g[region(p)].append(p)
    rs=[r for r in REG if g[r]]
    keep=lambda r: r=='niche and spiral platform' and (any(role(p).startswith('niche ceiling') for p in g[r]) or n>NC)
    for r in list(rs):
        if len(g[r])<12 and len(rs)>1 and not keep(r):
            i=rs.index(r); nb=rs[i-1] if i>0 else rs[i+1]; g[nb]+=g[r]; g[r]=[]; rs.remove(r)
    for r in rs:
        t=f'Layer {n+1}: {r}'
        if r=='niche and spiral platform':
            if any(role(p).startswith('niche ceiling') for p in g[r]): t=f'Layer {n+1}: niche span (ceiling plates over the toy shop niche)'
            elif n<NC: t=f'Layer {n+1}: walls of the toy shop niche'
            else: t=f'Layer {n+1}: spiral platform'
        add(band(n),t,sweep(g[r]))
sp=[p for p in P if role(p).startswith('SPIRAL')]
add(band(16),'Spiral placeholder (tan marker, not a part to buy)',sp)
assert sum(len(s[2]) for s in steps)==len(P)
# ---- buildability: every piece must connect (studs) to something already placed, or to its own step ----
anti={}
for i,p in enumerate(P):
    for pt,d in p['anti']: anti[(tuple(round(v,2) for v in pt),d)]=i
OPP={'-y':'+y','+y':'-y','+z':'-z','-z':'+z','+x':'-x','-x':'+x'}
E=collections.defaultdict(set)
for i,p in enumerate(P):
    for pt,d in p['studs']:
        k=(tuple(round(v,2) for v in pt),OPP[d])
        if k in anti: E[i].add(anti[k]); E[anti[k]].add(i)
hole={}
for i,p in enumerate(P):
    for pt,ax in p.get('holes',[]): hole[(tuple(round(v,2) for v in pt),ax)]=i
for i,p in enumerate(P):
    for pt,ax in p.get('pinends',[]):
        k=(tuple(round(v,2) for v in pt),ax)
        if k in hole: E[i].add(hole[k]); E[hole[k]].add(i)
idx={id(p):i for i,p in enumerate(P)}
def check():
    stepof={}
    for k,(sec,t,ps) in enumerate(steps):
        for p in ps: stepof[idx[id(p)]]=k
    placed=set(); bad=[]
    for k,(sec,t,ps) in enumerate(steps):
        ids={idx[id(p)] for p in ps}
        if not placed: placed|=ids; continue
        ok=set(); grow=True
        while grow:
            grow=False
            for i in ids-ok:
                if E[i]&(placed|ok): ok.add(i); grow=True
        bad+= [(i,k) for i in ids-ok]
        placed|=ids
    return bad,stepof
for it in range(10):
    bad,stepof=check()
    if not bad: break
    for i,k in bad:
        later=[stepof[j] for j in E[i] if stepof[j]>k]
        if not later: continue
        to=min(later); p=P[i]
        steps[k][2].remove(p); steps[to][2].append(p)
    print('moved',len(bad),'pieces to the step that holds them')
bad,_=check(); print('pieces not connected when placed:',len(bad))
steps=[s_ for s_ in steps if s_[2]]
# ---- write ----
L=['0 Nightmare Before Christmas display: 64x48 on 12 Technic 16x16 bricks, courtyard and mountains (v5, hollow)','0 Name: nbc_display_v5_steps.ldr','0 Author: Grok Bot for Jason',
   '0 // Same 4,789 parts as mountains_v5_hollow_lime.ldr (mountains_v5_hollow_full.ldr with hidden pieces in Lime), regrouped into booklet steps.']
secs=[]; k=0
for sec,t,ps in steps:
    k+=1
    if not secs or secs[-1]['name']!=sec: secs.append(dict(name=sec,steps=[k,k]))
    secs[-1]['steps'][1]=k
    L.append('0 // '+t)
    for p in ps:
        if role(p).startswith('SPIRAL'): L.append('0 !MOCKIT NAME Spiral placeholder (tan 6 x 6 plate): not a part to buy')
        L.append(line(p))
    L.append('0 STEP')
open('/workspace/courtyard_mountains_v5_hollow/instr/nbc_display_v5_steps.ldr','w').write('\n'.join(L)+'\n')
json.dump(secs,open('/workspace/courtyard_mountains_v5_hollow/instr/sections.json','w'),indent=1)
sizes=[len(s[2]) for s in steps]
print(len(steps),'steps in',len(secs),'sections; sizes min/max',min(sizes),max(sizes))
for s in secs: print(s)
for sec,t,ps in steps: print(f'{len(ps):4d} {t}')
