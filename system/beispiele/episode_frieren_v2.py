"""Episode: Warum frieren Frauen schneller? – EDITING V2 „Dunkel & Leuchtend" (21.11.2026).
Gleiche Stimme und gleiches Skript wie ep_frieren; neu sind Look, Schnitt und Untertitel."""
import math
import render as L
import edit2 as E2
from render import skia, W, H, P, clamp, ease, ease_out, lerp, mixc, word_t
from edit2 import ICE, ICE2, HEAT, HEAT2, GOLD, INKW, DIM, heat, kin

EDIT = 2
TOPIC = 'WARUM FRIEREN FRAUEN SCHNELLER?'
HOOK_TEXT = 'SIE FRIERT,\nER SCHWITZT.'
HOOK_COLORS = [ICE, HEAT]
HOOK_END = 2.22
HIGHLIGHT = ['schneller?', 'Bürotemperatur', 'Einbildung', 'Biologie?', 'wärmer.', 'Hände:', 'eineinhalb', 'kälter.',
             'Muskeln.', 'Heizung', 'Organe.', 'Auflösung:', 'Sechzigern.', '40-jährigen', 'Mann', '70', '20', '32',
             'Biologie.', 'Markier']

COLD = dict(core=0.44, head=0.36, arms=0.16, hands=0.0, legs=0.14, feet=0.0)
HOT = dict(core=0.97, head=0.92, arms=0.86, hands=0.8, legs=0.8, feet=0.72)
NORM = dict(core=0.84, head=0.76, arms=0.66, hands=0.56, legs=0.6, feet=0.5)


# ---------------------------------------------------------------- Motive
def halo(c, x, y, r, color, a=70):
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeRadial(skia.Point(x, y), r, [L.col(color, a), L.col(color, 0)]))
    c.drawCircle(x, y, r, p)


def dial(c, cx, cy, r, val, t, color=None):
    """Thermostat-Rad: Ring mit Skala (blau → orange) und Zeiger. val 0..1."""
    rect = skia.Rect.MakeXYWH(cx - r, cy - r, 2 * r, 2 * r)
    c.drawCircle(cx, cy, r, P('#0a1226', 230)); c.drawCircle(cx, cy, r, P(INKW, 255, stroke=7))
    inner = skia.Rect.MakeXYWH(cx - r * 0.78, cy - r * 0.78, r * 1.56, r * 1.56)
    for i in range(27):
        a0 = 135 + i * 10
        c.drawArc(inner, a0, 7, False, P(color or heat(i / 26), 255, stroke=r * 0.13, cap=False))
    for i in range(10):
        an = math.radians(135 + i * 30)
        c.drawLine(cx + math.cos(an) * r * 0.56, cy + math.sin(an) * r * 0.56, cx + math.cos(an) * r * 0.62, cy + math.sin(an) * r * 0.62, P(INKW, 200, stroke=4))
    an = math.radians(135 + 270 * clamp(val))
    c.drawLine(cx, cy, cx + math.cos(an) * r * 0.6, cy + math.sin(an) * r * 0.6, P(INKW, 255, stroke=11))
    c.drawCircle(cx, cy, r * 0.11, P(INKW))


def padlock(c, cx, cy, s, k_open=0.0, color=GOLD):
    """Vorhängeschloss; k_open 0..1 klappt den Bügel auf."""
    c.save(); c.translate(cx, cy); c.scale(s, s)
    c.save(); c.translate(-95, -60); c.rotate(-38 * k_open); c.translate(95, 60 - 26 * k_open)
    sh = skia.Path(); sh.moveTo(-95, -60); sh.lineTo(-95, -150); sh.cubicTo(-95, -280, 95, -280, 95, -150); sh.lineTo(95, -60)
    c.drawPath(sh, P(color, 255, stroke=34))
    c.restore()
    body = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-160, -70, 320, 260), 40, 40)
    c.drawRRect(body, P(color, 70)); c.drawRRect(body, P(color, 255, stroke=10))
    c.drawCircle(0, 40, 30, P(color)); c.drawRect(skia.Rect.MakeXYWH(-11, 50, 22, 62), P(color))
    c.restore()


def cloud(c, cx, cy, s, color=ICE):
    """Gedankenwolke (Einbildung)."""
    c.save(); c.translate(cx, cy); c.scale(s, s)
    p = skia.Path()
    for (x, y, r) in [(-90, 10, 78), (-20, -50, 92), (70, -20, 82), (110, 40, 62), (20, 50, 86), (-60, 60, 66)]:
        p.addCircle(x, y, r)
    c.drawPath(p, P(color, 60)); c.drawPath(p, P(color, 255, stroke=7))
    c.drawCircle(-120, 150, 26, P(color, 255, stroke=7)); c.drawCircle(-160, 205, 15, P(color, 255, stroke=7))
    for i in range(3):                                           # Kringel = „nur im Kopf"
        q = skia.Path(); q.moveTo(-70 + i * 60, 10)
        q.cubicTo(-50 + i * 60, -30, -30 + i * 60, 50, -10 + i * 60, 10)
        c.drawPath(q, P(INKW, 220, stroke=7))
    c.restore()


def dna(c, cx, cy, h, t, color=HEAT, w=95, turns=2.2, a=255):
    """DNA-Doppelhelix, dreht sich langsam."""
    n = 44; pa, pb = skia.Path(), skia.Path(); pts = []
    for i in range(n + 1):
        u = i / n; y = cy - h / 2 + h * u; ph = u * turns * 2 * math.pi + t * 1.6
        xa, xb = cx + math.sin(ph) * w, cx - math.sin(ph) * w
        (pa.moveTo if i == 0 else pa.lineTo)(xa, y); (pb.moveTo if i == 0 else pb.lineTo)(xb, y)
        if i % 4 == 2:
            pts.append((xa, xb, y, math.cos(ph)))
    for xa, xb, y, z in pts:
        c.drawLine(xa, y, xb, y, P(mixc(color, '#ffffff', 0.35), int(a * (0.45 + 0.4 * abs(z))), stroke=6))
    c.drawPath(pa, P(color, a, stroke=10)); c.drawPath(pb, P(mixc(color, GOLD, 0.5), a, stroke=10))


def camera(c, cx, cy, s, color=INKW):
    """Wärmebild-Kamera, schaut nach rechts."""
    c.save(); c.translate(cx, cy); c.scale(s, s)
    body = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-150, -90, 250, 190), 28, 28)
    c.drawRRect(body, P(color, 40)); c.drawRRect(body, P(color, 255, stroke=8))
    c.drawRect(skia.Rect.MakeXYWH(100, -52, 70, 114), P(color, 255, stroke=8))
    c.drawCircle(170, 5, 62, P('#0a1226')); c.drawCircle(170, 5, 62, P(color, 255, stroke=8)); c.drawCircle(170, 5, 34, P(HEAT, 255, stroke=8))
    c.drawRect(skia.Rect.MakeXYWH(-110, -128, 90, 38), P(color, 255, stroke=8))
    c.drawRect(skia.Rect.MakeXYWH(-50, 100, 44, 150), P(color, 255, stroke=8))
    c.restore()


def flex(c, x, y, s, bulge, v):
    """Angewinkelter Arm mit Bizeps (Seitenansicht). (x, y) = Ellenbeuge. v = Wärme 0..1, bulge = Muskelgröße."""
    co, c2 = heat(v), heat(max(0.0, v - 0.22))
    c.save(); c.translate(x, y); c.scale(s, s)
    p = skia.Path(); p.moveTo(-250, 10)
    pk = -30 - 84 * bulge                                         # Höhe des Bizeps
    p.cubicTo(-228, -30 - 30 * bulge, -190, pk, -122, pk)
    p.cubicTo(-64, pk, -34, -86, -22, -46)
    p.lineTo(-16, -214); p.lineTo(72, -214); p.lineTo(76, 58)
    p.cubicTo(78, 108, 44, 126, 2, 126); p.lineTo(-250, 126)
    p.cubicTo(-284, 126, -284, 10, -250, 10); p.close()
    c.drawPath(p, E2._gp(co, c2, 0, -150, 0, 130, 105)); c.drawPath(p, E2._gp(co, c2, 0, -150, 0, 130, 255, stroke=7))
    c.drawCircle(28, -266, 64, P(c2, 105)); c.drawCircle(28, -266, 64, P(c2, 255, stroke=7))      # Faust
    for i in (0.35, 0.6, 0.85):                                  # Drahtgitter am Bizeps
        w_ = 190 * i
        c.drawArc(skia.Rect.MakeXYWH(-122 - w_ / 2, pk, w_, (10 - pk) * 1.7), 180, 180, False, P(co, 150, stroke=2.5))
    for yy in (-170, -120, -70, -10):
        c.drawArc(skia.Rect.MakeXYWH(-18, yy - 12, 92, 24), 0, 180, False, P(c2, 150, stroke=2.5))
    for xx in (-200, -150, -90, -30):
        c.drawArc(skia.Rect.MakeXYWH(xx - 12, 12, 24, 112), 270, 180, False, P(co, 130, stroke=2.5))
    c.restore()


def shield(c, cx, cy, s, color=GOLD, k=1.0):
    if k <= 0:
        return
    c.save(); c.translate(cx, cy); c.scale(s * (0.86 + 0.14 * k), s * (0.86 + 0.14 * k))
    p = skia.Path(); p.moveTo(0, -150); p.cubicTo(60, -120, 110, -116, 150, -116); p.cubicTo(150, 20, 110, 110, 0, 170)
    p.cubicTo(-110, 110, -150, 20, -150, -116); p.cubicTo(-110, -116, -60, -120, 0, -150)
    c.drawPath(p, P(color, int(46 * k))); c.drawPath(p, P(color, int(255 * k), stroke=9))
    c.restore()


def heart(c, cx, cy, s, color=HEAT2, beat=0.0):
    sc = s * (1 + 0.10 * beat)
    p = skia.Path(); p.moveTo(cx, cy + 44 * sc)
    p.cubicTo(cx - 80 * sc, cy - 6 * sc, cx - 46 * sc, cy - 64 * sc, cx, cy - 24 * sc)
    p.cubicTo(cx + 46 * sc, cy - 64 * sc, cx + 80 * sc, cy - 6 * sc, cx, cy + 44 * sc)
    c.drawPath(p, P(color, 235)); c.drawPath(p, P('#ffd9c9', 255, stroke=4))


def flame(c, cx, cy, s, t, color=HEAT):
    """Flamme (Stoffwechsel = eigene Wärme), züngelt leicht."""
    w = math.sin(t * 6) * 10
    for sc, colr, a in [(1.0, color, 110), (0.58, GOLD, 200)]:
        p = skia.Path(); p.moveTo(cx + w * 0.4, cy - 190 * s * sc)
        p.cubicTo(cx + 130 * s * sc, cy - 60 * s * sc, cx + 150 * s * sc, cy + 110 * s * sc, cx, cy + 170 * s * sc)
        p.cubicTo(cx - 150 * s * sc, cy + 110 * s * sc, cx - 110 * s * sc, cy - 20 * s * sc, cx - 50 * s * sc, cy - 70 * s * sc)
        p.cubicTo(cx - 30 * s * sc, cy - 20 * s * sc, cx - 10 * s * sc, cy - 110 * s * sc, cx + w * 0.4, cy - 190 * s * sc)
        c.save(); c.translate(0, (1 - sc) * 60 * s)
        c.drawPath(p, P(colr, a)); c.drawPath(p, P(colr, 255, stroke=7))
        c.restore()


def radiator(c, cx, cy, w, h, color=HEAT, k=1.0):
    """Heizkörper (Rippen + Ventil)."""
    n = 7; rw = w / n * 0.72
    for i in range(n):
        x = cx - w / 2 + (i + 0.5) * w / n
        r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - rw / 2, cy - h / 2, rw, h), rw / 2, rw / 2)
        c.drawRRect(r, P(color, int(95 * k))); c.drawRRect(r, P(color, int(255 * k), stroke=6))
    c.drawLine(cx - w / 2 - 26, cy + h / 2 - 34, cx + w / 2 + 26, cy + h / 2 - 34, P(color, int(255 * k), stroke=8))
    c.drawCircle(cx + w / 2 + 44, cy + h / 2 - 34, 18, P(color, int(255 * k), stroke=7))


def brackets(c, x0, y0, x1, y1, color=GOLD, ln=70, k=1.0, width=7):
    """Mess-Ecken um ein Motiv („das ist die Norm" / „wird vermessen")."""
    a = int(255 * k)
    for (x, y, dx, dy) in [(x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)]:
        c.drawLine(x, y, x + dx * ln, y, P(color, a, stroke=width)); c.drawLine(x, y, x, y + dy * ln, P(color, a, stroke=width))


# ---------------------------------------------------------------- Szenen
def s1(c, t, d):
    i, lt, ld = E2.shots(0, t, d, ['im', 'dieses', 'warum'])
    if i == 0:                                  # SIE FRIERT, ER SCHWITZT. – Cover: zwei Wärmebild-Figuren, bildfüllend
        E2.stage(c, '#5a4bff', spot=(0.5, 0.6))
        E2.push(c, lt)
        halo(c, 290, 1000, 520, ICE2, 110); halo(c, 800, 1000, 520, HEAT2, 110)
        def dr(cc):
            E2.figure(cc, 290, 1100, 1.2, female=True, temps=COLD, pose='hug', t=t, shiver=1, face='cold')
            E2.figure(cc, 780, 1100, 1.2, female=False, temps=HOT, pose='fan', t=t, face='hot')
            E2.flakes(cc, t, n=7, x0=70, x1=500, y0=600, y1=1500)
            E2.drops(cc, 780, 1100 - 372 * 1.2, 1.2, t, color='#ffe2b8')
            E2.waves(cc, 780, 640, 300, 110, t, color=HEAT, n=4, a=170)
        E2.glow(c, dr)
    elif i == 1:                                # Im selben Raum. – ein Thermostat, zwei Menschen
        E2.stage(c, '#7b5cff', spot=(0.5, 0.3))
        E2.push(c, lt)
        def dr(cc):
            dial(cc, 540, 560, 220, 0.5, lt)
            L.neon_path(cc, [(70, 1010), (70, 1500), (1010, 1500), (1010, 1010)], k=kin(lt, 0.0, 0.5), color=DIM, width=5, glow=False)
            E2.figure(cc, 300, 1300, 0.7, female=True, temps=COLD, pose='hug', t=t, shiver=1, face='cold')
            E2.figure(cc, 690, 1300, 0.7, female=False, temps=HOT, pose='fan', t=t, face='hot')
        E2.glow(c, dr)
    elif i == 2:                                # … in jeder Wohnung ausdiskutiert. – Fenster gehen an, überall Streit
        E2.stage(c, '#3f5cff', spot=(0.5, 0.45))
        E2.push(c, lt)
        def dr(cc):
            cc.drawRect(skia.Rect.MakeLTRB(165, 345, 915, 1470), P('#0a1226', 220))
            cc.drawRect(skia.Rect.MakeLTRB(165, 345, 915, 1470), P(DIM, 255, stroke=6))
            n = 0
            for r in range(5):
                for q in range(3):
                    x, y = 215 + q * 240, 400 + r * 210
                    on = lt > 0.15 + ((n * 7) % 15) * 0.13
                    colr = (ICE, HEAT)[(r + q) % 2]
                    rr = skia.Rect.MakeXYWH(x, y, 170, 150)
                    if on:
                        fl = 0.75 + 0.25 * math.sin(lt * 9 + n)
                        cc.drawRect(rr, P(colr, int(235 * fl))); cc.drawRect(rr, P(colr, 255, stroke=5))
                        cc.drawLine(x + 85, y, x + 85, y + 150, P('#0a1226', 255, stroke=5))
                    else:
                        cc.drawRect(rr, P(DIM, 120, stroke=4))
                    n += 1
        E2.glow(c, dr)
        E2.word(c, 'STREIT!', W / 2, 640, 200, '#ff6a4a', lt, E2.at(0, 'ausdiskutiert', default=6.0) - (t - lt))
    else:                                       # Warum frieren Frauen schneller? – Nahaufnahme + großes Fragezeichen
        E2.stage(c, ICE2, spot=(0.4, 0.4), strength=1.2)
        E2.push(c, lt)
        def dr(cc):
            E2.figure(cc, 400, 1200, 1.7, female=True, temps=COLD, pose='hug', t=t, shiver=1, face='cold')
            E2.flakes(cc, t, n=12, y0=320, y1=1500)
        E2.glow(c, dr)
        E2.word(c, '?', 850, 640, 380, GOLD, lt, 0.05, key='frage', snd='pop')


def s2(c, t, d):
    i, lt, ld = E2.shots(1, t, d, ['warum'])
    if i == 0:                                  # Und am Ende erfährst du … – Schloss: Auflösung am Ende
        E2.stage(c, '#b98a1f', spot=(0.5, 0.45))
        E2.push(c, lt)
        E2.glow(c, lambda cc: padlock(cc, 540, 900, 1.5))
        E2.tag(c, 'AUFLÖSUNG AM ENDE', 420, 1300, lt, 0.25, size=40)
        L.finn(c, 870, 1450, 0.8, t, mood='happy', arm_l=250, arm_r=-70, look=(-1, -1))
    else:                                       # … warum sogar die Bürotemperatur gegen Frauen gerechnet ist.
        E2.stage(c, '#5a4bff', spot=(0.5, 0.42))
        E2.push(c, lt)
        def dr(cc):
            box = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(250, 500, 830, 1100), 64, 64)
            cc.drawRRect(box, P('#0a1226', 235)); cc.drawRRect(box, P(INKW, 255, stroke=9))
            scr = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(300, 550, 780, 796), 26, 26)
            cc.drawRRect(scr, P(ICE2, 70)); cc.drawRRect(scr, P(ICE, 255, stroke=6))
            E2.text(cc, '?', 540, 756, 230, GOLD, k=kin(lt, 0.1, 0.2), shadow=False)
            for q, colr in enumerate([ICE, INKW, HEAT]):
                cc.drawCircle(400 + q * 140, 1002, 36, P(colr, 255, stroke=9))
            E2.figure(cc, 190, 1480, 0.5, female=True, temps=COLD, pose='hug', t=t, shiver=1, face='cold')
            for q in range(3):                  # Schreibtisch-Reihe
                cc.drawLine(400 + q * 160, 1520, 520 + q * 160, 1520, P(DIM, 255, stroke=7))
                cc.drawRect(skia.Rect.MakeXYWH(422 + q * 160, 1400, 76, 62), P(DIM, 255, stroke=6))
                cc.drawLine(460 + q * 160, 1462, 460 + q * 160, 1520, P(DIM, 255, stroke=6))
        E2.glow(c, dr)
        E2.tag(c, 'BÜRO-TEMPERATUR', 520, 1200, lt, E2.at(1, 'bürotemperatur', default=2.2) - (t - lt), size=42)


def s3(c, t, d):
    i, lt, ld = E2.shots(2, t, d, ['forscher'])
    if i == 0:                                  # Einbildung (oben) oder Biologie? (unten)
        E2.stage(c, '#5a4bff', spot=(0.5, 0.45))
        E2.push(c, lt)
        tb = E2.at(2, 'biologie', default=1.2)
        def dr(cc):
            cloud(cc, 540, 570, 1.25 * (0.85 + 0.15 * kin(lt, 0.0, 0.2)))
            if lt >= tb - 0.05:
                dna(cc, 540, 1240, 460, t, w=120)
        E2.glow(c, dr)
        if lt >= tb - 0.05:
            L.sfx('pop', ('dna',))
    else:                                       # Forscher aus Utah haben es gemessen. – Wärmebild-Kamera, zwei Versuchspersonen
        E2.stage(c, ICE2, spot=(0.55, 0.42))
        E2.push(c, lt)
        def dr(cc):
            camera(cc, 280, 600, 1.2)
            for q in range(4):
                u = ((lt * 1.2 + q / 4) % 1.0)
                cc.drawLine(500 + u * 150, 540 - u * 100, 500 + u * 150, 680 + u * 100, P(HEAT, int(230 * (1 - u)), stroke=7))
            E2.hand(cc, 810, 640, 0.95, tip=lerp(0.6, 0.06, ease(clamp((lt - 0.4) / 1.2))), wrist=0.6)
            E2.figure(cc, 330, 1390, 0.6, female=True, temps=dict(core=0.8, head=0.6, arms=0.35, hands=0.08, legs=0.3, feet=0.08), pose='stand', t=t, arm=12)
            E2.figure(cc, 640, 1390, 0.6, female=False, temps=NORM, pose='stand', t=t, arm=12)
            brackets(cc, 170, 1100, 800, 1610, ICE, k=kin(lt, 0.2, 0.3))
        E2.glow(c, dr)
        E2.tag(c, 'UNIVERSITY OF UTAH · 1998', 465, 1030, lt, E2.at(2, 'utah', default=2.7) - (t - lt), size=36)


def s4(c, t, d):
    i, lt, ld = E2.shots(3, t, d, ['aber', 'rund'])
    if i == 0:                                  # Die Körpermitte von Frauen ist … ein kleines bisschen wärmer.
        E2.stage(c, HEAT2, spot=(0.38, 0.4), strength=0.9)
        E2.push(c, lt)
        tw = E2.at(3, 'bisschen', default=3.0)
        hot = clamp((lt - 0.3) / 1.0)
        tp = dict(core=lerp(0.7, 1.0, hot), head=0.6, arms=0.45, hands=0.3, legs=0.4, feet=0.25)
        def dr(cc):
            E2.figure(cc, 400, 1010, 1.5, female=True, temps=tp, pose='stand', t=t, face=None, arm=14)
            E2.ring(cc, 400, 1010 - 165 * 1.5, 120, HEAT, lt, 0.3, every=1.2, n=2, width=6)
            if lt > tw:
                cc.drawLine(450, 760, 640, 660, P(GOLD, 255, stroke=6))
        E2.glow(c, dr)
        E2.tag(c, 'KÖRPERMITTE', 800, 560, lt, E2.at(3, 'körpermitte', default=0.35), size=38)
        E2.pill(c, 'ETWAS WÄRMER', 800, 660, 42, HEAT, k=kin(lt, tw, 0.18))
        if lt > tw:
            L.sfx('pop', ('waermer',))
    elif i == 1:                                # Aber ihre Hände:
        E2.stage(c, ICE2, spot=(0.5, 0.33))
        E2.push(c, lt)
        def dr(cc):
            E2.hand(cc, 290, 800, 1.2, tip=0.8, wrist=0.9)
            E2.hand(cc, 790, 800, 1.2, tip=0.03, wrist=0.5)
        E2.glow(c, dr)
        E2.tag(c, 'MANN', 290, 1250, lt, 0.05, size=46)
        E2.tag(c, 'FRAU', 750, 1250, lt, 0.05, size=46)
    else:                                       # rund eineinhalb Grad kälter. – Vollbild-Zahl
        E2.impact(c, lt, '−1,5 °C', sub='IM SCHNITT KÄLTER', color=ICE, top='HÄNDE VON FRAUEN', tint=ICE2)
        def dr(cc):
            E2.hand(cc, 330, 1290, 0.6, tip=0.8, wrist=0.9)
            E2.hand(cc, 690, 1290, 0.6, tip=0.03, wrist=0.5)
        E2.glow(c, dr, a=0.7)


def s5(c, t, d):
    i, lt, ld = E2.shots(4, t, d, ['frauen', 'und'])
    if i == 0:                                  # Aber warte, es wird noch besser. – FINN unterbricht
        E2.stage(c, '#8a5cf6', spot=(0.5, 0.4), strength=1.3)
        E2.push(c, lt)
        for q in range(12):                     # ruhiger Strahlenkranz hinter FINN
            an = math.radians(q * 30 + 15)
            c.drawLine(540 + math.cos(an) * 420, 720 + math.sin(an) * 420, 540 + math.cos(an) * 590, 720 + math.sin(an) * 590, P(GOLD, 200, stroke=12))
        k = kin(lt, 0.0, 0.2)
        L.finn(c, 540, 730, 1.75 * (0.85 + 0.15 * k), t, mood='shock', arm_l=250, arm_r=-70, look=(0, 0))
        if lt > 0.05:
            L.sfx('pop', ('finn',))
    elif i == 1:                                # Frauen haben im Schnitt weniger Muskeln.
        E2.stage(c, HEAT2, spot=(0.4, 0.45), strength=0.9)
        E2.push(c, lt)
        def dr(cc):
            flex(cc, 400, 900, 1.45, 1.35, 0.95)
            flex(cc, 850, 930, 1.0, 0.7, 0.62)
        E2.glow(c, dr)
        E2.tag(c, 'MANN', 290, 1200, lt, 0.05, size=46)
        E2.tag(c, 'FRAU', 750, 1200, lt, 0.05, size=46)
        tw = E2.at(4, 'weniger', default=3.3) - (t - lt)
        E2.pill(c, 'WENIGER MUSKELN', 760, 520, 42, GOLD, k=kin(lt, tw, 0.18))
        if lt > tw:
            L.sfx('pop', ('weniger',))
    else:                                       # Und Muskeln sind die Heizung des Körpers.
        E2.stage(c, HEAT2, spot=(0.45, 0.42), strength=1.4)
        E2.push(c, lt)
        def dr(cc):
            E2.waves(cc, 440, 640, 420, 250, t, color=HEAT, n=5)
            flex(cc, 640, 990, 1.8, 1.35, 1.0)
        th = E2.at(4, 'heizung', default=5.6) - (t - lt)
        kh = kin(lt, th, 0.16)
        def dr2(cc):
            if kh > 0:
                radiator(cc, 465, 1395, 560 * (0.9 + 0.1 * kh), 240, HEAT, kh)
        E2.glow(c, lambda cc: (dr(cc), dr2(cc)))
        if lt > th:
            L.sfx('thud', ('heizung',))


def s6(c, t, d):
    i, lt, ld = E2.shots(5, t, d, ['hände'])
    if i == 0:                                  # Wird es kalt, schützt der Körper zuerst die Organe.
        E2.stage(c, ICE2, spot=(0.5, 0.42), strength=1.1)
        E2.push(c, lt)
        ts = E2.at(5, 'schützt', default=0.84)
        beat = max(0.0, math.sin(t * 7.5)) ** 4
        def dr(cc):
            E2.flakes(cc, t, n=14, y0=320, y1=1500)
            E2.figure(cc, 540, 1010, 1.5, female=True, temps=dict(core=0.95, head=0.6, arms=0.35, hands=0.15, legs=0.3, feet=0.1), pose='stand', t=t, shiver=0.6, arm=12)
            shield(cc, 540, 770, 1.25, GOLD, k=kin(lt, ts, 0.2))
            heart(cc, 540, 750, 1.5, HEAT2, beat)
        E2.glow(c, dr)
        if lt > ts:
            L.sfx('pop', ('schild',))
        E2.tag(c, 'ORGANE ZUERST', 465, 1090, lt, E2.at(5, 'organe', default=2.2), size=44)
    else:                                       # Hände und Füße bekommen dann weniger warmes Blut.
        E2.stage(c, ICE2, spot=(0.5, 0.42), strength=1.1)
        E2.push(c, lt)
        k = ease(clamp((lt - 0.2) / 1.9))
        tp = dict(core=0.97, head=0.7, arms=lerp(0.7, 0.3, k), hands=lerp(0.65, 0.02, k), legs=lerp(0.65, 0.25, k), feet=lerp(0.55, 0.0, k))
        def dr(cc):
            hp = E2.figure(cc, 540, 1000, 1.45, female=True, temps=tp, pose='stand', t=t, arm=26)
            for (hx, hy) in hp:                 # Wärme zieht sich aus den Händen zur Mitte zurück
                for q in range(3):
                    u = ((lt * 0.8 + q / 3) % 1.0)
                    px, py = lerp(hx, 540, u), lerp(hy, 1000 - 165 * 1.45, u)
                    cc.drawCircle(px, py, 11, P(HEAT, int(255 * (1 - u) * (1 - k * 0.5))))
                E2.ring(cc, hx, hy, 46, ICE, lt, 1.0, every=1.1, n=2, width=5)
            for sg in (-1, 1):
                E2.ring(cc, 540 + sg * 87, 1000 + 336 * 1.45, 56, ICE, lt, 1.2, every=1.1, n=2, width=5)
        E2.glow(c, dr)


def s7(c, t, d):
    i, lt, ld = E2.shots(6, t, d, [E2.at(6, 'formel', default=2.1) - 0.25, 'gerechnet'])
    if i == 0:                                  # Und jetzt die Auflösung: – das Schloss springt auf
        E2.stage(c, '#b98a1f', spot=(0.5, 0.45), strength=1.3)
        E2.push(c, lt)
        to = E2.at(6, 'auflösung', default=0.95)
        ko = ease_out(clamp((lt - to) / 0.25))
        def dr(cc):
            padlock(cc, 540, 900, 1.5, k_open=ko)
            if lt > to:
                E2.ring(cc, 540, 900, 330, GOLD, lt, to, every=0.9, n=2, width=8)
        E2.glow(c, dr)
        if lt > to:
            L.sfx('ding', ('schloss',))
    elif i == 1:                                # Die Formel für Bürotemperaturen stammt aus den Sechzigern.
        E2.stage(c, '#5a4bff', spot=(0.5, 0.33))
        E2.push(c, lt)
        def dr(cc):
            doc = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(230, 340, 620, 450), 26, 26)
            cc.drawRRect(doc, P('#0a1226', 235)); cc.drawRRect(doc, P(INKW, 255, stroke=7))
            E2.text(cc, 'BÜRO-FORMEL', 540, 428, 54, GOLD, k=kin(lt, 0.05, 0.2), shadow=False)
            cc.drawLine(280, 458, 800, 458, P(DIM, 255, stroke=4))
            for q, (ln, wv) in enumerate([(430, 0), (360, 1), (470, 2), (300, 3)]):
                kk = kin(lt, 0.2 + q * 0.18, 0.3)
                cc.drawLine(290, 520 + q * 62, 290 + ln * kk, 520 + q * 62, P(ICE, 255, stroke=9))
            dial(cc, 540, 1260, 180, 0.74, lt)                  # das alte Büro-Thermostat
        E2.glow(c, dr)
        ts = E2.at(6, 'sechzigern', default=4.3) - (t - lt)
        E2.word(c, '1960ER', 540, 640, 200, GOLD, lt, ts, maxw=820, angle=-6)       # Stempel quer über die Formel
        E2.tag(c, 'SO ALT IST DIE REGEL', 465, 1030, lt, ts + 0.25, size=36)
    else:                                       # Gerechnet für einen 40-jährigen Mann mit 70 Kilo.
        E2.stage(c, HEAT2, spot=(0.38, 0.42), strength=0.9)
        E2.push(c, lt)
        def dr(cc):
            E2.figure(cc, 380, 1010, 1.5, female=False, temps=NORM, pose='stand', t=t, arm=12)
            brackets(cc, 130, 330, 630, 1500, GOLD, k=kin(lt, 0.1, 0.3))
        E2.glow(c, dr)
        base = t - lt
        for txt, wd, yy in [('40 JAHRE', '40', 480), ('MANN', 'mann', 600), ('70 KG', '70', 720)]:
            tw = E2.at(6, wd, default=6.0) - base
            E2.pill(c, txt, 820, yy, 50, GOLD, k=kin(lt, tw, 0.16))
            if lt > tw:
                L.sfx('pop', ('norm', txt))


def s8(c, t, d):
    i, lt, ld = E2.shots(7, t, d, ['ihr'])
    if i == 0:                                  # Forscher aus Maastricht haben junge Frauen gemessen:
        E2.stage(c, ICE2, spot=(0.5, 0.42), strength=1.1)
        E2.push(c, lt)
        def dr(cc):
            E2.figure(cc, 540, 1000, 1.45, female=True, temps=dict(core=0.72, head=0.62, arms=0.45, hands=0.3, legs=0.42, feet=0.25), pose='stand', t=t, arm=12)
            brackets(cc, 280, 330, 800, 1500, ICE, k=kin(lt, 0.1, 0.3))
            u = (lt * 0.55) % 1.0
            ys = 340 + u * 1150
            cc.drawLine(250, ys, 830, ys, P(GOLD, 255, stroke=7))
        E2.glow(c, dr)
        E2.tag(c, 'UNI MAASTRICHT', 465, 1070, lt, E2.at(7, 'maastricht', default=0.7), size=40)
        E2.tag(c, 'NATURE CLIMATE CHANGE · 2015', 465, 1140, lt, E2.at(7, 'maastricht', default=0.7) + 0.3, size=30)
    else:                                       # Ihr Stoffwechsel lag 20 bis 32 Prozent unter dem Wert der Formel.
        E2.stage(c, HEAT2, spot=(0.5, 0.5), strength=0.9)
        E2.push(c, lt)
        base = t - lt
        t20 = E2.at(7, '20', default=4.0) - base; t32 = E2.at(7, '32', default=4.75) - base
        v = 1.0 - 0.20 * ease(clamp((lt - t20) / 0.35)) - 0.12 * ease(clamp((lt - t32) / 0.35))
        grow = kin(lt, 0.05, 0.4)
        def dr(cc):
            E2.bar(cc, 300, 1400, 230, 380, INKW, 'FORMEL', k=grow)
            E2.bar(cc, 700, 1400, 230, 380, HEAT, 'GEMESSEN', k=grow * v)
            if lt > t20:
                yt = 1400 - 380 * v
                cc.drawLine(185, 1020, 815, 1020, P(GOLD, 220, stroke=5))
                cc.drawLine(700, 1032, 700, yt - 12, P(GOLD, 255, stroke=8))
        E2.glow(c, dr)
        if t20 <= lt < t32:
            E2.word(c, '−20 %', W / 2, 660, 230, GOLD, lt, t20, key='m20', maxw=900)
        elif lt >= t32:
            E2.word(c, 'BIS −32 %', W / 2, 660, 230, GOLD, lt, t32, key='m32', maxw=900)
            E2.tag(c, 'WENIGER EIGENE WÄRME', W / 2, 770, lt, t32 + 0.3, size=36)
        else:
            E2.glow(c, lambda cc: flame(cc, 540, 620, 1.25 * (0.85 + 0.15 * kin(lt, 0.0, 0.2)), t))


def s9(c, t, d):
    i, lt, ld = E2.shots(8, t, d, [('das', 1)])
    if i == 0:                                  # Also: Sie bildet sich das nicht ein. – „Einbildung" wird durchgestrichen
        E2.stage(c, '#5a4bff', spot=(0.5, 0.45))
        E2.push(c, lt)
        tn = E2.at(8, 'nicht', default=1.55)
        ks = ease_out(clamp((lt - tn) / 0.22))
        def dr(cc):
            cloud(cc, 540, 580, 1.3)
            E2.text(cc, 'EINBILDUNG', 465, 1200, 124, mixc(ICE, '#51607f', ks * 0.7), k=kin(lt, 0.0, 0.15), shadow=False, maxw=780)
            if ks > 0:
                cc.drawLine(70, 1158, 70 + 790 * ks, 1158, P(HEAT2, 255, stroke=22))
                cc.drawLine(300, 380, 300 + 480 * ks, 380 + 400 * ks, P(HEAT2, 255, stroke=20))
        E2.glow(c, dr)
        if lt > tn:
            L.sfx('swipe', ('strich',))
    else:                                       # Das ist Biologie. – Vollbild
        E2.impact(c, lt, 'BIOLOGIE.', sub='KEINE EINBILDUNG', color=GOLD, tint=HEAT2, size=230)
        E2.glow(c, lambda cc: dna(cc, 540, 1230, 420, t, color=HEAT, w=120, turns=1.6), sigma=18, a=0.7,
                bounds=skia.Rect.MakeLTRB(300, 980, 780, 1480))


def s10(c, t, d):
    E2.stage(c, '#5a4bff', spot=(0.5, 0.45))
    E2.push(c, t, rate=0.006)
    tl = max(0.5, L.VOICE[9] - 0.5)
    def dr(cc):
        E2.figure(cc, 250, 1080, 1.05, female=True, temps=COLD, pose='hug', t=t, shiver=1, face='cold')
        E2.flakes(cc, t, n=8, x0=60, x1=460, y0=560, y1=1480)
    E2.glow(c, dr)
    L.finn(c, 830, 730, 0.8, t, mood='laugh', arm_l=200 + math.sin(t * 8) * 20, arm_r=-70, look=(-1, 1))
    E2.logo(c, t, tl)


SCENES = [s1, s2, s3, s4, s5, s6, s7, s8, s9, s10]
FADE_COL = ['#000000'] * 10
