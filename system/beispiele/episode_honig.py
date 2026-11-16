"""Beispiel-Episode (Honig). Vorlage fuer neue Folgen: 10 Szenenfunktionen s1..s10(c, t, d),
SCENES, FADE_COL, HIGHLIGHT. Hilfsfunktionen: finn(), jar(), bee(), germ(), draw_banner() usw."""
import sys, os, math, json
import render as L
from render import (skia, np, W, H, P, col, OUT, clamp, ease, pop, lerp, mixc, vgrad, draw_heart, draw_text_c,
                    text_w, draw_banner, finn, bubbles, rays, rock, FONT)

HIGHLIGHT = ['Tausende', 'verdorben', 'Honig', '60', '80', 'Prozent', 'Zucker', 'Wasser', 'sauer', '3', '4,5', 'Enzym',
               'Wasserstoffperoxid', 'Offen', 'Kristallisierter', 'nicht', 'Babys', 'keinen', 'Säuglingsbotulismus',
               'Deckel', 'Geheimwaffe', 'NICHT', 'KEINEN', 'DEINEM', 'Baby', 'zeig', 'trocknen', 'BfR']

GOLD = '#ffb627'
GOLDD = '#d98a00'

# ---------- props ----------
def jar(c, x, y, s, fill=1.0, lid=True, murky=0.0, crystal=0.0, lid_off=0.0, glow=0.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    if glow:
        c.drawCircle(0, 0, 190, P('#ffd23f', int(120 * glow), blur=50))
    body = skia.Rect.MakeXYWH(-110, -120, 220, 250)
    rr = skia.RRect.MakeRectXY(body, 40, 40)
    c.drawRRect(rr, P('#e8f6ff', 120))
    c.save(); c.clipRRect(rr, skia.ClipOp.kIntersect, True)
    top = 130 - 250 * fill
    hc = mixc(GOLD, '#8a7a3a', murky)
    c.drawRect(skia.Rect.MakeXYWH(-110, top, 220, 260), P(hc))
    c.drawRect(skia.Rect.MakeXYWH(60, top, 30, 260), P('#ffffff', 60))
    if crystal > 0:
        rng = np.random.RandomState(4)
        for i in range(60):
            cx, cy = rng.uniform(-100, 100), rng.uniform(top + 10, 125)
            c.drawCircle(cx, cy, rng.uniform(3, 7), P('#fff3c4', int(220 * crystal)))
    if murky > 0:
        rng = np.random.RandomState(8)
        for i in range(14):
            c.drawCircle(rng.uniform(-90, 90), rng.uniform(top + 20, 120), rng.uniform(6, 14), P('#ffffff', int(120 * murky), stroke=3))
    c.restore()
    c.drawRRect(rr, P(OUT, stroke=8))
    # label
    lr = skia.Rect.MakeXYWH(-80, -20, 160, 80)
    c.drawRRect(skia.RRect.MakeRectXY(lr, 14, 14), P('#fff8e6')); c.drawRRect(skia.RRect.MakeRectXY(lr, 14, 14), P(OUT, stroke=5))
    draw_text_c(c, 'HONIG', 0, 34, 40, fill=GOLDD, outline='#fff8e6', ow=2)
    if lid:
        c.save(); c.translate(lid_off * 60, -lid_off * 120); c.rotate(lid_off * 25)
        lr2 = skia.Rect.MakeXYWH(-120, -165, 240, 55)
        c.drawRRect(skia.RRect.MakeRectXY(lr2, 16, 16), P('#c0392b')); c.drawRRect(skia.RRect.MakeRectXY(lr2, 16, 16), P(OUT, stroke=7))
        for k in range(5):
            c.drawLine(-90 + k * 45, -160, -90 + k * 45, -115, P('#ffffff', 90, stroke=6))
        c.restore()
    c.restore()

def clay_pot(c, x, y, s, glow=0):
    c.save(); c.translate(x, y); c.scale(s, s)
    if glow:
        c.drawCircle(0, 0, 200, P('#ffd23f', int(130 * glow), blur=50))
    p = skia.Path(); p.moveTo(-70, -150); p.lineTo(70, -150); p.cubicTo(80, -110, 170, -60, 150, 40)
    p.cubicTo(130, 140, 60, 160, 0, 160); p.cubicTo(-60, 160, -130, 140, -150, 40); p.cubicTo(-170, -60, -80, -110, -70, -150); p.close()
    c.drawPath(p, P('#c0763a')); c.drawPath(p, P(OUT, stroke=8))
    c.drawLine(-140, 0, 140, 0, P('#8a4a1c', stroke=8)); c.drawLine(-120, 60, 120, 60, P('#8a4a1c', stroke=6))
    c.drawOval(skia.Rect.MakeXYWH(-80, -170, 160, 40), P('#8a4a1c')); c.drawOval(skia.Rect.MakeXYWH(-80, -170, 160, 40), P(OUT, stroke=7))
    c.drawOval(skia.Rect.MakeXYWH(-60, -165, 120, 28), P(GOLD))
    # drip
    c.drawPath(skia.Path().addOval(skia.Rect.MakeXYWH(-20, -150, 30, 60)), P(GOLD))
    c.restore()

def bee(c, x, y, s, t, fan=1.0, ang=0):
    c.save(); c.translate(x, y); c.rotate(ang); c.scale(s, s)
    wa = math.sin(t * 40 * fan) * 25
    for sx in (-1, 1):
        c.save(); c.rotate(sx * (20 + wa))
        w = skia.Rect.MakeXYWH(-22, -80, 44, 70)
        c.drawOval(w, P('#e8f8ff', 200)); c.drawOval(w, P(OUT, stroke=5)); c.restore()
    b = skia.Rect.MakeXYWH(-55, -38, 110, 76)
    c.drawOval(b, P('#ffd23f'))
    c.save(); c.clipPath(skia.Path().addOval(b), skia.ClipOp.kIntersect, True)
    for k in (-20, 10, 40):
        c.drawRect(skia.Rect.MakeXYWH(k - 8, -40, 16, 80), P('#2b1d16'))
    c.restore()
    c.drawOval(b, P(OUT, stroke=6))
    c.drawCircle(-58, -5, 30, P('#2b1d16'))
    c.drawCircle(-66, -12, 9, P('#ffffff')); c.drawCircle(-64, -12, 4, P('#000000'))
    c.drawLine(-70, -30, -85, -60, P(OUT, stroke=4)); c.drawCircle(-85, -60, 6, P(OUT))
    c.restore()

def germ(c, x, y, s, t, dry=0.0, seed=0, color='#6bd66b'):
    c.save(); c.translate(x, y); c.scale(s * (1 - 0.45 * dry), s * (1 - 0.45 * dry))
    clr = mixc(color, '#9a9a8a', dry)
    p = skia.Path()
    for i in range(13):
        a = i / 12 * 2 * math.pi
        r = 50 + 8 * math.sin(a * 5 + t * 4 + seed) - 14 * dry * math.sin(a * 7)
        if i == 0: p.moveTo(math.cos(a) * r, math.sin(a) * r)
        else: p.lineTo(math.cos(a) * r, math.sin(a) * r)
    p.close()
    for i in range(6):
        a = i / 6 * 2 * math.pi + t
        c.drawLine(math.cos(a) * 45, math.sin(a) * 45, math.cos(a) * 70, math.sin(a) * 70, P(OUT, stroke=5))
    c.drawPath(p, P(clr)); c.drawPath(p, P(OUT, stroke=6))
    for sx in (-1, 1):
        if dry > 0.5:
            c.drawLine(sx * 18 - 8, -10, sx * 18 + 8, 2, P(OUT, stroke=5)); c.drawLine(sx * 18 - 8, 2, sx * 18 + 8, -10, P(OUT, stroke=5))
        else:
            c.drawCircle(sx * 18, -8, 9, P('#ffffff')); c.drawCircle(sx * 18, -6, 4, P('#000000'))
    mp = skia.Path()
    if dry > 0.5: mp.moveTo(-14, 22); mp.cubicTo(-5, 12, 5, 12, 14, 22)
    else: mp.moveTo(-14, 14); mp.cubicTo(-5, 24, 5, 24, 14, 14)
    c.drawPath(mp, P(OUT, stroke=5))
    c.restore()

def waterdrop(c, x, y, s, a=255):
    p = skia.Path(); p.moveTo(x, y - 30 * s); p.cubicTo(x + 22 * s, y - 2 * s, x + 20 * s, y + 20 * s, x, y + 20 * s)
    p.cubicTo(x - 20 * s, y + 20 * s, x - 22 * s, y - 2 * s, x, y - 30 * s); p.close()
    c.drawPath(p, P('#4fb3ff', a)); c.drawPath(p, P(OUT, a, stroke=4))

def flower(c, x, y, s, color, t):
    sw = math.sin(t * 1.5 + x) * 6
    c.drawLine(x, y, x + sw, y - 160 * s, P(OUT, stroke=16 * s)); c.drawLine(x, y, x + sw, y - 160 * s, P('#3aa655', stroke=10 * s))
    cx, cy = x + sw, y - 160 * s
    for i in range(6):
        a = i / 6 * 2 * math.pi + t * 0.2
        c.drawCircle(cx + math.cos(a) * 36 * s, cy + math.sin(a) * 36 * s, 26 * s, P(color))
        c.drawCircle(cx + math.cos(a) * 36 * s, cy + math.sin(a) * 36 * s, 26 * s, P(OUT, stroke=5))
    c.drawCircle(cx, cy, 24 * s, P('#ffd23f')); c.drawCircle(cx, cy, 24 * s, P(OUT, stroke=5))

def shield(c, x, y, s, a=255):
    p = skia.Path(); p.moveTo(x, y - 120 * s); p.lineTo(x + 100 * s, y - 80 * s); p.cubicTo(x + 100 * s, y + 40 * s, x + 50 * s, y + 100 * s, x, y + 130 * s)
    p.cubicTo(x - 50 * s, y + 100 * s, x - 100 * s, y + 40 * s, x - 100 * s, y - 80 * s); p.close()
    c.drawPath(p, P('#7cf7ff', int(a * 0.5), blur=20))
    c.drawPath(p, P('#38b6ff', a)); c.drawPath(p, P(OUT, a, stroke=8))
    draw_text_c(c, 'H2O2', x, y + 20 * s, 54 * s, fill='#ffffff', outline='#1b4f8a', a=a)

def check(c, x, y, s, good=True):
    c.drawCircle(x, y, 60 * s, P('#2ecc71' if good else '#e74c3c')); c.drawCircle(x, y, 60 * s, P(OUT, stroke=6))
    if good:
        p = skia.Path(); p.moveTo(x - 28 * s, y); p.lineTo(x - 6 * s, y + 24 * s); p.lineTo(x + 30 * s, y - 22 * s)
        c.drawPath(p, P('#ffffff', stroke=14 * s))
    else:
        c.drawLine(x - 24 * s, y - 24 * s, x + 24 * s, y + 24 * s, P('#ffffff', stroke=14 * s))
        c.drawLine(x + 24 * s, y - 24 * s, x - 24 * s, y + 24 * s, P('#ffffff', stroke=14 * s))

def cam(c, z, cx, cy):
    c.translate(W / 2, H / 2); c.scale(z, z); c.translate(-cx, -cy)

# ---------- scenes ----------
def tomb_bg(c, t):
    vgrad(c, '#3a2412', '#1a0f07')
    for row in range(16):
        for k in range(8):
            off = 70 if row % 2 else 0
            r = skia.Rect.MakeXYWH(k * 160 - off - 40, row * 110 + 100, 150, 100)
            c.drawRect(r, P('#6b4423', 140)); c.drawRect(r, P('#2a180a', 160, stroke=4))
    # carved generic symbols
    for i, (x, y) in enumerate([(160, 380), (900, 420), (180, 760), (920, 820)]):
        tri = skia.Path(); tri.moveTo(x, y - 40); tri.lineTo(x + 45, y + 35); tri.lineTo(x - 45, y + 35); tri.close()
        c.drawPath(tri, P('#c9a46b', 90, stroke=6))
        wv = skia.Path(); wv.moveTo(x - 45, y + 70)
        for k in range(4): wv.quadTo(x - 34 + k * 22, y + 55 + (k % 2) * 30, x - 23 + k * 22, y + 70)
        c.drawPath(wv, P('#c9a46b', 90, stroke=6))
    c.drawRect(skia.Rect.MakeXYWH(-200, 1450, W + 400, 600), P('#8a6a3a'))
    c.drawLine(-200, 1450, W + 200, 1450, P(OUT, stroke=7))

def s1(c, t, d):
    z = lerp(1.0, 1.15, ease((t - 1.0) / 3))
    c.save(); cam(c, z, 560, 980)
    tomb_bg(c, t)
    # flashlight cone
    lk = ease((t - 0.3) / 0.8)
    cone = skia.Path(); cone.moveTo(330, 1180); cone.lineTo(900, 700); cone.lineTo(900, 1300); cone.close()
    c.drawPath(cone, P('#fff3b0', int(90 * lk), blur=30))
    clay_pot(c, 700, 1180, 1.05, glow=lk * (0.7 + 0.3 * math.sin(t * 4)))
    def torch(hx, hy, a):
        c.drawLine(hx, hy, hx + 60, hy - 30, P(OUT, stroke=30)); c.drawLine(hx, hy, hx + 60, hy - 30, P('#555c66', stroke=20))
        c.drawCircle(hx + 62, hy - 31, 18, P('#fff3b0'))
    finn(c, 250, 1300, 0.9, t, mood='shock' if t > 2.0 else 'happy', arm_l=200, arm_r=-25, hand_r_obj=torch, look=(1, 0))
    c.restore()
    if t < 2.2:
        draw_banner(c, 'Wie lange hält Honig?', t, 0.3, size=66)
    else:
        draw_banner(c, 'TAUSENDE JAHRE ALT', t, 2.2, size=70)

def s2(c, t, d):
    c.save(); cam(c, 1.0, 540, 960)
    vgrad(c, '#fde6c4', '#f5c38a')
    c.drawRect(skia.Rect.MakeXYWH(-200, 1150, W + 400, 900), P('#b07a4a')); c.drawLine(-200, 1150, W + 200, 1150, P(OUT, stroke=8))
    for x in range(0, W, 140):
        c.drawLine(x, 0, x, 1150, P('#ffffff', 40, stroke=6))
    # bread
    k1 = pop(t, 0.2)
    if k1 > 0:
        c.save(); c.translate(220, 1060); c.scale(k1, k1)
        br = skia.Rect.MakeXYWH(-120, -80, 240, 150)
        c.drawRRect(skia.RRect.MakeRectXY(br, 60, 60), P('#d9a35b')); c.drawRRect(skia.RRect.MakeRectXY(br, 60, 60), P(OUT, stroke=7))
        mold = ease((t - 0.8) / 1.0)
        rng = np.random.RandomState(2)
        for i in range(9):
            c.drawCircle(rng.uniform(-90, 90), rng.uniform(-60, 40), rng.uniform(10, 22) * mold, P('#5aa84f', 220))
        c.restore()
        if t > 1.2: check(c, 220, 880, 0.8, good=False)
    k2 = pop(t, 0.9)
    if k2 > 0:
        c.save(); c.translate(540, 1030); c.scale(k2, k2)
        mr = skia.Rect.MakeXYWH(-70, -150, 140, 230)
        c.drawRect(mr, P('#ffffff')); c.drawRect(mr, P(OUT, stroke=7))
        tp = skia.Path(); tp.moveTo(-70, -150); tp.lineTo(0, -210); tp.lineTo(70, -150); tp.close()
        c.drawPath(tp, P('#d6eaff')); c.drawPath(tp, P(OUT, stroke=7))
        draw_text_c(c, 'MILCH', 0, -40, 34, fill='#2f6fd6', outline='#ffffff', ow=2)
        sour = ease((t - 1.5) / 0.6)
        for i in range(3):
            c.drawLine(-40 + i * 40, -240 - i * 10, -30 + i * 40, -280 - i * 10, P('#5aa84f', int(255 * sour), stroke=8))
        c.restore()
        if t > 2.0: check(c, 540, 760, 0.8, good=False)
    k3 = pop(t, 2.6)
    if k3 > 0:
        jar(c, 850, 1000, 0.75 * k3, glow=0.6 + 0.4 * math.sin(t * 3))
    finn(c, 540, 1500, 0.75, t, mood='puzzled', arm_l=200, arm_r=-110 + math.sin(t * 9) * 12, look=(1 if t > 2.6 else -1, -1))
    c.restore()
    draw_banner(c, 'Warum hält Honig so lange?', t, 3.0, size=56)

def s3(c, t, d):
    c.save(); cam(c, 1.05, 540, 960)
    vgrad(c, '#8fd8ff', '#d7f7c8')
    c.drawCircle(880, 260, 90, P('#ffe066')); c.drawCircle(880, 260, 120, P('#ffe066', 80, blur=30))
    c.drawRect(skia.Rect.MakeXYWH(-200, 1350, W + 400, 700), P('#6cc96c')); c.drawLine(-200, 1350, W + 200, 1350, P(OUT, stroke=7))
    for x, clr in [(120, '#ff7eb6'), (330, '#ffffff'), (760, '#ffb347'), (980, '#c08bff')]:
        flower(c, x, 1400, 1.1, clr, t)
    # nectar drop with gauge
    dk = pop(t, 0.4)
    if dk > 0:
        c.save(); c.translate(540, 820); c.scale(dk, dk)
        p = skia.Path(); p.moveTo(0, -170); p.cubicTo(110, -20, 120, 80, 0, 110); p.cubicTo(-120, 80, -110, -20, 0, -170); p.close()
        c.drawPath(p, P('#bfe6ff')); c.save(); c.clipPath(p, skia.ClipOp.kIntersect, True)
        evap = ease((t - 0.55 * d) / 2.5)
        level = lerp(0.7, 0.2, evap)
        c.drawRect(skia.Rect.MakeXYWH(-130, 110 - 280 * (1 - level), 260, 300), P(mixc('#ffe08a', GOLD, evap)))
        c.drawRect(skia.Rect.MakeXYWH(-130, -180, 260, 290 - 280 * (1 - level) + 0), P('#4fb3ff', int(200 * (1 - evap))))
        c.restore(); c.drawPath(p, P(OUT, stroke=8))
        c.restore()
        draw_text_c(c, '60–80 % Wasser', 540, 1030, 52, fill='#ffffff', outline='#1b4f8a', a=int(255 * (1 - ease((t - 0.8 * d) / 1)) ))
    # bees fanning + evaporating drops
    for i, (bx, by) in enumerate([(300, 640), (780, 640)]):
        bk = pop(t, 0.55 * d - 0.6 + i * 0.3)
        if bk > 0:
            bee(c, bx + math.sin(t * 3 + i) * 10, by + math.sin(t * 4 + i) * 8, 0.9 * bk, t, fan=1.5, ang=0 if i else 0)
    if t > 0.55 * d:
        for k in range(8):
            ph = ((t - 0.55 * d) * 0.8 + k / 8) % 1
            waterdrop(c, 440 + (k % 4) * 70, 700 - ph * 500, 0.8, int(255 * (1 - ph)))
    finn(c, 170, 1500, 0.7, t, mood='happy', arm_l=200, arm_r=-70, look=(1, -1))
    c.restore()
    draw_banner(c, 'Nektar: 60–80 % Wasser', t, 0.5, size=58)

def honey_bg(c, t):
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeRadial(skia.Point(540, 900), 1200, [col('#ffd56b'), col('#e08a00')]))
    c.drawRect(skia.Rect.MakeXYWH(-500, -500, W + 1000, H + 1000), p)
    for i in range(18):
        x = (i * 173) % W; y = (i * 311 + t * 20) % H
        c.drawCircle(x, y, 20 + (i % 4) * 10, P('#fff2c0', 60))

def s4(c, t, d):
    c.save(); cam(c, lerp(1.1, 1.0, ease(t / d)), 540, 960)
    honey_bg(c, t)
    draw_text_c(c, 'ZUCKER', 540, 560, 120, fill='#fff6d6', outline='#c27000', ow=12, a=int(255 * ease(t / 0.8)))
    dry = ease((t - 0.5 * d) / 2.0)
    for i, (gx, gy) in enumerate([(300, 900), (560, 1000), (800, 880)]):
        ent = ease((t - 0.8 - i * 0.3) / 1.0)
        x = lerp(gx + (1 if i == 2 else -1) * 500, gx, ent)
        germ(c, x, gy + math.sin(t * 3 + i) * 10, 1.1, t, dry=dry, seed=i)
        if dry > 0:
            for k in range(3):
                ph = (t * 1.2 + k / 3 + i * 0.2) % 1
                waterdrop(c, x + (k - 1) * 30, gy - 80 - ph * 250, 0.6, int(255 * (1 - ph) * min(1, dry * 2)))
    c.restore()
    finn(c, 170, 1330, 0.75, t, mood='shock' if dry > 0.3 else 'happy', arm_l=200, arm_r=-60, look=(1, -1))
    draw_banner(c, 'Zucker zieht Wasser an', t, 0.4, size=58)

def s5(c, t, d):
    vgrad(c, '#e9f3ff', '#b8d4f0')
    draw_text_c(c, 'pH-Wert', W / 2, 520, 80, fill='#1b2a4a', outline='#ffffff', ow=8)
    x0, x1, y = 120, 960, 760
    cols = ['#e74c3c', '#e67e22', '#f1c40f', '#f7dc6f', '#a9dc76', '#2ecc71', '#1abc9c', '#3498db', '#2e86c1', '#5b4bd1', '#8e44ad', '#6c3483', '#4a235a', '#2c1340']
    wseg = (x1 - x0) / 14
    rk = ease(t / 0.8)
    for i, cl in enumerate(cols):
        if i / 14 <= rk:
            c.drawRect(skia.Rect.MakeXYWH(x0 + i * wseg, y - 45, wseg + 1, 90), P(cl))
    c.drawRect(skia.Rect.MakeXYWH(x0, y - 45, x1 - x0, 90), P(OUT, stroke=6))
    for v in (0, 7, 14):
        draw_text_c(c, str(v), x0 + v * wseg, y + 100, 40, fill='#1b2a4a', outline='#ffffff', ow=4)
    draw_text_c(c, 'sauer', x0 + 60, y - 80, 36, fill='#e74c3c', outline='#ffffff', ow=4)
    draw_text_c(c, 'neutral', x0 + 7 * wseg, y - 80, 36, fill='#2e8b57', outline='#ffffff', ow=4)
    zk = ease((t - 0.45 * d) / 1.0)
    if zk > 0:
        zr = skia.Rect.MakeXYWH(x0 + 3 * wseg, y - 70, 1.5 * wseg, 140)
        c.drawRRect(skia.RRect.MakeRectXY(zr, 16, 16), P('#ffffff', int(255 * zk), stroke=10))
        jar(c, x0 + 3.75 * wseg, y + 320, 0.7 * zk)
        draw_text_c(c, '3 – 4,5', x0 + 3.75 * wseg, y - 140, 56, fill='#1b2a4a', outline='#ffd23f', ow=8, a=int(255 * zk))
    # germ fleeing
    gk = ease((t - 0.62 * d) / 1.6)
    if gk > 0:
        germ(c, lerp(560, 1250, gk), 1150 - math.sin(gk * 6) * 30, 1.0, t, color='#6bd66b')
    finn(c, 780, 1330, 0.75, t, mood='laugh' if gk > 0.2 else 'happy', arm_l=200, arm_r=-80, look=(1, 0))

def s6(c, t, d):
    c.save(); cam(c, 1.0, 540, 960)
    vgrad(c, '#2a1a5e', '#5b2a86')
    rng = np.random.RandomState(3)
    for i in range(40):
        c.drawCircle(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(2, 5), P('#ffd23f', int(120 + 100 * math.sin(t * 3 + i))))
    bk = pop(t, 0.2)
    if bk > 0:
        bee(c, 540, 640 + math.sin(t * 3) * 15, 1.6 * bk, t)
        c.drawCircle(540, 640, 170, P('#ffd23f', int(60 * bk), blur=40))
    # enzyme sparkles to shield
    sk = ease((t - 0.35 * d) / 1.2)
    if sk > 0:
        for k in range(10):
            a = k / 10 * 6.28 + t
            r = lerp(60, 0, sk)
            c.drawCircle(540 + math.cos(a) * (120 - 60 * sk), lerp(700, 1000, sk) + math.sin(a) * 40, 10, P('#ffe98a', 220))
        shield(c, 540, 1050, 1.0 * ease((t - 0.45 * d) / 0.6), a=int(255 * ease((t - 0.45 * d) / 0.6)))
        # germs bouncing
        for i, sx in enumerate((-1, 1)):
            ph = ((t - 0.5 * d) * 0.9 + i * 0.5) % 1
            if t > 0.5 * d:
                gx = 540 + sx * lerp(520, 150, math.sin(ph * math.pi))
                germ(c, gx, 1050 + (i - 0.5) * 120, 0.7, t, seed=i + 3)
    finn(c, 170, 1360, 0.7, t, mood='shock' if t < 0.45 * d else 'laugh', arm_l=200, arm_r=-110, look=(1, -1))
    c.restore()
    draw_banner(c, 'Enzym bildet Wasserstoffperoxid', t, 0.5, size=50)

def s7(c, t, d):
    c.save(); cam(c, 1.0, 540, 960)
    vgrad(c, '#fde6c4', '#f5c38a')
    c.drawRect(skia.Rect.MakeXYWH(-200, 1150, W + 400, 900), P('#b07a4a')); c.drawLine(-200, 1150, W + 200, 1150, P(OUT, stroke=8))
    half = 0.55 * d
    if t < half:
        k = t / half
        mk = ease((k - 0.35) / 0.6)
        jar(c, 540, 980, 1.0, lid=True, lid_off=ease(k / 0.25), murky=mk)
        for i in range(5):
            ph = (t * 1.3 + i / 5) % 1
            if k > 0.2:
                waterdrop(c, 480 + i * 30, 620 + ph * 260, 0.9, int(255 * (1 - ph)))
        if k > 0.7: check(c, 820, 700, 0.9, good=False)
        finn(c, 200, 1340, 0.75, t, mood='shock' if k > 0.4 else 'puzzled', arm_l=200, arm_r=-40, look=(1, -1))
    else:
        k = (t - half) / (d - half)
        jar(c, 540, 980, 1.0, lid=True, crystal=ease(k / 0.5))
        if k > 0.4: check(c, 820, 700, 0.9, good=True)
        finn(c, 200, 1340, 0.75, t, mood='happy', arm_l=200, arm_r=-110, look=(1, -1))
    c.restore()
    if t < half:
        draw_banner(c, 'Offen + Wasser = Gefahr', t, 0.8, size=58, color='#e74c3c')
    else:
        draw_banner(c, 'Kristallisiert heißt nicht verdorben', t, half + 0.3, size=48, color='#2ecc71')

def s8(c, t, d):
    vgrad(c, '#dfeefa', '#a9cbe8')
    k = pop(t, 0.4, 0.5)
    if k > 0:
        c.save(); c.translate(540, 860); c.scale(k, k)
        c.drawCircle(0, 0, 250, P('#ffffff'));
        jar(c, 0, 20, 0.85)
        c.drawCircle(0, 0, 250, P('#e74c3c', stroke=40))
        c.drawLine(-177, -177, 177, 177, P('#e74c3c', stroke=40))
        c.restore()
    tk = ease((t - 1.6) / 0.6)
    if tk > 0:
        r = skia.Rect.MakeXYWH(240, 1170, 600, 120)
        c.drawRRect(skia.RRect.MakeRectXY(r, 30, 30), P('#1b2a4a', int(240 * tk)))
        draw_text_c(c, 'unter 1 Jahr', 540, 1252, 70, fill='#ffd23f', outline='#1b2a4a', a=int(255 * tk))
    finn(c, 160, 1360, 0.7, t, mood='happy', arm_l=200, arm_r=-20, look=(1, -1), bounce=False)
    if t < 0.7 * d:
        draw_banner(c, 'Kein Honig für Babys', t, 0.3, size=64, color='#e74c3c')
    else:
        draw_banner(c, 'Schick das allen mit Baby', t, 0.7 * d, size=60, color='#2ecc71')
    sk = ease((t - 0.55 * d) / 0.6)
    if sk > 0:
        draw_text_c(c, 'Quelle: Bundesinstitut für Risikobewertung', W / 2, 440, 32, fill='#1b2a4a', outline='#ffffff', ow=4, a=int(255 * sk))

def s9(c, t, d):
    vgrad(c, '#ffd56b', '#e08a00')
    items = ['wenig Wasser', 'viel Säure', 'H2O2', 'fester Deckel']
    for i, lab in enumerate(items):
        k = pop(t, 0.2 + i * (VOICE_9 / 4.6))
        if k <= 0: continue
        x = 300 if i % 2 == 0 else 780
        y = 640 if i < 2 else 1060
        c.save(); c.translate(x, y); c.scale(k, k)
        c.drawCircle(0, 0, 150, P('#ffffff')); c.drawCircle(0, 0, 150, P(OUT, stroke=8))
        if i == 0:
            waterdrop(c, 0, -20, 2.2); c.drawLine(-80, -80, 80, 60, P('#e74c3c', stroke=16))
        elif i == 1:
            c.drawOval(skia.Rect.MakeXYWH(-80, -70, 160, 120), P('#f7e94a')); c.drawOval(skia.Rect.MakeXYWH(-80, -70, 160, 120), P(OUT, stroke=7))
            c.drawLine(-50, -10, 50, -10, P('#d8c62a', stroke=6))
        elif i == 2:
            shield(c, 0, -10, 0.7)
        else:
            jar(c, 0, 10, 0.45)
        draw_text_c(c, lab, 0, 210, 44, fill='#ffffff', outline='#3a1f0f', ow=8)
        c.restore()

VOICE_9 = L.VOICE[8]

def s10(c, t, d):
    vgrad(c, '#fff1c9', '#ffc35c')
    for i in range(6):
        bee(c, (i * 197 + t * 120) % (W + 200) - 100, 300 + (i % 3) * 140 + math.sin(t * 3 + i) * 20, 0.5, t)
    jar(c, 760, 1120, 0.9, glow=0.5)
    def spoon(hx, hy, a):
        c.drawLine(hx, hy, hx + 40, hy - 90, P(OUT, stroke=20)); c.drawLine(hx, hy, hx + 40, hy - 90, P('#c0c6cf', stroke=12))
        c.drawOval(skia.Rect.MakeXYWH(hx + 15, hy - 140, 55, 60), P(GOLD)); c.drawOval(skia.Rect.MakeXYWH(hx + 15, hy - 140, 55, 60), P(OUT, stroke=5))
    finn(c, 330, 1300, 0.9, t, mood='laugh', arm_l=200 + math.sin(t * 8) * 20, arm_r=-70, hand_r_obj=spoon, look=(0, 0))
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
        draw_banner(c, 'Wie alt ist dein Honig?', t, 0.2, size=60)

SCENES = [s1, s2, s3, s4, s5, s6, s7, s8, s9, s10]
FADE_COL = ['#000000', '#ffffff', '#ffffff', '#ffd56b', '#ffffff', '#ffffff', '#ffffff', '#ffffff', '#ffd56b', '#ffffff']

