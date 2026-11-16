import pcbnew, json, re
from scipy.optimize import linear_sum_assignment
mm=pcbnew.FromMM
V=lambda x,y: pcbnew.VECTOR2I(mm(x),mm(y))
b=pcbnew.LoadBoard('orig/stripped.kicad_pcb')
FPS=list(b.GetFootprints())
cnt={}
for f in FPS:
    r=f.GetReference()
    if '*' in r:
        pre={'Ref**':'H','REF**':'TAB','G***':'LOGO'}.get(r,'X')
        cnt[pre]=cnt.get(pre,0)+1; f.SetReference('%s%d'%(pre,cnt[pre]))
# combined MX + Choc v1 hotswap: Choc socket sits on the opposite side of the MX socket.
# Left-half switches are turned 180 degrees so the Choc socket tab points inward, away from the board edge.
import math
def local_to_abs(f,lx,ly):
    a=math.radians(f.GetOrientationDegrees()); c,s_=math.cos(a),math.sin(a)
    p=f.GetPosition()
    return pcbnew.VECTOR2I(int(round(p.x+mm(lx)*c+mm(ly)*s_)),int(round(p.y-mm(lx)*s_+mm(ly)*c)))
def abs_to_local(f,p):
    a=math.radians(f.GetOrientationDegrees()); c,s_=math.cos(a),math.sin(a)
    q=f.GetPosition(); dx,dy=(p.x-q.x)/1e6,(p.y-q.y)/1e6
    return (dx*c-dy*s_, dx*s_+dy*c)
for f in FPS:
    m=re.match(r'^SW(\d+)$',f.GetReference())
    if not m: continue
    if int(m.group(1))<=21 and int(m.group(1))!=20: f.SetOrientationDegrees(f.GetOrientationDegrees()+180)
    pl=list(f.Pads())
    loc={id(p):abs_to_local(f,p.GetPosition()) for p in pl}
    smd={p.GetNumber():p for p in pl if p.GetNumber()}
    hole3=[p for p in pl if not p.GetNumber() and abs(p.GetDrillSize().x-mm(3.0))<1000][0]
    for p in pl:
        lx,ly=loc[id(p)]
        if not p.GetNumber() and abs(p.GetDrillSize().x-mm(1.9))<1000 and abs(ly)<0.01:
            # one slot takes the MX post (5.08) and the Choc post (5.5)
            sgn=1 if lx>0 else -1
            p.SetShape(pcbnew.PAD_SHAPE_OVAL); p.SetDrillShape(pcbnew.PAD_DRILL_SHAPE_OBLONG)
            p.SetSize(pcbnew.VECTOR2I(mm(2.3),mm(1.9))); p.SetDrillSize(pcbnew.VECTOR2I(mm(2.3),mm(1.9)))
            p.SetOrientation(f.GetOrientation())
            ls=pcbnew.LSET(); ls.AddLayer(pcbnew.F_Cu); ls.AddLayer(pcbnew.B_Cu); p.SetLayerSet(ls)
            p.SetPosition(local_to_abs(f,sgn*5.3,0)); p.SetPos0(pcbnew.VECTOR2I(mm(sgn*5.3),0))
    def clone(src,lx,ly,drill=None):
        n=pcbnew.PAD(src); n.SetPosition(local_to_abs(f,lx,ly)); n.SetPos0(pcbnew.VECTOR2I(mm(lx),mm(ly)))
        if drill:
            n.SetSize(pcbnew.VECTOR2I(mm(drill),mm(drill))); n.SetDrillSize(pcbnew.VECTOR2I(mm(drill),mm(drill)))
        f.Add(n); return n
    clone(hole3,0,5.9,3.05); clone(hole3,-5,3.8,3.05)
    clone(smd['1'],-8.5,3.8); clone(smd['2'],3.5,6.0)
# clear pad nets
for f in FPS:
    for p in f.Pads(): p.SetNetCode(0)
old=[n for n in b.GetNetInfo().NetsByNetcode().values() if n.GetNetCode()>0]
for n in old: b.Remove(n)
nets={}
def net(name):
    if name not in nets:
        n=pcbnew.NETINFO_ITEM(b,name); b.Add(n); nets[name]=n
    return nets[name]
LIB='proj/diodeless.pretty'
def add(name,ref,val,x,y,rot):
    f=pcbnew.FootprintLoad(LIB,name); f.SetReference(ref); f.SetValue(val)
    f.SetPosition(V(x,y)); f.SetOrientationDegrees(rot); b.Add(f); return f
# arduino pin number per ProMicro footprint pad, and nice!nano gpio
PAD2ARD={1:1,2:0,5:2,6:3,7:4,8:5,9:6,10:7,11:8,12:9,13:10,14:16,15:14,16:15,17:18,18:19,19:20,20:21}
ARD2NRF={1:'P0.06',0:'P0.08',2:'P0.17',3:'P0.20',4:'P0.22',5:'P0.24',6:'P1.00',7:'P0.11',8:'P1.04',9:'P1.06',10:'P0.09',16:'P0.10',14:'P1.11',15:'P1.13',18:'P1.15',19:'P0.02',20:'P0.29',21:'P0.31'}
pinmap={}
for side,sfx,U,RSW,sw0,edge,sgn in (('left','','U1','RSW1',1,144.94,1),('right','_r','U2','RSW2',22,151.955,-1)):
    u=b.FindFootprintByReference(U); c=u.GetPosition(); cx,cy=c.x/1e6,c.y/1e6
    pads={p.GetNumber():p for p in u.Pads()}
    y0=pads['1'].GetPosition().y/1e6
    ex=add('nice_nano_extra_pins','J1' if side=='left' else 'J2','nice!nano extra pins',cx,y0+9*2.54,0)
    GND=net('GND'+sfx)
    for n in ('3','4','23'): pads[n].SetNet(GND)
    pads['24'].SetNet(net('RAW'+sfx)); pads['22'].SetNet(net('RST'+sfx))
    r=b.FindFootprintByReference(RSW); rp={p.GetNumber():p for p in r.Pads()}
    rp['1'].SetNet(net('RST'+sfx)); rp['2'].SetNet(GND)
    # power switch at the old TRRS spot
    sw=add('SW_SPDT_CK_GT11MSCBE','SW43' if side=='left' else 'SW44','PWR GT11MSCBE',141.3 if sgn==1 else 296.895-141.3,75.7,90)
    for p in sw.Pads():
        if p.GetNumber()=='2': p.SetNet(net('BAT+'+sfx))
        if p.GetNumber()=='1': p.SetNet(net('RAW'+sfx))
    # two wire pads for an off-board toggle, in parallel with the on-board switch: 1 battery +, 2 to controller
    tg=add('PinHeader_1x02_P2.54mm_Vertical','J3' if side=='left' else 'J4','Toggle wire pads',132.5 if sgn==1 else 296.895-132.5,73.6,90*sgn)
    for p in tg.Pads():
        p.SetNet(net(('BAT+' if p.GetNumber()=='1' else 'RAW')+sfx))
    bat=add('JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical','BT1' if side=='left' else 'BT2','Battery JST-PH',cx-1.0,66.6,0)
    for p in bat.Pads():
        p.SetNet(net('BAT+'+sfx) if p.GetNumber()=='1' else GND)
    # keys
    keys=[]
    for i in range(21):
        f=b.FindFootprintByReference('SW%d'%(sw0+i))
        nm=('R%dC%d'%(i//6,i%6)) if i<18 else 'T%d'%(i-18)
        sp={}
        for p in f.Pads():
            if p.GetNumber(): sp.setdefault(p.GetNumber(),[]).append(p)
        for p in sp['2']: p.SetNet(GND)
        keys.append((nm,f,sp['1'][0],sp['1']))
    cand=[(('pm%d'%PAD2ARD[int(n)]),ARD2NRF[PAD2ARD[int(n)]],p) for n,p in pads.items() if int(n) in PAD2ARD]
    cand+=[('extra',p.GetNumber(),p) for p in ex.Pads()]
    cost=[[abs(k[2].GetPosition().x-c[2].GetPosition().x)+abs(k[2].GetPosition().y-c[2].GetPosition().y) for c in cand] for k in keys]
    ri,ci=linear_sum_assignment(cost)
    for r_,c_ in zip(ri,ci):
        nm,f,p,allp=keys[r_]; n=net('K_'+nm+sfx)
        for q in allp: q.SetNet(n)
        cand[c_][2].SetNet(n)
        pinmap.setdefault(side,{})[nm]={'switch':f.GetReference(),'pro_micro':cand[c_][0],'gpio':cand[c_][1]}
json.dump(pinmap,open('pinmap.json','w'),indent=1)
b.Save('stage1.kicad_pcb')
print(b.GetNetCount())
