"""Episode 24.11. 20:00: Black Friday – Fake-Rabatte erkennen (Editing V2, Viral-Stil V3)"""
import math
import render as L
import edit2 as E2
from render import skia, W, H, P, clamp, ease, ease_out, lerp, mixc, word_t
from edit2 import ICE, ICE2, HEAT, HEAT2, GOLD, INKW, DIM, kin

EDIT = 2
SHORT = True                 # Viral-Stil V3: Logo-Karte nur ~2,2 s
TOPIC = 'BLACK FRIDAY: FAKE-RABATT?'
HOOK_TEXT = '−50 %?\nODER FAKE?'
HOOK_COLORS = ['#ff5a4a', INKW]
HOOK_END = 2.0
HIGHLIGHT = ['50', 'Wort.', 'Fake-Rabatte.', 'niedrigsten', '30', 'Gerichtshof', 'Aldi', '29,', '69,', '23', '29.', 'null.', 'UVP', 'UVP.', 'jemand.', 'ja', 'nein?']
RED = '#ff5a4a'
GREEN = '#5fe39a'
BLUE = '#4aa8ff'
YEL = '#ffe14a'


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


def banana(c, cx, cy, s):
    c.save(); c.translate(cx, cy); c.scale(s, s)
    for dx in (-60, 0, 60):
        p = skia.Path(); p.moveTo(dx - 40, -160); p.cubicTo(dx - 190, -40, dx - 120, 160, dx + 120, 180)
        p.cubicTo(dx - 40, 120, dx - 70, -40, dx + 10, -150); p.close()
        c.drawPath(p, P(YEL, 210)); c.drawPath(p, P('#0b1020', 255, stroke=6))
    c.drawRect(skia.Rect.MakeXYWH(-90, -200, 120, 50), P('#6b4a1f'))
    c.restore()


def court(c, cx, cy, s, color=INKW):
    c.save(); c.translate(cx, cy); c.scale(s, s)
    roof = skia.Path(); roof.moveTo(-300, -150); roof.lineTo(0, -300); roof.lineTo(300, -150); roof.close()
    c.drawPath(roof, P('#0a1226', 230)); c.drawPath(roof, P(color, 255, stroke=9))
    for x in (-220, -110, 0, 110, 220):
        c.drawRect(skia.Rect.MakeXYWH(x - 28, -130, 56, 260), P(color, 200))
    c.drawRect(skia.Rect.MakeXYWH(-320, 140, 640, 40), P(color, 255))
    c.restore()


def para(c, cx, cy, size, color=GOLD, k=1.0):
    E2.text(c, '§', cx, cy, size, color, k=k, shadow=False)


# ---------------------------------------------------------------- Szenen
def s1(c, t, d):
    i, lt, ld = E2.shots(0, t, d, ['schau'])
    if i == 0:                                  # Minus 50 Prozent?
        E2.stage(c, RED, spot=(0.5, 0.62), strength=1.1)
        E2.push(c, lt)
        E2.glow(c, lambda cc: pricetag(cc, 560, 1320, 1.1, '99,99 €', '49,99 €', badge='−50 %'))
    else:                                       # Schau zuerst auf dieses eine Wort – Lupe aufs Kleingedruckte
        E2.stage(c, BLUE, spot=(0.5, 0.58), strength=1.0)
        E2.push(c, lt)
        u = ease_out(clamp(lt / 0.5))
        def dr(cc):
            pricetag(cc, 560, 1320, 1.1, '99,99 €', '49,99 €', badge='−50 %', small='statt UVP')
            lens(cc, lerp(820, 500, u), lerp(1560, 1480, u), 120)
        E2.glow(c, dr)
        E2.word(c, 'EIN WORT', W / 2, 650, 170, GOLD, lt, E2.at(0, 'wort', default=1.2) - (t - lt))


def s2(c, t, d):
    E2.stage(c, '#b98a1f', spot=(0.5, 0.5))
    E2.push(c, t)
    t22 = E2.at(1, '2022', default=0.3)
    def dr(cc):
        para(cc, 540, 1380, 520, GOLD, k=kin(t, 0.05, 0.2))
    E2.glow(c, dr)
    E2.word(c, 'SEIT 2022', W / 2, 650, 170, GOLD, t, t22)


def s3(c, t, d):
    E2.stage(c, '#7b5cff', spot=(0.5, 0.55))
    E2.push(c, t)
    tn = E2.at(2, 'niedrig', default=1.0)
    pts = [0.55, 0.6, 0.58, 0.62, 0.5, 0.45, 0.48, 0.3, 0.32, 0.35, 0.52, 0.6, 0.62, 0.66, 0.7, 0.72]
    k = clamp((t - 0.1) / 1.6)
    E2.glow(c, lambda cc: chart(cc, 150, 1050, 780, 360, pts, GOLD, k=k, low_idx=7 if t > tn else None, low_lab='TIEFSTPREIS'))
    E2.word(c, '30 TAGE', W / 2, 650, 190, GOLD, t, E2.at(2, '30', default=2.0))


def s4(c, t, d):
    E2.stage(c, BLUE, spot=(0.5, 0.55))
    E2.push(c, t)
    E2.glow(c, lambda cc: court(cc, 540, 1230, 1.1))
    E2.tag(c, 'EuGH · URTEIL 26.09.2024 · C-330/23', W / 2, 660, t, E2.at(3, 'gerichtshof', default=0.6), size=36)


def s5(c, t, d):
    E2.stage(c, '#5a4bff', spot=(0.5, 0.55))
    E2.push(c, t)
    ta = E2.at(4, 'aldi', default=1.8)
    E2.pill(c, 'VERBRAUCHERZENTRALE', W / 2 - 30, 1060, size=48, color=GREEN, k=kin(t, 0.1, 0.2))
    E2.text(c, 'GEGEN', W / 2, 1230, 64, INKW, k=kin(t, ta - 0.5, 0.2))
    E2.pill(c, 'ALDI SÜD', W / 2, 1400, size=70, color=BLUE, k=kin(t, ta, 0.2))
    if t > ta:
        L.sfx('thud', ('aldi',))


def s6(c, t, d):
    E2.stage(c, '#b98a1f', spot=(0.5, 0.6), strength=1.0)
    E2.push(c, t)
    t69 = E2.at(5, '69', default=2.8); t23 = E2.at(5, '23', default=4.6)
    def dr(cc):
        banana(cc, 230, 1290, 0.85)
        pricetag(cc, 600, 1260, 0.75, '1,69 €' if t > t69 - 0.6 else '', '1,29 €',
                 badge='−23 %' if t > t23 else '', k_strike=clamp((t - t69) / 0.3))
    E2.glow(c, dr)
    E2.tag(c, 'ALDI-SÜD-PROSPEKT (FALL VOR DEM EuGH)', W / 2, 660, t, 0.3, size=32)


def s7(c, t, d):
    i, lt, ld = E2.shots(6, t, d, ['echter'])
    if i == 0:                                  # Der niedrigste Preis der letzten 30 Tage? Auch 1,29.
        E2.stage(c, '#7b5cff', spot=(0.5, 0.55))
        E2.push(c, lt)
        ta = E2.at(6, 'auch', default=2.4) - (t - lt)
        pts = [0.7, 0.72, 0.35, 0.35, 0.36, 0.7, 0.72, 0.72, 0.35]
        E2.glow(c, lambda cc: chart(cc, 150, 1060, 780, 340, pts, GOLD, k=clamp(lt / 1.5), low_idx=2 if lt > ta else None, low_lab='1,29 €'))
        E2.word(c, 'AUCH 1,29 €', W / 2, 650, 160, GREEN, lt, ta, maxw=860)
    else:                                       # Echter Rabatt: null.
        E2.impact(c, lt, '0 %', sub='ECHTER RABATT', color=RED, tint=RED, size=320)


def s8(c, t, d):
    E2.stage(c, BLUE, spot=(0.5, 0.58))
    E2.push(c, t)
    tn = E2.at(7, 'nicht', default=2.6)
    ks = ease_out(clamp((t - tn) / 0.22))
    def dr(cc):
        pricetag(cc, 560, 1230, 1.0, 'UVP 99,99 €', '49,99 €', badge='−50 %')
    E2.glow(c, dr)
    E2.tag(c, '30-TAGE-REGEL', W / 2, 660, t, 0.4, size=46)
    if ks > 0:
        c.drawLine(300, 640, 300 + 480 * ks, 640, P(RED, 255, stroke=14))
        L.sfx('swipe', ('x8',))


def s9(c, t, d):
    i, lt, ld = E2.shots(8, t, d, [('das', 0)])
    if i == 0:                                  # Die UVP zahlt oft kaum jemand.
        E2.stage(c, '#5a4bff', spot=(0.5, 0.5))
        E2.push(c, lt)
        tk = E2.at(8, 'kaum', default=1.6) - (t - lt)
        def dr(cc):
            for k, x in enumerate((300, 540, 780)):
                cc.drawCircle(x, 1130, 52, P(DIM, 255, stroke=8))
                p = skia.Path(); p.moveTo(x - 95, 1320); p.cubicTo(x - 95, 1200, x + 95, 1200, x + 95, 1320)
                cc.drawPath(p, P(DIM, 255, stroke=8))
            if lt > tk:
                E2.pill(cc, 'ZAHLT KAUM JEMAND', W / 2, 1450, size=50, color=RED, k=kin(lt, tk, 0.2))
        E2.glow(c, dr)
        E2.word(c, 'UVP = EMPFEHLUNG', W / 2, 650, 110, GOLD, lt, 0.1, maxw=860)
    else:                                       # Das ist das Wort: UVP.
        E2.impact(c, lt, 'UVP', sub='DAS IST DAS WORT', color=GOLD, tint=HEAT2, size=340)


def s10(c, t, d):
    E2.stage(c, '#5a4bff', spot=(0.5, 0.45))
    E2.push(c, t, rate=0.006)
    tl = max(0.5, L.VOICE[9] - 0.5)
    tj = E2.at(9, 'ja', default=2.0)
    E2.pill(c, 'JA', 360, 660, size=90, color=GREEN, k=kin(t, tj, 0.2))
    E2.pill(c, 'NEIN', 720, 660, size=90, color=RED, k=kin(t, tj + 0.35, 0.2))
    L.finn(c, 200, 1180, 0.6, t, mood='laugh', arm_l=200 + math.sin(t * 8) * 20, arm_r=-70, look=(1, 0))
    E2.logo(c, t, tl)


SCENES = [s1, s2, s3, s4, s5, s6, s7, s8, s9, s10]
FADE_COL = ['#000000'] * 10
