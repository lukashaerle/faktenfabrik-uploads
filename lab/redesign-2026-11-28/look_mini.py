"""LOOK 2 „MINIATUR“ – isometrische 3D-Miniaturwelt: Objekte mit Licht und Schatten, langsame Kamerafahrt, Petrol-Grund."""
from core import *
from math import sin, cos, pi, radians

CREAM, BASE, CORAL, INKP, WHITE, PAPER = '#F0E9DB', '#C9BEA8', '#FF6B4A', '#14272B', '#FFFFFF', '#FBF8F1'
BIN, BIN_D, BIN_L, LIDC, LIDT = '#8FA0AC', '#788993', '#A9B8C2', '#B4C1CA', '#C9D4DB'
TONE = dict(px=0.68, pz=0.86, py=1.0, nx=0.56, nz=0.52, ny=0.40)
TINT = np.array([10, 39, 44]) / 255.0
LX, LZ = 0.30, -0.18                                   # Schattenversatz je Höheneinheit (Licht von links vorn oben)
T_NOCH, T_WEG, T_GELTEN, T_REGEL = wt('noch'), wt('weg'), wt('gelten'), wt('Regel')
T_DREI, T_FRIST, T_STARTET, T_ENDE, T_KAUF = wt('drei'), wt('Frist'), wt('startet'), wt('Ende'), wt('Kaufjahres')
T_BAR0, T_BAR1 = T_KAUF + 0.08, T_KAUF + 0.88
T_END = T_BAR1
XB = [-300, -150, 0, 150, 300]; Z0, Z1, HB, ZP = -10, 130, 56, 60
XP0, XP1 = -300 + 150 * (2.5 / 12), -150
BH, BR0, BR1, BRL = 236, 100, 126, 136                # Eimer: Höhe, Radius unten/oben, Deckel
CAP = dict(font='bold', size=56, y=1392, fg='#ffffff', dim=0.45, hi=CORAL, shadow=True)
SFX = [(T_NOCH + 0.08, 'thud', 0.8), (T_WEG - 0.04, 'pop', 0.9), (1.97, 'whoosh', 0.35)] + \
      [(T_GELTEN - 0.02 + i * 0.10, 'pop', 0.55) for i in range(4)] + \
      [(T_REGEL + 0.12, 'tick', 1.0), (T_DREI, 'thud', 0.8), (T_FRIST, 'pop', 0.8), (T_ENDE - 0.06, 'thud', 0.6),
       (T_BAR0 + 0.27, 'tick', 1.0), (T_BAR0 + 0.53, 'tick', 1.0), (T_END, 'thud', 1.0)]


def hex3(h):
    h = h.lstrip('#'); return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)]) / 255.0


def shade(col, n):
    tone = n[0] ** 2 * (TONE['px'] if n[0] > 0 else TONE['nx']) + n[1] ** 2 * (TONE['py'] if n[1] > 0 else TONE['ny']) + n[2] ** 2 * (TONE['pz'] if n[2] > 0 else TONE['nz'])
    rgb = hex3(col) * tone; rgb = rgb + (TINT - rgb) * (1 - tone) * 0.30
    return skia.Color(int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))


# ---------------------------------------------------------------- Mini-3D
def prism(poly, y0, y1, col, layer=2, top_col=None, decal=None, sides=True, flat=False):
    poly = np.array(poly, float); cen = poly.mean(0)
    F = [dict(p=np.array([[x, y1, z] for x, z in poly]), n=np.array([0, 1.0, 0]), col=top_col or col, layer=layer, decal=decal, flat=flat)]
    if sides:
        for i in range(len(poly)):
            a, b = poly[i], poly[(i + 1) % len(poly)]; d = b - a; nn = np.array([d[1], 0.0, -d[0]])
            if nn[0] * ((a + b) / 2 - cen)[0] + nn[2] * ((a + b) / 2 - cen)[1] < 0:
                nn = -nn
            F.append(dict(p=np.array([[a[0], y0, a[1]], [b[0], y0, b[1]], [b[0], y1, b[1]], [a[0], y1, a[1]]]), n=nn / np.linalg.norm(nn), col=col, layer=layer))
    return F


def box(x0, x1, z0, z1, y0, y1, col, **kw):
    return prism([(x0, z0), (x1, z0), (x1, z1), (x0, z1)], y0, y1, col, **kw)


def circle(cx, cz, r, n=48):
    return [(cx + r * cos(2 * pi * i / n), cz + r * sin(2 * pi * i / n)) for i in range(n)]


def rrpoly(w, d, r, seg=5):
    pts = []
    for (cx, cz, a0) in ((w / 2 - r, d / 2 - r, 0), (-w / 2 + r, d / 2 - r, 90), (-w / 2 + r, -d / 2 + r, 180), (w / 2 - r, -d / 2 + r, 270)):
        for k in range(seg + 1):
            a = radians(a0 + 90 * k / seg); pts.append((cx + r * cos(a), cz + r * sin(a)))
    return pts


def frustum(cx, cz, r0, r1, y0, y1, col, n=48, layer=2, top_col=None, alt=None, bottom=None, clip=False):
    """Kegelstumpf. alt=(k, farbe): jede k-te Facette dunkler (Rillen). clip: unter y=0 abschneiden."""
    if clip:
        if y1 <= 0.5:
            return []
        if y0 < 0:
            r0 = r0 + (r1 - r0) * (0 - y0) / (y1 - y0); y0 = 0.0
    F = []
    for i in range(n):
        a0, a1 = 2 * pi * i / n, 2 * pi * (i + 1) / n; am = (a0 + a1) / 2
        p = [[cx + r0 * cos(a0), y0, cz + r0 * sin(a0)], [cx + r0 * cos(a1), y0, cz + r0 * sin(a1)], [cx + r1 * cos(a1), y1, cz + r1 * sin(a1)], [cx + r1 * cos(a0), y1, cz + r1 * sin(a0)]]
        nn = np.array([cos(am), (r0 - r1) / max(1e-6, (y1 - y0)), sin(am)])
        F.append(dict(p=np.array(p), n=nn / np.linalg.norm(nn), col=(alt[1] if alt and i % alt[0] == 0 else col), layer=layer))
    F.append(dict(p=np.array([[x, y1, z] for x, z in circle(cx, cz, r1, n)]), n=np.array([0, 1.0, 0]), col=top_col or col, layer=layer))
    if bottom:
        F.append(dict(p=np.array([[x, y0, z] for x, z in circle(cx, cz, r0, n)]), n=np.array([0, -1.0, 0]), col=bottom, layer=layer))
    return F


def Rx(a): c, s = cos(a), sin(a); return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
def Ry(a): c, s = cos(a), sin(a); return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
def Rz(a): c, s = cos(a), sin(a); return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def xf(F, R=None, t=(0, 0, 0)):
    out = []; t = np.array(t, float)
    for f in F:
        g = dict(f); p, n = f['p'], f['n']
        if R is not None:
            p = p @ R.T; n = R @ n
        g['p'], g['n'] = p + t, n / max(1e-9, float(np.linalg.norm(n)))
        if f.get('decal'):
            O, U, V, fn = f['decal']
            if R is not None:
                O, U, V = R @ O, R @ U, R @ V
            g['decal'] = (O + t, U, V, fn)
        out.append(g)
    return out


class Cam:
    def __init__(s, yaw, pitch, sc, cx, cy):
        s.c1, s.s1, s.cp, s.sp, s.sc, s.cx, s.cy = cos(yaw), sin(yaw), cos(pitch), sin(pitch), sc, cx, cy
        s.view = np.array([s.s1 * s.cp, s.sp, s.c1 * s.cp])

    def lin(s, v):
        x1 = v[0] * s.c1 - v[2] * s.s1; z1 = v[0] * s.s1 + v[2] * s.c1
        return s.sc * x1, -s.sc * (v[1] * s.cp - z1 * s.sp)

    def pt(s, v):
        a, b = s.lin(v); return s.cx + a, s.cy + b


def fpath(cam, pts):
    path = skia.Path(); q = [cam.pt(p) for p in pts]; path.moveTo(*q[0])
    for a in q[1:]:
        path.lineTo(*a)
    path.close(); return path


def draw_faces(c, cam, F):
    vis = [f for f in F if float(np.dot(f['n'], cam.view)) > 1e-4]
    vis.sort(key=lambda f: (f['layer'], float(np.dot(f['p'].mean(0), cam.view))))
    for f in vis:
        path = fpath(cam, f['p']); col = C(f['col']) if f.get('flat') else shade(f['col'], f['n'])
        pa = skia.Paint(AntiAlias=True); pa.setColor(col); c.drawPath(path, pa)
        pa.setStyle(skia.Paint.kStroke_Style); pa.setStrokeWidth(1.1); c.drawPath(path, pa)
        if f.get('decal'):
            O, U, V, fn = f['decal']; ox, oy = cam.pt(O); ux, uy = cam.lin(U); vx, vy = cam.lin(V)
            c.save(); c.clipPath(path, True); c.concat(skia.Matrix.MakeAll(ux, vx, ox, uy, vy, oy, 0, 0, 1)); fn(c); c.restore()


def hull(pts):
    pts = sorted(set((round(x, 2), round(y, 2)) for x, y in pts))
    if len(pts) < 3:
        return pts
    def half(seq):
        h = []
        for p in seq:
            while len(h) >= 2 and (h[-1][0] - h[-2][0]) * (p[1] - h[-2][1]) - (h[-1][1] - h[-2][1]) * (p[0] - h[-2][0]) <= 0:
                h.pop()
            h.append(p)
        return h
    lo, up = half(pts), half(pts[::-1])
    return lo[:-1] + up[:-1]


def shadow(c, cam, pts3, a=0.24, blur=9, ground=True, y=0.4):
    """Weicher Schlagschatten auf der Plattform."""
    P2 = []
    for p in pts3:
        h = max(0.0, p[1])
        if ground:
            P2.append((p[0], p[2]))
        P2.append((p[0] + LX * h, p[2] + LZ * h))
    h_ = hull(P2)
    if len(h_) >= 3:
        c.drawPath(fpath(cam, [(x, y, z) for x, z in h_]), P('#04161A', a, blur=blur))


# ---------------------------------------------------------------- Szene
def card_decal(c):
    c.drawRect(skia.Rect.MakeWH(372, 236), lin(0, 0, 372, 236, [C('#ffffff', 0.0), C('#8A7B5C', 0.10)]))
    c.drawRect(skia.Rect.MakeXYWH(46, 0, 40, 236), P(CORAL))
    c.drawRect(skia.Rect.MakeXYWH(46, 0, 7, 236), P('#000000', 0.10))
    for sx in (-1, 1):                                               # Schleife
        c.save(); c.translate(66, 112); c.scale(sx, 1)
        pth = skia.Path(); pth.moveTo(0, 0); pth.cubicTo(18, -34, 62, -40, 58, -6); pth.cubicTo(56, 14, 22, 10, 0, 0); pth.close()
        c.drawPath(pth, P('#E9512F')); c.restore()
    rrect(c, 52, 98, 28, 28, 7, P('#D4421F'))
    text(c, 'GUTSCHEIN', 132, 84, font('black', 35), P(INKP), 'l', 2.5)
    text(c, '50 €', 128, 190, font('black', 106), P(INKP), 'l', -2)


def lid_decal(c):
    c.drawCircle(BRL, BRL, BRL - 15, P('#7F8E98'))
    c.drawCircle(BRL, BRL, BRL - 15, P('#5F6E78', 0.55, stroke=3))
    c.drawCircle(BRL, BRL, BRL - 52, P('#8A99A3'))


def inner_decal(c):
    r = BR1 - 8
    c.drawRect(skia.Rect.MakeWH(2 * r, 2 * r), lin(0, 0, 0, 2 * r, [C('#35424A'), C('#141C20'), C('#0B1013')], [0, 0.55, 1]))


CARD = prism(rrpoly(372, 236, 20), 0, 9, PAPER, layer=6, decal=(np.array([-186, 9.3, -118]), np.array([1.0, 0, 0]), np.array([0, 0, 1.0]), card_decal))
PLAT = prism(rrpoly(680, 480, 64, 8), -44, 0, CREAM, layer=0) + prism(rrpoly(652, 452, 54, 8), -70, -44, BASE, layer=-1)
_BG = None


def background(c):
    global _BG
    if _BG is None:
        s = skia.Surface(W, H); b = s.getCanvas()
        b.drawRect(skia.Rect.MakeWH(W, H), lin(0, 0, 0, H, [C('#16505A'), C('#0E3A42'), C('#082126')], [0, 0.55, 1]))
        b.drawRect(skia.Rect.MakeWH(W, H), rad(520, 900, 900, [C('#4A98A0', 0.40), C('#4A98A0', 0.0)]))
        b.drawRect(skia.Rect.MakeWH(W, H), rad(540, 960, 1280, [C('#000000', 0.0), C('#000000', 0.0), C('#000000', 0.40)], [0, 0.55, 1]))
        _BG = s.makeImageSnapshot()
    c.drawImage(_BG, 0, 0)


def label(c, ax, ay, s, dx, dy, k, fg=WHITE, bg='#0B2A2F', size=30, a=1.0):
    """Bildschirm-Etikett mit Führungslinie zum Objekt."""
    if k <= 0 or a <= 0:
        return
    f = font('mono', size); w = tw(s, f, 2.5) + 40; x, y = ax + dx, ay + dy; hh = size + 30
    c.drawLine(ax, ay, x, y + hh / 2 - 4, P(WHITE, 0.8 * a * k, stroke=3)); c.drawCircle(ax, ay, 6.5, P(WHITE, a * k))
    c.save(); c.translate(x, y); c.scale(back(k, 1.5), back(k, 1.5))
    rrect(c, -w / 2, -hh / 2, w, hh, 11, P(bg, a)); rrect(c, -w / 2, -hh / 2, w, hh, 11, P(fg, 0.40 * a, stroke=2))
    text(c, s, -w / 2 + 20, size * 0.36, f, P(fg, a), 'l', 2.5)
    c.restore()


def bin_faces(d, th):
    """Eimer im Ursprung. d = wie weit er in die Plattform gefahren ist, th = Deckelwinkel (0 = zu)."""
    top = BH - d; F = []
    F += frustum(0, 0, BR0, BR1, -d, top, BIN, 56, layer=2, alt=(4, BIN_D), clip=True)
    F += frustum(0, 0, BR1 + 6, BR1 + 6, top - 18, top, BIN_L, 56, layer=3, top_col=BIN_L, clip=True)
    if top > 1:
        r = BR1 - 8
        F += prism(circle(0, 0, r, 56), top + 0.3, top + 0.4, '#10181C', layer=4, sides=False, flat=True,
                   decal=(np.array([-r, top + 0.5, -r]), np.array([1.0, 0, 0]), np.array([0, 0, 1.0]), inner_decal))
    if th == 0:
        F += frustum(0, 0, BRL, BRL, top, top + 12, LIDC, 56, layer=5, top_col=LIDC, clip=True)
        F += frustum(0, 0, BRL - 22, BRL - 40, top + 12, top + 22, LIDC, 56, layer=5, top_col=LIDT, clip=True)
    else:
        lid = frustum(0, BRL, BRL, BRL, 0, 12, LIDC, 56, layer=5, top_col=LIDC, bottom='#9BAAB4') + \
              frustum(0, BRL, BRL - 22, BRL - 40, 12, 22, LIDC, 56, layer=5, top_col=LIDT)
        for fc in lid:
            if fc['n'][1] < -0.5:
                fc['decal'] = (np.array([-BRL, -0.3, 0.0]), np.array([1.0, 0, 0]), np.array([0, 0, 1.0]), lid_decal)
        F += xf(lid, Rx(th), (0, top, -BRL))
    return F


def pin(c, cam, x, y, col):
    """Markierung (Kugel auf Stab) über dem Zeitstrahl; y = Höhe des Stabfußes über dem Block."""
    gx, gy = cam.pt((x + LX * y * 0.6, HB + 0.5, ZP + LZ * y * 0.6))
    c.drawOval(skia.Rect.MakeXYWH(gx - 20, gy - 8, 44, 17), P('#04161A', 0.30 * (1 - 0.5 * clamp(y / 200, 0, 1)), blur=5))
    bx, by = cam.pt((x, HB + y, ZP)); hx, hy = cam.pt((x, HB + y + 64, ZP)); r = 23 * cam.sc
    c.drawLine(bx, by, hx, hy, P('#DAD3C4', 1.0, stroke=6)); c.drawLine(bx - 1.5, by, hx - 1.5, hy, P('#ffffff', 0.9, stroke=2))
    lite, dark = mix(col, '#ffffff', 0.45), mix(col, '#10262A', 0.42)
    c.drawCircle(hx, hy, r, rad(hx - r * 0.38, hy - r * 0.42, r * 1.55, [C(lite), C(col), C(dark)], [0, 0.5, 1]))
    return hx, hy - r


def draw(c, t):
    background(c)
    cam = Cam(radians(21 + 0.9 * t), radians(34), 1.16 + 0.003 * t, 530, 990)
    c.drawOval(skia.Rect.MakeLTRB(60, 1205, 1010, 1410), P('#020E10', 0.60, blur=44))
    draw_faces(c, cam, PLAT)
    ptop = fpath(cam, PLAT[0]['p'])
    c.save(); c.clipPath(ptop, True)
    c.drawPaint(lin(90, 1160, 960, 800, [C('#ffffff', 0.12), C('#ffffff', 0.0), C('#3B2A10', 0.10)], [0, 0.5, 1]))
    c.restore()
    c.drawPath(ptop, P('#ffffff', 0.50, stroke=2.5))
    kt = eio(pr(t, 1.95, 0.6))
    # --- Karte: fällt offen lesbar, landet auf dem Deckel, schwebt dann als Held über der Szene
    f = pr(t, 0, T_NOCH + 0.20); fe = f ** 1.7; bob = sin(t * 1.9) * kt
    set_ = 3.5 * sin(pi * pr(t, T_NOCH + 0.20, 0.22)) * (1 - pr(t, T_NOCH + 0.20, 0.22))
    p_fall = np.array([lerp(255, 0, f), lerp(596, BH + 23, fe) - set_, lerp(40, 0, f)])
    pos = p_fall + (np.array([222, 318 + 7 * bob, -60]) - p_fall) * kt
    R = Ry(radians(lerp(lerp(16, 9, f), -5, kt))) @ Rz(radians(lerp(lerp(13, 0, f), 1.5 * bob, kt))) @ Rx(radians(lerp(lerp(38, 0, fe), 27, kt))) * lerp(1.0, 0.9, kt)
    card = xf(CARD, R, pos)
    d = (BH + 30) * ei3(pr(t, 1.95, 0.5))                             # Eimer fährt in die Plattform
    F = []; SH = []
    kh = eo3(pr(t, 1.90, 0.10)) * (1 - eio(pr(t, 2.42, 0.26)))
    if kh > 0:
        F += prism(circle(0, 0, (BRL + 9) * kh, 56), 0.1, 0.2, '#0A1C1F', layer=1, sides=False, flat=True)
    if d < BH + 24:
        th = radians(lerp(-92, 0, ei3(pr(t, T_NOCH - 0.12, 0.20))))
        bf = bin_faces(d, th); F += bf
        SH.append(([(x, BH - d, z) for x, z in circle(0, 0, BRL, 20)] + [(x, 0, z) for x, z in circle(0, 0, BR0, 20)], 0.26, 10, True))
        SH.append(([(x, 0, z) for x, z in circle(0, 0, BR0 + 9, 24)], 0.36, 5, True))
        if th != 0:
            SH.append(([tuple(p) for fc in bf if fc['layer'] == 5 for p in fc['p'][::2]][::6], 0.16, 12, True))
    # --- Jahresblöcke wachsen aus der Plattform
    bx = lerp(XB[1], XB[4], eio(pr(t, T_BAR0, T_BAR1 - T_BAR0)))
    for i in range(4):
        k = pr(t, T_GELTEN - 0.10 + i * 0.10, 0.40)
        if k <= 0:
            continue
        h = max(1.0, HB * back(k, 1.3)); yr = str(2023 + i)
        dec = (np.array([XB[i], h + 0.3, Z0]), np.array([1.0, 0, 0]), np.array([0, 0, 1.0]),
               (lambda yr: lambda cc: text(cc, yr, 75, 93, font('cond', 66), P(INKP, 0.90), 'c', 1.5))(yr))
        F += box(XB[i] + 3, XB[i + 1] - 3, Z0, Z1, 0, h, '#F6F1E6', decal=dec)
        SH.append(([(XB[i] + 3, h, Z0), (XB[i + 1] - 3, h, Z0), (XB[i + 1] - 3, h, Z1), (XB[i] + 3, h, Z1)], 0.22, 7, True))
        SH.append(([(XB[i] - 3, 0, Z0 - 5), (XB[i + 1] + 3, 0, Z0 - 5), (XB[i + 1] + 3, 0, Z1 + 6), (XB[i] - 3, 0, Z1 + 6)], 0.30 * clamp(h / HB, 0, 1), 4, True))
    if t >= T_BAR0:                                                   # der 3-Jahres-Streifen
        def strip(cc):
            for j in (1, 2, 3):
                text(cc, str(2023 + j), XB[j] - XB[1] + 75, 93, font('cond', 66), P(WHITE), 'c', 1.5)
        F += box(XB[1] + 3, max(XB[1] + 8, bx - 3), Z0, Z1, HB, HB + 8, CORAL, layer=3,
                 decal=(np.array([XB[1], HB + 8.3, Z0]), np.array([1.0, 0, 0]), np.array([0, 0, 1.0]), strip))
    # --- Zielfahne am Ende von 2026
    kf = pr(t, T_END - 0.05, 0.30)
    if kf > 0:
        hp = 172 * eo3(kf); ks = back(pr(t, T_END + 0.10, 0.34), 1.5); y0 = HB + 8
        F += frustum(XB[4] - 8, ZP, 5.5, 5.5, y0, y0 + hp, '#F6F1E6', 14, layer=5)
        if ks > 0:
            F.append(dict(p=np.array([[XB[4] - 8, y0 + hp - 4, ZP], [XB[4] - 8, y0 + hp - 84, ZP], [XB[4] - 8 - 150 * ks, y0 + hp - 44, ZP]]),
                          n=np.array([0, 0, 1.0]), col='#FF7453', layer=5, flat=True))
        SH.append(([(XB[4] - 12, 0, ZP - 4), (XB[4] - 4, 0, ZP + 4), (XB[4] - 8, hp + y0, ZP)], 0.20, 5, True))
    F += card
    SH.append(([tuple(p) for p in card[0]['p']], lerp(0.22, 0.17, kt), lerp(10, 20, kt), False))
    c.save(); c.clipPath(ptop, True)
    for pts, a, bl, gr in SH:
        shadow(c, cam, pts, a, bl, gr)
    c.restore()
    draw_faces(c, cam, F)
    # --- Kauf-Marke: fällt auf März 2023, springt dann ans Jahresende
    kp = pr(t, T_REGEL - 0.10, 0.25); pin_xy = None
    if kp > 0:
        kh2 = eio(pr(t, T_STARTET, T_ENDE - T_STARTET - 0.05)); px = lerp(XP0, XP1, kh2)
        py = 260 * (1 - ei2(kp)) + 92 * sin(pi * kh2) + (8 if (t >= T_BAR0 and px > XB[1] - 3) else 0)
        pin_xy = pin(c, cam, px, py, mix('#F6F1E6', CORAL, pr(t, T_FRIST - 0.05, 0.18)))
    # --- Bildschirm-Ebene: Etiketten, Überschrift, Kopfzeile, Untertitel
    cx, cy = cam.pt(pos + np.array([0, 12, 0]))
    label(c, cx + 120, cy - 52, 'NOCH GÜLTIG?', 104, -126, pr(t, T_WEG - 0.05, 0.26), fg=WHITE, bg=CORAL, size=32, a=1 - pr(t, 1.95, 0.2))
    if pin_xy:
        label(c, pin_xy[0], pin_xy[1] - 6, 'GEKAUFT 03/2023', 14, -92, pr(t, T_REGEL + 0.10, 0.25), a=1 - pr(t, T_STARTET - 0.05, 0.25))
        label(c, pin_xy[0], pin_xy[1] - 6, 'START 31.12.2023', -10, -92, pr(t, T_ENDE - 0.03, 0.26), fg='#FF8A6E')
    k3 = pr(t, T_DREI - 0.02, 0.30)
    if k3 > 0:
        f3, fj = font('black', 204), font('black', 110); w3 = f3.measureText('3'); sc = lerp(0.88, 1.0, back(k3, 1.5))
        c.save(); c.translate(80, 478); c.scale(sc, sc)
        c.drawString('3', 0, 0, f3, P(CORAL, eo3(k3))); c.drawString('JAHRE', w3 + 24, 0, fj, P(WHITE, eo3(k3)))
        c.restore()
    ke = pr(t, T_END + 0.05, 0.32)
    if ke > 0:
        c.save(); c.translate(84, 556 + 16 * (1 - eo3(ke)))
        text(c, 'gültig bis 31.12.2026', 0, 0, font('xbold', 56), P(WHITE, eo3(ke)), 'l')
        c.restore()
    text(c, 'FAKTENFABRIK', 84, 268, font('mono', 25), P(WHITE, 0.82), 'l', 7)
    text(c, '04', 996, 268, font('mono', 25), P(WHITE, 0.82), 'r', 2)
    chip(c, 'KLEINGEDRUCKT', 940, 238, font('mono', 22), WHITE, CORAL, padx=16, pady=11, r=7, align='r', track=4)
    c.drawLine(84, 302, 996, 302, P(WHITE, 0.16, stroke=2.5))
    captions(c, t, CAP)


if __name__ == '__main__':
    import sys
    if sys.argv[1] == 'sheet':
        sheet(draw, [0.0, 0.9, 1.5, 2.25, 3.9, 4.6, 6.4, 7.6, 8.3, 9.9], LAB + '/out/mini_sheet.png', 0.25, 5)
    elif sys.argv[1] == 'big':
        sheet(draw, [float(x) for x in sys.argv[2:]], LAB + '/out/mini_big.png', 0.46, 2)
    else:
        build_audio(10.0, SFX, LAB + '/out/mini.wav'); render(draw, 10.0, LAB + '/out/LOOK2_MINIATUR.mp4', LAB + '/out/mini.wav')
