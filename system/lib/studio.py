"""FAKTENFABRIK – Look „STUDIO“ (von Lukas am 28.11.2026 gewählt: Mischung aus Test-Look 1 „KLAR“ und 2 „MINIATUR“).

Helle, klare Bühne (Papier mit Punktraster, Tintenschrift, EINE Signalfarbe, Untertitel in dunkler Pille)
+ kleine 3D-Welt auf einer Petrol-Plattform (Objekte mit Licht und Schatten, langsame Kamerafahrt).
Kein Maskottchen, kein Gelb, wenig Text, das Bild hüpft und wackelt nicht.

Eine Folge = Ordner mit voice.mp3, words.json, paras.json, script.txt und episode.py:

    import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
    from studio import *
    import props as PR
    SERIE, NAME = ('kleingedruckt', 4), 'Gutschein'
    def draw(c, t):
        st = Stage(c, t); st.begin()
        ...                      # 3D-Objekte mit st.add(...)
        st.end()
        ...                      # flache Ebene: headline(), label(), banner(), stamp()
        finish(c, t, SERIE)      # Kopfzeile + Untertitel
    if __name__ == '__main__':
        main(draw, SERIE, NAME)

Befehle (im Episodenordner):
    python3 episode.py timing            durs.json, voice.json, scene_starts.json, para_word_idx.json (danach hookcheck.py)
    python3 episode.py sheet [schritt]   Kontaktbögen sheet_0.png … (Standard alle 1,0 s)
    python3 episode.py big 0 2.5 7       big.png mit großen Einzelbildern
    python3 episode.py still 3.2         still_3.20.png (1080×1920)
    python3 episode.py check             Sperrzonen, Überlappungen, Länge, erstes Bild -> „STUDIOCHECK OK“
    python3 episode.py audio             mix.wav + music_credit.txt
    python3 episode.py render [hd]       FAKTENFABRIK_<Name>.mp4 (4K) und FAKTENFABRIK_<Name>_IG.mp4 (Full HD); „hd“ = schnelle Vorschau
    python3 episode.py render teil 1     nur die zweite Hälfte neu bauen (teil 0 = erste Hälfte)
    python3 episode.py thumb [t]         thumb.png (Titelbild aus dem Video)
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import wave
from math import sin, cos, pi, radians

import numpy as np
import skia

W, H, FPS = 1080, 1920, 30
LIB = os.path.dirname(os.path.abspath(__file__))
SYS = os.path.dirname(LIB)
FD = os.path.join(SYS, 'assets', 'fonts') + os.sep
_INTER = '/usr/share/fonts/opentype/inter/'
FONTFILES = {'black': 'InterDisplay-Black.otf', 'bold': 'InterDisplay-Bold.otf', 'med': 'InterDisplay-Medium.otf',
             'mono': 'IBMPlexMono-SemiBold.ttf', 'monom': 'IBMPlexMono-Medium.ttf', 'cond': 'BarlowCondensed-ExtraBold.ttf'}

# ---------------------------------------------------------------- Farben (eine Palette für alle Reihen)
PAPER, INK, MUTE, WHITE = '#F2F1ED', '#10242A', '#8B8F97', '#FFFFFF'
ACC, ACC_L, ACC_D = '#EC4B31', '#FF6A4E', '#C2371A'              # Signalfarbe (Koralle) – sparsam: Zahl, Akzent, Ergebnis
PETROL, PETROL_D, PETROL_L = '#1B5963', '#0F3A42', '#6FB6BF'      # Plattform
GREEN, AMBER = '#2FA36B', '#E9A220'                               # nur für Urteile: FAKT / HALB WAHR (MYTHOS = ACC)
OBJ, OBJ_CREAM, OBJ_GREY, OBJ_GREY_D, OBJ_DARK = '#FFFFFF', '#F7F4EC', '#D9DEE3', '#B7BFC7', '#22343A'
GOLD, GOLD_D = '#F2C14E', '#C99A2E'
SERIEN = {'kleingedruckt': 'KLEINGEDRUCKT', 'mythos': 'MYTHOS ODER FAKT?', 'test': 'MACH DEN TEST'}

_TF = {}


def font(name, size):
    if name not in _TF:
        fn = FONTFILES[name]; p = FD + fn
        if not os.path.exists(p):
            p = _INTER + fn
        _TF[name] = skia.Typeface.MakeFromFile(p); assert _TF[name], 'Schrift fehlt: ' + p
    f = skia.Font(_TF[name], size); f.setSubpixel(True); f.setEdging(skia.Font.Edging.kAntiAlias)
    return f


def C(h, a=1.0):
    h = h.lstrip('#'); return skia.Color(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), int(max(0.0, min(1.0, a)) * 255))


def mix(h1, h2, t):
    a = [int(h1.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)]; b = [int(h2.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)]
    t = max(0.0, min(1.0, t)); return '#%02x%02x%02x' % tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def P(color, a=1.0, stroke=None, butt=False, miter=False, blur=None):
    p = skia.Paint(AntiAlias=True); p.setColor(C(color, a))
    if stroke is not None:
        p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(stroke)
        p.setStrokeCap(skia.Paint.kButt_Cap if butt else skia.Paint.kRound_Cap)
        p.setStrokeJoin(skia.Paint.kMiter_Join if miter else skia.Paint.kRound_Join)
    if blur:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    return p


def lin(x0, y0, x1, y1, cols, pos=None):
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeLinear([skia.Point(x0, y0), skia.Point(x1, y1)], cols, pos)); return p


def rad(cx, cy, r, cols, pos=None):
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeRadial(skia.Point(cx, cy), r, cols, pos)); return p


# ---------------------------------------------------------------- Bewegung (weich, nichts hüpft)
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def lerp(a, b, t): return a + (b - a) * t
def pr(t, t0, dur): return clamp((t - t0) / dur)                 # Fortschritt 0..1 ab t0 über dur Sekunden
def eo3(t): t = clamp(t); return 1 - (1 - t) ** 3
def ei2(t): t = clamp(t); return t * t
def ei3(t): t = clamp(t); return t * t * t
def eio(t): t = clamp(t); return 4 * t * t * t if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2
def back(t, s=1.25): t = clamp(t) - 1; return 1 + t * t * ((s + 1) * t + s)          # weiches Überschwingen


_SFX = {}


def snd(t0, kind, gain=1.0):
    """Effekt-Ton anmelden (pop, thud, tick, swipe, type, ding, whoosh, hit). Doppelte Anmeldungen zählen einmal."""
    _SFX[(round(float(t0), 2), kind)] = gain


def rise(t, t0, dur=0.40, sound='pop', gain=0.55):
    """0..1 mit weichem Überschwingen – für alles, was aus der Plattform wächst oder aufploppt."""
    if sound:
        snd(t0, sound, gain)
    return back(pr(t, t0, dur), 1.3) if t >= t0 else 0.0


def sink(t, t0, dur=0.45, sound=None, gain=0.35):
    """0..1 beschleunigend – für alles, was in die Plattform zurückfährt (1 = weg)."""
    if sound:
        snd(t0, sound, gain)
    return ei3(pr(t, t0, dur))


def drop(t, t0, h=260.0, dur=0.25, sound='tick', gain=1.0):
    """Resthöhe über dem Ziel: fällt ab t0 aus Höhe h und landet nach dur Sekunden."""
    if sound:
        snd(t0 + dur, sound, gain)
    return h * (1 - ei2(pr(t, t0, dur)))


def pop(t, t0, dur=0.26, sound='pop', gain=0.8):
    """Fortschritt 0..1 für Etiketten/Banner (die Helfer rechnen das Überschwingen selbst)."""
    if sound:
        snd(t0, sound, gain)
    return pr(t, t0, dur)


# ---------------------------------------------------------------- Zeiten aus der Aufnahme
TAIL = 0.30                     # Sekunden nach dem letzten Wort (Loop-Ende: kein Abspann)
_Wd = _Pa = _PI = None


def norm(s):
    return re.sub(r'[^\wäöüÄÖÜß]', '', s).lower()


def _load():
    global _Wd, _Pa, _PI
    if _Wd is None:
        raw = json.load(open('words.json', encoding='utf-8')); raw = raw['words'] if isinstance(raw, dict) else raw
        _Wd = [w for w in raw if w.get('type', 'word') == 'word' and not w['text'].startswith('[') and not w['text'].endswith(']')
               and w['text'] not in ('—', '-', '–')]
        _Pa = json.load(open('paras.json', encoding='utf-8'))
        _PI, i = [], 0
        for p in _Pa:
            first = [norm(x) for x in p.split() if norm(x)][:3]; found = None
            for k in range(i, len(_Wd)):
                if [norm(_Wd[j]['text']) for j in range(k, min(k + len(first), len(_Wd)))] == first:
                    found = k; break
            if found is None:
                raise SystemExit('Absatz-Anfang nicht im Transkript gefunden: ' + p[:40])
            _PI.append(found); i = found + 1
    return _Wd


def total():
    """Länge des Videos in Sekunden (letztes Wort + TAIL)."""
    return _load()[-1]['end'] + TAIL


def _prange(p):
    _load(); a = _PI[p - 1]; b = _PI[p] if p < len(_PI) else len(_Wd)
    return a, b


def ps(p):
    """Sekunde, in der Absatz p (1 = Hook) beginnt."""
    a, _ = _prange(p); return 0.0 if p == 1 else _Wd[a]['start']


def pe(p):
    """Sekunde, in der Absatz p endet."""
    _, b = _prange(p); return _Wd[b - 1]['end']


def wt(word, p=None, nth=0, end=False, default=None):
    """Sekunde, in der ein Wort gesprochen wird (Wortanfang genügt, Groß/Klein egal). p = Absatz 1..n (empfohlen)."""
    ws = _load(); a, b = _prange(p) if p else (0, len(ws)); key = norm(word); k = 0
    for i in range(a, b):
        if norm(ws[i]['text']).startswith(key):
            if k == nth:
                return ws[i]['end' if end else 'start']
            k += 1
    if default is not None:
        return default
    raise SystemExit(f'Wort „{word}“ nicht gefunden' + (f' in Absatz {p}' if p else ''))


# ---------------------------------------------------------------- flache Ebene (Stil von Look 1)
_REG = None                    # Liste der Texte der flachen Ebene (nur beim Prüfen gefüllt)


def _reg(kind, txt, l, t, r, b):
    if _REG is not None:
        _REG.append((kind, txt, (l, t, r, b)))


def tw(s, f, track=0.0):
    return f.measureText(s) + track * max(0, len(s) - 1)


def text(c, s, x, y, f, paint, align='c', track=0.0):
    w = tw(s, f, track)
    x0 = x - w / 2 if align == 'c' else (x - w if align == 'r' else x)
    if track == 0:
        c.drawString(s, x0, y, f, paint)
    else:
        for ch in s:
            c.drawString(ch, x0, y, f, paint); x0 += f.measureText(ch) + track
    return w


def rrect(c, x, y, w, h, r, paint):
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), r, r), paint)


def chip(c, s, x, y, f, fg, bg, padx=18, pady=10, r=8, align='l', track=3.0, stroke=None, a=1.0):
    w = tw(s, f, track) + 2 * padx; h = f.getSize() * 0.72 + 2 * pady
    x0 = x - w / 2 if align == 'c' else (x - w if align == 'r' else x)
    rrect(c, x0, y, w, h, r, P(bg, a))
    if stroke:
        rrect(c, x0, y, w, h, r, P(stroke[0], a, stroke=stroke[1]))
    text(c, s, x0 + padx, y + pady + f.getSize() * 0.72, f, P(fg, a), 'l', track)
    return x0, y, w, h


def header(c, serie=None, folge=None):
    """Kopfzeile: Kanalname links, Reihe als Chip + Folgennummer rechts (die Reihe wird NICHT gesprochen)."""
    text(c, 'FAKTENFABRIK', 84, 268, font('mono', 25), P(INK), 'l', 7)
    if serie:
        nm = SERIEN.get(serie, str(serie).upper()); x = 996
        if folge is not None:
            w = text(c, '%02d' % int(folge), 996, 268, font('mono', 25), P(INK), 'r', 2); x = 996 - w - 16
        chip(c, nm, x, 238, font('mono', 22), WHITE, ACC, padx=16, pady=11, r=7, align='r', track=4)
    c.drawLine(84, 302, 996, 302, P(INK, 0.14, stroke=2.5))
    _reg('kopf', 'Kopfzeile', 84, 236, 996, 304)


def headline(c, big, small='', k=1.0, x=80, y=482, size=210, col=ACC, col2=INK, sub=None):
    """Große Zahl + Wort oben links (z. B. „3 JAHRE“). k = Fortschritt 0..1 (pop()). sub = kleine Zeile darunter."""
    if k <= 0:
        return
    f1, f2 = font('black', size), font('black', size * 0.533); w1 = f1.measureText(big); sc = lerp(0.88, 1.0, back(k, 1.5)); a = eo3(k)
    w2 = f2.measureText(small) if small else 0
    c.save(); c.translate(x, y); c.scale(sc, sc)
    c.drawString(big, 0, 0, f1, P(col, a))
    if small:
        c.drawString(small, w1 + size * 0.115, 0, f2, P(col2, a))
    c.restore()
    _reg('zahl', big + ' ' + small, x, y - size * 0.74, x + w1 + size * 0.115 + w2, y + 6)
    if sub:
        text(c, sub, x + 4, y + 62, font('bold', 44), P(col2, a), 'l')
        _reg('zahl2', sub, x + 4, y + 26, x + 4 + font('bold', 44).measureText(sub), y + 70)


def kicker(c, s, x=84, y=352, k=1.0, col=INK, size=28):
    """Kleine Mono-Zeile über einer großen Zahl (z. B. „DEIN GUTSCHEIN VON“ über „2023“)."""
    if k <= 0:
        return
    f = font('mono', size); w = text(c, s, x, y, f, P(col, eo3(k)), 'l', 4)
    _reg('zeile', s, x, y - size * 0.8, x + w, y + 6)


def banner(c, s, x, y, k=1.0, bg=ACC, fg=WHITE, size=36, align='l'):
    """Ergebnis-Banner (Mono-Schrift auf Farbfläche). x/y = linke obere Ecke (align 'l') bzw. Mitte ('c')."""
    if k <= 0:
        return
    f = font('mono', size); wb = tw(s, f, 3) + size * 1.45; hb = size * 2.1; sc = back(k, 1.5)
    cx = x + wb / 2 if align == 'l' else x
    c.save(); c.translate(cx, y + hb / 2); c.scale(sc, sc)
    rrect(c, -wb / 2, -hb / 2, wb, hb, size * 0.36, P(bg)); text(c, s, -wb / 2 + size * 0.72, size * 0.36, f, P(fg), 'l', 3)
    c.restore()
    _reg('banner', s, cx - wb / 2, y, cx + wb / 2, y + hb)


def label(c, ax, ay, s, dx, dy, k=1.0, fg=INK, bg=WHITE, size=30, a=1.0, edge=None):
    """Etikett (Mono-Schrift im Kästchen) mit Führungslinie zum Punkt (ax, ay). dx/dy = Versatz der Kästchen-Mitte."""
    if k <= 0 or a <= 0:
        return
    f = font('mono', size); w = tw(s, f, 2.5) + 40; x, y = ax + dx, ay + dy; hh = size + 30; edge = edge or fg
    x = clamp(x, 64 + w / 2, (866 if 930 < y + hh / 2 and y - hh / 2 < 1543 else 1013) - w / 2)       # nie unter die App-Knöpfe
    c.drawLine(ax, ay, x, y + (hh / 2 - 4) * (1 if dy < 0 else -1), P(INK, a * k, stroke=4))
    c.drawCircle(ax, ay, 8, P(INK, a * k)); c.drawCircle(ax, ay, 3.5, P(WHITE, a * k))
    c.save(); c.translate(x, y); c.scale(back(k, 1.5), back(k, 1.5))
    rrect(c, -w / 2, -hh / 2, w, hh, 10, P(bg, a)); rrect(c, -w / 2, -hh / 2, w, hh, 10, P(edge, a, stroke=5))
    text(c, s, -w / 2 + 20, size * 0.36, f, P(fg, a), 'l', 2.5)
    c.restore()
    if a > 0.5:
        _reg('etikett', s, x - w / 2, y - hh / 2, x + w / 2, y + hh / 2)


def stamp(c, s, x, y, k=1.0, col=ACC, size=120, angle=-7):
    """Urteil als Stempel (MYTHOS / FAKT / HALB WAHR): fällt weich auf seine Größe, steht dann still."""
    if k <= 0:
        return
    f = font('black', size); w = tw(s, f, 4) + size * 0.7; hh = size * 1.32; sc = lerp(1.5, 1.0, eo3(k)); a = eo3(pr(k, 0, 0.6))
    c.save(); c.translate(x, y); c.rotate(angle); c.scale(sc, sc)
    rrect(c, -w / 2, -hh / 2, w, hh, size * 0.16, P(WHITE, 0.92 * a))
    rrect(c, -w / 2, -hh / 2, w, hh, size * 0.16, P(col, a, stroke=size * 0.085))
    rrect(c, -w / 2 + size * 0.13, -hh / 2 + size * 0.13, w - size * 0.26, hh - size * 0.26, size * 0.09, P(col, a, stroke=size * 0.028))
    text(c, s, 0, size * 0.355, f, P(col, a), 'c', 4)
    c.restore()
    _reg('stempel', s, x - w / 2, y - hh / 2 - 12, x + w / 2, y + hh / 2 + 12)


def strike(c, x0, y0, x1, y1, k=1.0, col=ACC, width=14):
    """Durchstreichen (flach, auf dem Bildschirm)."""
    if k > 0:
        c.drawLine(x0, y0, lerp(x0, x1, eo3(k)), lerp(y0, y1, eo3(k)), P(col, 1.0, stroke=width))


_GR = None


def _groups():
    """Untertitel-Gruppen: 2–3 Wörter (höchstens ca. 24 Zeichen), Schnitt an Satzzeichen und Sprechpausen, keine einzelnen Restwörter."""
    global _GR
    if _GR is None:
        ws = _load(); _GR = []
        ln = lambda g: len(' '.join(x['text'] for x in g))
        for p in range(1, len(_PI) + 1):
            a, b = _prange(p); clauses, cur = [], []
            for i in range(a, b):
                cur.append(ws[i])
                gap = ws[i + 1]['start'] - ws[i]['end'] if i + 1 < b else 9
                if ws[i]['text'][-1:] in '.,:;!?–' or gap >= 0.30:
                    clauses.append(cur); cur = []
            if cur:
                clauses.append(cur)
            G = []
            for ci, cl in enumerate(clauses):
                gs, g = [], []
                for w in cl:                                             # gierig: bis 3 Wörter / 24 Zeichen
                    if g and (len(g) >= 3 or ln(g + [w]) > 24):
                        gs.append(g); g = []
                    g.append(w)
                if g:
                    gs.append(g)
                if len(gs) >= 2 and len(gs[-1]) == 1 and len(gs[-2]) == 3 and ln([gs[-2][-1]] + gs[-1]) <= 24:
                    gs[-1] = [gs[-2].pop()] + gs[-1]                     # 3+1 -> 2+2
                G.append(gs)
            flat = []
            for ci, gs in enumerate(G):                                  # Ein-Wort-Teilsätze („Also:“, „denn:“) anhängen
                if len(gs) == 1 and len(gs[0]) == 1:
                    nxt = G[ci + 1] if ci + 1 < len(G) else None
                    if nxt and len(nxt[0]) <= 2 and ln(gs[0] + nxt[0]) <= 24:
                        nxt[0] = gs[0] + nxt[0]; continue
                    if flat and len(flat[-1]) <= 2 and ln(flat[-1] + gs[0]) <= 24:
                        flat[-1] = flat[-1] + gs[0]; continue
                flat += gs
            _GR += flat
    return _GR


CAP_Y, CAP_SIZE = 1392, 54


def captions(c, t):
    """Untertitel in dunkler Pille: kurze Wortgruppen, gesprochene Wörter weiß, kommende gedimmt."""
    gs = _groups()
    for k, g in enumerate(gs):
        t0 = g[0]['start'] - 0.06
        t1 = gs[k + 1][0]['start'] - 0.06 if k + 1 < len(gs) and gs[k + 1][0]['start'] - g[-1]['end'] < 0.9 else g[-1]['end'] + 0.30
        if not (t0 <= t < t1):
            continue
        size = CAP_SIZE; f = font('bold', size); ws = [w['text'] for w in g]
        tot = sum(f.measureText(s) for s in ws) + f.measureText(' ') * (len(ws) - 1)
        if tot > 600:
            size = size * 600 / tot; f = font('bold', size); tot = 600.0
        sp = f.measureText(' '); a_in = eo3(pr(t, t0, 0.14)); y = CAP_Y + (1 - a_in) * 14; x = 540 - tot / 2
        hh = size * 0.74
        rrect(c, x - 30, y - hh - 20, tot + 60, hh + 40, 22, P(INK, a_in))
        _reg('untertitel', ' '.join(ws), x - 30, y - hh - 20, x + tot + 30, y + 20)
        for s, w in zip(ws, g):
            said = t >= w['start'] - 0.03
            c.drawString(s, x, y, f, P(WHITE, (1.0 if said else 0.42) * a_in)); x += f.measureText(s) + sp


def finish(c, t, serie=None):
    """Kopfzeile und Untertitel – immer als Letztes in draw() aufrufen."""
    header(c, *(serie or (None, None)))
    captions(c, t)


# ---------------------------------------------------------------- Mini-3D
TONE = dict(px=0.68, pz=0.86, py=1.0, nx=0.56, nz=0.52, ny=0.40)      # Helligkeit je Flächenrichtung (Licht von links vorn oben)
TINT = np.array([8, 34, 40]) / 255.0                                  # Schattenflächen ziehen leicht ins Petrol
LX, LZ = 0.30, -0.18                                                  # Schattenversatz je Höheneinheit


def _hex3(h):
    h = h.lstrip('#'); return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)]) / 255.0


def shade(col, n, a=1.0):
    tone = n[0] ** 2 * (TONE['px'] if n[0] > 0 else TONE['nx']) + n[1] ** 2 * (TONE['py'] if n[1] > 0 else TONE['ny']) + n[2] ** 2 * (TONE['pz'] if n[2] > 0 else TONE['nz'])
    rgb = _hex3(col) * tone; rgb = rgb + (TINT - rgb) * (1 - tone) * 0.30
    return skia.Color(int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255), int(clamp(a) * 255))


def face(pts, n, col, layer=2, decal=None, flat=False, alpha=1.0):
    return dict(p=np.array(pts, float), n=np.array(n, float), col=col, layer=layer, decal=decal, flat=flat, alpha=alpha)


def prism(poly, y0, y1, col, layer=2, top_col=None, decal=None, sides=True, flat=False, alpha=1.0):
    """Säule über einem Grundriss poly = [(x, z), …] von Höhe y0 bis y1. decal = (Ursprung, U, V, zeichenfunktion) auf der Oberseite."""
    poly = np.array(poly, float); cen = poly.mean(0)
    F = [face([[x, y1, z] for x, z in poly], [0, 1.0, 0], top_col or col, layer, decal, flat, alpha)]
    if sides:
        for i in range(len(poly)):
            a, b = poly[i], poly[(i + 1) % len(poly)]; d = b - a; nn = np.array([d[1], 0.0, -d[0]])
            if nn[0] * ((a + b) / 2 - cen)[0] + nn[2] * ((a + b) / 2 - cen)[1] < 0:
                nn = -nn
            F.append(face([[a[0], y0, a[1]], [b[0], y0, b[1]], [b[0], y1, b[1]], [a[0], y1, a[1]]], nn / max(1e-9, np.linalg.norm(nn)), col, layer, None, False, alpha))
    return F


def box(x0, x1, z0, z1, y0, y1, col, **kw):
    return prism([(x0, z0), (x1, z0), (x1, z1), (x0, z1)], y0, y1, col, **kw)


def circle(cx, cz, r, n=48):
    return [(cx + r * cos(2 * pi * i / n), cz + r * sin(2 * pi * i / n)) for i in range(n)]


def rrpoly(w, d, r, seg=5, cx=0.0, cz=0.0):
    """Grundriss: Rechteck w × d mit runden Ecken."""
    pts = []
    for (px, pz, a0) in ((w / 2 - r, d / 2 - r, 0), (-w / 2 + r, d / 2 - r, 90), (-w / 2 + r, -d / 2 + r, 180), (w / 2 - r, -d / 2 + r, 270)):
        for k in range(seg + 1):
            a = radians(a0 + 90 * k / seg); pts.append((cx + px + r * cos(a), cz + pz + r * sin(a)))
    return pts


def frustum(cx, cz, r0, r1, y0, y1, col, n=48, layer=2, top_col=None, alt=None, bottom=None, clip=False, alpha=1.0, top=True):
    """Zylinder/Kegelstumpf. alt=(k, farbe): jede k-te Facette dunkler (Rillen). clip: unter y=0 abschneiden (fürs Versinken)."""
    if clip:
        if y1 <= 0.5:
            return []
        if y0 < 0:
            r0 = r0 + (r1 - r0) * (0 - y0) / (y1 - y0); y0 = 0.0
    F = []
    for i in range(n):
        a0, a1 = 2 * pi * i / n, 2 * pi * (i + 1) / n; am = (a0 + a1) / 2
        p = [[cx + r0 * cos(a0), y0, cz + r0 * sin(a0)], [cx + r0 * cos(a1), y0, cz + r0 * sin(a1)], [cx + r1 * cos(a1), y1, cz + r1 * sin(a1)], [cx + r1 * cos(a0), y1, cz + r1 * sin(a0)]]
        nn = np.array([cos(am), (r0 - r1) / max(1e-6, (y1 - y0)), sin(am)])
        F.append(face(p, nn / np.linalg.norm(nn), (alt[1] if alt and i % alt[0] == 0 else col), layer, None, False, alpha))
    if top and r1 > 0.5:
        F.append(face([[x, y1, z] for x, z in circle(cx, cz, r1, n)], [0, 1.0, 0], top_col or col, layer, None, False, alpha))
    if bottom:
        F.append(face([[x, y0, z] for x, z in circle(cx, cz, r0, n)], [0, -1.0, 0], bottom, layer, None, False, alpha))
    return F


def sphere(cx, cy, cz, r, col, n=20, m=10, layer=2, alpha=1.0):
    """Kugel aus Facetten (weich schattiert)."""
    F = []
    for j in range(m):
        b0, b1 = -pi / 2 + pi * j / m, -pi / 2 + pi * (j + 1) / m
        for i in range(n):
            a0, a1 = 2 * pi * i / n, 2 * pi * (i + 1) / n
            def q(a, b): return [cx + r * cos(b) * cos(a), cy + r * sin(b), cz + r * cos(b) * sin(a)]
            am, bm = (a0 + a1) / 2, (b0 + b1) / 2
            F.append(face([q(a0, b0), q(a1, b0), q(a1, b1), q(a0, b1)], [cos(bm) * cos(am), sin(bm), cos(bm) * sin(am)], col, layer, None, False, alpha))
    return F


def Rx(a): c_, s_ = cos(a), sin(a); return np.array([[1, 0, 0], [0, c_, -s_], [0, s_, c_]])
def Ry(a): c_, s_ = cos(a), sin(a); return np.array([[c_, 0, s_], [0, 1, 0], [-s_, 0, c_]])
def Rz(a): c_, s_ = cos(a), sin(a); return np.array([[c_, -s_, 0], [s_, c_, 0], [0, 0, 1]])


def rot(rx=0.0, ry=0.0, rz=0.0, scale=1.0):
    """Drehmatrix aus Grad: erst um x (kippen zum Betrachter), dann z (rollen), dann y (drehen)."""
    return Ry(radians(ry)) @ Rz(radians(rz)) @ Rx(radians(rx)) * scale


def xf(F, R=None, t=(0, 0, 0)):
    """Flächen drehen (R) und verschieben (t) – Aufkleber (decals) wandern mit."""
    out = []; t = np.array(t, float)
    for f in F:
        g = dict(f); p, n = f['p'], f['n']
        if R is not None:
            p = p @ R.T; n = R @ n
        g['p'], g['n'] = p + t, n / max(1e-9, float(np.linalg.norm(n)))
        if f.get('decal'):
            O, U, V, fn = f['decal']
            if R is not None:
                O, U, V = R @ O, R @ U, R @ V
            g['decal'] = (O + t, U, V, fn)
        out.append(g)
    return out


def relayer(F, layer):
    for f in F:
        f['layer'] = layer
    return F


class Cam:
    def __init__(s, yaw, pitch, sc, cx, cy):
        s.c1, s.s1, s.cp, s.sp, s.sc, s.cx, s.cy = cos(yaw), sin(yaw), cos(pitch), sin(pitch), sc, cx, cy
        s.view = np.array([s.s1 * s.cp, s.sp, s.c1 * s.cp])

    def lin(s, v):
        x1 = v[0] * s.c1 - v[2] * s.s1; z1 = v[0] * s.s1 + v[2] * s.c1
        return s.sc * x1, -s.sc * (v[1] * s.cp - z1 * s.sp)

    def pt(s, v):
        a, b = s.lin(v); return s.cx + a, s.cy + b


def fpath(cam, pts):
    path = skia.Path(); q = [cam.pt(p) for p in pts]; path.moveTo(*q[0])
    for a in q[1:]:
        path.lineTo(*a)
    path.close(); return path


def draw_faces(c, cam, F):
    vis = [f for f in F if float(np.dot(f['n'], cam.view)) > 1e-4]
    vis.sort(key=lambda f: (f['layer'], float(np.dot(f['p'].mean(0), cam.view))))
    for f in vis:
        path = fpath(cam, f['p']); al = f.get('alpha', 1.0)
        col = C(f['col'], al) if f.get('flat') else shade(f['col'], f['n'], al)
        pa = skia.Paint(AntiAlias=True); pa.setColor(col); c.drawPath(path, pa)
        if al >= 0.999:
            pa.setStyle(skia.Paint.kStroke_Style); pa.setStrokeWidth(1.1); c.drawPath(path, pa)
        if f.get('decal'):
            O, U, V, fn = f['decal']; ox, oy = cam.pt(O); ux, uy = cam.lin(U); vx, vy = cam.lin(V)
            c.save(); c.clipPath(path, True); c.concat(skia.Matrix.MakeAll(ux, vx, ox, uy, vy, oy, 0, 0, 1)); fn(c); c.restore()


def _hull(pts):
    pts = sorted(set((round(x, 1), round(y, 1)) for x, y in pts))
    if len(pts) < 3:
        return pts

    def half(seq):
        h = []
        for p in seq:
            while len(h) >= 2 and (h[-1][0] - h[-2][0]) * (p[1] - h[-2][1]) - (h[-1][1] - h[-2][1]) * (p[0] - h[-2][0]) <= 0:
                h.pop()
            h.append(p)
        return h
    lo, up = half(pts), half(pts[::-1])
    return lo[:-1] + up[:-1]


_BGPIC = None


def background(c):
    """Papier mit feinem Punktraster (als Vektor-Aufnahme, bleibt auch in 4K scharf)."""
    global _BGPIC
    if _BGPIC is None:
        rec = skia.PictureRecorder(); b = rec.beginRecording(skia.Rect.MakeWH(W, H))
        b.drawRect(skia.Rect.MakeWH(W, H), P(PAPER))
        b.drawRect(skia.Rect.MakeWH(W, H), rad(540, 700, 1150, [C(WHITE, 0.65), C(WHITE, 0.0)]))
        dot = P(INK, 0.07)
        for gy in range(30, H, 60):
            for gx in range(30, W, 60):
                b.drawCircle(gx, gy, 2.2, dot)
        _BGPIC = rec.finishRecordingAsPicture()
    c.drawPicture(_BGPIC)


class Stage:
    """Die Bühne: Petrol-Plattform, langsame Kamerafahrt (kehrt am Ende zum Startwinkel zurück -> Loop), Licht und Schatten.

    st = Stage(c, t); st.begin(); st.add(flächen) …; st.end()
    Welt-Koordinaten: x nach rechts, z nach vorn (zum Betrachter), y nach oben; Plattform-Oberseite = y 0; Plattform-Mitte = (0, 0).
    Standard-Plattform 680 × 480: x von -340 bis 340, z von -240 bis 240. Wichtiges eher links/mittig (rechts unten liegen die App-Knöpfe).
    """

    def __init__(s, c, t, plat=(680, 480, 64), yaw=(20.0, 29.0), pitch=34.0, zoom=(1.15, 1.18), center=(530, 990), T=None, col=PETROL):
        s.c, s.t = c, t; T = T or total(); ph = (1 - cos(2 * pi * clamp(t / T))) / 2
        s.cam = Cam(radians(lerp(yaw[0], yaw[1], ph)), radians(pitch), lerp(zoom[0], zoom[1], ph), *center)
        s.plat, s.col = plat, col; s.F, s.SH = [], []

    def begin(s, bg=True):
        c, cam = s.c, s.cam; w, d, r = s.plat
        if bg:
            background(c)
        top = prism(rrpoly(w, d, r, 8), -44, 0, s.col, layer=0) + prism(rrpoly(w - 28, d - 28, max(8, r - 10), 8), -70, -44, PETROL_D, layer=-1)
        s.ptop = fpath(cam, top[0]['p'])
        sh = fpath(cam, [(x, -70, z) for x, z in rrpoly(w - 10, d - 10, r, 8)])
        c.save(); c.translate(0, 62); c.drawPath(sh, P('#0B2A30', 0.30, blur=38)); c.restore()
        draw_faces(c, cam, top)
        c.save(); c.clipPath(s.ptop, True)
        c.drawPaint(lin(90, 1160, 960, 800, [C(WHITE, 0.10), C(WHITE, 0.0), C('#000000', 0.14)], [0, 0.5, 1]))
        c.restore()
        c.drawPath(s.ptop, P(PETROL_L, 0.55, stroke=2.5))
        return s

    def pt(s, x, y=0.0, z=0.0):
        """Welt-Punkt -> Bildschirm-Punkt (für Etiketten)."""
        return s.cam.pt((x, y, z))

    def shadow(s, pts3, a=0.24, blur=9, ground=True):
        """Schatten von Hand: Punkte [(x, y, z), …]. ground=False für schwebende Dinge."""
        s.SH.append((pts3, a, blur, ground))

    def add(s, faces, shadow=True, a=0.24, blur=9, ground=True, layer=None):
        """Objekt auf die Bühne stellen. shadow=True: Schatten automatisch aus der Form; ground=False: Objekt schwebt."""
        if not faces:
            return s
        if layer is not None:
            relayer(faces, layer)
        s.F += faces
        if shadow:
            pts = np.vstack([f['p'] for f in faces])
            if len(pts) > 160:
                pts = pts[::max(1, len(pts) // 160)]
            s.SH.append((pts, a, blur, ground))
        return s

    def hole(s, x, z, r):
        """Dunkle Öffnung in der Plattform (für Dinge, die hinein- oder herausfahren)."""
        if r > 1:
            s.F += prism(circle(x, z, r, 48), 0.1, 0.2, '#061A1E', layer=1, sides=False, flat=True)

    def end(s):
        c, cam = s.c, s.cam
        c.save(); c.clipPath(s.ptop, True)
        for pts, a, bl, gr in s.SH:
            P2 = []
            for p in pts:
                h = max(0.0, float(p[1]))
                if gr:
                    P2.append((float(p[0]), float(p[2])))
                P2.append((float(p[0]) + LX * h, float(p[2]) + LZ * h))
            hl = _hull(P2)
            if len(hl) >= 3:
                c.drawPath(fpath(cam, [(x, 0.4, z) for x, z in hl]), P('#020F12', a * 1.5, blur=bl))
        c.restore()
        draw_faces(c, cam, s.F)
        return s


# ---------------------------------------------------------------- Bilder ansehen
def _frame(draw, t, scale=1):
    s = skia.Surface(int(W * scale), int(H * scale)); c = s.getCanvas(); c.scale(scale, scale); draw(c, t); return s


def still(draw, t, out=None):
    out = out or 'still_%.2f.png' % t
    _frame(draw, t).makeImageSnapshot().save(out, skia.kPNG); print('geschrieben:', out); return out


def sheet(draw, times, out, scale=0.25, cols=6):
    rows = (len(times) + cols - 1) // cols; cw, ch = int(W * scale), int(H * scale)
    S = skia.Surface(cols * cw, rows * ch); k = S.getCanvas(); k.clear(C('#101214'))
    for i, t in enumerate(times):
        img = _frame(draw, t).makeImageSnapshot()
        x, y = (i % cols) * cw, (i // cols) * ch
        k.drawImageRect(img, skia.Rect.MakeXYWH(x, y, cw, ch), skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear))
        k.drawString('%.2f' % t, x + 6, y + 18, skia.Font(None, 16), P('#FF5A3C'))
    S.makeImageSnapshot().save(out, skia.kPNG); print('geschrieben:', out)


# ---------------------------------------------------------------- Prüfen
ZONES = [('oben', lambda l, t, r, b: t < 119), ('oben Mitte (Tabs)', lambda l, t, r, b: t < 212 and r > 308 and l < 760),
         ('links', lambda l, t, r, b: l < 44), ('rechts', lambda l, t, r, b: r > 1033 and t < 956),
         ('rechts unten (Like/Kommentar/Teilen)', lambda l, t, r, b: r > 886 and b > 956 and t < 1543), ('unten', lambda l, t, r, b: b > 1543)]


def check(draw, step=0.1):
    """Prüft die flache Ebene (Kopfzeile, Zahlen, Etiketten, Banner, Stempel, Untertitel): Sperrzonen und Überlappungen; dazu Länge und erstes Bild."""
    global _REG
    T = total(); probs, seen = [], set(); null = skia.Surface(W // 4, H // 4).getCanvas()
    t = 0.0
    while t < T:
        _REG = []; draw(null, t); R = _REG; _REG = None
        for kind, txt, (l, tp, r, b) in R:
            for zn, fn in ZONES:
                if fn(l, tp, r, b) and (kind, txt, zn) not in seen:
                    seen.add((kind, txt, zn)); probs.append(f'{t:5.2f} s  SPERRZONE {zn}: {kind} „{txt}“  ({l:.0f},{tp:.0f})–({r:.0f},{b:.0f})')
        for i in range(len(R)):
            for j in range(i + 1, len(R)):
                (k1, t1, a), (k2, t2, b_) = R[i], R[j]
                ox = min(a[2], b_[2]) - max(a[0], b_[0]); oy = min(a[3], b_[3]) - max(a[1], b_[1])
                if ox > 6 and oy > 6 and (k1, t1, k2, t2) not in seen:
                    seen.add((k1, t1, k2, t2)); probs.append(f'{t:5.2f} s  ÜBERLAPPUNG: {k1} „{t1}“ × {k2} „{t2}“')
        t += step
    if not 22 <= T <= 42:
        probs.append(f'Länge {T:.1f} s – erlaubt 22 bis 42 s (Ziel 28–36)')
    a = np.frombuffer(_frame(draw, 0.0, 0.25).makeImageSnapshot().tobytes(), np.uint8).reshape(H // 4, W // 4, 4)[..., :3].astype(float)
    if a[60:330].std() < 22:                                           # y 240–1320: dort muss in Bild 0 schon das Motiv stehen
        probs.append('Bild 0 ist fast leer – das Hauptobjekt muss bei t = 0 groß und voll sichtbar sein (Startbild = Cover)')
    for p_ in probs:
        print('  PROBLEM:', p_)
    print(f'Länge {T:.1f} s · Effekte: {len(_SFX)}')
    print('STUDIOCHECK OK' if not probs else f'STUDIOCHECK: {len(probs)} Problem(e) – erst beheben, dann rendern')
    return not probs


# ---------------------------------------------------------------- Ton
def _collect(draw):
    """Spielt das Video einmal unsichtbar durch, damit alle Effekte (rise/drop/pop/snd) angemeldet sind."""
    null = skia.Surface(W // 8, H // 8).getCanvas(); T = total(); t = 0.0
    while t < T:
        draw(null, t); t += 1 / 15


def audio(draw):
    """Stimme + „Chill Wave“ (leise, unter der Stimme abgesenkt) + Effekte aus reinen Tönen -> mix.wav (ca. −15 LUFS)."""
    sys.path.insert(0, LIB); import pipeline as PL
    SR = 44100; T = total(); N = int(T * SR)
    dec = lambda path: np.frombuffer(subprocess.check_output(['ffmpeg', '-v', 'error', '-i', path, '-ar', str(SR), '-ac', '1', '-f', 'f32le', '-']), np.float32).copy()
    v = dec('voice.mp3'); voice = np.zeros(N, np.float32); voice[:min(N, len(v))] = v[:N]
    tdir = os.path.join(SYS, 'assets', 'musik'); tname = 'chill_wave.mp3'
    m = dec(os.path.join(tdir, tname))
    while len(m) < N:
        m = np.concatenate([m, m])
    m = m[:N]; m = m / max(1e-6, np.sqrt(np.mean(m ** 2))) * 0.055; fi = int(0.4 * SR); m[:fi] *= np.linspace(0, 1, fi)
    _SFX.clear(); _collect(draw)
    S = PL.sfx_sounds(SR); sfx = np.zeros(N + SR, np.float32)
    # Regeln wie in pipeline.py: jeder Effekt weich ein-/ausgeblendet, NIE zwei Effekte gleichzeitig (der wichtigere gewinnt),
    # nichts in den ersten 0,15 s und den letzten 0,3 s (Loop-Naht).
    BUSY = {'ink': 0.27, 'hit': 0.17, 'thud': 0.20, 'whoosh': 0.19, 'ding': 0.25, 'cut': 0.09, 'swipe': 0.15, 'type': 0.15, 'tick': 0.03, 'pop': 0.085}
    RANK = {'ink': 0, 'hit': 1, 'thud': 2, 'whoosh': 3, 'ding': 4, 'cut': 5, 'swipe': 6, 'type': 6, 'tick': 6, 'pop': 7}
    taken, keep = [], []
    for (te, kind), g in sorted(_SFX.items(), key=lambda e: (RANK.get(e[0][1], 9), e[0][0])):
        if kind not in S or te < 0.15 or te > T - 0.3:
            continue
        a0, a1 = te - 0.012, te + BUSY[kind]
        if any(a0 < b1 and b0 < a1 for b0, b1 in taken):
            continue
        taken.append((a0, a1)); keep.append((te, kind, g))
    for te, kind, g in sorted(keep):
        sg = np.array(S[kind], np.float32) * g * (PL.TRANS_GAIN if kind in ('whoosh', 'ink', 'cut') else 1.0)
        r = min(len(sg) // 4, int(0.006 * SR)); ramp = np.sin(np.linspace(0, np.pi / 2, r)) ** 2; sg[:r] *= ramp; sg[len(sg) - r:] *= ramp[::-1]
        i0 = int(te * SR); sfx[i0:i0 + len(sg)] += sg[:len(sfx) - i0]
    print('Effekte:', len(keep), 'Stück ·', ' '.join(f'{te:.2f}:{kind}' for te, kind, _ in sorted(keep)))
    PL.noise_check(sfx, SR, [])
    venv = np.convolve(np.abs(voice), np.ones(4410) / 4410, 'same'); duck = np.convolve(np.where(venv > 0.01, 0.45, 1.0), np.ones(8820) / 8820, 'same')
    mx = voice + m * duck * 0.9 + sfx[:N] * 0.6
    fo = int(0.12 * SR); mx[-fo:] *= np.linspace(1, 0, fo); mx = mx / np.max(np.abs(mx)) * 0.95
    with wave.open('mix.wav', 'wb') as wv:
        wv.setnchannels(1); wv.setsampwidth(2); wv.setframerate(SR); wv.writeframes((mx * 32767).astype(np.int16).tobytes())
    PL.master('mix.wav')
    credit = json.load(open(os.path.join(tdir, 'credits.json'), encoding='utf-8')).get(tname)
    open('music_credit.txt', 'w', encoding='utf-8').write(credit + '\n')
    print('Musik-Lizenzzeile (in jede Beschreibung!):', credit)
    print('mix.wav', round(T, 2), 's')


# ---------------------------------------------------------------- Rendern
def _render_part(draw, f0, f1, scale, out):
    tmp = out[:-4] + '.tmp.mp4'
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{W * scale}x{H * scale}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-g', '60', tmp], stdin=subprocess.PIPE)
    s = skia.Surface(W * scale, H * scale); c = s.getCanvas()
    for i in range(f0, f1):
        c.save(); c.scale(scale, scale); draw(c, i / FPS); c.restore()
        p.stdin.write(s.toarray(colorType=skia.kRGBA_8888_ColorType).tobytes())
    p.stdin.close()
    if p.wait():
        raise SystemExit('ffmpeg-Fehler in ' + out)
    os.replace(tmp, out)


def render(draw, name, hd=False, jobs=2, only=None):
    """Master in 4K (2160×3840) für TikTok/YouTube + Full-HD-Fassung für Instagram. hd=True: nur schnelle Full-HD-Vorschau.
    Das Video wird in zwei Hälften gebaut (part_0/part_1). only=[1]: nur diese Hälfte neu bauen (nach einer Änderung, die nur dort wirkt)."""
    audio(draw)
    T = total(); n = int(round(T * FPS)); scale = 1 if hd else 2
    edges = [round(n * k / jobs) for k in range(jobs + 1)]; parts = [f'part_{k}{"_hd" if hd else ""}.mp4' for k in range(jobs)]; pids = []
    for k in range(jobs):
        if only is not None and k not in only and os.path.exists(parts[k]):
            continue
        pid = os.fork()
        if pid == 0:
            try:
                _render_part(draw, edges[k], edges[k + 1], scale, parts[k]); os._exit(0)
            except BaseException as ex:                                   # noqa
                print('Fehler:', repr(ex)); os._exit(1)
        pids.append(pid)
    if any(os.waitpid(pid, 0)[1] for pid in pids):
        raise SystemExit('Rendern fehlgeschlagen')
    open('list.txt', 'w').write(''.join(f"file '{p_}'\n" for p_ in parts))
    subprocess.check_call(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', 'list.txt', '-c', 'copy', 'video.mp4'])
    out = f'FAKTENFABRIK_{name}.mp4' if not hd else f'VORSCHAU_{name}.mp4'
    subprocess.check_call(['ffmpeg', '-y', '-loglevel', 'error', '-i', 'video.mp4', '-i', 'mix.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
                           '-shortest', '-movflags', '+faststart', out])
    if hd:
        print('geschrieben:', out, '(Full-HD-Vorschau)'); return out
    ig = f'FAKTENFABRIK_{name}_IG.mp4'
    subprocess.check_call(['ffmpeg', '-y', '-loglevel', 'error', '-i', out, '-vf', 'scale=1080:1920:flags=lanczos', '-c:v', 'libx264', '-preset', 'slow', '-crf', '17',
                           '-profile:v', 'high', '-pix_fmt', 'yuv420p', '-c:a', 'copy', '-movflags', '+faststart', ig])
    print('geschrieben:', out, '(4K, TikTok/YouTube) und', ig, '(Full HD, Instagram)'); return out


def timing():
    """Schreibt durs.json, voice.json, scene_starts.json, para_word_idx.json (gleiche Dateien wie pipeline.py timing – für hookcheck.py)."""
    ws = _load(); T = total()
    starts = [0.0] + [max(0.0, ws[k]['start'] - 0.15) for k in _PI[1:]]; edges = starts + [T]
    d = [edges[i + 1] - edges[i] for i in range(len(starts))]
    for fn, v in (('voice.json', d), ('durs.json', d), ('scene_starts.json', starts), ('para_word_idx.json', _PI)):
        json.dump(v, open(fn, 'w'))
    print('Absätze (s):', [round(x, 2) for x in d], '· gesamt', round(T, 2), 's')
    for p in range(1, len(_PI) + 1):
        a, b = _prange(p); print(f'  {p:2d}  {ps(p):5.2f}–{pe(p):5.2f}  ' + ' '.join(f"{w['text']}@{w['start']:.2f}" for w in ws[a:b]))


def thumb(draw, t=0.0, out='thumb.png'):
    """Titelbild = ein Bild aus dem Video (Standard: Bild 0, das schon wie ein Cover aussehen muss)."""
    _frame(draw, t).makeImageSnapshot().save(out, skia.kPNG); print('geschrieben:', out)


def main(draw, serie=None, name='Folge'):
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'sheet'; a = sys.argv[2:]
    if cmd == 'timing':
        timing()
    elif cmd == 'sheet':
        step = float(a[0]) if a else 1.0; T = total(); ts = [round(i * step, 2) for i in range(int(T / step) + 1)]
        for k in range(0, len(ts), 18):
            sheet(draw, ts[k:k + 18], 'sheet_%d.png' % (k // 18))
    elif cmd == 'big':
        sheet(draw, [float(x) for x in a], 'big.png', 0.46, 2)
    elif cmd == 'still':
        still(draw, float(a[0]))
    elif cmd == 'check':
        sys.exit(0 if check(draw) else 1)
    elif cmd == 'audio':
        audio(draw)
    elif cmd == 'render':                      # render | render hd | render teil 1 (nur die zweite Hälfte neu) | render teil 0
        only = [int(x) for x in a[a.index('teil') + 1:]] if 'teil' in a else None
        render(draw, name, hd='hd' in a, only=only)
    elif cmd == 'thumb':
        thumb(draw, float(a[0]) if a else 0.0)
    else:
        raise SystemExit(__doc__)
