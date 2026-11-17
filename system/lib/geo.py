"""Weltkarten für FAKTENFABRIK-Doku-Folgen.

Daten: Natural Earth (gemeinfrei) über das npm-Paket world-atlas (ISC-Lizenz),
als lib/world-50m.json (TopoJSON) im Repository. Alles wird selbst gezeichnet.

    import geo
    M = geo.Map(lon0=-180, lon1=180, lat0=-60, lat1=80, x=0, y=420, w=1080)   # Ausschnitt -> Bildbereich
    M.draw_land(c, fill='#1d3557', stroke='#2c4a73')
    M.draw_country(c, 'France', fill='#ffd23f', glow=True)
    x, y = M.xy(2.35, 48.85)   # Paris
    geo.pulse_dot(c, x, y, t, color='#ff4d4d')
"""
import json, os, math
import skia

LIB = os.path.dirname(os.path.abspath(__file__))
_TOPO = None
_SHAPES = None


def _load():
    global _TOPO, _SHAPES
    if _SHAPES is not None:
        return _SHAPES
    _TOPO = json.load(open(os.path.join(LIB, 'world-50m.json')))
    sx, sy = _TOPO['transform']['scale']; tx, ty = _TOPO['transform']['translate']
    arcs = []
    for arc in _TOPO['arcs']:
        x = y = 0; pts = []
        for dx, dy in arc:
            x += dx; y += dy
            pts.append((x * sx + tx, y * sy + ty))
        arcs.append(pts)

    def ring(idx):
        out = []
        for i in idx:
            a = arcs[i] if i >= 0 else arcs[~i][::-1]
            out.extend(a if not out else a[1:])
        return out

    shapes = {}
    for g in _TOPO['objects']['countries']['geometries']:
        name = g.get('properties', {}).get('name', '?')
        polys = []
        if g['type'] == 'Polygon':
            polys.append([ring(r) for r in g['arcs']])
        elif g['type'] == 'MultiPolygon':
            for p in g['arcs']:
                polys.append([ring(r) for r in p])
        shapes.setdefault(name, []).extend(polys)
    _SHAPES = shapes
    return shapes


def names():
    return sorted(_load().keys())


class Map:
    """Equirektangulare Projektion eines Ausschnitts in ein Bildrechteck (Breite w, Höhe aus Seitenverhältnis)."""

    def __init__(self, lon0=-180, lon1=180, lat0=-60, lat1=82, x=0, y=400, w=1080):
        self.lon0, self.lon1, self.lat0, self.lat1 = lon0, lon1, lat0, lat1
        self.x, self.y, self.w = x, y, w
        self.k = w / (lon1 - lon0)
        self.h = (lat1 - lat0) * self.k
        self._cache = {}

    def xy(self, lon, lat):
        return self.x + (lon - self.lon0) * self.k, self.y + (self.lat1 - lat) * self.k

    def _path(self, polys):
        """Ringe über die Datumsgrenze werden "abgewickelt" und bei Bedarf um ±360° versetzt
        ein zweites Mal gezeichnet, damit keine Querstriche entstehen."""
        p = skia.Path()
        for shift in (0, -360, 360):
            for poly in polys:
                for r in poly:
                    pts = []; prev = None; off = 0
                    for lon, lat in r:
                        if prev is not None and abs(lon + off - prev) > 180:
                            off += -360 if lon + off - prev > 0 else 360
                        L = lon + off; pts.append((L, lat)); prev = L
                    lo = min(q[0] for q in pts) + shift; hi = max(q[0] for q in pts) + shift
                    if hi < self.lon0 - 1 or lo > self.lon1 + 1:
                        continue
                    for j, (lon, lat) in enumerate(pts):
                        X, Y = self.xy(lon + shift, lat)
                        (p.moveTo if j == 0 else p.lineTo)(X, Y)
                    p.close()
        p.setFillType(skia.PathFillType.kEvenOdd)
        return p

    def country_path(self, name):
        if name not in self._cache:
            self._cache[name] = self._path(_load().get(name, []))
        return self._cache[name]

    def rect(self):
        return skia.Rect.MakeXYWH(self.x, self.y, self.w, self.h)

    def draw_land(self, c, fill='#1d3557', stroke='#2c4a73', sw=2, a=255, skip=()):
        for n, polys in _load().items():
            if n in skip or n == 'Antarctica':
                continue
            p = self.country_path(n)
            c.drawPath(p, _paint(fill, a))
            if stroke:
                c.drawPath(p, _paint(stroke, a, stroke=sw))

    def draw_country(self, c, name, fill='#ffd23f', stroke='#ffffff', sw=3, a=255, glow=False):
        p = self.country_path(name)
        if glow:
            c.drawPath(p, _paint(fill, int(a * 0.55), blur=18))
        c.drawPath(p, _paint(fill, a))
        if stroke:
            c.drawPath(p, _paint(stroke, a, stroke=sw))

    def meridian(self, c, lon, color='#ffffff', a=60, sw=2):
        X, _ = self.xy(lon, 0)
        c.drawLine(X, self.y, X, self.y + self.h, _paint(color, a, stroke=sw))

    def band(self, c, lon_a, lon_b, color, a=40):
        Xa, _ = self.xy(lon_a, 0); Xb, _ = self.xy(lon_b, 0)
        c.drawRect(skia.Rect.MakeLTRB(Xa, self.y, Xb, self.y + self.h), _paint(color, a))


def _paint(hexcol, a=255, stroke=None, blur=None):
    h = hexcol.lstrip('#')
    p = skia.Paint(AntiAlias=True, Color=skia.Color(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a))
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(stroke)
        p.setStrokeJoin(skia.Paint.kRound_Join); p.setStrokeCap(skia.Paint.kRound_Cap)
    if blur:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    return p


def pulse_dot(c, x, y, t, color='#ff4d4d', r=12, period=1.4, phase=0.0, a=255):
    k = ((t + phase) % period) / period
    c.drawCircle(x, y, r + 46 * k, _paint(color, int(a * 0.55 * (1 - k)), stroke=5))
    c.drawCircle(x, y, r * 1.8, _paint(color, int(a * 0.35), blur=10))
    c.drawCircle(x, y, r, _paint(color, a))
    c.drawCircle(x, y, r, _paint('#ffffff', a, stroke=3))


def stars(c, w, h, t, n=120, seed=3, a=160):
    import random
    rnd = random.Random(seed)
    for _ in range(n):
        x, y, s, ph = rnd.random() * w, rnd.random() * h, rnd.choice([1.5, 2, 2.5, 3]), rnd.random() * 6
        c.drawCircle(x, y, s, _paint('#ffffff', int(a * (0.5 + 0.5 * math.sin(t * 2 + ph)))))
