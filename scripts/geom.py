import pcbnew, math
from shapely.geometry import LineString, Point, box, Polygon
from shapely.ops import unary_union, linemerge
def arc_pts(d,n=12):
    c=d.GetCenter(); s=d.GetStart(); e=d.GetEnd(); m=d.GetArcMid()
    r=math.hypot(s.x-c.x,s.y-c.y)
    a0=math.atan2(s.y-c.y,s.x-c.x); am=math.atan2(m.y-c.y,m.x-c.x); a1=math.atan2(e.y-c.y,e.x-c.x)
    norm=lambda a:a%(2*math.pi)
    d1=norm(a1-a0); dm=norm(am-a0)
    sweep=d1 if dm<=d1 else d1-2*math.pi
    return [((c.x+r*math.cos(a0+sweep*i/n))/1e6,(c.y+r*math.sin(a0+sweep*i/n))/1e6) for i in range(n+1)]
def half_polys(b, verbose=False):
    lines=[]
    for d in b.GetDrawings():
        if d.GetClass()=='PCB_SHAPE' and d.GetLayerName()=='Edge.Cuts':
            if d.GetShape()==pcbnew.SHAPE_T_SEGMENT:
                l=LineString([(round(d.GetStart().x/1e6,3),round(d.GetStart().y/1e6,3)),(round(d.GetEnd().x/1e6,3),round(d.GetEnd().y/1e6,3))])
            elif d.GetShape()==pcbnew.SHAPE_T_ARC:
                l=LineString([(round(x,3),round(y,3)) for x,y in arc_pts(d)])
            elif d.GetShape()==pcbnew.SHAPE_T_BEZIER:
                P=[(p.x/1e6,p.y/1e6) for p in (d.GetStart(),d.GetBezierC1(),d.GetBezierC2(),d.GetEnd())]
                pts=[]
                for i in range(9):
                    t=i/8; u=1-t
                    pts.append((round(u**3*P[0][0]+3*u*u*t*P[1][0]+3*u*t*t*P[2][0]+t**3*P[3][0],3),round(u**3*P[0][1]+3*u*u*t*P[1][1]+3*u*t*t*P[2][1]+t**3*P[3][1],3)))
                l=LineString(pts)
            else: continue
            if l.length>0: lines.append(l)
    walls=[l.buffer(0.03) for l in lines]
    for f in b.GetFootprints():
        if 'Breakaway' in f.GetValue():
            xs=[p.GetPosition().x/1e6 for p in f.Pads()]; ys=[p.GetPosition().y/1e6 for p in f.Pads()]
            walls.append(box(min(xs)-1.2,min(ys)-0.25,max(xs)+1.2,max(ys)+0.25))
    bb=b.GetBoardEdgesBoundingBox()
    free=box(bb.GetX()/1e6-1,bb.GetY()/1e6-1,bb.GetRight()/1e6+1,bb.GetBottom()/1e6+1).difference(unary_union(walls))
    out={}
    for name,ref in (('L','SW8'),('R','SW29')):
        p=b.FindFootprintByReference(ref).GetPosition(); pt=Point(p.x/1e6+3,p.y/1e6+7)
        g=[g for g in free.geoms if g.contains(pt)][0]
        out[name]=Polygon(g.exterior).buffer(0.03)
        if verbose: print(name, len(free.geoms))
    return out
if __name__=='__main__':
    b=pcbnew.LoadBoard('orig/corne-cherry.kicad_pcb')
    out=half_polys(b,True)
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(22,9))
    for k,g in out.items():
        print(k,g.geom_type,g.area,g.bounds)
        x,y=g.exterior.xy; ax.fill(x,y,alpha=0.4)
        gi=g.buffer(-0.5); x,y=gi.exterior.xy; ax.plot(x,y,'k-',lw=0.5)
    for f in b.GetFootprints():
        for p in f.Pads(): ax.plot(p.GetPosition().x/1e6,p.GetPosition().y/1e6,'r.',ms=1)
    ax.set_aspect('equal'); ax.invert_yaxis(); fig.savefig('halves.png',dpi=75,bbox_inches='tight')
