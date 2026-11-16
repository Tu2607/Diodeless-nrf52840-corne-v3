import pcbnew, geom, sys
from shapely.geometry import Point
import router
b=pcbnew.LoadBoard(sys.argv[1]); halves=geom.half_polys(b)
items=[]
for f in b.GetFootprints():
    for p in f.Pads():
        c=p.GetPosition(); pt=Point(c.x/1e6,c.y/1e6)
        if p.GetAttribute()==pcbnew.PAD_ATTRIB_NPTH:
            sh=router.pad_poly(p) if p.GetDrillShape()!=pcbnew.PAD_DRILL_SHAPE_CIRCLE else pt.buffer(p.GetDrillSize().x/2e6)
            items.append((f.GetReference(),'hole',sh,0))
        else: items.append((f.GetReference()+'.'+p.GetNumber(),'pad',router.pad_poly(p),p.GetNetCode()))
bad=0
for name,kind,sh,net in items:
    if name.startswith('TAB'): continue
    h=[k for k,g in halves.items() if g.buffer(-0.25).contains(sh)]
    if not h: print('EDGE',name,kind,[round(v,2) for v in sh.bounds]); bad+=1
import itertools
from shapely.strtree import STRtree
tree=STRtree([i[2] for i in items])
for i,(name,kind,sh,net) in enumerate(items):
    for j in tree.query(sh.buffer(0.2)):
        if j<=i: continue
        n2,k2,s2,net2=items[j]
        if kind=='pad' and k2=='pad' and net==net2 and net>0: continue
        dd=sh.distance(s2)
        if dd<0.2: print('NEAR',name,kind,n2,k2,round(dd,3)); bad+=1
print('issues',bad)
