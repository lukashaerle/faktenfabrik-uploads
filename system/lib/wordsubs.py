"""Word-timed subtitles: every word appears exactly when it is spoken."""
import math
from render import skia, P, W
import render as L

WORDS, PAGES, PSTART, HL = [], [], [], set()

def strip(w):
    return w.strip('.,:;?!–"„“')

def init(words, para_idx, highlight, maxc=24):
    global WORDS, PAGES, PSTART, HL
    if getattr(L, 'MODERN', False) and maxc == 24:
        maxc = 20                                   # moderner Stil: größere Schrift, kürzere Zeilen
    WORDS = words
    HL = set(strip(h).lower() for h in highlight)
    pages = []
    bounds = list(para_idx) + [len(words)]
    for p in range(len(para_idx)):
        a, b = bounds[p], bounds[p + 1]
        lines, cur = [], []
        for k in range(a, b):
            w = words[k]['text']
            if cur and len(' '.join(words[j]['text'] for j in cur + [k])) > maxc:
                lines.append(cur); cur = []
                if len(lines) == 2:
                    pages.append(lines); lines = []
            cur.append(k)
            if w[-1] in '.?!:' and (len(lines) == 1 or len(' '.join(words[j]['text'] for j in cur)) > 14):
                lines.append(cur); cur = []; pages.append(lines); lines = []
        if cur: lines.append(cur)
        if lines: pages.append(lines)
    PAGES = [pg for pg in pages if pg]
    PSTART = [words[pg[0][0]]['start'] for pg in PAGES]

def draw_word_subs(c, T):
    if getattr(L, 'MODERN', False):
        return draw_word_subs_modern(c, T)
    idx = None
    for n, s in enumerate(PSTART):
        if T >= s - 0.08: idx = n
    if idx is None: return
    pg = PAGES[idx]
    last_end = WORDS[pg[-1][-1]]['end']
    nxt = PSTART[idx + 1] if idx + 1 < len(PSTART) else 1e9
    if T > min(nxt, last_end + 1.2): return
    size = 58
    f = skia.Font(L.FONT, size)
    def lw(ln, f):
        return sum(f.measureText(WORDS[k]['text']) for k in ln) + f.measureText(' ') * 1.35 * (len(ln) - 1)
    while max(lw(ln, f) for ln in pg) > 900:
        size -= 2; f = skia.Font(L.FONT, size)
    lh = size * 1.25
    wmax = max(lw(ln, f) for ln in pg)
    y = 1330  # oberhalb der TikTok-Bedienelemente (Caption, Buttons)
    sp = f.measureText(' ') * 1.35
    for ln in pg:
        x = W / 2 - lw(ln, f) / 2
        for k in ln:
            w = WORDS[k]; tw = f.measureText(w['text'])
            if T >= w['start'] - 0.04:
                active = w['start'] - 0.04 <= T <= w['end'] + 0.05
                pop = min(1.0, (T - w['start'] + 0.04) / 0.12)
                fill = '#ffd23f' if (strip(w['text']).lower() in HL or active) else '#ffffff'
                c.save(); cx, cy = x + tw / 2, y - size * 0.35; s = 0.9 + 0.1 * pop
                c.translate(cx, cy); c.scale(s, s); c.translate(-cx, -cy)
                c.drawString(w['text'], x, y, f, P('#0d0d0d', stroke=14))
                c.drawString(w['text'], x, y, f, P(fill))
                c.restore()
            x += tw + sp
        y += lh


# ---------------- moderner Untertitel-Stil (17.11.2026) ----------------
# Groß und fett (Poppins 900), jedes Wort erscheint genau beim Sprechen und gleitet weich hoch.
# Das gerade gesprochene Wort sitzt in einer Pille, die von Wort zu Wort gleitet:
# gelb für normale Wörter, rot mit weißer Schrift für Schlüsselwörter (HIGHLIGHT).
# Bereits gesagte Schlüsselwörter bleiben gelb. Weicher Schatten statt Kasten.

def _layout(pg, f, sp):
    """Wortpositionen (x, Zeile) einer Seite, zentriert."""
    pos = {}
    for li, ln in enumerate(pg):
        tot = sum(f.measureText(WORDS[k]['text']) for k in ln) + sp * (len(ln) - 1)
        x = W / 2 - tot / 2
        for k in ln:
            tw = f.measureText(WORDS[k]['text']); pos[k] = (x, li, tw); x += tw + sp
    return pos

def draw_word_subs_modern(c, T):
    if getattr(L, 'PAPER', False):
        return draw_word_subs_paper(c, T)
    if getattr(L, 'MINIMAL', False):
        return draw_word_subs_minimal(c, T)
    idx = None
    for n, s in enumerate(PSTART):
        if T >= s - 0.08: idx = n
    if idx is None: return
    pg = PAGES[idx]
    last_end = WORDS[pg[-1][-1]]['end']
    nxt = PSTART[idx + 1] if idx + 1 < len(PSTART) else 1e9
    end_t = min(nxt, last_end + 1.2)
    if T > end_t: return
    out = 1.0 if T < end_t - 0.12 or end_t == nxt else max(0.0, (end_t - T) / 0.12)
    size = 72
    f = skia.Font(L.FONT_B, size)
    sp = f.measureText(' ') * 1.45
    while max(sum(f.measureText(WORDS[k]['text']) for k in ln) + sp * (len(ln) - 1) for ln in pg) > 920:
        size -= 2; f = skia.Font(L.FONT_B, size); sp = f.measureText(' ') * 1.45
    lh = size * 1.22
    y0 = 1330
    pos = _layout(pg, f, sp)
    words = [k for ln in pg for k in ln]
    # aktives Wort (gesprochen gerade oder zuletzt) + weiche Pillen-Bewegung zum nächsten
    spoken = [k for k in words if T >= WORDS[k]['start'] - 0.04]
    if spoken:
        cur = spoken[-1]
        prev = spoken[-2] if len(spoken) > 1 else cur
        u = min(1.0, (T - WORDS[cur]['start'] + 0.04) / 0.09)
        u = 1 - (1 - u) ** 3
        if pos[prev][1] != pos[cur][1]:
            u = 1.0                                   # Zeilenwechsel: Pille springt nicht schräg
        px = lambda k: (pos[k][0], y0 + pos[k][1] * lh, pos[k][2])
        (x1, yy1, w1), (x2, yy2, w2) = px(prev), px(cur)
        bx, by, bw = x1 + (x2 - x1) * u, yy1 + (yy2 - yy1) * u, w1 + (w2 - w1) * u
        ishl = strip(WORDS[cur]['text']).lower() in HL
        speaking = T <= WORDS[cur]['end'] + 0.25
        if speaking and out > 0:
            padx, pady = size * 0.17, size * 0.16
            r = skia.Rect.MakeXYWH(bx - padx, by - size * 0.86 - pady * 0.4, bw + 2 * padx, size * 1.06 + pady)
            rr = skia.RRect.MakeRectXY(r, size * 0.24, size * 0.24)
            c.save(); cx, cy = r.centerX(), r.centerY(); c.translate(cx, cy); c.rotate(-2.0 if L.TILT else 0.0); c.translate(-cx, -cy)
            c.drawRRect(skia.RRect.MakeRectXY(r.makeOffset(0, 7), size * 0.24, size * 0.24), P('#000000', int(90 * out), blur=10))
            c.drawRRect(rr, P(L.HOT if ishl else L.ACCENT, int(255 * out)))
            c.restore()
    else:
        cur, speaking = None, False
    for k in words:
        w = WORDS[k]
        if T < w['start'] - 0.04:
            continue
        x, li, tw = pos[k]
        y = y0 + li * lh
        a = min(1.0, (T - w['start'] + 0.04) / 0.1)
        e = 1 - (1 - a) ** 3
        al = int(255 * e * out)
        dy = (1 - e) * 14
        ishl = strip(w['text']).lower() in HL
        active = (k == cur and speaking)
        if active:
            fill = '#ffffff' if ishl else L.INK
            c.drawString(w['text'], x, y + dy, f, P(fill, al))
            continue
        fill = (L.ACCENT if L.ACCENT != '#ffffff' else (L.HOT if L.HOT != '#26365e' else '#ffffff')) if ishl else '#ffffff'
        c.drawString(w['text'], x, y + dy + size * 0.06, f, P('#000000', int(al * 0.45), blur=size * 0.08))
        c.drawString(w['text'], x, y + dy, f, P(L.INK, al, stroke=size * 0.16))
        c.drawString(w['text'], x, y + dy, f, P(fill, al))


# ---------------- „Dynamic Minimalism“ (Trend 2026) ----------------
# Weiß, fett, dunkle Kontur + weicher Schatten, kurze Phrasen (max. 2 Zeilen à ~14 Zeichen),
# jedes Wort erscheint beim Sprechen mit kleinem Größen-Impuls. Keine Farbflächen, keine Zusatzfarben.
_MIN_PAGES = None

def _min_pages():
    global _MIN_PAGES
    if _MIN_PAGES is not None:
        return _MIN_PAGES
    pages = []
    for pg in PAGES:
        flat = [k for ln in pg for k in ln]
        cur, lines = [], []
        for k in flat:
            txt = ' '.join(WORDS[j]['text'] for j in cur + [k])
            if cur and len(txt) > 14:
                lines.append(cur); cur = []
                if len(lines) == 2:
                    pages.append(lines); lines = []
            cur.append(k)
            if WORDS[k]['text'][-1] in '.?!:':
                lines.append(cur); cur = []; pages.append(lines); lines = []
        if cur: lines.append(cur)
        if lines: pages.append(lines)
    _MIN_PAGES = [p for p in pages if p]
    return _MIN_PAGES

def draw_word_subs_minimal(c, T):
    pages = _min_pages()
    starts = [WORDS[p[0][0]]['start'] for p in pages]
    idx = None
    for n, s in enumerate(starts):
        if T >= s - 0.06: idx = n
    if idx is None: return
    pg = pages[idx]
    last_end = WORDS[pg[-1][-1]]['end']
    nxt = starts[idx + 1] if idx + 1 < len(starts) else 1e9
    if T > min(nxt, last_end + 1.0): return
    caps = getattr(L, 'CAPS', False)
    txt = lambda k: WORDS[k]['text'].upper() if caps else WORDS[k]['text']
    size = 92 if caps else 96
    f = skia.Font(L.FONT_B, size)
    sp = f.measureText(' ') * 1.5
    lwid = lambda ln, f, sp: sum(f.measureText(txt(k)) for k in ln) + sp * (len(ln) - 1)
    while max(lwid(ln, f, sp) for ln in pg) > 900:
        size -= 2; f = skia.Font(L.FONT_B, size); sp = f.measureText(' ') * 1.5
    lh = size * 1.12
    y0 = 1330 - (len(pg) - 1) * lh * 0.35
    for li, ln in enumerate(pg):
        x = W / 2 - lwid(ln, f, sp) / 2
        y = y0 + li * lh
        for k in ln:
            w = WORDS[k]; s_ = txt(k); tw = f.measureText(s_)
            if T >= w['start'] - 0.05:
                u = min(1.0, (T - w['start'] + 0.05) / 0.16)
                sc = 1.0 + 0.10 * math.sin(u * math.pi) if u < 1 else 1.0      # kleiner Impuls beim Erscheinen
                al = int(255 * min(1.0, u * 2.5))
                c.save(); cx, cy = x + tw / 2, y - size * 0.36
                c.translate(cx, cy); c.scale(sc, sc); c.translate(-cx, -cy)
                c.drawString(s_, x, y + size * 0.07, f, P('#000000', int(al * 0.5), blur=size * 0.09))
                if getattr(L, 'GLOW', None):
                    hot = u < 1 or T <= w['end'] + 0.1
                    c.drawString(s_, x, y, f, P(L.GLOW, int(al * (0.95 if hot else 0.55)), blur=size * (0.22 if hot else 0.16)))
                c.drawString(s_, x, y, f, P('#000000', al, stroke=size * 0.11))
                c.drawString(s_, x, y, f, P('#ffffff', al))
                c.restore()
            x += tw + sp


# ---------------- Papier & Marker ----------------
# Tinten-Schrift auf einem Papierstreifen; das gesprochene Wort bekommt einen Textmarker-Strich,
# der in 0,15 s von links nach rechts gezogen wird; Schlüsselwörter behalten ihren Marker und
# bekommen zusätzlich eine rote Unterstreichung wie mit Filzstift.
def draw_word_subs_paper(c, T):
    pages = _min_pages()
    starts = [WORDS[p[0][0]]['start'] for p in pages]
    idx = None
    for n, s in enumerate(starts):
        if T >= s - 0.06: idx = n
    if idx is None: return
    pg = pages[idx]
    last_end = WORDS[pg[-1][-1]]['end']
    nxt = starts[idx + 1] if idx + 1 < len(starts) else 1e9
    if T > min(nxt, last_end + 1.0): return
    size = 84
    f = skia.Font(L.FONT_B, size)
    sp = f.measureText(' ') * 1.1
    lwid = lambda ln: sum(f.measureText(WORDS[k]['text']) for k in ln) + sp * (len(ln) - 1)
    # Sicherer Bereich (Like-/Kommentar-Spalte rechts): Zeile max. von x 64 bis 862
    while max(lwid(ln) for ln in pg) > 790:
        size -= 2; f = skia.Font(L.FONT_B, size); sp = f.measureText(' ') * 1.1
    lh = size * 1.18
    y0 = 1330 - (len(pg) - 1) * lh * 0.35
    for li, ln in enumerate(pg):
        y = y0 + li * lh
        x = L.safe_x(W / 2, lwid(ln) + size * 0.3, y - size, y + size * 0.3) - lwid(ln) / 2
        for k in ln:
            w = WORDS[k]; s_ = w['text']; tw = f.measureText(s_)
            if T >= w['start'] - 0.05:
                ishl = strip(s_).lower() in HL
                u = min(1.0, (T - w['start'] + 0.05) / 0.15)
                speaking = T <= w['end'] + 0.15
                al = int(255 * min(1.0, u * 3))
                bp = getattr(L, 'BP_ON', False)                                   # Blaupause: helle Schrift, dunkler Hof
                c.drawString(s_, x, y, f, P(L.BP_BG2 if bp else '#fffdf7', int(al * 0.85), stroke=size * 0.2))
                hot = speaking or ishl
                if hot and bp:                                                    # Multiply wirkt auf Dunkel nicht -> deckender Marker
                    c.drawRoundRect(skia.Rect.MakeLTRB(x - size * 0.08, y - size * 0.8, x + (tw + size * 0.16) * min(1.0, u * 1.5) - size * 0.08, y + size * 0.2), size * 0.12, size * 0.12, P(L.MARKER, 255))
                elif hot:
                    L.marker_swipe(c, x, y - size * 0.62, tw, size * 0.62, L.MARKER, u=u, a=200 if ishl else 170, seed=k)
                c.drawString(s_, x, y, f, P(L.INK_P if (not bp or hot) else L.BP_INK, al))
                if ishl:
                    uu = min(1.0, max(0.0, (T - w['start'] - 0.1) / 0.25))
                    if uu > 0:
                        pts = [(x - 4 + (tw + 8) * i / 8 * uu, y + size * 0.16 + math.sin(i * 1.7 + k) * 2) for i in range(9)]
                        c.drawPath(L.rough_path(pts, seed=k, amp=1.5), P(L.HOT, 230, stroke=size * 0.08))
            x += tw + sp
