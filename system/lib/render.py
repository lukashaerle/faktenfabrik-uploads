import skia, math, sys, subprocess, os, json
import numpy as np

W, H, FPS = 1080, 1920, 30
import os as _os
FONT = skia.Typeface.MakeFromFile(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'Poppins-800.ttf'))
FONT_B = skia.Typeface.MakeFromFile(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'Poppins-900.ttf'))

# ---------------- Design-System 2026 (modern look, 17.11.2026) ----------------
# Farben: tiefes Navy statt Schwarz, Marken-Gelb, knalliges Rot/Pink, Cyan als Zweitakzent.
INK = '#0e1424'      # Text-Kontur, Schatten, Glas-Grundton
PALETTES = {         # ACCENT = aktives Wort, Fortschritt, Schlüsselwörter · HOT = Hook, Schlüsselwort-Pille, Folgen-Knopf
    'gelb':   {'ACCENT': '#ffd23f', 'HOT': '#ff3b5c', 'CYAN': '#5ee6ff', 'LOGO': ('#ffe680', '#ffd23f', '#ffb000')},
    'neon':   {'ACCENT': '#3dff8f', 'HOT': '#ff2e93', 'CYAN': '#5ee6ff', 'LOGO': ('#a6ffcf', '#3dff8f', '#00d9a0')},
    'cyber':  {'ACCENT': '#2ee6ff', 'HOT': '#ff3dd2', 'CYAN': '#b9a6ff', 'LOGO': ('#a8f4ff', '#2ee6ff', '#7a7dff')},
    'sunset': {'ACCENT': '#ff9a1f', 'HOT': '#8b5cff', 'CYAN': '#ffd0a1', 'LOGO': ('#ffd27a', '#ff9a1f', '#ff4f7b')},
    'clean':  {'ACCENT': '#ffffff', 'HOT': '#ff2d55', 'CYAN': '#ff8fa6', 'LOGO': ('#ffffff', '#ffd6de', '#ff2d55')},
    'lime':   {'ACCENT': '#c8ff2e', 'HOT': '#7c4dff', 'CYAN': '#d9ccff', 'LOGO': ('#eaff9c', '#c8ff2e', '#7c4dff')},
    'mint':   {'ACCENT': '#2ef2c4', 'HOT': '#ff5a4e', 'CYAN': '#ffc2a8', 'LOGO': ('#b3ffee', '#2ef2c4', '#ff5a4e')},
    'ocean':  {'ACCENT': '#4dc3ff', 'HOT': '#ff6b1a', 'CYAN': '#ffd0a8', 'LOGO': ('#bfe9ff', '#4dc3ff', '#ff6b1a')},
    'berry':  {'ACCENT': '#ff7ad9', 'HOT': '#3b5bff', 'CYAN': '#a8d8ff', 'LOGO': ('#ffc6ef', '#ff7ad9', '#3b5bff')},
    'lava':   {'ACCENT': '#ff4d2e', 'HOT': '#1fd1ff', 'CYAN': '#ffb3a3', 'LOGO': ('#ffb199', '#ff4d2e', '#ff1f6b')},
    # schlicht: Weiß als Grundfarbe, genau EINE Akzentfarbe, nichts schräg
    'schlicht_orange': {'ACCENT': '#ffffff', 'HOT': '#ff8c2b', 'CYAN': '#ffffff', 'LOGO': ('#ffffff', '#ffffff', '#ffffff'), 'TILT': False},
    'schlicht_navy':   {'ACCENT': '#ffffff', 'HOT': '#26365e', 'CYAN': '#ffffff', 'LOGO': ('#ffffff', '#ffffff', '#ffffff'), 'TILT': False},
    'schlicht_rot':    {'ACCENT': '#ffffff', 'HOT': '#e8344e', 'CYAN': '#ffffff', 'LOGO': ('#ffffff', '#ffffff', '#ffffff'), 'TILT': False},
    # „Dynamic Minimalism“ (Trend 2026): weiße fette Schrift, dunkle Kontur, Wort für Wort, dezente Animation, keine Farbflächen
    'minimal':      {'ACCENT': '#ffffff', 'HOT': '#ffffff', 'CYAN': '#ffffff', 'LOGO': ('#ffffff', '#ffffff', '#ffffff'), 'TILT': False, 'MINIMAL': True, 'CAPS': False},
    # „abgespact“: Nebel-Polarlicht im Hintergrund, Sterne, Neon-Glühen auf Schrift und Rändern
    'cosmic':       {'ACCENT': '#ffffff', 'HOT': '#ff4fd8', 'CYAN': '#5ef2ff', 'LOGO': ('#5ef2ff', '#b18cff', '#ff4fd8'), 'TILT': False, 'MINIMAL': True, 'CAPS': False, 'COSMIC': True, 'GLOW': '#9b6bff'},
    'cosmic_caps':  {'ACCENT': '#ffffff', 'HOT': '#ff4fd8', 'CYAN': '#5ef2ff', 'LOGO': ('#5ef2ff', '#b18cff', '#ff4fd8'), 'TILT': False, 'MINIMAL': True, 'CAPS': True, 'COSMIC': True, 'GLOW': '#9b6bff'},
    # „Papier & Marker“: alles wie auf Papier gezeichnet, Tinte, Textmarker, Klebeband
    'papier':       {'ACCENT': '#1f1b18', 'HOT': '#e5412f', 'CYAN': '#2f6fd6', 'LOGO': ('#1f1b18', '#1f1b18', '#1f1b18'), 'TILT': True, 'PAPER': True, 'MARKER': '#ffd03f'},
    'minimal_caps': {'ACCENT': '#ffffff', 'HOT': '#ffffff', 'CYAN': '#ffffff', 'LOGO': ('#ffffff', '#ffffff', '#ffffff'), 'TILT': False, 'MINIMAL': True, 'CAPS': True},
}
PALETTE = _os.environ.get('FF_PALETTE', 'papier')   # Standard seit 17.11.2026: Papier & Marker (Marker seit 19.11. gelb wie FINNs Hoodie)
_pal = PALETTES.get(PALETTE, PALETTES['gelb'])
ACCENT, HOT, CYAN, LOGO_GRAD = _pal['ACCENT'], _pal['HOT'], _pal['CYAN'], _pal['LOGO']
TILT = _pal.get('TILT', True)
MINIMAL = _pal.get('MINIMAL', False)   # Untertitel ohne Pille, Hook ohne Farbflächen
CAPS = _pal.get('CAPS', False)         # Untertitel in GROSSBUCHSTABEN
PAPER = _pal.get('PAPER', False)       # Papier-Look (Hintergrund Papier, Tinte, Textmarker, Klebeband)
MARKER = _pal.get('MARKER', '#ffd84a') # Textmarker-Farbe
INK_P = '#1f1b18'                      # Tinte
COSMIC = _pal.get('COSMIC', False)     # bewegter Nebel/Polarlicht-Hintergrund, Sterne, Neon-Glühen
GLOW = _pal.get('GLOW', None)          # Glühfarbe für Schrift (None = kein Glühen)   # Sticker/Pillen leicht schräg (verspielt) oder gerade (schlicht)
NOW = 0.0            # globale Videozeit (setzt pipeline.py pro Bild) – für Hintergrund-Partikel
SCENE = -1           # aktuelle Szene (setzt pipeline.py) – Szene 0: Banner ab Bild 1 sichtbar (Cover)
MODERN = True        # False = alter Look (Notfall-Schalter)

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

# ---------------- Soundeffekte automatisch an Bildereignissen (seit 20.11.2026, nach Vorbild-Reel) ----------------
# pipeline.py audio spielt das Video einmal unsichtbar durch; jede Grafik-Funktion meldet hier, wann sie erscheint.
SFX_REC = None          # dict beim Aufnehmen, sonst None (normales Rendern: keine Wirkung)

def sfx(kind, key, t0=None):
    """kind: 'pop' (Einblendung), 'thud' (Stempel/große Zahl), 'count' (Zähler läuft, key enthält Dauer),
    'swipe' (Durchstreichen), 'type' (Etikett), 'ding' (Auflösung). t0 = Szenen-Zeit des Ereignisses."""
    if SFX_REC is None:
        return
    k = (kind, SCENE, key)
    if k not in SFX_REC:
        sc0 = STARTS[SCENE] if STARTS else 0.0
        SFX_REC[k] = (sc0 + t0) if t0 is not None else NOW

def pop(t, t0, d=0.35):
    """0 before t0, overshoot to 1"""
    if t >= t0: sfx('pop', round(t0, 2), t0)
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

def ease_out(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3

def spring(t, t0, d=0.45):
    """weiches Einschwingen 0 -> 1 mit ganz leichtem Überschwingen (modern, nicht hüpfig)"""
    x = (t - t0) / d
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    return 1 - math.exp(-6 * x) * math.cos(x * 4.2) * (1 - x)

_BG_CACHE = {}

def _bg_image(top, bot):
    """Hintergrund (Verlauf + Licht oben + Schatten unten) einmal klein vorrendern und dann hochskalieren.
    Verläufe sind weich, deshalb sieht man keinen Unterschied – in 4K aber ein Vielfaches schneller."""
    key = (top, bot)
    im = _BG_CACHE.get(key)
    if im is None:
        if len(_BG_CACHE) > 96:
            _BG_CACHE.clear()
        sw, sh, m = 216, 384, 0.2                      # Bild deckt -20 % .. +120 % des Bildausschnitts ab
        k = sw / (W * (1 + 2 * m))
        surf = skia.Surface(sw, sh)
        cc = surf.getCanvas(); cc.scale(k, sh / (H * (1 + 2 * m))); cc.translate(W * m, H * m)
        q = skia.Paint(AntiAlias=True)
        q.setShader(skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(0, H)], [col(top), col(bot)]))
        cc.drawRect(skia.Rect.MakeXYWH(-W, -H, 3 * W, 3 * H), q)
        q = skia.Paint(AntiAlias=True)
        q.setShader(skia.GradientShader.MakeRadial(skia.Point(W * 0.5, H * 0.24), 980, [col('#ffffff', 64), col('#ffffff', 0)]))
        cc.drawRect(skia.Rect.MakeXYWH(-W, -H, 3 * W, 3 * H), q)
        q = skia.Paint(AntiAlias=True)
        q.setShader(skia.GradientShader.MakeLinear([skia.Point(0, H * 0.66), skia.Point(0, H)], [col(INK, 0), col(INK, 60)]))
        cc.drawRect(skia.Rect.MakeXYWH(-W, -H, 3 * W, 3 * H), q)
        im = surf.makeImageSnapshot()
        _BG_CACHE[key] = im
    return im

_SAMP = skia.SamplingOptions(skia.FilterMode.kLinear)

def _hue_shift(hx, deg):
    import colorsys
    r, g, b = [int(hx.lstrip('#')[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    h, l, s_ = colorsys.rgb_to_hls(r, g, b)
    r, g, b = colorsys.hls_to_rgb((h + deg / 360) % 1, min(0.62, l * 1.0 + 0.30), min(1.0, s_ + 0.45))
    return '#%02x%02x%02x' % (int(r * 255), int(g * 255), int(b * 255))

_NEB = skia.Surface(216, 384)

def cosmic_bg(c, top, bot):
    """Bewegter Nebel / Polarlicht: drei leuchtende Farbwolken treiben langsam, dazu funkelnde Sterne.
    Nebel wird klein gerendert und hochskaliert (weich + schnell), Sterne gestochen scharf."""
    sw, sh, m = 216, 384, 0.2
    cc = _NEB.getCanvas(); cc.save()
    cc.scale(sw / (W * (1 + 2 * m)), sh / (H * (1 + 2 * m))); cc.translate(W * m, H * m)
    q = skia.Paint(AntiAlias=True)
    q.setShader(skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(0, H)], [col(top), col(bot)]))
    cc.drawRect(skia.Rect.MakeXYWH(-W, -H, 3 * W, 3 * H), q)
    T = NOW
    blobs = [(_hue_shift(top, 0), 0.25 + 0.12 * math.sin(T * 0.21), 0.22 + 0.06 * math.cos(T * 0.17), 760, 150),
             (_hue_shift(top, 70), 0.78 + 0.10 * math.cos(T * 0.19 + 1), 0.48 + 0.08 * math.sin(T * 0.23), 820, 120),
             (_hue_shift(bot, -60), 0.40 + 0.14 * math.sin(T * 0.15 + 2), 0.80 + 0.05 * math.cos(T * 0.2), 900, 110)]
    for clr, bx, by, r, a in blobs:
        q = skia.Paint(AntiAlias=True)
        q.setShader(skia.GradientShader.MakeRadial(skia.Point(W * bx, H * by), r, [col(clr, a), col(clr, int(a * 0.35)), col(clr, 0)], [0.0, 0.45, 1.0]))
        q.setBlendMode(skia.BlendMode.kScreen)
        cc.drawCircle(W * bx, H * by, r, q)
    # Polarlicht-Band: weicher, schräger Lichtschleier, der langsam wandert
    band = skia.Path(); off = math.sin(T * 0.12) * 160
    band.moveTo(-200, 420 + off); band.cubicTo(300, 260 + off, 700, 620 - off, 1300, 380 - off)
    band.lineTo(1300, 560 - off); band.cubicTo(700, 800 - off, 300, 440 + off, -200, 600 + off); band.close()
    q = skia.Paint(AntiAlias=True); q.setColor(col(_hue_shift(top, 120), 70)); q.setBlendMode(skia.BlendMode.kScreen)
    q.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 60))
    cc.drawPath(band, q)
    cc.restore()
    c.drawRect(skia.Rect.MakeXYWH(-2000, -2000, W + 4000, H + 4000), P(bot))
    c.drawImageRect(_NEB.makeImageSnapshot(), skia.Rect.MakeXYWH(-W * m, -H * m, W * (1 + 2 * m), H * (1 + 2 * m)), _SAMP)
    rng = np.random.RandomState(5)
    for i in range(70):
        x, y, r = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(1.2, 3.4)
        tw = 0.5 + 0.5 * math.sin(T * rng.uniform(1.0, 3.0) + rng.uniform(0, 6.28))
        al = int(rng.uniform(90, 230) * tw)
        if r > 2.6:
            c.drawCircle(x, y, r * 3, P('#ffffff', al // 5, blur=r * 2))
        c.drawCircle(x, y, r, P('#ffffff', al))
    # gelegentliche Sternschnuppe (alle ~7 s, ruhig und kurz)
    ph = (T % 7.0) / 7.0
    if ph < 0.09:
        u = ph / 0.09; sx0 = 1150 - 900 * u; sy0 = 120 + 380 * u
        g = skia.Paint(AntiAlias=True); g.setStrokeWidth(4); g.setStyle(skia.Paint.kStroke_Style); g.setStrokeCap(skia.Paint.kRound_Cap)
        g.setShader(skia.GradientShader.MakeLinear([skia.Point(sx0, sy0), skia.Point(sx0 + 260, sy0 - 110)], [col('#ffffff', int(230 * math.sin(u * math.pi))), col('#ffffff', 0)]))
        c.drawLine(sx0, sy0, sx0 + 260, sy0 - 110, g)

_PAPER_IMG = None

def _paper_image():
    """Papier-Struktur einmal erzeugen: warmes Off-White, feines Korn, Fasern, leicht dunklere Ränder."""
    global _PAPER_IMG
    if _PAPER_IMG is None:
        w, h = 540, 960
        rng = np.random.RandomState(42)
        base = np.array([244, 239, 228], np.float32)
        n = rng.normal(0, 1, (h, w)).astype(np.float32)
        k = np.ones(3, np.float32) / 3
        nb = np.apply_along_axis(lambda r: np.convolve(r, k, 'same'), 1, n)
        img = base[None, None, :] + (n * 2.2 + nb * 3.0)[..., None]
        for _ in range(260):                                    # Papierfasern
            x, y, L_, a = rng.randint(0, w), rng.randint(0, h), rng.randint(6, 26), rng.uniform(0, 3.14)
            for t_ in range(L_):
                xx, yy = int(x + math.cos(a) * t_), int(y + math.sin(a) * t_)
                if 0 <= xx < w and 0 <= yy < h:
                    img[yy, xx] -= 7
        yy, xx = np.mgrid[0:h, 0:w]
        d = np.sqrt(((xx - w / 2) / (w * 0.62)) ** 2 + ((yy - h / 2) / (h * 0.62)) ** 2)
        img *= (1 - 0.10 * np.clip(d - 0.55, 0, 1))[..., None]
        img = np.clip(img, 0, 255).astype(np.uint8)
        rgba = np.dstack([img, np.full((h, w), 255, np.uint8)])
        _PAPER_IMG = skia.Image.fromarray(np.ascontiguousarray(rgba), colorType=skia.kRGBA_8888_ColorType)
    return _PAPER_IMG

_PAPER_CACHE = {}

def paper_bg(c, top, bot):
    """Papier-Hintergrund. Die Szenenfarbe kommt als zarter Aquarell-Fleck zurück (Thema bleibt erkennbar).
    Papier + Farbflecken werden pro Farbpaar einmal vorgerendert und nur noch als ein Bild gezeichnet (schnell in 4K)."""
    key = (top, bot)
    im = _PAPER_CACHE.get(key)
    if im is None:
        if len(_PAPER_CACHE) > 48:
            _PAPER_CACHE.clear()
        sw, sh = 540, 960
        surf = skia.Surface(sw, sh); cc = surf.getCanvas()
        cc.drawImageRect(_paper_image(), skia.Rect.MakeWH(sw, sh), _SAMP)
        cc.save(); cc.scale(sw / W, sh / H)
        tint = _hue_shift(mixc(top, bot, 0.4), 0)
        for (bx, by, r, a) in [(0.18, 0.16, 520, 40), (0.86, 0.62, 600, 34), (0.3, 0.92, 480, 26)]:
            q = skia.Paint(AntiAlias=True)
            q.setShader(skia.GradientShader.MakeRadial(skia.Point(W * bx, H * by), r, [col(tint, a), col(tint, int(a * 0.6)), col(tint, 0)], [0.0, 0.6, 1.0]))
            q.setBlendMode(skia.BlendMode.kMultiply)
            cc.drawCircle(W * bx, H * by, r, q)
        cc.restore()
        im = surf.makeImageSnapshot(); _PAPER_CACHE[key] = im
    c.drawRect(skia.Rect.MakeXYWH(-2000, -2000, W + 4000, H + 4000), P('#f2ede2'))
    c.drawImageRect(im, skia.Rect.MakeXYWH(-40, -40, W + 80, H + 80), _SAMP)
    for y in range(160, H, 96):                                 # ganz feine Notizbuch-Linien
        c.drawLine(0, y, W, y, P('#7aa7c7', 26, stroke=2))

def rough_path(pts, seed=0, amp=3.0):
    """Linie mit leichtem Handzittern."""
    rng = np.random.RandomState(seed)
    p = skia.Path(); p.moveTo(pts[0][0] + rng.uniform(-amp, amp), pts[0][1] + rng.uniform(-amp, amp))
    for (x, y) in pts[1:]:
        p.lineTo(x + rng.uniform(-amp, amp), y + rng.uniform(-amp, amp))
    return p

def marker_swipe(c, x, y, w, h, color, u=1.0, a=150, seed=1):
    """Textmarker-Strich (u = wie weit schon gezogen, 0..1), ausgefranste Enden, multipliziert wie echter Marker."""
    if u <= 0:
        return
    rng = np.random.RandomState(seed)
    ww = w * u
    p = skia.Path(); p.moveTo(x - 6, y + rng.uniform(-3, 3))
    steps = 6
    for i in range(1, steps + 1):
        p.lineTo(x + ww * i / steps, y + rng.uniform(-4, 4))
    p.lineTo(x + ww + 6, y + h + rng.uniform(-3, 3))
    for i in range(steps - 1, -1, -1):
        p.lineTo(x + ww * i / steps, y + h + rng.uniform(-4, 4))
    p.close()
    q = P(color, a); q.setBlendMode(skia.BlendMode.kMultiply)
    c.drawPath(p, q)

def tape(c, cx, cy, w, h, ang=0.0, a=170):
    """Klebestreifen (halbtransparent, gezackte Enden)."""
    c.save(); c.translate(cx, cy); c.rotate(ang)
    p = skia.Path(); n = 6
    p.moveTo(-w / 2, -h / 2)
    p.lineTo(w / 2, -h / 2)
    for i in range(n + 1):
        p.lineTo(w / 2 + (6 if i % 2 else 0), -h / 2 + h * i / n)
    p.lineTo(-w / 2, h / 2)
    for i in range(n, -1, -1):
        p.lineTo(-w / 2 - (6 if i % 2 else 0), -h / 2 + h * i / n)
    p.close()
    c.drawPath(p, P('#000000', 30, blur=6))
    c.drawPath(p, P('#efe2bf', a))
    c.restore()

def paper_card(c, rect, ang=0.0, fill='#fffdf7', tape_top=True):
    """Papierzettel mit weichem Schatten und Klebestreifen."""
    c.save(); c.translate(rect.centerX(), rect.centerY()); c.rotate(ang); c.translate(-rect.centerX(), -rect.centerY())
    c.drawRect(rect.makeOffset(6, 12), P('#3a2a1a', 50, blur=14))
    c.drawRect(rect, P(fill))
    c.drawRect(rect, P('#d9cfbd', stroke=2))
    if tape_top:
        tape(c, rect.left() + 46, rect.top() + 4, 120, 40, -24)
        tape(c, rect.right() - 46, rect.top() + 4, 120, 40, 22)
    c.restore()

def vgrad(c, top, bot, y0=0, y1=H):
    full = MODERN and y0 == 0 and y1 == H
    if full and PAPER:
        paper_bg(c, top, bot)
        return
    if full and COSMIC:
        cosmic_bg(c, top, bot)
        return
    if full:
        c.drawRect(skia.Rect.MakeXYWH(-2000, -2000, W + 4000, H + 4000), P(mixc(top, bot, 0.5)))
        c.drawImageRect(_bg_image(top, bot), skia.Rect.MakeXYWH(-W * 0.2, -H * 0.2, W * 1.4, H * 1.4), _SAMP)
        bokeh(c)
        return
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeLinear([skia.Point(0, y0), skia.Point(0, y1)], [col(top), col(bot)]))
    c.drawRect(skia.Rect.MakeXYWH(-2000, -2000, W + 4000, H + 4000), p)

def bokeh(c):
    """dezente Lichtpunkte, die langsam nach oben schweben (Verlaufs-Kreise statt Unschärfe-Filter)."""
    rng = np.random.RandomState(11)
    for i in range(12):
        x0, y0_, r = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(22, 80)
        sp, ph, al = rng.uniform(6, 18), rng.uniform(0, 6.28), int(rng.uniform(12, 30))
        x = x0 + math.sin(NOW * 0.25 + ph) * 40
        y = (y0_ - NOW * sp) % (H + 200) - 100
        q = skia.Paint(AntiAlias=True)
        q.setShader(skia.GradientShader.MakeRadial(skia.Point(x, y), r, [col('#ffffff', al), col('#ffffff', al), col('#ffffff', 0)], [0.0, 0.35, 1.0]))
        c.drawCircle(x, y, r, q)

def depth(c, light=1.0):
    """Tiefe nachträglich über einen eigenen Hintergrund legen (für Szenen ohne vgrad)."""
    cx, cy, R0 = W * 0.5, H * 0.24, 980
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeRadial(skia.Point(cx, cy), R0, [col('#ffffff', int(64 * light)), col('#ffffff', 0)]))
    c.drawCircle(cx, cy, R0, p)
    bokeh(c)

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
    if MODERN:
        ow = ow or size * 0.12
        # weicher Schlagschatten statt dicker Comic-Kontur
        c.drawString(s, x - w / 2, y + size * 0.07, f, P(INK, int(a * 0.35), blur=size * 0.07))
    else:
        ow = ow or size * 0.16
    c.drawString(s, x - w / 2, y, f, P(outline, a, stroke=ow))
    c.drawString(s, x - w / 2, y, f, P(fill, a))

def glass(c, rect, radius, tint=INK, alpha=150, blur=10, stroke_a=60):
    """Milchglas-Fläche: verwischt den Hintergrund dahinter, dunkler Schleier, feiner heller Rand."""
    if PAPER:
        a = clamp(alpha / 200)
        c.drawRRect(skia.RRect.MakeRectXY(rect.makeOffset(4, 9), radius, radius), P('#3a2a1a', int(50 * a), blur=10))
        c.drawRRect(skia.RRect.MakeRectXY(rect, radius, radius), P(INK_P, int(235 * a)))
        return
    rr_ = skia.RRect.MakeRectXY(rect, radius, radius)
    c.drawRRect(skia.RRect.MakeRectXY(rect.makeOffset(0, 10), radius, radius), P('#000000', int(alpha * 0.35), blur=18))
    c.save()
    c.clipRRect(rr_, skia.ClipOp.kIntersect, True)
    _lp, _bf = skia.Paint(), skia.ImageFilters.Blur(blur, blur)   # Referenzen halten (sonst Absturz im Binding)
    rec = skia.Canvas.SaveLayerRec(rect, _lp, _bf, 0)
    c.saveLayer(rec)
    c.restore()
    c.drawRRect(rr_, P(tint, alpha))
    g = skia.Paint(AntiAlias=True)
    g.setShader(skia.GradientShader.MakeLinear([skia.Point(0, rect.top()), skia.Point(0, rect.bottom())],
                                               [col('#ffffff', 34), col('#ffffff', 0)]))
    c.drawRRect(rr_, g)
    c.restore()
    if COSMIC:
        gp = skia.Paint(AntiAlias=True); gp.setStyle(skia.Paint.kStroke_Style); gp.setStrokeWidth(3)
        gp.setShader(skia.GradientShader.MakeLinear([skia.Point(rect.left(), 0), skia.Point(rect.right(), 0)],
                                                    [col(LOGO_GRAD[0], int(stroke_a * 3.4)), col(LOGO_GRAD[2], int(stroke_a * 3.4))]))
        c.drawRRect(rr_, gp)
        gp.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 8)); gp.setStrokeWidth(6)
        c.drawRRect(rr_, gp)
    else:
        c.drawRRect(rr_, P('#ffffff', stroke_a, stroke=2.5))

def draw_chip(c, s, x, y, size=44, k=1.0, fill='#ffffff', txt=INK, a=255):
    """Moderne Beschriftungs-Pille (z. B. 'Bewegung', '55 %'), mittig auf (x, y). k = Einblend-Fortschritt 0..1."""
    if k <= 0:
        return
    sfx('pop', ('chip', s, int(x) // 40, int(y) // 40))
    f = skia.Font(FONT, size); w = f.measureText(s) + size * 1.1; h = size * 1.55
    e = ease_out(k)
    x = safe_x(x, w + 10, y - h / 2, y + h / 2)                     # nie unter die Like-/Kommentar-Knöpfe
    c.save(); c.translate(x, y + (1 - e) * 24); s_ = 0.9 + 0.1 * e; c.scale(s_, s_)
    al = int(a * clamp(k * 1.6))
    r = skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h)
    if PAPER:
        if fill == ACCENT:
            fill = MARKER
        c.rotate(-2)
        c.drawRect(r.makeOffset(3, 7), P('#3a2a1a', int(al * 0.25), blur=8))
        c.drawRect(r, P('#fffdf7' if fill == '#ffffff' else fill, al))
        c.drawPath(rough_path([(r.left(), r.top()), (r.right(), r.top()), (r.right(), r.bottom()), (r.left(), r.bottom()), (r.left(), r.top())], seed=len(s), amp=2.5), P(INK_P, al, stroke=4))
        c.drawString(s, -f.measureText(s) / 2, size * 0.36, f, P(INK_P if txt == INK else txt, al))
        c.restore()
        return
    c.drawRRect(skia.RRect.MakeRectXY(r.makeOffset(0, 8), h / 2, h / 2), P('#000000', int(al * 0.25), blur=12))
    c.drawRRect(skia.RRect.MakeRectXY(r, h / 2, h / 2), P(fill, al))
    c.drawString(s, -f.measureText(s) / 2, size * 0.36, f, P(txt, al))
    c.restore()

def draw_logo_card(c, t, t0, y=330):
    """Marken-Endkarte für Szene 10 (statt selbstgebauter Box): FAKTENFABRIK, @faktenfabrik.tv, Slogan."""
    k = spring(t, t0, 0.55)
    if k <= 0:
        return
    e = ease_out(clamp((t - t0) / 0.45))
    if PAPER:
        c.save(); c.translate(0, (1 - e) * 50)
        r = skia.Rect.MakeXYWH(W / 2 - 440, y - 130, 880, 270)
        paper_card(c, r, -1.5)
        c.save(); c.translate(W / 2, y); c.rotate(-1.5)
        fb = skia.Font(FONT_B, 92); wt = fb.measureText('FAKTENFABRIK')
        marker_swipe(c, -wt / 2, -40, wt, 54, MARKER, u=ease_out(clamp((t - t0 - 0.2) / 0.5)), a=170, seed=3)
        c.drawString('FAKTENFABRIK', -wt / 2, 4, fb, P(INK_P))
        f2 = skia.Font(FONT, 42); s2 = '@faktenfabrik.tv'
        c.drawString(s2, -f2.measureText(s2) / 2, 66, f2, P(HOT))
        f3 = skia.Font(FONT, 30); s3 = 'Wissen. Staunen. Verstehen.'
        c.drawString(s3, -f3.measureText(s3) / 2, 110, f3, P('#5a4e44'))
        c.restore(); c.restore()
        return
    c.save(); c.translate(W / 2, y + (1 - e) * 50)
    r = skia.Rect.MakeXYWH(-450, -130, 900, 270)
    c.save(); s_ = 0.94 + 0.06 * k; c.scale(s_, s_)
    glass(c, r, 54, alpha=int(228 * e))
    fb = skia.Font(FONT_B, 96); wt = fb.measureText('FAKTENFABRIK')
    gp = skia.Paint(AntiAlias=True)
    gp.setShader(skia.GradientShader.MakeLinear([skia.Point(-wt / 2, 0), skia.Point(wt / 2, 0)],
                                                [col(x, int(255 * e)) for x in LOGO_GRAD]))
    c.drawString('FAKTENFABRIK', -wt / 2, 2 + 6, fb, P(INK, int(110 * e), blur=8))
    c.drawString('FAKTENFABRIK', -wt / 2, 2, fb, gp)
    f2 = skia.Font(FONT, 44); s2 = '@faktenfabrik.tv'
    c.drawString(s2, -f2.measureText(s2) / 2, 66, f2, P(CYAN, int(255 * e)))
    f3 = skia.Font(FONT, 32); s3 = 'Wissen. Staunen. Verstehen.'
    c.drawString(s3, -f3.measureText(s3) / 2, 112, f3, P('#ffffff', int(220 * e)))
    c.restore(); c.restore()

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
    if MODERN:
        if color == '#ffd23f':
            color = ACCENT                 # Standardfarbe folgt der Palette
        return _banner_modern(c, s, t, t0, y, size, color)
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

def _banner_modern(c, s, t, t0, y, size, color):
    """Kopfzeile als Milchglas-Pille: gleitet weich von unten ein, farbiger Punkt links als Akzent."""
    if SCENE == 0 and t0 <= 0.6:
        k = e = 1.0                         # Szene 1: ab Bild 1 sichtbar (Cover)
    else:
        k = spring(t, t0, 0.5)
        e = ease_out(clamp((t - t0) / 0.35))
    if k <= 0:
        return
    if PAPER:
        # Klebeband-Etikett mit Tinten-Schrift, ein Stück schräg
        size = size * 0.9
        f = skia.Font(FONT, size)
        while f.measureText(s) > 860:
            size -= 2; f = skia.Font(FONT, size)
        tw = f.measureText(s); w = tw + size * 1.2; h = size * 1.55
        c.save(); c.translate(W / 2, y - size * 0.35 + (1 - e) * 30); c.rotate(-1.5); sc = 0.94 + 0.06 * k; c.scale(sc, sc)
        r = skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h)
        c.drawRect(r.makeOffset(4, 8), P('#3a2a1a', int(45 * e), blur=10))
        c.drawRect(r, P('#f6e7b8', int(235 * e)))
        for i in range(0, int(w), 14):                       # gezackte Bandenden
            c.drawCircle(-w / 2, -h / 2 + (i % int(h)), 3, P('#f2ede2', int(255 * e)))
        c.drawString(s, -tw / 2, size * 0.36, f, P(INK_P, int(255 * e)))
        c.restore()
        return
    size = size * 0.92
    f = skia.Font(FONT, size)
    while f.measureText(s) > 860:
        size -= 2; f = skia.Font(FONT, size)
    tw = f.measureText(s)
    dot = size * 0.34
    w = tw + size * 1.35 + dot * 2.4
    h = size * 1.7
    c.save(); c.translate(W / 2, y - size * 0.35 + (1 - e) * 36)
    s_ = 0.92 + 0.08 * k; c.scale(s_, s_)
    r = skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h)
    glass(c, r, h / 2, alpha=int(205 * e), stroke_a=int(70 * e))
    dx = -w / 2 + size * 0.6 + dot
    c.drawCircle(dx, 0, dot * 1.9, P(color, int(90 * e), blur=dot))
    c.drawCircle(dx, 0, dot, P(color, int(255 * e)))
    c.drawString(s, dx + dot * 1.4 + size * 0.15, size * 0.36, f, P('#ffffff', int(255 * e)))
    c.restore()

# ---------------- FINN ----------------
FO = '#ff8c2b'   # orange
FOD = '#e06d12'
FB = '#2f6fd6'   # blue jacket
FBD = '#1f4fa3'
FY = '#ffc928'   # yellow bag

def finn_alt(c, x, y, s, t, mood='happy', arm_l=200, arm_r=-20, goggles=False, blink=True, lean=0.0, sit=False,
         hand_l_obj=None, hand_r_obj=None, look=(0, 0), bounce=True):
    """FINN bis 19.11.2026 (orange, Jacke, Umhängetasche) – nur noch als Archiv."""
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

# ---------------- FINN (neu seit 19.11.2026: violetter Tinten-Tropfen im gelben Hoodie, Sticker-Look) ----------------
# Farben: FV Körper, FYH Hoodie, FPK Akzent – hier zentral ändern.
FV, FYH, FPK = '#8a5cf6', '#ffc93a', '#ff5d8f'      # Körper, Hoodie, Akzent
FYD = '#f0a51c'                                   # Bündchen / Naht
FINK, FWH = '#1e1440', '#ffffff'
FLW, FRIM = 5, 13                                   # Linie, Sticker-Rand


def _finn_rr(x, y, w, h, r):
    p = skia.Path(); p.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), r, r)); return p


def _finn_body(R, shape):
    p = skia.Path()
    rect = skia.Rect.MakeLTRB(-R, -R * 1.05, R, R * 1.05)
    if shape == 'kugel':
        p.addOval(rect)
    else:
        rr = skia.RRect()
        rr.setRectRadii(rect, [skia.Point(R, R * 1.04), skia.Point(R, R * 1.04), skia.Point(R * 0.84, R * 0.8), skia.Point(R * 0.84, R * 0.8)])
        p.addRRect(rr)
    return p


def _finn_top(kind):
    """Gibt [(path, farbe)] für das Markenzeichen auf dem Kopf zurück."""
    out = []
    if kind == 'locke':
        p = skia.Path(); p.moveTo(-30, -110); p.cubicTo(-34, -150, -6, -176, 34, -164)
        p.cubicTo(12, -156, 8, -136, 24, -108); p.close(); out.append((p, FV))
    elif kind == 'muetze':
        d = skia.Path(); d.moveTo(-108, -70); d.cubicTo(-104, -170, 104, -170, 108, -70); d.close(); out.append((d, FPK))
        out.append((_finn_rr(-114, -92, 228, 32, 15), FWH))
        b = skia.Path(); b.addCircle(0, -150, 15); out.append((b, FWH))
    elif kind == 'antenne':
        out.append((_finn_rr(-4, -156, 8, 40, 4), FINK))
        b = skia.Path(); b.addCircle(0, -160, 13); out.append((b, FYH))
    return out


def finn(c, x, y, s, t, mood='happy', arm_l=200, arm_r=-20, goggles=False, blink=True, lean=0.0, sit=False,
         hand_l_obj=None, hand_r_obj=None, look=(0, 0), bounce=True, top='locke', shape='drop', talk=None):
    c.save(); c.translate(x, y); c.rotate(lean); c.scale(s, s)
    by = math.sin(t * 4.0) * 4 if bounce else 0
    R = 120
    body = _finn_body(R, shape)
    tops = _finn_top(top)

    # ---- Beine und Schuhe ----
    low, front = [], []
    for sx in (-1, 1):
        if sit:
            front.append(_finn_rr(sx * 46 - 34, R - 28, 68, 50, 24))
        else:
            low.append((_finn_rr(sx * 48 - 24, R - 16 + by * 0.3, 48, 62, 24), FV))
            low.append((_finn_rr(sx * 48 - 38 + sx * 5, R + 36 + by * 0.3, 80, 32, 16), FWH))

    # ---- Arme (gleiche Geometrie wie bisher: Hand bleibt am selben Punkt) ----
    arms = []
    for ang, side, obj in ((arm_l, -1, hand_l_obj), (arm_r, 1, hand_r_obj)):
        a = math.radians(ang); sx0, sy0, Ln = side * 98, 25 + by, 95
        arms.append((sx0, sy0, a, Ln, obj))

    def arm_shape(paint_line, paint_fill, grow):
        for sx0, sy0, a, Ln, _ in arms:
            ca, sa = math.cos(a), math.sin(a)
            paint_line.setStrokeWidth(36 + grow * 2)
            c.drawLine(sx0, sy0, sx0 + ca * Ln, sy0 + sa * Ln, paint_line)
            c.drawCircle(sx0 + ca * (Ln + 18), sy0 + sa * (Ln + 18), 24 + grow, paint_fill)

    def silhouette(col, grow, blur=None):
        ps, pf = P(col, stroke=grow * 2, blur=blur), P(col, blur=blur)
        for p in [q for q, _ in low] + front:
            c.drawPath(p, ps); c.drawPath(p, pf)
        if col != FINK and not sit:
            c.drawRect(skia.Rect.MakeLTRB(-48, R - 10, 48, R + 60 + by * 0.3), pf)
        c.save(); c.translate(0, by)
        for p in [body] + [q for q, _ in tops]:
            c.drawPath(p, ps); c.drawPath(p, pf)
        c.restore()
        arm_shape(P(col, stroke=1, blur=blur), pf, grow)

    # Bodenschatten + Sticker (Schatten, weißer Rand, feine Linie)
    c.drawOval(skia.Rect.MakeXYWH(-92, R + (12 if sit else 48), 184, 26), P('#000000', 40, blur=8))
    c.saveLayerAlpha(skia.Rect.MakeLTRB(-280, -240, 280, 280), 52); c.translate(0, 7); silhouette('#000000', FLW + FRIM, blur=4.5); c.restore()   # Sticker-Schatten
    silhouette(FWH, FLW + FRIM)
    silhouette(FINK, FLW)

    # ---- Beine / Schuhe füllen ----
    for p, col in low:
        c.drawPath(p, P(col))
        if col == FWH:
            b = p.getBounds()
            c.save(); c.clipPath(p, skia.ClipOp.kIntersect, True)
            c.drawRect(skia.Rect.MakeLTRB(b.left(), b.bottom() - 10, b.right(), b.bottom()), P(FPK)); c.restore()

    c.save(); c.translate(0, by)
    # ---- Markenzeichen ----
    for p, col in tops:
        c.drawPath(p, P(FINK, stroke=FLW * 2)) if col != FV else None
        c.drawPath(p, P(col))
    # ---- Körper ----
    c.drawPath(body, P(FV))
    c.save(); c.clipPath(body, skia.ClipOp.kIntersect, True)
    ny, nd = 6, 50                                     # Ausschnitt: Höhe an der Seite, Tiefe in der Mitte
    hood = skia.Path(); hood.moveTo(-R, ny); hood.cubicTo(-58, ny + nd, 58, ny + nd, R, ny)
    hood.lineTo(R, R * 1.1); hood.lineTo(-R, R * 1.1); hood.close()
    c.drawPath(hood, P(FYH))
    c.drawRect(skia.Rect.MakeLTRB(-R, R * 1.05 - 20, R, R * 1.1), P(FYD))               # Saum
    rim = skia.Path(); rim.moveTo(-R, ny); rim.cubicTo(-58, ny + nd, 58, ny + nd, R, ny)
    c.drawPath(rim, P(FINK, stroke=22, cap=False)); c.drawPath(rim, P(mixc(FYH, FWH, 0.45), stroke=14, cap=False))   # Kragen
    pk = skia.Path(); pk.moveTo(-50, 106); pk.lineTo(-38, 76); pk.lineTo(38, 76); pk.lineTo(50, 106)
    c.drawPath(pk, P(FYD, stroke=6))                                                    # Bauchtasche
    for sx in (-1, 1):                                                                 # Kordeln
        c.drawLine(sx * 18, ny + 40, sx * 22, ny + 78, P(FINK, stroke=9)); c.drawLine(sx * 18, ny + 40, sx * 22, ny + 78, P(FWH, stroke=5))
        c.drawCircle(sx * 22, ny + 82, 6.5, P(FINK)); c.drawCircle(sx * 22, ny + 82, 4, P(FPK))
    c.drawOval(skia.Rect.MakeXYWH(R * 0.34, -R * 1.3, R * 1.6, R * 2.8), P(FINK, 30))   # Schattenseite (flach)
    c.drawOval(skia.Rect.MakeXYWH(-R + 26, -R * 0.86, 54, 30), P(FWH, 70))              # Glanz
    c.restore()

    # ---- Gesicht ----
    closed = blink and (t % 3.3) < 0.12
    lx, ly = look[0] * 7, look[1] * 5
    c.save(); c.clipPath(body, skia.ClipOp.kIntersect, True)
    ew, eh, ex, ey = (44, 72, 43, -46) if mood == 'shock' else (38, 64, 42, -50)
    for sx in (-1, 1):
        cx, cy = sx * ex + lx, ey + ly
        if mood == 'laugh':
            p = skia.Path(); p.moveTo(cx - 22, cy + 8); p.cubicTo(cx - 12, cy - 20, cx + 12, cy - 20, cx + 22, cy + 8)
            c.drawPath(p, P(FINK, stroke=10)); continue
        if closed:
            c.drawLine(cx - 20, cy + 4, cx + 20, cy + 4, P(FINK, stroke=9)); continue
        r = skia.Rect.MakeXYWH(cx - ew / 2, cy - eh / 2, ew, eh)
        if mood == 'tired':                              # schwere Lider: nur die untere Augenhälfte
            c.save(); c.clipRect(skia.Rect.MakeLTRB(r.left() - 2, cy - 2, r.right() + 2, r.bottom() + 2), skia.ClipOp.kIntersect, True)
            c.drawOval(r, P(FINK)); c.restore()
            c.drawCircle(cx - 6, cy + 10, 5, P(FWH, 220))
            c.drawLine(r.left() - 4, cy - 2, r.right() + 4, cy - 2, P(FINK, stroke=7)); continue
        c.drawOval(r, P(FINK))
        c.drawOval(skia.Rect.MakeXYWH(cx - 11 + look[0] * 3, cy - eh / 2 + 9 + look[1] * 3, 15, 20), P(FWH))
        c.drawCircle(cx + 8, cy + eh / 2 - 13, 4.5, P(FWH, 210))
    if mood == 'shock':
        for sx in (-1, 1):
            p = skia.Path(); p.moveTo(sx * ex - 15 + lx, -93 + ly); p.quadTo(sx * ex + lx, -105 + ly, sx * ex + 15 + lx, -93 + ly); c.drawPath(p, P(FINK, stroke=7))
    elif mood == 'puzzled':
        c.drawLine(-60 + lx, -91 + ly, -26 + lx, -89 + ly, P(FINK, stroke=7)); c.drawLine(26 + lx, -90 + ly, 54 + lx, -96 + ly, P(FINK, stroke=7))
    # Mund (talk = Mundöffnung 0..1 beim Sprechen, kommt aus der Lautstärke der Stimme – siehe lib/kino.py)
    if talk is not None and talk >= 0.12 and mood != 'laugh':
        mw, mh = 30 + 12 * talk, 10 + 30 * talk
        mo = skia.Rect.MakeXYWH(-mw / 2, 5 - mh * 0.35, mw, mh)
        c.drawOval(mo, P('#3b1030'))
        if talk > 0.45:
            mp = skia.Path(); mp.addOval(mo)
            c.save(); c.clipPath(mp, skia.ClipOp.kIntersect, True)
            c.drawOval(skia.Rect.MakeXYWH(-mw * 0.34, 5 + mh * 0.3, mw * 0.68, mh * 0.6), P(FPK)); c.restore()
    elif mood == 'shock':
        c.drawOval(skia.Rect.MakeXYWH(-14, -6, 28, 34), P('#3b1030'))
    elif mood == 'laugh':
        p = skia.Path(); p.moveTo(-28, -8); p.cubicTo(-24, 34, 24, 34, 28, -8); p.close()
        c.drawPath(p, P('#3b1030'))
        c.save(); c.clipPath(p, skia.ClipOp.kIntersect, True); c.drawOval(skia.Rect.MakeXYWH(-16, 10, 32, 22), P(FPK)); c.restore()
    elif mood == 'puzzled':
        p = skia.Path(); p.moveTo(-18, 6); p.cubicTo(-8, -4, 6, 14, 20, 2); c.drawPath(p, P(FINK, stroke=7))
    elif mood == 'tired':
        c.drawOval(skia.Rect.MakeXYWH(-15, -2, 30, 22), P('#3b1030'))
    else:
        p = skia.Path(); p.moveTo(-20, -4); p.cubicTo(-9, 15, 9, 15, 20, -4); c.drawPath(p, P(FINK, stroke=7))
    for sx in (-1, 1):
        c.drawOval(skia.Rect.MakeXYWH(sx * 78 - 16, -14, 32, 16), P(FPK, 120))
    c.restore()
    if goggles:
        c.drawLine(-118, -50, 118, -50, P('#2b2f3a', stroke=14))
        for sx in (-1, 1):
            g = skia.Rect.MakeXYWH(sx * 43 - 44, -98, 88, 98)
            c.drawRoundRect(g, 36, 36, P('#bfeaff', 80)); c.drawRoundRect(g, 36, 36, P('#2b2f3a', stroke=11))
    c.restore()
    for p in front:                                   # Schuhsohlen beim Sitzen
        b = p.getBounds(); c.drawPath(p, P(FWH))
        c.drawRoundRect(skia.Rect.MakeLTRB(b.left() + 11, b.top() + 11, b.right() - 11, b.bottom() - 11), 13, 13, P(FPK))

    # ---- Arme ----
    for sx0, sy0, a, Ln, obj in arms:
        ca, sa = math.cos(a), math.sin(a)
        c.drawLine(sx0, sy0, sx0 + ca * Ln, sy0 + sa * Ln, P(FINK, stroke=36 + FLW * 2))
        c.drawLine(sx0, sy0, sx0 + ca * Ln, sy0 + sa * Ln, P(FYH, stroke=36))
        c.drawLine(sx0 + ca * Ln * 0.74, sy0 + sa * Ln * 0.74, sx0 + ca * Ln * 0.96, sy0 + sa * Ln * 0.96, P(FYD, stroke=36, cap=False))
        hx, hy = sx0 + ca * (Ln + 18), sy0 + sa * (Ln + 18)
        c.drawCircle(hx, hy, 24 + FLW, P(FINK)); c.drawCircle(hx, hy, 24, P(FV))
        if obj: obj(hx, hy, a)
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


# ======================================================================================
# Bausteine „Abschauen von Top-Shorts“ (18.11.2026): Zähler, Schlüsselwort-Stempel,
# Durchstreichen, Balkendiagramm mit FINN, Entweder-oder-Karten.
# Alle funktionieren in jedem Look; im Papier-Look sehen sie aus wie mit Tinte/Filzstift gemacht.
# ======================================================================================
WORDS_ALL = []      # setzt pipeline.py: alle Wörter mit Zeiten (Sekunden, Gesamtvideo)
STARTS = []         # setzt pipeline.py: Startzeit jeder Szene im Gesamtvideo

def _wnorm(s):
    return ''.join(ch for ch in s.lower() if ch.isalnum() or ch in 'äöüß')

def word_t(scene, text, nth=0, default=None):
    """Zeitpunkt (Sekunden ab Szenenbeginn), an dem ein Wort in dieser Szene gesprochen wird –
    damit Stempel/Zähler/Durchstreichen genau auf den Ton fallen. text = Wortanfang, z. B. 'schlimm'."""
    if not STARTS or scene >= len(STARTS):
        return default
    s0 = STARTS[scene]; s1 = STARTS[scene + 1] if scene + 1 < len(STARTS) else 1e9
    key = _wnorm(text); n = 0
    for w in WORDS_ALL:
        if s0 - 0.05 <= w['start'] < s1 and _wnorm(w['text']).startswith(key):
            if n == nth:
                return max(0.0, w['start'] - s0)
            n += 1
    return default

def _shown_from(t, t0):
    """Szene 1: alles, was in den ersten 0,6 s starten soll, ist schon ab Bild 1 sichtbar (Cover)."""
    return 1e9 if (SCENE == 0 and t0 <= 0.6) else (t - t0)

def _ink(): return BP_INK if globals().get('BP_ON') else (INK_P if PAPER else '#ffffff')

def _fmt_num(v, dec=0):
    s = f"{v:,.{dec}f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    return s

def draw_counter(c, t, t0, v0, v1, x=W / 2, y=760, size=130, dur=1.6, label='', suffix='', dec=0):
    """ZÄHLER-EFFEKT: Zahl läuft im Bild von v0 bis v1 hoch (z. B. Alter 0 -> 392 Jahre).
    Startet bei t0 (am besten word_t(...) der Zahl), endet nach dur Sekunden mit Marker-Strich."""
    u = _shown_from(t, t0)
    if u < 0:
        return
    if u < 1e8:
        sfx('count', (round(t0, 2), round(dur, 2)), t0); sfx('thud', ('cnt', round(t0, 2)), t0 + dur)
    k = clamp(u / dur); e = ease_out(k)
    v = v0 + (v1 - v0) * e
    txt = _fmt_num(v, dec) + suffix
    fin = _fmt_num(v1, dec) + suffix
    fb = skia.Font(FONT_B, size)
    while fb.measureText(fin) > 820:
        size -= 4; fb = skia.Font(FONT_B, size)
    fl = skia.Font(FONT, size * 0.3)
    w = max(fb.measureText(fin), fl.measureText(label)) + size * 0.9
    h = size * (1.35 + (0.4 if label else 0))
    ap = ease_out(clamp(u / 0.3))
    c.save(); c.translate(0, (1 - ap) * 30)
    r = skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h)
    if PAPER:
        paper_card(c, r, -1.5, tape_top=True)
    else:
        glass(c, r, 36, alpha=int(200 * ap))
    c.save(); c.translate(x, y); c.rotate(-1.5 if PAPER else 0)
    ny = size * 0.36 + (size * 0.2 if label else 0)
    if label:
        c.drawString(label, -fl.measureText(label) / 2, -h / 2 + size * 0.42, fl, P('#5a4e44' if PAPER else '#ffffff', int(230 * ap)))
    if k >= 1:
        mu = ease_out(clamp((u - dur) / 0.3))
        tw = fb.measureText(txt)
        marker_swipe(c, -tw / 2, ny - size * 0.62, tw, size * 0.6, MARKER if PAPER else ACCENT, u=mu, a=150, seed=11)
    tw = fb.measureText(txt)
    if not PAPER:
        c.drawString(txt, -tw / 2, ny, fb, P(INK, int(255 * ap), stroke=size * 0.12))
    c.drawString(txt, -tw / 2, ny, fb, P(INK_P if PAPER else _ink(), int(255 * ap)))   # Zahl steht auf heller Papierkarte -> immer dunkel (auch auf der Blaupause)
    c.restore(); c.restore()

def word_stamp(c, word, t, t0, x=W / 2, y=760, size=150, hold=1.1, angle=-6, color=None):
    """SCHLÜSSELWORT-STEMPEL: ein Wort knallt groß ins Bild (wie ein roter Stempel), hält ~1 s, verblasst.
    t0 = word_t(szene, 'wort') -> sitzt genau auf dem gesprochenen Wort. Sparsam: 1–3 pro Video."""
    u = _shown_from(t, t0)
    if u < 0 or (u > hold + 0.3 and u < 1e8):
        return
    if u < 1e8: sfx('thud', ('stamp', word, round(t0, 2)), t0)
    sc = 1.35 - 0.35 * ease_out(clamp(u / 0.14))
    a = clamp(u / 0.06) * (1 - clamp((u - hold) / 0.3)) if u < 1e8 else 1.0
    col_ = color or HOT
    f = skia.Font(FONT_B, size)
    while f.measureText(word) > 820:
        size -= 4; f = skia.Font(FONT_B, size)
    tw = f.measureText(word)
    x = safe_x(x, tw + size * 0.75, y - size * 1.05, y + size * 0.4)   # sicherer Bereich
    c.save(); c.translate(x, y); c.rotate(angle); c.scale(sc, sc)
    al = int(235 * a)
    r = skia.Rect.MakeXYWH(-tw / 2 - size * 0.3, -size * 0.95, tw + size * 0.6, size * 1.25)
    if PAPER:
        c.drawRect(r, P('#fffdf7', int(120 * a)))
        pts = [(r.left(), r.top()), (r.right(), r.top()), (r.right(), r.bottom()), (r.left(), r.bottom()), (r.left(), r.top())]
        c.drawPath(rough_path(pts, seed=len(word), amp=4), P(col_, al, stroke=size * 0.08))
        q = P(col_, al); q.setBlendMode(skia.BlendMode.kMultiply)
        c.drawString(word, -tw / 2, 0, f, q)
    else:
        c.drawString(word, -tw / 2, 0, f, P(INK, al, stroke=size * 0.12))
        c.drawString(word, -tw / 2, 0, f, P(col_, al))
    c.restore()

def strike(c, x0, y0, x1, y1, t, t0, dur=0.3, color=None, width=12, seed=0):
    """DURCHSTREICHEN: roter Filzstift-Strich von (x0,y0) nach (x1,y1), wird in dur Sekunden gezogen."""
    u = ease_out(clamp(_shown_from(t, t0) / dur))
    if u <= 0:
        return
    if _shown_from(t, t0) < 1e8: sfx('swipe', round(t0, 2), t0)
    n = 14
    pts = [(x0 + (x1 - x0) * i / n * u, y0 + (y1 - y0) * i / n * u) for i in range(n + 1)]
    c.drawPath(rough_path(pts, seed=seed, amp=width * 0.25), P(color or HOT, 240, stroke=width))

def strike_text(c, s, x, y, size, t, t0, dur=0.3, fill=None, color=None):
    """Text zeigen und ab t0 durchstreichen (Mythen! z. B. '5-Sekunden-Regel')."""
    f = skia.Font(FONT_B, size); tw = f.measureText(s)
    if PAPER:
        bp = globals().get('BP_ON')
        c.drawString(s, x - tw / 2, y, f, P(BP_BG2 if bp else '#fffdf7', 220, stroke=size * 0.2))
        c.drawString(s, x - tw / 2, y, f, P(fill or (BP_INK if bp else INK_P)))
    else:
        draw_text_c(c, s, x, y, size, fill=fill or '#ffffff', outline=INK)
    strike(c, x - tw / 2 - 16, y - size * 0.22, x + tw / 2 + 16, y - size * 0.42, t, t0, dur, color, width=size * 0.13, seed=len(s))

def draw_bars(c, values, labels, x, y, w, h, k=1.0, colors=None, unit='', dec=0):
    """BALKENDIAGRAMM (wächst mit k = 0..1). (x, y) = linke untere Ecke der Grundlinie, w/h = Fläche.
    Gibt die Oberkanten [(mitte_x, oben_y), ...] zurück -> FINN mit finn_on() auf einen Balken stellen."""
    hi = safe_right(y - h - 60, y + 60, pad=24)                     # sicherer Bereich (Like-Spalte rechts)
    if x + w + 20 > hi:
        x = max(SAFE_LEFT + 20, hi - w - 20); w = min(w, hi - 20 - x)
    n = len(values); vmax = max(values) or 1
    slot = w / n; bw = slot * 0.6
    colors = colors or ['#ffb27a', '#8fd3ff', '#b6f36b', '#ff9ac1', '#c9a8ff', '#ffe08a']
    tops = []
    base = rough_path([(x - 20, y), (x + w + 20, y)], seed=2, amp=2)
    c.drawPath(base, P(_ink(), stroke=6))
    fl = skia.Font(FONT, 38); fv = skia.Font(FONT_B, 44)
    for i, v in enumerate(values):
        kk = ease_out(clamp((k * (n + 1) - i) / 1.5)) if k < 1 else 1.0
        if 0 < kk and k < 1: sfx('pop', ('bar', str(labels[i]) if i < len(labels) else i, int(x) // 40))
        bh = h * v / vmax * kk
        cx = x + slot * (i + 0.5)
        r = skia.Rect.MakeXYWH(cx - bw / 2, y - bh, bw, bh)
        if bh > 1:
            c.drawRect(r, P(colors[i % len(colors)]))
            pts = [(r.left(), r.bottom()), (r.left(), r.top()), (r.right(), r.top()), (r.right(), r.bottom())]
            c.drawPath(rough_path(pts, seed=i + 5, amp=2.5), P(OUT if not PAPER else INK_P, stroke=6))
        if kk > 0.95:
            s = _fmt_num(v, dec) + unit
            c.drawString(s, cx - fv.measureText(s) / 2, y - bh - 18, fv, P(_ink()))
        lab = labels[i] if i < len(labels) else ''
        c.drawString(lab, cx - fl.measureText(lab) / 2, y + 52, fl, P(_ink()))
        tops.append((cx, y - bh))
    return tops

def finn_on(c, x, top_y, s, t, **kw):
    """FINN so hinstellen, dass er mit den Füßen auf top_y steht (z. B. auf einem Balken aus draw_bars)."""
    finn(c, x, top_y - 158 * s, s, t, **kw)

def choice_cards(c, a, b, t, t0=0.0, reveal=None, correct=0, y=930, size=54):
    """ENTWEDER-ODER: zwei Karten (A/B) gleiten nacheinander ein. Ab reveal wird die richtige
    abgehakt + markiert, die falsche durchgestrichen. Ideal als Hook (Szene 1) und für Quiz-Themen."""
    lo_, hi_ = SAFE_LEFT, safe_right(y - 160, y + 160)              # sicherer Bereich: Karten ggf. etwas kleiner
    kk_ = min(1.0, (hi_ - lo_) / 950); mid_ = (lo_ + hi_) / 2 if kk_ < 1 else W / 2
    for i, s in enumerate((a, b)):
        u = _shown_from(t, t0 + i * 0.25)
        if u < 0:
            continue
        if u < 1e8: sfx('pop', ('card', i, round(t0, 2)), t0 + i * 0.25)
        if reveal is not None and t >= reveal: sfx('ding', ('reveal', round(reveal, 2)), reveal)
        e = ease_out(clamp(u / 0.35)) if u < 1e8 else 1.0
        cx = mid_ + (-250 if i == 0 else 250) * kk_
        ang = -3 if i == 0 else 3
        f = skia.Font(FONT_B, size); sz = size
        while f.measureText(s) > 380:
            sz -= 2; f = skia.Font(FONT_B, sz)
        c.save(); c.translate(cx + (1 - e) * (-40 if i == 0 else 40), y); c.rotate(ang); c.scale(kk_, kk_)
        r = skia.Rect.MakeXYWH(-215, -150, 430, 300)
        if PAPER:
            paper_card(c, r, 0, tape_top=True)
        else:
            glass(c, r, 34, alpha=int(210 * e))
        badge = 'A' if i == 0 else 'B'
        c.drawCircle(0, -78, 40, P(HOT if i == 0 else CYAN if not PAPER else '#2f6fd6'))
        fb = skia.Font(FONT_B, 46); c.drawString(badge, -fb.measureText(badge) / 2, -62, fb, P('#ffffff'))
        tw = f.measureText(s)
        if reveal is not None and t >= reveal and i == correct:
            marker_swipe(c, -tw / 2, 40 - sz * 0.62, tw, sz * 0.62, MARKER if PAPER else ACCENT, u=ease_out(clamp((t - reveal) / 0.3)), a=170, seed=21)
        c.drawString(s, -tw / 2, 40, f, P(_ink()))
        if reveal is not None and t >= reveal:
            if i == correct:
                uu = ease_out(clamp((t - reveal) / 0.35))
                p = skia.Path(); p.moveTo(110, 70); p.lineTo(150, 110); p.lineTo(215, 30)
                m = skia.PathMeasure(p, False); seg = skia.Path(); m.getSegment(0, m.getLength() * uu, seg, True)
                c.drawPath(seg, P('#2fbf71', stroke=18))
            else:
                strike(c, -180, -120, 180, 120, t, reveal, 0.3, width=16, seed=9)
                strike(c, 180, -120, -180, 120, t, reveal + 0.12, 0.3, width=16, seed=10)
        c.restore()


# ======================================================================================
# SICHERER BEREICH (18.11.2026, Wunsch von Lukas): Rechts sitzen bei TikTok, Reels und Shorts
# Like/Kommentar/Teilen, unten Name und Caption, oben die Tabs. Dort darf KEIN Text stehen.
# Raster 1080x1920 (aus Lukas' Vorlage gemessen):
#   oben y < 119 · oben Mitte x 308–760, y 119–212 (Tabs) · links x < 44
#   rechts x > 1033 für y 119–956 · rechts x > 886 für y 956–1543 (Button-Spalte) · unten y > 1543
# ======================================================================================
SAFE_ZONES = [
    (0, 0, 1080, 119, 'oben (Statusleiste)'),
    (308, 119, 760, 212, 'oben Mitte (Tabs „Für dich“)'),
    (0, 0, 44, 1920, 'linker Rand'),
    (1033, 119, 1080, 956, 'rechter Rand'),
    (886, 956, 1080, 1543, 'rechts (Like/Kommentar/Teilen)'),
    (0, 1543, 1080, 1920, 'unten (Name/Caption)'),
]
SAFE_LEFT = 44 + 20

def safe_right(y0, y1=None, pad=20):
    """Rechte Grenze für Text, der von y0 bis y1 reicht (inkl. Abstand pad)."""
    y1 = y0 if y1 is None else y1
    lo, hi = min(y0, y1), max(y0, y1)
    r = 1033 if hi < 956 or lo > 1543 else 886
    return r - pad

def safe_x(cx, w, y0, y1, pad=20):
    """Mittelpunkt cx so verschieben, dass ein w breites Element (von y0 bis y1) im sicheren Bereich bleibt."""
    lo, hi = 44 + pad, safe_right(y0, y1, pad)
    if w >= hi - lo:
        return (lo + hi) / 2
    return min(max(cx, lo + w / 2), hi - w / 2)

# --- automatische Prüfung: jeder gezeichnete Text wird gegen die Sperrzonen geprüft ---------------
SAFE_CHECK = False
SAFE_HITS = []
_orig_drawString = skia.Canvas.drawString
_orig_drawTextBlob = skia.Canvas.drawTextBlob

def _safe_record(canvas, rect, text, paint):
    try:
        if paint is not None and paint.getAlphaf() < 0.3:
            return
        s = str(text).strip()
        if not s:
            return
        r = canvas.getTotalMatrix().mapRect(rect)
        for x0, y0, x1, y1, name in SAFE_ZONES:
            ox = min(r.right(), x1) - max(r.left(), x0); oy = min(r.bottom(), y1) - max(r.top(), y0)
            if ox > 6 and oy > 6:
                SAFE_HITS.append({'text': s, 'zone': name, 'rect': [round(r.left()), round(r.top()), round(r.right()), round(r.bottom())]})
    except Exception:
        pass

def _chk_drawString(self, text, x, y, font, paint, *a, **k):
    if SAFE_CHECK:
        sz = font.getSize()
        _safe_record(self, skia.Rect.MakeLTRB(x, y - sz * 0.74, x + font.measureText(text), y + sz * 0.2), text, paint)
    return _orig_drawString(self, text, x, y, font, paint, *a, **k)

def _chk_drawTextBlob(self, blob, x, y, paint, *a, **k):
    if SAFE_CHECK:
        b = blob.bounds()
        _safe_record(self, skia.Rect.MakeLTRB(x + b.left(), y + b.top(), x + b.right(), y + b.bottom()), '(Textblock)', paint)
    return _orig_drawTextBlob(self, blob, x, y, paint, *a, **k)

skia.Canvas.drawString = _chk_drawString
skia.Canvas.drawTextBlob = _chk_drawTextBlob

def safe_overlay(c, a=90):
    """Sperrzonen rot einblenden (nur für Prüfbilder)."""
    for x0, y0, x1, y1, _ in SAFE_ZONES:
        c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), P('#ff0000', a))


# ======================================================================================
# BLAUPAUSE (19.11.): „Jetzt schauen wir genauer hin“ – Stilwechsel für den Analyse-Teil
# Dunkelblaues Millimeterpapier, Linien in Hellblau/Weiß. Davor und danach normales Papier.
# Nutzung in episode.py:  L.blaupause(c)  statt  L.vgrad(...)  für 2–4 Szenen in der Mitte.
# Auf der Blaupause hell zeichnen: BP_INK (weiß-blau), BP_LINE, Akzent HOT (rot) / MARKER (orange).
# ======================================================================================
BP_BG1, BP_BG2 = '#16284d', '#0c1730'
BP_INK, BP_LINE, BP_DIM = '#eaf3ff', '#8fc1ff', '#4f78b8'
_BP_CACHE = {}

def _bp_image():
    if 'img' in _BP_CACHE:
        return _BP_CACHE['img']
    w, h = 540, 960
    s = skia.Surface(w, h); c = s.getCanvas()
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeRadial(skia.Point(w * 0.5, h * 0.42), h * 0.75, [col(BP_BG1), col(BP_BG2)]))
    c.drawRect(skia.Rect.MakeWH(w, h), p)
    for i, x in enumerate(range(0, w + 1, 20)):
        c.drawLine(x, 0, x, h, P(BP_LINE, 34 if i % 5 == 0 else 13, stroke=1.2 if i % 5 == 0 else 0.7))
    for i, y in enumerate(range(0, h + 1, 20)):
        c.drawLine(0, y, w, y, P(BP_LINE, 34 if i % 5 == 0 else 13, stroke=1.2 if i % 5 == 0 else 0.7))
    _BP_CACHE['img'] = s.makeImageSnapshot()
    return _BP_CACHE['img']

BP_ON = False   # wird pro Bild in pipeline.frame zurückgesetzt; blaupause() schaltet helle Schrift ein

def blaupause(c):
    """Hintergrund im Blaupausen-Stil (statt vgrad) – für den „Röntgen“-/Analyse-Teil eines Videos.
    Schaltet für dieses Bild helle Beschriftungen (draw_bars usw.) und helle Untertitel ein."""
    global BP_ON
    BP_ON = True
    c.drawRect(skia.Rect.MakeXYWH(-2000, -2000, W + 4000, H + 4000), P(BP_BG2))
    c.drawImageRect(_bp_image(), skia.Rect.MakeXYWH(-W * 0.04, -H * 0.04, W * 1.08, H * 1.08), _SAMP)

def neon_path(c, pts, k=1.0, color=BP_LINE, width=6, glow=True, dash=False):
    """Linie wie auf einer Blaupause, wird mit k (0..1) gezeichnet. pts = [(x,y), ...]."""
    if len(pts) < 2 or k <= 0:
        return
    seg = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    total = sum(seg) * clamp(k); p = skia.Path(); p.moveTo(*pts[0]); run = 0
    for i, sl in enumerate(seg):
        if run + sl >= total:
            f = (total - run) / sl if sl else 0
            p.lineTo(pts[i][0] + (pts[i + 1][0] - pts[i][0]) * f, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * f); break
        p.lineTo(*pts[i + 1]); run += sl
    if glow:
        g = P(color, 90, stroke=width * 3.2); g.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, width * 1.6))
        g.setStrokeCap(skia.Paint.kRound_Cap); c.drawPath(p, g)
    q = P(color, 255, stroke=width); q.setStrokeCap(skia.Paint.kRound_Cap); q.setStrokeJoin(skia.Paint.kRound_Join)
    if dash:
        q.setPathEffect(skia.DashPathEffect.Make([width * 3, width * 2.2], 0))
    c.drawPath(p, q)

def akten_label(c, text, x, y, t=10, t0=0, size=30, dark=None):
    """Kleines Etikett mit Rahmen (Großbuchstaben, gesperrt), z. B. „BBC · 2023“ als Quellen-Marke
    oder „AKTE · GTA 6“. dark=True für Blaupause (heller Rahmen), sonst Tinte auf Papier. x = Mitte."""
    u = _shown_from(t, t0)
    if u < 0:
        return
    if u < 1e8: sfx('type', (text, round(t0, 2)), t0)
    e = ease_out(clamp(u / 0.3)) if u < 1e8 else 1.0
    dark = (not PAPER) if dark is None else dark
    s = text.upper(); f = skia.Font(FONT_B, size); sp = size * 0.12
    tw = sum(f.measureText(ch) for ch in s) + sp * (len(s) - 1)
    w, h = tw + size * 1.0, size * 1.55
    x = safe_x(x, w, y - h / 2, y + h / 2)
    fg = BP_INK if dark else INK_P
    c.save(); c.translate(x, y + (1 - e) * 14)
    r = skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h)
    c.drawRect(r, P(BP_BG1 if dark else '#fffdf7', int(235 * e)))
    c.drawRect(r, P(fg, int(255 * e), stroke=3))
    xx = -tw / 2
    for ch in s:
        c.drawString(ch, xx, size * 0.36, f, P(fg, int(255 * e))); xx += f.measureText(ch) + sp
    c.restore()
