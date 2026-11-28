"""Gemeinsamer Kern für die drei Look-Tests (28.11.2026): Schriften, Farben, Easing, Untertitel, Rendern, Ton."""
import skia, math, json, os, subprocess, sys, wave
import numpy as np

W, H, FPS = 1080, 1920, 30
LAB = os.path.dirname(os.path.abspath(__file__))
FD = LAB + '/fonts/'
INTER = FD + 'inter/' if os.path.isdir(FD + 'inter') else '/usr/share/fonts/opentype/inter/'          # Inter Display (Paket fonts-inter)
REPO = next((p for p in (os.path.abspath(LAB + '/../..'), '/home/claude/ff2') if os.path.isdir(p + '/system/lib')), '/home/claude/ff2')
FONTFILES = {
    'black': INTER + 'InterDisplay-Black.otf', 'xbold': INTER + 'InterDisplay-ExtraBold.otf', 'bold': INTER + 'InterDisplay-Bold.otf',
    'semi': INTER + 'InterDisplay-SemiBold.otf', 'med': INTER + 'InterDisplay-Medium.otf', 'reg': INTER + 'InterDisplay-Regular.otf',
    'mono': FD + 'IBMPlexMono-SemiBold.ttf', 'monom': FD + 'IBMPlexMono-Medium.ttf',
    'serif': FD + 'InstrumentSerif-Regular.ttf', 'serifi': FD + 'InstrumentSerif-Italic.ttf',
    'dms': FD + 'DMSerifDisplay-Regular.ttf', 'dmsi': FD + 'DMSerifDisplay-Italic.ttf',
    'cond': FD + 'BarlowCondensed-ExtraBold.ttf',
}
_TF = {}


def font(name, size):
    if name not in _TF:
        _TF[name] = skia.Typeface.MakeFromFile(FONTFILES[name]); assert _TF[name], name
    f = skia.Font(_TF[name], size); f.setSubpixel(True); f.setEdging(skia.Font.Edging.kAntiAlias)
    return f


def C(h, a=1.0):
    h = h.lstrip('#')
    return skia.Color(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), int(round(255 * max(0.0, min(1.0, a)))))


def mix(h1, h2, t):
    a = [int(h1.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)]; b = [int(h2.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)]
    return '#%02x%02x%02x' % tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def P(color, a=1.0, stroke=None, butt=False, miter=False, blur=None):
    p = skia.Paint(AntiAlias=True)
    p.setColor(C(color, a) if isinstance(color, str) else color)
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(stroke)
        p.setStrokeCap(skia.Paint.kButt_Cap if butt else skia.Paint.kRound_Cap)
        p.setStrokeJoin(skia.Paint.kMiter_Join if miter else skia.Paint.kRound_Join)
    if blur:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    return p


def lin(x0, y0, x1, y1, cols, pos=None):
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeLinear([skia.Point(x0, y0), skia.Point(x1, y1)], cols, pos))
    return p


def rad(cx, cy, r, cols, pos=None):
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeRadial(skia.Point(cx, cy), r, cols, pos))
    return p


# ---------------------------------------------------------------- Easing
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def lerp(a, b, t): return a + (b - a) * t
def pr(t, t0, dur): return clamp((t - t0) / dur)
def eo3(t): t = clamp(t); return 1 - (1 - t) ** 3
def eo5(t): t = clamp(t); return 1 - (1 - t) ** 5
def ei2(t): t = clamp(t); return t * t
def ei3(t): t = clamp(t); return t * t * t
def eio(t): t = clamp(t); return 4 * t * t * t if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2
def back(t, s=1.25): t = clamp(t) - 1; return 1 + t * t * ((s + 1) * t + s)          # weiches Überschwingen (kein Hüpfen)


# ---------------------------------------------------------------- Text
def tw(s, f, track=0.0):
    return f.measureText(s) + track * max(0, len(s) - 1)


def text(c, s, x, y, f, paint, align='c', track=0.0):
    w = tw(s, f, track); x0 = x - (w / 2 if align == 'c' else (w if align == 'r' else 0))
    if not track:
        c.drawString(s, x0, y, f, paint)
    else:
        for ch in s:
            c.drawString(ch, x0, y, f, paint); x0 += f.measureText(ch) + track
    return w


def rrect(c, x, y, w, h, r, paint):
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), r, r), paint)


def chip(c, s, x, y, f, fg, bg, padx=18, pady=10, r=8, align='l', track=3.0, stroke=None, a=1.0):
    """Etikett (Mono-Versalien im Kasten). (x, y) = linke obere Ecke bzw. Mitte/rechts je nach align. Liefert Breite."""
    w = tw(s, f, track) + 2 * padx; m = f.getMetrics(); h = (-m.fAscent * 0.74) + 2 * pady
    x0 = x - (w / 2 if align == 'c' else (w if align == 'r' else 0))
    if bg:
        rrect(c, x0, y, w, h, r, P(bg, a))
    if stroke:
        rrect(c, x0, y, w, h, r, P(stroke[0], a, stroke=stroke[1]))
    text(c, s, x0 + padx, y + pady + (-m.fAscent * 0.74), f, P(fg, a), 'l', track)
    return w


# ---------------------------------------------------------------- Wörter + Untertitel
CUT = (2.20, 2.75)            # Pause nach dem Hook auf ruhige 0,6 s gekürzt (wie tighten.py)
GROUPS = [[0, 1, 2], [3, 4, 5], [6, 7], [8, 9, 10], [11, 12], [13, 14, 15], [16, 17], [18, 19], [20, 21]]


def load_words():
    ws = [w for w in json.load(open(LAB + '/audio/words.json'))['words'] if w['text'] not in ('[pause]', '–', '-', '—')]
    sh = CUT[1] - CUT[0]
    for w in ws:
        if w['start'] >= CUT[1]:
            w['start'] -= sh; w['end'] -= sh
    return ws


WORDS = None


def wt(word, nth=0):
    """Startzeit eines gesprochenen Wortes."""
    global WORDS
    WORDS = WORDS or load_words()
    hits = [w for w in WORDS if w['text'].strip('.,?!').lower() == word.lower()]
    return hits[nth]['start']


def captions(c, t, st):
    """Untertitel: kurze Wortgruppen, gesprochene Wörter hell, kommende gedimmt. st = Stil (dict)."""
    global WORDS
    WORDS = WORDS or load_words()
    gs = [[WORDS[i] for i in g] for g in GROUPS]
    for k, g in enumerate(gs):
        t0 = g[0]['start'] - 0.06
        t1 = gs[k + 1][0]['start'] - 0.06 if k + 1 < len(gs) and gs[k + 1][0]['start'] - g[-1]['end'] < 0.9 else g[-1]['end'] + 0.30
        if k == len(gs) - 1:
            t1 = min(t1, g[-1]['start'] + 1.15)
        if not (t0 <= t < t1):
            continue
        f = font(st.get('font', 'bold'), st.get('size', 54)); sp = f.measureText(' ')
        ws = [w['text'] for w in g]; widths = [f.measureText(s) for s in ws]
        tot = sum(widths) + sp * (len(ws) - 1)
        a_in = eo3(pr(t, t0, 0.14)); dy = (1 - a_in) * 14
        y = st.get('y', 1392) + dy; x = 540 - tot / 2
        if st.get('pill'):
            px, py = st.get('padx', 30), st.get('pady', 20); hh = st.get('size', 54) * 0.74
            rrect(c, x - px, y - hh - py, tot + 2 * px, hh + 2 * py, st.get('radius', 22), P(st['pill'], a_in * st.get('pill_a', 1.0)))
        for s, wd, w in zip(ws, widths, g):
            said = t >= w['start'] - 0.03
            cur = said and t < w['end'] + 0.08
            colr = st.get('hi') if (cur and st.get('hi')) else st.get('fg', '#ffffff')
            al = (1.0 if said else st.get('dim', 0.42)) * a_in
            if st.get('shadow'):
                c.drawString(s, x, y + 3, f, P('#000000', 0.55 * al, blur=7))
            c.drawString(s, x, y, f, P(colr, al))
            x += wd + sp


# ---------------------------------------------------------------- Rendern
def _surface():
    return skia.Surface(W, H)


def sheet(draw, times, out, scale=0.25, cols=6):
    """Kontaktbogen mehrerer Zeitpunkte (zum Prüfen)."""
    s = _surface(); tw_, th_ = int(W * scale), int(H * scale); rows = (len(times) + cols - 1) // cols
    big = skia.Surface(tw_ * cols, th_ * rows); bc = big.getCanvas(); bc.clear(C('#202020'))
    smp = skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear)
    for i, t in enumerate(times):
        c = s.getCanvas(); c.save(); draw(c, t); c.restore()
        img = s.makeImageSnapshot()
        x, y = (i % cols) * tw_, (i // cols) * th_
        bc.drawImageRect(img, skia.Rect.MakeXYWH(x, y, tw_, th_), smp)
        bc.drawString('%.2f' % t, x + 6, y + 18, skia.Font(None, 16), P('#ff3b30'))
    big.makeImageSnapshot().save(out, skia.kPNG)


def still(draw, t, out):
    s = _surface(); c = s.getCanvas(); draw(c, t); s.makeImageSnapshot().save(out, skia.kPNG)


def render(draw, T, out, audio=None):
    tmp = out.replace('.mp4', '_v.tmp.mp4')
    cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
           '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', tmp]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    s = _surface()
    for i in range(int(round(T * FPS))):
        c = s.getCanvas(); c.save(); draw(c, i / FPS); c.restore()
        p.stdin.write(s.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType).tobytes())
    p.stdin.close(); assert p.wait() == 0
    if audio:
        subprocess.check_call(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-i', audio, '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                               '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', out])
        os.remove(tmp)
    else:
        os.replace(tmp, out)


# ---------------------------------------------------------------- Ton
def _sfx(SR):
    src = open(REPO + '/system/lib/pipeline.py', encoding='utf-8').read()
    a = src.index('def sfx_sounds(SR):'); b = src.index('def noise_check', a)
    ns = {}; exec(src[a:b], ns)
    return ns['sfx_sounds'](SR)


def build_audio(T, events, out, music_start=0.0):
    """Stimme (Pause gekürzt) + „Chill Wave“ leise + Effekte (reine Töne), gemastert auf ca. −15 LUFS. events = [(zeit, art, pegel)]."""
    SR = 44100
    dec = lambda path: np.frombuffer(subprocess.check_output(['ffmpeg', '-v', 'error', '-i', path, '-ar', str(SR), '-ac', '1', '-f', 'f32le', '-']), np.float32).copy()
    v = dec(LAB + '/audio/voice_raw.mp3'); a, b = int(CUT[0] * SR), int(CUT[1] * SR); xf = int(0.012 * SR)
    left = v[:a].copy(); right = v[b:].copy(); left[-xf:] *= np.linspace(1, 0, xf); right[:xf] *= np.linspace(0, 1, xf)
    v = np.concatenate([left, right]); N = int(T * SR)
    voice = np.zeros(N, np.float32); voice[:min(N, len(v))] = v[:N]
    voice *= 0.16 / max(1e-6, np.sqrt(np.mean(voice[np.abs(voice) > 0.01] ** 2)))
    m = dec(REPO + '/system/assets/musik/chill_wave.mp3')[int(music_start * SR):][:N]
    m = m / max(1e-6, np.sqrt(np.mean(m ** 2))) * 0.050; fi = int(0.35 * SR); m[:fi] *= np.linspace(0, 1, fi)
    S = _sfx(SR); sfx = np.zeros(N + SR, np.float32)
    for (te, kind, g) in events:
        i0 = max(0, int(te * SR)); sg = S[kind] * g; sfx[i0:i0 + len(sg)] += sg[:len(sfx) - i0]
    venv = np.convolve(np.abs(voice), np.ones(4410) / 4410, 'same'); duck = np.convolve(np.where(venv > 0.01, 0.5, 1.0), np.ones(8820) / 8820, 'same')
    mx = voice + m * duck + sfx[:N] * 0.55
    fo = int(0.5 * SR); mx[-fo:] *= np.linspace(1, 0, fo); mx = mx / np.max(np.abs(mx)) * 0.92
    tmp = out + '.raw.wav'
    with wave.open(tmp, 'wb') as wv:
        wv.setnchannels(1); wv.setsampwidth(2); wv.setframerate(SR); wv.writeframes((mx * 32767).astype(np.int16).tobytes())
    subprocess.check_call(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-af', 'loudnorm=I=-15:TP=-1.5:LRA=11', '-ar', '48000', out]); os.remove(tmp)
