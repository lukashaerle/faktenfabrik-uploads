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
    for k in range(int(T / cl) + 1):
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
    from render import skia, P, W
    a = 255 if t < 2.2 else int(255 * (1 - (t - 2.2) / 0.4))
    lines = text.split('\n')
    size = 96
    f = skia.Font(L.FONT, size)
    while max(f.measureText(x) for x in lines) > 960:
        size -= 4; f = skia.Font(L.FONT, size)
    s = 1.0 + 0.04 * math.sin(t * 14) * max(0.0, 1 - t / 1.2)
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

def follow_overlays(c, scene, t, T, TOTAL):
    """2) Abo-Karte in der letzten Szene, 3) kurzer Hinweis in der Videomitte."""
    import render as L
    from render import skia, P, W, draw_text_c
    pop = L.pop
    # --- 3) Mitte: kleiner Hinweis, ca. 45 % der Laufzeit, 2,4 s ---
    m0 = TOTAL * 0.45
    if m0 <= T <= m0 + 2.4:
        k = pop(T, m0, 0.35)
        out = 1.0 if T < m0 + 2.0 else max(0.0, 1 - (T - m0 - 2.0) / 0.4)
        x = W - 30 - 600 * min(1.0, k) * out
        c.save(); c.translate(x, 1150)
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

def setup():
    import render as L
    import wordsubs as WS
    import episode as E
    L.DUR = json.load(open('durs.json')); L.VOICE = json.load(open('voice.json'))
    L.SCENES = E.SCENES; L.FADE_COL = E.FADE_COL
    L.HIGHLIGHT = getattr(E, 'HIGHLIGHT', [])
    WS.init(load_words(), json.load(open('para_word_idx.json')), L.HIGHLIGHT)
    starts = json.load(open('scene_starts.json'))
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
        c.save()
        T = starts[scene] + t
        # Kamera: packend, aber ohne Ruckeln.
        # 1) Szenenstart: weicher Push-out (1,06 -> 1,0) für Energie beim Schnitt
        z = 1.0 + 0.06 * (1 - smooth(t / 0.6))
        # 2) langsamer, stetiger Push-in über die Szene
        z += 0.025 * smooth(t / max(d, 0.1))
        # 3) Rhythmus: alle 2,2 s ein sanfter Zoom-Atem (stetig, keine Stufen)
        z += 0.012 * (1 - math.cos(t * math.pi / 1.1)) / 2
        # 4) Akzent beim Schlüsselwort
        z += 0.03 * pulse(T)
        # seitliches Schwenken, stetig, Richtung wechselt pro Szene
        dirn = 1 if scene % 2 == 0 else -1
        px = dirn * 14 * math.sin(t * math.pi / 2.2) * smooth(t / 0.6) * smooth((d - t) / 0.6)
        py = -6 * pulse(T)
        c.translate(W / 2 + px, H / 2 + py); c.scale(z, z); c.translate(-W / 2, -H / 2)
        if scene in shake and t < 0.5:   # nur noch ein kurzer, weicher Ruck (optional pro Episode)
            a = 6 * (1 - smooth(t / 0.5))
            c.translate(math.sin(t * 40) * a, 0)
        L.SCENES[scene](c, t, d)
        c.restore()
        hook_overlay(c, scene, t, getattr(E, 'HOOK_TEXT', ''))
        follow_overlays(c, scene, t, starts[scene] + t, TOTAL)
        # progress bar (retention)
        g = (starts[scene] + t) / TOTAL
        c.drawRect(skia.Rect.MakeXYWH(0, 0, W, 12), P('#000000', 90))
        c.drawRect(skia.Rect.MakeXYWH(0, 0, W * g, 12), P('#ffd23f'))
        WS.draw_word_subs(c, starts[scene] + t)
        if scene > 0 and t < 0.25:
            c.drawRect(skia.Rect.MakeWH(W, H), P(L.FADE_COL[scene], int(255 * (1 - t / 0.25))))

    L.frame = frame
    return L

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'timing': cmd_timing()
    elif cmd == 'audio': cmd_audio()
    elif cmd == 'still':
        L = setup(); i, t = int(sys.argv[2]), float(sys.argv[3]); L.render_scene(i, f'still_{i}_{t}.png', still=t)
    elif cmd == 'scenes':
        L = setup()
        for i in map(int, sys.argv[2:]):
            L.render_scene(i, f'scene_{i:02d}.mp4'); print('done', i, flush=True)
    elif cmd == 'render':
        name = sys.argv[2] if len(sys.argv) > 2 else 'Folge'
        n = len(json.load(open('durs.json')))
        me = os.path.abspath(__file__)
        a = subprocess.Popen([sys.executable, me, 'scenes'] + [str(i) for i in range(0, n, 2)])
        b = subprocess.Popen([sys.executable, me, 'scenes'] + [str(i) for i in range(1, n, 2)])
        if a.wait() or b.wait(): raise SystemExit('scene render failed')
        open('list.txt', 'w').write(''.join(f"file 'scene_{i:02d}.mp4'\n" for i in range(n)))
        subprocess.check_call(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', 'list.txt', '-c', 'copy', 'video.mp4'])
        out = f'FAKTENFABRIK_{name}.mp4'
        subprocess.check_call(['ffmpeg', '-y', '-loglevel', 'error', '-i', 'video.mp4', '-i', 'mix.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', out])
        print('wrote', out)
