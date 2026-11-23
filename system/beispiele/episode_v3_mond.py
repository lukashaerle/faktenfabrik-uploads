"""Episode 24.11. 17:30: Supermond – der Fingernagel-Test (Editing V2, Viral-Aufbau V3 final: Loop-Ende, kein Abspann)"""
import math
import render as L
import edit2 as E2
from render import skia, W, H, P, clamp, ease, ease_out, lerp, mixc, word_t
from edit2 import ICE, ICE2, HEAT, HEAT2, GOLD, INKW, DIM, kin

EDIT = 2
LOOP = True                  # Viral-Aufbau V3: kein Abspann, keine Abo-Karte – letzter Satz läuft in Satz 1 zurück
TOPIC = 'SUPERMOND HEUTE'
HOOK_TEXT = 'SUPERMOND\n= FINGERNAGEL?'
HOOK_COLORS = ['#ffe2a8', GOLD]
HOOK_END = 3.3
HIGHLIGHT = ['Supermond', 'Fingernagel?', 'Test:', 'gleich', 'NASA.', 'riesig?', 'Mondtäuschung.', 'genauso', '24.000', 'kaum.', 'geklärt.', 'Schreib']
MOON = '#ffe2a8'
ORANGE = '#ffb15a'
RED = '#ff5a4a'
GREEN = '#5fe39a'
NIGHT = '#2a3bff'
PINK = '#ff8ad8'


# ---------------------------------------------------------------- Motive
def moon(c, x, y, r, color=MOON, a=255):
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeRadial(skia.Point(x, y), r * 2.4, [L.col(color, int(a * 0.35)), L.col(color, 0)]))
    c.drawCircle(x, y, r * 2.4, p)
    c.drawCircle(x, y, r, P(color, a))
    for dx, dy, rr in [(-0.3, -0.2, 0.22), (0.25, 0.1, 0.16), (-0.05, 0.35, 0.12), (0.35, -0.35, 0.1)]:
        c.drawCircle(x + dx * r, y + dy * r, rr * r, P(mixc(color, '#8a7a5a', 0.45), int(a * 0.55)))


def skyline(c, y, color='#060a18', edge=DIM):
    p = skia.Path(); p.moveTo(0, H)
    xs = [0, 90, 90, 200, 200, 260, 260, 380, 380, 470, 470, 600, 600, 700, 700, 820, 820, 900, 900, 1080]
    hs = [80, 80, 190, 190, 120, 120, 260, 260, 150, 150, 220, 220, 100, 100, 300, 300, 160, 160, 110, 110]
    for x, h in zip(xs, hs):
        p.lineTo(x, y - h)
    p.lineTo(1080, H); p.close()
    c.drawPath(p, P(color, 255)); c.drawPath(p, P(edge, 200, stroke=5))


def earth(c, x, y, r):
    c.drawCircle(x, y, r, P('#2a6bff', 230))
    for dx, dy, rr in [(-0.3, -0.2, 0.35), (0.3, 0.3, 0.28)]:
        c.drawCircle(x + dx * r, y + dy * r, rr * r, P(GREEN, 200))
    c.drawCircle(x, y, r, P(INKW, 255, stroke=6))


def arm_thumb(c, tx, ty, s, a=255):
    """Ausgestreckter Arm von unten rechts, Daumen zeigt nach oben; (tx, ty) = Daumennagel."""
    c.save(); c.translate(tx, ty); c.scale(s, s)
    fill, line = P('#0a1226', a), P(INKW, a, stroke=9)
    arm = skia.Path(); arm.moveTo(30, 200); arm.lineTo(520, 900); arm.lineTo(700, 820); arm.lineTo(150, 130); arm.close()
    c.drawPath(arm, fill); c.drawPath(arm, line)
    fist = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-70, 70, 230, 190), 70, 70)
    c.drawRRect(fist, fill); c.drawRRect(fist, line)
    th = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-40, -40, 80, 160), 40, 40)
    c.drawRRect(th, fill); c.drawRRect(th, line)
    c.drawRoundRect(skia.Rect.MakeXYWH(-26, -28, 52, 52), 18, 18, P(GOLD, a, stroke=6))
    c.restore()


def brain(c, x, y, s, color='#ff8ad8', a=255):
    """Gehirn von oben: gewellter Umriss, Mittelfurche, Windungen."""
    c.save(); c.translate(x, y); c.scale(s, s)
    body = skia.Path(); body.addOval(skia.Rect.MakeXYWH(-205, -165, 410, 330))
    n = 12
    for k in range(n):
        an = 2 * math.pi * k / n
        bump = skia.Path(); bump.addCircle(215 * math.cos(an), 172 * math.sin(an), 62)
        body = skia.Op(body, bump, skia.PathOp.kUnion_PathOp)
    c.drawPath(body, P(color, int(a * 0.3))); c.drawPath(body, P(color, a, stroke=9))
    c.drawLine(0, -225, 0, 225, P(color, a, stroke=9))
    for sx in (-1, 1):
        for (x0, y0, x1, y1, bend) in [(40, -150, 190, -90, -40), (50, -50, 230, -10, 40), (40, 40, 220, 80, -40), (50, 130, 180, 150, 30)]:
            pth = skia.Path(); pth.moveTo(sx * x0, y0); pth.quadTo(sx * (x0 + x1) / 2, (y0 + y1) / 2 + bend, sx * x1, y1)
            c.drawPath(pth, P(color, a, stroke=7))
    c.restore()


def arm_finger(c, tx, ty, s, a=255):
    """Ausgestreckter Arm von unten rechts, Zeigefinger zeigt nach oben; (tx, ty) = Mitte des Fingernagels."""
    c.save(); c.translate(tx, ty); c.scale(s, s)
    fill, line = P('#0a1226', a), P(INKW, a, stroke=9)
    arm = skia.Path(); arm.moveTo(40, 300); arm.lineTo(520, 980); arm.lineTo(700, 900); arm.lineTo(170, 230); arm.close()
    c.drawPath(arm, fill); c.drawPath(arm, line)
    fist = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-60, 150, 240, 200), 70, 70)
    c.drawRRect(fist, fill); c.drawRRect(fist, line)
    fg = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-36, -40, 72, 250), 36, 36)
    c.drawRRect(fg, fill); c.drawRRect(fg, line)
    c.drawRoundRect(skia.Rect.MakeXYWH(-26, -26, 52, 52), 18, 18, P(GOLD, a, stroke=7))
    c.restore()


def nail_big(c, x, y, s, a=255):
    """Fingerkuppe groß: Finger von unten, Nagel als goldener Rahmen (Breite 300 * s)."""
    c.save(); c.translate(x, y); c.scale(s, s)
    fg = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-200, -230, 400, 760), 190, 190)
    c.drawRRect(fg, P('#0a1226', a)); c.drawRRect(fg, P(INKW, a, stroke=10))
    nl = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-150, -170, 300, 330), 110, 110)
    c.drawRRect(nl, P(GOLD, int(a * 0.22))); c.drawRRect(nl, P(GOLD, a, stroke=12))
    c.restore()


def photo(c, x, y, mode, k=1.0, mr=70, label='', s=0.9):
    """Foto-Karte (Sofortbild): mode 'horizont' = Mond über Häusern, 'oben' = Mond hoch am Himmel. Mond in beiden gleich groß."""
    a = int(255 * clamp(k * 1.4))
    c.save(); c.translate(x, y); c.scale(s * (0.9 + 0.1 * k), s * (0.9 + 0.1 * k))
    c.drawRoundRect(skia.Rect.MakeXYWH(-200, -260, 400, 520), 22, 22, P(INKW, a))
    c.drawRect(skia.Rect.MakeXYWH(-176, -236, 352, 380), P('#0a1226', a))
    if mode == 'horizont':
        c.drawCircle(0, 30, mr, P(ORANGE, a))
        pts = [(-176, 144), (-176, 80), (-120, 80), (-120, 40), (-60, 40), (-60, 100), (10, 100), (10, 60), (70, 60), (70, 110), (130, 110), (130, 70), (176, 70), (176, 144)]
        p = skia.Path(); p.moveTo(*pts[0])
        for q in pts[1:]:
            p.lineTo(*q)
        p.close(); c.drawPath(p, P('#04060d', a)); c.drawPath(p, P(DIM, a, stroke=4))
    else:
        c.drawCircle(0, -120, mr, P(MOON, a))
        for sx, sy in [(-130, -40), (110, -200), (120, 20), (-90, 90), (40, 110)]:
            c.drawCircle(sx, sy, 5, P(INKW, a))
    if label:
        E2.text(c, label, 0, 218, 40, '#0b1020', a=a, shadow=False, maxw=340)
    c.restore()


def bubble(c, x, y, s, t, a=255):
    """Kommentar-Sprechblase mit drei tippenden Punkten."""
    c.save(); c.translate(x, y); c.scale(s, s)
    r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-260, -150, 520, 300), 90, 90)
    c.drawRRect(r, P('#0a1226', int(a * 0.92))); c.drawRRect(r, P(INKW, a, stroke=10))
    tl = skia.Path(); tl.moveTo(-150, 140); tl.lineTo(-190, 250); tl.lineTo(-60, 146); tl.close()
    c.drawPath(tl, P('#0a1226', a)); c.drawPath(tl, P(INKW, a, stroke=10))
    c.drawLine(-140, 146, -70, 146, P('#0a1226', a, stroke=14))
    for k in range(3):
        up = max(0.0, math.sin(t * 7 - k * 0.9)) * 26
        c.drawCircle(-110 + k * 110, -up, 34, P(GOLD, a))
    c.restore()


def opening(c, lt, rise=True):
    """Startbild = Schlussbild (Loop): riesiger Mond steigt hinter Häusern auf – bewegt sich ab Bild 0.
    rise=False (letzte Einstellung): Mond steht dort, wo er in Bild 0 losläuft -> der Loop springt nicht."""
    E2.stage(c, ORANGE, spot=(0.5, 0.66), strength=1.15)
    if rise:
        E2.push(c, lt)
    u = ease_out(clamp(lt / 1.6)) if rise else 0.0
    def dr(cc):
        moon(cc, 540, lerp(1370, 1290, u), 300 * (1 + (0.0 if rise else 0.015 * math.sin(lt * 5))), ORANGE)
        skyline(cc, 1600)
    E2.glow(c, dr)


# ---------------------------------------------------------------- Szenen
def s1(c, t, d):
    i, lt, ld = E2.shots(0, t, d, ['nicht'])
    if i == 0:                                  # Wetten, der Supermond heute ist …
        opening(c, lt)
    else:                                       # … nicht größer als dein Fingernagel?
        E2.stage(c, NIGHT, spot=(0.5, 0.58), strength=1.1)
        E2.push(c, lt)
        u = ease_out(clamp(lt / 0.55))
        def dr(cc):
            moon(cc, 430, 1180, 26)
            arm_finger(cc, lerp(760, 560, u), lerp(1420, 1180, u), 1.0)
            if u >= 1:
                E2.text(cc, '=', 495, 1204, 70, GOLD, shadow=False)
        E2.glow(c, dr)


def s2(c, t, d):
    i, lt, ld = E2.shots(1, t, d, ['arm'])
    if i == 0:                                  # Mach den Test:
        E2.impact(c, lt, 'MACH DEN TEST', color=GOLD, tint=NIGHT, size=200)
    else:                                       # Arm ausstrecken, Zeigefinger neben den Mond.
        E2.stage(c, NIGHT, spot=(0.5, 0.56))
        E2.push(c, lt)
        tz = E2.at(1, 'zeigefinger', default=2.1) - (t - lt)
        u = ease_out(clamp((lt - 0.05) / 0.9))
        def dr(cc):
            moon(cc, 430, 1160, 26)
            arm_finger(cc, lerp(900, 560, u), lerp(1640, 1160, u), 1.0)
        E2.glow(c, dr)
        E2.word(c, 'SCHRITT 1', W / 2, 650, 170, GOLD, lt, 0.1, maxw=860, hold=max(0.5, tz - 0.15), snd='pop')
        E2.word(c, 'SCHRITT 2', W / 2, 650, 170, MOON, lt, tz, maxw=860, snd='pop')


def s3(c, t, d):
    i, lt, ld = E2.shots(2, t, d, ['sagt'])
    if i == 0:                                  # Fingernagel und Mond sind etwa gleich groß
        E2.stage(c, '#7b5cff', spot=(0.5, 0.56))
        E2.push(c, lt)
        tm = E2.at(2, 'mond', default=0.9) - (t - lt)
        tg = E2.at(2, 'gleich', default=1.7) - (t - lt)
        def dr(cc):
            nail_big(cc, 250, 1230, 0.9)
            km = kin(lt, tm, 0.2)
            if km > 0:
                moon(cc, 730, 1215, 138 * km)
            if lt > tg:
                E2.text(cc, '=', 490, 1262, 140, INKW, shadow=False, k=kin(lt, tg, 0.15))
        E2.glow(c, dr)
        E2.word(c, 'GLEICH GROSS', W / 2, 650, 150, GREEN, lt, tg, maxw=860)
    else:                                       # – sagt die NASA.
        E2.impact(c, lt, 'NASA', sub='SAGT: ETWA GLEICH GROSS', color=INKW, tint=NIGHT, size=300)


def s4(c, t, d):                                # Warum wirkt er am Horizont dann so riesig?
    E2.stage(c, ORANGE, spot=(0.5, 0.66), strength=1.15)
    E2.push(c, t)
    tr = E2.at(3, 'riesig', default=1.7)
    gro = 0.8 + 0.2 * ease_out(clamp(t / 0.5)) + 0.18 * ease_out(clamp((t - tr + 0.25) / 0.4))
    def dr(cc):
        moon(cc, 540, 1310, 270 * gro, ORANGE)
        skyline(cc, 1600)
    E2.glow(c, dr)
    E2.word(c, 'WARUM SO RIESIG?', W / 2, 650, 118, ORANGE, t, 0.1, maxw=860)


def s5(c, t, d):
    i, lt, ld = E2.shots(4, t, d, ['die'])
    if i == 0:                                  # Dein Gehirn trickst dich aus:
        E2.stage(c, PINK, spot=(0.5, 0.58), strength=1.0)
        E2.push(c, lt)
        tt = E2.at(4, 'trickst', default=0.8) - (t - lt)
        E2.glow(c, lambda cc: brain(cc, 540, 1250, 1.3))
        E2.word(c, 'DEIN GEHIRN!', W / 2, 650, 160, PINK, lt, 0.1, maxw=860)
    else:                                       # die Mondtäuschung.
        E2.impact(c, lt, 'MONDTÄUSCHUNG', sub='EIN TRICK IM KOPF', color=MOON, tint=PINK, size=170)


def s6(c, t, d):
    i, lt, ld = E2.shots(5, t, d, ['am'])
    if i == 0:                                  # Fotos zeigen:
        E2.stage(c, '#4aa8ff', spot=(0.5, 0.58))
        E2.push(c, lt)
        def dr(cc):
            photo(cc, 255, 1235, 'horizont', k=kin(lt, 0.0, 0.2), label='HORIZONT')
            photo(cc, 675, 1235, 'oben', k=kin(lt, 0.25, 0.2), label='HOCH OBEN')
        E2.glow(c, dr)
        E2.word(c, 'FOTO-BEWEIS', W / 2, 650, 160, GOLD, lt, 0.1, maxw=860, snd='pop')
    else:                                       # Am Horizont ist er genauso breit wie hoch oben.
        E2.stage(c, GREEN, spot=(0.5, 0.58), strength=0.9)
        E2.push(c, lt)
        tg = E2.at(5, 'genauso', default=1.0) - (t - lt)
        kb = kin(lt, tg, 0.2)
        def dr(cc):
            photo(cc, 255, 1235, 'horizont', label='HORIZONT')
            photo(cc, 675, 1235, 'oben', label='HOCH OBEN')
            if kb > 0:                           # Messklammern: gleiche Breite
                for x, yy in ((255, 1262), (675, 1127)):
                    for sx in (-63, 63):
                        cc.drawLine(x + sx, yy - 86 * kb, x + sx, yy + 86 * kb, P(GREEN, 255, stroke=7))
                E2.text(cc, '=', 465, 1265, 110, GREEN, shadow=False, k=kb)
        E2.glow(c, dr)
        E2.word(c, 'GENAUSO BREIT', W / 2, 650, 140, GREEN, lt, tg, maxw=860)


def s7(c, t, d):
    i, lt, ld = E2.shots(6, t, d, ['24'])
    if i == 0:                                  # Heute ist er zwar rund …
        E2.stage(c, '#4aa8ff', spot=(0.5, 0.56))
        E2.push(c, lt)
        def dr(cc):
            earth(cc, 190, 1230, 120)
            moon(cc, 800, 1230, 62)
            for k in range(8):
                cc.drawLine(335 + k * 50, 1230, 360 + k * 50, 1230, P(DIM, 255, stroke=6))
        E2.glow(c, dr)
        E2.tag(c, 'IM SCHNITT: 384.400 KM', W / 2, 660, lt, 0.1, size=40)
    else:                                       # … 24.000 Kilometer näher als im Schnitt.
        E2.stage(c, '#4aa8ff', spot=(0.5, 0.56))
        E2.push(c, lt)
        u = ease_out(clamp(lt / 0.6))
        def dr(cc):
            earth(cc, 190, 1230, 120)
            mx = lerp(800, 720, u)
            moon(cc, mx, 1230, 66)
            cc.drawLine(335, 1230, mx - 90, 1230, P(GOLD, 255, stroke=8))
            cc.drawCircle(800, 1230, 62, P(DIM, 200, stroke=5))
        E2.glow(c, dr)
        E2.word(c, '24.000 KM NÄHER', W / 2, 650, 120, GOLD, lt, 0.05, maxw=860)
        E2.tag(c, 'HEUTE: RUND 360.800 KM', W / 2, 1480, lt, 0.9, size=38)


def s8(c, t, d):                                # Mit bloßem Auge siehst du das aber kaum.
    E2.stage(c, '#7b5cff', spot=(0.5, 0.56))
    E2.push(c, t)
    ts = E2.at(7, 'siehst', default=1.0)
    def dr(cc):
        moon(cc, 270, 1220, 150)
        moon(cc, 700, 1220, 160)
    E2.glow(c, dr)
    E2.tag(c, 'NORMAL', 270, 1480, t, 0.1, size=38)
    E2.tag(c, 'HEUTE', 700, 1480, t, 0.25, size=38)
    E2.word(c, 'SIEHST DU KAUM', W / 2, 650, 130, MOON, t, ts - 0.05, maxw=860)


def s9(c, t, d):
    i, lt, ld = E2.shots(8, t, d, ['ist'])
    if i == 0:                                  # Warum das Gehirn so trickst, …
        E2.stage(c, PINK, spot=(0.5, 0.58), strength=1.0)
        E2.push(c, lt)
        def dr(cc):
            brain(cc, 540, 1250, 1.3)
            E2.text(cc, '?', 540, 1330, 260, INKW, shadow=False, k=kin(lt, 0.2, 0.2))
        E2.glow(c, dr)
        E2.word(c, 'WARUM?', W / 2, 650, 200, PINK, lt, 0.1)
    else:                                       # … ist bis heute nicht endgültig geklärt.
        E2.stage(c, '#4aa8ff', spot=(0.5, 0.56))
        E2.push(c, lt)
        tg = E2.at(8, 'geklärt', default=2.6) - (t - lt)
        E2.glow(c, lambda cc: E2.text(cc, '?', 700, 1400, 440, GOLD, shadow=False, k=kin(lt, 0.0, 0.2)))
        L.finn(c, 290, 1300, 0.95, t, mood='puzzled', arm_l=200, arm_r=-70, look=(1, 0))
        E2.word(c, 'NICHT GEKLÄRT', W / 2, 650, 140, GOLD, lt, max(0.1, tg - 0.6), maxw=860)


def s10(c, t, d):
    i, lt, ld = E2.shots(9, t, d, ['und'])
    if i == 0:                                  # Schreib mir, was du siehst.
        E2.stage(c, '#5a4bff', spot=(0.5, 0.56))
        E2.push(c, lt)
        E2.glow(c, lambda cc: bubble(cc, 600, 1200, 0.95, lt))
        L.finn(c, 230, 1400, 0.7, t, mood='laugh', arm_l=200, arm_r=-60, look=(1, 0))
        E2.word(c, 'SCHREIB ES MIR!', W / 2, 650, 140, GOLD, lt, 0.1, maxw=860, snd='pop')
    else:                                       # Und wer zweifelt:  (zurück zum Startbild -> Loop)
        opening(c, lt, rise=False)


SCENES = [s1, s2, s3, s4, s5, s6, s7, s8, s9, s10]
FADE_COL = ['#000000'] * 10
