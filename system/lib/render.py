import skia, math, sys, subprocess, os, json
import numpy as np

W, H, FPS = 1080, 1920, 30
import os as _os
FONT = skia.Typeface.MakeFromFile(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'Poppins-800.ttf'))

DUR = json.load(open('durs.json')) if os.path.exists('durs.json') else [10]*10  # scene durations in seconds

# ---------------- helpers ----------------
def col(h, a=255):
    h = h.lstrip('#')
    return skia.Color(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), int(a))

def P(c, a=255, stroke=None, cap=True, blur=None):
    p = skia.Paint(AntiAlias=True)
    p.setColor(col(c, a) if isinstance(c, str) else c)
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(stroke)
        if cap:
            p.setStrokeCap(skia.Paint.kRound_Cap)
            p.setStrokeJoin(skia.Paint.kRound_Join)
    if blur:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    return p

OUT = '#2b1d16'

def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))

def ease(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)

def pop(t, t0, d=0.35):
    """0 before t0, overshoot to 1"""
    x = (t - t0) / d
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    return (1 - (1 - x) ** 3) * (1 + 0.25 * math.sin(x * math.pi))

def lerp(a, b, x):
    return a + (b - a) * x

def mixc(c1, c2, x):
    a = [int(c1.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)]
    b = [int(c2.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)]
    return '#%02x%02x%02x' % tuple(int(lerp(a[i], b[i], clamp(x))) for i in range(3))

def vgrad(c, top, bot, y0=0, y1=H):
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeLinear([skia.Point(0, y0), skia.Point(0, y1)], [col(top), col(bot)]))
    c.drawRect(skia.Rect.MakeXYWH(-2000, -2000, W + 4000, H + 4000), p)

def heart_path(x, y, s):
    p = skia.Path()
    p.moveTo(x, y + s * 0.35)
    p.cubicTo(x - s * 1.2, y - s * 0.4, x - s * 0.5, y - s * 1.15, x, y - s * 0.45)
    p.cubicTo(x + s * 0.5, y - s * 1.15, x + s * 1.2, y - s * 0.4, x, y + s * 0.35)
    p.close()
    return p

def draw_heart(c, x, y, s, color='#ff4d6d', a=255, glow=True):
    if glow:
        c.drawPath(heart_path(x, y, s * 1.15), P(color, int(a * 0.5), blur=s * 0.35))
    c.drawPath(heart_path(x, y, s), P(color, a))
    c.drawPath(heart_path(x, y, s), P(OUT, a, stroke=max(3, s * 0.08)))
    c.drawCircle(x - s * 0.38, y - s * 0.45, s * 0.12, P('#ffffff', int(a * 0.8)))

# ---------------- text ----------------
def text_w(s, size):
    return skia.Font(FONT, size).measureText(s)

def draw_text_c(c, s, x, y, size, fill='#ffffff', outline='#111111', ow=None, a=255):
    f = skia.Font(FONT, size)
    w = f.measureText(s)
    ow = ow or size * 0.16
    c.drawString(s, x - w / 2, y, f, P(outline, a, stroke=ow))
    c.drawString(s, x - w / 2, y, f, P(fill, a))

HIGHLIGHT = ['drei', 'Herzen', 'blau', 'blau.', 'Blut.', 'Kupferhaltiges', 'Hämocyanin', '500', 'Millionen', 'zwei', 'Drittel',
             'Gehirn', 'Gehirne?', 'Oktopus.', 'Körperherz', '200', 'schlaue', 'Arme.', 'Hund.', 'Herzen.', 'Denkende']

def draw_sub(c, lines, a=255):
    size = 56
    while max(skia.Font(FONT, size).measureText(l) for l in lines) > 960:
        size -= 2
    f = skia.Font(FONT, size)
    y = 1600
    lh = size * 1.25
    wmax = max(f.measureText(l) for l in lines)
    box = skia.Rect.MakeXYWH(W / 2 - wmax / 2 - 30, y - size - 14, wmax + 60, lh * len(lines) + 22)
    c.drawRRect(skia.RRect.MakeRectXY(box, 26, 26), P('#000000', 105))
    for ln in lines:
        words = ln.split(' ')
        widths = [f.measureText(w_ + ' ') for w_ in words]
        total = sum(widths) - f.measureText(' ')
        x = W / 2 - total / 2
        for w_, wd in zip(words, widths):
            fill = '#ffd23f' if w_.strip('.,:?–') in [h.strip('.,:?') for h in HIGHLIGHT] else '#ffffff'
            c.drawString(w_, x, y, f, P('#0d0d0d', a, stroke=10))
            c.drawString(w_, x, y, f, P(fill, a))
            x += wd
        y += lh

def draw_banner(c, s, t, t0, y=300, size=66, color='#ffd23f'):
    k = pop(t, t0, 0.4)
    if k <= 0:
        return
    w = text_w(s, size) + 70
    c.save()
    c.translate(W / 2, y - size * 0.35)
    c.scale(k, k)
    r = skia.Rect.MakeXYWH(-w / 2, -size * 0.85, w, size * 1.5)
    c.drawRRect(skia.RRect.MakeRectXY(r, 30, 30), P('#000000', 70, blur=10))
    c.drawRRect(skia.RRect.MakeRectXY(r, 30, 30), P('#1b2a4a', 235))
    c.drawRRect(skia.RRect.MakeRectXY(r, 30, 30), P(color, 255, stroke=6))
    f = skia.Font(FONT, size)
    c.drawString(s, -text_w(s, size) / 2, size * 0.35, f, P('#ffffff'))
    c.restore()

# ---------------- FINN ----------------
FO = '#ff8c2b'   # orange
FOD = '#e06d12'
FB = '#2f6fd6'   # blue jacket
FBD = '#1f4fa3'
FY = '#ffc928'   # yellow bag

def finn(c, x, y, s, t, mood='happy', arm_l=200, arm_r=-20, goggles=False, blink=True, lean=0.0, sit=False,
         hand_l_obj=None, hand_r_obj=None, look=(0, 0), bounce=True):
    c.save()
    c.translate(x, y)
    c.rotate(lean)
    c.scale(s, s)
    by = math.sin(t * 4.0) * 4 if bounce else 0
    R = 120
    ow = 7
    # shadow
    c.drawOval(skia.Rect.MakeXYWH(-95, R + 40, 190, 34), P('#000000', 50, blur=6))
    # legs
    if sit:
        for sx in (-1, 1):
            c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(sx * 45 - 34, R - 30, 68, 50), 25, 25), P(FO))
            c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(sx * 45 - 34, R - 30, 68, 50), 25, 25), P(OUT, stroke=ow))
    else:
        for sx in (-1, 1):
            r = skia.Rect.MakeXYWH(sx * 50 - 30, R - 10 + by * 0.3, 60, 62)
            c.drawRRect(skia.RRect.MakeRectXY(r, 28, 28), P(FO))
            c.drawRRect(skia.RRect.MakeRectXY(r, 28, 28), P(OUT, stroke=ow))
            r2 = skia.Rect.MakeXYWH(sx * 50 - 38, R + 38 + by * 0.3, 76, 30)
            c.drawRRect(skia.RRect.MakeRectXY(r2, 15, 15), P('#ffffff'))
            c.drawRRect(skia.RRect.MakeRectXY(r2, 15, 15), P(OUT, stroke=ow))
    c.translate(0, by)

    def arm(angle_deg, side, obj):
        a = math.radians(angle_deg)
        sx, sy = side * 98, 25
        L = 95
        ex, ey = sx + math.cos(a) * L, sy + math.sin(a) * L
        c.drawLine(sx, sy, ex, ey, P(OUT, stroke=48))
        c.drawLine(sx, sy, ex, ey, P(FB, stroke=36))
        hx, hy = sx + math.cos(a) * (L + 18), sy + math.sin(a) * (L + 18)
        c.drawCircle(hx, hy, 24, P(FO))
        c.drawCircle(hx, hy, 24, P(OUT, stroke=ow))
        if obj:
            obj(hx, hy, a)

    # arms behind? draw after body for visibility
    # body
    body = skia.Path()
    body.addOval(skia.Rect.MakeXYWH(-R, -R * 1.05, 2 * R, 2.1 * R))
    c.drawPath(body, P(FO))
    c.save()
    c.clipPath(body, skia.ClipOp.kIntersect, True)
    c.drawRect(skia.Rect.MakeXYWH(-R, 5, 2 * R, R * 1.2), P(FB))
    # collar V
    v = skia.Path()
    v.moveTo(-55, 5); v.lineTo(0, 60); v.lineTo(55, 5); v.close()
    c.drawPath(v, P(FO))
    c.drawLine(-60, 5, 0, 62, P(FBD, stroke=10))
    c.drawLine(60, 5, 0, 62, P(FBD, stroke=10))
    c.drawLine(0, 62, 0, 140, P('#cfd8e6', stroke=5))
    # cheeks shading
    c.drawOval(skia.Rect.MakeXYWH(-R + 6, -R * 0.9, 50, 2 * R), P(FOD, 70, blur=12))
    # strap
    c.drawLine(80, -10, -70, 110, P('#b8860b', stroke=16))
    c.restore()
    c.drawPath(body, P(OUT, stroke=ow))
    # bag
    br = skia.Rect.MakeXYWH(-118, 70, 70, 58)
    c.drawRRect(skia.RRect.MakeRectXY(br, 14, 14), P(FY))
    c.drawRRect(skia.RRect.MakeRectXY(br, 14, 14), P(OUT, stroke=6))
    c.drawLine(-118, 92, -48, 92, P(OUT, stroke=5))
    c.drawCircle(-83, 100, 6, P('#b8860b'))

    # eyes
    blinkk = 1.0
    if blink and (t % 3.3) < 0.12:
        blinkk = 0.1
    ex_off = 46
    eye_w, eye_h = 66, 82
    if mood == 'shock':
        eye_w, eye_h = 76, 96
    for sx in (-1, 1):
        cx, cy = sx * ex_off, -45
        h = eye_h * blinkk
        if mood == 'tired':
            h = eye_h * 0.5 * blinkk
        r = skia.Rect.MakeXYWH(cx - eye_w / 2, cy - h / 2, eye_w, h)
        c.drawOval(r, P('#ffffff'))
        if h > 20:
            c.save()
            c.clipRect(r)
            ix, iy = cx + look[0] * 10, cy + look[1] * 10 + (8 if mood == 'tired' else 0)
            irs = 24 if mood != 'shock' else 20
            c.drawCircle(ix, iy, irs, P('#4a2a14'))
            c.drawCircle(ix, iy, irs * 0.55, P('#120a05'))
            c.drawCircle(ix - 8, iy - 9, 8, P('#ffffff'))
            c.drawCircle(ix + 7, iy + 7, 4, P('#ffffff'))
            c.restore()
        c.drawOval(r, P(OUT, stroke=6))
        if mood == 'tired':
            c.drawLine(cx - eye_w / 2, cy - h / 2, cx + eye_w / 2, cy - h / 2, P(OUT, stroke=8))
    # brows
    if mood == 'puzzled':
        c.drawLine(-70, -108, -25, -100, P(OUT, stroke=8))
        c.drawLine(25, -118, 70, -128, P(OUT, stroke=8))
    elif mood == 'shock':
        c.drawLine(-75, -122, -25, -128, P(OUT, stroke=8))
        c.drawLine(25, -128, 75, -122, P(OUT, stroke=8))
    # mouth
    if mood == 'shock':
        c.drawOval(skia.Rect.MakeXYWH(-17, 0, 34, 40), P('#7a1f1f'))
        c.drawOval(skia.Rect.MakeXYWH(-17, 0, 34, 40), P(OUT, stroke=6))
    elif mood == 'puzzled':
        p = skia.Path(); p.moveTo(-25, 18); p.cubicTo(-10, 8, 5, 28, 25, 14)
        c.drawPath(p, P(OUT, stroke=7))
    elif mood == 'tired':
        c.drawOval(skia.Rect.MakeXYWH(-20, 8, 40, 26), P('#7a1f1f'))
        c.drawOval(skia.Rect.MakeXYWH(-20, 8, 40, 26), P(OUT, stroke=6))
    elif mood == 'laugh':
        p = skia.Path(); p.moveTo(-34, 4); p.cubicTo(-30, 50, 30, 50, 34, 4); p.close()
        c.drawPath(p, P('#7a1f1f')); c.drawPath(p, P(OUT, stroke=6))
        c.drawOval(skia.Rect.MakeXYWH(-14, 22, 28, 14), P('#ff7b8a'))
    else:
        p = skia.Path(); p.moveTo(-30, 8); p.cubicTo(-15, 34, 15, 34, 30, 8)
        c.drawPath(p, P(OUT, stroke=7))
    # blush
    c.drawOval(skia.Rect.MakeXYWH(-98, -8, 34, 18), P('#ff5e5e', 90, blur=4))
    c.drawOval(skia.Rect.MakeXYWH(64, -8, 34, 18), P('#ff5e5e', 90, blur=4))
    if goggles:
        c.drawLine(-120, -50, 120, -50, P('#333a44', stroke=14))
        for sx in (-1, 1):
            r = skia.Rect.MakeXYWH(sx * 46 - 48, -100, 96, 104)
            c.drawRRect(skia.RRect.MakeRectXY(r, 40, 40), P('#9fe3ff', 70))
            c.drawRRect(skia.RRect.MakeRectXY(r, 40, 40), P('#333a44', stroke=12))
    arm(arm_l, -1, hand_l_obj)
    arm(arm_r, 1, hand_r_obj)
    c.restore()

# ---------------- Octopus ----------------
def octo(c, x, y, s, t, color='#c2457a', swim=0.0, wave=1.0, arm_glow=0.0, head_glow=0.0, hearts=None,
         look=(0, 0), crawl=0.0, wave_arm=0.0, bulbs=0.0, holds=None, mood='happy'):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    dark = mixc(color, '#000000', 0.3)
    light = mixc(color, '#ffffff', 0.35)
    ow = 7
    tips = []
    # tentacles
    for i in range(8):
        frac = i / 7
        base_ang = math.radians(lerp(155, 25, frac))  # spread downward (y positive down)
        # swim: arms gather backwards (down)
        ang = lerp(base_ang, math.radians(lerp(100, 80, frac)), swim)
        bx = lerp(-80, 80, frac)
        by = 60
        pts = []
        N = 18
        L = lerp(260, 330, swim) * (0.9 + 0.1 * math.sin(i * 1.7))
        for k in range(N + 1):
            u = k / N
            wv = math.sin(t * 3.2 * wave + i * 0.9 + u * 4.2) * 28 * u * wave
            if crawl:
                wv += math.sin(t * 5 + i * 1.3) * 18 * u * crawl
            px = bx + math.cos(ang) * L * u + math.cos(ang + math.pi / 2) * wv
            py = by + math.sin(ang) * L * u * (0.75 if not swim else 1) + math.sin(ang + math.pi / 2) * wv * 0.5
            # curl tip
            if u > 0.75 and swim < 0.5:
                curl = (u - 0.75) / 0.25
                px += math.cos(ang - 1.6 * (1 if frac < 0.5 else -1)) * 40 * curl
                py += -abs(math.sin(ang)) * 20 * curl
            pts.append((px, py))
        if wave_arm and i == 7:
            pts = []
            for k in range(N + 1):
                u = k / N
                a2 = math.radians(-20 - 50 * u) + math.sin(t * 7) * 0.4 * u
                pts.append((80 + 260 * u * math.cos(a2) * 0.9, 40 + 260 * u * math.sin(a2)))
        tips.append(pts[-1])
        for k in range(N):
            w = lerp(46, 10, k / N)
            c.drawLine(*pts[k], *pts[k + 1], P(OUT, stroke=w + ow * 2))
        for k in range(N):
            w = lerp(46, 10, k / N)
            c.drawLine(*pts[k], *pts[k + 1], P(color, stroke=w))
        if arm_glow > 0:
            for k in range(N):
                c.drawLine(*pts[k], *pts[k + 1], P('#7cf7ff', int(200 * arm_glow), stroke=lerp(14, 3, k / N), blur=6))
                c.drawLine(*pts[k], *pts[k + 1], P('#e9ffff', int(255 * arm_glow), stroke=lerp(5, 1.5, k / N)))
        # suckers
        for k in range(3, N, 3):
            w = lerp(46, 10, k / N)
            c.drawCircle(pts[k][0], pts[k][1] + w * 0.2, w * 0.22, P(light))
    # mantle
    mant = skia.Path()
    mant.moveTo(-105, 70)
    mant.cubicTo(-150, -60, -110, -230, 0, -235)
    mant.cubicTo(110, -230, 150, -60, 105, 70)
    mant.cubicTo(60, 105, -60, 105, -105, 70)
    mant.close()
    c.drawPath(mant, P(color))
    c.save()
    c.clipPath(mant, skia.ClipOp.kIntersect, True)
    c.drawOval(skia.Rect.MakeXYWH(30, -230, 140, 320), P(dark, 120, blur=20))
    for (sx, sy, r) in [(-50, -170, 14), (40, -150, 10), (-20, -110, 8), (60, -90, 12)]:
        c.drawCircle(sx, sy, r, P(light, 160))
    if head_glow > 0:
        c.drawCircle(0, -120, 90, P('#7cf7ff', int(160 * head_glow), blur=30))
    c.restore()
    c.drawPath(mant, P(OUT, stroke=ow))
    # nerve net in head
    if head_glow > 0:
        rng = np.random.RandomState(3)
        for k in range(14):
            a1 = rng.uniform(0, 6.28)
            r1 = rng.uniform(20, 90)
            c.drawLine(0, -110, math.cos(a1) * r1, -110 + math.sin(a1) * r1 * 0.9, P('#e9ffff', int(230 * head_glow), stroke=3))
        c.drawCircle(0, -110, 26, P('#bffcff', int(255 * head_glow), blur=8))
    # hearts
    if hearts:
        for (hx, hy, hs, alive) in hearts:
            beat = 1 + 0.14 * max(0, math.sin(t * 7.5)) ** 4 if alive else 1.0
            draw_heart(c, hx, hy, hs * beat, '#ff4d6d' if alive else '#7d8590', 255, glow=alive)
    # eyes
    for sx in (-1, 1):
        cx, cy = sx * 52, 0 if not hearts else 10
        r = skia.Rect.MakeXYWH(cx - 34, cy - 30, 68, 60)
        c.drawOval(r, P('#fff7e8'))
        c.drawOval(r, P(OUT, stroke=6))
        if (t % 4.1) > 0.12:
            pr = skia.Rect.MakeXYWH(cx - 20 + look[0] * 8, cy - 8 + look[1] * 6, 40, 16)
            c.drawRRect(skia.RRect.MakeRectXY(pr, 8, 8), P('#1a1010'))
            c.drawCircle(cx - 8 + look[0] * 8, cy - 6, 4, P('#ffffff'))
        else:
            c.drawLine(cx - 30, cy, cx + 30, cy, P(OUT, stroke=6))
    p = skia.Path(); p.moveTo(-18, 52); p.cubicTo(-8, 64, 8, 64, 18, 52)
    c.drawPath(p, P(OUT, stroke=6))
    if bulbs > 0:
        for i, (tx, ty) in enumerate(tips):
            on = clamp((bulbs * 9 - i) / 1.0)
            if on <= 0 and bulbs * 9 < i:
                pass
            bx, by = tx, ty - 40
            lit = clamp(bulbs * 9 - i)
            if lit > 0:
                c.drawCircle(bx, by, 50, P('#fff07a', int(200 * lit), blur=18))
            c.drawRect(skia.Rect.MakeXYWH(bx - 12, by + 22, 24, 22), P('#8a8f99'))
            c.drawCircle(bx, by, 28, P(mixc('#d9dde3', '#fff07a', lit)))
            c.drawCircle(bx, by, 28, P(OUT, stroke=5))
    c.restore()
    return tips

# ---------------- props ----------------
def bubbles(c, t, seed=1, n=26, alpha=110):
    rng = np.random.RandomState(seed)
    for i in range(n):
        x0 = rng.uniform(0, W)
        sp = rng.uniform(60, 160)
        r = rng.uniform(5, 18)
        ph = rng.uniform(0, H)
        y = H + 50 - ((t * sp + ph) % (H + 100))
        x = x0 + math.sin(t * 1.5 + i) * 18
        c.drawCircle(x, y, r, P('#ffffff', alpha // 3))
        c.drawCircle(x, y, r, P('#ffffff', alpha, stroke=3))
        c.drawCircle(x - r * 0.35, y - r * 0.35, r * 0.25, P('#ffffff', alpha))

def rays(c, t, alpha=40):
    for i in range(6):
        x = 120 + i * 190 + math.sin(t * 0.5 + i) * 40
        p = skia.Path()
        p.moveTo(x - 30, -50); p.lineTo(x + 30, -50); p.lineTo(x + 180, 1300); p.lineTo(x - 20, 1300); p.close()
        c.drawPath(p, P('#ffffff', alpha, blur=25))

def ocean_bg(c, t):
    vgrad(c, '#3fd0e6', '#0b4f8a')
    rays(c, t)
    # far seafloor silhouettes
    p = skia.Path(); p.moveTo(-50, 1550)
    for i in range(12):
        p.quadTo(i * 100 + 50, 1480 + (i % 3) * 30, i * 100 + 100, 1540)
    p.lineTo(1200, 2000); p.lineTo(-50, 2000); p.close()
    c.drawPath(p, P('#0a3f6e'))
    bubbles(c, t, 1)

def seaweed(c, x, y, h, t, color='#2fae6a'):
    pts = [(x + math.sin(t * 1.6 + k * 0.6 + x) * 12 * (k / 8), y - h * k / 8) for k in range(9)]
    for k in range(8):
        c.drawLine(*pts[k], *pts[k + 1], P(OUT, stroke=lerp(30, 12, k / 8) + 10))
        c.drawLine(*pts[k], *pts[k + 1], P(color, stroke=lerp(30, 12, k / 8)))

def rock(c, x, y, w, h, color='#6b7a8f'):
    r = skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h)
    c.drawOval(r, P(color)); c.drawOval(r, P(OUT, stroke=7))
    c.drawOval(skia.Rect.MakeXYWH(x - w * 0.3, y - h * 0.35, w * 0.3, h * 0.2), P('#ffffff', 50))

def coral(c, x, y, s, color):
    for i, (dx, hh) in enumerate([(-40, 140), (0, 200), (45, 160)]):
        c.drawLine(x + dx * s, y, x + dx * s * 1.3, y - hh * s, P(OUT, stroke=38 * s))
        c.drawLine(x + dx * s, y, x + dx * s * 1.3, y - hh * s, P(color, stroke=26 * s))
        c.drawCircle(x + dx * s * 1.3, y - hh * s, 22 * s, P(color)); c.drawCircle(x + dx * s * 1.3, y - hh * s, 22 * s, P(OUT, stroke=6))

def brain(c, x, y, s, a=255, glow=0):
    if glow:
        c.drawCircle(x, y, s * 1.6, P('#ffd23f', int(150 * glow), blur=s * 0.6))
    for (dx, dy, r) in [(-0.5, -0.1, 0.55), (0.0, -0.35, 0.6), (0.5, -0.1, 0.55), (-0.25, 0.3, 0.5), (0.3, 0.3, 0.5)]:
        c.drawCircle(x + dx * s, y + dy * s, r * s, P('#ff9ec4', a))
    for (dx, dy, r) in [(-0.5, -0.1, 0.55), (0.0, -0.35, 0.6), (0.5, -0.1, 0.55), (-0.25, 0.3, 0.5), (0.3, 0.3, 0.5)]:
        c.drawCircle(x + dx * s, y + dy * s, r * s, P(OUT, a, stroke=max(3, s * 0.08)))
    for (dx, dy, r) in [(-0.5, -0.1, 0.5), (0.0, -0.35, 0.55), (0.5, -0.1, 0.5), (-0.25, 0.3, 0.45), (0.3, 0.3, 0.45)]:
        c.drawCircle(x + dx * s, y + dy * s, r * s, P('#ff9ec4', a))
    c.drawLine(x, y - s * 0.7, x, y + s * 0.6, P('#d9678f', a, stroke=max(3, s * 0.07)))

def dog(c, x, y, s, t, glow=0):
    c.save(); c.translate(x, y); c.scale(s, s)
    c.drawOval(skia.Rect.MakeXYWH(-90, 40, 180, 150), P('#c98b4f')); c.drawOval(skia.Rect.MakeXYWH(-90, 40, 180, 150), P(OUT, stroke=7))
    c.drawCircle(0, 0, 90, P('#d99a5b')); c.drawCircle(0, 0, 90, P(OUT, stroke=7))
    for sx in (-1, 1):
        e = skia.Rect.MakeXYWH(sx * 85 - 30, -60, 60, 120)
        c.save(); c.rotate(sx * 15 + math.sin(t * 6) * 4)
        c.drawOval(e, P('#8a5a2b')); c.drawOval(e, P(OUT, stroke=7)); c.restore()
        c.drawCircle(sx * 32, -15, 13, P('#1a1010')); c.drawCircle(sx * 32 - 4, -19, 4, P('#ffffff'))
    c.drawOval(skia.Rect.MakeXYWH(-40, 15, 80, 55), P('#f1d2a8')); c.drawOval(skia.Rect.MakeXYWH(-40, 15, 80, 55), P(OUT, stroke=6))
    c.drawOval(skia.Rect.MakeXYWH(-16, 18, 32, 22), P('#1a1010'))
    c.drawOval(skia.Rect.MakeXYWH(-12, 52, 24, 30 + 6 * math.sin(t * 8)), P('#ff7b8a'))
    if glow > 0:
        rng = np.random.RandomState(7)
        c.drawCircle(0, -10, 70, P('#7cf7ff', int(120 * glow), blur=24))
        for k in range(12):
            a1 = rng.uniform(0, 6.28); r1 = rng.uniform(20, 70)
            c.drawLine(0, -20, math.cos(a1) * r1, -20 + math.sin(a1) * r1, P('#e9ffff', int(230 * glow), stroke=3))
    c.restore()

def drop(c, x, y, s, color):
    p = skia.Path()
    p.moveTo(x, y - s * 1.4)
    p.cubicTo(x + s * 0.4, y - s * 0.8, x + s, y - s * 0.2, x + s, y + s * 0.3)
    p.cubicTo(x + s, y + s * 0.9, x + s * 0.5, y + s * 1.2, x, y + s * 1.2)
    p.cubicTo(x - s * 0.5, y + s * 1.2, x - s, y + s * 0.9, x - s, y + s * 0.3)
    p.cubicTo(x - s, y - s * 0.2, x - s * 0.4, y - s * 0.8, x, y - s * 1.4)
    p.close()
    c.drawPath(p, P(color)); c.drawPath(p, P(OUT, stroke=8))
    c.drawOval(skia.Rect.MakeXYWH(x - s * 0.6, y - s * 0.3, s * 0.35, s * 0.6), P('#ffffff', 140))

def ecg(c, x, y, w, t, flat):
    r = skia.Rect.MakeXYWH(x - w / 2 - 20, y - 70, w + 40, 140)
    c.drawRRect(skia.RRect.MakeRectXY(r, 24, 24), P('#0f1d33', 220))
    c.drawRRect(skia.RRect.MakeRectXY(r, 24, 24), P('#ffffff', 200, stroke=5))
    path = skia.Path()
    for i in range(121):
        u = i / 120
        xx = x - w / 2 + u * w
        ph = (u * 3 - t * 1.2) % 1
        yy = y
        if not flat:
            if 0.4 < ph < 0.45: yy -= 50
            elif 0.45 < ph < 0.5: yy += 30
        if i == 0: path.moveTo(xx, yy)
        else: path.lineTo(xx, yy)
    clr = '#ff4d6d' if flat else '#5cff9d'
    c.drawPath(path, P(clr, 120, stroke=10, blur=6))
    c.drawPath(path, P(clr, stroke=5))
    draw_heart(c, x - w / 2 - 70, y, 34, '#7d8590' if flat else '#ff4d6d')

# ---------------- subtitles timing ----------------
SUBS = [
    ["Dieses Tier hat drei Herzen.", "Und eins hört auf zu schlagen,|wenn es schwimmt."],
    ["Die Rede ist vom Oktopus.", "Er wirkt wie ein Wesen|von einem anderen Planeten."],
    ["Zwei kleine Herzen pumpen Blut|durch die Kiemen.", "Das dritte versorgt|den restlichen Körper."],
    ["Sein Blut ist nicht rot,|sondern blau.", "Kupferhaltiges Hämocyanin|transportiert den Sauerstoff."],
    ["Beim Rückstoß-Schwimmen|setzt sein Körperherz kurz aus.", "Darum krabbelt er lieber|über den Meeresboden."],
    ["Rund 500 Millionen Nervenzellen,", "so viele wie ein Hund."],
    ["Mehr als zwei Drittel sitzen|in Armen und Körper.", "Über 200 Saugnäpfe pro Arm:|tasten, schmecken, riechen."],
    ["Hat ein Oktopus neun Gehirne?|Nicht ganz.", "Die Arme melden ihre Infos|ans zentrale Gehirn zurück."],
    ["Ein Gehirn –", "und acht sehr schlaue Arme."],
    ["Drei Herzen. Blaues Blut.|Denkende Arme.", "Welcher Fakt hat dich|am meisten überrascht?"],
]
VOICE = json.load(open('voice.json')) if os.path.exists('voice.json') else [10]*10  # spoken length per scene

def sub_for(scene, t):
    chunks = SUBS[scene]
    speak = VOICE[scene]
    lens = [len(ch) for ch in chunks]
    tot = sum(lens)
    acc = 0
    for ch, l in zip(chunks, lens):
        acc += l / tot * speak
        if t < acc or ch is chunks[-1]:
            return ch.split('|')
    return chunks[-1].split('|')

# ---------------- scenes ----------------
def cam(c, z, cx, cy):
    c.translate(W / 2, H / 2)
    c.scale(z, z)
    c.translate(-cx, -cy)

def s1(c, t, d):
    z = lerp(1.0, 1.15, ease((t - 1.5) / 3.5))
    c.save(); cam(c, z, 580, 900)
    ocean_bg(c, t)
    seaweed(c, 120, 1600, 260, t); seaweed(c, 960, 1620, 320, t, '#38c27a')
    ox = lerp(1350, 640, ease(t / 1.3))
    dead = t > 3.6
    hearts = [(-62, -95, 26, True), (62, -95, 26, True), (0, -150, 44, not dead)]
    octo(c, ox, 860 + math.sin(t * 2) * 15, 1.15, t, hearts=hearts, look=(-1, 0))
    fk = pop(t, 0.6, 0.45)
    if fk > 0:
        mood = 'shock' if t > 1.4 else 'happy'
        al, ar = (lerp(200, 300, ease((t - 1.4) / 0.3)), lerp(-20, -120, ease((t - 1.4) / 0.3))) if t > 1.4 else (200, -20)
        finn(c, 310, 1230 + (1 - fk) * 400, 0.9, t, mood=mood, arm_l=al, arm_r=ar, goggles=True, look=(1, -0.5))
    c.restore()
    draw_banner(c, '3 HERZEN?', t, 0.5, size=80)

def s2(c, t, d):
    k = ease(t / d)
    c.save(); cam(c, 1.08, lerp(480, 600, k), 960)
    top = mixc('#2fb8d8', '#1a1146', ease((t - 1.5) / 3))
    bot = mixc('#0b4f8a', '#2a1a5e', ease((t - 1.5) / 3))
    vgrad(c, top, bot)
    sa = ease((t - 2) / 2)
    rng = np.random.RandomState(5)
    for i in range(70):
        x, y = rng.uniform(-100, 1200), rng.uniform(0, 1000)
        tw = 0.6 + 0.4 * math.sin(t * 3 + i)
        c.drawCircle(x, y, rng.uniform(2, 5), P('#ffffff', int(230 * sa * tw)))
    pa = ease((t - 2.8) / 1.2)
    if pa > 0:
        c.drawCircle(820, 330, 90, P('#ffb347', int(255 * pa)))
        c.drawCircle(820, 330, 90, P(OUT, int(255 * pa), stroke=7))
        c.drawOval(skia.Rect.MakeXYWH(680, 300, 280, 60), P('#ffe08a', int(255 * pa), stroke=12))
    # reef
    p = skia.Path(); p.moveTo(-200, 1500)
    for i in range(14): p.quadTo(i * 110 - 150, 1380 + (i % 2) * 90, i * 110 - 90, 1470)
    p.lineTo(1400, 2200); p.lineTo(-200, 2200); p.close()
    c.drawPath(p, P('#5b4b7a')); c.drawPath(p, P(OUT, stroke=7))
    coral(c, 150, 1500, 1.0, '#ff7f6e'); coral(c, 980, 1490, 0.8, '#ffb000')
    hue = ['#c2457a', '#8a4fd1', '#d9a35b', '#c2457a']
    ph = (t * 0.8) % 3
    color = mixc(hue[int(ph)], hue[int(ph) + 1], ph - int(ph))
    octo(c, 420, 1050, 1.05, t, color=color, look=(1, -0.3))
    rock(c, 860, 1420, 300, 110)
    sc = 160 + math.sin(t * 9) * 25
    finn(c, 860, 1220, 0.9, t, mood='puzzled', arm_l=200, arm_r=-110 + math.sin(t * 9) * 12, look=(-1 if (t % 2) < 1 else 0.5, -0.5))
    c.restore()

def chalkboard(c):
    vgrad(c, '#2a7fb5', '#123c63')
    for i in range(0, W, 120):
        c.drawLine(i, 0, i, H, P('#ffffff', 18, stroke=3))
    r = skia.Rect.MakeXYWH(70, 420, 940, 820)
    c.drawRRect(skia.RRect.MakeRectXY(r, 30, 30), P('#8b5a2b'))
    c.drawRRect(skia.RRect.MakeRectXY(r, 30, 30), P(OUT, stroke=8))
    r2 = skia.Rect.MakeXYWH(100, 450, 880, 760)
    c.drawRRect(skia.RRect.MakeRectXY(r2, 18, 18), P('#1f4d3a'))
    c.drawRect(skia.Rect.MakeXYWH(0, 1560, W, 400), P('#a6c8de'))
    c.drawLine(0, 1560, W, 1560, P(OUT, stroke=7))

def s3(c, t, d):
    zt = 1.0 + 0.12 * ease((t - 2.2) / 1.0) - 0.12 * ease((t - 6.0) / 1.0)
    c.save(); cam(c, zt, 560, 830)
    chalkboard(c)
    ch = P('#f4f1e8', 230, stroke=7)
    # chalk octopus outline
    mant = skia.Path()
    mant.moveTo(440, 900); mant.cubicTo(400, 700, 450, 560, 540, 560); mant.cubicTo(630, 560, 680, 700, 640, 900); mant.close()
    c.drawPath(mant, ch)
    for i in range(6):
        a = math.radians(lerp(150, 30, i / 5))
        p = skia.Path(); p.moveTo(540 + math.cos(a) * 90, 900)
        p.cubicTo(540 + math.cos(a) * 200, 980, 540 + math.cos(a) * 260, 1080 + math.sin(t * 2 + i) * 10, 540 + math.cos(a) * 330, 1130)
        c.drawPath(p, ch)
    # gills
    for sx in (-1, 1):
        c.drawOval(skia.Rect.MakeXYWH(540 + sx * 150 - 40, 790, 80, 50), P('#9fd8ff', 200, stroke=6))
    hs = [(390, 760, 0.30 * d), (690, 760, 0.42 * d), (540, 700, 0.58 * d)]
    for i, (hx, hy, t0) in enumerate(hs):
        k = pop(t, t0, 0.4)
        if k > 0:
            beat = 1 + 0.12 * max(0, math.sin(t * 7)) ** 4
            draw_heart(c, hx, hy, (30 if i < 2 else 55) * k * beat)
    # arrows flowing
    if t > 0.6 * d:
        dash = skia.Paint(AntiAlias=True, Color=col('#ffd23f'), Style=skia.Paint.kStroke_Style, StrokeWidth=8, StrokeCap=skia.Paint.kRound_Cap)
        dash.setPathEffect(skia.DashPathEffect.Make([24, 22], -t * 120))
        p = skia.Path(); p.moveTo(390, 800); p.cubicTo(420, 860, 500, 860, 520, 760)
        c.drawPath(p, dash)
        p = skia.Path(); p.moveTo(690, 800); p.cubicTo(660, 860, 580, 860, 560, 760)
        c.drawPath(p, dash)
        p = skia.Path(); p.moveTo(540, 650); p.cubicTo(540, 560, 800, 540, 860, 640)
        c.drawPath(p, dash)
    # labels
    if t > 0.45 * d:
        draw_text_c(c, 'Kiemenherzen', 330, 690, 34, fill='#f4f1e8', outline='#1f4d3a', a=int(255 * ease((t - 0.45 * d) / 0.4)))
    if t > 0.62 * d:
        draw_text_c(c, 'Körperherz', 830, 545, 34, fill='#ffd23f', outline='#1f4d3a', a=int(255 * ease((t - 0.62 * d) / 0.4)))
    # FINN with pointer
    targets = [(390, 760), (690, 760), (540, 700)]
    idx = 0 if t < 0.42 * d else (1 if t < 0.58 * d else 2)
    tx, ty = targets[idx]
    fx, fy = 230, 1400
    ang = math.degrees(math.atan2(ty - (fy + 25 * 0.85), tx - (fx + 98 * 0.85)))
    def stick(hx, hy, a):
        c.drawLine(hx, hy, hx + math.cos(a) * 230, hy + math.sin(a) * 230, P(OUT, stroke=16))
        c.drawLine(hx, hy, hx + math.cos(a) * 230, hy + math.sin(a) * 230, P('#c58c4a', stroke=9))
        c.drawCircle(hx + math.cos(a) * 230, hy + math.sin(a) * 230, 9, P('#ff4d6d'))
    finn(c, fx, fy, 0.85, t, mood='happy', arm_l=150, arm_r=ang + math.sin(t * 6) * 3, hand_r_obj=stick, look=(1, -1))
    c.restore()
    draw_banner(c, '2 Kiemenherzen + 1 Körperherz', t, 0.5, size=54)

def s4(c, t, d):
    z = lerp(1.0, 1.18, ease((t - 0.62 * d) / 1.2))
    c.save(); cam(c, z, lerp(540, 700, ease((t - 0.62 * d) / 1.2)), 900)
    vgrad(c, '#5ab4e0', '#1d5a8f')
    for i in range(3):
        x = 140 + i * 140
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, 1180, 60, 200), 28, 28), P('#d8f3ff', 160))
        c.drawRect(skia.Rect.MakeXYWH(x + 5, 1290, 50, 85), P(['#ff6b6b', '#5cff9d', '#7c9cff'][i], 200))
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, 1180, 60, 200), 28, 28), P(OUT, stroke=6))
    c.drawRect(skia.Rect.MakeXYWH(-200, 1380, W + 400, 700), P('#e8d3b0'))
    c.drawLine(-200, 1380, W + 200, 1380, P(OUT, stroke=8))
    rx = lerp(-200, 330, ease(t / 0.9))
    bx = lerp(1300, 760, ease((t - 0.3) / 0.9))
    drop(c, rx, 860, 120, '#e8333f')
    drop(c, bx, 860, 120, '#2f7bff')
    for (x, lab, t0, clr) in [(rx, 'Fe', 1.2, '#ffffff'), (bx, 'Cu', 1.5, '#ffffff')]:
        k = pop(t, t0)
        if k > 0:
            c.save(); c.translate(x, 600); c.scale(k, k)
            c.drawCircle(0, 0, 70, P('#1b2a4a')); c.drawCircle(0, 0, 70, P('#ffd23f', stroke=7))
            draw_text_c(c, lab, 0, 22, 62, fill=clr, outline='#1b2a4a')
            c.restore()
    if t > 2.0:
        draw_text_c(c, 'Eisen', rx, 1060, 44, a=int(255 * ease(t - 2.0)))
        draw_text_c(c, 'Kupfer', bx, 1060, 44, fill='#9fd0ff', a=int(255 * ease(t - 2.0)))
    def lens(hx, hy, a):
        lx, ly = hx + 70, hy - 70
        c.drawLine(hx, hy, lx, ly, P(OUT, stroke=22)); c.drawLine(hx, hy, lx, ly, P('#7a4a22', stroke=14))
        c.drawCircle(lx + 50, ly - 50, 75, P('#bfeaff', 90)); c.drawCircle(lx + 50, ly - 50, 75, P('#3b3f47', stroke=14))
    finn(c, 560, 1290, 0.85, t, mood='shock' if t > 0.62 * d else 'happy', arm_l=160, arm_r=-60, hand_r_obj=lens, look=(1, -1))
    c.restore()
    draw_banner(c, 'Fe = rot  ·  Cu = blau', t, 1.0, size=60)

def s5(c, t, d):
    half = 0.55 * d
    c.save()
    shake = 0
    cam(c, 1.0, 540 + (math.sin(t * 30) * 4 if t < half else 0), 960)
    vgrad(c, '#46c6e0', '#145f96')
    rays(c, t, 30)
    p = skia.Path(); p.moveTo(-200, 1450)
    for i in range(14): p.quadTo(i * 110 - 150, 1420 + (i % 2) * 30, i * 110 - 90, 1450)
    p.lineTo(1400, 2200); p.lineTo(-200, 2200); p.close()
    c.drawPath(p, P('#f2d59b')); c.drawPath(p, P(OUT, stroke=7))
    for x in (80, 300, 900, 1020):
        seaweed(c, x, 1470, 220, t)
    if t < half:
        k = t / half
        ox = lerp(320, 1250, ease(k * 1.1)); oy = lerp(1100, 400, ease(k * 1.1))
        bubbles(c, t * 3, 4, 20, 140)
        c.save(); c.translate(ox, oy); c.rotate(-35 + 90); c.translate(-ox, -oy)
        octo(c, ox, oy, 0.85, t, swim=1.0, wave=0.4)
        c.restore()
        fx = lerp(-100, 380, ease(k * 1.4))
        finn(c, fx, 1250, 0.85, t, mood='tired' if k > 0.6 else 'shock', arm_l=lerp(150, 240, (math.sin(t * 12) + 1) / 2), arm_r=lerp(-30, 60, (math.sin(t * 12) + 1) / 2), goggles=True)
        ecg(c, 600, 300 - 0, 380, t, flat=k > 0.3)
    else:
        k = (t - half) / (d - half)
        rock(c, 260, 1420, 260, 100)
        finn(c, 260, 1300, 0.85, t, mood='tired' if k < 0.5 else 'happy', arm_l=200, arm_r=-20, goggles=True, sit=True, bounce=False)
        ox = lerp(1250, 720, ease(k * 1.3))
        octo(c, ox, 1180, 0.8, t, crawl=1.0, wave=0.6, look=(-1, 0))
        ecg(c, 600, 300, 380, t, flat=False)
    c.restore()
    draw_banner(c, 'Herzpause beim Schwimmen', t, 0.8, y=520, size=56, color='#ff4d6d')

def s6(c, t, d):
    z = lerp(1.15, 1.0, ease(t / d))
    c.save(); cam(c, z, 540, 960)
    vgrad(c, '#123a6b', '#050d24')
    rng = np.random.RandomState(9)
    for i in range(60):
        x, y = rng.uniform(0, W), (rng.uniform(0, H) - t * rng.uniform(10, 40)) % H
        c.drawCircle(x, y, rng.uniform(2, 5), P('#9ff6ff', int(rng.uniform(60, 180))))
    g = ease((t - 0.4) / 1.6)
    octo(c, 380, 900, 0.95, t, color='#b0407a', arm_glow=g, head_glow=g, look=(1, 0))
    dk = pop(t, 2.4, 0.5)
    if dk > 0:
        dog(c, 820, 1150 + (1 - dk) * 600, 0.9, t, glow=ease((t - 3.0) / 1.0))
    finn(c, 640, 1330, 0.8, t, mood='shock' if t > 1.5 else 'happy', arm_l=170, arm_r=-30 + math.sin(t * 8) * 15 if dk > 0 else -20, look=(1 if dk > 0 else -1, -1))
    c.restore()
    # counter
    n = int(500_000_000 * ease((t - 0.5) / 2.2))
    s = '{:,}'.format(n).replace(',', '.')
    draw_text_c(c, s, W / 2, 330, 100, fill='#7cf7ff', outline='#050d24', ow=16)
    draw_text_c(c, 'Nervenzellen', W / 2, 420, 52, fill='#ffffff', outline='#050d24')

def s7(c, t, d):
    c.save()
    cam(c, 1.06, lerp(460, 640, ease(t / d)), 980)
    vgrad(c, '#ffb38a', '#c4537a')
    rays(c, t, 35)
    p = skia.Path(); p.moveTo(-200, 1480)
    for i in range(14): p.quadTo(i * 110 - 150, 1440 + (i % 2) * 50, i * 110 - 90, 1480)
    p.lineTo(1400, 2200); p.lineTo(-200, 2200); p.close()
    c.drawPath(p, P('#e9c48a')); c.drawPath(p, P(OUT, stroke=7))
    coral(c, 90, 1500, 1.1, '#ff5e7e'); coral(c, 1040, 1500, 1.0, '#7c5cff')
    k = ease((t - 0.3) / 2.0)
    octo(c, 380, 950, 1.0, t, color='#b0407a', arm_glow=k, head_glow=1 - 0.6 * k, look=(1, 0.3))
    # FINN shaking an arm (hand reaches tentacle tip)
    laugh = t > 0.55 * d
    finn(c, 790, 1310, 0.82, t, mood='laugh' if laugh else 'happy', arm_l=lerp(200, 205, 1) + math.sin(t * 10) * (8 if laugh else 0), arm_r=-40)
    c.restore()
    # pie chart
    pk = ease((t - 1.0) / 1.6)
    cx, cy, r = 820, 640, 120
    c.drawCircle(cx, cy, r + 8, P('#1b2a4a', 230))
    c.drawCircle(cx, cy, r, P('#3a4a6a'))
    if pk > 0:
        arc = skia.Path(); arc.moveTo(cx, cy)
        arc.arcTo(skia.Rect.MakeXYWH(cx - r, cy - r, 2 * r, 2 * r), -90, 250 * pk, False); arc.close()
        c.drawPath(arc, P('#7cf7ff'))
    c.drawCircle(cx, cy, r + 4, P('#ffffff', stroke=6))
    draw_text_c(c, '> 2/3', cx, cy + 22, 58, fill='#ffffff', outline='#1b2a4a')
    # sense pills
    for i, w_ in enumerate(['tasten', 'schmecken', 'riechen']):
        kk = pop(t, 0.55 * d + i * 0.5)
        if kk > 0:
            y = 880 + i * 95
            c.save(); c.translate(820, y); c.scale(kk, kk)
            tw = text_w(w_, 44) + 50
            rr = skia.Rect.MakeXYWH(-tw / 2, -40, tw, 72)
            c.drawRRect(skia.RRect.MakeRectXY(rr, 36, 36), P('#ffffff'))
            c.drawRRect(skia.RRect.MakeRectXY(rr, 36, 36), P(OUT, stroke=5))
            f = skia.Font(FONT, 44); c.drawString(w_, -text_w(w_, 44) / 2, 12, f, P('#c4537a'))
            c.restore()
    draw_banner(c, 'über 2/3 in Armen und Körper', t, 0.5, size=54)

def aquarium(c, warm=0.0):
    vgrad(c, mixc('#9ad7ff', '#ffd9a0', warm), mixc('#3d7fb8', '#d98f5a', warm))
    c.drawRect(skia.Rect.MakeXYWH(-200, 1500, W + 400, 600), P('#d8c08f'))
    for x in range(60, W, 240):
        c.drawLine(x, 0, x, 1500, P('#ffffff', 60, stroke=10))
    c.drawRect(skia.Rect.MakeXYWH(30, 180, W - 60, 1340), P('#ffffff', 160, stroke=14))

def s8(c, t, d):
    c.save(); cam(c, lerp(1.0, 1.1, ease(t / d)), 540, lerp(960, 900, ease(t / d)))
    aquarium(c)
    # Y maze
    yp = P('#e6f6ff', 140, stroke=60)
    c.drawLine(560, 1450, 560, 1250, yp); c.drawLine(560, 1250, 430, 1120, yp); c.drawLine(560, 1250, 690, 1120, yp)
    for a, b in [((560, 1450), (560, 1250)), ((560, 1250), (430, 1120)), ((560, 1250), (690, 1120))]:
        c.drawLine(*a, *b, P('#ffffff', 220, stroke=8))
    c.drawCircle(690, 1110, 22, P('#ff8a3d'))
    octo(c, 560, 900, 0.85, t, look=(0, 0.5))
    # nine brains
    cx0, cy0 = 560, 430
    pos = [(cx0 + (i - 4) * 105, cy0 + (0 if i % 2 == 0 else 40)) for i in range(9)]
    conv = ease((t - 0.45 * d) / 1.4)
    for i, (x, y) in enumerate(pos):
        k = pop(t, 0.3 + i * 0.12)
        if k <= 0:
            continue
        if i == 4:
            brain(c, x, y, 46 * k * (1 + 0.3 * conv), glow=conv)
        else:
            if conv < 0.5:
                brain(c, x, y, 40 * k * (1 - conv * 2) + 0.01)
            else:
                u = (conv - 0.5) * 2
                ax, ay = lerp(x, cx0, u), lerp(y + 120, cy0 + 40, u)
                ang = math.atan2(cy0 - y, cx0 - x)
                c.drawLine(ax - math.cos(ang) * 40, ay - math.sin(ang) * 40, ax, ay, P('#ffd23f', stroke=10))
                c.drawCircle(ax, ay, 12, P('#ffd23f'))
    # FINN counting
    fing = t < 0.45 * d
    finn(c, 220, 1330, 0.8, t, mood='puzzled' if fing else 'happy', arm_l=200, arm_r=-80 + (math.sin(t * 12) * 20 if not fing else 0), look=(1, -1))
    if fing:
        n = min(9, int(t / 0.3) + 1)
        draw_text_c(c, str(n), 300, 1120, 90, fill='#ffd23f')
    c.restore()
    draw_banner(c, 'Studie 2020 · Current Biology', t, 0.4, y=250, size=50, color='#7cf7ff')

def s9(c, t, d):
    c.save(); cam(c, lerp(1.0, 1.08, ease(t / d)), 540, 960)
    aquarium(c, warm=0.7)
    octo(c, 560, 960, 0.9, t, color='#c2457a', head_glow=0.6, bulbs=ease((t - 0.8) / 3.0), wave=0.6, look=(0, -0.5))
    brain(c, 560, 760, 55, glow=1.0)
    clap = math.sin(t * 14)
    finn(c, 200, 1340, 0.8, t, mood='laugh', arm_l=lerp(300, 330, clap), arm_r=lerp(-120, -150, clap), look=(1, -1))
    c.restore()
    k = pop(t, 0.3)
    if k > 0:
        c.save(); c.translate(W / 2, 330); c.scale(k, k)
        draw_text_c(c, '1 Gehirn + 8 schlaue Arme', 0, 0, 64, fill='#ffd23f', outline='#3a1f0f', ow=12)
        c.restore()

def s10(c, t, d):
    c.save(); cam(c, lerp(1.15, 1.0, ease(t / 2.0)), 540, 960)
    ocean_bg(c, t)
    seaweed(c, 120, 1600, 260, t); seaweed(c, 960, 1620, 320, t, '#38c27a')
    octo(c, 700, 1020, 0.9, t, wave_arm=1.0, look=(-1, 0))
    finn(c, 260, 1290, 0.9, t, mood='happy', arm_l=200, arm_r=-80 + math.sin(t * 9) * 25, look=(0, 0))
    c.restore()
    icons = [(260, 'heart'), (540, 'drop'), (820, 'arm')]
    for i, (x, kind) in enumerate(icons):
        k = pop(t, 0.2 + i * 0.6)
        if k <= 0: continue
        fly = ease((t - 4.0) / 0.6)
        y = lerp(500, 260, fly)
        c.save(); c.translate(lerp(x, W / 2, fly), y); c.scale(k * (1 - 0.6 * fly), k * (1 - 0.6 * fly))
        c.drawCircle(0, 0, 95, P('#1b2a4a', 230)); c.drawCircle(0, 0, 95, P('#ffd23f', stroke=8))
        if kind == 'heart': draw_heart(c, 0, 10, 48)
        elif kind == 'drop': drop(c, 0, 0, 42, '#2f7bff')
        else:
            pth = skia.Path(); pth.moveTo(-40, 50); pth.cubicTo(-30, -20, 40, -10, 30, -50)
            c.drawPath(pth, P(OUT, stroke=36)); c.drawPath(pth, P('#c2457a', stroke=24))
        c.restore()
    lk = pop(t, 4.3, 0.5)
    if lk > 0:
        c.save(); c.translate(W / 2, 330); c.scale(lk, lk)
        r = skia.Rect.MakeXYWH(-430, -110, 860, 230)
        c.drawRRect(skia.RRect.MakeRectXY(r, 40, 40), P('#000000', 80, blur=14))
        c.drawRRect(skia.RRect.MakeRectXY(r, 40, 40), P('#1b2a4a', 240))
        c.drawRRect(skia.RRect.MakeRectXY(r, 40, 40), P('#ffd23f', stroke=8))
        draw_text_c(c, 'FAKTENWELT', 0, 10, 96, fill='#ffd23f', outline='#0d1626')
        draw_text_c(c, 'Wissen. Staunen. Verstehen.', 0, 80, 44, fill='#ffffff', outline='#0d1626')
        c.restore()

SCENES = [s1, s2, s3, s4, s5, s6, s7, s8, s9, s10]
FADE_COL = ['#ffffff', '#3fd0e6', '#ffffff', '#2f7bff', '#ffffff', '#ffffff', '#7cf7ff', '#ffffff', '#ffffff', '#ffffff']

def frame(surface, scene, t, d):
    c = surface.getCanvas()
    c.clear(col('#000000'))
    SCENES[scene](c, t, d)
    # subtitles (not in last scene's logo tail)
    sub = sub_for(scene, t)
    if not (scene == 9 and t > VOICE[9] + 0.2):
        draw_sub(c, sub)
    # transition in: flash from color over first 0.25s
    if scene > 0 and t < 0.25:
        c.drawRect(skia.Rect.MakeWH(W, H), P(FADE_COL[scene], int(255 * (1 - t / 0.25))))
    if scene == 0 and t < 0.12:
        c.drawRect(skia.Rect.MakeWH(W, H), P('#000000', int(255 * (1 - t / 0.12))))

def render_scene(i, out, still=None):
    """Szene rendern. Video in 4K (FF_SCALE=2 -> 2160x3840, alle Koordinaten bleiben 1080er-Raster),
    Standbilder immer in 1080x1920 (für Checks und Titelbild-Ausschnitte)."""
    d = DUR[i]
    K = 1.0 if still is not None else float(os.environ.get('FF_SCALE', '2'))
    surface = skia.Surface(int(W * K), int(H * K))

    def draw(t):
        c = surface.getCanvas(); c.save(); c.scale(K, K)
        frame(surface, i, t, d)
        c.restore()
    if still is not None:
        draw(still)
        surface.makeImageSnapshot().save(out, skia.kPNG)
        return
    n = int(round(d * FPS))
    tmp = out.replace('.mp4', '.part.mp4')
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgra', '-s', f'{int(W * K)}x{int(H * K)}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-profile:v', 'high', '-pix_fmt', 'yuv420p', '-r', str(FPS), tmp], stdin=subprocess.PIPE)
    for f in range(n):
        draw(f / FPS)
        arr = surface.makeImageSnapshot().toarray(colorType=skia.kBGRA_8888_ColorType)
        p.stdin.write(arr.tobytes())
    p.stdin.close()
    if p.wait() == 0:
        os.replace(tmp, out)

if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'still':
        i, t = int(sys.argv[2]), float(sys.argv[3])
        render_scene(i, f'still_{i}_{t}.png', still=t)
    else:
        for i in map(int, sys.argv[2:]):
            render_scene(i, f'scene_{i:02d}.mp4')
            print('done', i, flush=True)
