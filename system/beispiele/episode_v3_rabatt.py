"""Episode 24.11. 20:00: Black Friday – im Schnitt nur 8 % (Editing V2, Viral-Aufbau V3 final: Loop-Ende, kein Abspann)"""
import math
import render as L
import edit2 as E2
from render import skia, W, H, P, clamp, ease, ease_out, lerp, mixc, word_t
from edit2 import ICE, ICE2, HEAT, HEAT2, GOLD, INKW, DIM, kin

EDIT = 2
LOOP = True                  # Viral-Aufbau V3: kein Abspann, keine Abo-Karte – letzter Satz läuft in Satz 1 zurück
TOPIC = 'BLACK FRIDAY 2026'
HOOK_TEXT = 'BLACK FRIDAY:\nNUR −8 %'
HOOK_COLORS = [INKW, '#ffe14a']
HOOK_END = 2.61
HIGHLIGHT = ['8', 'Prozent.', '10.000', '50', 'Trick', 'UVP', 'kaum', 'Mondpreis', 'Preisvergleich', 'Oktober', 'nichts.', 'Schick']
RED = '#ff5a4a'
GREEN = '#5fe39a'
BLUE = '#4aa8ff'
YEL = '#ffe14a'
VIO = '#7b5cff'
MOON = '#ffe2a8'


# ---------------------------------------------------------------- Motive
def pricetag(c, cx, cy, s, old, new, badge='', k_strike=1.0, a=255, small=''):
    """Preisschild: alter Preis (durchgestrichen), neuer Preis groß, rote Rabatt-Plakette."""
    c.save(); c.translate(cx, cy); c.scale(s, s)
    p = skia.Path(); p.moveTo(-300, -200); p.lineTo(220, -200); p.lineTo(330, 0); p.lineTo(220, 200); p.lineTo(-300, 200); p.close()
    c.drawPath(p, P('#0a1226', int(a * 0.95))); c.drawPath(p, P(INKW, a, stroke=10))
    c.drawCircle(230, 0, 26, P(INKW, a, stroke=8))
    if old:
        E2.text(c, old, 10, -80, 72, DIM, a=a, shadow=False, maxw=420)
        f = skia.Font(L.FONT_B, 72); w = min(420, f.measureText(old))
        if k_strike > 0:
            c.drawLine(10 - w / 2 - 10, -106, 10 - w / 2 - 10 + (w + 20) * clamp(k_strike), -106, P(RED, a, stroke=10))
    E2.text(c, new, -60, 90, 150, YEL, a=a, shadow=False, maxw=440)
    if small:
        E2.text(c, small, -60, 160, 30, INKW, a=int(a * 0.8), shadow=False, maxw=440)
    c.restore()
    if badge:
        c.save(); c.translate(cx + 170 * s, cy - 240 * s); c.rotate(12)
        c.drawCircle(0, 0, 120 * s, P(RED, a)); c.drawCircle(0, 0, 120 * s, P(INKW, a, stroke=6))
        E2.text(c, badge, 0, 26 * s, 76 * s, INKW, a=a, shadow=False, maxw=210 * s)
        c.restore()


def lens(c, x, y, r, a=255):
    c.drawCircle(x, y, r, P(BLUE, int(a * 0.15))); c.drawCircle(x, y, r, P(INKW, a, stroke=14))
    an = math.radians(45)
    c.drawLine(x + r * math.cos(an), y + r * math.sin(an), x + (r + 170) * math.cos(an), y + (r + 170) * math.sin(an), P(INKW, a, stroke=30))


def chart(c, x0, y0, w, h, pts, color=GOLD, k=1.0, low_idx=None, low_lab=''):
    """Preisverlauf über 30 Tage (pts 0..1 Höhe)."""
    c.drawLine(x0, y0 + h, x0 + w, y0 + h, P(DIM, 255, stroke=5)); c.drawLine(x0, y0, x0, y0 + h, P(DIM, 255, stroke=5))
    n = len(pts); m = max(2, int(n * clamp(k)))
    p = skia.Path()
    for i in range(m):
        xx = x0 + w * i / (n - 1); yy = y0 + h - pts[i] * h
        (p.moveTo if i == 0 else p.lineTo)(xx, yy)
    c.drawPath(p, P(color, 255, stroke=9))
    if low_idx is not None and m > low_idx:
        xx = x0 + w * low_idx / (n - 1); yy = y0 + h - pts[low_idx] * h
        c.drawCircle(xx, yy, 22, P(GREEN)); c.drawCircle(xx, yy, 40, P(GREEN, 255, stroke=6))
        if low_lab:
            E2.text(c, low_lab, xx, yy + 100, 56, GREEN, shadow=False)


def badge(c, x, y, r, txt, color=RED, rot=12, a=255, ink=INKW):
    """Runde Rabatt-Plakette."""
    c.save(); c.translate(x, y); c.rotate(rot)
    c.drawCircle(0, 0, r, P(color, a)); c.drawCircle(0, 0, r, P(INKW, a, stroke=max(4, r * 0.05)))
    E2.text(c, txt, 0, r * 0.22, r * 0.64, ink, a=a, shadow=False, maxw=r * 1.75)
    c.restore()


def moon(c, x, y, r, color=MOON, a=255):
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeRadial(skia.Point(x, y), r * 2.2, [L.col(color, int(a * 0.3)), L.col(color, 0)]))
    c.drawCircle(x, y, r * 2.2, p)
    c.drawCircle(x, y, r, P(color, a))
    for dx, dy, rr in [(-0.3, -0.2, 0.22), (0.25, 0.1, 0.16), (-0.05, 0.35, 0.12), (0.35, -0.35, 0.1)]:
        c.drawCircle(x + dx * r, y + dy * r, rr * r, P(mixc(color, '#8a7a5a', 0.45), int(a * 0.55)))


def shop(c, x, y, s, a=255):
    """Kleiner Laden (Markise + Tür)."""
    c.save(); c.translate(x, y); c.scale(s, s)
    c.drawRect(skia.Rect.MakeXYWH(-60, -40, 120, 100), P('#0a1226', a)); c.drawRect(skia.Rect.MakeXYWH(-60, -40, 120, 100), P(INKW, a, stroke=7))
    aw = skia.Path(); aw.moveTo(-76, -40); aw.lineTo(-56, -84); aw.lineTo(56, -84); aw.lineTo(76, -40); aw.close()
    c.drawPath(aw, P(BLUE, a)); c.drawPath(aw, P(INKW, a, stroke=7))
    c.drawRect(skia.Rect.MakeXYWH(-18, 4, 36, 56), P(INKW, int(a * 0.8)))
    c.restore()


def person(c, x, y, s, color=INKW, a=255):
    c.drawCircle(x, y - 120 * s, 52 * s, P(color, a, stroke=8 * s))
    p = skia.Path(); p.moveTo(x - 95 * s, y + 70 * s); p.cubicTo(x - 95 * s, y - 50 * s, x + 95 * s, y - 50 * s, x + 95 * s, y + 70 * s)
    c.drawPath(p, P(color, a, stroke=8 * s))


def bag(c, x, y, s, color=GOLD, a=255):
    """Einkaufstüte mit Prozentzeichen."""
    c.save(); c.translate(x, y); c.scale(s, s)
    c.drawRect(skia.Rect.MakeXYWH(-70, -60, 140, 150), P(color, int(a * 0.3))); c.drawRect(skia.Rect.MakeXYWH(-70, -60, 140, 150), P(color, a, stroke=8))
    c.drawArc(skia.Rect.MakeXYWH(-36, -110, 72, 100), 180, 180, False, P(color, a, stroke=8))
    E2.text(c, '%', 0, 52, 90, color, a=a, shadow=False)
    c.restore()


def opening(c, lt):
    """Startbild = Schlussbild (Loop): Preisschild mit pulsierender −50-%-Plakette – bewegt sich ab Bild 0."""
    E2.stage(c, RED, spot=(0.5, 0.64), strength=1.15)
    E2.push(c, lt)
    pul = 1 + 0.07 * math.sin(lt * 8.0)
    def dr(cc):
        pricetag(cc, 520, 1340, 0.95, '99,99 €', '49,99 €')
        badge(cc, 700, 1100, 118 * pul, '−50 %', RED)
    E2.glow(c, dr)


# ---------------------------------------------------------------- Szenen
def s1(c, t, d):
    i, lt, ld = E2.shots(0, t, d, ['nur'])
    if i == 0:                                  # Am Black Friday sparst du im Schnitt …
        opening(c, lt)
    else:                                       # … nur 8 Prozent.
        E2.stage(c, '#b98a1f', spot=(0.5, 0.62), strength=1.15)
        E2.push(c, lt)
        k = kin(lt, 0.0, 0.16)
        def dr(cc):
            badge(cc, 290, 1080, 92, '−50 %', DIM, rot=-10, a=230)
            cc.drawLine(205, 1130, 375, 1030, P(RED, 255, stroke=14))
            badge(cc, 560, 1290, 240 * (0.8 + 0.2 * k), '−8 %', YEL, rot=6, ink='#0b1020')
            E2.ring(cc, 560, 1290, 260, YEL, lt, 0.0, every=0.7, n=2, width=8)
        E2.glow(c, dr)


def s2(c, t, d):
    i, lt, ld = E2.shots(1, t, d, ['bei'])
    if i == 0:                                  # Das hat Idealo für 2025 …
        E2.stage(c, BLUE, spot=(0.5, 0.6))
        E2.push(c, lt)
        u = ease_out(clamp(lt / 0.8))
        def dr(cc):
            pricetag(cc, 500, 1340, 0.85, '99,99 €', '49,99 €')
            lens(cc, lerp(760, 470, u), lerp(1500, 1300, u), 130)
        E2.glow(c, dr)
        E2.word(c, 'NACHGERECHNET', W / 2, 650, 124, GOLD, lt, 0.1, maxw=860)
        E2.tag(c, 'QUELLE: IDEALO-PREISSTUDIE · BLACK FRIDAY 2025', W / 2, 740, lt, 0.45, size=30)
    else:                                       # … bei 10.000 Produkten nachgerechnet.
        E2.impact(c, lt, '10.000', sub='PRODUKTE VERGLICHEN', color=GOLD, tint=BLUE, top='OKTOBER GEGEN BLACK FRIDAY', size=300)


def s3(c, t, d):
    i, lt, ld = E2.shots(2, t, d, ['minus'])
    if i == 0:                                  # Aber warum steht dann überall …
        E2.stage(c, RED, spot=(0.5, 0.6), strength=1.0)
        E2.push(c, lt)
        items = [(260, 1100, 105, '−50 %', RED, -8), (680, 1170, 118, 'SALE', YEL, 10), (330, 1390, 112, 'DEAL', BLUE, 8),
                 (700, 1420, 100, '−50 %', RED, -12), (500, 1250, 84, '%', GREEN, 0)]
        def dr(cc):
            for n, (x, y, r, tx, col, rot) in enumerate(items):
                k = kin(lt, 0.03 + n * 0.17, 0.16)
                if k > 0:
                    badge(cc, x, y, r * (0.7 + 0.3 * k), tx, col, rot=rot, a=int(255 * k), ink='#0b1020' if col in (YEL, GREEN) else INKW)
        E2.glow(c, dr)
        for n in range(len(items)):
            if lt > 0.03 + n * 0.17:
                L.sfx('pop', ('badge', n))
    else:                                       # … minus 50 Prozent?
        E2.impact(c, lt, '−50 %?', color=RED, tint=RED, size=300)


def s4(c, t, d):                                # Der Trick ist der durchgestrichene Preis.
    E2.stage(c, VIO, spot=(0.5, 0.62))
    E2.push(c, t)
    td = E2.at(3, 'durchgestr', default=0.9)
    ks = clamp((t - td) / 0.35)
    u = ease_out(clamp((t - td + 0.2) / 0.5))
    def dr(cc):
        pricetag(cc, 520, 1330, 1.0, '99,99 €', '49,99 €', k_strike=ks)
        if t > td:
            E2.ring(cc, 530, 1238, 250, YEL, t, td, every=0.8, n=2, width=8)
        lens(cc, lerp(780, 640, u), lerp(1500, 1300, u), 110)
    E2.glow(c, dr)
    E2.word(c, 'SCHAU GENAU HIN', W / 2, 650, 124, YEL, t, 0.2, maxw=860)


def s5(c, t, d):
    i, lt, ld = E2.shots(4, t, d, ['und'])
    if i == 0:                                  # Oft ist das die UVP
        E2.impact(c, lt, 'UVP', sub='UNVERBINDLICHE PREISEMPFEHLUNG', color=GOLD, tint=HEAT2, size=340)
    else:                                       # – und die verlangt kaum ein Händler wirklich.
        E2.stage(c, BLUE, spot=(0.5, 0.6))
        E2.push(c, lt)
        tk = E2.at(4, 'kaum', default=2.7) - (t - lt)
        hs = [190, 240, 170, 220, 185]
        def dr(cc):
            for k in range(11):                  # gestrichelte UVP-Linie
                cc.drawLine(120 + k * 68, 1040, 160 + k * 68, 1040, P(GOLD, 255, stroke=8))
            for n, h in enumerate(hs):
                kk = kin(lt, 0.05 + n * 0.1, 0.16)
                if kk > 0:
                    x = 190 + n * 140
                    cc.drawRoundRect(skia.Rect.MakeXYWH(x - 50, 1420 - h * kk, 100, h * kk), 12, 12, P(BLUE, int(230 * kk)))
                    shop(cc, x, 1468, 0.6, a=int(255 * kk))
        E2.glow(c, dr)
        E2.pill(c, 'UVP', 800, 1000, size=40, color=GOLD, k=kin(lt, 0.0, 0.2))
        E2.tag(c, 'ECHTE PREISE IM HANDEL', W / 2 - 20, 1112, lt, 0.5, size=34)
        E2.word(c, 'VERLANGT KAUM EINER', W / 2, 650, 104, RED, lt, max(0.1, tk - 0.1), maxw=860)


def s6(c, t, d):
    i, lt, ld = E2.shots(5, t, d, ['mondpreis'])
    if i == 0:                                  # Dein Rabatt wird dann von einem …
        E2.stage(c, RED, spot=(0.5, 0.62), strength=1.0)
        E2.push(c, lt)
        u = ease_out(clamp((lt - 0.2) / 0.5))
        def dr(cc):
            pricetag(cc, 520, 1340, 0.95, '99,99 €', '49,99 €')
            badge(cc, 700, 1100, 118, '−50 %', RED)
            if u > 0:                            # Pfeil: Plakette -> durchgestrichener Preis
                x0, y0, x1, y1 = 610, 1150, 560, 1215
                cc.drawLine(x0, y0, lerp(x0, x1, u), lerp(y0, y1, u), P(YEL, 255, stroke=12))
                if u >= 1:
                    ar = skia.Path(); ar.moveTo(x1 - 8, y1 + 30); ar.lineTo(x1 - 34, y1 - 14); ar.lineTo(x1 + 22, y1 - 4); ar.close()
                    cc.drawPath(ar, P(YEL))
        E2.glow(c, dr)
        E2.word(c, 'RABATT VON WAS?', W / 2, 650, 124, YEL, lt, 0.1, maxw=860)
    else:                                       # … Mondpreis berechnet.
        E2.stage(c, '#2a3bff', spot=(0.5, 0.6), strength=1.1)
        E2.push(c, lt)
        def dr(cc):
            moon(cc, 520, 1250, 210 * kin(lt, 0.0, 0.2))
            cc.drawLine(640, 1400, 700, 1470, P(INKW, 255, stroke=6))
        E2.glow(c, dr)
        E2.pill(c, 'UVP 99,99 €', 700, 1495, size=38, color=YEL, k=kin(lt, 0.15, 0.2))
        E2.word(c, 'MONDPREIS', W / 2, 650, 190, MOON, lt, 0.05)


def s7(c, t, d):
    i, lt, ld = E2.shots(6, t, d, ['produkt'])
    if i == 0:                                  # So prüfst du es:
        E2.impact(c, lt, 'SO PRÜFST DU ES', color=GREEN, tint=GREEN, size=180)
    else:                                       # Produkt in einen Preisvergleich eingeben.
        E2.stage(c, GREEN, spot=(0.5, 0.6), strength=0.9)
        E2.push(c, lt)
        tp = E2.at(6, 'preisvergleich', default=1.9) - (t - lt)
        full = 'PRODUKTNAME'; n = int(clamp(lt / 0.7) * len(full))
        def dr(cc):
            bar = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(120, 1110, 730, 130), 65, 65)
            cc.drawRRect(bar, P('#0a1226', 240)); cc.drawRRect(bar, P(INKW, 255, stroke=9))
            cc.drawCircle(195, 1170, 26, P(INKW, 255, stroke=8)); cc.drawLine(214, 1190, 232, 1208, P(INKW, 255, stroke=10))
            f = skia.Font(L.FONT_B, 54); txt = full[:n] + ('|' if int(lt * 4) % 2 == 0 else '')
            cc.drawString(txt, 262, 1190, f, P(INKW))
        E2.glow(c, dr)
        if 0 < n < len(full):
            L.sfx('type', ('tippen', n // 3))
        E2.pill(c, 'PREISVERGLEICH', 485, 1370, size=56, color=GOLD, k=kin(lt, tp, 0.18))
        E2.word(c, 'PREIS-CHECK', W / 2, 650, 160, GREEN, lt, 0.15, maxw=860, snd='pop')


def s8(c, t, d):
    i, lt, ld = E2.shots(7, t, d, ['sparst'])
    if i == 0:                                  # War es im Oktober schon so billig, …
        E2.stage(c, VIO, spot=(0.5, 0.6))
        E2.push(c, lt)
        pts = [0.52, 0.5, 0.53, 0.5, 0.5, 0.52, 0.5, 0.51, 0.5, 0.5, 0.52, 0.5, 0.5]
        k = clamp((lt - 0.05) / 0.9)
        def dr(cc):
            chart(cc, 150, 1050, 700, 330, pts, GOLD, k=k)
            cc.drawCircle(150 + 700 * 1 / 12, 1050 + 330 - 0.5 * 330, 22, P(GREEN))
            if k >= 1:
                cc.drawCircle(150 + 700, 1050 + 330 - 0.5 * 330, 22, P(RED)); cc.drawCircle(150 + 700, 1050 + 330 - 0.5 * 330, 40, P(RED, 255, stroke=6))
        E2.glow(c, dr)
        E2.tag(c, 'OKTOBER', 230, 1460, lt, 0.1, size=34)
        E2.tag(c, 'BLACK FRIDAY', 700, 1460, lt, 0.7, size=34)
        E2.word(c, 'GLEICHER PREIS', W / 2, 650, 136, GOLD, lt, E2.at(7, 'billig', default=1.2) - (t - lt) - 0.1, maxw=860)
    else:                                       # … sparst du nichts.
        E2.impact(c, lt, '0 €', sub='GESPART', color=RED, tint=RED, size=340)


def s9(c, t, d):                                # Schick das jemandem, der am Freitag zuschlagen will.
    E2.stage(c, BLUE, spot=(0.5, 0.6))
    E2.push(c, t)
    u = ease_out(clamp(t / 0.8))
    def dr(cc):
        person(cc, 720, 1230, 1.1, GOLD)
        bag(cc, 600, 1380, 0.8, YEL)
        bag(cc, 820, 1390, 0.7, RED)
        px, py = lerp(170, 560, u), lerp(1300, 1160, u) - math.sin(u * math.pi) * 140
        pl = skia.Path(); pl.moveTo(px + 80, py); pl.lineTo(px - 66, py - 46); pl.lineTo(px - 26, py); pl.lineTo(px - 66, py + 46); pl.close()
        cc.drawPath(pl, P(GOLD))
    E2.glow(c, dr)
    L.finn(c, 230, 1400, 0.7, t, mood='laugh', arm_l=200, arm_r=-60, look=(1, 0))
    E2.word(c, 'SCHICK DAS WEITER', W / 2, 650, 110, GOLD, t, 0.1, maxw=860, snd='pop')


def s10(c, t, d):                               # Und sag ihm vorher:  (zurück zum Startbild -> Loop)
    opening(c, t)


SCENES = [s1, s2, s3, s4, s5, s6, s7, s8, s9, s10]
FADE_COL = ['#000000'] * 10
