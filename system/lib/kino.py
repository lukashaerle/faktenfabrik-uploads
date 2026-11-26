"""KINO – Schnitt-Engine für den „FINN-Show“-Stil (25.11.2026).
Wunsch von Lukas: brutale Hook ab Sekunde 1, spürbar „krass geschnitten“, Wiedererkennungswert.

Baut auf dem Cartoon-Baukasten (lib/cartoon.py) auf und macht daraus eine geschnittene Show:
  - FINN ist MODERATOR: steht in jedem Bild unten, bewegt den Mund zur Stimme (Lautstärke der Aufnahme),
    federt auf jedes Wort, zeigt auf die Bühne und reagiert (K.host).
  - Bildaufbau: BÜHNE oben (y 230–800) · UNTERTITEL-Band (y 815–955, groß, 1–3 Wörter, gesprochenes Wort im
    Marker-Kasten) · FINN unten (y 1000–1540, links der Like-Spalte).
  - Farbrollen: Gelb mit Strahlen = Hook/Alarm · Creme = Erklären · Violett = Schlüsselzahl (K.stage).
  - Kamera: Zoom-Stoß auf betonte Wörter (punch), Zoom-Stufe (step), Wackler mit Einschlag-Blitz (shake).
  - Blenden an den SATZGRENZEN (Szenenwechsel), im Wechsel: Tinten-Blende violett/gelb ('ink', Markenzeichen – FINN ist ein
    Tintentropfen, eigener Ton „Blubb-Blubb“), Wisch-Blende mit Tempo-Streifen ('whip'), Zoom-Blende ('zoom').
    Schnitte IM Satz sind harte Schnitte mit kurzem Zoom-Setzen ('cut'); 'snap' = harter Schnitt mit Blitz (nur Hook/Höhepunkt).
  - Töne automatisch: 'ink' an der Tinten-Blende, 'whoosh' an Wisch/Zoom, 'hit' bei Wacklern und 'snap' (reine Töne, kein Rauschen).
  - Comic-Raster (Punkte) in den Ecken jedes Hintergrunds, Tempolinien beim Einschlag, Sticker-Umrisse: eine Bildsprache.

Einschalten in episode.py:   EDIT = 2 · LOOK = 'cartoon' · KINO = True · LOOP = True · HOOK_TEXT = 'x' (nur Platzhalter:
                             hält die Untertitel bis HOOK_END zurück – den Hook setzt die Szene selbst mit K.slam)
Jede Szenenfunktion beginnt: i, lt, ld = K.begin(c, szene, t, d, marks=[...], punch=[...], shake=[...])
"""
import math
import subprocess
import numpy as np
import render as L
import edit2 as E2
import cartoon as C
from render import skia, W, H, P, clamp, ease_out, mixc

CAP_Y = 912                       # Grundlinie der Untertitel
HOST_X, HOST_Y, HOST_S = 460, 1320, 1.7
CLOSE_X, CLOSE_Y, CLOSE_S = 540, 1580, 2.7       # Nahaufnahme: FINN füllt das untere Bild (K.closeup)
STAGE = (540, 540)                # Mitte der Bühne = Zentrum der Kamera
FR = 1 / 30
T_IN = {'ink': 0.24, 'whip': 0.16, 'zoom': 0.18, 'snap': 0.12, 'cut': 0.12}
T_OUT = {'ink': 0.15, 'whip': 0.10, 'zoom': 0.10, 'snap': 0.0, 'cut': 0.0}
ORDER_SCENE = ['ink', 'ink', 'whip', 'zoom', 'ink', 'whip', 'zoom', 'cut', 'whip', 'zoom']   # Blende zu Beginn von Szene n (Satzgrenze)
ORDER_SHOT = ['cut']                                                                        # Schnitte IM Satz: harter Schnitt mit kurzem Zoom-Setzen
SCENE_TRANS = {}                  # episode.py darf einzelne Szenen festlegen, z. B. K.SCENE_TRANS = {4: 'ink'}
SHOT_TRANS = {}                   # … und einzelne Schnitte in einer Szene: K.SHOT_TRANS = {(0, 1): 'snap'}
_S = {'cur': None}
_FULL = skia.Rect.MakeXYWH(-80, -80, W + 160, H + 160)
_BIG = skia.Rect.MakeXYWH(-2000, -2000, W + 4000, H + 4000)

POSES = {   # (linker Arm, rechter Arm) in Grad: 0 = nach rechts, 90 = nach unten, 180 = nach links, -90/270 = nach oben
    'rest': (115, 65), 'hips': (150, 30), 'up': (115, -72), 'up_l': (252, 65), 'both_up': (250, -70),
    'wave': (215, -35), 'cheer': (238, -58), 'stop': (182, -2), 'shrug': (165, 15), 'point_r': (120, -25),
    'point_l': (205, 60), 'think': (115, -105),
}


# ---------------------------------------------------------------- Bewegungskurven
def pop(u, f=4.6, z=0.52):
    """Feder 0→1 mit Überschwingen (u = Sekunden seit Start). Für alles, was „reinploppt“."""
    if u <= 0:
        return 0.0
    w = 2 * math.pi * f; wd = w * math.sqrt(1 - z * z)
    return 1 - math.exp(-z * w * u) * (math.cos(wd * u) + z * w / wd * math.sin(wd * u))


def back(x, s=1.9):
    """0→1 mit kurzem Überschwingen am Ende (x = 0..1)."""
    x = clamp(x) - 1
    return x * x * ((s + 1) * x + s) + 1


def wig(amp=6.0, speed=1.6, phase=0.0):
    """Kleines Schweben, damit nichts stillsteht."""
    return amp * math.sin(L.NOW * speed * 2 * math.pi / 2 + phase)


# ---------------------------------------------------------------- Stimme → Mundbewegung
_ENV = None


def _env():
    global _ENV
    if _ENV is None:
        try:
            raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', 'voice.mp3', '-ac', '1', '-ar', '8000', '-f', 's16le', '-'],
                                 capture_output=True).stdout
            a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
            n = 8000 // 60
            r = np.sqrt(np.mean(a[:len(a) // n * n].reshape(-1, n) ** 2, axis=1))
            _ENV = np.clip(r / (np.percentile(r, 90) + 1e-6), 0, 1.4)
        except Exception:
            _ENV = np.zeros(1, np.float32)
    return _ENV


def mouth(T):
    """Mundöffnung 0..1 aus der Lautstärke der Stimme (60 Werte pro Sekunde)."""
    e = _env(); i = int(T * 60)
    if i < 1 or i >= len(e):
        return 0.0
    return clamp((max(float(e[i]), 0.55 * float(e[i - 1])) - 0.10) * 1.2)


def _word_age(T):
    """Sekunden seit dem Anfang des gerade gesprochenen Wortes (99, wenn gerade nicht gesprochen wird)."""
    try:
        import wordsubs as WS
        last = None
        for w_ in WS.WORDS:
            if w_['start'] - 0.03 <= T:
                last = w_
            else:
                break
        if last is not None and T <= last['end'] + 0.12:
            return T - (last['start'] - 0.03)
    except Exception:
        pass
    return 99.0


def host(c, t, mood='happy', pose='rest', x=None, y=None, s=None, look=(0, 0), jump=0.0, lean=0.0, talk=True, **kw):
    """FINN als Moderator: spricht (Mund folgt der Stimme), federt auf jedes Wort. jump = Pixel nach oben."""
    T = L.NOW
    x = HOST_X if x is None else x; y = HOST_Y if y is None else y; s = HOST_S if s is None else s
    al, ar = POSES.get(pose, POSES['rest'])
    wob = math.sin(T * 9.0) * 7 if pose in ('wave', 'cheer', 'both_up') else math.sin(T * 3.1) * 2.5
    nod = math.exp(-_word_age(T) * 15)
    sx, sy = 1 + 0.03 * nod, 1 - 0.035 * nod
    if jump:
        sx, sy = sx - 0.04, sy + 0.06
    foot = y + 188 * s
    c.save(); c.translate(x, foot - jump); c.scale(sx, sy); c.translate(-x, -foot)
    kw.setdefault('blink', mood != 'shock')            # im Schreck-Moment bleiben die Augen offen (kein Blinzeln auf dem Höhepunkt)
    L.finn(c, x, y, s, T + 0.6, mood=mood, arm_l=al + wob, arm_r=ar - wob, look=look, lean=lean,
           talk=(mouth(T) if talk else None), **kw)
    c.restore()


# ---------------------------------------------------------------- Hintergrund
def rays(c, cx, cy, color, deg, n=14, a=255):
    for k in range(n):
        a0 = math.radians(deg + k * 360 / n); a1 = a0 + math.radians(180 / n)
        p = skia.Path(); p.moveTo(cx, cy)
        p.lineTo(cx + 3200 * math.cos(a0), cy + 3200 * math.sin(a0)); p.lineTo(cx + 3200 * math.cos(a1), cy + 3200 * math.sin(a1)); p.close()
        c.drawPath(p, P(color, a))


def halftone(c, color, ox, oy, reach=1150, a=255, grid=50, rmax=15):
    """Comic-Raster: Punkte, die von der Ecke (ox, oy) aus kleiner werden und nach `reach` Pixeln auslaufen.
    Gehört zum Markenbild (Tinte/Comic) und wandert ganz langsam, damit kein Hintergrund stillsteht."""
    T = L.NOW; dx = (T * 7) % grid; dy = (T * 4) % grid
    pa = P(color, a)
    for j in range(-1, int(H / grid * 0.866) + 6):
        y = j * grid * 0.866 + dy
        for i in range(-1, W // grid + 3):
            x = i * grid + (grid / 2 if j % 2 else 0) + dx
            r = rmax * (1 - math.hypot(x - ox, y - oy) / reach)
            if r > 1.2:
                c.drawCircle(x, y, r, pa)


def stage(c, kind='cream', tint='vio'):
    """Hintergrund nach Farbrolle: 'yel' = Hook/Alarm (gelbe Strahlen) · 'cream' = Erklären (zarte Flecken in tint) ·
    'vio' = Schlüsselzahl/Einschlag (violette Strahlen). Dazu das Comic-Raster in den Ecken und unten immer der Boden,
    auf dem FINN steht."""
    T = L.NOW
    if kind == 'yel':
        c.drawRect(_BIG, P(C.YEL)); rays(c, 540, 860, '#ffd968', T * 10); fl = C.YEL_D
        halftone(c, '#f7b425', W + 40, -40, 900); halftone(c, '#f7b425', -40, 1500, 760)
    elif kind == 'vio':
        c.drawRect(_BIG, P(C.VIO)); rays(c, 540, 600, '#9b74ff', -T * 10); fl = '#6a3fe0'
        halftone(c, '#7646ea', W + 40, -40, 900); halftone(c, '#7646ea', -40, 1500, 760)
    else:
        C.bg(c, tint); fl = mixc(C.CREAM2, '#f3bd62', 0.4)
        a, b = C.TINTS.get(tint, C.TINTS['vio'])
        halftone(c, mixc(a, C.INK, 0.10), W + 40, -40, 1000); halftone(c, mixc(C.CREAM2, '#f3bd62', 0.55), -40, 1500, 760)
    c.drawOval(skia.Rect.MakeXYWH(-420, 1350, 1920, 1000), P(fl))


def closeup(c, t, mood='happy', pose='think', lean=0.0, look=(0, -0.4), **kw):
    """NAHAUFNAHME: FINN groß von unten ins Bild (Kopf und Oberkörper) – für Bindewörter wie „Der Grund:“, „Ausnahme:“."""
    host(c, t, mood=mood, pose=pose, x=CLOSE_X, y=CLOSE_Y, s=CLOSE_S, lean=lean, look=look, **kw)


def mark(c, lt, ch='?', t0=0.0, x=540, y=560, size=560, fill=None, rot=-8):
    """Riesiges Satzzeichen als Sticker ('?' oder '!') über FINNs Nahaufnahme – ploppt rein und wackelt."""
    u = lt - t0
    if u < 0:
        return
    L.sfx('pop', ('mark', ch, round(t0, 2)))
    k = 1.0 if L.SAFE_CHECK else pop(u, 4.2, 0.45)
    f = C._font(size); w = f.measureText(ch)
    c.save(); c.translate(x, y - size * 0.36); c.rotate(rot + (0 if L.SAFE_CHECK else 5 * math.sin(L.NOW * 5))); c.scale(max(k, 0.01), max(k, 0.01))
    c.translate(-x, -(y - size * 0.36))
    c.drawString(ch, x - w / 2 + 16, y + 18, f, P(C.INK, 255, stroke=44))
    c.drawString(ch, x - w / 2, y, f, P(C.INK, 255, stroke=44))
    c.drawString(ch, x - w / 2, y, f, P(C.WHITE, 255, stroke=18))
    c.drawString(ch, x - w / 2, y, f, P(fill or C.YEL))
    c.restore()


# ---------------------------------------------------------------- Kamera + Blenden
def _trans_scene(scene):
    return SCENE_TRANS.get(scene, ORDER_SCENE[scene % len(ORDER_SCENE)])


def _trans_shot(scene, i):
    return SHOT_TRANS.get((scene, i), ORDER_SHOT[(scene + i) % len(ORDER_SHOT)])


def _when(scene, w):
    """Szenen-Zeit eines Wortes ('wort' oder ('wort', nth)) oder einer festen Zeit; None, wenn nicht gefunden."""
    if isinstance(w, (int, float)):
        return float(w)
    word, nth = (w, 0) if isinstance(w, str) else w
    v = L.word_t(scene, word, nth=nth, default=None)
    return None if v is None else max(0.0, v - 0.04)


def at(scene, w, t, lt, default=0.0):
    """Zeit eines gesprochenen Wortes, gemessen ab dem letzten Schnitt (passt zu lt). default, wenn das Wort fehlt."""
    v = _when(scene, w)
    return default if v is None else v - (t - lt)


def begin(c, scene, t, d, marks=(), punch=(), step=(), shake=(), focus=None):
    """Am Anfang JEDER Szenenfunktion aufrufen (vor dem ersten Zeichnen).
    marks  = Schnitte an diesen Wörtern (wie E2.shots) → jeder Schnitt bekommt automatisch eine Blende.
    punch  = Zoom-Stoß genau auf diesen Wörtern (kurz rein, federt zurück).
    step   = Zoom-Stufe ab diesem Wort (bleibt bis zum nächsten Schnitt näher dran).
    shake  = Wackler + Einschlag-Blitz auf diesen Wörtern (für Stempel, Zahlen, „abgelehnt“).
    Rückgabe wie E2.shots: (Nummer der Einstellung, Zeit seit dem Schnitt, Länge der Einstellung)."""
    i, lt, ld = E2.shots(scene, t, d, list(marks)) if marks else (0, t, d)
    off = t - lt
    last_shot = off + ld >= d - 1e-3
    tin = None if (scene == 0 and i == 0) else (_trans_scene(scene) if i == 0 else _trans_shot(scene, i))
    if last_shot:
        tout = None if scene == len(L.DUR) - 1 else _trans_scene(scene + 1); nxt = (scene + 1, 0)
    else:
        tout = _trans_shot(scene, i + 1); nxt = (scene, i + 1)
    if tin == 'ink':
        L.sfx('ink', ('tr', i), off - 0.12)             # Markenton der Tinten-Blende („Blubb-Blubb“)
    elif tin in ('whip', 'zoom'):
        L.sfx('whoosh', ('tr', i), off - 0.05)
    elif tin == 'snap':
        L.sfx('hit', ('tr', i), off)
    st = dict(sc=c.getSaveCount(), scene=scene, lt=lt, ld=ld, tin=tin, tout=tout, flash=None, seed=scene * 7 + i,
              sgn_in=(1 if (scene + i) % 2 == 0 else -1), sgn_out=(1 if sum(nxt) % 2 == 0 else -1))
    _S['cur'] = st
    c.save()
    if L.SAFE_CHECK:                                   # Layout-Prüfungen sehen das Bild in Ruhe (ohne Kamera/Blenden)
        return i, lt, ld
    if isinstance(focus, list):                        # je Einstellung ein eigenes Zentrum, z. B. [(540, 1150), None]
        focus = focus[min(i, len(focus) - 1)]
    fx, fy = focus or STAGE
    z = 1.0 + 0.016 * lt; dx = dy = rot = 0.0; bx = by = 0.0
    for w in punch:
        v = _when(scene, w)
        if v is not None and 0 <= t - v < 1.2:
            u = t - v; z += 0.075 * min(1.0, u / 0.05) * math.exp(-u * 6.5)
    for w in step:
        v = _when(scene, w)
        if v is not None and off <= v <= t:
            z += 0.09 * back((t - v) / 0.14)
    for w in shake:
        v = _when(scene, w)
        if v is not None and off <= v <= t:
            L.sfx('hit', ('shake', str(w)), v)
            u = t - v
            if u < 0.4:
                a = 20 * math.exp(-u * 10)
                dx += a * math.sin(u * 92); dy += 0.7 * a * math.cos(u * 81); rot += 0.5 * math.sin(u * 70) * math.exp(-u * 10)
            if u < 0.22:
                st['flash'] = u if st['flash'] is None else min(st['flash'], u)
    if tin and lt < T_IN[tin]:
        v = lt / T_IN[tin]; e = 1 - ease_out(v); sgn = 1 if (scene + i) % 2 == 0 else -1
        if tin == 'whip':
            dx += sgn * W * 0.85 * e; bx = 60 * (1 - v)
        elif tin == 'zoom':
            z *= 1 - 0.28 * e; bx = by = 20 * (1 - v)
        elif tin == 'snap':
            z *= 1 + 0.10 * e
        elif tin == 'cut':
            z *= 1 + 0.07 * e
        else:
            z *= 1 + 0.05 * e
    r = ld - lt
    if tout and T_OUT[tout] > 0 and r < T_OUT[tout] + FR:
        v = clamp(1 - (r - FR) / T_OUT[tout]); e = v * v; sgn = 1 if sum(nxt) % 2 == 0 else -1
        if tout == 'whip':
            dx -= sgn * W * 0.85 * e; bx = max(bx, 60 * v)
        elif tout == 'zoom':
            z *= 1 + 0.55 * e; bx = by = max(bx, 20 * v)
    if (bx > 0.5 or by > 0.5) and L.SFX_REC is None:
        bp = skia.Paint(); bp.setImageFilter(skia.ImageFilters.Blur(bx, by)); c.saveLayer(None, bp)
    c.translate(fx + dx, fy + dy); c.rotate(rot); c.scale(z, z); c.translate(-fx, -fy)
    return i, lt, ld


def finish(c, scene, t, d):
    """Ruft pipeline.py nach jeder Szene auf: Kamera-Ebenen schließen, Tinten-Blende und Einschlag-Blitz zeichnen."""
    st = _S.get('cur'); _S['cur'] = None
    if not st or st['scene'] != scene:
        return
    c.restoreToCount(st['sc'])
    if L.SAFE_CHECK or L.SFX_REC is not None:
        return
    lt, r = st['lt'], st['ld'] - st['lt']
    if st['flash'] is not None:
        impact(c, st['flash'])
    if st['tin'] == 'whip' and lt < T_IN['whip']:
        streaks(c, 1 - lt / T_IN['whip'], st['sgn_in'])
    if st['tout'] == 'whip' and r < T_OUT['whip'] + FR:
        streaks(c, clamp(1 - (r - FR) / T_OUT['whip']), st['sgn_out'])
    if st['tin'] == 'snap' and lt < 0.1:
        c.drawRect(_FULL, P('#ffffff', int(120 * (1 - lt / 0.1))))
    if st['tout'] == 'ink' and r < T_OUT['ink'] + FR:
        ink(c, clamp(1 - (r - FR) / T_OUT['ink']), True, st['seed'])
    if st['tin'] == 'ink' and lt < T_IN['ink']:
        ink(c, lt / T_IN['ink'], False, st['seed'])


_BLOBS = {}


def _blobs(seed):
    if seed not in _BLOBS:
        rs = np.random.RandomState(1000 + seed)
        pts = [(W / 2 + rs.uniform(-100, 100), H / 2 + rs.uniform(-160, 160), 1400.0)]
        pts += [(rs.uniform(0, W), rs.uniform(0, H), rs.uniform(520, 900)) for _ in range(8)]
        pts += [(rs.uniform(0, W), rs.uniform(0, H), rs.uniform(60, 170)) for _ in range(12)]     # Spritzer
        _BLOBS[seed] = pts
    return _BLOBS[seed]


def _blob_path(pts, k):
    p = skia.Path()
    for x, y, r in pts:
        if r * k > 1:
            p.addCircle(x, y, r * k)
    return p


def ink(c, u, out, seed=0):
    """TINTEN-BLENDE (Markenzeichen). out=True: Tinte breitet sich aus, bis das Bild zu ist (gelb voraus, violett deckt).
    out=False: die Tinte reißt auf und gibt das neue Bild frei (violett zuerst, gelber Rand folgt)."""
    pts = _blobs(seed)
    if out:
        c.drawPath(_blob_path(pts, clamp(u / 0.75) ** 1.5), P(C.YEL))
        c.drawPath(_blob_path(pts, clamp((u - 0.2) / 0.8) ** 1.5), P(C.VIO))
    else:
        for k, colr in ((ease_out(clamp((u - 0.18) / 0.82)), C.YEL), (ease_out(clamp(u / 0.8)), C.VIO)):
            c.save(); c.clipPath(_blob_path(pts, k), skia.ClipOp.kDifference, True); c.drawRect(_FULL, P(colr)); c.restore()


_LINES = np.random.RandomState(7).uniform(0, 1, (26, 3))


def impact(c, u):
    """Einschlag-Bild wie im Comic: kurzer weißer Blitz + Tempolinien, die vom Rand zur Bildmitte zeigen
    (als Ellipse um die Bildmitte, damit sie im Hochformat rundum stehen – nicht nur unten)."""
    cx, cy = W / 2, H / 2
    if u < 0.067:
        c.drawRect(_FULL, P('#ffffff', int(160 * (1 - u / 0.067))))
    if u < 0.22:
        a = int(215 * (1 - u / 0.22))
        for k in range(30):
            an = (k + _LINES[k % 26][0] * 0.6) / 30 * 2 * math.pi; q = 1 + 0.22 * _LINES[k % 26][1] + 0.9 * u
            w = 0.010 + 0.016 * _LINES[k % 26][2]
            p = skia.Path(); p.moveTo(cx + 470 * q * math.cos(an), cy + 880 * q * math.sin(an))
            p.lineTo(cx + 1900 * math.cos(an - w), cy + 3400 * math.sin(an - w)); p.lineTo(cx + 1900 * math.cos(an + w), cy + 3400 * math.sin(an + w)); p.close()
            c.drawPath(p, P(C.INK, a))


_STREAK = np.random.RandomState(11).uniform(0, 1, (14, 4))


def streaks(c, k, sgn=1):
    """Wisch-Blende: Tempo-Streifen quer durchs Bild (k = Stärke 0..1, sgn = Richtung). Füllt die 2–3 Bilder,
    in denen das alte Bild schon weg und das neue noch nicht da ist."""
    if k <= 0.02:
        return
    cols = (C.WHITE, C.YEL, C.VIO, C.INK)
    for n in range(14):
        r = _STREAK[n]; y = 60 + (n + 0.5 * r[0]) / 14 * (H - 120); ln = 520 + 900 * r[1]; h = 16 + 44 * r[2]
        x = (r[3] * (W + ln) - ln) - sgn * (1 - k) * 1100 * (0.6 + r[1])
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, ln, h), h / 2, h / 2), P(cols[n % 4], int(235 * min(1.0, k * 1.5))))


# ---------------------------------------------------------------- Auftritte (alles kommt mit Schwung ins Bild)
def show(c, lt, t0, x, y, draw, kind='pop', snd='pop', key=None):
    """Zeichnet draw(c) erst ab t0 und mit Auftritt um den Punkt (x, y):
    'pop' = ploppt auf (Feder) · 'slam' = knallt von groß auf normal · 'drop' = fällt von oben und staucht ·
    'left'/'right' = schießt von der Seite rein · 'none' = einfach da. Rückgabe: 0, solange unsichtbar."""
    u = lt - t0
    cur = _S.get('cur')
    if t0 <= 0.02 and cur and cur.get('tin') in ('cut', 'snap'):      # harter Schnitt: das Motiv ist schon im ersten Bild (fast) da,
        u += {'pop': 0.06, 'left': 0.14, 'right': 0.14, 'drop': 0.15}.get(kind, 0.0)   # sonst flackert ein leeres Bild auf
    if u < 0:
        return 0.0
    if snd:
        L.sfx(snd, ('show', key or (round(x), round(y)), round(t0, 2)))
    k = pop(u)
    if L.SAFE_CHECK:
        draw(c); return 1.0
    c.save(); c.translate(x, y)
    if kind == 'pop':
        c.rotate(-8 * (1 - min(1.0, k))); c.scale(max(k, 0.01), max(k, 0.01))
    elif kind == 'slam':
        s = 2.4 - 1.4 * pop(u, 5.4, 0.66) if u < 0.6 else 1.0; c.scale(s, s)
    elif kind == 'drop':
        v = clamp(u / 0.2); c.translate(0, -1100 * (1 - v * v))
        if u > 0.2:
            q = math.exp(-(u - 0.2) * 16); c.scale(1 + 0.14 * q, 1 - 0.16 * q)
    elif kind in ('left', 'right'):
        c.translate((-1 if kind == 'left' else 1) * 1100 * (1 - back(u / 0.3, 1.4)), 0)
    c.translate(-x, -y)
    draw(c)
    c.restore()
    return max(k, 0.01)


def slam(c, s, lt, t0, x, y, size, color=None, box=None, rot=-3.0, maxw=960, snd='thud'):
    """HOOK-/Schlagzeile: knallt genau auf dem gesprochenen Wort ins Bild. box = Farbe des Marker-Kastens (oder None = Sticker-Schrift)."""
    u = lt - t0
    if u < 0:
        return
    if snd:
        L.sfx(snd, ('slam', s, round(t0, 2)))
    f, size = C.fit(s, size, maxw); w = f.measureText(s)
    sc = 2.3 - 1.3 * pop(u, 5.4, 0.66) if u < 0.6 else 1.0
    al = int(255 * clamp(u / 0.04 + 0.2))
    if L.SAFE_CHECK:
        sc, rot = 1.0, 0.0
    cy = y - size * 0.34
    c.save(); c.translate(x, cy); c.rotate(rot); c.scale(sc, sc); c.translate(-x, -cy)
    if box:
        pad = size * 0.16
        C.box(c, x - w / 2 - pad, y - size * 0.86, w + 2 * pad, size * 1.12, box, r=size * 0.18, out=10, shadow=12, a=al)
        c.drawString(s, x - w / 2, y, f, P(color or C.INK, al))
    else:
        st = min(size * 0.2, 24)
        c.drawString(s, x - w / 2 + 7, y + 9, f, P(C.INK, al, stroke=st))
        c.drawString(s, x - w / 2, y, f, P(C.INK, al, stroke=st))
        c.drawString(s, x - w / 2, y, f, P(color or C.WHITE, al))
    c.restore()


def count(lt, t0, v0, v1, dur=0.6, key='zahl'):
    """Zahl läuft hoch/runter (mit Klick-Ton). Rückgabe: aktueller Wert."""
    if lt >= t0:
        L.sfx('count', (key, dur))
    return v0 + (v1 - v0) * ease_out(clamp((lt - t0) / dur))


# ---------------------------------------------------------------- Untertitel (von cartoon.subs aufgerufen)
def subs(c, T, WS, t_from=0.0):
    """1–3 Wörter, GROSS, im Band über FINN. Jedes Häppchen ploppt rein und kippt abwechselnd leicht nach links/rechts.
    Das gerade gesprochene Wort sitzt im gelben Marker-Kasten, Schlüsselwörter (HIGHLIGHT) im violetten."""
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
    if T > min(nxt, WS.WORDS[g[-1]]['end'] + 0.6):
        return
    words = [WS.WORDS[k]['text'].upper() for k in g]
    size = 110; f = C._font(size); sp = size * 0.26
    wid = lambda: sum(f.measureText(s) for s in words) + sp * (len(words) - 1)
    while wid() > 860 and size > 44:
        size -= 2; f = C._font(size); sp = size * 0.26
    tw = wid()
    u = T - (WS.WORDS[g[0]]['start'] - 0.06)
    sc = 1.0 if L.SAFE_CHECK else 0.55 + 0.45 * pop(u, 5.5, 0.5)
    rot = 0.0 if L.SAFE_CHECK else (-2.0 if idx % 2 == 0 else 2.0)
    y = CAP_Y; cy = y - size * 0.36
    act = None
    for k in g:
        if T >= WS.WORDS[k]['start'] - 0.05:
            act = k
    c.save(); c.translate(W / 2, cy); c.rotate(rot); c.scale(sc, sc); c.translate(-W / 2, -cy)
    x = W / 2 - tw / 2
    st = min(size * 0.22, 22)
    for k, s in zip(g, words):
        w_ = WS.WORDS[k]; ww = f.measureText(s)
        key = WS.strip(w_['text']).lower() in WS.HL
        if k == act:
            pad = size * 0.13
            C.box(c, x - pad, y - size * 0.85, ww + 2 * pad, size * 1.1, C.VIO if key else C.YEL, r=size * 0.2, out=8, shadow=9)
            c.drawString(s, x, y, f, P(C.WHITE if key else C.INK))
        else:
            said = T >= w_['start'] - 0.05
            c.drawString(s, x + 6, y + 8, f, P(C.INK, 255, stroke=st))
            c.drawString(s, x, y, f, P(C.INK, 255, stroke=st))
            c.drawString(s, x, y, f, P(C.WHITE, 255 if said else 185))
        x += ww + sp
    c.restore()


# ---------------------------------------------------------------- Serien (seit 26.11.2026)
# episode.py:  SERIE = ('kleingedruckt', 1)   ·   ('mythos', 3)   ·   ('test', 2)
# Wirkt automatisch: FINN-Outfit (render.OUTFIT), Titelkarte „REIHE #Nr“ während des Hooks (unten, wo später die
# Untertitel stehen), Serienfarbe für Akzente (SERIEN[...]['farbe'] – in eigenen Motiven als K.SF verwenden).
SERIEN = {
    'kleingedruckt': dict(name='KLEINGEDRUCKT', farbe='#ef4444', zweit='#ffc93a', outfit='detektiv', slot='11:30'),
    'mythos':        dict(name='MYTHOS ODER FAKT?', farbe='#14b8a6', zweit='#4f8cff', outfit='forscher', slot='17:30'),
    'test':          dict(name='MACH DEN TEST', farbe='#f97316', zweit='#8a5cf6', outfit='sport', slot='20:00'),
}
SF, SF2 = '#8a5cf6', '#ffc93a'          # aktuelle Serienfarbe / Zweitfarbe (setzt serie_setup)


def serie_setup(serie):
    global SF, SF2
    if not serie:
        L.OUTFIT = None; return
    key = serie[0]; cfg = SERIEN[key]
    L.OUTFIT = cfg['outfit']; SF, SF2 = cfg['farbe'], cfg['zweit']


def serie_card(c, T, hook_end, serie, y=1462):
    """Titelkarte „KLEINGEDRUCKT #4“ ab Bild 0 bis zum Hook-Ende (unten, im Untertitel-Band, das bis dahin frei ist)."""
    if not serie or T > hook_end + 0.2:
        return
    cfg = SERIEN[serie[0]]
    a = 1.0 if T <= hook_end else 1 - (T - hook_end) / 0.2
    if a <= 0:
        return
    k = 1.0 if (T > 0.25 or L.SAFE_CHECK) else 0.6 + 0.4 * pop(T / 0.25, 5.0, 0.6)
    name, nr = cfg['name'], f'#{serie[1]}'
    f1, s1 = C.fit(name, 64, 600); f2 = C._font(64)
    w1, w2 = f1.measureText(name), f2.measureText(nr)
    pad, gap, h = 34, 26, 104
    wt = w1 + w2 + gap + 2 * pad + 30
    x0 = 540 - wt / 2
    c.save(); c.translate(540, y); c.scale(k, k); c.rotate(-2); c.translate(-540, -y)
    c.saveLayerAlpha(None, int(255 * a))
    C.box(c, x0, y - h / 2, wt, h, cfg["farbe"], r=h / 2)
    nb = w2 + 40
    C.box(c, x0 + wt - nb - 14, y - h / 2 + 12, nb, h - 24, C.WHITE, r=(h - 24) / 2, out=6, shadow=0)
    C.text(c, name, x0 + pad + w1 / 2, y + 22, s1, C.WHITE, maxw=620)
    C.text(c, nr, x0 + wt - nb / 2 - 14, y + 22, 58, C.INK)
    c.restore(); c.restore()
