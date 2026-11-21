"""EDITING V2 – „Dunkel & Leuchtend" (21.11.2026).

Abgeschaut bei den deutschsprachigen Faceless-Erklärkanälen, die gerade am besten laufen:
  - dunkle Bühne, das Motiv leuchtet und füllt das Bild
  - jeder Satz bekommt ein eigenes Bild (harter Schnitt), dazwischen bauen sich Details auf
  - Untertitel: 1–2 Wörter, groß, GROSSBUCHSTABEN, in der Bildmitte
  - Schlüsselzahlen als eigene Vollbild-Karte
Die Kamera bleibt ruhig: kein Wackeln, kein Zoom-Pulsieren. Bewegung kommt aus Schnitt und Motiv.

Einschalten in episode.py:   EDIT = 2
Zusätzlich möglich:          TOPIC = 'WARUM FRIEREN FRAUEN SCHNELLER?'   (kleine Themenzeile oben)
                             HOOK_TEXT = 'SIE FRIERT,\nER SCHWITZT.'      (große Zeilen im ersten Bild)
                             HOOK_COLORS = [E2.ICE, E2.HEAT]              (Farbe je Zeile)
                             HOOK_END = 2.2    (Sekunden; so lange steht der Hook, erst danach kommen Untertitel)
"""
import math
import numpy as np
import render as L
from render import skia, W, H, P, clamp, ease, ease_out, lerp, mixc, col

ICE, ICE2 = '#8fdcff', '#2f7bff'       # kalt
HEAT, HEAT2 = '#ffa23a', '#ff4a2e'     # warm
GOLD = '#ffd03f'                       # Akzent (wie FINNs Hoodie)
INKW = '#eef6ff'                       # helle Schrift
DIM = '#7f93b8'                        # gedämpfte Linien
BG_TOP, BG_BOT = '#0b1430', '#04060d'

SUB_Y = 915                            # Grundlinie der Untertitel (Band y 820–945, volle Breite frei)


# ---------------------------------------------------------------- Bühne
_ST = {}
_DUST = np.random.RandomState(11).uniform(0, 1, (40, 5))


def stage(c, tint=ICE2, spot=(0.5, 0.42), grid=True, strength=1.0):
    """Dunkle Bühne mit weichem Lichtkegel in der Themenfarbe, feinem Raster und schwebendem Staub."""
    L.BP_ON = True                                         # helle Beschriftungen (wie auf der Blaupause)
    key = (tint, spot, grid, strength)
    im = _ST.get(key)
    if im is None:
        if len(_ST) > 40:
            _ST.clear()
        w, h = 540, 960
        s = skia.Surface(w, h); cc = s.getCanvas()
        p = skia.Paint(AntiAlias=True)
        p.setShader(skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(0, h)], [col(BG_TOP), col(BG_BOT)]))
        cc.drawRect(skia.Rect.MakeWH(w, h), p)
        q = skia.Paint(AntiAlias=True)
        q.setShader(skia.GradientShader.MakeRadial(skia.Point(w * spot[0], h * spot[1]), h * 0.6,
                                                   [col(tint, int(95 * strength)), col(tint, int(30 * strength)), col(tint, 0)], [0.0, 0.5, 1.0]))
        cc.drawRect(skia.Rect.MakeWH(w, h), q)
        if grid:
            for i, x in enumerate(range(0, w + 1, 30)):
                cc.drawLine(x, 0, x, h, P('#9fc8ff', 20 if i % 3 == 0 else 8, stroke=1))
            for i, y in enumerate(range(0, h + 1, 30)):
                cc.drawLine(0, y, w, y, P('#9fc8ff', 20 if i % 3 == 0 else 8, stroke=1))
        v = skia.Paint(AntiAlias=True)
        v.setShader(skia.GradientShader.MakeRadial(skia.Point(w / 2, h * 0.46), h * 0.78,
                                                   [col('#000000', 0), col('#000000', 0), col('#000000', 170)], [0.0, 0.55, 1.0]))
        cc.drawRect(skia.Rect.MakeWH(w, h), v)
        im = s.makeImageSnapshot(); _ST[key] = im
    c.drawRect(skia.Rect.MakeXYWH(-2000, -2000, W + 4000, H + 4000), P(BG_BOT))
    c.drawImageRect(im, skia.Rect.MakeXYWH(-W * 0.06, -H * 0.06, W * 1.12, H * 1.12), L._SAMP)
    dust(c)


def dust(c, a=150):
    T = L.NOW
    for x0, y0, r, sp, ph in _DUST:
        y = (y0 * H - T * (8 + sp * 18)) % H
        x = x0 * W + math.sin(T * 0.5 + ph * 6.28) * 18
        tw = 0.5 + 0.5 * math.sin(T * 1.3 + ph * 6.28)
        c.drawCircle(x, y, 1.5 + r * 3.0, P('#cfe6ff', int(a * tw * 0.55)))


def push(c, lt, rate=0.011, cx=W / 2, cy=H * 0.44):
    """Ruhiger, gleichmäßiger Push-in innerhalb einer Einstellung (ca. 1 % pro Sekunde)."""
    z = 1.0 + rate * max(0.0, lt)
    c.translate(cx, cy); c.scale(z, z); c.translate(-cx, -cy)


_GLOW = {}
_LIN = skia.SamplingOptions(skia.FilterMode.kLinear)


def glow(c, draw, sigma=22, a=0.9, bounds=None):
    """Zeichnet draw(c) einmal als weichen Schein und einmal scharf darüber.
    Der Schein wird in Viertel-Auflösung gerechnet – sonst dauert jedes 4K-Bild über eine Sekunde."""
    if L.SFX_REC is not None:                               # Ton-Durchlauf: nur Ereignisse einsammeln
        draw(c); return
    K = c.getBaseLayerSize().width() / W
    q = 0.25
    surf = _GLOW.get('s')
    if surf is None:
        surf = skia.Surface(int(W * q), int(H * q)); _GLOW['s'] = surf
    gc = surf.getCanvas(); gc.clear(skia.ColorTRANSPARENT)
    m = skia.Matrix(); m.setScale(q / K, q / K); m.preConcat(c.getTotalMatrix())
    bp = skia.Paint(); bp.setImageFilter(skia.ImageFilters.Blur(sigma * q, sigma * q))
    gc.save(); gc.resetMatrix(); gc.saveLayer(None, bp); gc.setMatrix(m)
    chk = L.SAFE_CHECK; L.SAFE_CHECK = False                # Schein-Durchgang zählt nicht für Sperrzonen-/Überlappungs-Check
    try:
        draw(gc)
    finally:
        L.SAFE_CHECK = chk
    gc.restore(); gc.restore()
    lp = skia.Paint(); lp.setAlphaf(a)                      # normales Überblenden: additiv (kPlus) kostet in 4K das Achtfache
    c.save(); c.resetMatrix()
    c.drawImageRect(surf.makeImageSnapshot(), skia.Rect.MakeWH(W * K, H * K), _LIN, lp)
    c.restore()
    draw(c)


# ---------------------------------------------------------------- Einstellungen (Schnitte)
def shots(scene, t, d, marks, lead=0.10):
    """Teilt eine Szene in Einstellungen. marks: Wortanfang ('aber'), (Wortanfang, nth) oder feste Zeit (Sek.).
    An jedem Punkt wird hart geschnitten. Rückgabe: (Nummer, Zeit seit dem Schnitt, Länge der Einstellung)."""
    cuts = [0.0]
    for m in marks:
        if isinstance(m, (int, float)):
            tt = float(m)
        else:
            w_, nth = (m, 0) if isinstance(m, str) else m
            tt = L.word_t(scene, w_, nth=nth, default=None)
            if tt is None:
                continue
            tt = max(0.0, tt - lead)
        if cuts[-1] + 0.5 < tt < d - 0.4:
            cuts.append(tt)
    i = max(k for k in range(len(cuts)) if cuts[k] <= t + 1e-6)
    end = cuts[i + 1] if i + 1 < len(cuts) else d
    if i > 0:
        L.sfx('cut', ('cut', i), cuts[i])
    return i, t - cuts[i], end - cuts[i]


def at(scene, word, nth=0, default=0.0, lead=0.0):
    """Szenen-Zeit eines gesprochenen Wortes (für Einblendungen genau auf dem Wort)."""
    v = L.word_t(scene, word, nth=nth, default=None)
    return default if v is None else max(0.0, v - lead)


def kin(lt, t0=0.0, d=0.16):
    """0→1 beim Einblenden (schnell, ohne Nachwippen)."""
    return ease_out(clamp((lt - t0) / d))


# ---------------------------------------------------------------- Farben / Wärmebild
_TH = ['#2a5bff', '#35b8ff', '#7df0e0', '#ffe66b', '#ff9d2e', '#ff4326']


def heat(v):
    """Wärmebild-Farbe: 0 = kalt (blau) … 1 = heiß (rot)."""
    v = clamp(v) * (len(_TH) - 1); i = min(int(v), len(_TH) - 2)
    return mixc(_TH[i], _TH[i + 1], v - i)


def _gp(c1, c2, x0, y0, x1, y1, a=255, stroke=None):
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeLinear([skia.Point(x0, y0), skia.Point(x1, y1)], [col(c1, a), col(c2, a)]))
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(stroke)
        p.setStrokeCap(skia.Paint.kRound_Cap); p.setStrokeJoin(skia.Paint.kRound_Join)
    return p


def _limb(c, ax, ay, bx, by, w, ca, cb, a=255, rings=5):
    """Gliedmaße als Drahtgitter-Kapsel mit Farbverlauf von ca (Ansatz) nach cb (Ende)."""
    ln = math.hypot(bx - ax, by - ay); ang = math.degrees(math.atan2(by - ay, bx - ax))
    c.save(); c.translate(ax, ay); c.rotate(ang)
    r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-w / 2, -w / 2, ln + w, w), w / 2, w / 2)
    c.drawRRect(r, _gp(ca, cb, 0, 0, ln, 0, int(a * 0.30)))
    c.drawRRect(r, _gp(ca, cb, 0, 0, ln, 0, a, stroke=5))
    for i in range(1, rings + 1):
        x = ln * i / (rings + 1)
        c.drawOval(skia.Rect.MakeXYWH(x - w * 0.15, -w / 2, w * 0.30, w), P(mixc(ca, cb, i / (rings + 1)), int(a * 0.55), stroke=2))
    c.restore()


def figure(c, x, y, s=1.0, female=False, temps=None, pose='stand', t=0.0, shiver=0.0, a=255, face=None, arm=10):
    """Mensch als leuchtende Drahtgitter-Figur im Wärmebild. (x, y) = Hüftmitte, Höhe bei s=1 ca. 770 px
    (Kopf oben −440, Füße +330). temps: dict mit core/head/arms/hands/legs/feet (0 kalt … 1 heiß).
    pose: 'stand' | 'hug' (Arme verschränkt, friert) | 'fan' (ein Arm oben, schwitzt)."""
    tp = dict(core=0.8, head=0.75, arms=0.6, hands=0.5, legs=0.55, feet=0.45)
    tp.update(temps or {})
    C = {k: heat(v) for k, v in tp.items()}
    sx = math.sin(t * 38) * 3.2 * shiver                    # Zittern nur an der Figur, nicht an der Kamera
    c.save(); c.translate(x + sx, y); c.scale(s, s)
    sw = 84 if female else 100                               # Schulter-Halbbreite
    wa = 54 if female else 70                                # Taille
    hp = 92 if female else 80                                # Hüfte
    lw = 54 if female else 60                                # Beinbreite
    aw = 38 if female else 46                                # Armbreite
    # Beine + Füße
    for sg in (-1, 1):
        _limb(c, sg * 44, 0, sg * 52, 300, lw, C['core'], C['legs'], a, rings=6)
        fr = skia.Rect.MakeXYWH(sg * 60 - 48, 316, 96, 40)
        c.drawOval(fr, P(C['feet'], int(a * 0.32))); c.drawOval(fr, P(C['feet'], a, stroke=5))
    # Arme hinter dem Rumpf (stand/fan)
    hands = []
    if pose == 'stand':
        for sg in (-1, 1):
            ang = math.radians(90 + sg * -arm)
            ex, ey = sg * sw + math.cos(ang) * 250 * 1.0, -262 + math.sin(ang) * 250
            _limb(c, sg * sw, -262, ex, ey, aw, C['arms'], C['hands'], a)
            hands.append((ex, ey))
    elif pose == 'fan':
        ex, ey = -sw - 44, -12
        _limb(c, -sw, -262, ex, ey, aw, C['arms'], C['hands'], a); hands.append((ex, ey))
        ex, ey = sw + 96, -372 + math.sin(t * 9) * 16
        _limb(c, sw, -262, sw + 70, -250, aw, C['arms'], C['arms'], a, rings=1)
        _limb(c, sw + 70, -250, ex, ey, aw, C['arms'], C['hands'], a, rings=3); hands.append((ex, ey))
    # Rumpf
    tr = skia.Path(); tr.moveTo(-sw, -285)
    tr.cubicTo(-sw - 16, -200, -wa - 4, -170, -wa, -110); tr.cubicTo(-wa + 2, -60, -hp, -40, -hp, 10)
    tr.cubicTo(-hp * 0.6, 40, hp * 0.6, 40, hp, 10); tr.cubicTo(hp, -40, wa - 2, -60, wa, -110)
    tr.cubicTo(wa + 4, -170, sw + 16, -200, sw, -285); tr.cubicTo(sw * 0.5, -300, -sw * 0.5, -300, -sw, -285)
    rp = skia.Paint(AntiAlias=True)
    rp.setShader(skia.GradientShader.MakeRadial(skia.Point(0, -165), 210, [col(C['core'], int(a * 0.62)), col(C['core'], int(a * 0.34)), col(C['arms'], int(a * 0.22))], [0.0, 0.55, 1.0]))
    c.drawPath(tr, rp); c.drawPath(tr, P(C['core'], a, stroke=5))
    for yy, hw in [(-250, sw * 0.96), (-205, (sw + wa) / 2 + 6), (-160, wa + 8), (-110, wa), (-60, (wa + hp) / 2), (-15, hp * 0.98)]:
        c.drawArc(skia.Rect.MakeXYWH(-hw, yy - hw * 0.2, hw * 2, hw * 0.4), 0, 180, False, P(C['core'], int(a * 0.5), stroke=2))
    c.drawLine(0, -290, 0, 20, P(C['core'], int(a * 0.4), stroke=2))
    # Hals + Kopf
    c.drawRect(skia.Rect.MakeXYWH(-18, -318, 36, 36), P(C['head'], int(a * 0.3)))
    c.drawCircle(0, -372, 64, P(C['head'], int(a * 0.34))); c.drawCircle(0, -372, 64, P(C['head'], a, stroke=5))
    for ry in (20, 44):
        c.drawOval(skia.Rect.MakeXYWH(-64, -372 - ry * 0.45, 128, ry * 0.9), P(C['head'], int(a * 0.45), stroke=2))
    c.drawOval(skia.Rect.MakeXYWH(-26, -436, 52, 128), P(C['head'], int(a * 0.45), stroke=2))
    if female:                                                # Haare als zwei Bögen
        c.drawArc(skia.Rect.MakeXYWH(-84, -452, 168, 190), 180, 180, False, P(C['head'], a, stroke=5))
        c.drawLine(-84, -357, -78, -290, P(C['head'], a, stroke=5)); c.drawLine(84, -357, 78, -290, P(C['head'], a, stroke=5))
    if face:
        c.drawCircle(-22, -380, 7, P(INKW, a)); c.drawCircle(22, -380, 7, P(INKW, a))
        if face == 'cold':
            c.drawArc(skia.Rect.MakeXYWH(-22, -350, 44, 26), 200, 140, False, P(INKW, a, stroke=5))
        elif face == 'hot':                                  # erschöpft: offener Mund
            c.drawOval(skia.Rect.MakeXYWH(-13, -356, 26, 22), P(INKW, a, stroke=5))
            c.drawLine(-34, -398, -12, -392, P(INKW, a, stroke=5)); c.drawLine(34, -398, 12, -392, P(INKW, a, stroke=5))
        else:
            c.drawArc(skia.Rect.MakeXYWH(-22, -366, 44, 30), 20, 140, False, P(INKW, a, stroke=5))
    # verschränkte Arme vor dem Rumpf
    if pose == 'hug':
        _limb(c, -sw, -262, -sw - 22, -150, aw, C['arms'], C['arms'], a, rings=2)
        _limb(c, -sw - 22, -150, 46, -168, aw, C['arms'], C['hands'], a, rings=3); hands.append((46, -168))
        _limb(c, sw, -262, sw + 22, -140, aw, C['arms'], C['arms'], a, rings=2)
        _limb(c, sw + 22, -140, -46, -128, aw, C['arms'], C['hands'], a, rings=3); hands.append((-46, -128))
    for hx, hy in hands:
        c.drawCircle(hx, hy, 30, P(C['hands'], int(a * 0.4))); c.drawCircle(hx, hy, 30, P(C['hands'], a, stroke=5))
    c.restore()
    return [(x + sx + hx * s, y + hy * s) for hx, hy in hands]


def hand(c, x, y, s, tip=0.3, wrist=0.7, a=255):
    """Große Hand (Wärmebild): Handgelenk → Fingerspitzen mit Farbverlauf. (x, y) = Mitte der Handfläche."""
    cw, ct = heat(wrist), heat(tip)
    c.save(); c.translate(x, y); c.scale(s, s)
    for fx, fl, fw in [(-78, 150, 40), (-27, 190, 42), (25, 180, 42), (76, 140, 38)]:
        _limb(c, fx, -70, fx, -70 - fl, fw, mixc(cw, ct, 0.45), ct, a, rings=3)
    _limb(c, 100, 30, 176, -50, 44, mixc(cw, ct, 0.4), ct, a, rings=2)                    # Daumen
    palm = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-105, -90, 210, 220), 62, 62)
    c.drawRRect(palm, _gp(mixc(cw, ct, 0.45), cw, 0, -90, 0, 130, int(a * 0.36)))
    c.drawRRect(palm, _gp(mixc(cw, ct, 0.45), cw, 0, -90, 0, 130, a, stroke=5))
    for yy in (-40, 10, 60):
        c.drawArc(skia.Rect.MakeXYWH(-105, yy - 22, 210, 44), 0, 180, False, P(mixc(cw, ct, 0.3), int(a * 0.5), stroke=2))
    _limb(c, 0, 150, 0, 260, 120, cw, cw, a, rings=2)                                     # Handgelenk
    c.restore()


def waves(c, x, y, w, h, t, color=HEAT, n=5, a=255):
    """Aufsteigende Wärme-Schlangenlinien (oder mit negativem h fallend)."""
    for i in range(n):
        xx = x - w / 2 + w * (i + 0.5) / n
        ph = (t * 0.55 + i * 0.37) % 1.0
        p = skia.Path()
        for k in range(13):
            yy = y - h * (ph * 0.35 + k / 12 * 0.65)
            xo = math.sin(k * 1.1 + t * 3 + i) * 14
            (p.moveTo if k == 0 else p.lineTo)(xx + xo, yy)
        c.drawPath(p, P(color, int(a * (0.35 + 0.65 * math.sin(ph * math.pi))), stroke=7))


def flakes(c, t, n=16, x0=80, x1=1000, y0=220, y1=1500, color=ICE, a=220):
    """Fallende Eiskristalle."""
    rng = np.random.RandomState(5)
    for i in range(n):
        bx, sp, sz, ph = rng.uniform(x0, x1), rng.uniform(60, 140), rng.uniform(12, 26), rng.uniform(0, 6.28)
        yy = y0 + ((t * sp + rng.uniform(0, 1500)) % (y1 - y0)); xx = bx + math.sin(t * 1.2 + ph) * 20
        for k in range(3):
            an = math.radians(k * 60 + t * 20)
            c.drawLine(xx - math.cos(an) * sz, yy - math.sin(an) * sz, xx + math.cos(an) * sz, yy + math.sin(an) * sz, P(color, a, stroke=4))


def drops(c, x, y, s, t, color=ICE, n=3):
    """Schweißtropfen, die neben dem Kopf herunterlaufen."""
    for k in range(n):
        dx = (-1 if k % 2 else 1) * (92 + 26 * (k // 2)) * s
        ph = (t * 0.9 + k * 0.4) % 1.0
        yy = y + (-40 + ph * 150) * s; r = 15 * s
        p = skia.Path(); p.moveTo(x + dx, yy - r * 1.9); p.cubicTo(x + dx + r * 1.2, yy - r * 0.2, x + dx + r, yy + r, x + dx, yy + r)
        p.cubicTo(x + dx - r, yy + r, x + dx - r * 1.2, yy - r * 0.2, x + dx, yy - r * 1.9)
        al = int(255 * math.sin(ph * math.pi))
        c.drawPath(p, P(color, int(al * 0.45))); c.drawPath(p, P(color, al, stroke=4))


# ---------------------------------------------------------------- Schrift
def fit(text, size, maxw, font=None):
    f = skia.Font(font or L.FONT_B, size)
    while f.measureText(text) > maxw and size > 20:
        size -= 2; f = skia.Font(font or L.FONT_B, size)
    return f, size


def text(c, s, x, y, size, color=INKW, a=255, maxw=930, k=1.0, shadow=True, font=None):
    """Fette Zeile, mittig bei x, Grundlinie y. k = Einblenden (0..1): leichtes Aufploppen."""
    if k <= 0:
        return 0
    f, size = fit(s, size, maxw, font)
    w = f.measureText(s)
    sc = 1.0 + 0.16 * (1 - k)
    c.save(); c.translate(x, y - size * 0.34); c.scale(sc, sc); c.translate(-x, -(y - size * 0.34))
    al = int(a * clamp(k * 1.6))
    if shadow:
        c.drawString(s, x - w / 2, y + min(size * 0.05, 6), f, P('#000000', int(al * 0.7), blur=size * 0.12))
        c.drawString(s, x - w / 2, y, f, P('#04060d', al, stroke=min(size * 0.14, 18)))
    c.drawString(s, x - w / 2, y, f, P(color, al))
    c.restore()
    return w


def word(c, s, x, y, size, color, lt, t0, key=None, hold=None, maxw=900, snd='thud', angle=0.0):
    """SCHLAGWORT: knallt groß und leuchtend ins Bild, genau auf dem gesprochenen Wort. angle = Schräglage (Stempel)."""
    u = lt - t0
    if u < 0 or (hold is not None and u > hold):
        return
    L.sfx(snd, ('word', key or s, round(t0, 2)))            # Zeitpunkt = jetzt (t0 ist Zeit innerhalb der Einstellung)
    k = kin(u, 0, 0.13)
    def d(cc):
        cc.save(); cc.translate(x, y - size * 0.34); cc.rotate(angle); cc.translate(-x, -(y - size * 0.34))
        text(cc, s, x, y, size, color, k=k, maxw=maxw)
        cc.restore()
    glow(c, d, sigma=18, a=0.8)


def tag(c, s, x, y, lt, t0=0.0, size=38):
    """Kleines Etikett (Quelle, Beschriftung) – gesperrte Großbuchstaben im hellen Rahmen."""
    if lt >= t0:
        L.sfx('type', ('tag', s))
    rec = L.SFX_REC; L.SFX_REC = None                       # akten_label würde die Zeit der Einstellung als Szenen-Zeit melden
    try:
        L.akten_label(c, s, x, y, lt, t0, size=size, dark=True)
    finally:
        L.SFX_REC = rec


def pill(c, s, x, y, size=44, color=GOLD, k=1.0, txt='#0b1020'):
    """Farbige Pille mit dunkler Schrift (für Werte wie „40 JAHRE")."""
    if k <= 0:
        return
    f = skia.Font(L.FONT_B, size); w = f.measureText(s) + size * 1.0; h = size * 1.5
    c.save(); c.translate(x, y); c.scale(0.8 + 0.2 * k, 0.8 + 0.2 * k)
    r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), h / 2, h / 2)
    c.drawRRect(r, P(color, int(70 * k), blur=18)); c.drawRRect(r, P(color, int(255 * clamp(k * 1.5))))
    c.drawString(s, -f.measureText(s) / 2, size * 0.36, f, P(txt, int(255 * clamp(k * 1.5))))
    c.restore()


def impact(c, lt, big, sub='', color=ICE, top='', tint=None, key=None, size=300):
    """VOLLBILD-KARTE für die Schlüsselzahl: dunkel, eine riesige leuchtende Zahl, darunter eine Zeile."""
    stage(c, tint or color, spot=(0.5, 0.36), grid=False, strength=1.25)
    L.sfx('thud', ('impact', key or big))
    k = kin(lt, 0, 0.14)
    f, sz = fit(big, size, 920)
    yb = 640
    glow(c, lambda cc: text(cc, big, W / 2, yb, sz, color, k=k, maxw=920), sigma=26, a=0.95,
         bounds=skia.Rect.MakeLTRB(-200, yb - sz * 1.5, W + 200, yb + sz * 0.8))
    w = f.measureText(big)
    u = ease_out(clamp((lt - 0.12) / 0.3))
    if u > 0:                                               # Strich unter der Zahl zieht sich auf
        c.drawLine(W / 2 - w / 2 * u, yb + sz * 0.16, W / 2 + w / 2 * u, yb + sz * 0.16, P(color, 255, stroke=8))
    if top:
        text(c, top, W / 2, yb - sz * 0.86, 50, INKW, k=kin(lt, 0.05, 0.2), maxw=880)
    if sub:
        text(c, sub, W / 2, yb + sz * 0.16 + 76, 54, INKW, k=kin(lt, 0.25, 0.2), maxw=900)


def ring(c, x, y, r, color, lt, t0=0.0, every=1.3, n=2, width=5):
    """Sich ausbreitende Ringe (Signal/„hier schauen")."""
    for i in range(n):
        ph = ((lt - t0) / every + i / n) % 1.0
        if lt < t0:
            continue
        c.drawCircle(x, y, r * (1 + ph * 0.9), P(color, int(230 * (1 - ph)), stroke=width))


def bar(c, x, y_base, w, h, color, label, value='', k=1.0, lab_size=40):
    """Leuchtende Säule (Unterkante y_base). k = Anteil der Höhe (0..1)."""
    hh = h * clamp(k)
    r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - w / 2, y_base - hh, w, hh), 16, 16)
    c.drawRRect(r, _gp(color, mixc(color, '#04060d', 0.55), 0, y_base - hh, 0, y_base, 235))
    c.drawRRect(r, P(color, 255, stroke=5))
    if label:
        text(c, label, x, y_base + lab_size * 1.35, lab_size, INKW, maxw=w + 120, shadow=False)
    if value:
        text(c, value, x, y_base - hh - 26, 64, color, maxw=w + 160)


def logo(c, t, t0, y=330):
    """Endkarte im dunklen Look."""
    k = kin(t, t0, 0.35)
    if k <= 0:
        return
    def d(cc):
        text(cc, 'FAKTENFABRIK', W / 2, y, 104, INKW, k=k, maxw=900)
    glow(c, d, sigma=16, a=0.6, bounds=skia.Rect.MakeLTRB(0, y - 180, W, y + 80))
    u = ease_out(clamp((t - t0 - 0.15) / 0.4))
    c.drawLine(W / 2 - 300 * u, y + 30, W / 2 + 300 * u, y + 30, P(GOLD, 255, stroke=8))
    text(c, '@faktenfabrik.tv', W / 2, y + 96, 46, GOLD, k=kin(t, t0 + 0.15, 0.3), maxw=800)
    text(c, 'Wissen. Staunen. Verstehen.', W / 2, y + 150, 32, INKW, a=210, k=kin(t, t0 + 0.25, 0.3), maxw=800)


# ---------------------------------------------------------------- Hook, Themenzeile, Fortschritt (von pipeline.py aufgerufen)
def hook(c, t, lines, colors=None, end=2.2):
    """Großer Text-Hook ab Bild 1 (Cover): je Zeile eine Farbe, steht bis zum ersten Schnitt."""
    if t > end or not lines:
        return
    colors = colors or [INKW, GOLD]
    sz = 132
    for ln in lines:
        _, s2 = fit(ln, sz, 930); sz = min(sz, s2)
    y = 372
    for i, ln in enumerate(lines):
        cl = colors[min(i, len(colors) - 1)]
        glow(c, lambda cc, ln=ln, cl=cl, yy=y: text(cc, ln, W / 2, yy, sz, cl, maxw=930), sigma=16, a=0.7,
             bounds=skia.Rect.MakeLTRB(0, y - sz * 1.4, W, y + sz * 0.7))
        y += sz * 1.12


def topic(c, s, a=1.0):
    """Kleine Themenzeile oben (bleibt stehen, damit jeder sofort weiß, worum es geht)."""
    if not s or a <= 0:
        return
    size = 34; f = skia.Font(L.FONT_B, size); sp = size * 0.06
    tw = sum(f.measureText(ch) for ch in s) + sp * (len(s) - 1)
    while tw > 880 and size > 22:
        size -= 2; f = skia.Font(L.FONT_B, size); sp = size * 0.06
        tw = sum(f.measureText(ch) for ch in s) + sp * (len(s) - 1)
    wb, hb = tw + size * 1.3, size * 1.7
    y = 262
    r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(W / 2 - wb / 2, y - hb / 2, wb, hb), hb / 2, hb / 2)
    c.drawRRect(r, P('#060a16', int(200 * a))); c.drawRRect(r, P(INKW, int(120 * a), stroke=2.5))
    xx = W / 2 - tw / 2
    for ch in s:
        c.drawString(ch, xx, y + size * 0.36, f, P(INKW, int(235 * a))); xx += f.measureText(ch) + sp


def progress(c, g):
    c.drawRect(skia.Rect.MakeXYWH(0, 0, W, 10), P('#ffffff', 34))
    if g > 0:
        x = W * min(1.0, g)
        c.drawRect(skia.Rect.MakeXYWH(0, 0, x, 10), P(GOLD))
        c.drawCircle(x, 5, 14, P(GOLD, 150, blur=8))


# ---------------------------------------------------------------- Untertitel: 1–2 Wörter, groß, mittig
_CH = None


def _chunks(WS):
    """Zerlegt den Text in Häppchen: höchstens 2 Wörter und 13 Zeichen, Satzzeichen beendet das Häppchen."""
    global _CH
    if _CH is not None and _CH[0] is WS.WORDS:
        return _CH[1]
    out, cur = [], []
    for k, w_ in enumerate(WS.WORDS):
        s = w_['text']
        if cur:
            joined = ' '.join(WS.WORDS[j]['text'] for j in cur + [k])
            gap = w_['start'] - WS.WORDS[cur[-1]]['end']
            if (len(cur) == 1 and len(joined) > 14) or (len(cur) == 2 and len(joined) > 11) or len(cur) >= 3 or gap > 0.35:
                out.append(cur); cur = []
        cur.append(k)
        if s[-1] in '.,:;?!':
            out.append(cur); cur = []
    if cur:
        out.append(cur)
    # kein kurzes Wort (der, die, im …) allein stehen lassen: an das nächste oder vorige Häppchen hängen
    txt = lambda g: ' '.join(WS.WORDS[j]['text'] for j in g)
    k = 0
    while k < len(out):
        g = out[k]; s = txt(g)
        if len(g) == 1 and len(s) <= 3 and s[-1] not in '.,:;?!':
            if k + 1 < len(out) and len(s + ' ' + txt(out[k + 1])) <= 19 and WS.WORDS[out[k + 1][0]]['start'] - WS.WORDS[g[-1]]['end'] < 0.35:
                out[k + 1] = g + out[k + 1]; del out[k]; continue
            if k > 0 and txt(out[k - 1])[-1] not in '.,:;?!' and len(txt(out[k - 1]) + ' ' + s) <= 16:
                out[k - 1] = out[k - 1] + g; del out[k]; continue
        k += 1
    _CH = (WS.WORDS, out)
    return out


def subs(c, T, WS, t_from=0.0, accent=GOLD):
    """Untertitel V2. Das gerade gesprochene Wort leuchtet in der Akzentfarbe; Schlüsselwörter bleiben farbig."""
    if T < t_from:
        return
    ch = _chunks(WS)
    idx = None
    for n, g in enumerate(ch):
        if T >= WS.WORDS[g[0]]['start'] - 0.06:
            idx = n
    if idx is None:
        return
    g = ch[idx]
    if WS.WORDS[g[0]]['start'] - 0.06 < t_from:               # Häppchen gehört noch zum Hook
        return
    nxt = WS.WORDS[ch[idx + 1][0]]['start'] - 0.06 if idx + 1 < len(ch) else 1e9
    if T > min(nxt, WS.WORDS[g[-1]]['end'] + 0.7):
        return
    words = [WS.WORDS[k]['text'].upper() for k in g]
    size = 128; f = skia.Font(L.FONT_B, size); sp = f.measureText(' ') * 0.9
    wid = lambda: sum(f.measureText(s) for s in words) + sp * (len(words) - 1)
    while wid() > 920 and size > 40:
        size -= 2; f = skia.Font(L.FONT_B, size); sp = f.measureText(' ') * 0.9
    tw = wid()
    u = clamp((T - WS.WORDS[g[0]]['start'] + 0.06) / 0.10)
    sc = 1.0 + 0.10 * (1 - ease_out(u))
    y = SUB_Y; cy = y - size * 0.36
    c.save(); c.translate(W / 2, cy); c.scale(sc, sc); c.translate(-W / 2, -cy)
    # weicher dunkler Hof hinter dem Wort, damit es über jedem Motiv lesbar ist
    c.drawRoundRect(skia.Rect.MakeXYWH(W / 2 - tw / 2 - 40, y - size * 0.86, tw + 80, size * 1.14), 40, 40, P('#04060d', 150, blur=34))
    x = W / 2 - tw / 2
    for k, s in zip(g, words):
        w_ = WS.WORDS[k]; ww = f.measureText(s)
        said = T >= w_['start'] - 0.05
        key = WS.strip(w_['text']).lower() in WS.HL
        c.drawString(s, x, y + size * 0.05, f, P('#000000', 200, blur=size * 0.10))
        c.drawString(s, x, y, f, P('#04060d', 255, stroke=min(size * 0.15, 18)))
        if key and said:
            c.drawString(s, x, y, f, P(accent, 150, blur=size * 0.16))
        c.drawString(s, x, y, f, P(accent if (key and said) else ('#ffffff' if said else '#8d99b3'), 255))
        x += ww + sp
    c.restore()
