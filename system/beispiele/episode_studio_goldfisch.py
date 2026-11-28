"""Mythos oder Fakt? #4 – „Drei Sekunden – dann vergisst dein Goldfisch alles“ (29.11.2026, 17:30) · Look STUDIO.

Vorlage für die Reihe „Mythos oder Fakt?“: Behauptung als große Zahl ab Bild 0, zwei Antwort-Chips (Kommentar-Köder),
Urteil als Stempel früh im Video, dann der Beleg als kleine Szene (Hebel, Uhr, Mini-Labyrinth), Loop ins Startbild.
"""
import os
import sys
from math import atan2, degrees

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from studio import *            # noqa
import props as PR              # noqa

SERIE, NAME = ('mythos', 4), 'Goldfisch'
T = total()
umbruch('Sekunden', 1)          # Untertitel: „Drei Sekunden“ | „dann vergisst dein“ | „Goldfisch alles.“

# ---------------------------------------------------------------- Zeitpunkte aus der Aufnahme: wt('Wort', Absatz)
A2, T_FAKT = ps(2), wt('Fakt', 2)
A3 = ps(3)
A4, T_HEBEL, T_BECKEN, T_DRUECK, T_FUTTER = ps(4), wt('Hebel', 4), wt('Becken', 4), wt('Drücken', 4), wt('Futter', 4)
A5, T_EINE = ps(5), wt('eine', 5)
A6, T_GENAU, T_RICHTIG, T_ZEIT = ps(6), wt('genau', 6), wt('richtigen', 6), wt('Zeit', 6)
A7, T_FLUCHT, T_WOCHEN, T_MONATE = ps(7), wt('Fluchtwege', 7), wt('Wochen', 7), wt('Monate', 7)
A8, T_CULUM, T_JAHRE = ps(8), wt('Culum', 8), wt('Jahre', 8)
A9, T_WER, T_DU, T_GOLD9 = ps(9), wt('Wer', 9), wt('du', 9), wt('Goldfisch', 9)
A10 = ps(10)

TX, TZ = -24, -38                                                         # Mitte des Beckens auf der Plattform
BW, BD, BHH = 500, 250, 280                                               # Becken: Breite, Tiefe, Höhe
FS = 1.3                                                                  # Größe des Fischs
PRESS = np.array([TX + 94.0, 142.0, TZ])                                  # Fisch mit der Nase am Hebel
LAB = [(-212, 36), (-100, 84), (-30, 2), (40, -82), (150, -14)]           # Weg durchs Mini-Labyrinth (x, z ab Beckenmitte)
T_LAB0, T_LAB1 = T_FLUCHT - 0.25, T_MONATE + 0.55


def bump(t, a, b, c, d):
    """0 → 1 (zwischen a und b) → 1 (bis c) → 0 (bis d), weich."""
    return eio(pr(t, a, b - a)) * (1 - eio(pr(t, c, d - c)))


def catmull(pts, s):
    P_ = [pts[0]] + list(pts) + [pts[-1]]; n = len(pts) - 1; u = clamp(s) * n; i = min(int(u), n - 1); f = u - i
    p0, p1, p2, p3 = (np.array(P_[i + k], float) for k in range(4))
    return 0.5 * ((2 * p1) + (-p0 + p2) * f + (2 * p0 - 5 * p1 + 4 * p2 - p3) * f * f + (-p0 + 3 * p1 - 3 * p2 + p3) * f ** 3)


def fish_state(t):
    """Wo der Fisch ist und wohin er schaut. Ruhe = ovale Bahn, die bei t = 0 und t = T gleich ist (Loop)."""
    th = 2 * pi * 6 * t / T + 0.6
    idle = np.array([TX - 12 + 118 * cos(th), 142 + 10 * sin(2 * th), TZ + 44 * sin(th)]); vi = np.array([-118 * sin(th), 44 * cos(th)])
    pos, v = idle, vi
    pos = pos - np.array([0.0, 72.0, 0.0]) * bump(t, A3 - 0.30, A3 + 0.30, A4 - 0.08, A4 + 0.55)   # taucht unter dem Stempel durch
    wp = max(bump(t, T_DRUECK - 0.55, T_DRUECK + 0.15, T_FUTTER + 0.35, T_FUTTER + 1.0), bump(t, T_GENAU - 0.45, T_RICHTIG - 0.02, T_ZEIT + 0.45, T_ZEIT + 1.0))
    if wp > 0:                                                            # zum Hebel schwimmen und drücken
        pos = idle + (PRESS - idle) * wp; v = vi * (1 - wp) + np.array([120.0, 0.0]) * wp
    wl = bump(t, T_LAB0 - 0.4, T_LAB0, T_LAB1, T_LAB1 + 0.5)
    if wl > 0:                                                            # Slalom durchs Mini-Labyrinth
        s = eio(pr(t, T_LAB0, T_LAB1 - T_LAB0)) * 0.9 + 0.1 * pr(t, T_LAB0, T_LAB1 - T_LAB0)
        a = catmull(LAB, s); b = catmull(LAB, min(1.0, s + 0.02)); lab = np.array([TX + a[0], 134.0, TZ + a[1]])
        pos = pos + (lab - pos) * wl; v = v * (1 - wl) + (b - a) * 50 * wl
    return pos, degrees(atan2(-v[1], v[0])), sin(t * 9.0)


def draw(c, t):
    st = Stage(c, t).begin()
    st.add(PR.setze(PR.becken(BW, BD, BHH), x=TX, z=TZ), a=0.20, blur=12)
    pos, ry, wag = fish_state(t)
    st.add(PR.setze(PR.fisch(wedel=wag, s=FS), x=pos[0], y=pos[1], z=pos[2], ry=ry), shadow=False, layer=3)

    # --- Absatz 4–6: Hebel im Becken, Futterrohr darüber, Uhr davor
    weg = sink(t, A7 - 0.20, 0.35, 'whoosh')
    if T_HEBEL - 0.2 < t < A7 + 0.3:
        kh = rise(t, T_HEBEL - 0.08, 0.35) * (1 - weg)
        druck = max(bump(t, T_DRUECK + 0.12, T_DRUECK + 0.24, T_DRUECK + 0.5, T_DRUECK + 0.7), bump(t, T_RICHTIG + 0.0, T_RICHTIG + 0.12, T_RICHTIG + 0.4, T_RICHTIG + 0.6))
        if kh > 0.02:
            st.add(PR.setze(PR.hebel(druck), x=TX + 180, y=142, z=TZ, scale=kh), shadow=False, layer=3)
        if t >= T_BECKEN - 0.05 and weg < 1:
            st.add(PR.setze(PR.rohr(BHH + 6, BHH + 96, r=26), x=TX + 112, z=TZ, y=drop(t, T_BECKEN - 0.05, 220, 0.28) + 260 * weg), shadow=False, layer=5)
        for t0 in (T_FUTTER - 0.02, T_ZEIT - 0.02):                       # Futterkörner fallen aus dem Rohr
            for j in range(3):
                f = pr(t, t0 + j * 0.09, 0.55)
                if 0 < f < 1:
                    snd(t0, 'ding', 0.5)
                    st.add(PR.setze(PR.korn(9), x=TX + 112 + (j - 1) * 15, y=lerp(BHH, 116, ei2(f)), z=TZ + (j - 1) * 7), shadow=False, layer=3)
    if A5 - 0.1 < t < A7 + 0.4:
        ku = rise(t, A5 + 0.0, 0.40) * (1 - weg)
        if ku > 0.02:
            zeiger = lerp(5.0, 12.5, eio(pr(t, A5 + 0.5, T_RICHTIG - A5 - 0.45)))
            st.add(PR.setze(PR.uhr(zeiger=zeiger, sektor=pr(t, T_EINE - 0.05, 0.4), r=88), x=246, z=166, scale=ku), a=0.22, blur=9, layer=6)

    # --- Absatz 7: zwei Trennwände wachsen im Becken – der Fisch findet den Weg hindurch
    if A7 - 0.2 < t < A8 + 0.5:
        hw = 186 * rise(t, A7 - 0.05, 0.40) * (1 - sink(t, A8 - 0.05, 0.35))
        if hw > 1:
            st.add(PR.setze(PR.wand(d=150, h=hw), x=TX - 100, z=TZ - 50, y=12), shadow=False, layer=3)
            st.add(PR.setze(PR.wand(d=150, h=hw), x=TX + 40, z=TZ + 50, y=12), shadow=False, layer=3)
    st.end()

    # --- flache Ebene
    ha = (1 - pr(t, A4 - 0.25, 0.2)) if t < 20 else pr(t, T - 0.5, 0.3)      # Titel ab Bild 0 (Cover) und wieder im letzten Bild (Loop)
    kicker(c, 'GOLDFISCH-GEDÄCHTNIS:', 84, 356, ha)
    headline(c, '3', 'SEKUNDEN', ha if t > 1 else 1.0, y=524, size=188)
    if t < A4 + 0.2:
        banner(c, 'MYTHOS?', 84, 548, pop(t, A2 - 0.04) * (1 - pr(t, A3 - 0.2, 0.18)), size=40)
        banner(c, 'FAKT?', 372, 548, pop(t, T_FAKT - 0.04) * (1 - pr(t, A3 - 0.2, 0.18)), bg=GREEN, size=40)
        ks = pr(t, A3 + 0.10, 0.30)
        if ks > 0:                                                         # „Mythos.“: die Behauptung wird durchgestrichen
            c.drawLine(74, 462, 74 + 700 * eo3(ks), 462, P(INK, ha, stroke=13)); snd(A3 + 0.10, 'swipe', 0.9)
        stamp(c, 'MYTHOS', 548, 640, pop(t, A3 - 0.03, 0.30, 'thud') * (1 - pr(t, A4 - 0.25, 0.2)), size=112)
    if T_HEBEL < t < A5 + 0.2:
        hx, hy = st.pt(TX + 184, 182, TZ)
        label(c, hx, hy, 'HEBEL', 150, -150, pop(t, T_HEBEL + 0.12), a=1 - pr(t, A5 - 0.25, 0.2), size=32)
    banner(c, 'NUR 1 STUNDE AM TAG', 84, 344, pop(t, T_EINE - 0.05) * (1 - pr(t, A6 + 0.9, 0.2)), size=38)
    banner(c, 'PÜNKTLICH GEDRÜCKT', 84, 344, pop(t, T_ZEIT - 0.05, sound='thud') * (1 - pr(t, A7 - 0.25, 0.2)), bg=GREEN, size=38)
    if A7 < t < A9:
        kk = pop(t, T_WOCHEN - 0.25, sound=None) * (1 - pr(t, A9 - 0.25, 0.2))
        kicker(c, 'GEMERKT FÜR' if t < T_JAHRE - 0.05 else 'GEDÄCHTNIS: ÜBER', 84, 356, kk)
        headline(c, 'WOCHEN', '', pop(t, T_WOCHEN - 0.04) * (1 - pr(t, T_MONATE - 0.12, 0.1)), y=506, size=140)
        headline(c, 'MONATE', '', pop(t, T_MONATE - 0.04) * (1 - pr(t, T_JAHRE - 0.14, 0.1)), y=506, size=140)
        headline(c, 'JAHRE', '', pop(t, T_JAHRE - 0.04, 0.30, 'thud') * (1 - pr(t, A9 - 0.25, 0.2)), y=506, size=150)
        banner(c, 'C. BROWN · MACQUARIE UNIVERSITY', 84, 548, pop(t, T_CULUM - 0.05) * (1 - pr(t, A9 - 0.25, 0.2)), bg=INK, size=28)
    if A9 < t < A10 + 0.3:
        fa = 1 - pr(t, A10 - 0.15, 0.2)
        kicker(c, 'WER VERGISST MEHR?', 84, 356, pop(t, T_WER - 0.05, sound=None) * fa)
        banner(c, 'DU?', 84, 388, pop(t, T_DU - 0.05) * fa, bg=INK, size=42)
        banner(c, 'DEIN GOLDFISCH?', 84, 486, pop(t, T_GOLD9 - 0.05) * fa, size=42)
    finish(c, t, SERIE)


if __name__ == '__main__':
    main(draw, SERIE, NAME)
