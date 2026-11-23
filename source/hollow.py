"""v5: hollow the hidden interior of v4. Visible pieces stay exactly as they are; hidden mountain / reserved-layer bricks are
removed and replaced by the minimum lime-coloured support (pillars of the largest brick that fits, 2x4 max), plus tie beams."""
import json, collections, itertools
P4=json.load(open('/workspace/courtyard_mountains_v4/src/v4.json'))['parts']
HID=set(json.load(open('/workspace/courtyard_mountains_v4/lime/hidden.json')))
REMOVABLE=lambda p:p['role'].startswith('mountain brick') or p['role'].startswith('L2 reserved')
removed=[i for i in HID if REMOVABLE(P4[i])]
assert all(P4[i]['id'] in ('3001','3002','3003','3010','3622','3004','3005') for i in removed)
fixed=[p for i,p in enumerate(P4) if i not in set(removed)]
def lay_of_bottom(y): return int(round((-24-y)/24))           # brick whose bottom is at y sits in layer n
def cells(p):
    b=p['body'][0]; return [(x,z) for x in range(int(b[0]//20),int(round(b[3]))//20) for z in range(int(b[2]//20),int(round(b[5]))//20)]
avail=collections.defaultdict(set)
for i in removed:
    p=P4[i]; n=lay_of_bottom(p['body'][0][4]); avail[n]|=set(cells(p))
# enlarge the free space to every 1x1x1-brick cell that is completely empty enclosed air (voxel flood fill as in lime/hidden.py)
import numpy as np
from scipy import ndimage
V=4; X0,Y0,Z0=-8,-624,-8; NX,NY,NZ=(1280+16)//V,(32+624+8)//V,(960+16)//V
OCC=np.zeros((NX,NY,NZ),bool); COV=np.zeros((NX,NY,NZ),bool)
SLOPE=('cap ','snow curved','snow drift','rock face sideways cheese')
def sl(b): x0,y0,z0,x1,y1,z1=[int(round(v)) for v in b]; return (slice((x0-X0)//V,(x1-X0)//V),slice((y0-Y0)//V,(y1-Y0)//V),slice((z0-Z0)//V,(z1-Z0)//V))
for p in fixed:
    if p['id']=='2780': continue
    b=list(p['body'][0]); OCC[sl(b)]=True
    if p['role'].startswith(SLOPE):
        r=p['rot']; d=(r[1],r[4],r[7]); k=[q for q in range(3) if d[q]][0]
        if d[k]>0: b[k]=b[k+3]-V
        else: b[k+3]=b[k]+V
    COV[sl(b)]=True
lab,_=ndimage.label(~COV); OUT=lab==lab[0,0,0]
FREE=~OCC & ~OUT
extra=0
for n in range(-1,25):
    y1=-24-24*n; y0=y1-24
    for x in range(64):
        for z in range(48):
            if (x,z) in avail[n]: continue
            if FREE[sl((20*x,y0,20*z,20*x+20,y1,20*z+20))].all(): avail[n].add((x,z)); extra+=1
print('extra enclosed cells usable',extra)
WALL=collections.defaultdict(set)    # cells occupied at layer n by fixed bricks/plates (full-height course pieces)
for p in fixed:
    b=p['body'][0]
    if p['id'] in ('65803','2780'): continue
    if abs((b[4]-b[1])-24)<0.1 and lay_of_bottom(b[4])>=-1 and not p['role'].startswith('rock face sideways') and not p['role'].startswith('paver'):
        WALL[lay_of_bottom(b[4])]|=set(cells(p))
stud=collections.defaultdict(list)   # top studs: (x,y,z) -> piece
def reg_studs(p):
    for pt,d in p['studs']:
        if d=='-y': stud[tuple(round(v,2) for v in pt)].append(id(p))
for p in fixed: reg_studs(p)
BR=[(4,2,'3001'),(2,4,'3001'),(3,2,'3002'),(2,3,'3002'),(2,2,'3003'),(4,1,'3010'),(1,4,'3010'),(3,1,'3622'),(1,3,'3622'),(2,1,'3004'),(1,2,'3004'),(1,1,'3005')]
I=(1,0,0,0,1,0,0,0,1); R90=(0,0,1,0,1,0,-1,0,0)
new=[]
def place(n,x0,z0,w,d,pid,role):
    y1=-24-24*n; y0=y1-24; X0,Z0=20*x0,20*z0
    rot=I if w>=d and not (w==d) or (w==d) else R90
    if pid in ('3001','3002','3010','3622','3004') and w<d: rot=R90
    else: rot=I
    cs=[(20*x+10,20*z+10) for x in range(x0,x0+w) for z in range(z0,z0+d)]
    p=dict(id=pid,color=71,pos=(X0+10*w,y0,Z0+10*d),rot=rot,body=[(X0,y0,Z0,X0+20*w,y1,Z0+20*d)],
           studs=[((a,y0,b),'-y') for a,b in cs],anti=[((a,y1,b),'+y') for a,b in cs],role=role+' L%d'%(n+1))
    new.append(p); reg_studs(p)
    for c in [(x,z) for x in range(x0,x0+w) for z in range(z0,z0+d)]: used[n].add(c)
    return p
used=collections.defaultdict(set)
def free(n,x0,z0,w,d): return all((x,z) in avail[n] and (x,z) not in used[n] for x in range(x0,x0+w) for z in range(z0,z0+d))
def supported(p):
    a=[pt for pt,d in p['anti'] if d=='+y']
    g=sum(1 for pt in a if stud.get(tuple(round(v,2) for v in pt)))
    if g>=min(2,len(a)): return True
    # cannot add more grip if no free hollow cell is under its remaining antistuds: accept what it has
    return False
def needs_check(p):
    return any(d=='+y' for _,d in p['anti']) and p['id'] not in ('65803',)
TOP=max(avail)
# tie beams: every 4th course, 2-stud-wide lines across the hollow every 8 studs in x and z (only through hollow cells)
stats=collections.Counter()
for n in range(TOP,-2,-1):
    # 2) support for everything whose bottom sits on this course's top
    ytop=-24-24*n-24
    above=[p for p in fixed+new if needs_check(p) and any(abs(pt[1]-ytop)<0.01 for pt,d in p['anti'] if d=='+y')]
    uns=[p for p in above if not supported(p)]
    while uns:
        best=None
        for p in uns:
            for pt,d in p['anti']:
                cx,cz=int(pt[0]//20),int(pt[2]//20)
                if (cx,cz) not in avail[n] or (cx,cz) in used[n]: continue
                for w,d2,pid in BR:
                    for ox in range(w):
                        for oz in range(d2):
                            x0,z0=cx-ox,cz-oz
                            if not free(n,x0,z0,w,d2): continue
                            cover={(x,z) for x in range(x0,x0+w) for z in range(z0,z0+d2)}
                            sc=sum(1 for q in uns if any((int(a[0]//20),int(a[2]//20)) in cover for a,_ in q['anti']))
                            key=(sc,w*d2)
                            if best is None or key>best[0]: best=(key,(x0,z0,w,d2,pid))
        if best is None:
            g1=[q for q in uns if any(stud.get(tuple(round(v,2) for v in pt)) for pt,d in q['anti'] if d=='+y')]
            stats['single_grip_no_room']+=len(g1); uns=[q for q in uns if q not in g1]
            if not uns: break
            stats['unsupportable']+=len(uns); print('no room under',[(q['id'],q['role']) for q in uns][:5]); break
        place(n,*best[1],'hollow support'); stats['support']+=1
        uns=[p for p in uns if not supported(p)]

# tie plates: every 4th course, 2-wide plates laid across the hollow on the top of the course below, each one gripping
# studs at both ends (wall or pillar) so opposite walls are tied together; x-direction and z-direction alternate.
PL={2:'3022',3:'3021',4:'3020',6:'3795',8:'3034',10:'3832',12:'2445',14:'91988',16:'4282'}
def hasstud(x,y,z): return bool(stud.get((round(20*x+10.,2),round(y,2),round(20*z+10.,2))))
def tieplate(m,cs,along):
    ybot=-24-24*m; ytop=ybot-8
    xs=[c[0] for c in cs]; zs=[c[1] for c in cs]; X0,X1,Z0,Z1=20*min(xs),20*max(xs)+20,20*min(zs),20*max(zs)+20
    L=max(xs)-min(xs)+1 if along=='x' else max(zs)-min(zs)+1
    p=dict(id=PL[L],color=71,pos=((X0+X1)/2,ytop,(Z0+Z1)/2),rot=I if along=='x' else R90,body=[(X0,ytop,Z0,X1,ybot,Z1)],
       studs=[((20*x+10,ytop,20*z+10),'-y') for x,z in cs],anti=[((20*x+10,ybot,20*z+10),'+y') for x,z in cs],role='hollow tie plate L%d'%m)
    new.append(p); reg_studs(p); used[m]|=set(cs); stats['tieplate']+=1
for m,along in [(m,a) for m in range(2,TOP+1,3) for a in ('x','z')]:
    ybot=-24-24*m
    for k in range(0,64):
        for line in ([k] if k%4==0 else []):
            rows=(line,line+1)
            rng=range(0,64) if along=='x' else range(0,48)
            cell=lambda t,r:(t,r) if along=='x' else (r,t)
            ok=lambda t:all(cell(t,r) in avail[m] and cell(t,r) not in used[m] for r in rows)
            st=lambda t:any(hasstud(*((t,ybot,r) if along=='x' else (r,ybot,t))) for r in rows)
            t=0
            while t<64:
                if not ok(t): t+=1; continue
                u=t
                while u<64 and ok(u): u+=1
                run=list(range(t,u)); pos=[q for q in run if st(q)]
                i=0
                while i<len(pos):
                    s0=pos[i]; best=None
                    for j in range(i+1,len(pos)):
                        e=pos[j]
                        if e-s0+1>16: break
                        if any(not st(q) for q in range(s0,e+1)): best=j
                    if best is None: i+=1; continue
                    e=pos[best]; need=e-s0+1; Ls=[L for L in sorted(PL) if L>=need]
                    placed=False
                    for L in Ls:
                        for st0 in (s0, e-L+1):
                            if st0>=t and st0+L<=u:
                                tieplate(m,[cell(q,r) for q in range(st0,st0+L) for r in rows],along); placed=True; break
                        if placed: break
                    i=best+1
                t=u

# ---- bracing: a pillar piece that only touches other pillar pieces is moved/rotated (same course, still gripping the
# pieces above and below it) so that it also grips a wall piece; repeated until no long unbraced runs remain ----
def rk(pt): return tuple(round(v,2) for v in pt)
def conn_maps():
    T=collections.defaultdict(list); B=collections.defaultdict(list)
    for q in fixed+new:
        for pt,d in q['studs']:
            if d=='-y': T[rk(pt)].append(id(q))
        for pt,d in q['anti']:
            if d=='+y': B[rk(pt)].append(id(q))
    return T,B
HOL={id(q) for q in new}
def nbrs(p,T,B):
    s=set()
    for pt,d in p['studs']:
        if d=='-y': s|=set(B.get(rk(pt),[]))
    for pt,d in p['anti']:
        if d=='+y': s|=set(T.get(rk(pt),[]))
    s.discard(id(p)); return s
def mk(n,x0,z0,w,d,pid,role):
    y1=-24-24*n; y0=y1-24; X0_,Z0_=20*x0,20*z0
    rot=R90 if (w<d) else I
    cs=[(20*x+10,20*z+10) for x in range(x0,x0+w) for z in range(z0,z0+d)]
    return dict(id=pid,color=71,pos=(X0_+10*w,y0,Z0_+10*d),rot=rot,body=[(X0_,y0,Z0_,X0_+20*w,y1,Z0_+20*d)],
           studs=[((a,y0,b),'-y') for a,b in cs],anti=[((a,y1,b),'+y') for a,b in cs],role=role)
byid={}
for it in range(6):
    T,B=conn_maps(); byid={id(q):q for q in fixed+new}
    iso=[q for q in new if all(j in HOL for j in nbrs(q,T,B))]
    swapped=0
    for q in iso:
        T,B=conn_maps(); byid={id(r):r for r in fixed+new}
        nb=nbrs(q,T,B)
        if any(j not in HOL for j in nb): continue
        b=q['body'][0]; n=int(round((-24-b[4])/24))
        qc={(x,z) for x in range(int(b[0]//20),int(round(b[3]))//20) for z in range(int(b[2]//20),int(round(b[5]))//20)}
        ytop=b[1]; ybot=b[4]
        above=[byid[j] for j in nb if byid[j]['body'][0][4]<=ytop+0.01]   # pieces resting on q
        below=[byid[j] for j in nb if byid[j]['body'][0][1]>=ybot-0.01]
        def cellsof(r,y):
            return {(int(pt[0]//20),int(pt[2]//20)) for pt,d in (r['anti'] if r['body'][0][4]<=ytop+0.01 else r['studs']) }
        aboveC=[cellsof(r,0) for r in above]; belowC=[cellsof(r,0) for r in below]
        used[n]-=qc
        best=None
        for w,d,pid in BR[:2]+BR[2:4]+BR[5:7]:
            for x0 in range(min(c[0] for c in qc)-w+1,max(c[0] for c in qc)+1):
                for z0 in range(min(c[1] for c in qc)-d+1,max(c[1] for c in qc)+1):
                    if not free(n,x0,z0,w,d): continue
                    cand=mk(n,x0,z0,w,d,pid,q['role']); cc={(x,z) for x in range(x0,x0+w) for z in range(z0,z0+d)}
                    if any(len(cc&C)<min(2,len(C)) for C in aboveC) or any(len(cc&C)<min(2,len(C)) for C in belowC): continue
                    wall=sum(1 for j in nbrs(cand,T,B) if j not in HOL and j!=id(q))
                    if wall and (best is None or (wall,w*d)>best[0]): best=((wall,w*d),cand,cc)
        if best:
            new.remove(q); HOL.discard(id(q)); new.append(best[1]); HOL.add(id(best[1])); used[n]|=best[2]; swapped+=1
            reg_studs(best[1])
        else: used[n]|=qc
    print('brace pass',it,'isolated',len(iso),'re-placed',swapped)
    if not swapped: break
print('removed',len(removed),'new',len(new),dict(stats))
P5=fixed+new
json.dump(dict(parts=P5,removed=[P4[i] for i in removed],new=len(new)),open('v5.json','w'))
if __name__=='__main__' and 'dbg' in __import__('sys').argv:
    for m in range(0,TOP+1):
        fr=avail[m]-used[m]; ybot=-24-24*m
        print(m,len(avail[m]),len(fr),sum(hasstud(x,ybot,z) for x,z in fr), sorted(fr)[:3])
    print(list(stud.keys())[:3])
if 'dbg2' in __import__('sys').argv:
    col=collections.Counter()
    for c in set().union(*[avail[m]-used[m] for m in avail]):
        best=cur=0
        for m in range(-1,TOP+1):
            if c in avail[m] and c not in used[m]: cur+=1; best=max(best,cur)
            else: cur=0
        col[best]+=1
    print('vertical hollow run (courses) -> columns',sorted(col.items()))
    print(sorted((m,len(avail[m]-used[m])) for m in avail))
