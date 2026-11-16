"""Episode: Warum Gähnen ansteckt. Hauptmotive y=430..1150, Untertitel ~1250-1420, FINN unten."""
import math
import render as L
from render import (skia, W, H, P, OUT, clamp, ease, pop, lerp, vgrad, draw_text_c,
                    draw_banner, finn, brain, dog)

HIGHLIGHT = ['ansteckend.', 'gähnst,', 'Provine', 'Hälfte', 'LESEN', 'Nottingham', '2017', 'Kortex.',
             'Reflex.', 'NOCH', 'Drang.', 'umstritten.', 'Schimpansen', 'Hunde', 'gegähnt?', 'gegähnt',
             'überlebt', 'Kommentare!']

FY = 1640


def rr(c, x, y, w, h, r, fill, stroke=OUT, sw=7, a=255):
    rect = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), r, r)
    c.drawRRect(rect, P(fill, a))
    if stroke:
        c.drawRRect(rect, P(stroke, a, stroke=sw))


def yawn_face(c, x, y, s, t, phase=0.0, color='#ffcf6b', speed=1.0):
    """Round face that yawns in a loop."""
    k = 0.5 - 0.5 * math.cos(((t * speed + phase) % 3.0) / 3.0 * 2 * math.pi)
    open_ = clamp((k - 0.2) / 0.6)
    c.save(); c.translate(x, y); c.scale(s, s)
    c.drawCircle(0, 0, 100, P(color)); c.drawCircle(0, 0, 100, P(OUT, stroke=7))
    for sx in (-1, 1):  # closed eyes when yawning
        if open_ > 0.4:
            c.drawArc(skia.Rect.MakeXYWH(sx * 38 - 18, -35, 36, 24), 200, 140, False, P(OUT, stroke=6))
        else:
            c.drawCircle(sx * 36, -25, 10, P(OUT))
    mh = 12 + 70 * open_
    c.drawOval(skia.Rect.MakeXYWH(-24 - 8 * open_, 20, 48 + 16 * open_, mh), P('#7a2b2b'))
    c.drawOval(skia.Rect.MakeXYWH(-24 - 8 * open_, 20, 48 + 16 * open_, mh), P(OUT, stroke=6))
    if open_ > 0.5:
        draw_text_c(c, 'z', 95, -80, 50, fill='#ffffff', outline=OUT, a=int(255 * (open_ - 0.5) * 2))
    c.restore()


def s1(c, t, d):
    vgrad(c, '#ffe066', '#ffb627')
    for i in range(12):  # warning stripes
        x = (i * 180 + t * 120) % (W + 360) - 180
        p = skia.Path(); p.moveTo(x, 1180); p.lineTo(x + 90, 1180); p.lineTo(x + 30, 1230); p.lineTo(x - 60, 1230); p.close()
        c.drawPath(p, P('#1b1b1b', 200))
    k = pop(t, 0.1, 0.45)
    c.save(); c.translate(W / 2, 760); c.scale(k, k); c.rotate(math.sin(t * 6) * 3)
    tri = skia.Path(); tri.moveTo(0, -300); tri.lineTo(300, 220); tri.lineTo(-300, 220); tri.close()
    c.drawPath(tri, P('#ffffff')); c.drawPath(tri, P('#e74c3c', stroke=34))
    yawn_face(c, 0, 60, 1.25, t, phase=1.2)
    c.restore()
    finn(c, 230, FY, 0.75, t, mood='tired' if (t % 3) > 1.5 else 'shock', arm_l=210, arm_r=-30, look=(1, -1))
    if t < d * 0.45:
        draw_banner(c, 'ACHTUNG: ANSTECKEND!', t, 0.1, size=66, color='#e74c3c')
    else:
        draw_banner(c, 'Wetten, du gähnst?', t, d * 0.45, size=66)


def s2(c, t, d):
    vgrad(c, '#2a1f4f', '#5b3fa3')
    rr(c, 130, 440, 820, 560, 36, '#2b2f3a', sw=9)
    rr(c, 165, 475, 750, 490, 20, '#0f1830', stroke=None)
    cols = ['#ffcf6b', '#ffb38a', '#f2c29b', '#c98b4f', '#ffd9a0', '#e8a87c']
    for i in range(6):
        if pop(t, 0.2 + i * 0.15, 0.3) > 0:
            yawn_face(c, 290 + (i % 3) * 250, 600 + (i // 3) * 230, 0.8, t, phase=i * 0.5, color=cols[i])
    pct = int(55 * ease(clamp((t - d * 0.45) / (d * 0.4))))
    if t > d * 0.45:
        kp = pop(t, d * 0.45, 0.35)
        c.save(); c.translate(W / 2, 1120); c.scale(kp, kp)
        rr(c, -230, -70, 460, 120, 30, '#ffd23f', sw=8)
        draw_text_c(c, f'{pct} %', 0, 18, 80, fill='#1b2a4a', outline='#ffd23f', ow=2)
        c.restore()
    finn(c, 900, FY, 0.72, t, mood='tired' if t > d * 0.7 else 'puzzled', arm_l=180, arm_r=-40, look=(-1, -1))
    if t < d * 0.45:
        draw_banner(c, 'Robert Provine', t, 0.1, size=66)
    else:
        draw_banner(c, 'Mehr als die Hälfte gähnt mit', t, d * 0.45, size=54)


def s3(c, t, d):
    vgrad(c, '#eaf6ff', '#b9e1ff')
    k = pop(t, 0.1, 0.45)
    c.save(); c.translate(W / 2, 790); c.scale(k, k); c.rotate(-3)
    rr(c, -330, -320, 660, 640, 24, '#fffdf4', sw=8)
    c.drawLine(0, -300, 0, 300, P('#d8d0b8', stroke=6))
    for side in (-1, 1):
        for i in range(6):
            yy = -230 + i * 85
            word = 'Gähnen' if (i + (side > 0)) % 2 == 0 else '...'
            kk = clamp((t - 0.6 - i * 0.18 - (side > 0) * 0.5) / 0.3)
            if kk > 0:
                draw_text_c(c, word, side * 165, yy + 20, 44, fill='#22304d', outline='#fffdf4', ow=2, a=int(255 * kk))
    c.restore()
    finn(c, 220, FY, 0.75, t, mood='tired' if t > d * 0.5 else 'happy', arm_l=200, arm_r=-60, look=(1, -1))
    draw_banner(c, 'Schon LESEN reicht!', t, 0.1, size=66)


def s4(c, t, d):
    vgrad(c, '#e9f3ef', '#b8dccb')
    # head silhouette
    c.drawCircle(W / 2, 760, 230, P('#ffcf9e')); c.drawCircle(W / 2, 760, 230, P(OUT, stroke=8))
    c.drawRect(skia.Rect.MakeXYWH(W / 2 - 80, 970, 160, 120), P('#ffcf9e'))
    # magnetic coil (figure of eight) above the head
    cy = 500 + math.sin(t * 3) * 6
    for sx in (-1, 1):
        c.drawCircle(W / 2 + sx * 70, cy, 70, P('#2f6fd6', stroke=22))
    c.drawLine(W / 2, cy, W / 2 + 260, cy - 140, P(OUT, stroke=16))
    # pulses
    for j in range(3):
        ph = (t * 1.2 + j / 3) % 1.0
        c.drawCircle(W / 2, cy + 60, 40 + ph * 260, P('#7cf7ff', int(200 * (1 - ph)), stroke=8))
    draw_text_c(c, 'Uni Nottingham, 2017', W / 2, 1160, 44, fill='#1b2a4a', outline='#ffffff')
    finn(c, 870, FY, 0.72, t, mood='puzzled', arm_l=180, arm_r=-40, look=(-1, -1))
    draw_banner(c, 'Aber warum?', t, 0.1, size=70)


def s5(c, t, d):
    vgrad(c, '#fff4d6', '#ffd98a')
    kb = pop(t, 0.1, 0.5)
    c.save(); c.translate(W / 2, 800); c.scale(kb, kb)
    brain(c, 0, 0, 230, glow=0.25)
    # motor cortex strip, lights up
    gl = 0.85 + 0.15 * math.sin(t * 6)
    arc = skia.Rect.MakeXYWH(-140, -205, 280, 280)
    c.drawArc(arc, 200, 140, False, P('#ff4d6d', int(255 * gl), stroke=40))
    c.drawArc(arc, 200, 140, False, P('#ffffff', int(150 * gl), stroke=12))
    c.restore()
    if t > d * 0.35:
        kk = pop(t, d * 0.35, 0.35)
        c.save(); c.translate(800, 520); c.scale(kk, kk)
        rr(c, -170, -50, 340, 100, 24, '#ffffff', sw=6)
        draw_text_c(c, 'Bewegung', 0, 16, 46, fill='#e74c3c', outline='#ffffff', ow=2)
        c.restore()
    finn(c, 220, FY, 0.75, t, mood='happy', arm_l=150, arm_r=-80, look=(1, -1))
    if t < d * 0.6:
        draw_banner(c, 'Motorischer Kortex', t, 0.1, size=66)
    else:
        draw_banner(c, 'Ein uralter Reflex', t, d * 0.6, size=66)


def s6(c, t, d):
    vgrad(c, '#2a0f1f', '#6b1f3a')
    # urge meter
    lvl = clamp(0.25 + 0.75 * ease(t / (d * 0.85)))
    rr(c, 420, 440, 240, 700, 40, '#1b1b1b', sw=8)
    h = 640 * lvl
    colr = '#2fbf71' if lvl < 0.5 else ('#ffb627' if lvl < 0.8 else '#e74c3c')
    rr(c, 450, 1110 - h, 180, h, 26, colr, stroke=None)
    draw_text_c(c, 'DRANG', 540, 420, 50, fill='#ffffff', outline='#2a0f1f')
    if lvl > 0.85:
        draw_text_c(c, '!!!', 540, 600, 120, fill='#ffd23f', outline='#2a0f1f')

    def hand(hx, hy, a):
        c.drawCircle(hx, hy, 34, P('#ff8c2b')); c.drawCircle(hx, hy, 34, P(OUT, stroke=6))
    finn(c, 830, FY, 0.78, t, mood='shock', arm_l=150, arm_r=-100, hand_r_obj=hand, look=(-1, -1))
    draw_banner(c, 'Unterdrücken? Noch schlimmer!', t, 0.1, size=54, color='#ff4d6d')


def s7(c, t, d):
    vgrad(c, '#e8f1ff', '#bcd4f5')
    cols = ['#ffcf6b', '#ffb38a', '#c98b4f', '#f2c29b', '#ffd9a0']
    lv = [0.9, 0.3, 0.6, 0.1, 0.75]
    for i in range(5):
        k = pop(t, 0.2 + i * 0.2, 0.35)
        if k <= 0:
            continue
        x = 140 + i * 200
        c.save(); c.translate(x, 700); c.scale(k, k)
        yawn_face(c, 0, 0, 0.75, t, phase=i * 0.7, color=cols[i], speed=0.5 + lv[i])
        rr(c, -30, 110, 60, 260, 18, '#ffffff', sw=5)
        rr(c, -22, 118 + 244 * (1 - lv[i]), 44, 244 * lv[i], 14, '#e74c3c', stroke=None)
        c.restore()
    if t > d * 0.5:
        kk = pop(t, d * 0.5, 0.4)
        c.save(); c.translate(W / 2, 1150); c.scale(kk, kk)
        rr(c, -300, -55, 600, 100, 24, '#ffffff', sw=6)
        draw_text_c(c, 'Mitgefühl? Umstritten.', 0, 14, 44, fill='#22304d', outline='#ffffff', ow=2)
        c.restore()
    finn(c, 880, FY, 0.72, t, mood='puzzled', arm_l=200, arm_r=-40, look=(-1, -1))
    draw_banner(c, 'Bei jedem anders', t, 0.1, size=66)


def chimp(c, x, y, s, t):
    c.save(); c.translate(x, y); c.scale(s, s)
    for sx in (-1, 1):
        c.drawCircle(sx * 95, -10, 38, P('#5a3a22')); c.drawCircle(sx * 95, -10, 38, P(OUT, stroke=6))
    c.drawCircle(0, 0, 100, P('#5a3a22')); c.drawCircle(0, 0, 100, P(OUT, stroke=7))
    c.drawOval(skia.Rect.MakeXYWH(-70, -40, 140, 130), P('#d9a77a'))
    for sx in (-1, 1):
        c.drawArc(skia.Rect.MakeXYWH(sx * 30 - 16, -30, 32, 22), 200, 140, False, P(OUT, stroke=6))
    o = 0.5 + 0.5 * math.sin(t * 2.2)
    c.drawOval(skia.Rect.MakeXYWH(-28, 20, 56, 20 + 50 * o), P('#7a2b2b')); c.drawOval(skia.Rect.MakeXYWH(-28, 20, 56, 20 + 50 * o), P(OUT, stroke=5))
    c.restore()


def s8(c, t, d):
    vgrad(c, '#e9fff1', '#a8e6c1')
    k1, k2 = pop(t, 0.2, 0.4), pop(t, 1.0, 0.4)
    if k1 > 0:
        c.save(); c.translate(320, 760); c.scale(k1 * 1.6, k1 * 1.6); chimp(c, 0, 0, 1.0, t); c.restore()
        draw_text_c(c, 'Schimpanse', 320, 1030, 46, fill='#1b4a2e', outline='#ffffff')
    if k2 > 0:
        dog(c, 770, 740, 1.5 * k2, t)
        draw_text_c(c, 'Hund', 770, 1030, 46, fill='#1b4a2e', outline='#ffffff')
    finn(c, W / 2, FY, 0.72, t, mood='laugh', arm_l=200, arm_r=-60, look=(0, -1))
    draw_banner(c, 'Tiere stecken sich auch an', t, 0.1, size=56)


def s9(c, t, d):
    vgrad(c, '#2a1f4f', '#5b3fa3')
    k = pop(t, 0.1, 0.45)
    c.save(); c.translate(W / 2, 640); c.scale(k, k)
    yawn_face(c, 0, 0, 1.4, t, phase=0.8)
    c.restore()
    for i, (lab, colr) in enumerate([('GEGÄHNT', '#ffd23f'), ('ÜBERLEBT', '#7cf7ff')]):
        kk = pop(t, 0.8 + i * 0.4, 0.35)
        if kk <= 0:
            continue
        c.save(); c.translate(300 + i * 480, 1060); c.scale(kk, kk)
        rr(c, -200, -60, 400, 120, 40, colr, sw=8)
        draw_text_c(c, lab, 0, 20, 58, fill='#1b2a4a', outline=colr, ow=2)
        c.restore()
    draw_banner(c, 'Hast du gerade gegähnt?', t, 0.1, size=62)


def s10(c, t, d):
    vgrad(c, '#ffe066', '#ffb627')
    yawn_face(c, 780, 820, 1.1, t, phase=0.3)
    finn(c, 280, FY, 0.8, t, mood='laugh', arm_l=200 + math.sin(t * 8) * 20, arm_r=-70, look=(1, -1))
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
        draw_banner(c, 'Gegähnt oder überlebt?', t, 0.1, size=62)


SCENES = [s1, s2, s3, s4, s5, s6, s7, s8, s9, s10]
FADE_COL = ['#000000', '#ffffff', '#ffffff', '#ffffff', '#ffffff', '#000000', '#ffffff', '#ffffff', '#ffffff', '#ffffff']
SHAKE_SCENES = [5]
