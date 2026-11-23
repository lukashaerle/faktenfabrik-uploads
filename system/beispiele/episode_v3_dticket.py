"""Episode 24.11. 11:30: Deutschlandticket – bis Montag zustimmen, sonst weg (Editing V2, Viral-Stil V3)"""
import math
import render as L
import edit2 as E2
from render import skia, W, H, P, clamp, ease, ease_out, lerp, mixc, word_t
from edit2 import ICE, ICE2, HEAT, HEAT2, GOLD, INKW, DIM, kin

EDIT = 2
SHORT = True                 # Viral-Stil V3: Logo-Karte nur ~2,2 s
TOPIC = 'DEUTSCHLANDTICKET 2027'
HOOK_TEXT = 'BIS MONTAG\nZUSTIMMEN!'
HOOK_COLORS = [INKW, '#ff5a4a']
HOOK_END = 2.5
HIGHLIGHT = ['weg.', '66', '80', 'nicht', 'aktiv', 'Frist:', '30.', '31.', 'zwei', 'Silvester', 'jedem,', 'ja', 'nein?']
GREEN = '#5fe39a'
RED = '#ff5a4a'
BLUE = '#4aa8ff'


# ---------------------------------------------------------------- Motive
def phone(c, cx, cy, s, a=255):
    c.save(); c.translate(cx, cy); c.scale(s, s)
    r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-210, -400, 420, 800), 60, 60)
    c.drawRRect(r, P('#0a1226', int(235 * a / 255))); c.drawRRect(r, P(INKW, a, stroke=10))
    c.drawRoundRect(skia.Rect.MakeXYWH(-60, -380, 120, 22), 11, 11, P(INKW, int(a * 0.6)))
    c.restore()


def ticket(c, cx, cy, s, a=255, color=GOLD, gone=0.0):
    """Ticket-Karte „D-TICKET" mit QR-Muster; gone 0..1 = rot durchgestrichen + verblasst."""
    al = int(a * (1 - 0.55 * gone))
    c.save(); c.translate(cx, cy); c.scale(s, s)
    r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-170, -250, 340, 500), 36, 36)
    c.drawRRect(r, P(color, int(al * 0.25))); c.drawRRect(r, P(color, al, stroke=9))
    E2.text(c, 'D-TICKET', 0, -170, 54, color, a=al, shadow=False)
    for i in range(7):
        for j in range(7):
            if (i * 3 + j * 5 + i * j) % 3 != 0:
                c.drawRect(skia.Rect.MakeXYWH(-112 + i * 32, -110 + j * 32, 28, 28), P(INKW, int(al * 0.85)))
    E2.text(c, 'ABO AKTIV', 0, 190, 40, INKW, a=al, shadow=False)
    if gone > 0:
        k = ease_out(clamp(gone))
        c.drawLine(-200, -280, -200 + 400 * k, -280 + 560 * k, P(RED, a, stroke=28))
        c.drawLine(200, -280, 200 - 400 * k, -280 + 560 * k, P(RED, a, stroke=28))
    c.restore()


def calsheet(c, cx, cy, s, day, mon, color=RED, k=1.0):
    c.save(); c.translate(cx, cy); c.scale(s * (0.85 + 0.15 * k), s * (0.85 + 0.15 * k))
    a = int(255 * clamp(k * 1.4))
    r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-230, -240, 460, 480), 40, 40)
    c.drawRRect(r, P('#0a1226', int(a * 0.92))); c.drawRRect(r, P(INKW, a, stroke=9))
    c.drawRect(skia.Rect.MakeXYWH(-230, -240, 460, 120), P(color, a))
    E2.text(c, mon, 0, -158, 66, '#0b1020', a=a, shadow=False)
    E2.text(c, day, 0, 140, 240, INKW, a=a, shadow=False)
    for x in (-120, 120):
        c.drawCircle(x, -240, 22, P(INKW, a))
    c.restore()


def button(c, cx, cy, w, label, color=GREEN, press=0.0, k=1.0):
    sc = (0.85 + 0.15 * k) * (1 - 0.06 * press)
    c.save(); c.translate(cx, cy); c.scale(sc, sc)
    r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-w / 2, -70, w, 140), 70, 70)
    c.drawRRect(r, P(color, int(90 * k), blur=26)); c.drawRRect(r, P(color, int(255 * clamp(k * 1.4))))
    E2.text(c, label, 0, 22, 64, '#0b1020', a=int(255 * clamp(k * 1.4)), shadow=False, maxw=w - 40)
    c.restore()


def finger(c, x, y, s, a=255):
    """Zeigefinger von unten (tippt)."""
    c.save(); c.translate(x, y); c.scale(s, s)
    p = skia.Path(); p.moveTo(-40, 0); p.lineTo(-40, 160); p.cubicTo(-40, 200, -110, 230, -110, 300); p.lineTo(-110, 420)
    p.lineTo(110, 420); p.lineTo(110, 230); p.cubicTo(110, 180, 40, 170, 40, 150); p.lineTo(40, 0); p.cubicTo(40, -50, -40, -50, -40, 0)
    c.drawPath(p, P('#0a1226', a)); c.drawPath(p, P(INKW, a, stroke=9))
    c.drawRoundRect(skia.Rect.MakeXYWH(-26, -26, 52, 50), 18, 18, P(INKW, int(a * 0.5), stroke=5))
    c.restore()


def renew(c, cx, cy, r, color, t):
    """Kreispfeil „automatische Verlängerung"."""
    ang = (t * 140) % 360
    rect = skia.Rect.MakeXYWH(cx - r, cy - r, 2 * r, 2 * r)
    c.drawArc(rect, ang, 290, False, P(color, 255, stroke=26))
    a2 = math.radians(ang + 290)
    hx, hy = cx + r * math.cos(a2), cy + r * math.sin(a2)
    tx, ty = -math.sin(a2), math.cos(a2)
    p = skia.Path(); p.moveTo(hx + tx * 60, hy + ty * 60)
    p.lineTo(hx + math.cos(a2) * 46, hy + math.sin(a2) * 46); p.lineTo(hx - math.cos(a2) * 46, hy - math.sin(a2) * 46); p.close()
    c.drawPath(p, P(color))


def stopwatch(c, cx, cy, s, t, color=GOLD, prog=1.0):
    c.save(); c.translate(cx, cy); c.scale(s, s)
    c.drawCircle(0, 0, 230, P('#0a1226', 230)); c.drawCircle(0, 0, 230, P(INKW, 255, stroke=12))
    c.drawRect(skia.Rect.MakeXYWH(-40, -300, 80, 50), P(INKW))
    c.drawArc(skia.Rect.MakeXYWH(-190, -190, 380, 380), -90, 360 * clamp(prog), True, P(color, 120))
    an = math.radians(-90 + 360 * clamp(prog))
    c.drawLine(0, 0, 170 * math.cos(an), 170 * math.sin(an), P(color, 255, stroke=12))
    c.drawCircle(0, 0, 18, P(color))
    c.restore()


def person(c, x, y, s, color=INKW, a=255):
    c.drawCircle(x, y - 120 * s, 52 * s, P(color, a, stroke=8 * s))
    p = skia.Path(); p.moveTo(x - 95 * s, y + 70 * s); p.cubicTo(x - 95 * s, y - 50 * s, x + 95 * s, y - 50 * s, x + 95 * s, y + 70 * s)
    c.drawPath(p, P(color, a, stroke=8 * s))


def train(c, cx, cy, s, color=INKW):
    c.save(); c.translate(cx, cy); c.scale(s, s)
    body = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-330, -120, 660, 200), 50, 50)
    c.drawRRect(body, P('#0a1226', 230)); c.drawRRect(body, P(color, 255, stroke=9))
    for i in range(5):
        c.drawRoundRect(skia.Rect.MakeXYWH(-290 + i * 120, -80, 90, 70), 12, 12, P(GOLD, 200))
    for x in (-220, -120, 120, 220):
        c.drawCircle(x, 100, 30, P(color, 255, stroke=8))
    c.drawLine(-400, 140, 400, 140, P(DIM, 255, stroke=8))
    c.restore()


# ---------------------------------------------------------------- Szenen
def s1(c, t, d):
    i, lt, ld = E2.shots(0, t, d, ['ist'])
    if i == 0:                                  # Wenn du bis Montag nicht klickst … – Handy mit Ticket
        E2.stage(c, '#7b5cff', spot=(0.5, 0.62), strength=1.2)
        E2.push(c, lt)
        def dr(cc):
            phone(cc, 540, 1260, 0.9)
            ticket(cc, 540, 1260, 1.0)
        E2.glow(c, dr)
    else:                                       # … ist dein Deutschlandticket weg.
        E2.stage(c, RED, spot=(0.5, 0.6), strength=1.1)
        E2.push(c, lt)
        tw = E2.at(0, 'weg', default=0.8) - (t - lt)
        g = clamp((lt - tw) / 0.25)
        def dr(cc):
            phone(cc, 540, 1260, 0.9)
            ticket(cc, 540, 1260, 1.0, gone=g)
        E2.glow(c, dr)
        E2.word(c, 'WEG.', W / 2, 640, 220, RED, lt, tw)


def s2(c, t, d):
    i, lt, ld = E2.shots(1, t, d, ['statt'])
    if i == 0:                                  # Ab Januar kostet es 66,80 – Preistreppe
        E2.stage(c, '#b98a1f', spot=(0.5, 0.55), strength=1.0)
        E2.push(c, lt)
        t66 = E2.at(1, '66', default=1.0) - (t - lt)
        steps = [('49 €', '2023'), ('58 €', '2025'), ('63 €', '2026'), ('66,80 €', '2027')]
        def dr(cc):
            for k, (v, y) in enumerate(steps):
                show = kin(lt, 0.1 + k * 0.18, 0.2) if k < 3 else kin(lt, t66, 0.2)
                if show <= 0:
                    continue
                x = 200 + k * 175; h = 140 + k * 80
                col = RED if k == 3 else GOLD
                E2.bar(cc, x, 1420, 140, h, col, y, value=v, k=show, lab_size=34)
        E2.glow(c, dr)
    else:                                       # statt 63 Euro
        E2.impact(c, lt, '66,80 €', sub='STATT 63 € · AB JANUAR', color=GOLD, tint=HEAT2, size=260)


def s3(c, t, d):
    E2.stage(c, BLUE, spot=(0.5, 0.5))
    E2.push(c, t)
    tn = E2.at(2, 'nicht', default=1.8)
    ks = ease_out(clamp((t - tn) / 0.22))
    def dr(cc):
        renew(cc, 540, 1150, 260, BLUE, t if t < tn else tn)
        E2.text(cc, 'AUTO', 540, 1180, 96, INKW, shadow=False)
        if ks > 0:
            cc.drawLine(260, 870, 260 + 560 * ks, 870 + 560 * ks, P(RED, 255, stroke=30))
    E2.glow(c, dr)
    E2.word(c, 'DIESMAL NICHT!', W / 2, 650, 120, RED, t, tn, maxw=820)


def s4(c, t, d):
    i, lt, ld = E2.shots(3, t, d, ['musst'])
    if i == 0:                                  # Ticket bei der DB oder im DB Navigator
        E2.stage(c, '#7b5cff', spot=(0.5, 0.55))
        E2.push(c, lt)
        def dr(cc):
            phone(cc, 540, 1180, 0.9)
            E2.text(cc, 'DB', 540, 1120, 150, RED, shadow=False)
            E2.text(cc, 'NAVIGATOR', 540, 1230, 60, INKW, shadow=False)
        E2.glow(c, dr)
        E2.tag(c, 'ABO BEI DB / DB NAVIGATOR', W / 2, 660, lt, 0.2, size=40)
    else:                                       # musst du aktiv zustimmen – Finger tippt
        E2.stage(c, GREEN, spot=(0.5, 0.55), strength=1.0)
        E2.push(c, lt)
        ta = E2.at(3, 'aktiv', default=0.6) - (t - lt)
        pr = clamp(1 - abs(lt - ta - 0.15) / 0.15)
        def dr(cc):
            button(cc, 540, 1150, 640, 'ZUSTIMMEN', GREEN, press=pr, k=kin(lt, 0.0, 0.2))
            if lt > ta:
                E2.ring(cc, 540, 1150, 330, GREEN, lt, ta, every=0.8, n=2, width=8)
        E2.glow(c, dr)
        if lt > ta:
            L.sfx('pop', ('tap', 4))
        E2.word(c, 'AKTIV!', W / 2, 650, 180, GREEN, lt, ta)


def s5(c, t, d):
    E2.stage(c, RED, spot=(0.5, 0.55), strength=1.1)
    E2.push(c, t)
    t30 = E2.at(4, '30', default=1.2)
    E2.glow(c, lambda cc: calsheet(cc, 540, 1180, 1.05, '30', 'NOVEMBER', RED, k=kin(t, 0.05, 0.25)))
    if t > t30:
        E2.glow(c, lambda cc: E2.ring(cc, 540, 1180, 300, RED, t, t30, every=0.9, n=2, width=8))
    E2.word(c, 'MONTAG', W / 2, 650, 190, GOLD, t, E2.at(4, 'montag', default=0.6))


def s6(c, t, d):
    i, lt, ld = E2.shots(5, t, d, ['am'])
    if i == 0:                                  # Sagst du nichts …
        E2.stage(c, '#5a4bff', spot=(0.5, 0.45), strength=1.1)
        E2.push(c, lt)
        L.finn(c, 540, 860, 1.5, t, mood='puzzled', arm_l=200, arm_r=-70, look=(0, 0))
    else:                                       # … endet dein Abo am 31. Dezember
        E2.stage(c, RED, spot=(0.5, 0.55), strength=1.0)
        E2.push(c, lt)
        t31 = E2.at(5, '31', default=0.3) - (t - lt)
        def dr(cc):
            calsheet(cc, 290, 1200, 0.72, '31', 'DEZEMBER', RED, k=kin(lt, 0.0, 0.2))
            ticket(cc, 680, 1200, 0.72, gone=clamp((lt - t31 - 0.2) / 0.3))
        E2.glow(c, dr)
        E2.word(c, 'ABO ENDET', W / 2, 650, 170, RED, lt, t31)


def s7(c, t, d):
    i, lt, ld = E2.shots(6, t, d, [('im', 0)])
    if i == 0:                                  # Zustimmen dauert zwei Minuten
        E2.stage(c, GREEN, spot=(0.5, 0.55))
        E2.push(c, lt)
        tz = E2.at(6, 'zwei', default=0.9) - (t - lt)
        E2.glow(c, lambda cc: stopwatch(cc, 540, 1180, 1.05, t, GREEN, prog=clamp((lt - tz) / 1.0) * 0.33))
        E2.word(c, '2 MINUTEN', W / 2, 650, 170, GREEN, lt, tz)
    else:                                       # im DB Navigator oder im Abo-Portal
        E2.stage(c, '#7b5cff', spot=(0.5, 0.55))
        E2.push(c, lt)
        tp = E2.at(6, 'abo', default=1.4) - (t - lt)
        E2.pill(c, 'DB NAVIGATOR', W / 2 - 40, 1060, size=70, color=GOLD, k=kin(lt, 0.05, 0.2))
        E2.text(c, 'ODER', W / 2, 1230, 54, INKW, k=kin(lt, tp - 0.3, 0.2))
        E2.pill(c, 'ABO-PORTAL', W / 2 - 40, 1380, size=66, color=BLUE, k=kin(lt, tp, 0.2))
        if lt > tp:
            L.sfx('pop', ('portal',))


def s8(c, t, d):
    i, lt, ld = E2.shots(7, t, d, ['bis'])
    if i == 0:                                  # Verpasst?
        E2.stage(c, RED, spot=(0.5, 0.5), strength=0.9)
        E2.push(c, lt)
        E2.impact(c, lt, 'VERPASST?', color=RED, tint=RED, size=230)
    else:                                       # Bis Silvester noch reaktivieren
        E2.stage(c, GREEN, spot=(0.5, 0.55), strength=1.0)
        E2.push(c, lt)
        tr = E2.at(7, 'reaktiv', default=1.2) - (t - lt)
        def dr(cc):
            button(cc, 540, 1160, 760, 'ABO REAKTIVIEREN', GREEN, k=kin(lt, tr, 0.2))
        E2.glow(c, dr)
        E2.word(c, 'BIS 31.12.', W / 2, 650, 170, GOLD, lt, E2.at(7, 'silvester', default=0.3) - (t - lt))


def s9(c, t, d):
    E2.stage(c, '#4aa8ff', spot=(0.5, 0.55))
    E2.push(c, t)
    tj = E2.at(8, 'jedem', default=0.6)
    def dr(cc):
        train(cc, 540, 1380, 0.95)
        for k, x in enumerate((270, 540, 810)):
            kk = kin(t, tj + k * 0.15, 0.2)
            if kk > 0:
                person(cc, x, 1120, 0.9, GOLD if k == 1 else INKW, a=int(255 * kk))
        u = ease_out(clamp((t - tj) / 0.7))
        if u > 0:                                # Papierflieger fliegt zu den Leuten
            px, py = lerp(160, 900, u), lerp(980, 900, u) - math.sin(u * math.pi) * 120
            p = skia.Path(); p.moveTo(px + 60, py); p.lineTo(px - 50, py - 34); p.lineTo(px - 20, py); p.lineTo(px - 50, py + 34); p.close()
            cc.drawPath(p, P(GOLD))
    E2.glow(c, dr)
    E2.word(c, 'SCHICK DAS WEITER', W / 2, 650, 110, GOLD, t, tj, maxw=820, snd='pop')


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
