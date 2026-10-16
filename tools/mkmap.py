import json, math, sys
topo = json.load(open(sys.argv[1]))
sx, sy = topo["transform"]["scale"]; tx, ty = topo["transform"]["translate"]
arcs = []
for a in topo["arcs"]:
    x = y = 0; pts = []
    for dx, dy in a:
        x += dx; y += dy; pts.append((x * sx + tx, y * sy + ty))
    arcs.append(pts)
LON0, LON1, LAT0, LAT1 = -75.62, -73.85, 38.90, 40.40
K = math.cos(math.radians(39.7))
W = 1000
def proj(lon, lat):
    x = (lon - LON0) * K; y = LAT1 - lat
    s = W / ((LON1 - LON0) * K)
    return x * s, y * s
H = proj(LON0, LAT0)[1]
def ring(r):
    pts = []
    for i in r:
        p = arcs[i] if i >= 0 else arcs[~i][::-1]
        pts.extend(p if not pts else p[1:])
    out = []; last = None
    for lon, lat in pts:
        x, y = proj(lon, lat); q = (round(x, 1), round(y, 1))
        if q != last: out.append(q); last = q
    return "M" + "L".join("%g %g" % q for q in out) + "Z"
HI = {"34005": ("burlington", "Burlington County, NJ", 3), "34007": ("camden", "Camden County, NJ", 0), "34015": ("gloucester", "Gloucester County, NJ", 1),
      "34033": ("salem", "Salem County, NJ", 2), "34001": ("atlantic", "Atlantic County, NJ", 4), "42017": ("bucks", "Bucks County, PA", 5), "42101": ("philadelphia", "Philadelphia County, PA", 6)}
base, hi = [], []
for g in topo["objects"]["counties"]["geometries"]:
    fid = g.get("id", "")
    if not (fid.startswith("34") or fid in ("42017", "42101", "42091", "42045", "42029", "10003", "10001", "36085", "36047")): continue
    polys = g["arcs"] if g["type"] == "MultiPolygon" else [g["arcs"]]
    d = "".join(ring(r) for poly in polys for r in poly)
    if fid in HI:
        key, name, idx = HI[fid]
        hi.append('<path class="cm-county" pathLength="1" d="%s" data-county="%s" data-idx="%d" tabindex="0" role="button" aria-label="%s"/>' % (d, key, idx, name))
    else:
        base.append('<path class="cm-base%s" pathLength="1" d="%s"/>' % (" cm-nj" if fid.startswith("34") else "", d))
TOWNS = [("Philadelphia", -75.1652, 39.9526, 1), ("Camden", -75.1196, 39.9259, 0), ("Pennsauken", -75.0577, 39.9562, 0), ("Cherry Hill", -75.0307, 39.9348, 1),
         ("Maple Shade", -74.9924, 39.9526, 0), ("Cinnaminson", -74.9927, 40.0006, 0), ("Riverside", -74.9574, 40.0384, 1), ("Somerdale", -75.0230, 39.8440, 0),
         ("Williamstown", -74.9952, 39.6862, 1), ("Pennsville", -75.5163, 39.6537, 1), ("Atlantic City", -74.4229, 39.3643, 1)]
dots = []
for i, (n, lon, lat, lab) in enumerate(TOWNS):
    x, y = proj(lon, lat)
    t = '<g class="cm-town" style="--i:%d" transform="translate(%.1f %.1f)"><title>%s</title><circle class="cm-pulse" r="6"/><circle class="cm-dot" r="4.5"/>' % (i, x, y, n)
    if lab:
        dx = -12 if n in ("Philadelphia", "Pennsville") else 12
        t += '<text x="%d" y="4" text-anchor="%s">%s</text>' % (dx, "end" if dx < 0 else "start", n)
    dots.append(t + "</g>")
ox, oy = proj(-74.9488, 39.9690)
office = '<g class="cm-office" transform="translate(%.1f %.1f)"><title>Keller Williams Moorestown office</title><path d="M0 -13 L9 -4 V8 H-9 V-4 Z"/></g>' % (ox, oy)
svg = ('<svg class="cm-svg" viewBox="0 0 %d %d" role="group" aria-label="Map of the seven counties I cover in New Jersey and Pennsylvania">'
       '<defs><filter id="cm-glow" x="-20%%" y="-20%%" width="140%%" height="140%%"><feGaussianBlur stdDeviation="5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
       '<radialGradient id="cm-fade" cx=".55" cy=".5" r=".62"><stop offset=".6" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>'
       '<mask id="cm-mask"><rect width="100%%" height="100%%" fill="url(#cm-fade)"/></mask></defs>'
       '<g mask="url(#cm-mask)"><g class="cm-bases">%s</g><g class="cm-counties" filter="url(#cm-glow)">%s</g></g>'
       '<text class="cm-river" transform="translate(%.0f %.0f) rotate(-58)">Delaware River</text>'
       '<g class="cm-towns">%s</g>%s</svg>') % (W, round(H), "".join(base), "".join(hi), *proj(-75.36, 39.70), "".join(dots), office)
open(sys.argv[2], "w").write(svg)
print(W, round(H), len(svg))
