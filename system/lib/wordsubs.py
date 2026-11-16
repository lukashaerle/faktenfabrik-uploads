"""Word-timed subtitles: every word appears exactly when it is spoken."""
from render import skia, P, W
import render as L

WORDS, PAGES, PSTART, HL = [], [], [], set()

def strip(w):
    return w.strip('.,:;?!–"„“')

def init(words, para_idx, highlight, maxc=24):
    global WORDS, PAGES, PSTART, HL
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
