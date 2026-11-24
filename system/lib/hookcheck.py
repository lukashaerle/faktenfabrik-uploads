"""FAKTENFABRIK – Hook- und Aufbau-Prüfung (Viral-Aufbau V3).

Aufruf im Episodenordner:
    python3 ../lib/hookcheck.py                  prüft script.txt (10 Zeilen); liegen words.json + durs.json vor, auch die Zeiten
    python3 ../lib/hookcheck.py --hooks hooks.txt   bewertet mehrere Hook-Varianten (eine pro Zeile), beste zuerst

Geprüft wird nur, was sich zählen lässt (Länge, Du-Bezug, Zahl/Datum, Einsatz, Bitte, Loop, Tempo).
Ob der Hook inhaltlich stimmt und belegt ist, prüft der Faktencheck – nicht dieses Skript.
"""
import json
import os
import re
import sys

TAG = re.compile(r'\[[a-zA-Z ]+\]\s*')
WORD = re.compile(r"[0-9A-Za-zÄÖÜäöüß€%]+(?:[.,][0-9]+)?")

DU = {'du', 'dich', 'dir', 'dein', 'deine', 'deinen', 'deinem', 'deiner', 'deines', 'dir.', 'euch', 'euer', 'eure'}
IMPERATIV = {'halte', 'halt', 'mach', 'schau', 'guck', 'achte', 'kauf', 'streck', 'probier', 'schick', 'wetten', 'zähl', 'zähle',
             'drück', 'leg', 'stell', 'nimm', 'prüf', 'prüfe', 'check', 'lies', 'hör', 'öffne', 'vergiss', 'merk', 'klick', 'tipp'}
ZAHLWORT = {'null', 'ein', 'eine', 'einen', 'eins', 'zwei', 'drei', 'vier', 'fünf', 'sechs', 'sieben', 'acht', 'neun', 'zehn', 'elf', 'zwölf',
            'zwanzig', 'dreißig', 'vierzig', 'fünfzig', 'hundert', 'tausend', 'million', 'millionen', 'milliarde', 'milliarden',
            'halb', 'halbe', 'doppelt', 'dreimal', 'zweimal', 'prozent', 'euro', 'cent', 'sekunden', 'minuten', 'stunden', 'tage', 'kilometer'}
ZEIT = {'heute', 'morgen', 'jetzt', 'montag', 'dienstag', 'mittwoch', 'donnerstag', 'freitag', 'samstag', 'sonntag', 'januar', 'februar',
        'märz', 'april', 'mai', 'juni', 'juli', 'august', 'september', 'oktober', 'november', 'dezember', 'silvester', 'weihnachten',
        'woche', 'nacht', 'abend', 'früh'}
EINSATZ = {'weg', 'kostet', 'kosten', 'teurer', 'teuer', 'verlierst', 'verlieren', 'strafe', 'bußgeld', 'frist', 'sonst', 'falsch',
           'fehler', 'lügt', 'trick', 'fake', 'nur', 'nie', 'niemals', 'verboten', 'gefährlich', 'sparst', 'spart', 'sparen', 'zahlst',
           'zahlen', 'geld', 'abzocke', 'endet', 'riesig', 'kaputt', 'illegal', 'pflicht', 'musst', 'darfst', 'recht', 'unrecht',
           'irrtum', 'mythos', 'stimmt', 'wetten', 'schaffst', 'kannst', 'betrogen', 'umsonst', 'gratis', 'doppelt', 'mehr', 'weniger',
           'kleiner', 'größer', 'schneller', 'langsamer', 'bevor', 'statt', 'täuscht', 'trickst', 'lüge', 'warnung', 'achtung', 'stopp'}
FUELLSTART = ['wusstest du', 'hast du dich', 'heute geht', 'in diesem video', 'hallo', 'hey ', 'stell dir vor', 'was ist ', 'wer ist ',
              'warum ', 'wieso ', 'weshalb ', 'kennst du', 'schon mal gefragt', 'willkommen', 'ich zeige', 'ich erkläre']
FLOSKEL = ['kommt am schluss', 'kommt ganz am schluss', 'aber warte', 'bleib dran', 'bleib bis zum', 'gleich verrate', 'am ende verrate',
           'du wirst nicht glauben', 'das glaubst du nicht', 'der verrückteste teil', 'es wird noch']
BITTE = {'teilen': ['schick', 'teil das', 'teile das', 'zeig das', 'leite'], 'kommentar': ['schreib', 'kommentier', 'sag mir', 'verrat mir'],
         'speichern': ['speicher', 'merk dir das video']}
BETTELN = ['folge ', 'folg ', 'abonnier', 'like ', 'liken', 'daumen hoch', 'lass ein abo']
OFFEN = (':', '–', '-', '…', '...')


def clean(s):
    return TAG.sub('', s).strip()


def words(s):
    return WORD.findall(clean(s))


def konkret(w):
    lw = w.lower()
    return any(ch.isdigit() for ch in w) or lw in ZAHLWORT or lw in ZEIT or '€' in w or '%' in w


def hook_score(line):
    """0–100 Punkte + Liste der Abzüge."""
    ws = words(line); low = [w.lower() for w in ws]; txt = ' ' + clean(line).lower() + ' '
    pts, notes = 0, []
    n = len(ws)
    if n <= 8: pts += 20
    elif n <= 10: pts += 15
    elif n <= 12: pts += 8; notes.append(f'{n} Wörter – Ziel höchstens 10')
    else: notes.append(f'{n} Wörter – viel zu lang (höchstens 10)')
    if any(w in DU for w in low) or (low and low[0] in IMPERATIV):
        pts += 20
    else:
        notes.append('kein „du/dein" und kein Befehl am Anfang')
    if any(konkret(w) for w in ws):
        pts += 20
    else:
        notes.append('keine Zahl, kein Datum, kein „heute/Montag"')
    if any(w in EINSATZ for w in low):
        pts += 20
    else:
        notes.append('kein Einsatz (Geld, Frist, falsch, weg, nur …)')
    early = low[:4]
    if any(konkret(w) for w in ws[:4]) or any(w in EINSATZ for w in early) or (early and early[0] in IMPERATIV):
        pts += 10
    else:
        notes.append('die ersten 4 Wörter tragen nichts (Zahl/Einsatz/Befehl nach vorn)')
    if any(txt.strip().startswith(f.strip()) for f in FUELLSTART):
        pts -= 30; notes.append('Füll-Einstieg (Wissensfrage/„Wusstest du") – verboten')
    else:
        pts += 10
    return max(0, min(100, pts)), notes


def check_script(path='script.txt'):
    lines = [l.rstrip('\n') for l in open(path, encoding='utf-8') if l.strip()]
    probs, warns = [], []
    n = len(lines)
    if not 8 <= n <= 10:
        probs.append(f'{n} Absätze – erlaubt sind 8 bis 10 (Standard 10)')
    total = sum(len(words(l)) for l in lines)
    chars = sum(len(l) for l in lines)
    sc, notes = hook_score(lines[0])
    print(f'HOOK  {sc:3d}/100  „{clean(lines[0])}"')
    for nt in notes:
        print('        –', nt)
    if sc < 70:
        probs.append(f'Hook nur {sc}/100 (Mindestwert 70) – andere Formel wählen, nicht nachpolieren')
    # 25.11.2026: ruhigeres Tempo (tighten.py) macht das Video bei gleichem Text ca. 10 % länger – daher 75–90 Wörter
    if total > 98:
        probs.append(f'{total} Wörter – höchstens 98 (Ziel 75–90)')
    elif total > 90:
        warns.append(f'{total} Wörter – über dem Ziel 75–90 (das Video wird mit dem ruhigeren Tempo länger als 34 s)')
    elif total < 62:
        warns.append(f'{total} Wörter – sehr kurz (Ziel 75–90)')
    if chars > 750:
        probs.append(f'{chars} Zeichen inkl. Tags – höchstens 750')
    for i, l in enumerate(lines, 1):
        k = len(words(l))
        if k > 15:
            probs.append(f'Absatz {i}: {k} Wörter – höchstens 15 (teilen oder kürzen)')
        elif k > 13:
            warns.append(f'Absatz {i}: {k} Wörter – lang (über 4 s), braucht zwei Einstellungen')
        low = ' ' + clean(l).lower() + ' '
        for f in FLOSKEL:
            if f in low:
                probs.append(f'Absatz {i}: Ankündigungs-Floskel „{f}" – streichen')
        for b in BETTELN:
            if b in low:
                probs.append(f'Absatz {i}: Bettel-Aufruf „{b.strip()}" – streichen')
    arten = set()
    for l in lines:
        low = clean(l).lower()
        for art, keys in BITTE.items():
            if any(k in low for k in keys):
                arten.add(art)
    if not arten:
        probs.append('keine Bitte (genau EINE: teilen ODER kommentieren ODER speichern)')
    elif len(arten) > 1:
        probs.append('mehr als eine Bitte (' + ', '.join(sorted(arten)) + ') – nur EINE')
    last = clean(lines[-1])
    if not last.endswith(OFFEN):
        probs.append('letzter Absatz ist keine Loop-Zeile (offener Halbsatz, der in Satz 1 mündet, endet auf „:" oder „–")')
    if len(words(lines[-1])) > 11:
        warns.append('Loop-Zeile länger als 11 Wörter')
    zahlen = sum(1 for l in lines if any(any(ch.isdigit() for ch in w) or w.lower() in ZAHLWORT for w in words(l)))
    if zahlen < 3:
        warns.append(f'nur {zahlen} Absätze mit Zahl – Zahlen statt Adjektive (Ziel mindestens 3)')
    print(f'SKRIPT  {n} Absätze · {total} Wörter · {chars} Zeichen · Bitte: {", ".join(sorted(arten)) or "–"} · Loop: {"ja" if last.endswith(OFFEN) else "NEIN"}')
    return probs, warns, lines


def check_timing(probs, warns):
    if not (os.path.exists('words.json') and os.path.exists('durs.json') and os.path.exists('para_word_idx.json')):
        print('ZEITEN  (noch keine Aufnahme – nach `pipeline.py timing` erneut prüfen)')
        return
    W = json.load(open('words.json'))['words']
    W = [w for w in W if w.get('type', 'word') == 'word' and not w['text'].startswith('[') and not w['text'].endswith(']')
         and w['text'] not in ('—', '-', '–')]                      # wie pipeline.load_words(): Regie-Tags und Striche zählen nicht
    D = json.load(open('durs.json')); st = json.load(open('para_word_idx.json'))
    total = sum(D)
    hook_end = W[st[1] - 1]['end'] if len(st) > 1 else W[-1]['end']
    wps = len(W) / max(0.1, W[-1]['end'] - W[0]['start'])
    gap = max((b['start'] - a['end'] for a, b in zip(W, W[1:])), default=0)
    print(f'ZEITEN  Länge {total:.1f} s · Hook endet bei {hook_end:.2f} s · {wps:.2f} Wörter/s · längste Pause {gap:.2f} s · längste Szene {max(D):.2f} s')
    if hook_end > 3.5:
        probs.append(f'Hook endet erst bei {hook_end:.2f} s – höchstens 3,5 s (Ziel 2,8): Stimme straffen (tighten.py) oder Hook kürzen')
    elif hook_end > 2.8:
        warns.append(f'Hook endet bei {hook_end:.2f} s – Ziel höchstens 2,8 s (nächstes Mal höchstens 9 Wörter)')
    if total > 42:
        probs.append(f'Video {total:.1f} s – höchstens 42 s (Ziel 28–38): Pausen kürzen, atempo bis 1,10')
    elif total > 38:
        warns.append(f'Video {total:.1f} s – über dem Ziel 28–38 s')
    elif total < 22:
        warns.append(f'Video {total:.1f} s – sehr kurz')
    # Tempo (Lukas, 25.11.2026: rund 3 Wörter/s ohne Pausen war „schon sehr schnell“ – ein Ticken langsamer)
    if wps < 2.35:
        probs.append(f'{wps:.2f} Wörter/s – zu langsam (Ziel 2,55–2,9): Pausen kürzen oder tighten.py mit höherem Tempo')
    elif wps < 2.5:
        warns.append(f'{wps:.2f} Wörter/s – etwas langsam (Ziel 2,55–2,9)')
    elif wps > 2.95:
        warns.append(f'{wps:.2f} Wörter/s – schneller als gewünscht (Ziel 2,55–2,9; Lukas: „ein Ticken langsamer“)')
    if max(D) > 5.2:
        probs.append(f'eine Szene dauert {max(D):.1f} s – höchstens 5,2 s')
    if gap > 0.45:
        warns.append(f'Pause von {gap:.2f} s zwischen zwei Wörtern – auf höchstens 0,3 s kürzen')


def main():
    if len(sys.argv) > 2 and sys.argv[1] == '--hooks':
        rows = [(hook_score(l), clean(l)) for l in open(sys.argv[2], encoding='utf-8') if l.strip()]
        rows.sort(key=lambda r: -r[0][0])
        for (sc, notes), l in rows:
            print(f'{sc:3d}/100  „{l}"' + ('' if not notes else '   – ' + '; '.join(notes)))
        best = rows[0]
        print('\nGEWINNER:', best[1], f'({best[0][0]}/100)' + ('' if best[0][0] >= 70 else '  – UNTER 70: neue Hooks schreiben'))
        return
    probs, warns, _ = check_script(sys.argv[1] if len(sys.argv) > 1 else 'script.txt')
    check_timing(probs, warns)
    for w in warns:
        print('  Hinweis:', w)
    for p in probs:
        print('  PROBLEM:', p)
    print('HOOKCHECK OK' if not probs else f'HOOKCHECK: {len(probs)} Problem(e) – erst beheben, dann Stimme erzeugen bzw. rendern')
    sys.exit(0 if not probs else 1)


if __name__ == '__main__':
    main()
