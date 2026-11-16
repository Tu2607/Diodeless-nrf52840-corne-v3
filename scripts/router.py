"""Small two-layer grid maze router for the diodeless Corne.

Every signal net here is a two-pin net (switch pad to controller pin), so a
plain A* search with rip-up by reordering is enough.
"""
import heapq, math, sys, json
import numpy as np
import pcbnew
from shapely.geometry import Polygon, Point, box
from shapely import contains_xy
import geom

P = 0.15            # grid pitch, mm
W = 0.25            # track width
CL = 0.23           # copper clearance (0.2 rule plus margin for grid rounding)
VIA_D, VIA_DRILL = 0.6, 0.3
EDGE = 0.4          # copper to board edge
HOLE_CL = 0.3       # copper to non-plated hole
B_COST = 1.6        # routing on the back costs more, keeps the back free for ground
VIA_COST = 40.0     # in grid steps
mm = pcbnew.FromMM


def pad_poly(p):
    sps = p.GetEffectivePolygon()
    o = sps.Outline(0)
    pts = [(o.CPoint(i).x / 1e6, o.CPoint(i).y / 1e6) for i in range(o.PointCount())]
    return Polygon(pts).buffer(0)


class Grid:
    def __init__(self, poly):
        self.poly = poly
        x0, y0, x1, y1 = poly.bounds
        self.x0, self.y0 = x0, y0
        self.nx = int((x1 - x0) / P) + 2
        self.ny = int((y1 - y0) / P) + 2
        xs = self.x0 + np.arange(self.nx) * P
        ys = self.y0 + np.arange(self.ny) * P
        self.X, self.Y = np.meshgrid(xs, ys)
        # occ: 0 free, -1 blocked for everyone, n>0 blocked for all nets but n
        self.occ = np.zeros((2, self.ny, self.nx), dtype=np.int32)
        inside = contains_xy(poly.buffer(-(EDGE + W / 2)), self.X, self.Y)
        self.occ[:, ~inside] = -1
        self.novia = np.zeros((self.ny, self.nx), dtype=bool)

    def cell(self, x, y):
        return int(round((y - self.y0) / P)), int(round((x - self.x0) / P))

    def xy(self, iy, ix):
        return self.x0 + ix * P, self.y0 + iy * P

    def _mask(self, shape):
        x0, y0, x1, y1 = shape.bounds
        iy0, ix0 = self.cell(x0, y0)
        iy1, ix1 = self.cell(x1, y1)
        iy0, ix0 = max(iy0 - 1, 0), max(ix0 - 1, 0)
        iy1, ix1 = min(iy1 + 2, self.ny), min(ix1 + 2, self.nx)
        if iy1 <= iy0 or ix1 <= ix0:
            return None
        sl = (slice(iy0, iy1), slice(ix0, ix1))
        return sl, contains_xy(shape, self.X[sl], self.Y[sl])

    def block(self, shape, layers, net):
        r = self._mask(shape)
        if r is None:
            return
        sl, m = r
        for L in layers:
            o = self.occ[L][sl]
            if net == -1:
                o[m] = -1
            else:
                o[m & (o == 0)] = net
                o[m & (o != 0) & (o != net)] = -1

    def block_via(self, shape):
        r = self._mask(shape)
        if r is not None:
            sl, m = r
            self.novia[sl][m] = True


def layers_of(p):
    L = []
    if p.IsOnLayer(pcbnew.F_Cu):
        L.append(0)
    if p.IsOnLayer(pcbnew.B_Cu):
        L.append(1)
    return L


def build_grid(board, poly):
    g = Grid(poly)
    region = poly.buffer(2)
    for f in board.GetFootprints():
        for p in f.Pads():
            c = p.GetPosition()
            if not region.contains(Point(c.x / 1e6, c.y / 1e6)):
                continue
            if p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH:
                r = max(p.GetDrillSize().x, p.GetDrillSize().y) / 2e6
                hole = Point(c.x / 1e6, c.y / 1e6).buffer(r)
                g.block(hole.buffer(HOLE_CL + W / 2), (0, 1), -1)
                g.block_via(hole.buffer(HOLE_CL + VIA_D / 2))
                continue
            sh = pad_poly(p)
            net = p.GetNetCode() if p.GetNetCode() > 0 else -1
            g.block(sh.buffer(CL + W / 2), layers_of(p), net)
            g.block_via(sh.buffer(CL + VIA_D / 2))
            if p.GetDrillSize().x > 0:  # plated hole: keep other copper off both layers
                g.block(sh.buffer(CL + W / 2), (0, 1), net)
    return g


DIRS = [(-1, 0, 1.0), (1, 0, 1.0), (0, -1, 1.0), (0, 1, 1.0),
        (-1, -1, 1.4142), (-1, 1, 1.4142), (1, -1, 1.4142), (1, 1, 1.4142)]
VR = int(math.ceil((VIA_D / 2 - W / 2) / P))
VIA_OFFS = [(dy, dx) for dy in range(-VR, VR + 1) for dx in range(-VR, VR + 1)
            if math.hypot(dy, dx) * P <= VIA_D / 2 - W / 2 + 0.03]


def astar(g, net, starts, goal, goal_layers):
    occ = g.occ
    ny, nx = g.ny, g.nx
    gy, gx = goal
    def h(y, x):
        dy, dx = abs(y - gy), abs(x - gx)
        return (max(dy, dx) + 0.4142 * min(dy, dx))
    lc = (1.0, B_COST)
    openh = []
    best = {}
    came = {}
    for s in starts:
        best[s] = 0.0
        heapq.heappush(openh, (h(s[1], s[2]), 0.0, s, None))
    while openh:
        f, c, s, prev = heapq.heappop(openh)
        if c > best.get(s, 1e18):
            continue
        came[s] = prev
        L, y, x = s
        if y == gy and x == gx and L in goal_layers:
            path = [s]
            while came[path[-1]] is not None:
                path.append(came[path[-1]])
            return path[::-1]
        for dy, dx, w in DIRS:
            y2, x2 = y + dy, x + dx
            if not (0 <= y2 < ny and 0 <= x2 < nx):
                continue
            o = occ[L, y2, x2]
            if o != 0 and o != net:
                continue
            if dy and dx:  # no corner cutting
                o1 = occ[L, y, x2]; o2 = occ[L, y2, x]
                if (o1 != 0 and o1 != net) or (o2 != 0 and o2 != net):
                    continue
            c2 = c + w * lc[L]
            s2 = (L, y2, x2)
            if c2 < best.get(s2, 1e18):
                best[s2] = c2
                heapq.heappush(openh, (c2 + h(y2, x2), c2, s2, s))
        # via
        if not g.novia[y, x]:
            ok = True
            for dy, dx in VIA_OFFS:
                yy, xx = y + dy, x + dx
                if not (0 <= yy < ny and 0 <= xx < nx):
                    ok = False; break
                a, b = occ[0, yy, xx], occ[1, yy, xx]
                if (a != 0 and a != net) or (b != 0 and b != net):
                    ok = False; break
            if ok:
                s2 = (1 - L, y, x)
                c2 = c + VIA_COST
                if c2 < best.get(s2, 1e18):
                    best[s2] = c2
                    heapq.heappush(openh, (c2 + h(y, x), c2, s2, s))
    return None


def run_cells(a, b):
    """Cells of a straight or 45 degree run from a to b (inclusive), or None."""
    dy, dx = b[0] - a[0], b[1] - a[1]
    n = max(abs(dy), abs(dx))
    if n == 0:
        return np.array([a[0]]), np.array([a[1]])
    if not (dy == 0 or dx == 0 or abs(dy) == abs(dx)):
        return None
    sy, sx = (dy > 0) - (dy < 0), (dx > 0) - (dx < 0)
    k = np.arange(n + 1)
    return a[0] + sy * k, a[1] + sx * k


def run_free(g, net, L, a, b):
    r = run_cells(a, b)
    ys, xs = r
    o = g.occ[L]
    v = o[ys, xs]
    if not np.all((v == 0) | (v == net)):
        return False
    if a[0] != b[0] and a[1] != b[1]:  # diagonal: no corner cutting
        v1 = o[ys[:-1], xs[1:]]; v2 = o[ys[1:], xs[:-1]]
        if not (np.all((v1 == 0) | (v1 == net)) and np.all((v2 == 0) | (v2 == net))):
            return False
    return True


def elbows(a, b):
    """The two octilinear two-segment connections between cells a and b."""
    dy, dx = b[0] - a[0], b[1] - a[1]
    d = min(abs(dy), abs(dx))
    sy, sx = (dy > 0) - (dy < 0), (dx > 0) - (dx < 0)
    m1 = (a[0] + sy * d, a[1] + sx * d)          # diagonal first
    m2 = (b[0] - sy * d, b[1] - sx * d)          # straight first
    return [m1, m2]


def smooth_run(g, net, L, pts):
    out = [pts[0]]
    i = 0
    last = len(pts) - 1
    while i < last:
        rem = last - i
        done = False
        for frac in (1, 0.8, 0.6, 0.45, 0.33, 0.25, 0.18, 0.12, 0.08, 0.05, 0.03):
            j = i + max(1, int(rem * frac))
            a, b = pts[i], pts[j]
            for m in elbows(a, b):
                if run_free(g, net, L, a, m) and run_free(g, net, L, m, b):
                    if m != a and m != b:
                        out.append(m)
                    out.append(b)
                    i = j
                    done = True
                    break
            if done:
                break
        if not done:
            out.append(pts[i + 1])
            i += 1
    # merge collinear points
    res = [out[0]]
    for p in out[1:]:
        if len(res) >= 2:
            a, b = res[-2], res[-1]
            d1 = (b[0] - a[0], b[1] - a[1]); d2 = (p[0] - b[0], p[1] - b[1])
            if d1[0] * d2[1] == d1[1] * d2[0] and (d1[0] * d2[0] + d1[1] * d2[1]) > 0:
                res[-1] = p
                continue
        if p != res[-1]:
            res.append(p)
    return res


def simplify(g, net, path):
    """Returns list of ('seg', L, (y,x), (y,x)) and ('via', (y,x)), smoothed."""
    out = []
    run = [path[0]]
    def flush():
        pts = [(s[1], s[2]) for s in run]
        if len(pts) > 1:
            sm = smooth_run(g, net, run[0][0], pts)
            for a, b in zip(sm, sm[1:]):
                out.append(('seg', run[0][0], a, b))
    for s in path[1:]:
        if s[0] != run[-1][0]:
            flush()
            out.append(('via', (s[1], s[2])))
            run = [s]
        else:
            run.append(s)
    flush()
    return out


def commit(g, net, items):
    from shapely.geometry import LineString
    for it in items:
        if it[0] == 'seg':
            _, L, a, b = it
            ls = LineString([g.xy(*a), g.xy(*b)]) if a != b else Point(g.xy(*a))
            g.block(ls.buffer(W / 2 + CL + W / 2), (L,), net)
            g.block_via(ls.buffer(W / 2 + CL + VIA_D / 2))
        else:
            pt = Point(g.xy(*it[1]))
            g.block(pt.buffer(VIA_D / 2 + CL + W / 2), (0, 1), net)
            g.block_via(pt.buffer(VIA_D / 2 + max(CL, 0.25) + VIA_D / 2))


def route_half(board, poly, tag):
    # nets: name -> pads (within this half)
    region = poly.buffer(2)
    nets = {}
    for f in board.GetFootprints():
        for p in f.Pads():
            c = p.GetPosition()
            if p.GetNetCode() > 0 and region.contains(Point(c.x / 1e6, c.y / 1e6)):
                nets.setdefault(p.GetNetname(), []).append(p)
    def d(a, b):
        return math.hypot(a.GetPosition().x - b.GetPosition().x, a.GetPosition().y - b.GetPosition().y)
    jobs = {}
    for n, pads in nets.items():
        if n.startswith('GND'):
            continue
        # spanning tree over the net's pads: each new pad joins its nearest connected pad
        done = [pads[0]]
        rest = list(pads[1:])
        i = 0
        while rest:
            p, q = min(((p, q) for p in rest for q in done), key=lambda pq: d(*pq))
            # start the search at a through-hole pad when there is one, so the goal can be on either layer
            jobs[(n, i)] = (q, p)
            done.append(p); rest.remove(p); i += 1
    order = sorted(jobs, key=lambda k: d(*jobs[k]))
    for attempt in range(12):
        g = build_grid(board, poly)
        result = {}
        failed = None
        for n in order:
            a, b = jobs[n]
            code = a.GetNetCode()
            # start from the controller-side or either; search from pad a to pad b
            ca = g.cell(a.GetPosition().x / 1e6, a.GetPosition().y / 1e6)
            cb = g.cell(b.GetPosition().x / 1e6, b.GetPosition().y / 1e6)
            starts = [(L, ca[0], ca[1]) for L in layers_of(a)]
            path = astar(g, code, starts, cb, set(layers_of(b)))
            if path is None:
                failed = n
                break
            items = simplify(g, code, path)
            commit(g, code, items)
            result[n] = (a, b, items)
        if failed is None:
            print(tag, 'routed', len(result), 'nets on attempt', attempt + 1, flush=True)
            return g, result
        print(tag, 'attempt', attempt + 1, 'failed on', failed, flush=True)
        order.remove(failed)
        order.insert(0, failed)
    raise SystemExit('routing failed for ' + tag)


def emit(board, g, result):
    nvias = 0
    length = 0.0
    for n, (a, b, items) in result.items():
        net = a.GetNet()
        def track(L, p0, p1):
            nonlocal length
            if p0 == p1:
                return
            t = pcbnew.PCB_TRACK(board)
            t.SetStart(pcbnew.VECTOR2I(mm(p0[0]), mm(p0[1])))
            t.SetEnd(pcbnew.VECTOR2I(mm(p1[0]), mm(p1[1])))
            t.SetWidth(mm(W)); t.SetLayer(pcbnew.F_Cu if L == 0 else pcbnew.B_Cu); t.SetNet(net)
            board.Add(t)
            length += math.hypot(p0[0] - p1[0], p0[1] - p1[1])
        # stubs from exact pad centres to the first and last grid points
        first = [it for it in items if it[0] == 'seg']
        pa = (a.GetPosition().x / 1e6, a.GetPosition().y / 1e6)
        pb = (b.GetPosition().x / 1e6, b.GetPosition().y / 1e6)
        if first:
            track(first[0][1], pa, g.xy(*first[0][2]))
            track(first[-1][1], g.xy(*first[-1][3]), pb)
        for it in items:
            if it[0] == 'seg':
                track(it[1], g.xy(*it[2]), g.xy(*it[3]))
            else:
                v = pcbnew.PCB_VIA(board)
                x, y = g.xy(*it[1])
                v.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
                v.SetWidth(mm(VIA_D)); v.SetDrill(mm(VIA_DRILL))
                v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); v.SetNet(net)
                board.Add(v); nvias += 1
    return nvias, length


if __name__ == '__main__':
    src, dst = sys.argv[1], sys.argv[2]
    board = pcbnew.LoadBoard(src)
    halves = geom.half_polys(board)
    for tag in ('L', 'R'):
        g, res = route_half(board, halves[tag], tag)
        nv, ln = emit(board, g, res)
        print(tag, 'vias', nv, 'track mm', round(ln), flush=True)
    board.Save(dst)
