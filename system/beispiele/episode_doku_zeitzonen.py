"""Doku-Test: Zeitzonen (Frankreich 12, Russland 11, USA 11, China 1).
Stil: dunkle Infografik-Doku mit selbst gezeichneten Karten (Natural Earth, gemeinfrei).
Inhalt y=430..1200, Untertitel ~1260-1340, FINN klein unten."""
import math
import render as L
import geo
from render import (skia, W, H, P, OUT, clamp, ease, pop, lerp, draw_text_c, draw_banner, finn)

HIGHLIGHT = ['Russland?', 'Falsch.', 'EINER', 'elf', 'zehn', 'Frankreich.', 'zwölf.', 'Überseegebiete.',
             'Montagmittag,', 'Sonntag.', 'seltsamer.', 'fünf', 'eine.', '1949', 'fünfzehn', 'Dunkeln.', 'lieber?']

FY = 1690
NAVY = '#0a1024'
LAND = '#1c2c4f'
LANDS = '#2d4675'
GOLD = '#ffd23f'
RED = '#ff4d4d'
CYAN = '#7cf7ff'

WORLD = geo.Map(lon0=-180, lon1=180, lat0=-58, lat1=80, x=0, y=700, w=1080)
WORLD_HI = geo.Map(lon0=-180, lon1=180, lat0=-58, lat1=80, x=0, y=560, w=1080)
RUS = geo.Map(lon0=16, lon1=194, lat0=38, lat1=80, x=0, y=640, w=1080)
USA = geo.Map(lon0=140, lon1=300, lat0=-16, lat1=74, x=0, y=520, w=1080)
EUR = geo.Map(lon0=-14, lon1=24, lat0=35, lat1=58, x=-80, y=470, w=1240)
CHN = geo.Map(lon0=68, lon1=140, lat0=14, lat1=56, x=0, y=470, w=1080)
CHN8 = geo.Map(lon0=68, lon1=140, lat0=18, lat1=54, x=90, y=500, w=900)


def bg(c, t, top='#121a3a', bot=NAVY, grid=True):
    L.vgrad(c, top, bot)
    if grid:
        for i in range(0, W + 1, 90):
            c.drawLine(i, 0, i, H, P('#ffffff', 10, stroke=1))
        for j in range(0, H + 1, 90):
            c.drawLine(0, j, W, j, P('#ffffff', 10, stroke=1))
    geo.stars(c, W, 1250, t, n=70, a=90)


def rr(c, x, y, w, h, r, fill, stroke=None, sw=6, a=255):
    rect = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), r, r)
    c.drawRRect(rect, P(fill, a))
    if stroke:
        c.drawRRect(rect, P(stroke, a, stroke=sw))


def badge(c, x, y, text, k, size=46, fill='#1b2a4a', color=GOLD, txt='#ffffff'):
    if k <= 0:
        return
    w = L.text_w(text, size) + 56
    c.save(); c.translate(x, y); c.scale(k, k)
    rr(c, -w / 2, -size * 0.95, w, size * 1.6, 26, fill, color, 5, a=240)
    draw_text_c(c, text, 0, size * 0.3, size, fill=txt, outline=fill, ow=2)
    c.restore()


def big_number(c, x, y, s, k, size=200, color=GOLD, sub=None):
    if k <= 0:
        return
    c.save(); c.translate(x, y); c.scale(k, k)
    c.drawCircle(0, -size * 0.32, size * 0.75, P(color, 60, blur=40))
    draw_text_c(c, s, 0, 0, size, fill=color, outline='#0d1626', ow=10)
    if sub:
        draw_text_c(c, sub, 0, size * 0.42, 44, fill='#ffffff', outline='#0d1626', ow=6)
    c.restore()


def clock(c, x, y, r, hh, mm, color=CYAN, label=None, day=None, k=1.0):
    if k <= 0:
        return
    c.save(); c.translate(x, y); c.scale(k, k)
    c.drawCircle(0, 0, r * 1.15, P(color, 50, blur=25))
    c.drawCircle(0, 0, r, P('#0f1830')); c.drawCircle(0, 0, r, P(color, stroke=8))
    for i in range(12):
        a = i / 12 * 2 * math.pi
        c.drawLine(math.sin(a) * r * 0.82, -math.cos(a) * r * 0.82, math.sin(a) * r * 0.93, -math.cos(a) * r * 0.93,
                   P('#ffffff', 200, stroke=6 if i % 3 == 0 else 3))
    ah = ((hh % 12) + mm / 60) / 12 * 2 * math.pi; am = mm / 60 * 2 * math.pi
    c.drawLine(0, 0, math.sin(ah) * r * 0.5, -math.cos(ah) * r * 0.5, P('#ffffff', stroke=12))
    c.drawLine(0, 0, math.sin(am) * r * 0.75, -math.cos(am) * r * 0.75, P(color, stroke=7))
    c.drawCircle(0, 0, 10, P(color))
    if day:
        draw_text_c(c, day, 0, r + 70, 54, fill=GOLD, outline='#0d1626', ow=6)
    if label:
        draw_text_c(c, label, 0, -r - 34, 40, fill='#ffffff', outline='#0d1626', ow=6)
    c.restore()


def sun(c, x, y, r, t, a=255):
    for i in range(10):
        ang = i / 10 * 2 * math.pi + t * 0.4
        c.drawLine(x + math.cos(ang) * r * 1.3, y + math.sin(ang) * r * 1.3, x + math.cos(ang) * r * 1.7,
                   y + math.sin(ang) * r * 1.7, P('#ffd23f', a, stroke=8))
    c.drawCircle(x, y, r * 1.4, P('#ffb627', int(a * 0.35), blur=30))
    c.drawCircle(x, y, r, P('#ffd23f', a))


def xmark(c, x, y, s, k):
    if k <= 0:
        return
    c.save(); c.translate(x, y); c.scale(k * s, k * s); c.rotate(-8)
    for sgn in (-1, 1):
        c.drawLine(-110, -110 * sgn, 110, 110 * sgn, P('#000000', 120, stroke=58, blur=6))
        c.drawLine(-110, -110 * sgn, 110, 110 * sgn, P(RED, stroke=44))
    c.restore()


def band_zones(c, M, centers, t, t0, step, colors, a=70, merge=None):
    """vertikale Zeitzonen-Streifen nacheinander einblenden; merge=(t1, color) -> alle gleiche Farbe"""
    for i, lc in enumerate(centers):
        k = clamp((t - t0 - i * step) / 0.3)
        if k <= 0:
            continue
        colr = colors[i % len(colors)]
        if merge and t > merge[0]:
            colr = merge[1]
        M.band(c, lc - 7.5, lc + 7.5, colr, int(a * k))
        M.meridian(c, lc - 7.5, '#ffffff', int(50 * k))



def vignette(c, a=170):
    sh = skia.GradientShader.MakeRadial((W / 2, H * 0.45), H * 0.72,
                                        [skia.Color(0, 0, 0, 0), skia.Color(0, 0, 0, 0), skia.Color(0, 0, 0, a)], [0.0, 0.55, 1.0])
    pt = skia.Paint(); pt.setShader(sh); c.drawRect(skia.Rect.MakeWH(W, H), pt)


def night(c, M, t, lon_c=-40, speed=6.0, a=150):
    """weiche Tag-Nacht-Grenze, die über die Karte wandert"""
    lc = lon_c + t * speed
    for off in (-360, 0, 360):
        x0, _ = M.xy(lc - 90 + off, 0); x1, _ = M.xy(lc + 90 + off, 0); e = 18 * M.k
        sh = skia.GradientShader.MakeLinear([(x0 - e, 0), (x1 + e, 0)],
                                            [skia.Color(0, 0, 0, 0), skia.Color(3, 6, 20, a), skia.Color(3, 6, 20, a), skia.Color(0, 0, 0, 0)],
                                            [0.0, e / (x1 - x0 + 2 * e) * 2, 1 - e / (x1 - x0 + 2 * e) * 2, 1.0])
        pt = skia.Paint(); pt.setShader(sh)
        c.drawRect(skia.Rect.MakeLTRB(x0 - e, M.y, x1 + e, M.y + M.h), pt)


def zoom_map(e, k0, k1, c0, c1, ycen=830, y=470, h=760):
    k = math.exp(lerp(math.log(k0), math.log(k1), e))
    cx = lerp(c0[0], c1[0], e); cy = lerp(c0[1], c1[1], e)
    lat1 = cy + (ycen - y) / k
    return geo.Map(lon0=cx - 540 / k, lon1=cx + 540 / k, lat0=lat1 - h / k, lat1=lat1, x=0, y=y, w=1080)


def arc(c, x0, y0, x1, y1, f, color=GOLD, a=200, lift=0.35):
    if f <= 0:
        return
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2 - abs(x1 - x0) * lift - 40
    p = skia.Path(); p.moveTo(x0, y0)
    n = 30
    for i in range(1, int(n * f) + 1):
        u = i / n
        X = (1 - u) ** 2 * x0 + 2 * (1 - u) * u * mx + u * u * x1
        Y = (1 - u) ** 2 * y0 + 2 * (1 - u) * u * my + u * u * y1
        p.lineTo(X, Y)
    c.drawPath(p, P(color, int(a * 0.4), stroke=9, blur=6))
    c.drawPath(p, P(color, a, stroke=3))


ZONE_COLS = ['#ff4d4d', '#ffd23f', '#3fd0e6', '#a66bff', '#4cd964', '#ff8c2b']


# 1 ── Hook: Welches Land hat die meisten Zeitzonen?
def s1(c, t, d):
    bg(c, t)
    c.save(); c.clipRect(WORLD.rect().makeOutset(0, 30))
    for i, lc in enumerate(range(-172, 181, 15)):
        WORLD.band(c, lc - 7.5, lc + 7.5, ZONE_COLS[i % 6], 26 + int(14 * math.sin(t * 2 + i)))
    WORLD.draw_land(c, LAND, LANDS)
    night(c, WORLD, t, lon_c=-178, a=130)
    sx = (t * 260) % (W + 400) - 200                       # Scan-Linie
    c.drawRect(skia.Rect.MakeXYWH(sx - 60, WORLD.y, 60, WORLD.h), P(CYAN, 25, blur=12))
    c.drawLine(sx, WORLD.y, sx, WORLD.y + WORLD.h, P(CYAN, 120, stroke=3))
    if t > 3.2:
        WORLD.draw_country(c, 'Russia', fill=RED, a=int(255 * clamp((t - 3.2) / 0.3)), glow=True)
    if t > 5.6:
        WORLD.draw_country(c, 'China', fill=GOLD, a=int(160 + 95 * math.sin(t * 6) ** 2))
    c.restore()
    for i, lc in enumerate(range(-165, 181, 45)):          # kleine Uhren über der Karte
        X, _ = WORLD.xy(lc, 0)
        h = (i * 3 + int(t * 2)) % 12
        clock(c, X, 640, 34, h, (t * 60) % 60, color=ZONE_COLS[i % 6], k=1.0)
    rx, ry = WORLD.xy(95, 62)
    if 3.2 < t < 4.85:
        badge(c, rx, ry - 60, 'RUSSLAND?', pop(t, 3.2, 0.3), size=50, color=RED)
    xmark(c, rx, ry, 0.9, pop(t, 4.85, 0.25))
    cx, cy = WORLD.xy(104, 34)
    badge(c, cx, cy + 150, 'NUR 1 ZEITZONE?!', pop(t, 6.6, 0.3), size=46, color=GOLD)
    draw_text_c(c, '24 ZEITZONEN WELTWEIT', W / 2, 1185, 40, fill=CYAN, outline='#0d1626', ow=6, a=int(190 + 65 * math.sin(t * 4)))
    finn(c, 170, FY, 0.62, t, mood='shock' if t > 4.85 else ('puzzled' if t > 3.2 else 'happy'), blink=t > 1.0, arm_l=200, arm_r=-40, look=(1, -1))
    if t > 2.6:
        draw_banner(c, 'Die meisten Zeitzonen?' if t < 4.85 else 'FALSCH!', t, 2.6 if t < 4.85 else 4.85,
                    size=66, color=GOLD if t < 4.85 else RED)


# 2 ── Russland: 11 Zeitzonen, 10 Stunden
def s2(c, t, d):
    bg(c, t)
    c.save(); c.clipRect(RUS.rect().makeOutset(0, 60))
    RUS.draw_land(c, LAND, LANDS)
    band_zones(c, RUS, [30 + 15 * i for i in range(11)], t, 0.3, 0.28, ZONE_COLS, a=80)
    RUS.draw_country(c, 'Russia', fill='#ff6b6b', a=150)
    c.restore()
    n = min(11, max(0, int((t - 0.3) / 0.28) + 1))
    big_number(c, W / 2, 560, str(n), 1.0 if t > 0.3 else 0, size=170, color=RED, sub='ZEITZONEN')
    kx, ky = RUS.xy(20.5, 54.7); px, py = RUS.xy(158.6, 53.0)
    k1 = pop(t, 2.3, 0.3); k2 = pop(t, 3.6, 0.3)
    if k1 > 0:
        geo.pulse_dot(c, kx + 40, ky, t, RED); badge(c, 230, ky + 150, 'Kaliningrad UTC+2', k1, size=34, color=RED)
    if k2 > 0:
        geo.pulse_dot(c, px, py, t, CYAN, phase=0.4); badge(c, min(px, W - 230), py + 150, 'Kamtschatka UTC+12', k2, size=34, color=CYAN)
    k3 = clamp((t - 4.6) / 0.6)
    if k3 > 0:
        y = 1150; x0, x1 = 120, lerp(120, 960, ease(k3))
        c.drawLine(x0, y, x1, y, P(GOLD, stroke=10))
        tri = skia.Path(); tri.moveTo(x1 + 26, y); tri.lineTo(x1 - 8, y - 22); tri.lineTo(x1 - 8, y + 22); tri.close(); c.drawPath(tri, P(GOLD))
        draw_text_c(c, '10 STUNDEN', W / 2, y - 26, 58, fill=GOLD, outline='#0d1626', ow=8, a=int(255 * k3))
    finn(c, 920, FY, 0.6, t, mood='shock' if t > 4.6 else 'happy', arm_l=170, arm_r=-60, look=(-1, -1))
    draw_banner(c, 'Russland', t, 0.1, size=66, color=RED)


# 3 ── USA: auch 11
def s3(c, t, d):
    bg(c, t)
    c.save(); c.clipRect(USA.rect())
    USA.draw_land(c, LAND, LANDS)
    USA.draw_country(c, 'United States of America', fill='#3f7cff', a=230, glow=True)
    c.restore()
    pts = [(-150, 64, 'Alaska', 2.1), (-157.8, 21.3, 'Hawaii', 2.9), (166.6, 19.3, 'Wake', 3.9),
           (-176.5, 0.2, 'Baker', 4.4), (144.8, 13.4, 'Guam', 4.8), (-170.7, -14.3, 'Samoa', 5.1)]
    for lon, lat, name, t0 in pts:
        k = pop(t, t0, 0.3)
        if k <= 0:
            continue
        X, Y = USA.xy(lon if lon > 0 else lon + 360, lat)
        geo.pulse_dot(c, X, Y, t, GOLD, r=11, phase=t0)
        draw_text_c(c, name, min(max(X, 70), W - 70), Y + 52, 34, fill='#ffffff', outline='#0d1626', ow=6, a=int(255 * k))
    big_number(c, 860, 470, '11', pop(t, 1.1, 0.35), size=150, color='#6fa0ff', sub='ZEITZONEN')
    finn(c, 170, FY, 0.6, t, mood='puzzled', arm_l=200, arm_r=-30, look=(1, -1))
    draw_banner(c, 'USA', t, 0.1, size=66, color='#6fa0ff')


# 4 ── Frankreich: in Europa 1, insgesamt 12
def s4(c, t, d):
    bg(c, t)
    e = ease(clamp(t / 2.6))
    M = zoom_map(e, 3.0, 30.0, (10, 20), (3.5, 46.4))
    c.save(); c.clipRect(skia.Rect.MakeXYWH(0, 430, W, 800))
    M.draw_land(c, LAND, LANDS)
    k = clamp((t - 2.6) / 0.4)
    M.draw_country(c, 'France', fill=GOLD, a=int(110 + 145 * k), glow=True)
    c.restore()
    fx, fy = M.xy(2.4, 46.6)
    if t < 2.6:   # Zielrahmen während des Zooms
        r = 260 * (1.4 - e)
        c.drawRect(skia.Rect.MakeXYWH(fx - r, fy - r, 2 * r, 2 * r), P(GOLD, 160, stroke=4))
    if t < 7.0:
        badge(c, W / 2, 520, 'Europa: 1 Zeitzone', pop(t, 2.8, 0.3), size=40, color=CYAN)
    if 4.6 < t < 7.0:
        badge(c, W / 2, 1150, 'FRANKREICH', pop(t, 4.6, 0.3), size=60, color=GOLD)
    if t > 7.0:
        a = int(200 * (1 - clamp((t - 7.0) / 0.4)))
        c.drawRect(skia.Rect.MakeWH(W, H), P('#ffffff', a))
    big_number(c, W / 2, 760, '12', pop(t, 7.05, 0.3), size=330, color=GOLD, sub='ZEITZONEN!')
    finn(c, 900, FY, 0.62, t, mood='shock' if t > 7.0 else 'happy', arm_l=200, arm_r=-70, look=(-1, -1))
    draw_banner(c, 'Der Rekordhalter', t, 0.1, size=62)


# 5 ── Überseegebiete
FR_TERR = [(2.4, 46.6, 0.3, None), (-61.5, 16.2, 2.2, ('Karibik', 330, 650)), (-61.0, 14.6, 2.4, None), (-56.3, 46.9, 2.6, None),
           (-53.0, 4.0, 2.9, ('Südamerika', 440, 1010)), (55.5, -21.1, 4.0, ('Indischer Ozean', 760, 1020)), (45.1, -12.8, 4.2, None),
           (69.5, -49.3, 4.4, None), (165.5, -21.3, 5.0, None), (-176.2, -13.3, 5.2, None),
           (-149.4, -17.6, 5.4, ('Pazifik', 140, 1090)), (-139.5, -9.4, 5.6, None), (-134.9, -23.1, 5.8, None), (-109.2, 10.3, 6.0, None)]


def s5(c, t, d):
    bg(c, t)
    c.save(); c.clipRect(WORLD_HI.rect().makeOutset(0, 40))
    WORLD_HI.draw_land(c, LAND, LANDS)
    WORLD_HI.draw_country(c, 'France', fill=GOLD, glow=True)
    for nm in ['Fr. Polynesia', 'New Caledonia', 'Wallis and Futuna Is.', 'St. Pierre and Miquelon']:
        WORLD_HI.draw_country(c, nm, fill=GOLD)
    c.restore()
    night(c, WORLD_HI, t, lon_c=60, a=110)
    px0, py0 = WORLD_HI.xy(2.4, 46.6)
    for lon, lat, t0, lab in FR_TERR[1:]:
        X, Y = WORLD_HI.xy(lon, lat)
        arc(c, px0, py0, X, Y, clamp((t - t0 + 0.5) / 0.5), lift=0.18)
    shown = 0
    for lon, lat, t0, lab in FR_TERR:
        k = pop(t, t0, 0.3)
        if k <= 0:
            continue
        shown += 1
        X, Y = WORLD_HI.xy(lon, lat)
        geo.pulse_dot(c, X, Y, t, GOLD, r=10, phase=t0)
        if lab:
            name, lx, ly = lab
            c.drawLine(X, Y, lx, ly - 20, P(GOLD, int(150 * k), stroke=3))
            badge(c, lx, ly, name, k, size=36, color=GOLD)
    zones = min(12, max(1, int(1 + 11 * clamp((t - 2.0) / 4.4))))
    big_number(c, W / 2, 1200, f'{zones} / 12', 1.0, size=110, color=GOLD)
    k = pop(t, 6.2, 0.3)
    badge(c, W / 2, 480, 'Alles offiziell Frankreich', k, size=44, color=CYAN)
    finn(c, 150, FY, 0.58, t, mood='laugh' if t > 6.2 else 'puzzled', arm_l=210, arm_r=-30, look=(1, -1))
    draw_banner(c, 'Überseegebiete', t, 0.1, size=66)


# 6 ── Montagmittag vs. Sonntag
def s6(c, t, d):
    bg(c, t, top='#1a1240', bot='#0a0c20')
    k1 = pop(t, 0.3, 0.35); k2 = pop(t, 3.1, 0.35)
    clock(c, 290, 760, 150, 12, 0, color=GOLD, label='Wallis und Futuna', day='MONTAG 12:00', k=k1)
    clock(c, 790, 760, 150, 14, 0, color=CYAN, label='Franz.-Polynesien', day='SONNTAG 14:00', k=k2)
    kd = clamp((t - 1.6) / 0.6)
    if kd > 0:
        for yy in range(560, int(560 + 420 * kd), 36):
            c.drawLine(540, yy, 540, yy + 20, P('#ffffff', 170, stroke=5))
        draw_text_c(c, 'Datumsgrenze', W / 2, 1020, 34, fill='#ffffff', outline='#0d1626', ow=5, a=int(255 * kd))
    k3 = clamp((t - 4.4) / 0.5)
    if k3 > 0:
        draw_text_c(c, '22 STUNDEN', W / 2, 1080, 70, fill='#ffffff', outline='#0d1626', ow=8, a=int(255 * k3))
        draw_text_c(c, 'Unterschied', W / 2, 1140, 44, fill=GOLD, outline='#0d1626', ow=6, a=int(255 * k3))
    badge(c, W / 2, 470, 'IM SELBEN LAND!', pop(t, 5.9, 0.3), size=54, color=RED)
    if t > 7.1:
        a = int(140 * clamp((t - 7.1) / 0.5))
        c.drawRect(skia.Rect.MakeWH(W, H), P('#000000', a))
        for i in range(6):   # Glitch-Streifen
            y = (i * 337 + int(t * 900)) % H
            c.drawRect(skia.Rect.MakeXYWH(0, y, W, 8), P(RED, 90))
        badge(c, W / 2, 900, 'ES WIRD NOCH SELTSAMER', pop(t, 7.2, 0.3), size=50, color=RED)
    finn(c, 540, FY, 0.6, t, mood='shock' if t > 5.9 else 'puzzled', arm_l=200, arm_r=-60, look=(0, -1))
    draw_banner(c, 'Gleiches Land, anderer Tag', t, 0.1, size=56)


# 7 ── China: eigentlich 5 Zeitzonen, genutzt: 1
def s7(c, t, d):
    bg(c, t)
    c.save(); c.clipRect(CHN.rect())
    CHN.draw_land(c, LAND, LANDS)
    merge = 4.45
    CHN.draw_country(c, 'China', fill=RED if t > merge else '#ff8a8a', a=200 if t > merge else 120, glow=t > merge)
    band_zones(c, CHN, [75, 90, 105, 120, 135], t, 0.4, 0.45, ZONE_COLS, a=95, merge=(merge, RED))
    c.restore()
    if merge < t < merge + 0.35:
        c.drawRect(skia.Rect.MakeWH(W, H), P('#ffffff', int(180 * (1 - (t - merge) / 0.35))))
    n = min(5, max(0, int((t - 0.4) / 0.45) + 1))
    if t <= merge:
        big_number(c, W / 2, 1200, f'{n} Zeitzonen?', 1.0 if t > 0.4 else 0, size=96, color='#ffffff')
    else:
        big_number(c, W / 2, 1210, '1', pop(t, merge, 0.25), size=260, color=RED)
    finn(c, 920, FY, 0.6, t, mood='shock' if t > merge else 'puzzled', arm_l=170, arm_r=-60, look=(-1, -1))
    draw_banner(c, 'China', t, 0.1, size=66, color=RED)


# 8 ── Peking-Zeit, Kaschgar: Sonne erst gegen 15 Uhr am höchsten
def s8(c, t, d):
    bg(c, t)
    c.save(); c.clipRect(CHN8.rect())
    CHN8.draw_land(c, LAND, LANDS)
    CHN8.draw_country(c, 'China', fill=RED, a=190)
    c.restore()
    bx0, by0 = CHN8.xy(116.4, 39.9)
    c.save(); c.clipPath(CHN8.country_path('China'), doAntiAlias=True)
    for i in range(4):
        rad = ((t - 0.3) * 260 - i * 160)
        if 0 < rad < 1100:
            c.drawCircle(bx0, by0, rad, P(GOLD, int(150 * (1 - rad / 1100)), stroke=10))
    c.restore()
    bx, by = CHN8.xy(116.4, 39.9); kx, ky = CHN8.xy(75.99, 39.47)
    geo.pulse_dot(c, bx, by, t, GOLD); geo.pulse_dot(c, kx, ky, t, CYAN, phase=0.5)
    badge(c, bx - 10, by - 70, 'Peking', pop(t, 0.6, 0.3), size=38, color=GOLD)
    badge(c, kx + 70, ky - 70, 'Kaschgar', pop(t, 4.3, 0.3), size=38, color=CYAN)
    badge(c, W / 2, 470, 'Seit 1949: Peking-Zeit', pop(t, 0.3, 0.3), size=46, color=GOLD)
    hour = 12 + 3 * ease(clamp((t - 6.2) / 1.6))
    clock(c, 250, 1110, 85, int(hour), (hour % 1) * 60, color=CYAN, label=None, k=pop(t, 5.0, 0.3))
    k = pop(t, 5.0, 0.3)
    if k > 0:   # Sonnenbogen: höchster Stand wandert zu 15 Uhr
        cx, cy, R = 720, 1190, 190
        c.drawArc(skia.Rect.MakeXYWH(cx - R, cy - R, 2 * R, 2 * R), 180, 180, False, P('#ffffff', 70, stroke=4))
        p = clamp((t - 5.0) / 3.0) * 0.5
        ang = math.pi * (1 - p)
        sun(c, cx + math.cos(ang) * R, cy - math.sin(ang) * R, 34, t, a=int(255 * k))
        if t > 7.8:
            draw_text_c(c, 'Höchststand ca. 15 Uhr', 650, cy + 50, 40, fill=GOLD, outline='#0d1626', ow=6)
    finn(c, 540, FY, 0.58, t, mood='puzzled' if t < 7.8 else 'shock', arm_l=200, arm_r=-40, look=(0, -1))
    draw_banner(c, 'Eine Uhr für alle', t, 0.1, size=62)


# 9 ── Winter: Sonnenaufgang erst gegen 10 Uhr
def s9(c, t, d):
    dawn = clamp((t - 2.5) / 3.0)
    L.vgrad(c, L.mixc('#050814', '#2b2c6a', dawn), L.mixc('#0a1024', '#ff9a5a', dawn * 0.8))
    geo.stars(c, W, 1100, t, n=110, a=int(200 * (1 - dawn)))
    sun(c, 760, lerp(1260, 1040, dawn), 60, t, a=int(255 * clamp(dawn * 2)))
    c.drawRect(skia.Rect.MakeXYWH(0, 1150, W, 800), P('#0b0f1f'))
    for i, (x, w, h) in enumerate([(40, 160, 220), (230, 120, 300), (380, 200, 180), (620, 140, 260), (800, 220, 200)]):
        c.drawRect(skia.Rect.MakeXYWH(x, 1150 - h, w, h + 10), P('#11172e'))
        for wx in range(x + 20, x + w - 20, 40):     # erleuchtete Fenster
            for wy in range(1150 - h + 30, 1130, 50):
                if (wx * 7 + wy) % 3:
                    c.drawRect(skia.Rect.MakeXYWH(wx, wy, 18, 22), P('#ffd27a', int(200 * (1 - dawn * 0.7))))
    clock(c, W / 2, 620, 120, 10, 0, color=GOLD, label='Winter in Kaschgar', k=pop(t, 0.2, 0.35))
    badge(c, W / 2, 870, 'Sonnenaufgang: ca. 10 Uhr', pop(t, 1.6, 0.3), size=44, color=GOLD)
    fx = lerp(1150, 300, ease(clamp((t - 3.2) / 2.6)))
    finn(c, fx, FY, 0.62, t, mood='tired', arm_l=190, arm_r=-30, look=(-1, 0))
    draw_banner(c, 'Schulweg im Dunkeln', t, 3.4, size=62)


# 10 ── Frage + Logo
def s10(c, t, d):
    bg(c, t)
    k1 = pop(t, 0.3, 0.3); k2 = pop(t, 1.2, 0.3)
    badge(c, 300, 760, '12 Zeitzonen', k1, size=56, color=GOLD)
    badge(c, 300, 900, 'oder nur 1?', k2, size=56, color=RED)
    finn(c, 280, FY, 0.66, t, mood='laugh', arm_l=200 + math.sin(t * 8) * 20, arm_r=-70, look=(1, -1))
    lk = pop(t, max(0.5, L.VOICE[9] - 0.5), 0.5)
    if lk > 0:
        c.save(); c.translate(W / 2, 330); c.scale(lk, lk)
        r = skia.Rect.MakeXYWH(-430, -110, 860, 250)
        c.drawRRect(skia.RRect.MakeRectXY(r, 40, 40), P('#1b2a4a', 240)); c.drawRRect(skia.RRect.MakeRectXY(r, 40, 40), P(GOLD, stroke=8))
        draw_text_c(c, 'FAKTENFABRIK', 0, 0, 92, fill=GOLD, outline='#0d1626')
        draw_text_c(c, '@faktenfabrik.tv', 0, 62, 42, fill=CYAN, outline='#0d1626')
        draw_text_c(c, 'Wissen. Staunen. Verstehen.', 0, 104, 34, fill='#ffffff', outline='#0d1626')
        c.restore()
    else:
        draw_banner(c, 'Was wäre dir lieber?', t, 0.1, size=62)


def _vig(f):
    def g(c, t, d):
        f(c, t, d); vignette(c)
    return g


SCENES = [_vig(f) for f in (s1, s2, s3, s4, s5, s6, s7, s8, s9, s10)]
CAMERA = 'calm'
FADE_COL = ['#000000', '#ffffff', '#ffffff', '#ffd23f', '#ffffff', '#000000', '#ff4d4d', '#ffffff', '#000000', '#ffffff']
HOOK_TEXT = "MEISTE\nZEITZONEN?"
