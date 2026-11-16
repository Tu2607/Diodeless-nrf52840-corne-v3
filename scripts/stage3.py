import pcbnew, json, shutil, sys
import geom

mm = pcbnew.FromMM
NAME = 'corne-diodeless'
b = pcbnew.LoadBoard('stage2.kicad_pcb')
halves = geom.half_polys(b)

b.GetDesignSettings().m_SolderMaskExpansion = mm(0.05)
# title block
tb = b.GetTitleBlock()
tb.SetTitle('Corne Cherry v3 diodeless wireless')
tb.SetRevision('0.4')
tb.SetCompany('based on Corne Cherry v3.0.1 by foostan')
tb.SetDate('2026-11-15')


def text(s, x, y, size=1.0, layer=pcbnew.F_SilkS, rot=0):
    t = pcbnew.PCB_TEXT(b)
    t.SetText(s)
    t.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
    t.SetLayer(layer)
    t.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size)))
    t.SetTextThickness(mm(size * 0.15))
    if rot:
        t.SetTextAngleDegrees(rot)
    if layer == pcbnew.B_SilkS:
        t.SetMirrored(True)
    b.Add(t)


for ref, sw, sgn in (('BT1', 'SW43', 1), ('BT2', 'SW44', -1)):
    f = b.FindFootprintByReference(ref)
    f.Reference().SetVisible(False)
    b.FindFootprintByReference(sw).Reference().SetVisible(False)
    pads = {p.GetNumber(): p.GetPosition() for p in f.Pads()}
    for p in f.Pads():
        p.SetZoneConnection(pcbnew.ZONE_CONNECTION_FULL)
    x1, y1 = pads['1'].x / 1e6, pads['1'].y / 1e6
    x2 = pads['2'].x / 1e6
    text('+', x1 - 1.9, y1 - 2.9, 1.2)
    text('-', x2 + 1.9, y1 - 2.9, 1.2)
    text('BAT', (x1 + x2) / 2, y1 + 4.1, 0.9)
    s = b.FindFootprintByReference(sw).GetPosition()
    text('PWR', s.x / 1e6 - sgn * 5.6, s.y / 1e6 + 3.3, 0.9)
    tg = b.FindFootprintByReference('J3' if sgn == 1 else 'J4')
    tg.Reference().SetVisible(False)
    tp = {p.GetNumber(): p.GetPosition() for p in tg.Pads()}
    text('TOGGLE', (tp['1'].x + tp['2'].x) / 2e6, tp['2'].y / 1e6 + 2.0, 0.8)

# ground pours
for tag, netname in (('L', 'GND'), ('R', 'GND_r')):
    net = b.FindNet(netname)
    poly = halves[tag].buffer(-0.4).simplify(0.02)
    for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
        z = pcbnew.ZONE(b)
        z.SetLayer(layer)
        z.SetNet(net)
        z.SetLocalClearance(mm(0.3))
        z.SetMinThickness(mm(0.25))
        z.SetThermalReliefGap(mm(0.3))
        z.SetThermalReliefSpokeWidth(mm(0.4))
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
        z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
        o = z.Outline()
        o.NewOutline()
        for x, y in list(poly.exterior.coords)[:-1]:
            o.Append(mm(x), mm(y))
        b.Add(z)

filler = pcbnew.ZONE_FILLER(b)
filler.Fill(b.Zones())
out = 'proj/%s.kicad_pcb' % NAME
b.Save(out)
print('saved', out)
