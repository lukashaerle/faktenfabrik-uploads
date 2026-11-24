"""FAKTENFABRIK – Stimme straffen (Viral-Aufbau V3): Pausen kürzen + Tempo anheben, Wortzeiten mitrechnen.

Aufruf im Episodenordner (braucht voice_orig.mp3, words_raw.json, script.txt):
    python3 ../lib/tighten.py            Tempo automatisch (Ziel ca. 2,75 Wörter/s, höchstens 1,04)
    python3 ../lib/tighten.py 1.02       festes Tempo

TEMPO (Lukas, 25.11.2026: „ein Ticken langsamer – das ist jetzt schon sehr schnell“): Bis 24.11. wurde jede Pause auf
0,14 s gekürzt und die Stimme um 8–10 % beschleunigt (rund 3 Wörter/s ohne Luft). Jetzt bleiben Pausen bis 0,30 s
unverändert, längere werden auf 0,26 s gekürzt, eine im Skript gesetzte [pause] behält 0,40 s, und die Stimme wird
höchstens um 4 % beschleunigt.

Schreibt voice.mp3, words.json und paras.json (script.txt ohne Regie-Tags).
Optional fix.json: {"U-V-P": "UVP"} – ersetzt Wörter im Transkript (Untertitel-Schreibweise).
Danach: `python3 ../lib/pipeline.py timing` und `python3 ../lib/hookcheck.py`.
"""
import json
import os
import re
import subprocess
import sys

MAXGAP, KEEP = 0.30, 0.26          # Stille über 0,30 s wird auf 0,26 s gekürzt (bis 24.11.: über 0,24 s auf 0,14 s)
KEEP_PAUSE = 0.40                  # Stille an einer [pause] aus dem Skript: bewusste Kunstpause
ZIEL_WPS, MAX_TEMPO = 2.75, 1.04   # bis 24.11.: 3,05 / 1,10


def probe(f):
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]))


def silences(f, noise='-38dB', d=0.12):
    """Stille-Abschnitte direkt aus dem Ton (verlässlicher als Wortzeiten: Scribe rechnet Pausen oft ins Wort)."""
    out = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', f, '-af', f'silencedetect=noise={noise}:d={d}', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r'silence_start: (-?[0-9.]+)', out)]
    en = [float(x) for x in re.findall(r'silence_end: (-?[0-9.]+)', out)]
    return list(zip(st, en + [None] * (len(st) - len(en))))


def is_word(w):
    t = w['text']
    return w.get('type', 'word') == 'word' and not t.startswith('[') and not t.endswith(']') and t not in ('—', '-', '–')


def main():
    W = json.load(open('words_raw.json', encoding='utf-8'))['words']
    W = [w for w in W if w.get('type', 'word') == 'word']
    real = [w for w in W if is_word(w)]
    pauses = [w['start'] for w in W if w['text'].strip().lower() == '[pause]']
    dur = probe('voice_orig.mp3')
    sil = silences('voice_orig.mp3')
    start = 0.0; end = dur
    segs, cur = [], None
    for s0, e0 in sil:
        e0 = dur if e0 is None else e0
        if s0 <= 0.05:                                  # Stille am Anfang: der Hook beginnt bei 0
            start = max(0.0, e0 - 0.03); continue
        if e0 >= dur - 0.02:                            # Stille am Ende: kurzer Ausklang reicht
            end = min(dur, s0 + 0.30); continue
        keep_ = KEEP_PAUSE if any(s0 - 0.15 <= p <= e0 + 0.15 for p in pauses) else KEEP
        if e0 - s0 > max(MAXGAP, keep_ + 0.02):
            segs.append((s0 + keep_ / 2, e0 - keep_ / 2))  # dieser Teil wird entfernt
    keep, cur = [], start
    for a, b in segs:
        if b <= cur or a >= end:
            continue
        keep.append((cur, a)); cur = b
    keep.append((cur, end))
    segs = keep
    cut_len = sum(e - s for s, e in segs)
    wps = len(real) / cut_len
    arg = sys.argv[1] if len(sys.argv) > 1 else 'auto'
    tempo = max(1.0, min(MAX_TEMPO, ZIEL_WPS / wps)) if arg == 'auto' else float(arg)

    def mapt(t):
        acc = 0.0
        for s, e in segs:
            if t < s:
                return acc
            if t <= e:
                return acc + (t - s)
            acc += e - s
        return acc

    for w in W:
        w['start'] = round(mapt(w['start']) / tempo, 3); w['end'] = round(mapt(w['end']) / tempo, 3)
    fl = ''.join(f'[0:a]atrim={s:.3f}:{e:.3f},asetpts=PTS-STARTPTS[a{i}];' for i, (s, e) in enumerate(segs))
    fl += ''.join(f'[a{i}]' for i in range(len(segs))) + f'concat=n={len(segs)}:v=0:a=1[c];[c]atempo={tempo:.4f}[o]'
    subprocess.check_call(['ffmpeg', '-y', '-loglevel', 'error', '-i', 'voice_orig.mp3', '-filter_complex', fl, '-map', '[o]', '-b:a', '192k', 'voice.mp3'])
    fix = json.load(open('fix.json', encoding='utf-8')) if os.path.exists('fix.json') else {}
    for w in W:
        core = w['text'].strip('.,:;!?–-„"“”')
        if core in fix:
            w['text'] = w['text'].replace(core, fix[core])
    json.dump({'words': W}, open('words.json', 'w', encoding='utf-8'), ensure_ascii=False)
    lines = [re.sub(r'\[[a-zA-Z ]+\]\s*', '', l).strip() for l in open('script.txt', encoding='utf-8') if l.strip()]
    json.dump(lines, open('paras.json', 'w', encoding='utf-8'), ensure_ascii=False)
    nd = probe('voice.mp3')
    print(f'Stimme: {dur:.2f} s -> {nd:.2f} s · {len(segs) - 1} Pausen gekürzt · Tempo {tempo:.3f} · {len(real) / nd:.2f} Wörter/s · letztes Wort endet bei {W[-1]["end"]:.2f} s')


if __name__ == '__main__':
    main()
