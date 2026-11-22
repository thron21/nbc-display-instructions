"""Find pieces with no visible face in the finished v4 model (voxel grid at 4 LDU, flood fill of outside air)."""
import json, collections, numpy as np
from scipy import ndimage
P=json.load(open('/workspace/courtyard_mountains_v4/src/v4.json'))['parts']
V=4; X0,Y0,Z0=-8,-624,-8; NX,NY,NZ=(1280+16)//V,(32+624+8)//V,(960+16)//V
G=-np.ones((NX,NY,NZ),np.int32)
SLOPE=('cap ','snow curved','snow drift','rock face sideways cheese')
def box(i,b):
    x0,y0,z0,x1,y1,z1=[int(round(v)) for v in b]
    sl=(slice((x0-X0)//V,(x1-X0)//V),slice((y0-Y0)//V,(y1-Y0)//V),slice((z0-Z0)//V,(z1-Z0)//V))
    assert (G[sl]==-1).all(), ('overlap',i,P[i]['role'],set(G[sl].ravel())-{-1})
    G[sl]=i
for i,p in enumerate(P):
    if p['id']=='2780': continue                       # pins sit inside the Technic bricks' holes
    b=list(p['body'][0])
    if p['role'].startswith(SLOPE):                     # slopes: only the flat base (4 LDU slab) counts as a cover
        r=p['rot']; d=(r[1],r[4],r[7])                 # local +y (the base side) in model coordinates
        ax=[k for k in range(3) if d[k]]; assert len(ax)==1; a=ax[0]
        if d[a]>0: b[a]=b[a+3]-V
        else: b[a+3]=b[a]+V
    box(i,b)
air=G<0
lab,_=ndimage.label(air)                                # 6-connected air pockets
outside=lab==lab[0,0,0]
vis=set()
for ax in range(3):
    for s in (1,-1):
        nb=np.roll(outside,s,axis=ax)                   # grid is padded, so roll never wraps into the model
        vis.update(np.unique(G[nb & (G>=0)]).tolist())
KEEP=('65803','Technic pin','paver','rock face','SPIRAL')+SLOPE
hidden=[i for i,p in enumerate(P) if i not in vis and p['id']!='2780' and not p['role'].startswith(KEEP)]
# sanity: every slope base and sideways rock piece should sit against something
print('pieces:',len(P),'visible:',len(vis),'hidden candidates:',len(hidden))
print('enclosed air pockets (not outside):', int((air&~outside).sum()), 'voxels')
c=collections.Counter((P[i]['id'],P[i]['role'].split(' L')[0] if P[i]['role'].startswith('mountain') else P[i]['role']) for i in hidden)
for k,v in sorted(c.items(),key=lambda x:-x[1]): print(v,k)
excl_hidden=collections.Counter(P[i]['role'][:30] for i,p in enumerate(P) if i not in vis and p['id']!='2780' and p['role'].startswith(KEEP))
print('hidden but kept as is:',dict(excl_hidden))
json.dump(hidden,open('hidden.json','w'))
sl=ndimage.find_objects(lab); sizes=ndimage.sum(air,lab,index=range(1,lab.max()+1))
big=sorted([(int(s),k+1) for k,s in enumerate(sizes) if k+1!=lab[0,0,0]],reverse=True)
print('pockets:',len(big))
for s,k in big[:12]:
    o=sl[k-1]; print(s,[(a.start*V+X0 if j!=1 else a.start*V+Y0, a.stop*V+(X0 if j!=1 else Y0)) for j,a in enumerate(o)])
def at(x,y,z): return (x-X0)//V,(y-Y0)//V,(z-Z0)//V
for pt in [(700,-100,400),(700,-300,470),(700,-300,300),(300,-200,400),(300,-200,200)]:
    q=at(*pt); print(pt,'outside' if outside[q] else ('piece '+P[G[q]]['role'][:30] if G[q]>=0 else 'pocket %d'%lab[q]))
# niche opening: column along z at x=700,y=-100
col=[('o' if outside[at(700,-100,z)] else ('#' if G[at(700,-100,z)]>=0 else '.')) for z in range(0,960,20)]
print(''.join(col))
col=[('o' if outside[at(x,-200,400)] else ('#' if G[at(x,-200,400)]>=0 else '.')) for x in range(0,1280,20)]
print(''.join(col))
ok=bad=0
for i,p in enumerate(P):
    if not p['role'].startswith(SLOPE): continue
    r=p['rot']; d=(r[1],r[4],r[7]); a=[k for k in range(3) if d[k]][0]; b=p['body'][0]
    c=[(b[k]+b[k+3])/2 for k in range(3)]; c[a]=(b[a+3]+2) if d[a]>0 else (b[a]-2)
    q=at(*[int(v) for v in c])
    if G[q]>=0: ok+=1
    else: bad+=1
print('slope bases against a piece:',ok,'not:',bad)
