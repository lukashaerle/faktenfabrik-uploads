"""Episode: Zeigarnik-Effekt (Psychologie). Untertitel liegen bei y~1250-1420, deshalb
Hauptmotive zwischen y=430 und 1150, FINN unten (y~1640)."""
import math
import render as L
from render import (skia, W, H, P, OUT, clamp, ease, pop, lerp, mixc, vgrad, draw_text_c,
                    text_w, draw_banner, finn, brain)

HIGHLIGHT = ['Cliffhanger', 'Zeigarnik', 'Zeigarnik-Effekt', '1927', 'unterbrochen.', 'Unterbrochene',
             'Wendung.', 'NICHT.', 'Bern', 'Ovsiankina-Effekt', 'Ovsiankina.', 'Plan', 'Kommentare!', 'DIR']

FY = 1640   # FINN baseline


def rr(c, x, y, w, h, r, fill, stroke=OUT, sw=7, a=255):
    rect = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), r, r)
    c.drawRRect(rect, P(fill, a))
    if stroke:
        c.drawRRect(rect, P(stroke, a, stroke=sw))


def check(c, x, y, s, color='#2fbf71', a=255):
    p = skia.Path(); p.moveTo(x - 22 * s, y); p.lineTo(x - 6 * s, y + 18 * s); p.lineTo(x + 26 * s, y - 20 * s)
    c.drawPath(p, P(color, a, stroke=10 * s))


def cross(c, x, y, s, color='#e74c3c', a=255):
    c.drawLine(x - 20 * s, y - 20 * s, x + 20 * s, y + 20 * s, P(color, a, stroke=10 * s))
    c.drawLine(x + 20 * s, y - 20 * s, x - 20 * s, y + 20 * s, P(color, a, stroke=10 * s))


def tv(c, x, y, s, t, text='Fortsetzung folgt ...', prog=0.8):
    c.save(); c.translate(x, y); c.scale(s, s)
    c.drawLine(-80, 230, -130, 300, P(OUT, stroke=12)); c.drawLine(80, 230, 130, 300, P(OUT, stroke=12))
    rr(c, -330, -230, 660, 460, 40, '#2b2f3a', sw=9)
    rr(c, -295, -195, 590, 360, 20, '#0f1830', stroke=None)
    for i in range(18):
        c.drawCircle(-250 + (i * 97) % 520, -160 + (i * 61) % 300, 3, P('#ffffff', 60))
    draw_text_c(c, text, 0, 0, 44, fill='#ffd23f', outline='#0f1830')
    c.drawRect(skia.Rect.MakeXYWH(-250, 120, 500, 14), P('#ffffff', 60))
    c.drawRect(skia.Rect.MakeXYWH(-250, 120, 500 * prog, 14), P('#ff4d6d'))
    c.drawCircle(-250 + 500 * prog, 127, 13, P('#ffffff'))
    c.restore()


def thought(c, x, y, s, a=255):
    for i, (dx, dy, r) in enumerate([(-150, 170, 14), (-115, 125, 22)]):
        c.drawCircle(x + dx * s, y + dy * s, r * s, P('#ffffff', a)); c.drawCircle(x + dx * s, y + dy * s, r * s, P(OUT, a, stroke=5))
    for dx, dy, r in [(-60, 20, 70), (20, -10, 85), (100, 20, 70), (30, 60, 75)]:
        c.drawCircle(x + dx * s, y + dy * s, r * s, P(OUT, a, stroke=10))
    for dx, dy, r in [(-60, 20, 70), (20, -10, 85), (100, 20, 70), (30, 60, 75)]:
        c.drawCircle(x + dx * s, y + dy * s, r * s, P('#ffffff', a))


# ---------------- scenes ----------------
def s1(c, t, d):
    vgrad(c, '#2a1f4f', '#5b3fa3')
    for i in range(30):
        c.drawCircle((i * 131) % W, (i * 277) % 1100, 2 + i % 3, P('#ffffff', 70 + 40 * math.sin(t * 2 + i)))
    k = pop(t, 0.1, 0.5)
    c.save(); c.translate(W / 2, 780); c.scale(k, k)
    tv(c, 0, 0, 1.0, t, prog=0.78 + 0.02 * math.sin(t * 3))
    c.restore()
    ka = pop(t, 1.6, 0.4)
    if ka > 0:
        thought(c, 800, 470, 0.9 * ka)
        draw_text_c(c, '???', 820, 500, 70, fill='#ff4d6d')
    finn(c, 300, FY, 0.75, t, mood='shock' if t > 1.5 else 'puzzled', arm_l=210, arm_r=-30, look=(1, -1))
    if t < d * 0.55:
        draw_banner(c, 'Kennst du das?', t, 0.2, size=70)
    else:
        draw_banner(c, 'Achtung: Am Ende ist alles anders', t, d * 0.55, size=50, color='#ff4d6d')


def s2(c, t, d):
    vgrad(c, '#f7e3c3', '#e2b886')
    for x in range(0, W, 160):
        c.drawRect(skia.Rect.MakeXYWH(x, 0, 80, 1150), P('#ffffff', 35))
    c.drawRect(skia.Rect.MakeXYWH(0, 1150, W, 800), P('#8a5a3b'))
    c.drawLine(0, 1150, W, 1150, P(OUT, stroke=8))
    # notepad of the waiter
    paid = t > d * 0.8
    rr(c, 300, 470, 480, 620, 26, '#fffdf4', sw=8)
    c.drawRect(skia.Rect.MakeXYWH(300, 470, 480, 70), P('#e74c3c'))
    rr(c, 300, 470, 480, 620, 26, '#ffffff', a=0, sw=8)
    draw_text_c(c, 'Bestellungen', 540, 522, 42, fill='#ffffff', outline='#8f1d12')
    items = ['2x Kaffee', '1x Kuchen', '3x Wasser', '1x Tee']
    for i, it in enumerate(items):
        k = pop(t, 0.4 + i * 0.35, 0.3)
        fade = 1.0 if not paid else clamp(1 - (t - d * 0.8 - i * 0.12) / 0.4)
        a = int(255 * min(k, 1) * fade)
        if a > 0:
            f = skia.Font(L.FONT, 48)
            c.drawString(it, 360, 640 + i * 105, f, P('#22304d', a))
    if paid:
        kp = pop(t, d * 0.8, 0.4)
        c.save(); c.translate(560, 820); c.rotate(-14); c.scale(kp, kp)
        rr(c, -190, -60, 380, 120, 20, '#2fbf71', a=230)
        draw_text_c(c, 'BEZAHLT', 0, 22, 66, fill='#ffffff', outline='#1a7a46')
        c.restore()
    finn(c, 830, FY, 0.75, t, mood='puzzled' if not paid else 'shock', arm_l=160, arm_r=-30, look=(-1, -1))
    draw_banner(c, 'Berlin, 1920er-Jahre', t, 0.2, size=62)


def s3(c, t, d):
    vgrad(c, '#e8f1ff', '#bcd4f5')
    labels = ['Puzzle', 'Rechnen', 'Kette', 'Falten', 'Malen', 'Raten']
    stop = [False, True, False, True, True, False]
    for i, lab in enumerate(labels):
        x = 150 + (i % 3) * 270; y = 470 + (i // 3) * 330
        k = pop(t, 0.3 + i * 0.25, 0.35)
        if k <= 0:
            continue
        c.save(); c.translate(x + 110, y + 130); c.scale(k, k)
        rr(c, -110, -130, 220, 260, 26, '#ffffff', sw=7)
        draw_text_c(c, lab, 0, -60, 38, fill='#22304d', outline='#ffffff', ow=2)
        prog = 1.0 if not stop[i] else 0.45
        c.drawRect(skia.Rect.MakeXYWH(-80, 10, 160, 22), P('#dfe6f0'))
        c.drawRect(skia.Rect.MakeXYWH(-80, 10, 160 * prog * clamp((t - 0.6 - i * 0.25) / 0.8), 22), P('#2f6fd6'))
        if stop[i] and t > 2.4 + i * 0.2:
            ks = pop(t, 2.4 + i * 0.2, 0.3)
            c.save(); c.scale(ks, ks)
            rr(c, -75, 50, 150, 60, 14, '#e74c3c', sw=5)
            draw_text_c(c, 'STOPP', 0, 95, 36, fill='#ffffff', outline='#8f1d12', ow=3)
            c.restore()
        elif not stop[i] and t > 1.6 + i * 0.25:
            check(c, 0, 80, 1.3)
        c.restore()
    finn(c, 220, FY, 0.75, t, mood='happy', arm_l=200, arm_r=-60, look=(1, -1))
    draw_banner(c, 'Bluma Zeigarnik, 1927', t, 0.2, size=62)


def s4(c, t, d):
    vgrad(c, '#fff4d6', '#ffd98a')
    kb = pop(t, 0.2, 0.5)
    c.save(); c.translate(W / 2, 800); c.scale(kb * 1.0, kb * 1.0)
    brain(c, 0, 0, 1.6, glow=0.5 + 0.3 * math.sin(t * 4))
    c.restore()
    for i, (lab, ang) in enumerate([('Rechnen', -150), ('Falten', -30), ('Malen', 90)]):
        k = pop(t, 1.0 + i * 0.4, 0.4)
        if k <= 0:
            continue
        a = math.radians(ang + t * 20)
        x = W / 2 + math.cos(a) * 360; y = 800 + math.sin(a) * 260
        c.save(); c.translate(x, y); c.scale(k, k)
        rr(c, -95, -45, 190, 90, 20, '#ffffff', sw=6)
        draw_text_c(c, lab, 0, 14, 34, fill='#e74c3c', outline='#ffffff', ow=2)
        c.restore()
    finn(c, 850, FY, 0.75, t, mood='laugh', arm_l=150, arm_r=-80, look=(-1, -1))
    if t < d * 0.55:
        draw_banner(c, 'Unterbrochenes bleibt hängen?', t, 0.2, size=56)
    else:
        draw_banner(c, 'DER ZEIGARNIK-EFFEKT', t, d * 0.55, size=64)


def s5(c, t, d):
    vgrad(c, '#14101f', '#3a0f2a')
    fl = 1 if (int(t * 6) % 5 == 0 and t < 1.2) else 0
    if fl:
        c.drawRect(skia.Rect.MakeWH(W, H), P('#ffffff', 90))
    k = pop(t, 0.3, 0.5)
    c.save(); c.translate(W / 2, 780); c.scale(k, k); c.rotate(math.sin(t * 5) * 4)
    c.drawCircle(0, 0, 260, P('#ff4d6d', 90, blur=40))
    draw_text_c(c, '?!', 0, 120, 360, fill='#ffd23f', outline='#3a0f2a', ow=26)
    c.restore()
    finn(c, W / 2, FY, 0.8, t, mood='shock', arm_l=230, arm_r=-50, look=(0, -1))
    draw_banner(c, 'Aber jetzt: die Wendung', t, 0.1, size=62, color='#ff4d6d')


def s6(c, t, d):
    vgrad(c, '#eef3f8', '#c9d6e6')
    # stack of studies
    n = int(clamp(t / 2.0) * 9)
    for i in range(n):
        y = 1100 - i * 46
        rr(c, 170 + (i % 2) * 14, y, 330, 52, 8, '#ffffff', sw=5)
        c.drawLine(200 + (i % 2) * 14, y + 26, 460, y + 26, P('#9fb0c6', stroke=5))
    draw_text_c(c, 'fast 100 Jahre', 340, 640, 42, fill='#22304d', outline='#ffffff')
    draw_text_c(c, 'Studien', 340, 690, 42, fill='#22304d', outline='#ffffff')
    # verdict card
    kv = pop(t, d * 0.62, 0.45)
    if kv > 0:
        c.save(); c.translate(760, 860); c.scale(kv, kv)
        rr(c, -210, -230, 420, 400, 30, '#ffffff', sw=8)
        draw_text_c(c, 'Gedächtnis-', 0, -140, 40, fill='#22304d', outline='#ffffff')
        draw_text_c(c, 'vorteil?', 0, -90, 40, fill='#22304d', outline='#ffffff')
        cross(c, 0, 40, 2.8)
        c.restore()
    draw_text_c(c, 'Universität Bern, 2025', W / 2, 450, 40, fill='#22304d', outline='#ffffff')
    finn(c, 880, FY, 0.72, t, mood='shock' if t > d * 0.62 else 'puzzled', arm_l=180, arm_r=-40, look=(-1, -1))
    if t < d * 0.62:
        draw_banner(c, 'Große Übersichtsstudie', t, 0.2, size=60)
    else:
        draw_banner(c, 'Kein klarer Gedächtnisvorteil', t, d * 0.62, size=54, color='#ff4d6d')


def puzzle_piece(c, x, y, s, color, a=255):
    c.save(); c.translate(x, y); c.scale(s, s)
    p = skia.Path()
    p.addRect(skia.Rect.MakeXYWH(-80, -80, 160, 160))
    p.addCircle(80, 0, 32); p.addCircle(0, -80, 32)
    c.drawPath(p, P(color, a)); c.drawPath(p, P(OUT, a, stroke=7))
    c.restore()


def s7(c, t, d):
    vgrad(c, '#e9fff1', '#a8e6c1')
    cols = ['#2f6fd6', '#ffb627', '#e74c3c', '#9b59b6', '#2fbf71', '#ff8c2b']
    pos = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    for i, (px, py) in enumerate(pos):
        if pop(t, 0.1 + i * 0.08, 0.3) > 0:
            puzzle_piece(c, W / 2 + px * 200, 780 + py * 200, 1.0, cols[i % 6])
    # missing piece flies in, never quite snaps
    mx = lerp(900, W / 2 + 40, ease((t - 1.0) / 2.5)); my = lerp(470, 760, ease((t - 1.0) / 2.5))
    c.drawRect(skia.Rect.MakeXYWH(W / 2 - 80, 700, 160, 160), P('#ffffff', 120))
    puzzle_piece(c, mx, my + math.sin(t * 6) * 6, 1.0, '#ffd23f')
    finn(c, 240, FY, 0.75, t, mood='happy', arm_l=150, arm_r=-80, look=(1, -1))
    draw_banner(c, 'DER OVSIANKINA-EFFEKT', t, 0.2, size=62)


def album(c, x, y, s, t):
    c.save(); c.translate(x, y); c.scale(s, s)
    rr(c, -150, -110, 300, 220, 18, '#2f6fd6', sw=7)
    for i in range(6):
        cx = -95 + (i % 3) * 95; cy = -45 + (i // 3) * 95
        filled = i in (0, 1, 3)
        rr(c, cx - 38, cy - 38, 76, 76, 10, '#ffd23f' if filled else '#1f4fa3', sw=4)
        if not filled:
            draw_text_c(c, '?', cx, cy + 16, 46, fill='#7fa6e8', outline='#1f4fa3', ow=2)
    c.restore()


def s8(c, t, d):
    vgrad(c, '#ffe9f0', '#ffb3c8')
    k1, k2, k3 = pop(t, 0.2, 0.4), pop(t, 1.4, 0.4), pop(t, 2.6, 0.4)
    if k1 > 0:
        c.save(); c.translate(300, 620); c.scale(k1 * 0.5, k1 * 0.5); tv(c, 0, 0, 1.0, t); c.restore()
    if k2 > 0:
        c.save(); c.translate(760, 620); c.scale(k2, k2)
        rr(c, -170, -50, 340, 100, 50, '#ffffff', sw=7)
        pr = 0.6 + 0.3 * ease((t - 1.4) / 2)
        rr(c, -150, -30, 300 * pr, 60, 30, '#2fbf71', stroke=None)
        draw_text_c(c, f'{int(pr * 100)} %', 0, 16, 44, fill='#22304d', outline='#ffffff')
        c.restore()
    if k3 > 0:
        c.save(); c.translate(W / 2, 980); c.scale(k3, k3); album(c, 0, 0, 1.0, t); c.restore()
    finn(c, 860, FY, 0.72, t, mood='laugh', arm_l=200, arm_r=-60, look=(-1, -1))
    draw_banner(c, 'Darum fesselt es uns', t, 0.1, size=62)


def s9(c, t, d):
    vgrad(c, '#eaf6ff', '#b9e1ff')
    k = pop(t, 0.2, 0.45)
    c.save(); c.translate(W / 2 + 60, 790); c.rotate(-4); c.scale(k, k)
    rr(c, -280, -300, 560, 600, 24, '#fffdf4', sw=8)
    for i in range(6):
        c.drawLine(-240, -180 + i * 80, 240, -180 + i * 80, P('#bcd4f5', stroke=4))
    f = skia.Font(L.FONT, 50)
    lines = [('Was?', 'Steuererklärung'), ('Wann?', 'Samstag, 10 Uhr')]
    for i, (a_, b_) in enumerate(lines):
        kk = clamp((t - 0.8 - i * 0.9) / 0.6)
        if kk > 0:
            c.drawString(a_, -240, -200 + i * 190, f, P('#e74c3c', int(255 * kk)))
            c.drawString(b_, -240, -130 + i * 190, skia.Font(L.FONT, 46), P('#22304d', int(255 * kk)))
    if t > 3.0:
        check(c, 180, 200, 2.4 * pop(t, 3.0, 0.3))
    c.restore()
    def pen(hx, hy, a):
        c.drawLine(hx, hy, hx + 50, hy - 80, P(OUT, stroke=22)); c.drawLine(hx, hy, hx + 50, hy - 80, P('#ffb627', stroke=14))
    finn(c, 210, FY, 0.75, t, mood='happy', arm_l=200, arm_r=-60, hand_r_obj=pen, look=(1, -1))
    draw_banner(c, 'Tipp: Plan aufschreiben', t, 0.2, size=60)


def s10(c, t, d):
    vgrad(c, '#2a1f4f', '#5b3fa3')
    for i in range(24):
        c.drawCircle((i * 151) % W, (i * 233) % 1200, 3, P('#ffffff', 90))
    thought(c, 560, 820, 1.5)
    draw_text_c(c, '...', 590, 860, 110, fill='#5b3fa3', outline='#ffffff', ow=2)
    finn(c, 300, FY, 0.8, t, mood='laugh', arm_l=200 + math.sin(t * 8) * 20, arm_r=-70, look=(1, -1))
    lk = pop(t, max(0.5, L.VOICE[9] - 0.5), 0.5)
    if lk > 0:
        c.save(); c.translate(W / 2, 330); c.scale(lk, lk)
        r = skia.Rect.MakeXYWH(-430, -110, 860, 250)
        c.drawRRect(skia.RRect.MakeRectXY(r, 40, 40), P('#1b2a4a', 240)); c.drawRRect(skia.RRect.MakeRectXY(r, 40, 40), P('#ffd23f', stroke=8))
        draw_text_c(c, 'FAKTENFABRIK', 0, 0, 92, fill='#ffd23f', outline='#0d1626')
        draw_text_c(c, '@faktenfabrik.tv', 0, 62, 42, fill='#7cf7ff', outline='#0d1626')
        draw_text_c(c, 'Wissen. Staunen. Verstehen.', 0, 104, 34, fill='#ffffff', outline='#0d1626')
        c.restore()
    else:
        draw_banner(c, 'Was geht dir nicht aus dem Kopf?', t, 0.2, size=52)


SCENES = [s1, s2, s3, s4, s5, s6, s7, s8, s9, s10]
FADE_COL = ['#000000', '#ffffff', '#ffffff', '#ffffff', '#000000', '#ffffff', '#ffffff', '#ffffff', '#ffffff', '#000000']

SHAKE_SCENES = [4, 5]
