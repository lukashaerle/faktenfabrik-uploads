"""Mach den Test #3 – „Wetten, du kannst diese vier Wörter nicht richtig sagen?“ (Stroop-Test, 29.11.2026, 20:00) · Look STUDIO.

Vorlage für die Reihe „Mach den Test“: Der Test steht ab Bild 0 groß im Bild (dunkle Testkarte, Regel als Zeile auf der Karte).
Die Runden laufen in stillen Testfenstern (recut.json: Abstände ab 1 s) – ein Wort nach dem anderen wird markiert, unten läuft
der Zeitbalken, auf der Bühne die Stoppuhr; die Lampen zeigen nach jedem Wort die richtige Farbe. Danach: Lösung, Erklärung an
EINEM Beispiel, Vergleichsrunde, Bitte um das Ergebnis, Loop ins Startbild.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import studio as S              # noqa
from studio import *            # noqa
import props as PR              # noqa

SERIE, NAME = ('test', 3), 'Stroop'
T = total()

# ---------------------------------------------------------------- Zeitpunkte aus der Aufnahme
T_VIER = wt('vier', 1)
A2, T_FARBE, T_LOS = ps(2), wt('Farbe', 2), wt('Los', 2)
A3, T_JETZT, T_DOPPELT = ps(3), wt('Jetzt', 3), wt('doppelt', 3)
A4, T_STROOP, T_BESCHR, T_1935 = ps(4), wt('Stroop', 4), wt('beschrieben', 4), wt('1935', 4)
A5, T_LIEST, T_KAUM, T_ABSCH = ps(5), wt('liest', 5), wt('kaum', 5), wt('abschalten', 5)
A6, T_FUNKT = ps(6), wt('funkt', 6)
A7, T_PASSEN = ps(7), wt('Passen', 7)
A8, T_WIE = ps(8), wt('wie', 8)
A9 = ps(9)

# Die drei Runden liegen in den stillen Testfenstern und enden kurz vor dem nächsten Satz
DT1, DT2 = 0.75, 0.375                       # Sekunden je Wort: Runde 1 · Runde 2 und 3 („doppelt so schnell“)
R1 = A3 - 0.15 - 4 * DT1
R2 = A4 - 0.28 - 4 * DT2
R3 = A8 - 0.22 - 4 * DT2

# ---------------------------------------------------------------- Testkarte (flach, dunkel)
FARBE = {'ROT': '#F23B2E', 'BLAU': '#3E8BFF', 'GRÜN': '#2FC46E', 'GELB': '#FFC61A'}
SATZ_A = [('ROT', 'BLAU'), ('GELB', 'ROT'), ('BLAU', 'GRÜN'), ('GRÜN', 'GELB')]       # (Wort, Farbe der Schrift) – Startbild und Runde 1
SATZ_B = [('GELB', 'GRÜN'), ('GRÜN', 'BLAU'), ('ROT', 'GELB'), ('BLAU', 'ROT')]       # Runde 2: neue Wörter, doppeltes Tempo
SATZ_C = [('BLAU', 'BLAU'), ('ROT', 'ROT'), ('GELB', 'GELB'), ('GRÜN', 'GRÜN')]       # Vergleich: Wort und Farbe passen
RUNDEN = [(R1, DT1, SATZ_A, T_JETZT), (R2, DT2, SATZ_B, T_BESCHR), (R3, DT2, SATZ_C, A9 + 0.2)]   # (Start, Takt, Wörter, Anzeige zurück)
KX0, KX1, KY0, KY1 = 84, 996, 372, 852       # Karte
GY0, ZH = 458, 178                           # Wortfeld: obere Kante, Zeilenhöhe
AUS = '#2C4047'                              # Lampe aus


def fade(t, a, b, fi=0.16, fo=0.14):
    """Sichtbarkeit 0..1 zwischen den Sekunden a und b (weich ein, weich aus)."""
    return pr(t, a, fi) * (1 - pr(t, b - fo, fo))


def runde(t, r0, dt):
    """(markiertes Wort 0..3 oder None, Fortschritt 0..4)"""
    if t < r0:
        return None, 0.0
    f = (t - r0) / dt
    return (None, 4.0) if f >= 4 else (int(f), f)


def zelle(i):
    return KX0 + 228 + (i % 2) * 456, GY0 + ZH / 2 + (i // 2) * ZH


def karte(c):
    rrect(c, KX0 + 10, KY0 + 22, KX1 - KX0 - 20, KY1 - KY0, 30, P('#0B2A30', 0.30, blur=26))
    rrect(c, KX0, KY0, KX1 - KX0, KY1 - KY0, 30, P(INK))
    c.save(); c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(KX0, KY0, KX1, KY1), 30, 30), True)
    c.drawRect(skia.Rect.MakeLTRB(KX0, KY0, KX1, KY1), lin(KX0, KY0, KX1, KY1, [C(WHITE, 0.07), C(WHITE, 0.0)]))
    c.restore()
    text(c, 'SAG DIE FARBE – NICHT DAS WORT', KX0 + 40, KY0 + 54, font('mono', 27), P(WHITE, 0.94), 'l', 3.4)
    c.drawLine(KX0 + 40, KY0 + 82, KX1 - 40, KY0 + 82, P(WHITE, 0.13, stroke=2))
    S._reg('karte', 'Testkarte', KX0, KY0, KX1, KY1)


def woerter(c, t, satz, a, r0=None, dt=None, loesung=0.0, demo=0.0, puls=None):
    """Vier Farbwörter 2 × 2. r0/dt: Runde (markiert ein Wort nach dem anderen). loesung 0..1: richtige Farbe unter jedem Wort."""
    if a <= 0:
        return
    hi, fr = runde(t, r0, dt) if r0 is not None else (None, 0.0)
    f = font('black', 118); fp = font('mono', 25)
    for i, (wort, farbe) in enumerate(satz):
        cx, cy = zelle(i)
        kp = max(clamp(loesung * 1.3 - i * 0.1), demo if i == 0 else 0.0)
        aw = a * (1.0 if hi is None or hi == i else 0.24)
        sc = 1.0
        if hi == i:
            k = pr(t, r0 + i * dt, 0.16); sc = 1 + 0.05 * sin(pi * k)
            rrect(c, cx - 214, cy - 80, 428, 160, 22, P(WHITE, 0.10 * a)); rrect(c, cx - 214, cy - 80, 428, 160, 22, P(WHITE, 0.92 * a, stroke=4))
        if puls is not None:
            sc = 1 + 0.07 * sin(pi * pr(t, puls + i * 0.09, 0.22))
        c.save(); c.translate(cx, cy + 43 - 22 * eo3(kp)); c.scale(sc, sc)
        text(c, wort, 0, 0, f, P(FARBE[farbe], aw), 'c', -1)
        c.restore()
        if kp > 0:                                                           # Lösung: Farbfeld mit dem Namen der Farbe
            s = ('SAG: ' if demo > 0 and i == 0 and loesung <= 0 else '') + farbe
            w = tw(s, fp, 2.5) + 40; kb = back(kp, 1.5)
            c.save(); c.translate(cx, cy + 62); c.scale(kb, kb)
            rrect(c, -w / 2, -21, w, 42, 12, P(FARBE[farbe], a)); text(c, s, 0, 9, fp, P(INK, a), 'c', 2.5)
            c.restore()
    # Zeitbalken: ein Feld je Wort
    x0, y0, ws = KX0 + 40, KY1 - 31, (KX1 - KX0 - 80 - 30) / 4
    aus = 1 - pr(t, r0 + 4 * dt + 0.5, 0.3) if r0 is not None else 0.0
    for i in range(4):
        rrect(c, x0 + i * (ws + 10), y0, ws, 10, 5, P(WHITE, 0.15 * a))
        fi = clamp(fr - i)
        if fi > 0 and aus > 0:
            rrect(c, x0 + i * (ws + 10), y0, max(10.0, ws * fi), 10, 5, P(WHITE, 0.95 * a * aus))


def zweimal(c, a, k):
    """Zwischen Runde 1 und 2: „2× so schnell“."""
    if a <= 0:
        return
    sc = lerp(0.8, 1.0, back(k, 1.6))
    c.save(); c.translate(540, 676); c.scale(sc, sc)
    text(c, '2×', 0, 0, font('black', 210), P(WHITE, a), 'c', -2)
    c.restore()
    text(c, 'SO SCHNELL', 540, 752, font('mono', 34), P(WHITE, 0.78 * a), 'c', 8)


def beispiel(c, t, a):
    """Erklärung an EINEM Wort: BLAU in roter Schrift – du liest „BLAU“, richtig wäre „ROT“."""
    if a <= 0:
        return
    bx = lerp(540, 336, eio(pr(t, T_LIEST - 0.30, 0.35)))                    # erst mittig, dann nach links: rechts erscheint die Erklärung
    text(c, 'BLAU', bx, 696, font('black', 170), P(FARBE['ROT'], a), 'c', -2)
    c.drawLine(590, 500, 590, 776, P(WHITE, 0.13 * a * eo3(pr(t, T_LIEST - 0.10, 0.20)), stroke=2))
    fl, fv = font('mono', 24), font('black', 64)
    k1 = pop(t, T_LIEST - 0.05) * a
    if k1 > 0:
        text(c, 'DU LIEST', 626, 556, fl, P(WHITE, 0.62 * eo3(k1)), 'l', 3)
        text(c, 'BLAU', 624, 624 + 12 * (1 - eo3(k1)), fv, P(WHITE, eo3(k1)), 'l', -0.5)
    k2 = pop(t, A6 + 0.05) * a
    if k2 > 0:
        zit = 7 * sin((t - T_FUNKT) * 46) * (1 - pr(t, T_FUNKT, 0.75)) if t >= T_FUNKT else 0.0     # „funkt dazwischen“: die richtige Antwort wackelt
        text(c, 'RICHTIG', 626, 700, fl, P(WHITE, 0.62 * eo3(k2)), 'l', 3)
        text(c, 'ROT', 624 + zit, 768 + 12 * (1 - eo3(k2)), fv, P(FARBE['ROT'], eo3(k2)), 'l', -0.5)
    kb = pop(t, T_FUNKT - 0.03, 0.22, 'thud', 0.7) * a
    if kb > 0:                                                               # Blitz von der gelesenen zur richtigen Antwort
        sc = back(kb, 1.7)
        c.save(); c.translate(884, 664); c.scale(sc, sc)
        p = skia.Path(); p.moveTo(14, -62); p.lineTo(-30, 8); p.lineTo(-4, 8); p.lineTo(-16, 62); p.lineTo(32, -14); p.lineTo(4, -14); p.close()
        c.drawPath(p, P(ACC, a))
        c.restore()


def ergebnis(c, t, a):
    """Bitte: „Wie oft gestolpert?“ – vier Antworten zum Kommentieren."""
    if a <= 0:
        return
    text(c, 'WIE OFT GESTOLPERT?', 540, 596, font('black', 62), P(WHITE, a), 'c', -0.5)
    f = font('black', 50)
    for i, (s, col) in enumerate((('0×', 'GRÜN'), ('1×', 'BLAU'), ('2×', 'GELB'), ('3×+', 'ROT'))):
        k = pop(t, T_WIE - 0.05 + i * 0.13, 0.24, 'pop', 0.6) * a
        if k <= 0:
            continue
        cx = 540 + (i - 1.5) * 190; sc = back(k, 1.6)
        c.save(); c.translate(cx, 712); c.scale(sc, sc)
        rrect(c, -80, -46, 160, 92, 22, P(FARBE[col], a)); text(c, s, 0, 18, f, P(INK, a), 'c', -0.5)
        c.restore()


# ---------------------------------------------------------------- Bühne: Stoppuhr, vier Lampen, Kippschalter
def uhr_anteil(t):
    v = 0.0
    for r0, dt, _, zurueck in RUNDEN:
        if t >= r0:
            v = clamp((t - r0) / (4 * dt)) * (1 - eio(pr(t, zurueck, 0.35)))
    return v


def lampe(t, i):
    """Farbe und Höhe der Lampe i: weiß, solange das Wort dran ist, danach die richtige Farbe."""
    col, h = AUS, 12.0
    for r0, dt, satz, zurueck in RUNDEN:
        if r0 + i * dt <= t < zurueck:
            col, h = (WHITE, 26.0) if t < r0 + (i + 1) * dt else (FARBE[satz[i][1]], 20.0)
    if T_WIE + i * 0.28 <= t < A9 + 0.2:                                      # „wie oft gestolpert“: eins, zwei, drei, vier
        col, h = ACC, 20.0
    return col, h


def kipp(t):
    """Der Hebel will auf AUS – und schnappt zurück (zweimal): Lesen lässt sich kaum abschalten."""
    k = 0.0
    for t0 in (T_KAUM - 0.42, T_ABSCH + 0.10):
        if t0 <= t < t0 + 0.34:
            k = 0.85 * eio((t - t0) / 0.34)
        elif t0 + 0.34 <= t < t0 + 0.50:
            k = 0.85 * (1 - eo3((t - t0 - 0.34) / 0.16))
        snd(t0 + 0.34, 'tick', 1.0)
    return k


def draw(c, t):
    st = Stage(c, t, plat=(640, 360, 56), zoom=(0.86, 0.885), center=(540, 1108)).begin()
    an = uhr_anteil(t)
    st.add(PR.setze(PR.uhr(zeiger=12 * an, sektor=an, r=88, winkel=360.0, krone=True), x=-212, z=-10), a=0.22, blur=9)
    kl = (1 - sink(t, A5 - 0.40, 0.30, 'whoosh')) if t < A7 else 1.0         # Lampen machen dem Schalter Platz und kommen zur Vergleichsrunde wieder
    for i in range(4):
        k = kl if t < A7 else rise(t, A7 + 0.10 + i * 0.07, 0.34, 'pop' if i == 0 else None)
        if k > 0.03:
            col, h = lampe(t, i)
            st.add(PR.setze(PR.lampe(col, h), x=-62 + i * 98, z=52, scale=k), a=0.20, blur=7)
    if A5 - 0.2 < t < A7 + 0.3:
        ks = rise(t, A5 - 0.06, 0.38) * (1 - sink(t, A7 - 0.22, 0.30))
        if ks > 0.03:
            st.add(PR.setze(PR.schalter(kipp(t)), x=92, z=44, scale=ks), a=0.22, blur=9)
    st.end()

    # --- flache Ebene: Zeile über der Karte
    for a, b, s in ((-1, T_LOS - 0.05, 'SCHAFFST DU ALLE VIER?'), (T_LOS - 0.05, T_JETZT, 'RUNDE 1'), (T_JETZT, T_STROOP - 0.05, 'RUNDE 2 · DOPPELTES TEMPO'),
                    (T_STROOP - 0.05, A7 - 0.05, 'DER STROOP-EFFEKT'), (A7 - 0.05, A8 - 0.05, 'ZUM VERGLEICH: WORT = FARBE'),
                    (A8 - 0.05, A9 + 0.30, 'AB IN DIE KOMMENTARE'), (A9 + 0.30, T + 1, 'SCHAFFST DU ALLE VIER?')):
        kicker(c, s, 84, 346, fade(t, a, b))
    k35 = pop(t, T_1935 - 0.04) * (1 - pr(t, A7 - 0.19, 0.14))
    if k35 > 0:
        x35 = 84 + tw('DER STROOP-EFFEKT', font('mono', 28), 4) + 26
        c.save(); c.translate(x35, 336); c.scale(back(k35, 1.6), back(k35, 1.6)); chip(c, '1935', 0, -20, font('mono', 26), WHITE, ACC, padx=14, pady=10, r=8, track=3); c.restore()
        S._reg('zeile', '1935', x35, 316, x35 + 110, 356)

    # --- Testkarte
    karte(c)
    woerter(c, t, SATZ_A, fade(t, -1, T_JETZT), R1, DT1, loesung=pop(t, A3 - 0.02), demo=pop(t, T_FARBE - 0.05) * (1 - pr(t, T_LOS - 0.10, 0.14)),
            puls=T_VIER if t < A2 else None)
    zweimal(c, fade(t, T_JETZT + 0.04, R2 - 0.30, 0.12, 0.10), pop(t, T_DOPPELT - 0.04, 0.28, 'thud'))
    woerter(c, t, SATZ_B, fade(t, R2 - 0.30, T_BESCHR - 0.04, 0.10), R2, DT2, loesung=pop(t, A4 - 0.02))
    beispiel(c, t, fade(t, T_BESCHR, T_PASSEN - 0.04))
    woerter(c, t, SATZ_C, fade(t, T_PASSEN, A8 + 0.20), R3, DT2)
    ergebnis(c, t, fade(t, A8 + 0.24, A9 + 0.30))
    woerter(c, t, SATZ_A, fade(t, A9 + 0.34, T + 1))

    # --- Etikett am Schalter
    if T_LIEST - 0.1 < t < A7:
        lx, ly = st.pt(92 + 58, 30 + 118, 44)
        label(c, lx, ly, 'LESEN', 190, -44, pop(t, T_LIEST + 0.10), a=1 - pr(t, A7 - 0.30, 0.2), size=32)

    # --- Töne der Runden: Startsignal, dann ein Tick je Wort
    for r0, dt, _, _ in RUNDEN:
        snd(r0, 'ding', 0.55)
        for i in (1, 2, 3):
            snd(r0 + i * dt, 'tick', 1.0)
    for i in range(4):
        snd(T_VIER + i * 0.09, 'tick', 0.55)
    snd(A9 + 0.34, 'swipe', 0.7)
    finish(c, t, SERIE)


if __name__ == '__main__':
    main(draw, SERIE, NAME)
