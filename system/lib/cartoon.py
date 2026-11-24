"""LOOK „FINN-Cartoon" (24.11.2026, Wahl von Lukas).

Heller, warmer Hintergrund, alles im Sticker-Stil wie FINN: kräftige dunkle Umrisse, flache Farben,
versetzter harter Schatten. Eine feste Palette (Violett, Gelb, Dunkelblau-Tinte, Creme) statt wechselnder Neonfarben.
Wenig Text: pro Einstellung höchstens EINE Überschrift-Karte, dazu die Untertitel unten.
FINN ist in (fast) jeder Einstellung im Bild und reagiert (zeigt, staunt, lacht).

Einschalten in episode.py:   EDIT = 2   und   LOOK = 'cartoon'
pipeline.py setzt dann edit2.CARTOON = True: Bühne, Hook, Untertitel, Fortschritt und impact() zeichnen im Cartoon-Stil,
Themenzeile und Farbkorrektur entfallen.
"""
import math
import render as L
from render import skia, W, H, P, clamp, ease_out, mixc

# ---- Palette ----
CREAM = '#fff6e5'
CREAM2 = '#ffe9be'
INK = '#1e1440'
VIO = '#8a5cf6'
VIO_L = '#efe6ff'
YEL = '#ffc93a'
YEL_D = '#f0a51c'
PINK = '#ff5d8f'
RED = '#ef4444'
GREEN = '#34d399'
BLUE = '#4f8cff'
WHITE = '#ffffff'
GREY = '#d9d4e6'

OUT = 10          # Umrissstärke
SHADOW = 14       # versetzter Schatten

SUB_Y = 1490      # Untertitel-Grundlinie (unter den Motiven, über Name/Caption)

TINTS = {         # Themenfarbe -> zarte Hintergrund-Flecken
    'vio': (VIO_L, CREAM2), 'yel': (CREAM2, VIO_L), 'red': ('#ffe0d9', CREAM2), 'green': ('#dcf7ea', CREAM2),
    'blue': ('#e0ebff', CREAM2),
}


def bg(c, tint='vio', drift=0.0):
    """Creme-Hintergrund mit zwei großen, weichen Farbflecken (bewegen sich kaum)."""
    a, b = TINTS.get(tint, TINTS['vio'])
    c.drawRect(skia.Rect.MakeXYWH(-2000, -2000, W + 4000, H + 4000), P(CREAM))
    T = L.NOW
    c.drawCircle(W * 0.88 + math.sin(T * 0.3) * 12, H * 0.10 + drift, 430, P(a))
    c.drawCircle(W * 0.05 + math.cos(T * 0.25) * 12, H * 0.80 - drift, 560, P(b))


def _rr(x, y, w, h, r):
    return skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), r, r)


def box(c, x, y, w, h, fill=WHITE, r=40, out=OUT, shadow=SHADOW, a=255):
    """Sticker-Rechteck: harter Schatten, Füllung, dunkler Umriss."""
    if shadow:
        c.drawRRect(_rr(x + shadow, y + shadow, w, h, r), P(INK, a))
    c.drawRRect(_rr(x, y, w, h, r), P(fill, a))
    if out:
        c.drawRRect(_rr(x, y, w, h, r), P(INK, a, stroke=out))


def circle(c, x, y, r, fill=WHITE, out=OUT, shadow=SHADOW * 0.8, a=255):
    if shadow:
        c.drawCircle(x + shadow, y + shadow, r, P(INK, a))
    c.drawCircle(x, y, r, P(fill, a))
    if out:
        c.drawCircle(x, y, r, P(INK, a, stroke=out))


def path(c, p, fill=WHITE, out=OUT, shadow=SHADOW, a=255):
    if shadow:
        c.save(); c.translate(shadow, shadow); c.drawPath(p, P(INK, a)); c.restore()
    c.drawPath(p, P(fill, a))
    if out:
        c.drawPath(p, P(INK, a, stroke=out))


def _font(size, bold=True):
    return skia.Font(L.FONT_B if bold else L.FONT, size)


def fit(s, size, maxw, bold=True):
    f = _font(size, bold)
    while f.measureText(s) > maxw and size > 20:
        size -= 2; f = _font(size, bold)
    return f, size


def text(c, s, x, y, size, color=INK, a=255, maxw=900, k=1.0, outline=None, bold=True):
    """Schrift mittig bei x, Grundlinie y. outline = Farbe einer dicken Kontur (z. B. INK bei weißer Schrift)."""
    if k <= 0 or not s:
        return 0
    f, size = fit(s, size, maxw, bold)
    w = f.measureText(s)
    sc = 1.0 + 0.18 * (1 - ease_out(clamp(k)))
    al = int(a * clamp(k * 1.6))
    c.save(); c.translate(x, y - size * 0.34); c.scale(sc, sc); c.translate(-x, -(y - size * 0.34))
    if outline:
        c.drawString(s, x - w / 2 + 6, y + 7, f, P(INK, al, stroke=min(size * 0.2, 22)))
        c.drawString(s, x - w / 2, y, f, P(outline, al, stroke=min(size * 0.2, 22)))
    c.drawString(s, x - w / 2, y, f, P(color, al))
    c.restore()
    return w


def card(c, lines, x=W / 2, y=300, colors=None, size=110, k=1.0, fill=WHITE, tail=None, maxw=860, pad=46):
    """Überschrift-Karte (Sprechblase): weiße Karte mit Umriss + Schatten, 1–2 Zeilen.
    tail = (x, y) Spitze der Sprechblase (zeigt auf FINN) oder None. Gibt das Rechteck zurück."""
    if k <= 0:
        return None
    if isinstance(lines, str):
        lines = [lines]
    colors = colors or [INK, VIO]
    sz = size
    for ln in lines:
        _, s2 = fit(ln, sz, maxw); sz = min(sz, s2)
    f = _font(sz)
    tw = max(f.measureText(ln) for ln in lines)
    bw, bh = tw + pad * 2, sz * 1.12 * len(lines) + pad * 1.2
    sc = 0.7 + 0.3 * ease_out(clamp(k))
    al = int(255 * clamp(k * 2))
    c.save(); c.translate(x, y + bh / 2); c.scale(sc, sc); c.translate(-x, -(y + bh / 2))
    if tail:
        tx, ty = tail
        bx = clamp((tx - (x - bw / 2)) / bw, 0.18, 0.82) * bw + x - bw / 2
        tp = skia.Path(); tp.moveTo(bx - 46, y + bh - 6); tp.lineTo(tx, ty); tp.lineTo(bx + 46, y + bh - 6); tp.close()
        c.save(); c.translate(SHADOW, SHADOW); c.drawPath(tp, P(INK, al)); c.restore()
    box(c, x - bw / 2, y, bw, bh, fill, r=46, a=al)
    if tail:
        c.drawPath(tp, P(fill, al)); c.drawPath(tp, P(INK, al, stroke=OUT))
        c.drawLine(bx - 40, y + bh - 2, bx + 40, y + bh - 2, P(fill, al, stroke=OUT + 4, cap=False))
    yy = y + pad * 0.6 + sz * 0.86
    for i, ln in enumerate(lines):
        cl = colors[min(i, len(colors) - 1)]
        c.drawString(ln, x - f.measureText(ln) / 2, yy, f, P(cl, al))
        yy += sz * 1.12
    c.restore()
    return (x - bw / 2, y, bw, bh)


def chip(c, s, x, y, size=50, fill=YEL, txt=INK, k=1.0, angle=0.0):
    """Kleines Etikett/Wert-Pille im Sticker-Stil."""
    if k <= 0:
        return
    f = _font(size); w = f.measureText(s) + size * 0.9; h = size * 1.45
    sc = 0.6 + 0.4 * ease_out(clamp(k)); al = int(255 * clamp(k * 2))
    c.save(); c.translate(x, y); c.rotate(angle); c.scale(sc, sc)
    box(c, -w / 2, -h / 2, w, h, fill, r=h / 2, out=8, shadow=9, a=al)
    c.drawString(s, -f.measureText(s) / 2, size * 0.36, f, P(txt, al))
    c.restore()


def stamp(c, s, x, y, size, color, lt, t0, angle=-7, hold=None):
    """Schlagwort knallt als Sticker ins Bild (auf das gesprochene Wort)."""
    u = lt - t0
    if u < 0 or (hold is not None and u > hold):
        return
    L.sfx('thud', ('cstamp', s, round(t0, 2)))
    k = clamp(u / 0.14)
    c.save(); c.translate(x, y - size * 0.34); c.rotate(angle); c.translate(-x, -(y - size * 0.34))
    text(c, s, x, y, size, color, k=k, outline=WHITE)
    c.restore()


def strike(c, x0, y0, x1, y1, lt, t0, dur=0.25, color=RED, width=22):
    u = clamp((lt - t0) / dur)
    if u <= 0:
        return
    L.sfx('swipe', ('cstrike', round(x0), round(t0, 2)))
    k = ease_out(u)
    c.drawLine(x0, y0, x0 + (x1 - x0) * k, y0 + (y1 - y0) * k, P(INK, stroke=width + 10))
    c.drawLine(x0, y0, x0 + (x1 - x0) * k, y0 + (y1 - y0) * k, P(color, stroke=width))


def arrow(c, x0, y0, x1, y1, k=1.0, color=INK, width=14):
    if k <= 0:
        return
    x1 = x0 + (x1 - x0) * ease_out(clamp(k)); y1 = y0 + (y1 - y0) * ease_out(clamp(k))
    c.drawLine(x0, y0, x1, y1, P(color, stroke=width))
    a = math.atan2(y1 - y0, x1 - x0)
    for d in (2.5, -2.5):
        c.drawLine(x1, y1, x1 - 46 * math.cos(a + d * 0.2), y1 - 46 * math.sin(a + d * 0.2), P(color, stroke=width))


def finn(c, x, y, s, t, mood='happy', pose='wave', look=(0, 0), lean=0.0, hand_r_obj=None, hand_l_obj=None):
    """FINN mit fertigen Posen. pose: wave (beide Arme hoch), point_r / point_l (zeigt schräg nach oben rechts/links),
    shrug, think (Hand am Kinn), cheer, hold (hält etwas rechts). Aussehen bleibt wie in render.finn."""
    arms = {
        'wave': (215, -35), 'cheer': (230, -50), 'point_r': (120, -28), 'point_l': (208, 60),
        'shrug': (160, 20), 'think': (120, 210), 'hold': (120, -10), 'rest': (115, 65), 'stop': (120, -5),
    }.get(pose, (200, -20))
    wob = math.sin(t * 6.0) * 6 if pose in ('wave', 'cheer') else 0
    L.finn(c, x, y, s, t + 0.6, mood=mood, arm_l=arms[0] + wob, arm_r=arms[1] - wob, look=look, lean=lean,
           hand_r_obj=hand_r_obj, hand_l_obj=hand_l_obj)


# ---------------------------------------------------------------- Anbindung an pipeline.py / edit2.py
def hook(c, t, lines, colors=None, end=2.2):
    """Hook-Karte ab Bild 0 – oben, Sprechblase, bleibt bis HOOK_END."""
    import edit2 as E2
    if getattr(E2, 'KINO', None):          # FINN-Show: der Hook wird in der Szene selbst gesetzt (K.slam)
        return
    if t > end or not lines:
        return
    card(c, lines, W / 2, 240, colors=colors or [INK, VIO], size=118, k=1.0)


def progress(c, g):
    c.drawRect(skia.Rect.MakeXYWH(0, 0, W, 12), P(INK, 40))
    if g > 0:
        c.drawRect(skia.Rect.MakeXYWH(0, 0, W * min(1.0, g), 12), P(VIO))


def subs(c, T, WS, t_from=0.0, accent=YEL):
    """Untertitel: 1–3 Wörter, weiße Schrift mit dicker Tinten-Kontur, gesprochenes Schlüsselwort gelb. Unten über der Caption."""
    import edit2 as E2
    if getattr(E2, 'KINO', None):
        return E2.KINO.subs(c, T, WS, t_from)
    if T < t_from:
        return
    ch = E2._chunks(WS)
    idx = None
    for n, g in enumerate(ch):
        if T >= WS.WORDS[g[0]]['start'] - 0.06:
            idx = n
    if idx is None:
        return
    g = ch[idx]
    if WS.WORDS[g[0]]['start'] - 0.06 < t_from:
        return
    nxt = WS.WORDS[ch[idx + 1][0]]['start'] - 0.06 if idx + 1 < len(ch) else 1e9
    if T > min(nxt, WS.WORDS[g[-1]]['end'] + 0.7):
        return
    words = [WS.WORDS[k]['text'] for k in g]
    size = 92; f = _font(size); sp = size * 0.32
    wid = lambda: sum(f.measureText(s) for s in words) + sp * (len(words) - 1)
    while wid() > 580 and size > 40:
        size -= 2; f = _font(size); sp = size * 0.32
    tw = wid()
    u = clamp((T - WS.WORDS[g[0]]['start'] + 0.06) / 0.10)
    sc = 1.0 + 0.10 * (1 - ease_out(u))
    y = SUB_Y; cy = y - size * 0.36
    c.save(); c.translate(W / 2 + 20, cy); c.scale(sc, sc); c.translate(-(W / 2 + 20), -cy)
    x = W / 2 + 20 - tw / 2              # leicht links der Mitte: rechts unten liegt die Like-Spalte
    for k, s in zip(g, words):
        w_ = WS.WORDS[k]; ww = f.measureText(s)
        said = T >= w_['start'] - 0.05
        key = WS.strip(w_['text']).lower() in WS.HL
        c.drawString(s, x + 6, y + 7, f, P(INK, 255, stroke=min(size * 0.24, 22)))
        c.drawString(s, x, y, f, P(INK, 255, stroke=min(size * 0.24, 22)))
        c.drawString(s, x, y, f, P(accent if (key and said) else WHITE, 255 if said else 200))
        x += ww + sp
    c.restore()


def impact(c, lt, big, sub='', top='', color=VIO, key=None, size=230, tint='yel', fill=YEL):
    """Vollbild-Zahl als großes Preisschild."""
    bg(c, tint)
    L.sfx('thud', ('cimpact', key or big))
    k = clamp(lt / 0.16)
    f, sz = fit(big, size, 820)
    bw = f.measureText(big) + 120; bh = sz * 1.25 + (150 if sub else 60) + (90 if top else 0)
    x0, y0 = W / 2 - bw / 2, 330
    sc = 0.7 + 0.3 * ease_out(k)
    c.save(); c.translate(W / 2, y0 + bh / 2); c.scale(sc, sc); c.translate(-W / 2, -(y0 + bh / 2))
    box(c, x0, y0, bw, bh, fill, r=60)
    c.drawCircle(x0 + 60, y0 + 60, 22, P(CREAM)); c.drawCircle(x0 + 60, y0 + 60, 22, P(INK, stroke=8))
    yy = y0 + 40
    if top:
        text(c, top, W / 2, yy + 62, 60, INK); yy += 90
    text(c, big, W / 2, yy + sz * 0.95, sz, INK, maxw=820); yy += sz * 1.15
    if sub:
        text(c, sub, W / 2, yy + 70, 60, INK, maxw=bw - 80)
    c.restore()
