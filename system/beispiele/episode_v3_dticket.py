"""Episode 24.11. 11:30: Deutschlandticket – bis Montag klicken, sonst weg (Editing V2, Viral-Aufbau V3 final: Loop-Ende, kein Abspann)"""
import math
import render as L
import edit2 as E2
from render import skia, W, H, P, clamp, ease, ease_out, lerp, mixc, word_t
from edit2 import ICE, ICE2, HEAT, HEAT2, GOLD, INKW, DIM, kin

EDIT = 2
LOOP = True                  # Viral-Aufbau V3: kein Abspann, keine Abo-Karte – letzter Satz läuft in Satz 1 zurück
TOPIC = 'DEUTSCHLANDTICKET 2027'
HOOK_TEXT = 'BIS MONTAG\nKLICKEN!'
HOOK_COLORS = [INKW, '#ff5a4a']
HOOK_END = 2.75
HIGHLIGHT = ['weg.', '66', '80', 'nicht', 'zustimmen.', 'Stichtag:', '30.', 'Silvester.', 'reaktivieren.', 'schick']
GREEN = '#5fe39a'
RED = '#ff5a4a'
BLUE = '#4aa8ff'
VIO = '#7b5cff'


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


def laptop(c, cx, cy, s, a=255):
    """Browserfenster/Laptop (für das Abo-Portal)."""
    c.save(); c.translate(cx, cy); c.scale(s, s)
    scr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-330, -230, 660, 420), 26, 26)
    c.drawRRect(scr, P('#0a1226', int(235 * a / 255))); c.drawRRect(scr, P(INKW, a, stroke=10))
    c.drawLine(-330, -160, 330, -160, P(INKW, int(a * 0.6), stroke=5))
    for i, col in enumerate((RED, GOLD, GREEN)):
        c.drawCircle(-290 + i * 40, -195, 11, P(col, a))
    base = skia.Path(); base.moveTo(-400, 190); base.lineTo(400, 190); base.lineTo(350, 240); base.lineTo(-350, 240); base.close()
    c.drawPath(base, P('#0a1226', a)); c.drawPath(base, P(INKW, a, stroke=10))
    c.restore()


def opening(c, lt):
    """Startbild = Schlussbild (Loop): Handy mit Ticket, darunter der grüne Knopf mit Tipp-Wellen – bewegt sich ab Bild 0."""
    E2.stage(c, VIO, spot=(0.5, 0.62), strength=1.2)
    E2.push(c, lt)
    pr = 0.5 + 0.5 * math.sin(lt * 7.0)
    def dr(cc):
        phone(cc, 540, 1290, 0.82)
        ticket(cc, 540, 1175, 0.6)
        button(cc, 540, 1455, 270, 'ZUSTIMMEN', GREEN, press=pr * 0.6, k=1.0)
        E2.ring(cc, 540, 1455, 140, GREEN, lt + 0.9, 0.0, every=0.7, n=2, width=8)
    E2.glow(c, dr)


# ---------------------------------------------------------------- Szenen
def s1(c, t, d):
    i, lt, ld = E2.shots(0, t, d, ['sonst'])
    if i == 0:                                  # Bis Montag klicken –
        opening(c, lt)
    else:                                       # – sonst ist dein Deutschlandticket weg.
        E2.stage(c, RED, spot=(0.5, 0.6), strength=1.15)
        E2.push(c, lt)
        g = clamp((lt - 0.25) / 0.45)
        def dr(cc):
            phone(cc, 540, 1290, 0.82)
            ticket(cc, 540, 1280, 0.82, gone=g)
        E2.glow(c, dr)
        if g > 0:
            L.sfx('swipe', ('weg',))


def s2(c, t, d):
    i, lt, ld = E2.shots(1, t, d, ['etwa'])
    if i == 0:                                  # Das gilt für Abos bei der Deutschen Bahn
        E2.stage(c, BLUE, spot=(0.5, 0.6))
        E2.push(c, lt)
        u = ease_out(clamp(lt / 0.5))
        E2.glow(c, lambda cc: train(cc, lerp(760, 540, u), 1300, 1.0))
        E2.word(c, 'ABO BEI DER BAHN?', W / 2, 650, 120, GOLD, lt, E2.at(1, 'abos', default=0.6) - (t - lt), maxw=860)
    else:                                       # – etwa im DB Navigator
        E2.stage(c, VIO, spot=(0.5, 0.58))
        E2.push(c, lt)
        def dr(cc):
            phone(cc, 540, 1290, 0.82)
            E2.text(cc, 'DB', 540, 1260, 140, INKW, shadow=False)
            E2.text(cc, 'NAVIGATOR', 540, 1350, 42, GOLD, shadow=False)
        E2.glow(c, dr)
        E2.tag(c, 'Z. B. IM DB NAVIGATOR GEBUCHT', W / 2, 660, lt, 0.15, size=38)


def s3(c, t, d):
    i, lt, ld = E2.shots(2, t, d, ['66'])
    if i == 0:                                  # Ab Januar kostet das Ticket … – Preistreppe
        E2.stage(c, '#b98a1f', spot=(0.5, 0.58), strength=1.0)
        E2.push(c, lt)
        steps = [('49 €', '2023'), ('58 €', '2025'), ('63 €', '2026'), ('?', '2027')]
        def dr(cc):
            for k, (v, y) in enumerate(steps):
                show = kin(lt, 0.03 + k * 0.15, 0.18)
                if show <= 0:
                    continue
                E2.bar(cc, 200 + k * 175, 1440, 140, 150 + k * 85, RED if k == 3 else GOLD, y, value=v, k=show, lab_size=34)
        E2.glow(c, dr)
        E2.tag(c, 'PREIS PRO MONAT', W / 2, 660, lt, 0.1, size=40)
    else:                                       # 66 Euro 80 statt 63
        E2.impact(c, lt, '66,80 €', sub='STATT 63 € · AB 1. JANUAR', color=GOLD, tint=HEAT2, size=260)


def s4(c, t, d):
    i, lt, ld = E2.shots(3, t, d, ['du'])
    if i == 0:                                  # Die Bahn verlängert dein Abo nicht automatisch
        E2.stage(c, BLUE, spot=(0.5, 0.55))
        E2.push(c, lt)
        tn = E2.at(3, 'nicht', default=1.3) - (t - lt)
        ks = ease_out(clamp((lt - tn) / 0.22))
        def dr(cc):
            renew(cc, 540, 1250, 240, BLUE, lt if lt < tn else tn)
            E2.text(cc, 'AUTO', 540, 1282, 96, INKW, shadow=False)
            if ks > 0:
                cc.drawLine(280, 990, 280 + 520 * ks, 990 + 520 * ks, P(RED, 255, stroke=30))
        E2.glow(c, dr)
        E2.word(c, 'NICHT AUTOMATISCH', W / 2, 650, 104, RED, lt, tn, maxw=860)
    else:                                       # – du musst zustimmen
        E2.stage(c, GREEN, spot=(0.5, 0.55), strength=1.0)
        E2.push(c, lt)
        tz = E2.at(3, 'zustimmen', default=2.7) - (t - lt)
        pr = clamp(1 - abs(lt - tz - 0.12) / 0.14)
        def dr(cc):
            button(cc, 540, 1200, 640, 'ZUSTIMMEN', GREEN, press=pr, k=kin(lt, 0.0, 0.16))
            E2.ring(cc, 540, 1200, 330, GREEN, lt, max(0.0, tz), every=0.6, n=2, width=8)
        E2.glow(c, dr)
        if lt > tz:
            L.sfx('pop', ('tap', 4))
        E2.word(c, 'DU MUSST!', W / 2, 650, 170, GREEN, lt, 0.05)


def s5(c, t, d):                                # Stichtag: Montag, der 30. November.
    E2.stage(c, RED, spot=(0.5, 0.58), strength=1.1)
    E2.push(c, t)
    tm = E2.at(4, 'montag', default=1.0)
    t30 = E2.at(4, '30', default=1.4)
    E2.glow(c, lambda cc: calsheet(cc, 540, 1270, 1.0, '30', 'NOVEMBER', RED, k=kin(t, 0.0, 0.2)))
    if t > t30:
        E2.glow(c, lambda cc: E2.ring(cc, 540, 1270, 290, RED, t, t30, every=0.7, n=2, width=8))
    E2.word(c, 'STICHTAG', W / 2, 650, 190, RED, t, 0.05, hold=tm - 0.1)
    E2.word(c, 'MONTAG', W / 2, 650, 200, GOLD, t, tm - 0.05)


def s6(c, t, d):
    i, lt, ld = E2.shots(5, t, d, ['endet'])
    if i == 0:                                  # Sagst du nichts, …
        E2.stage(c, '#5a4bff', spot=(0.5, 0.5), strength=1.1)
        E2.push(c, lt)
        L.finn(c, 540, 1230, 1.25, t, mood='puzzled', arm_l=200, arm_r=-70, look=(0, 0))
        E2.word(c, '. . .', W / 2, 650, 200, INKW, lt, 0.1, snd='pop')
    else:                                       # … endet dein Abo an Silvester.
        E2.stage(c, RED, spot=(0.5, 0.56), strength=1.0)
        E2.push(c, lt)
        ts = E2.at(5, 'silvester', default=1.8) - (t - lt)
        def dr(cc):
            calsheet(cc, 300, 1220, 0.72, '31', 'DEZEMBER', RED, k=kin(lt, 0.0, 0.18))
            ticket(cc, 700, 1220, 0.72, gone=clamp((lt - 0.2) / 0.35))
        E2.glow(c, dr)
        E2.word(c, 'ABO ENDET', W / 2, 650, 170, RED, lt, 0.05)


def s7(c, t, d):
    i, lt, ld = E2.shots(6, t, d, ['oder'])
    if i == 0:                                  # Zustimmen geht im DB Navigator
        E2.stage(c, GREEN, spot=(0.5, 0.58))
        E2.push(c, lt)
        tk = E2.at(6, 'navigator', default=1.3) - (t - lt)
        def dr(cc):
            phone(cc, 540, 1290, 0.82)
            E2.text(cc, 'DB', 540, 1200, 124, INKW, shadow=False)
            E2.text(cc, 'NAVIGATOR', 540, 1285, 42, GOLD, shadow=False)
            button(cc, 540, 1460, 250, 'OK', GREEN, k=kin(lt, tk, 0.18))
        E2.glow(c, dr)
        E2.word(c, 'WEG 1: APP', W / 2, 650, 160, GREEN, lt, 0.1, maxw=860)
    else:                                       # oder im Abo-Portal der Bahn
        E2.stage(c, BLUE, spot=(0.5, 0.58))
        E2.push(c, lt)
        def dr(cc):
            laptop(cc, 540, 1290, 0.95)
            E2.text(cc, 'ABO-PORTAL', 540, 1300, 78, GOLD, shadow=False)
            E2.text(cc, 'bahn.de', 540, 1380, 50, INKW, shadow=False)
        E2.glow(c, dr)
        E2.word(c, 'WEG 2: PORTAL', W / 2, 650, 150, BLUE, lt, 0.1, maxw=860)


def s8(c, t, d):
    i, lt, ld = E2.shots(7, t, d, ['bis'])
    if i == 0:                                  # Frist verpasst?
        E2.impact(c, lt, 'VERPASST?', color=RED, tint=RED, size=230)
    else:                                       # Bis Silvester kannst du das Abo noch reaktivieren.
        E2.stage(c, GREEN, spot=(0.5, 0.56), strength=1.0)
        E2.push(c, lt)
        tr = E2.at(7, 'reaktiv', default=2.4) - (t - lt)
        def dr(cc):
            button(cc, 540, 1200, 760, 'ABO REAKTIVIEREN', GREEN, press=clamp(1 - abs(lt - tr - 0.12) / 0.14), k=kin(lt, 0.0, 0.18))
            if lt > tr:
                E2.ring(cc, 540, 1200, 390, GREEN, lt, tr, every=0.7, n=2, width=8)
        E2.glow(c, dr)
        E2.word(c, 'BIS 31.12.', W / 2, 650, 180, GOLD, lt, 0.1)


def s9(c, t, d):                                # Kennst du jemanden mit Deutschlandticket?
    E2.stage(c, BLUE, spot=(0.5, 0.58))
    E2.push(c, t)
    def dr(cc):
        for k, x in enumerate((270, 540, 810)):
            kk = kin(t, 0.03 + k * 0.1, 0.16)
            if kk > 0:
                person(cc, x, 1180, 1.15, GOLD if k == 1 else INKW, a=int(255 * kk))
                ticket(cc, x, 1420, 0.27, a=int(255 * kk))
    E2.glow(c, dr)
    E2.word(c, 'KENNST DU WEN?', W / 2, 650, 130, GOLD, t, 0.1, maxw=860, snd='pop')


def s10(c, t, d):
    i, lt, ld = E2.shots(9, t, d, ['und'])
    if i == 0:                                  # Dann schick ihm das –
        E2.stage(c, BLUE, spot=(0.5, 0.58))
        E2.push(c, lt)
        u = ease_out(clamp(lt / 0.7))
        def dr(cc):
            person(cc, 800, 1240, 1.1, GOLD)
            px, py = lerp(180, 640, u), lerp(1330, 1210, u) - math.sin(u * math.pi) * 150
            p = skia.Path(); p.moveTo(px + 80, py); p.lineTo(px - 66, py - 46); p.lineTo(px - 26, py); p.lineTo(px - 66, py + 46); p.close()
            cc.drawPath(p, P(GOLD))
        E2.glow(c, dr)
        L.finn(c, 230, 1390, 0.7, t, mood='laugh', arm_l=200, arm_r=-60, look=(1, 0))
        E2.word(c, 'SCHICK DAS WEITER', W / 2, 650, 110, GOLD, lt, 0.1, maxw=860, snd='pop')
    else:                                       # – und sag ihm:  (zurück zum Startbild -> Loop)
        opening(c, lt)


SCENES = [s1, s2, s3, s4, s5, s6, s7, s8, s9, s10]
FADE_COL = ['#000000'] * 10
