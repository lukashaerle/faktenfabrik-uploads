"""FAKTENFABRIK – Aufnahme umschneiden statt neu aufnehmen (Sätze umstellen, Wörter herausschneiden).

Aufruf im Episodenordner NACH tighten.py:   python3 ../lib/recut.py recut.json

recut.json (Indizes = Einträge in words.json, gezählt wie von `python3 ../lib/recut.py --list` gezeigt):
    {"order": [[5, 10], [1, 4], [11, 21], [23, 94]],   Abschnitte [erstes Wort, letztes Wort] in neuer Reihenfolge
     "gaps":  [0.18, 0.18, 0.0],                        Stille, die zwischen die Abschnitte gelegt wird (s)
     "lead":  0.02}                                     Stille vor dem ersten Wort (der Hook beginnt sofort)

Schnitte liegen in echter Stille (silencedetect auf voice.mp3). Gibt es zwischen zwei Wörtern keine Stille
(ein Wort mitten im Satz herausschneiden), wird an der leisesten Stelle zwischen ihnen geschnitten; ein Abstand
von 0 setzt die Teile dann nahtlos aneinander. Jede Kante bekommt 8 ms Blende.
Schreibt voice.mp3 und words.json neu (Sicherung: voice_vor_umschnitt.mp3, words_vor_umschnitt.json).
script.txt / paras.json müssen den neuen Wortlaut schon haben. Danach `pipeline.py timing` und `hookcheck.py`.
"""
import json
import os
import re
import shutil
import subprocess
import sys

import numpy as np

SR = 44100
EDGE = 0.04          # so viel Stille bleibt an einer Schnittkante in Stille stehen


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


def silences(f, noise='-38dB', d=0.10):
    out = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', f, '-af', f'silencedetect=noise={noise}:d={d}', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r'silence_start: (-?[0-9.]+)', out)]
    en = [float(x) for x in re.findall(r'silence_end: (-?[0-9.]+)', out)]
    return list(zip(st, en + [None] * (len(st) - len(en))))


def quietest(x, t0, t1):
    """Leisester 10-ms-Punkt zwischen t0 und t1 (Schnitt mitten im Satz)."""
    n = int(0.01 * SR)
    a, b = max(0, int(t0 * SR)), min(len(x) - n, int(t1 * SR))
    if b <= a:
        return (t0 + t1) / 2
    best = min(range(a, b, n // 2), key=lambda i: float(np.sqrt(np.mean(x[i:i + n] ** 2))))
    return (best + n / 2) / SR


def main():
    W = json.load(open('words.json', encoding='utf-8'))['words']
    W = [w for w in W if w.get('type', 'word') == 'word']
    if sys.argv[1:] == ['--list']:
        for i, w in enumerate(W):
            print(i, repr(w['text']), w['start'], w['end'])
        return
    spec = json.load(open(sys.argv[1] if len(sys.argv) > 1 else 'recut.json', encoding='utf-8'))
    order, gaps, lead = spec['order'], spec.get('gaps', []), float(spec.get('lead', 0.02))
    mine = fresh_backup('voice_vor_umschnitt.mp3', 'recut_mark.txt') or (           # auch: hookvoice.py hat unser Ergebnis nur angeglichen
        os.path.exists('voice_vor_umschnitt.mp3') and fresh_backup('voice_vor_hook.mp3', 'hook_mark.txt')
        and os.path.exists('recut_mark.txt') and md5('voice_vor_hook.mp3') == open('recut_mark.txt').read().strip())
    if not mine:                                                                     # voice.mp3 ist neu (tighten.py lief erneut): neu sichern
        shutil.copy('voice.mp3', 'voice_vor_umschnitt.mp3'); shutil.copy('words.json', 'words_vor_umschnitt.json')
    src = 'voice_vor_umschnitt.mp3'
    W = [w for w in json.load(open('words_vor_umschnitt.json', encoding='utf-8'))['words'] if w.get('type', 'word') == 'word']
    x = pcm(src); dur = len(x) / SR
    sil = [(a, dur if b is None else b) for a, b in silences(src)]

    def start_cut(i):                    # Schnitt vor Wort i
        if all(w['text'].startswith('[') for w in W[:i]):    # nur Regie-Tags davor: Anfang der Aufnahme
            return 0.0, True, 0.0
        for a, b in sil:
            if a >= W[i - 1]['start'] + 0.12 and W[i]['start'] - 0.35 <= b <= W[i]['start'] + 0.15:
                return max(a, b - EDGE), True, b                 # b = Einsatz der Stimme (Ende der Stille)
        q = quietest(x, (W[i - 1]['end'] + W[i]['start']) / 2 - 0.05, (W[i - 1]['end'] + W[i]['start']) / 2 + 0.05)
        return q, False, q

    def end_cut(j):                      # Schnitt nach Wort j
        if j == len(W) - 1:
            return dur, True
        for a, b in sil:
            if W[j]['start'] + 0.12 <= a <= max(W[j]['end'], W[j]['start'] + 0.2) + 0.35:
                return min(b, a + EDGE), True
        return quietest(x, (W[j]['end'] + W[j + 1]['start']) / 2 - 0.05, (W[j]['end'] + W[j + 1]['start']) / 2 + 0.05), False

    pieces, new_words, t_out = [], [], 0.0
    for k, (i, j) in enumerate(order):
        s, s_sil, onset = start_cut(i); e, e_sil = end_cut(j)
        if k == 0 and s_sil:                                  # Hook: höchstens `lead` Stille vor dem Einsatz der Stimme
            s = max(s, onset - lead)
        gap = lead if k == 0 and not s_sil else (0.0 if k == 0 else float(gaps[k - 1] if k - 1 < len(gaps) else 0.0))
        if k == 0 and s_sil:
            gap = 0.0
        if gap > 0:
            pieces.append(np.zeros(int(gap * SR), np.float32)); t_out += gap
        seg = x[int(s * SR):int(e * SR)].copy()
        f = int(0.008 * SR); ramp = np.linspace(0, 1, f, dtype=np.float32)
        seg[:f] *= ramp; seg[-f:] *= ramp[::-1]
        pieces.append(seg)
        for w in W[i:j + 1]:
            nw = dict(w); nw['start'] = round(max(0.0, w['start'] - s) + t_out, 3); nw['end'] = round(min(e, w['end']) - s + t_out, 3)
            new_words.append(nw)
        print(f'Abschnitt {k + 1}: Wörter {i}–{j} „{" ".join(w["text"] for w in W[i:j + 1] if not w["text"].startswith("["))[:60]}“ '
              f'{s:.3f}–{e:.3f} s ({"Stille" if s_sil else "im Satz"}/{"Stille" if e_sil else "im Satz"}) -> ab {t_out:.3f} s')
        t_out += len(seg) / SR
    y = np.concatenate(pieces)
    tmp = 'voice_umschnitt.wav'
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 's16le', '-ar', str(SR), '-ac', '1', '-i', '-', tmp],
                   input=(np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes(), check=True)
    subprocess.check_call(['ffmpeg', '-y', '-v', 'error', '-i', tmp, '-b:a', '256k', 'voice.mp3'])
    json.dump({'words': new_words}, open('words.json', 'w', encoding='utf-8'), ensure_ascii=False)
    open('recut_mark.txt', 'w').write(md5('voice.mp3')); os.remove(tmp)
    print(f'voice.mp3 {dur:.2f} s -> {len(y) / SR:.2f} s · {len(new_words)} Einträge in words.json')


if __name__ == '__main__':
    main()
