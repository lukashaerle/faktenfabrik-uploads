"""LOOK 3 „KINO“ – dunkle Bühne, ein warmer Lichtkegel, ein Hauptobjekt, ruhige Serifenschrift, langsame Kamerafahrt."""
from core import *
from math import sin, cos, pi, radians

CREAM, INK, RED, REDL, GOLD, MUTE = '#F4EBDA', '#1C1915', '#D8402F', '#FF6A52', '#C9A86A', '#A89C88'
T_NOCH, T_WEG, T_GELTEN, T_REGEL = wt('noch'), wt('weg'), wt('gelten'), wt('Regel')
T_DREI, T_JAHRE, T_FRIST, T_STARTET, T_ENDE, T_KAUF = wt('drei'), wt('Jahre'), wt('Frist'), wt('startet'), wt('Ende'), wt('Kaufjahres')
T_BAR0, T_BAR1 = T_KAUF + 0.08, T_KAUF + 0.88
T_END = T_BAR1
XS = [150, 345, 540, 735, 930]; LY = 1128
XBUY = XS[0] + (XS[1] - XS[0]) * (2.5 / 12)
CAP = dict(font='semi', size=54, y=1392, fg='#F8F2E6', dim=0.36, shadow=True)
SFX = [(T_NOCH + 0.02, 'hit', 0.55), (T_WEG - 0.04, 'tick', 0.6), (1.97, 'whoosh', 0.35)] + \
      [(T_GELTEN + 0.05 + i * 0.11, 'tick', 0.5) for i in range(4)] + \
      [(T_REGEL + 0.04, 'pop', 0.5), (T_DREI, 'thud', 0.9), (T_FRIST, 'tick', 0.6), (T_ENDE - 0.06, 'thud', 0.5),
       (T_BAR0 + 0.27, 'tick', 0.9), (T_BAR0 + 0.53, 'tick', 0.9), (T_END, 'thud', 0.8), (T_END + 0.02, 'ding', 0.35)]
SAMP = skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear)
RNG = np.random.default_rng(7)


def Rx(a): c_, s_ = cos(a), sin(a); return np.array([[1, 0, 0], [0, c_, -s_], [0, s_, c_]])
def Ry(a): c_, s_ = cos(a), sin(a); return np.array([[c_, 0, s_], [0, 1, 0], [-s_, 0, c_]])
def Rz(a): c_, s_ = cos(a), sin(a); return np.array([[c_, -s_, 0], [s_, c_, 0], [0, 0, 1]])


def noise_img(w, h, k, seed):
    n = np.random.default_rng(seed).normal(0, 1, (h, w))
    arr = np.zeros((h, w, 4), np.uint8)
    arr[..., :3] = np.where(n > 0, 255, 0)[..., None]
    arr[..., 3] = np.clip(np.abs(n) * k * 255, 0, 255).astype(np.uint8)
    return skia.Image.fromarray(arr, colorType=skia.kRGBA_8888_ColorType, alphaType=skia.kUnpremul_AlphaType)


GRAIN = noise_img(W, H, 0.024, 11)          # feines, stehendes Korn (gegen Farbstufen im Dunkeln; flimmert nicht)


# ---------------------------------------------------------------- Bühne
_BG = None


def background(c):
    global _BG
    if _BG is None:
        s = skia.Surface(W, H); b = s.getCanvas(); full = skia.Rect.MakeWH(W, H)
        b.clear(C('#080706'))
        b.drawRect(full, rad(540, 330, 1150, [C('#4A3824', 0.80), C('#22190F', 0.55), C('#080706', 0.0)], [0, 0.42, 1]))
        beam = skia.Path(); beam.moveTo(410, -80); beam.lineTo(670, -80); beam.lineTo(1120, 1560); beam.lineTo(-40, 1560); beam.close()
        pb = lin(0, 0, 0, 1500, [C('#FFE6BE', 0.16), C('#FFE6BE', 0.07), C('#FFE6BE', 0.0)], [0, 0.55, 1])
        pb.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 90)); b.drawPath(beam, pb)
        core_ = skia.Path(); core_.moveTo(480, -80); core_.lineTo(600, -80); core_.lineTo(820, 1300); core_.lineTo(260, 1300); core_.close()
        pc = lin(0, 0, 0, 1300, [C('#FFF0D2', 0.10), C('#FFF0D2', 0.0)])
        pc.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 60)); b.drawPath(core_, pc)
        b.drawRect(full, rad(540, 860, 1300, [C('#000000', 0.0), C('#000000', 0.0), C('#000000', 0.78)], [0, 0.42, 1]))
        b.drawRect(full, lin(0, 1380, 0, 1920, [C('#000000', 0.0), C('#000000', 0.55)]))
        b.drawImage(GRAIN, 0, 0)
        _BG = s.makeImageSnapshot()
    c.drawImage(_BG, 0, 0)


DUST = [dict(x=RNG.uniform(180, 900), y=RNG.uniform(260, 1400), r=RNG.uniform(1.4, 3.6), a=RNG.uniform(0.10, 0.34), w=RNG.uniform(0.3, 0.9),
             ph=RNG.uniform(0, 6.28), vy=RNG.uniform(5, 16), ax=RNG.uniform(6, 22)) for _ in range(34)]
BOKEH = [dict(x=RNG.uniform(60, 1020), y=RNG.uniform(300, 1500), r=RNG.uniform(16, 34), a=RNG.uniform(0.030, 0.060), w=RNG.uniform(0.2, 0.5),
              ph=RNG.uniform(0, 6.28), vy=RNG.uniform(8, 20), ax=RNG.uniform(14, 40)) for _ in range(7)]


def dust(c, t, items, blur):
    for d in items:
        x = d['x'] + d['ax'] * sin(d['w'] * t + d['ph']); y = d['y'] - d['vy'] * t
        beam = clamp(1 - abs(x - 540) / (190 + 0.36 * y)) ** 0.6           # nur im Lichtkegel sichtbar
        a = d['a'] * (0.65 + 0.35 * sin(1.7 * d['w'] * t + 2 * d['ph'])) * (beam if blur < 6 else 1.0)
        if a > 0.004:
            c.drawCircle(x, y, d['r'], P('#FFE9C8', a, blur=blur))


# ---------------------------------------------------------------- Gutschein (als Bild, dann perspektivisch gezeichnet)
CW, CH = 1000, 630


def make_card():
    s = skia.Surface(CW, CH); k = s.getCanvas(); k.clear(0)
    rr = skia.RRect.MakeRectXY(skia.Rect.MakeWH(CW, CH), 38, 38)
    k.save(); k.clipRRect(rr, doAntiAlias=True)
    k.drawPaint(lin(0, 0, CW, CH, [C('#FBF5E8'), C('#F1E8D6'), C('#E5D9C2')], [0, 0.55, 1]))
    k.drawImage(noise_img(CW, CH, 0.030, 3), 0, 0)
    fr = skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(30, 30, CW - 30, CH - 30), 16, 16)
    k.drawRRect(fr, P(GOLD, 0.85, stroke=2.5)); k.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(40, 40, CW - 40, CH - 40), 10, 10), P(GOLD, 0.40, stroke=1.2))
    # Band
    k.drawRect(skia.Rect.MakeXYWH(176, 0, 96, CH), P('#000000', 0.16, blur=10))
    k.drawRect(skia.Rect.MakeXYWH(184, 0, 80, CH), lin(184, 0, 264, 0, [C('#7C0E16'), C('#B21C25'), C('#D7373D'), C('#B21C25'), C('#7C0E16')], [0, 0.22, 0.5, 0.78, 1]))
    k.drawRect(skia.Rect.MakeXYWH(219, 0, 10, CH), P('#FFFFFF', 0.10))
    # Schleife
    bx, by = 224, 306
    for sx in (-1, 1):
        k.save(); k.translate(bx, by); k.scale(sx, 1)
        tail = skia.Path(); tail.moveTo(4, 14); tail.lineTo(74, 150); tail.lineTo(46, 142); tail.lineTo(34, 168); tail.lineTo(-6, 30); tail.close()
        k.drawPath(tail, lin(0, 20, 60, 160, [C('#B21C25'), C('#7C0E16')]))
        loop = skia.Path(); loop.moveTo(0, 0); loop.cubicTo(30, -86, 150, -98, 150, -18); loop.cubicTo(150, 44, 52, 34, 0, 0); loop.close()
        k.drawPath(loop, P('#000000', 0.22, blur=8))
        k.drawPath(loop, rad(92, -40, 110, [C('#E4484B'), C('#B21C25'), C('#7C0E16')], [0, 0.6, 1]))
        inner = skia.Path(); inner.moveTo(24, -6); inner.cubicTo(46, -52, 118, -62, 120, -20); inner.cubicTo(120, 8, 60, 10, 24, -6); inner.close()
        k.drawPath(inner, P('#5E0A11', 0.55))
        k.restore()
    k.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(bx - 30, by - 34, 60, 62), 16, 16), lin(bx - 30, 0, bx + 30, 0, [C('#8E131B'), C('#D7373D'), C('#8E131B')]))
    # Schrift
    text(k, 'Gutschein', 338, 232, font('dms', 106), P(INK), 'l', 0.5)
    k.drawLine(342, 276, 900, 276, P(INK, 0.28, stroke=2))
    text(k, '50 €', 330, 502, font('dms', 252), P(INK), 'l', -3)
    text(k, 'AUSGESTELLT 03/2023', 344, 566, font('med', 26), P('#7C705E'), 'l', 6)
    k.restore()
    k.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(1.5, 1.5, CW - 1.5, CH - 1.5), 37, 37), P('#FFFFFF', 0.55, stroke=3))
    return s.makeImageSnapshot()


CARD_IMG = make_card()
SRC = [skia.Point(0, 0), skia.Point(CW, 0), skia.Point(CW, CH), skia.Point(0, CH)]
EDGE = skia.Paint(AntiAlias=True); EDGE.setColorFilter(skia.ColorFilters.Blend(C('#9C8F78'), skia.BlendMode.kSrcIn))


def card(c, cx, cy, w, yaw, pitch, roll, sheen=None, glow=0.16):
    """Gutschein mit Perspektive. Winkel in Grad; sheen = Lage des Lichtstreifens (0..1) oder None."""
    h = w * CH / CW; R = Rz(radians(roll)) @ Rx(radians(pitch)) @ Ry(radians(yaw)); f = 2600.0
    q = []
    for (x, y) in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)):
        v = R @ np.array([x, y, 0.0]); k = f / (f + v[2]); q.append((cx + v[0] * k, cy + v[1] * k))
    n = R @ np.array([0, 0, -1.0])
    if glow > 0:
        c.save(); c.translate(cx, cy); c.scale(1.0, 0.72)
        c.drawCircle(0, 0, w * 0.95, rad(0, 0, w * 0.95, [C('#FFDFAE', glow), C('#FFDFAE', glow * 0.35), C('#FFDFAE', 0.0)], [0, 0.5, 1])); c.restore()
    m = skia.Matrix()
    for j in range(5, 0, -1):                                           # Kartenkante (Dicke)
        o = j * 1.9
        m.setPolyToPoly(SRC, [skia.Point(px - n[0] * o, py - n[1] * o + o * 0.35) for px, py in q])
        c.save(); c.concat(m); c.drawImage(CARD_IMG, 0, 0, SAMP, EDGE); c.restore()
    m.setPolyToPoly(SRC, [skia.Point(*p) for p in q])
    c.save(); c.concat(m)
    c.drawImage(CARD_IMG, 0, 0, SAMP)
    c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeWH(CW, CH), 38, 38), doAntiAlias=True)
    c.drawPaint(lin(0, 0, 0, CH, [C('#FFFFFF', 0.06), C('#000000', 0.0), C('#1A0E00', 0.22)], [0, 0.35, 1]))
    turn = clamp(abs(n[0]) * 0.9 + max(0.0, n[1]) * 0.8)
    if turn > 0.01:
        c.drawPaint(P('#0A0603', 0.38 * turn))
    if sheen is not None and 0 < sheen < 1:
        u = lerp(-320, CW + 320, sheen)
        c.save(); c.translate(u, 0); c.skew(-0.36, 0)
        c.drawRect(skia.Rect.MakeXYWH(-170, -40, 340, CH + 80), lin(-170, 0, 170, 0, [C('#FFFFFF', 0.0), C('#FFF6E0', 0.34), C('#FFFFFF', 0.0)]))
        c.restore()
    c.restore()
    return q


# ---------------------------------------------------------------- Eimer (nur im Hook)
def bin_(c, a, dy):
    if a <= 0.004:
        return
    cx, top, base = 540, 992 + dy, 1272 + dy; rx, ry, bx, by = 178, 42, 142, 33
    c.save(); c.translate(cx, base + 26); c.scale(1.0, 0.20)
    c.drawCircle(0, 0, 470, rad(0, 0, 470, [C('#FFDDA8', 0.30 * a), C('#FFDDA8', 0.10 * a), C('#FFDDA8', 0.0)], [0, 0.5, 1])); c.restore()
    c.drawOval(skia.Rect.MakeLTRB(cx - bx - 30, base - 6, cx + bx + 90, base + by + 34), P('#000000', 0.70 * a, blur=16))
    body = skia.Path(); body.moveTo(cx - rx, top); body.lineTo(cx - bx, base)
    body.arcTo(skia.Rect.MakeLTRB(cx - bx, base - by, cx + bx, base + by), 180, -180, False)
    body.lineTo(cx + rx, top); body.arcTo(skia.Rect.MakeLTRB(cx - rx, top - ry, cx + rx, top + ry), 0, 180, False); body.close()
    c.drawPath(body, lin(cx - rx, 0, cx + rx, 0, [C('#0E0D0C', a), C('#3A3530', a), C('#857A6E', a), C('#403B36', a), C('#191715', a), C('#0E0D0C', a)], [0, 0.12, 0.30, 0.52, 0.84, 1]))
    c.save(); c.clipPath(body, True)
    c.drawPaint(lin(0, top, 0, base + by, [C('#000000', 0.0), C('#000000', 0.50 * a)]))
    for i in range(-5, 6):                                               # Rillen
        u = i / 6.0; xt, xb = cx + u * rx * 0.985, cx + u * bx * 0.985; yo = ry * (1 - u * u) ** 0.5
        c.drawLine(xt, top + yo, xb, base + by * (1 - u * u) ** 0.5, P('#000000', 0.50 * a, stroke=4.5))
        c.drawLine(xt + 3.5, top + yo, xb + 3.5, base + by * (1 - u * u) ** 0.5, P('#FFFFFF', 0.08 * a, stroke=1.6))
    c.restore()
    c.drawLine(cx - rx + 2, top + 4, cx - bx + 2, base, P('#E9D2A8', 0.55 * a, stroke=3, blur=1.2))
    c.drawLine(cx + rx - 2, top + 4, cx + bx - 2, base, P('#E9D2A8', 0.22 * a, stroke=2.5, blur=1.2))
    c.drawOval(skia.Rect.MakeLTRB(cx - rx + 7, top - ry + 5, cx + rx - 7, top + ry - 3), lin(0, top - ry, 0, top + ry, [C('#3A322A', a), C('#0B0A09', a), C('#000000', a)], [0, 0.45, 1]))
    rim = lin(0, top - ry, 0, top + ry, [C('#F6E4C2', a), C('#8E8372', a), C('#C4B59B', a)], [0, 0.55, 1])
    rim.setStyle(skia.Paint.kStroke_Style); rim.setStrokeWidth(11)
    c.drawOval(skia.Rect.MakeLTRB(cx - rx, top - ry, cx + rx, top + ry), rim)
    c.drawArc(skia.Rect.MakeLTRB(cx - rx, top - ry, cx + rx, top + ry), 200, 140, False, P('#FFF4DC', 0.75 * a, stroke=3))


# ---------------------------------------------------------------- Zeitstrahl
def timeline(c, t):
    k0 = pr(t, T_GELTEN - 0.10, 0.60)
    if k0 <= 0:
        return
    xe = lerp(XS[0], XS[4], eio(k0))
    c.drawLine(XS[0], LY, xe, LY, P(CREAM, 0.50, stroke=3.5))
    bx = lerp(XS[1], XS[4], eio(pr(t, T_BAR0, T_BAR1 - T_BAR0))) if t >= T_BAR0 else None
    for i in range(5):
        ka = pr(t, T_GELTEN - 0.05 + i * 0.11, 0.30)
        if ka > 0:
            c.drawLine(XS[i], LY - 16, XS[i], LY + 16, P(CREAM, 0.75 * ka, stroke=3.5))
        if i < 4 and ka > 0:
            lit = clamp((bx - XS[i]) / (XS[1] - XS[0])) if (bx is not None and i >= 1) else 0.0
            text(c, str(2023 + i), (XS[i] + XS[i + 1]) / 2, LY + 72 + 8 * (1 - eo3(ka)), font('dms', 56), P(mix(MUTE, '#FFFFFF', 0.30 + 0.70 * lit), eo3(ka) * (0.85 + 0.15 * lit)), 'c', 1)
    if bx is not None:                                                   # die drei Jahre
        c.drawLine(XS[1], LY, bx, LY, P(REDL, 0.55, stroke=16, blur=10))
        c.drawLine(XS[1], LY, bx, LY, P(RED, 1.0, stroke=9, butt=True))
        c.drawCircle(bx, LY, 9, P(REDL))
    # Kauf-Marke: März 2023, wandert dann ans Jahresende
    kp = pr(t, T_REGEL - 0.06, 0.30)
    if kp > 0:
        kh = eio(pr(t, T_STARTET, T_ENDE - T_STARTET - 0.05)); mx = lerp(XBUY, XS[1], kh)
        col = mix(CREAM, REDL, pr(t, T_FRIST - 0.05, 0.25)); a = eo3(kp)
        c.drawLine(mx, LY - 30, mx, LY, P(col, a, stroke=3))
        c.drawCircle(mx, LY, 9 * back(kp, 1.4), P(col, a)); c.drawCircle(mx, LY, 15, P(col, 0.35 * a, stroke=2))
        a1 = a * (1 - pr(t, T_STARTET - 0.05, 0.25))
        if a1 > 0:
            text(c, 'gekauft 03/2023', XBUY - 12, LY - 46, font('dmsi', 46), P(CREAM, 0.95 * a1), 'l')
        a2 = eo3(pr(t, T_ENDE - 0.03, 0.32))
        if a2 > 0:
            text(c, 'Fristbeginn 31.12.2023', XS[1] - 12, LY - 46 - 8 * (1 - a2), font('dmsi', 46), P(REDL, a2), 'l')
    ke = pr(t, T_END + 0.02, 0.40)
    if ke > 0:
        a = eo3(ke); y = LY + 164 + 10 * (1 - a)
        f1, f2 = font('dmsi', 50), font('dms', 78); w2 = f2.measureText('31.12.2026')
        c.drawString('31.12.2026', XS[4] - w2, y, f2, P('#FFF8EA', a))
        text(c, 'gültig bis', XS[4] - w2 - 22, y, f1, P(CREAM, 0.88 * a), 'r')
        c.drawCircle(XS[4], LY, 15 * back(ke, 1.4), P(REDL, a)); c.drawCircle(XS[4], LY, 6, P('#FFF8EA', a))


def header(c):
    text(c, 'FAKTENFABRIK', 84, 268, font('med', 24), P(CREAM, 0.80), 'l', 8)
    text(c, 'Kleingedruckt · 04', 996, 272, font('serifi', 44), P(CREAM, 0.92), 'r')
    c.drawLine(84, 302, 996, 302, P(CREAM, 0.16, stroke=2))


def draw(c, t):
    background(c)
    dust(c, t, DUST, 1.2)
    z = 1 + 0.035 * t / 10.0
    c.save(); c.translate(540, 880); c.scale(z, z); c.translate(-540, -880)
    kt = eio(pr(t, 1.95, 0.75))
    c.save(); c.translate(540, 1190); c.scale(1.0, 0.34)
    c.drawCircle(0, 0, 560, rad(0, 0, 560, [C('#FFDDA8', 0.085 * kt), C('#FFDDA8', 0.03 * kt), C('#FFDDA8', 0.0)], [0, 0.55, 1])); c.restore()
    bin_(c, 1 - ei2(pr(t, 1.95, 0.5)), 230 * ei3(pr(t, 1.95, 0.6)))
    # --- Gutschein: fällt in Zeitlupe, bleibt bei „noch nicht“ in der Luft stehen, steigt dann als Hauptobjekt auf
    f = pr(t, 0, T_NOCH + 0.16); fe = 1 - (1 - f) ** 2.2
    hx, hy, hw = lerp(572, 546, fe), lerp(528, 736, fe), 520
    hyaw, hpit, hrol = lerp(24, -8, fe), lerp(-18, 15, fe), lerp(-12, 6, fe)
    fl = clamp((t - 2.6) / 1.2)                                         # ruhiges Schweben
    cx = lerp(hx, 540, kt); cy = lerp(hy, 552, kt) + 6 * sin(1.25 * t) * fl; w = lerp(hw, 576, kt)
    yaw = lerp(hyaw, -9, kt) + 3.0 * sin(0.9 * t + 1.0) * fl; pit = lerp(hpit, -6, kt) + 1.5 * sin(0.7 * t) * fl; rol = lerp(hrol, -2.5, kt) + 0.8 * sin(0.8 * t + 2.0) * fl
    pulse = sin(pi * pr(t, T_NOCH - 0.02, 0.60))
    sh = pr(t, 2.55, 1.05) if t < 5 else pr(t, T_BAR0 + 0.15, 1.10)
    card(c, cx, cy, w, yaw, pit, rol, sheen=sh, glow=0.15 + 0.16 * pulse)
    ka = eo3(pr(t, T_WEG - 0.05, 0.32)) * (1 - pr(t, 1.95, 0.22))
    if ka > 0:
        fq = font('serifi', 60); wq = fq.measureText('noch gültig?')
        c.drawString('noch gültig?', 968 - wq, 566 - 10 * (1 - ka), fq, P('#FFF8EA', ka))
        c.drawLine(968 - wq, 584, 968 - wq * (1 - ka), 584, P(REDL, ka, stroke=3))
    # --- „3 Jahre“
    k3 = pr(t, T_DREI - 0.04, 0.50)
    if k3 > 0:
        f3, fj = font('dms', 332), font('dmsi', 150); w3 = f3.measureText('3'); wj = fj.measureText('Jahre'); x0 = 540 - (w3 + 30 + wj) / 2
        a = eo3(k3); s3 = lerp(1.07, 1.0, eo3(k3))
        c.save(); c.translate(x0 + w3 / 2, 900); c.scale(s3, s3); c.translate(-(x0 + w3 / 2), -900)
        g = lin(0, 780, 0, 1010, [C('#FFF8EA', a), C('#E8D6B0', a)]); c.drawString('3', x0, 1004, f3, P('#000000', 0.5 * a, blur=14)); c.drawString('3', x0, 1004, f3, g)
        c.restore()
        aj = eo3(pr(t, T_JAHRE - 0.06, 0.40))
        if aj > 0:
            c.drawString('Jahre', x0 + w3 + 30 + 14 * (1 - aj), 1004, fj, P('#FFF8EA', aj))
    timeline(c, t)
    c.restore()
    dust(c, t, BOKEH, 9)
    header(c)
    captions(c, t, CAP)


if __name__ == '__main__':
    import sys
    if sys.argv[1] == 'sheet':
        sheet(draw, [0.0, 0.9, 1.5, 2.25, 3.9, 4.6, 6.4, 7.6, 8.3, 9.9], LAB + '/out/kino_sheet.png', 0.25, 5)
    elif sys.argv[1] == 'big':
        sheet(draw, [float(x) for x in sys.argv[2:]], LAB + '/out/kino_big.png', 0.46, 2)
    else:
        build_audio(10.0, SFX, LAB + '/out/kino.wav'); render(draw, 10.0, LAB + '/out/LOOK3_KINO.mp4', LAB + '/out/kino.wav')
