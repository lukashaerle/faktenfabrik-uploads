"""LOOK 1 „KLAR“ – helle, präzise Flach-Infografik: Tintenkontur, eine Signalfarbe, Mono-Etiketten, dunkle Untertitel-Pille."""
from core import *

BG, FLOOR, INK, RED, WHITE, MUTE = '#F2F1ED', '#E4E2DB', '#15171C', '#E5432D', '#FFFFFF', '#8B8F97'
GREY, GREY_D, LID, LID_D = '#CDD1D6', '#B3B8BF', '#9BA1AA', '#7E848D'
OUT = 7
T_NOCH, T_WEG, T_GUT2, T_GELTEN, T_REGEL = wt('noch'), wt('weg'), wt('Gutscheine'), wt('gelten'), wt('Regel')
T_DREI, T_FRIST, T_STARTET, T_ENDE, T_KAUF = wt('drei'), wt('Frist'), wt('startet'), wt('Ende'), wt('Kaufjahres')
X0, X1, LY = 150, 930, 1010                          # Zeitstrahl
XS = [X0 + (X1 - X0) * i / 4 for i in range(5)]      # Jahresgrenzen 2023 … Ende 2026
XBUY = X0 + (X1 - X0) / 4 * (2.5 / 12)               # gekauft im März 2023
T_BAR0, T_BAR1 = T_KAUF + 0.08, T_KAUF + 0.88
T_END = T_BAR1
CAP = dict(font='bold', size=54, y=1392, pill=INK, fg='#ffffff', dim=0.42, radius=22)
SFX = [(T_NOCH + 0.10, 'thud', 0.8), (T_WEG - 0.04, 'pop', 1.0), (1.97, 'whoosh', 0.35)] + \
      [(T_GELTEN + 0.02 + i * 0.10, 'tick', 1.0) for i in range(5)] + \
      [(T_REGEL - 0.08, 'pop', 0.8), (T_DREI, 'thud', 0.85), (T_FRIST, 'pop', 0.8), (T_ENDE - 0.03, 'pop', 0.9),
       (T_BAR0 + 0.27, 'tick', 1.0), (T_BAR0 + 0.53, 'tick', 1.0), (T_END, 'thud', 1.0)]


def header(c):
    text(c, 'FAKTENFABRIK', 84, 268, font('mono', 25), P(INK), 'l', 7)
    text(c, '04', 996, 268, font('mono', 25), P(INK), 'r', 2)
    chip(c, 'KLEINGEDRUCKT', 940, 238, font('mono', 22), WHITE, RED, padx=16, pady=11, r=7, align='r', track=4)
    c.drawLine(84, 302, 996, 302, P(INK, 0.14, stroke=2.5))


def bin_(c, cx, base, k):
    top = base - 400; rt, rb, lr = 235, 196, 250
    c.drawOval(skia.Rect.MakeLTRB(cx - 250, base - 6, cx + 250, base + 46), P(INK, 0.16, blur=12))

    def lid():
        cy = lerp(top - 240, top - 6, k); ry = lerp(214, 46, k)
        if k > 0.5:
            c.drawOval(skia.Rect.MakeLTRB(cx - lr, cy - ry + 16, cx + lr, cy + ry + 16), P(LID_D)); c.drawOval(skia.Rect.MakeLTRB(cx - lr, cy - ry + 16, cx + lr, cy + ry + 16), P(INK, stroke=OUT))
        r = skia.Rect.MakeLTRB(cx - lr, cy - ry, cx + lr, cy + ry)
        c.drawOval(r, P(LID)); c.drawOval(skia.Rect.MakeLTRB(cx - 172, cy - ry * 0.62, cx + 172, cy + ry * 0.62), P(WHITE, 0.16)); c.drawOval(r, P(INK, stroke=OUT))
        if k > 0.85:
            rrect(c, cx - 54, cy - 14, 108, 24, 12, P(LID_D)); rrect(c, cx - 54, cy - 14, 108, 24, 12, P(INK, stroke=5))
    if k <= 0.5:
        lid()
    p = skia.Path(); p.moveTo(cx - rt, top); p.lineTo(cx - rb, base)
    p.arcTo(skia.Rect.MakeLTRB(cx - rb, base - 32, cx + rb, base + 32), 180, -180, False); p.lineTo(cx + rt, top)
    p.arcTo(skia.Rect.MakeLTRB(cx - rt, top - 40, cx + rt, top + 40), 0, 180, False); p.close()
    c.drawPath(p, P(GREY))
    c.save(); c.clipPath(p, doAntiAlias=True)
    c.drawRect(skia.Rect.MakeLTRB(cx + 92, top - 44, cx + 300, base + 44), P(GREY_D))
    for i in range(-2, 3):
        c.drawLine(cx + i * 78, top + 78, cx + i * 65, base - 38, P(INK, 0.16, stroke=6))
    c.restore()
    c.drawPath(p, P(INK, stroke=OUT))
    rim = skia.Rect.MakeLTRB(cx - rt, top - 40, cx + rt, top + 40)
    c.drawOval(rim, P('#DADDE1')); c.drawOval(skia.Rect.MakeLTRB(cx - rt + 22, top - 27, cx + rt - 22, top + 31), P('#2A2D34')); c.drawOval(rim, P(INK, stroke=OUT))
    if k > 0.5:
        lid()


def card(c, cx, cy, ang, s=1.0):
    c.save(); c.translate(cx, cy); c.rotate(ang); c.scale(s, s)
    body = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-220, -140, 440, 280), 26, 26)
    c.drawRRect(body, P(WHITE))
    c.save(); c.clipRRect(body, True)
    c.drawRect(skia.Rect.MakeXYWH(-220 + 58, -140, 46, 280), P(RED))
    c.restore()
    for sg in (-1, 1):                                                       # Schleife
        c.save(); c.translate(-139, -52); c.rotate(sg * 32)
        r = skia.Rect.MakeXYWH(4 if sg > 0 else -66, -17, 62, 34)
        c.drawOval(r, P(RED)); c.drawOval(r, P(INK, stroke=5)); c.restore()
    rrect(c, -152, -66, 26, 28, 7, P(RED)); rrect(c, -152, -66, 26, 28, 7, P(INK, stroke=5))
    text(c, 'GUTSCHEIN', -78, -62, font('black', 43), P(INK), 'l', 1.5)
    text(c, 'AUSGESTELLT 03/2023', -76, -24, font('monom', 19.5), P(MUTE), 'l', 1.2)
    text(c, '50 €', -80, 100, font('black', 116), P(INK), 'l')
    c.drawRRect(body, P(INK, stroke=OUT))
    c.restore()


def timeline(c, t):
    k = eo3(pr(t, T_GELTEN - 0.10, 0.55))
    if k <= 0:
        return
    c.drawLine(X0, LY, lerp(X0, X1, k), LY, P(INK, stroke=9))
    for i, x in enumerate(XS):
        a = eo3(pr(t, T_GELTEN - 0.06 + i * 0.10, 0.18))
        if a > 0:
            c.drawLine(x, LY - 24 * a, x, LY + 24 * a, P(INK, stroke=9))
    bx = lerp(XS[1], X1, eio(pr(t, T_BAR0, T_BAR1 - T_BAR0)))
    for i, yr in enumerate(('2023', '2024', '2025', '2026')):
        a = eo3(pr(t, T_GELTEN + 0.04 + i * 0.10, 0.25)); xm = (XS[i] + XS[i + 1]) / 2
        on = i > 0 and bx >= XS[i] + 60
        if a > 0:
            text(c, yr, xm, 1090 + (1 - a) * 10, font('mono', 39), P(INK if on else MUTE, a), 'c', 1)
    kb = pr(t, T_REGEL - 0.10, 0.28)                                        # Kauf-Markierung
    if kb > 0:
        c.drawCircle(XBUY, LY, 17 * back(kb), P(WHITE)); c.drawCircle(XBUY, LY, 17 * back(kb), P(INK, stroke=8))
        fa = 1 - pr(t, T_STARTET - 0.05, 0.3)
        if fa > 0:
            c.save(); c.translate(X0 - 6, 932); c.scale(back(kb), back(kb))
            chip(c, 'GEKAUFT 03/2023', 0, -30, font('mono', 29), INK, WHITE, padx=18, pady=14, r=9, track=2.5, stroke=(INK, 5), a=fa)
            c.restore()
    if t >= T_FRIST:                                                        # Frist: Marke wandert ans Jahresende, dann wächst der Balken
        mx = lerp(XBUY, XS[1], eio(pr(t, T_STARTET, T_ENDE - T_STARTET - 0.05)))
        if t >= T_BAR0:
            c.drawLine(XS[1], LY, bx, LY, P(RED, stroke=24))
        m = back(pr(t, T_FRIST, 0.25)); x_ = mx if t < T_BAR0 else XS[1]
        c.drawCircle(x_, LY, 22 * m, P(RED)); c.drawCircle(x_, LY, 22 * m, P(INK, stroke=8))
        k1 = pr(t, T_ENDE - 0.05, 0.28)
        if k1 > 0:
            c.save(); c.translate(XS[1], 932); c.scale(back(k1), back(k1))
            chip(c, 'START 31.12.2023', 0, -30, font('mono', 29), RED, WHITE, padx=18, pady=14, r=9, align='c', track=2.5, stroke=(RED, 5))
            c.restore()
        if t >= T_BAR0:
            c.drawCircle(bx, LY, 22, P(RED)); c.drawCircle(bx, LY, 22, P(INK, stroke=8))
        k2 = pr(t, T_END, 0.32)
        if k2 > 0:                                                          # Ergebnis-Banner
            f = font('mono', 41); wb = tw('GÜLTIG BIS 31.12.2026', f, 3) + 56; sc = back(k2, 1.5)
            c.save(); c.translate(956 - wb / 2, 1216); c.scale(sc, sc)
            tri = skia.Path(); tri.moveTo(wb / 2 - 26 - 16, -42); tri.lineTo(wb / 2 - 26, -66); tri.lineTo(wb / 2 - 26 + 16, -42); tri.close()
            c.drawPath(tri, P(RED)); rrect(c, -wb / 2, -44, wb, 88, 14, P(RED))
            text(c, 'GÜLTIG BIS 31.12.2026', -wb / 2 + 28, 15, f, P(WHITE), 'l', 3)
            c.restore()


_BGIMG = None


def background(c):
    global _BGIMG
    if _BGIMG is None:
        s = skia.Surface(W, H); b = s.getCanvas(); b.clear(C(BG))
        b.drawRect(skia.Rect.MakeWH(W, H), rad(540, 640, 1150, [C(WHITE, 0.6), C(WHITE, 0.0)]))
        for gy in range(30, H, 60):
            for gx in range(30, W, 60):
                b.drawCircle(gx, gy, 2.2, P(INK, 0.07))
        _BGIMG = s.makeImageSnapshot()
    c.drawImage(_BGIMG, 0, 0)


def draw(c, t):
    background(c)
    kt = eio(pr(t, 1.95, 0.55))                               # Übergang Hook → Erklärung (Blick fährt nach oben, Karte bleibt Held)
    z = 1 + 0.02 * pr(t, 2.5, 7.5)
    c.save(); c.translate(540, 820); c.scale(z, z); c.translate(-540, -820)
    fy = 1250 + kt * 1050
    if fy < H + 60:
        c.drawRect(skia.Rect.MakeLTRB(-40, fy, W + 40, H + 80), lin(0, fy, 0, fy + 560, [C(FLOOR), C(BG)]))
        c.drawLine(-40, fy, W + 40, fy, P(INK, 0.10, stroke=3))
        bin_(c, 540, fy, ei3(pr(t, T_NOCH - 0.10, 0.20)))
    f = pr(t, 0, T_NOCH + 0.20)                                # Karte: fällt, landet auf dem Deckel, wandert dann nach links oben
    hx, hy, ha = lerp(628, 548, f), lerp(578, 697, f ** 1.5), lerp(-22, -9, f) + 2 * eo3(pr(t, T_NOCH + 0.20, 0.3))
    cx, cy, ang, s = lerp(hx, 302, kt), lerp(hy, 520, kt), lerp(ha, -3, kt), lerp(1.18, 0.98, kt)
    if f >= 1 and kt < 1:
        c.drawOval(skia.Rect.MakeLTRB(cx - 215, fy - 422, cx + 215, fy - 386), P(INK, 0.20 * (1 - kt), blur=9))
    card(c, cx, cy, ang, s)
    q = pr(t, T_WEG - 0.05, 0.26); qa = 1 - pr(t, 1.95, 0.2)
    if q > 0 and qa > 0:
        c.save(); c.translate(800, 492); c.rotate(5); c.scale(back(q, 1.6), back(q, 1.6))
        chip(c, 'NOCH GÜLTIG?', 0, -30, font('mono', 33), WHITE, RED, padx=22, pady=16, r=10, align='c', track=3, a=qa)
        c.restore()
    k3 = pr(t, T_DREI - 0.02, 0.30)                            # „3 JAHRE“ rechts neben der Karte
    if k3 > 0:
        sc = lerp(0.86, 1.0, back(k3, 1.5))
        c.save(); c.translate(772, 560); c.scale(sc, sc); c.translate(-772, -560)
        text(c, '3', 772, 610, font('black', 330), P(RED, eo3(k3)), 'c')
        text(c, 'JAHRE', 772, 722, font('black', 100), P(INK, eo3(k3)), 'c', 2)
        c.restore()
    timeline(c, t)
    c.restore()
    header(c)
    captions(c, t, CAP)


if __name__ == '__main__':
    import sys
    if sys.argv[1] == 'sheet':
        sheet(draw, [0.0, 0.9, 1.5, 2.25, 3.9, 4.6, 6.4, 7.6, 8.3, 9.9], LAB + '/out/klar_sheet.png', 0.25, 5)
    elif sys.argv[1] == 'still':
        still(draw, float(sys.argv[2]), LAB + '/out/klar_%s.png' % sys.argv[2])
    else:
        build_audio(10.0, SFX, LAB + '/out/klar.wav'); render(draw, 10.0, LAB + '/out/LOOK1_KLAR.mp4', LAB + '/out/klar.wav')
