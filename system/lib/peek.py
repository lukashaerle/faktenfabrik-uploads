"""peek.py – Bilder zu beliebigen Zeitpunkten ansehen (im Episoden-Ordner aufrufen).

    python3 ../lib/peek.py 0 0.5 2.8 15.3            -> peek.png  (ein Bogen, Zeiten in Sekunden ab Videostart)
    python3 ../lib/peek.py --range 3.0 3.6           -> jedes Einzelbild (30 pro Sekunde) von 3,0 bis 3,6 s
    python3 ../lib/peek.py --range 3.0 3.6 0.1       -> alle 0,1 s
    python3 ../lib/peek.py --big 2.8                 -> peek_2.80.png in halber Größe (540x960) zum genauen Hinsehen
    python3 ../lib/peek.py --cols 8 --out x.png ...  -> Spalten / Dateiname

Wofür: Blenden und Auftritte Bild für Bild prüfen (ein Kontaktbogen alle 1 s zeigt die Schnitte nicht).
"""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.getcwd())
import pipeline as PL


def main():
    a = sys.argv[1:]; cols, out, big, times = 6, 'peek.png', False, []
    while a:
        x = a.pop(0)
        if x == '--cols': cols = int(a.pop(0))
        elif x == '--out': out = a.pop(0)
        elif x == '--big': big = True
        elif x == '--range':
            t0, t1 = float(a.pop(0)), float(a.pop(0)); st = 1 / 30
            if a and not a[0].startswith('--'):
                try: st = float(a[0]); a.pop(0)
                except ValueError: pass
            t = t0
            while t <= t1 + 1e-6: times.append(round(t, 4)); t += st
        else: times.append(float(x))
    L = PL.setup()
    from render import skia, W, H, P
    starts = json.load(open('scene_starts.json')); TOTAL = sum(L.DUR); n = len(L.DUR)
    surf = skia.Surface(W, H)

    def shot(T):
        T = min(max(T, 0.0), TOTAL - 1e-3)
        sc = max(i for i in range(n) if starts[i] <= T + 1e-9)
        L.frame(surf, sc, T - starts[sc], L.DUR[sc]); return surf.makeImageSnapshot()

    smp = skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear)
    if big:
        for T in times:
            s2 = skia.Surface(W // 2, H // 2)
            s2.getCanvas().drawImageRect(shot(T), skia.Rect.MakeWH(W // 2, H // 2), smp)
            name = f'peek_{T:.2f}.png'; s2.makeImageSnapshot().save(name, skia.kPNG); print(name)
        return
    cw, ch = 270, 480
    rows = (len(times) + cols - 1) // cols
    sheet = skia.Surface(cols * cw, rows * ch); cs = sheet.getCanvas(); cs.clear(skia.ColorWHITE)
    f = skia.Font(L.FONT, 26)
    for k, T in enumerate(times):
        x, y = (k % cols) * cw, (k // cols) * ch
        cs.drawImageRect(shot(T), skia.Rect.MakeXYWH(x, y, cw, ch), smp)
        cs.drawRect(skia.Rect.MakeXYWH(x, y, 96, 34), P('#000000', 170))
        cs.drawString(f'{T:.2f}', x + 6, y + 26, f, P('#ffffff'))
    sheet.makeImageSnapshot().save(out, skia.kPNG); print(out, len(times), 'Bilder')


if __name__ == '__main__':
    main()
