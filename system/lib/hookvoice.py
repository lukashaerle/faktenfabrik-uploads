"""FAKTENFABRIK – Hook-Stimme angleichen: der erste Satz darf nicht lauter und greller sein als der Rest.

Hintergrund (Lukas, 25.11.2026: „das Schreien am Anfang …“): Mit der Regieanweisung [urgent] spricht die Stimme den
ersten Satz rund 60–90 % höher, bis zu 2 dB lauter und deutlich greller als den Rest. Dieses Werkzeug misst Absatz 1
gegen die übrigen Absätze und nimmt ihn nur zurück, nie hoch: Pegel auf das Niveau des Rests, Höhen (2–5 kHz)
um höchstens 4 dB. Die Tonhöhe selbst lässt sich nachträglich nicht sauber ändern – ruhig wird der Einstieg nur mit
einer ruhigen Aufnahme (Hook ohne [urgent]/[excited] sprechen lassen).

Aufruf im Episodenordner NACH tighten.py (und ggf. recut.py), VOR `pipeline.py timing`:
    python3 ../lib/hookvoice.py          messen und angleichen (Sicherung: voice_vor_hook.mp3)
    python3 ../lib/hookvoice.py --check  nur messen
"""
import json
import os
import re
import shutil
import subprocess
import sys

import numpy as np

SR = 44100


def md5(f):
    import hashlib
    return hashlib.md5(open(f, 'rb').read()).hexdigest()


def fresh_backup(backup, mark):
    """True, wenn voice.mp3 genau die Datei ist, die dieses Werkzeug zuletzt geschrieben hat – dann ist die Sicherung
    die richtige Quelle. Sonst ist voice.mp3 neu (z. B. tighten.py erneut gelaufen) und muss neu gesichert werden."""
    return os.path.exists(backup) and os.path.exists(mark) and open(mark).read().strip() == md5('voice.mp3')


def pcm(f):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768


def speech(seg):
    n = int(0.01 * SR)
    r = np.sqrt(np.mean(seg[:len(seg) // n * n].reshape(-1, n) ** 2, axis=1))
    m = np.repeat(r > 0.02, n)
    return seg[:len(m)][m]


def level(seg):
    s = speech(seg)
    return 20 * np.log10(np.sqrt(np.mean(s ** 2)) + 1e-9) if len(s) else -99.0


def tilt(seg):
    s = speech(seg)
    if len(s) < 2048:
        return 0.0
    X = np.abs(np.fft.rfft(s * np.hanning(len(s)))) ** 2
    f = np.fft.rfftfreq(len(s), 1 / SR)
    return float(10 * np.log10(X[(f >= 2000) & (f < 5000)].sum() + 1e-12) - 10 * np.log10(X[(f >= 100) & (f < 1000)].sum() + 1e-12))


def is_word(w):
    t = w['text']
    return w.get('type', 'word') == 'word' and not t.startswith('[') and t not in ('—', '-', '–')


def bounds():
    """Absatzgrenzen aus words.json + paras.json (wie pipeline.py: Wörter je Absatz abzählen)."""
    W = [w for w in json.load(open('words.json', encoding='utf-8'))['words'] if is_word(w)]
    P = json.load(open('paras.json', encoding='utf-8'))
    n = [len([t for t in p.split() if t not in ('—', '-', '–')]) for p in P]
    idx = np.cumsum([0] + n)
    edges = []
    for k in range(1, len(P)):
        a = W[min(idx[k] - 1, len(W) - 1)]['end']; b = W[min(idx[k], len(W) - 1)]['start']
        edges.append((min(a, b) + max(a, b)) / 2 if b > a else b - 0.01)
    return edges


def measure(x, edges):
    T = len(x) / SR
    cuts = [0.0] + edges + [T]
    L = [level(x[int(a * SR):int(b * SR)]) for a, b in zip(cuts, cuts[1:])]
    K = [tilt(x[int(a * SR):int(b * SR)]) for a, b in zip(cuts, cuts[1:])]
    return L[0], float(np.median(L[1:])), K[0], float(np.median(K[1:]))


def main():
    if not fresh_backup('voice_vor_hook.mp3', 'hook_mark.txt'):          # voice.mp3 ist neu: das ist die Quelle
        shutil.copy('voice.mp3', 'voice_vor_hook.mp3')
    src = 'voice_vor_hook.mp3'
    x = pcm(src); edges = bounds(); he = edges[0]
    l1, lr, k1, kr = measure(x, edges)
    print(f'vorher:  Hook {l1:.1f} dB / Rest {lr:.1f} dB ({l1 - lr:+.1f} dB) · Höhen Hook {k1:.1f} / Rest {kr:.1f} ({k1 - kr:+.1f} dB) · Hook endet bei {he:.2f} s')
    if '--check' in sys.argv:
        return
    g = min(0.0, lr - l1)                     # nur leiser, nie lauter
    sh = float(np.clip(kr - k1, -4.0, 0.0))   # Höhen höchstens 4 dB zurück
    if g > -0.3 and sh > -0.5:
        shutil.copy(src, 'voice.mp3'); open('hook_mark.txt', 'w').write(md5('voice.mp3'))
        print('Hook passt schon zum Rest – nichts geändert'); return
    def apply(g_, sh_, out):
        fl = (f'[0:a]atrim=0:{he:.3f},asetpts=PTS-STARTPTS,highshelf=f=2500:g={sh_:.2f},volume={g_:.2f}dB[a];'
              f'[0:a]atrim={he:.3f},asetpts=PTS-STARTPTS[b];[a][b]concat=n=2:v=0:a=1[o]')
        subprocess.check_call(['ffmpeg', '-y', '-v', 'error', '-i', src, '-filter_complex', fl, '-map', '[o]', '-b:a', '256k', out])
    if sh < -0.5:                              # die Höhen-Absenkung macht den Satz auch etwas leiser: Pegel danach neu bemessen
        apply(0.0, sh, 'voice_tmp_hook.mp3')
        g = min(0.0, lr - measure(pcm('voice_tmp_hook.mp3'), edges)[0]); os.remove('voice_tmp_hook.mp3')
    apply(g, sh, 'voice.mp3')
    open('hook_mark.txt', 'w').write(md5('voice.mp3'))
    y = pcm('voice.mp3')
    l1, lr, k1, kr = measure(y, edges)
    print(f'nachher: Hook {l1:.1f} dB / Rest {lr:.1f} dB ({l1 - lr:+.1f} dB) · Höhen Hook {k1:.1f} / Rest {kr:.1f} ({k1 - kr:+.1f} dB) · '
          f'angewandt: Pegel {g:+.1f} dB, Höhen {sh:+.1f} dB · Länge {len(x) / SR:.2f} -> {len(y) / SR:.2f} s')


if __name__ == '__main__':
    main()
