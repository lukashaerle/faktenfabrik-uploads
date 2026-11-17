"""FAKTENFABRIK video pipeline (generic part).

Usage inside an episode folder that contains:
  voice.mp3     - ElevenLabs Jesco recording (one take)
  words.json    - ElevenLabs transcript {"words":[{text,start,end,type}...]}
  paras.json    - list of 10 paragraph texts (spoken text, no [tags]), one per scene
  episode.py    - defines SCENES (10 functions f(c, t, d)), FADE_COL (10 colors),
                  HIGHLIGHT (list of words shown yellow); may import from render

  python3 /path/to/lib/pipeline.py timing      -> durs.json, voice.json, scene_starts.json
  python3 /path/to/lib/pipeline.py audio       -> mix.wav (voice + music + whooshes)
  python3 /path/to/lib/pipeline.py still 0 2.5 -> still_0_2.5.png  (check frames!)
  python3 /path/to/lib/pipeline.py render      -> FAKTENFABRIK_<name>.mp4 (2 parallel jobs)
"""
import sys, os, json, re, subprocess, math
LIB = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, LIB)
sys.path.insert(0, os.getcwd())

TAIL = 2.5   # seconds after the last word for the logo

def load_words():
    raw = json.load(open('words.json'))
    raw = raw['words'] if isinstance(raw, dict) else raw
    return [w for w in raw if w.get('type', 'word') == 'word' and not w['text'].startswith('[')
            and not w['text'].endswith(']') and w['text'] not in ('—', '-', '–')]

def norm(s):
    return re.sub(r'[^\wäöüÄÖÜß]', '', s).lower()

def para_starts(words, paras):
    """index of the first word of each paragraph, matched in order"""
    starts, i = [], 0
    for p in paras:
        first = [norm(x) for x in p.split() if norm(x)][:3]
        found = None
        for k in range(i, len(words)):
            seq = [norm(words[j]['text']) for j in range(k, min(k + len(first), len(words)))]
            if seq == first:
                found = k; break
        if found is None:
            raise SystemExit(f'Paragraph start not found in transcript: {p[:40]}')
        starts.append(found); i = found + 1
    return starts

def cmd_timing():
    words = load_words(); paras = json.load(open('paras.json'))
    st = para_starts(words, paras)
    dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', 'voice.mp3']))
    starts = [0.0] + [max(0.0, words[k]['start'] - 0.15) for k in st[1:]]
    edges = starts + [dur]
    d = [edges[i + 1] - edges[i] for i in range(len(starts))]
    tail = min(6.0, max(TAIL, 61.5 - dur))   # Logo-Karte verlängern, damit das Video sicher > 61 s ist
    v = d[:]; d[-1] += tail
    json.dump(v, open('voice.json', 'w')); json.dump(d, open('durs.json', 'w'))
    json.dump(starts, open('scene_starts.json', 'w')); json.dump(st, open('para_word_idx.json', 'w'))
    print('scene durations', [round(x, 2) for x in d], 'total', round(sum(d), 2))

def cmd_audio():
    import numpy as np, wave
    SR = 44100
    D = json.load(open('durs.json')); T = sum(D)
    starts = np.concatenate([[0], np.cumsum(D)[:-1]]); N = int(T * SR) + SR
    raw = subprocess.check_output(['ffmpeg', '-loglevel', 'error', '-i', 'voice.mp3', '-ar', str(SR), '-ac', '1', '-f', 'f32le', '-'])
    a = np.frombuffer(raw, np.float32); voice = np.zeros(N, np.float32); voice[:len(a)] += a[:N]
    note = lambda m: 440 * 2 ** ((m - 69) / 12)
    chords = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]
    music = np.zeros(N, np.float32); cl = 2.4
    mood = json.load(open('music.json')).get('mood', 'fakten') if os.path.exists('music.json') else 'fakten'
    if mood == 'doku':
        # Doku-Stimmung (selbst erzeugt): tiefer Moll-Drone, langsamer Puls, dunkle Fläche
        t_all = np.arange(N) / SR
        for m, g in [(33, 0.10), (40, 0.06), (45, 0.045), (48, 0.03)]:          # A1, E2, A2, C3
            f = note(m); music += g * np.sin(2 * np.pi * f * t_all + 0.3 * np.sin(2 * np.pi * 0.07 * t_all)) * (0.75 + 0.25 * np.sin(2 * np.pi * 0.05 * t_all + m))
        prog = [[57, 60, 64], [53, 57, 60], [55, 59, 62], [52, 56, 59]]          # Am F G E
        for k in range(int(T / 4.8) + 1):
            ch = prog[k % 4]; s = int(k * 4.8 * SR); e = min(N, s + int(5.4 * SR)); tt = np.arange(e - s) / SR
            env = np.minimum(1, tt / 1.6) * np.minimum(1, np.maximum(0, (5.4 - tt)) / 1.2)
            for m in ch:
                music[s:e] += 0.018 * np.sin(2 * np.pi * note(m) * tt) * env
        beat = 0.0
        while beat < T:                                                          # dumpfer Herzschlag-Puls
            for off, g in [(0, 1.0), (0.28, 0.6)]:
                s = int((beat + off) * SR); tt = np.arange(int(0.35 * SR)) / SR; e = min(N, s + len(tt))
                if s < N: music[s:e] += 0.22 * g * np.sin(2 * np.pi * (55 * np.exp(-tt * 6)) * tt)[:e - s] * np.exp(-tt * 9)[:e - s]
            beat += 1.2
        cl = 1e9
    for k in range(int(T / cl) + 1 if mood != 'doku' else 0):
        ch = chords[k % 4]; s = int(k * cl * SR); e = min(N, int((k + 1) * cl * SR) + SR // 2); tt = np.arange(e - s) / SR
        env = np.minimum(1, tt / 0.6) * np.exp(-np.maximum(0, tt - cl) * 4)
        for m in ch:
            f = note(m - 12); music[s:e] += (0.05 * np.sin(2 * np.pi * f * tt) + 0.025 * np.sin(2 * np.pi * f * 1.003 * tt)) * env
        for j, m in enumerate([ch[0], ch[1], ch[2], ch[1] + 12, ch[2], ch[1]]):
            ps = s + int(j * cl / 6 * SR); pe = min(N, ps + SR); pt = np.arange(pe - ps) / SR; f = note(m + 12)
            music[ps:pe] += 0.05 * np.sin(2 * np.pi * f * pt) * np.exp(-pt * 6)
    sfx = np.zeros(N, np.float32); rng = np.random.RandomState(1)
    def add(sec, sig, g=1.0):
        s = int(sec * SR); e = min(N, s + len(sig))
        if s < N: sfx[s:e] += g * sig[:e - s]
    n = int(0.45 * SR); x = rng.randn(n); y = np.convolve(x, np.ones(40) / 40, 'same'); W = y / np.max(np.abs(y)) * np.sin(np.linspace(0, np.pi, n)) * 0.25
    for i in range(1, len(D)): add(starts[i] - 0.15, W)
    pops = json.load(open('pops.json')) if os.path.exists('pops.json') else []
    tt = np.arange(int(0.12 * SR)) / SR; P = 0.35 * np.sin(2 * np.pi * (300 + 1500 * tt) * tt * 3) * np.exp(-tt * 30)
    for sc, t0 in pops: add(starts[sc] + t0, P)
    booms = json.load(open('booms.json')) if os.path.exists('booms.json') else []
    tb = np.arange(int(0.9 * SR)) / SR
    B = 0.9 * np.sin(2 * np.pi * (90 * np.exp(-tb * 3)) * tb) * np.exp(-tb * 4) + 0.15 * rng.randn(len(tb)) * np.exp(-tb * 25)
    for sc, t0 in booms: add(starts[sc] + t0, B)
    s10 = starts[-1] + max(0.5, json.load(open('voice.json'))[-1] - 0.5)
    for j, m in enumerate([72, 76, 79, 84]):
        tt = np.arange(SR) / SR; add(s10 + j * 0.09, 0.12 * np.sin(2 * np.pi * note(m) * tt) * np.exp(-tt * 4))
    venv = np.convolve(np.abs(voice), np.ones(4410) / 4410, 'same'); duck = np.convolve(np.where(venv > 0.01, 0.45, 1.0), np.ones(8820) / 8820, 'same')
    mix = (voice + music * duck * 0.9 + sfx * 0.6)[:int(T * SR)]
    fade = int(1.5 * SR); mix[-fade:] *= np.linspace(1, 0, fade); mix = mix / np.max(np.abs(mix)) * 0.95
    with wave.open('mix.wav', 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())
    print('mix.wav', round(T, 2))



def hook_overlay(c, scene, t, text):
    """Text-Hook ab Bild 1: groß, sofort sichtbar, ca. 2,6 s."""
    if scene != 0 or not text or t > 2.6:
        return
    import render as L
    if L.MODERN:
        return hook_modern(c, t, text)
    from render import skia, P, W
    a = 255 if t < 2.2 else int(255 * (1 - (t - 2.2) / 0.4))
    lines = text.split('\n')
    size = 96
    f = skia.Font(L.FONT, size)
    while max(f.measureText(x) for x in lines) > 960:
        size -= 4; f = skia.Font(L.FONT, size)
    s = 1.0  # ruhig, kein Wackeln
    y0 = 560 - (len(lines) - 1) * size * 0.6
    c.save(); c.translate(W / 2, y0); c.scale(s, s); c.rotate(-3)
    h = size * 1.15 * len(lines) + 50
    wmax = max(f.measureText(x) for x in lines) + 80
    r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-wmax / 2, -size - 10, wmax, h), 30, 30)
    c.drawRRect(r, P('#ff3b5c', int(a * 0.95))); c.drawRRect(r, P('#ffffff', a, stroke=8))
    for i, ln in enumerate(lines):
        w = f.measureText(ln); y = i * size * 1.15
        c.drawString(ln, -w / 2, y, f, P('#0d0d0d', a, stroke=12))
        c.drawString(ln, -w / 2, y, f, P('#ffffff', a))
    c.restore()

def hook_modern(c, t, text):
    """Moderner Text-Hook: jede Zeile als eigener Sticker (Zeile 1 weiß/dunkle Schrift, Zeile 2 rot/weiße Schrift),
    leicht schräg, ab Bild 1 voll sichtbar (Cover!). Ab 2,2 s gleitet er weich nach oben weg."""
    import render as L
    from render import skia, P, W
    out = 0.0 if t < 2.2 else L.ease((t - 2.2) / 0.4)
    a = int(255 * (1 - out))
    if a <= 0:
        return
    lines = text.split('\n')
    size = 112
    f = skia.Font(L.FONT_B, size)
    while max(f.measureText(x) for x in lines) > 900:
        size -= 4; f = skia.Font(L.FONT_B, size)
    lh = size * 1.32
    y0 = 560 - (len(lines) - 1) * lh * 0.5 - out * 60
    if getattr(L, 'PAPER', False):
        # Papier: Zettel mit Klebeband, Tinten-Schrift, letzte Zeile mit Textmarker + roter Filzstift-Unterstreichung
        lhp = size * 1.14
        wmax = max(f.measureText(x) for x in lines)
        top = 560 - len(lines) * lhp * 0.5 - size * 0.55 - out * 60
        r = skia.Rect.MakeXYWH(W / 2 - wmax / 2 - 60, top - 20, wmax + 120, len(lines) * lhp + 70)
        c.save()
        if out > 0:
            c.saveLayerAlpha(None, a)
        L.paper_card(c, r, -2.5)
        c.save(); c.translate(W / 2, r.centerY()); c.rotate(-2.5); c.translate(-W / 2, -r.centerY())
        for i, ln in enumerate(lines):
            w = f.measureText(ln); y = top + 30 + size * 0.9 + i * lhp
            if i == len(lines) - 1:
                L.marker_swipe(c, W / 2 - w / 2, y - size * 0.66, w, size * 0.66, L.MARKER, u=1.0, a=200, seed=7)
            c.drawString(ln, W / 2 - w / 2, y, f, P(L.INK_P))
            if i == len(lines) - 1:
                pts = [(W / 2 - w / 2 - 6 + (w + 12) * j / 10, y + size * 0.2 + math.sin(j * 1.3) * 3) for j in range(11)]
                c.drawPath(L.rough_path(pts, seed=9, amp=2), P(L.HOT, stroke=size * 0.09))
        c.restore()
        if out > 0:
            c.restore()
        c.restore()
        return
    if getattr(L, 'MINIMAL', False):
        # schlicht: große weiße Schrift mit dunkler Kontur und Schatten, keine Farbflächen
        for i, ln in enumerate(lines):
            w = f.measureText(ln); y = y0 + i * lh * 0.86
            c.drawString(ln, W / 2 - w / 2, y + size * 0.08, f, P('#000000', int(a * 0.55), blur=size * 0.1))
            if getattr(L, 'GLOW', None):
                c.drawString(ln, W / 2 - w / 2, y, f, P(L.HOT if i % 2 else L.CYAN, int(a * 0.9), blur=size * 0.24))
            c.drawString(ln, W / 2 - w / 2, y, f, P('#000000', a, stroke=size * 0.10))
            c.drawString(ln, W / 2 - w / 2, y, f, P('#ffffff', a))
        return
    styles = [('#ffffff', L.INK), (L.HOT, '#ffffff'), (L.ACCENT, L.INK)] if L.TILT else [('#ffffff', L.INK), (L.HOT, '#ffffff'), ('#ffffff', L.INK)]
    for i, ln in enumerate(lines):
        bg, fg = styles[min(i, 2)]
        w = f.measureText(ln); padx = size * 0.32
        y = y0 + i * lh
        c.save(); c.translate(W / 2 + ((i - (len(lines) - 1) / 2) * 14 if L.TILT else 0), y); c.rotate((-3 + i * 1.2) if L.TILT else 0)
        r = skia.Rect.MakeXYWH(-w / 2 - padx, -size * 0.92, w + 2 * padx, size * 1.2)
        rr = skia.RRect.MakeRectXY(r, size * 0.22, size * 0.22)
        c.drawRRect(skia.RRect.MakeRectXY(r.makeOffset(0, 14), size * 0.22, size * 0.22), P('#000000', int(a * 0.35), blur=18))
        c.drawRRect(rr, P(bg, a))
        c.drawString(ln, -w / 2, 0, f, P(fg, a))
        c.restore()

FOLLOW_W, FOLLOW_H, FOLLOW_DUR = 620, 96, 2.4

def place_follow(force=False):
    """Sucht Zeitpunkt und Platz für den Hinweis „Mehr Fakten? Folgen!“, an dem er keinen
    Inhalt verdeckt: rendert die Szenen (ohne Overlays) im Fenster 30–65 % der Laufzeit,
    misst die Kantendichte in jeder Kandidaten-Fläche und nimmt die ruhigste. -> follow.json"""
    if os.path.exists('follow.json') and not force:
        return json.load(open('follow.json'))
    import numpy as np
    import render as L
    import episode as E
    from render import skia, W, H
    L.DUR = json.load(open('durs.json')); L.VOICE = json.load(open('voice.json'))
    L.SCENES = E.SCENES; L.FADE_COL = E.FADE_COL
    starts = json.load(open('scene_starts.json')); TOTAL = sum(L.DUR); n = len(L.DUR)
    surf = skia.Surface(W, H)
    def frame_at(T):
        sc = max(i for i in range(n) if starts[i] <= T)
        c = surf.getCanvas(); c.clear(L.col('#000000'))
        L.SCENES[sc](c, T - starts[sc], L.DUR[sc])
        a = surf.makeImageSnapshot().toarray(colorType=skia.kBGRA_8888_ColorType)[::4, ::4, :3].astype(float).mean(axis=2)
        return sc, a
    # Kandidaten-Flächen (Mitte y), links oder rechts eingeschoben; Untertitel (1250-1420) und Banner bleiben frei
    ys = [1150, 1500, 560, 450]
    rects = [(side, y) for y in ys for side in ('right', 'left')]
    cache = {}
    def busy(T, side, y):
        key = round(T, 1)
        if key not in cache:
            cache[key] = frame_at(T)
        sc, a = cache[key]
        x0 = W - 30 - FOLLOW_W if side == 'right' else 30
        r = a[(y - FOLLOW_H // 2 - 20) // 4:(y + FOLLOW_H // 2 + 20) // 4, x0 // 4:(x0 + FOLLOW_W) // 4]
        gy, gx = np.gradient(r)
        return float(np.hypot(gx, gy).mean())
    best = None
    T = TOTAL * 0.30
    while T <= TOTAL * 0.65:
        scs = {max(i for i in range(n) if starts[i] <= T + k) for k in (0, FOLLOW_DUR)}
        if not (scs & {0, n - 1}) and len(scs) == 1:      # nicht über einen Schnitt, nicht in Szene 1/Logo
            for side, y in rects:
                score = max(busy(T + k, side, y) for k in (0.0, 0.8, 1.6, 2.4))
                score += 0.4 if y != 1150 else 0.0            # leichte Vorliebe für den gewohnten Platz
                if best is None or score < best[0]:
                    best = (score, round(T, 2), side, y)
        T += 0.4
    res = {'t0': best[1], 'side': best[2], 'y': best[3], 'score': round(best[0], 2)} if best else {'t0': TOTAL * 0.45, 'side': 'right', 'y': 1150, 'score': None}
    json.dump(res, open('follow.json', 'w'))
    print('follow hint', res)
    return res

def follow_overlays(c, scene, t, T, TOTAL):
    """2) Abo-Karte in der letzten Szene, 3) kurzer Hinweis in der Videomitte."""
    import render as L
    from render import skia, P, W, draw_text_c
    pop = L.pop
    # --- 3) Mitte: kleiner Hinweis an der ruhigsten Stelle (place_follow), 2,4 s ---
    fp = FOLLOW
    m0 = fp['t0']
    if L.MODERN:
        return follow_modern(c, scene, t, T, fp)
    if m0 <= T <= m0 + FOLLOW_DUR:
        k = pop(T, m0, 0.35)
        out = 1.0 if T < m0 + 2.0 else max(0.0, 1 - (T - m0 - 2.0) / 0.4)
        slide = 1 - min(1.0, k) * out
        if fp['side'] == 'right':
            x = W - 30 - FOLLOW_W + slide * (FOLLOW_W + 60)
        else:
            x = 30 - slide * (FOLLOW_W + 60)
        c.save(); c.translate(x, fp['y'])
        r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(0, -48, 620, 96), 48, 48)
        c.drawRRect(r, P('#1b2a4a', 235)); c.drawRRect(r, P('#ffd23f', stroke=6))
        c.drawCircle(52, 0, 30, P('#ff3b5c')); draw_text_c(c, '+', 52, 17, 50, fill='#ffffff', outline='#ff3b5c', ow=2)
        draw_text_c(c, 'Mehr Fakten? Folgen!', 335, 14, 40, fill='#ffffff', outline='#1b2a4a', ow=2)
        c.restore()
    # --- 2) Ende: animiertes Plus, das zum Haken wird ---
    last = len(L.DUR) - 1
    if scene == last and t > 0.3:
        k = pop(t, 0.3, 0.45)
        cx, cy = 820, 900
        c.save(); c.translate(cx, cy); c.scale(k, k)
        tapped = t > 2.2
        pulse = 1 + 0.08 * math.sin(t * 9) if not tapped else 1.0
        c.save(); c.scale(pulse, pulse)
        c.drawCircle(0, 0, 135, P('#ffffff', 60, blur=30))
        c.drawCircle(0, 0, 100, P('#ff3b5c' if not tapped else '#2fbf71'))
        c.drawCircle(0, 0, 100, P('#ffffff', stroke=10))
        if not tapped:
            c.drawLine(-45, 0, 45, 0, P('#ffffff', stroke=22)); c.drawLine(0, -45, 0, 45, P('#ffffff', stroke=22))
        else:
            p = skia.Path(); p.moveTo(-45, 0); p.lineTo(-12, 35); p.lineTo(48, -35)
            c.drawPath(p, P('#ffffff', stroke=22))
        c.restore()
        # tapping finger
        if 1.2 < t < 2.6:
            ft = (t - 1.2) / 1.0
            fy = 170 - 90 * min(1.0, ft)
            c.drawCircle(70, fy, 34, P('#ffcf9e')); c.drawCircle(70, fy, 34, P('#0d0d0d', stroke=6))
            c.drawRect(skia.Rect.MakeXYWH(48, fy, 44, 110), P('#ffcf9e'))
        r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-190, 125, 380, 110), 30, 30)
        c.drawRRect(r, P('#1b2a4a', 240)); c.drawRRect(r, P('#ffd23f', stroke=6))
        draw_text_c(c, 'Folgen' if not tapped else 'Danke!', 0, 172, 44, fill='#ffd23f', outline='#1b2a4a', ow=2)
        draw_text_c(c, 'Abonnieren' if not tapped else 'Bis morgen!', 0, 218, 34, fill='#ffffff', outline='#1b2a4a', ow=2)
        c.restore()

def follow_modern(c, scene, t, T, fp):
    import render as L
    from render import skia, P, W
    m0 = fp['t0']
    # --- Hinweis in der Videomitte: Milchglas-Pille mit Profil-Kreis und rotem „Folgen“-Knopf ---
    if m0 <= T <= m0 + FOLLOW_DUR:
        k = L.spring(T, m0, 0.5)
        out = 1.0 if T < m0 + 2.0 else max(0.0, 1 - (T - m0 - 2.0) / 0.4)
        slide = (1 - min(1.0, k)) + (1 - out)
        x = (W - 30 - FOLLOW_W + slide * (FOLLOW_W + 60)) if fp['side'] == 'right' else (30 - slide * (FOLLOW_W + 60))
        c.save(); c.translate(x, fp['y'])
        r = skia.Rect.MakeXYWH(0, -48, FOLLOW_W, 96)
        L.glass(c, r, 48, alpha=210)
        c.drawCircle(50, 0, 34, P('#ff8c2b')); c.drawCircle(50, 0, 34, P('#ffffff', stroke=4))
        fb = skia.Font(L.FONT_B, 34); c.drawString('F', 50 - fb.measureText('F') / 2, 12, fb, P('#ffffff'))
        f1 = skia.Font(L.FONT, 34); c.drawString('Mehr Fakten?', 100, 12, f1, P('#ffffff'))
        bw = 210; br = skia.Rect.MakeXYWH(FOLLOW_W - bw - 16, -32, bw, 64)
        pulse = 1 + 0.04 * math.sin(T * 7)
        c.save(); c.translate(br.centerX(), 0); c.scale(pulse, pulse); c.translate(-br.centerX(), 0)
        mn = getattr(L, 'MINIMAL', False)
        c.drawRRect(skia.RRect.MakeRectXY(br, 32, 32), P('#ffffff' if mn else L.HOT))
        f2 = skia.Font(L.FONT_B, 32); lab = '+ Folgen'
        c.drawString(lab, br.centerX() - f2.measureText(lab) / 2, 11, f2, P(L.INK if mn else '#ffffff'))
        c.restore(); c.restore()
    # --- Ende: großer Folgen-Knopf, Tipp-Welle, wird zum Haken ---
    last = len(L.DUR) - 1
    if scene == last and t > 0.3:
        k = L.spring(t, 0.3, 0.55)
        e = L.ease_out(min(1.0, (t - 0.3) / 0.4))
        cx, cy = 820, 900
        tapped = t > 2.2
        c.save(); c.translate(cx, cy + (1 - e) * 60)
        sc = 0.9 + 0.1 * k
        if 2.0 < t < 2.35:
            sc *= 1 - 0.08 * math.sin((t - 2.0) / 0.35 * math.pi)       # Knopf wird „gedrückt“
        c.save(); c.scale(sc, sc)
        c.drawCircle(0, 0, 150, P(L.HOT if not tapped else '#2fbf71', int(80 * e), blur=40))
        c.drawCircle(0, 0, 100, P(L.HOT if not tapped else '#2fbf71', int(255 * e)))
        c.drawCircle(0, 0, 100, P('#ffffff', int(255 * e), stroke=8))
        if not tapped:
            c.drawLine(-42, 0, 42, 0, P('#ffffff', int(255 * e), stroke=20)); c.drawLine(0, -42, 0, 42, P('#ffffff', int(255 * e), stroke=20))
        else:
            u = L.ease_out((t - 2.2) / 0.3)
            p = skia.Path(); p.moveTo(-44, 2); p.lineTo(-12, 34); p.lineTo(46, -32)
            m = skia.PathMeasure(p, False); seg = skia.Path(); m.getSegment(0, m.getLength() * u, seg, True)
            c.drawPath(seg, P('#ffffff', stroke=20))
        c.restore()
        if 1.9 < t < 2.9:                                        # Tipp-Welle
            u = (t - 2.0) / 0.9
            if u > 0:
                c.drawCircle(0, 0, 100 + 120 * L.ease_out(u), P('#ffffff', int(200 * (1 - u)), stroke=8))
        r = skia.Rect.MakeXYWH(-190, 128, 380, 112)
        L.glass(c, r, 36, alpha=int(215 * e), stroke_a=int(70 * e))
        f1 = skia.Font(L.FONT_B, 42); f2 = skia.Font(L.FONT, 30)
        s1 = 'Folgen' if not tapped else 'Danke!'; s2 = 'für täglich 3 Fakten' if not tapped else 'Bis morgen!'
        c.drawString(s1, -f1.measureText(s1) / 2, 178, f1, P('#ffffff' if getattr(L, 'PAPER', False) or L.ACCENT == L.INK else L.ACCENT, int(255 * e)))
        c.drawString(s2, -f2.measureText(s2) / 2, 220, f2, P('#ffffff', int(230 * e)))
        c.restore()

def grade(c, W, H):
    """Look-Finish über jedem Bild: dezente Vignette (lenkt den Blick in die Mitte).
    Nur der Rand wird gezeichnet (Mitte ausgespart) – spart viel 4K-Renderzeit."""
    import render as L
    from render import skia
    cx, cy, R0 = W / 2, H * 0.47, H * 0.72
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeRadial(skia.Point(cx, cy), R0,
                                               [L.col(L.INK, 0), L.col(L.INK, 0), L.col(L.INK, 90)], [0.0, 0.58, 1.0]))
    ring = skia.Path(); ring.setFillType(skia.PathFillType.kEvenOdd)
    ring.addRect(skia.Rect.MakeWH(W, H)); ring.addCircle(cx, cy, R0 * 0.58)
    c.drawPath(ring, p)

def progress_modern(c, g, W):
    import render as L
    from render import skia, P
    if getattr(L, 'PAPER', False):
        c.drawRect(skia.Rect.MakeXYWH(0, 0, W, 12), P('#d8cfbf', 200))
        if g > 0:
            pts = [(-10 + (W * min(1.0, g) + 10) * i / 24, 6 + math.sin(i * 1.9) * 1.5) for i in range(25)]
            c.drawPath(L.rough_path(pts, seed=4, amp=0.8), P(L.HOT, stroke=10))
        return
    c.drawRect(skia.Rect.MakeXYWH(0, 0, W, 10), P('#000000', 70))
    if g <= 0:
        return
    x = W * min(1.0, g)
    p = skia.Paint(AntiAlias=True)
    cols = [L.col(L.LOGO_GRAD[0]), L.col(L.LOGO_GRAD[2])] if getattr(L, 'COSMIC', False) else [L.col(L.LOGO_GRAD[2]), L.col(L.ACCENT)]
    p.setShader(skia.GradientShader.MakeLinear([skia.Point(0, 0), skia.Point(max(x, 1), 0)], cols))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-10, 0, x + 10, 10), 5, 5), p)
    c.drawCircle(x, 5, 16, P(L.LOGO_GRAD[2] if getattr(L, 'COSMIC', False) else L.ACCENT, 150, blur=9))
    c.drawCircle(x, 5, 7, P('#ffffff'))

def setup():
    import render as L
    import wordsubs as WS
    import episode as E
    L.DUR = json.load(open('durs.json')); L.VOICE = json.load(open('voice.json'))
    L.SCENES = E.SCENES; L.FADE_COL = E.FADE_COL
    L.HIGHLIGHT = getattr(E, 'HIGHLIGHT', [])
    WS.init(load_words(), json.load(open('para_word_idx.json')), L.HIGHLIGHT)
    starts = json.load(open('scene_starts.json'))
    L.WORDS_ALL, L.STARTS = WS.WORDS, starts          # für word_t(): Bausteine genau auf den Ton setzen
    global FOLLOW
    FOLLOW = place_follow()
    from render import skia, W, H, P
    TOTAL = sum(L.DUR)
    shake = set(getattr(E, 'SHAKE_SCENES', []))
    # Akzent-Zeitpunkte: gelb markierte Schlüsselwörter -> weicher Kamera-Impuls genau beim Wort
    hl = set(h.strip('.,:?!–').lower() for h in L.HIGHLIGHT)
    accents = [w['start'] for w in load_words() if w['text'].strip('.,:?!–').lower() in hl]

    def smooth(x):
        x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)

    def pulse(T):
        """weicher Zoom-Impuls (ca. 0,6 s) bei jedem Schlüsselwort, ohne Sprung"""
        v = 0.0
        for a in accents:
            dt = T - a + 0.05
            if 0 <= dt < 0.6:
                v = max(v, smooth(dt / 0.12) * (1 - smooth((dt - 0.12) / 0.48)))
        return v

    def frame(surface, scene, t, d):
        c = surface.getCanvas(); c.clear(L.col('#000000'))
        T = starts[scene] + t
        L.NOW, L.SCENE = T, scene
        modern = L.MODERN
        c.save()
        # Kamera: RUHIG (Wunsch von Lukas, 17.11.): kein Hüpfen, keine Rucke, keine Zoom-Impulse.
        # Nur ein sehr langsamer, gleichmäßiger Push-in über die ganze Szene (kaum wahrnehmbar).
        z = 1.0 + 0.02 * smooth(t / max(d, 0.1))
        # Moderner Szenenwechsel: neue Szene kommt aus leichter Unschärfe und setzt sich weich (0,35 s)
        tr = smooth(t / 0.35) if (modern and scene > 0) else 1.0
        if modern and scene > 0 and tr < 1.0:
            z *= 1.0 + 0.035 * (1 - tr)
            bl = 16 * (1 - tr)
            lp = skia.Paint(); lp.setImageFilter(skia.ImageFilters.Blur(bl, bl))
            c.saveLayer(None, lp)
        c.translate(W / 2, H / 2); c.scale(z, z); c.translate(-W / 2, -H / 2)
        L.SCENES[scene](c, t, d)
        if modern and scene > 0 and tr < 1.0:
            c.restore()
        c.restore()
        if modern and not getattr(L, 'PAPER', False):
            grade(c, W, H)
        hook_overlay(c, scene, t, getattr(E, 'HOOK_TEXT', ''))
        follow_overlays(c, scene, t, T, TOTAL)
        # progress bar (retention)
        g = T / TOTAL
        if modern:
            progress_modern(c, g, W)
        else:
            c.drawRect(skia.Rect.MakeXYWH(0, 0, W, 12), P('#000000', 90))
            c.drawRect(skia.Rect.MakeXYWH(0, 0, W * g, 12), P('#ffd23f'))
        WS.draw_word_subs(c, T)
        if scene > 0 and t < 0.25:
            if modern:
                c.drawRect(skia.Rect.MakeWH(W, H), P(L.FADE_COL[scene], int(55 * (1 - smooth(t / 0.2)))))
            else:
                c.drawRect(skia.Rect.MakeWH(W, H), P(L.FADE_COL[scene], int(255 * (1 - t / 0.25))))

    L.frame = frame
    return L

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'timing': cmd_timing()
    elif cmd == 'follow': place_follow(force=True)
    elif cmd == 'audio': cmd_audio()
    elif cmd == 'still':
        L = setup(); i, t = int(sys.argv[2]), float(sys.argv[3]); L.render_scene(i, f'still_{i}_{t}.png', still=t)
    elif cmd == 'scenes':
        L = setup()
        for i in map(int, sys.argv[2:]):
            L.render_scene(i, f'scene_{i:02d}.mp4'); print('done', i, flush=True)
    elif cmd == 'render':
        name = sys.argv[2] if len(sys.argv) > 2 else 'Folge'
        place_follow(force=True)
        n = len(json.load(open('durs.json')))
        me = os.path.abspath(__file__)
        a = subprocess.Popen([sys.executable, me, 'scenes'] + [str(i) for i in range(0, n, 2)])
        b = subprocess.Popen([sys.executable, me, 'scenes'] + [str(i) for i in range(1, n, 2)])
        if a.wait() or b.wait(): raise SystemExit('scene render failed')
        open('list.txt', 'w').write(''.join(f"file 'scene_{i:02d}.mp4'\n" for i in range(n)))
        subprocess.check_call(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', 'list.txt', '-c', 'copy', 'video.mp4'])
        out = f'FAKTENFABRIK_{name}.mp4'
        subprocess.check_call(['ffmpeg', '-y', '-loglevel', 'error', '-i', 'video.mp4', '-i', 'mix.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', out])
        # Instagram nimmt über die Schnittstelle max. 1920 px Breite: hochwertige Full-HD-Fassung aus dem 4K-Master
        ig = f'FAKTENFABRIK_{name}_IG.mp4'
        subprocess.check_call(['ffmpeg', '-y', '-loglevel', 'error', '-i', out, '-vf', 'scale=1080:1920:flags=lanczos', '-c:v', 'libx264',
                               '-preset', 'slow', '-crf', '17', '-profile:v', 'high', '-pix_fmt', 'yuv420p', '-c:a', 'copy', '-movflags', '+faststart', ig])
        print('wrote', out, '(4K, TikTok/YouTube) und', ig, '(Full HD, Instagram)')
