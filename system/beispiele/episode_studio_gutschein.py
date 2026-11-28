"""Kleingedruckt #4 – „Dein Gutschein von 2023 gilt nur noch bis Silvester“ (29.11.2026, 11:30) · Look STUDIO.

Vorlage für die Reihe „Kleingedruckt“: Produkt + Zahl ab Bild 0, Zeitstrahl aus Blöcken, Urteil als Stempel,
Merkregel aus drei Blöcken, Schluss läuft ins Startbild zurück (Loop).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from studio import *            # noqa
import props as PR              # noqa

SERIE, NAME = ('kleingedruckt', 4), 'Gutschein'
T = total()

# ---------------------------------------------------------------- Zeitpunkte aus der Aufnahme: wt('Wort', Absatz)
T_2023, T_NUR, T_SILV1 = wt('2023', 1), wt('nur', 1), wt('Silvester', 1)
A2, T_GELTEN, T_DREI = ps(2), wt('gelten', 2), wt('drei', 2)
T_FRIST, T_ERST, T_KAUFJ = wt('Frist', 3), wt('erst', 3), wt('Kaufjahres', 3)
T_MAERZ, T_DANN, T_SILV = wt('März', 4), wt('Dann', 4), wt('Silvester', 4)
A5, T_SCHLUSS, T_VIER = ps(5), wt('Schluss', 5), wt('vier', 5)
A6, T_EIN = ps(6), wt('ein', 6, nth=1)
T_UNW, T_DREI7 = wt('unwirksam', 7), wt('drei', 7)
A8, T_KJ8, T_DREI8, T_BIS8 = ps(8), wt('Kaufjahr', 8), wt('drei', 8), wt('bis', 8)
A9, T_SCHUB = ps(9), wt('Gutschein-Schublade', 9)
A10 = ps(10)

# ---------------------------------------------------------------- der Gutschein: Haltungen und Flug dazwischen
HOOK0 = dict(p=(156, 286, -6), rx=42, ry=-12, rz=5, s=1.12, bob=1)        # Bild 0 (und letztes Bild – Loop)
HOOK = dict(p=(132, 238, -6), rx=38, ry=-8, rz=0, s=1.12, bob=1)
OBEN = dict(p=(222, 318, -60), rx=27, ry=-5, rz=0, s=0.9, bob=1)          # schwebt klein über dem Zeitstrahl
MITTE = dict(p=(6, 176, 70), rx=46, ry=0, rz=0, s=1.24, bob=0.4)          # groß in der Mitte
LADE = dict(p=(28, 96, 232), rx=34, ry=10, rz=0, s=0.42, bob=0)           # liegt in der Schublade
KEYS = [(0.0, HOOK0), (1.3, HOOK), (A2 - 0.15, HOOK), (A2 + 0.55, OBEN), (A6 - 0.10, OBEN), (A6 + 0.65, MITTE), (A8 - 0.15, MITTE),
        (A8 + 0.55, OBEN), (T_SCHUB + 0.20, OBEN), (T_SCHUB + 0.90, LADE), (A10 + 0.0, LADE), (A10 + 1.15, HOOK0), (T, HOOK0)]


def card_pose(t):
    for (t0, a), (t1, b) in zip(KEYS, KEYS[1:]):
        if t <= t1:
            k = eio(pr(t, t0, max(1e-6, t1 - t0)))
            v = {key: lerp(a[key], b[key], k) for key in ('rx', 'ry', 'rz', 's', 'bob')}
            p = np.array([lerp(a['p'][i], b['p'][i], k) for i in range(3)])
            p[1] += 7 * sin(2 * pi * 12 * t / T) * v['bob']
            return p, rot(v['rx'], v['ry'], v['rz'] + 1.2 * sin(2 * pi * 12 * t / T) * v['bob'], v['s'])
    a = KEYS[-1][1]; return np.array(a['p'], float), rot(a['rx'], a['ry'], a['rz'], a['s'])


XB = [-300, -150, 0, 150, 300]; Z0, Z1, HB, ZP = -10, 130, 56, 60          # Zeitstrahl aus vier Jahresblöcken
XKAUF = XB[0] + 150 * (2.5 / 12)                                           # gekauft im März 2023


def draw(c, t):
    st = Stage(c, t).begin()
    pos, R = card_pose(t)

    # --- Hook und Schluss: Abreißkalender „31 DEZ“ neben dem Gutschein (Bild 0 = letztes Bild)
    kk = (1 - sink(t, A2 - 0.12, 0.45, 'whoosh')) if t < 20 else rise(t, A10 + 0.95, 0.45)
    if kk > 0.01:
        hop = 16 * sin(pi * pr(t, T_SILV1 - 0.04, 0.32)); snd(T_SILV1 - 0.04, 'tick', 1.0)      # „… bis Silvester“: der Kalender hüpft kurz
        st.add(PR.setze(PR.kalender('31', 'DEZ', k=kk), x=-176, z=40, y=hop, scale=1.34))

    # --- Absatz 2–5: Zeitstrahl aus vier Jahresblöcken
    weg = sink(t, A6 - 0.15, 0.45, 'whoosh')
    if T_GELTEN - 0.2 < t < A6 + 0.4:
        for i in range(4):
            h = HB * rise(t, T_GELTEN - 0.10 + i * 0.10) * (1 - weg)
            if h > 0.5:
                st.add(PR.block(XB[i] + 3, XB[i + 1] - 3, Z0, Z1, h, txt=str(2023 + i)), a=0.22, blur=7)
        top = HB * (1 - weg)
        if t >= A5 - 0.05 and weg < 1:                                     # „Drei Jahre später“: Streifen wächst über 2024–2026
            bx = lerp(XB[1], XB[4], eio(pr(t, A5 - 0.05, T_SCHLUSS - A5)))
            for f_ in (0.437, 0.563):                                      # Klick, wenn der Streifen eine Jahresgrenze überfährt
                snd(A5 - 0.05 + (T_SCHLUSS - A5) * f_, 'tick', 1.0)
            st.add(PR.streifen(XB[1] + 3, bx - 3, Z0, Z1, top, 8 * (1 - weg), texte=[((XB[j] + XB[j + 1]) / 2, str(2023 + j)) for j in (1, 2, 3)]), shadow=False)
        if t >= T_FRIST - 0.05 and weg < 0.5:                              # Kauf-Nadel (weiß) fällt auf März 2023
            y = top + drop(t, T_FRIST - 0.05, 240, 0.25)
            st.add(PR.setze(PR.nadel(WHITE), x=XKAUF, z=ZP, y=y), a=0.30, blur=5)
        if t >= T_ERST and weg < 0.5:                                      # Frist-Nadel (Koralle) springt ans Jahresende
            kh = eio(pr(t, T_ERST, T_KAUFJ - T_ERST)); snd(T_KAUFJ, 'thud', 0.6)
            x = lerp(XKAUF, XB[1], kh); y = top + 96 * sin(pi * kh) + (8 if (t >= A5 and x > XB[1] - 3) else 0)
            st.add(PR.setze(PR.nadel(ACC_L), x=x, z=ZP, y=y), a=0.30, blur=5)
        kf = pr(t, T_SCHLUSS - 0.05, 0.30)
        if kf > 0 and weg < 0.5:                                           # „… ist Schluss“: Zielfahne am Ende von 2026
            snd(T_SCHLUSS - 0.05, 'thud', 1.0)
            st.add(PR.setze(PR.fahne(172 * eo3(kf), back(pr(t, T_SCHLUSS + 0.10, 0.34), 1.5)), x=XB[4] - 8, z=ZP, y=top + 8), a=0.20, blur=5)

    # --- Absatz 8: Merkregel aus drei Blöcken
    weg8 = sink(t, A9 - 0.15, 0.40, 'whoosh')
    if T_KJ8 - 0.2 < t < A9 + 0.4:
        for (x0, x1, hh, col, txt, tc, size, t0) in ((-336, -112, 56, OBJ_CREAM, 'KAUFJAHR', INK, 54, T_KJ8), (-66, 66, 70, ACC, '+ 3', WHITE, 84, T_DREI8),
                                                     (112, 336, 56, OBJ_CREAM, 'BIS 31.12.', INK, 50, T_BIS8)):
            h = hh * rise(t, t0 - 0.10) * (1 - weg8)
            if h > 0.5:
                st.add(PR.block(x0, x1, -10, 160, h, col, txt, tc, size), a=0.22, blur=7)

    # --- Absatz 9: Kommode, Schublade fährt heraus
    if A9 - 0.1 < t < A10 + 1.0:
        hoch = rise(t, A9 + 0.22, 0.45) * (1 - sink(t, A10 + 0.42, 0.42, 'whoosh'))
        auf = eio(pr(t, T_SCHUB - 0.18, 0.5)) * (1 - eio(pr(t, A10 + 0.12, 0.34))); snd(T_SCHUB - 0.18, 'swipe', 1.0)
        if hoch > 0.01:
            st.add(PR.setze(PR.schublade(auf, karten=2, hoch=hoch), x=-30, z=-40), a=0.24, blur=10)

    # --- der Gutschein (immer im Bild): „GÜLTIG: 1 JAHR“ wird in Absatz 7 durchgestrichen
    durch = pr(t, T_UNW - 0.22, 0.34) * (1 - pr(t, A10 + 0.25, 0.45))            # am Schluss wieder weg -> letztes Bild = erstes Bild
    if 0 < durch < 1:
        snd(T_UNW - 0.22, 'swipe', 1.0)
    card = xf(PR.karte(PR.gutschein_decal('GUTSCHEIN', '50 €', zeile='GÜLTIG: 1 JAHR', durch=durch)), R, pos)
    st.add(card, a=0.20, blur=16, ground=False)
    st.end()

    # --- flache Ebene
    ha = (1 - pr(t, A2 - 0.2, 0.2)) if t < 20 else pr(t, T - 0.5, 0.3)      # Titel steht ab Bild 0 (Cover) und wieder im letzten Bild (Loop)
    kicker(c, 'DEIN GUTSCHEIN VON', 84, 356, ha)
    headline(c, '2023', '', ha if t > 1 else 1.0, y=506, size=152)
    if ha > 0 and t < 20:                                                 # Strich unter der Zahl, genau wenn sie gesprochen wird
        c.drawLine(88, 522, 88 + 368 * eo3(pr(t, T_2023 - 0.02, 0.45)), 522, P(INK, ha, stroke=9)); snd(T_2023 - 0.02, 'swipe', 0.9)
    banner(c, 'NUR NOCH GUT 4 WOCHEN', 84, 538, pop(t, T_NUR - 0.10, sound='thud') * (1 - pr(t, A2 - 0.2, 0.2)), size=35)
    headline(c, '3', 'JAHRE', pop(t, T_DREI - 0.02, 0.30, 'thud') * (1 - pr(t, A6 - 0.2, 0.2)))
    if T_FRIST < t < A6 + 0.2:                                              # Etiketten am Zeitstrahl – immer nur eines
        ax, ay = st.pt(XKAUF, HB + 86, ZP); bx_, by_ = st.pt(XB[1], HB + 86 + (8 if t >= A5 else 0), ZP)
        label(c, ax, ay, 'KAUF', 10, -86, pop(t, T_FRIST + 0.22), a=1 - pr(t, T_ERST + 0.25, 0.2))
        label(c, bx_, by_, 'FRISTSTART', -10, -92, pop(t, T_KAUFJ + 0.02), fg=ACC, a=1 - pr(t, T_MAERZ - 0.25, 0.2))
        label(c, ax, ay, 'GEKAUFT 03/2023', 14, -86, pop(t, T_MAERZ), a=1 - pr(t, T_DANN + 0.25, 0.2))
        label(c, bx_, by_, 'START 31.12.2023', -10, -92, pop(t, T_SILV - 0.05), fg=ACC, a=1 - pr(t, A6 - 0.25, 0.2))
    banner(c, 'GÜLTIG BIS 31.12.2026', 84, 518, pop(t, T_SCHLUSS + 0.05) * (1 - pr(t, A6 - 0.2, 0.2)), size=33)
    banner(c, 'NOCH GUT 4 WOCHEN', 84, 598, pop(t, T_VIER - 0.06) * (1 - pr(t, A6 - 0.2, 0.2)), bg=INK, size=33)
    if T_EIN - 0.1 < t < T_UNW:
        zx, zy = st.pt(*(R @ np.array([30.0, 9.5, 86.0]) + pos))            # die Zeile „GÜLTIG: 1 JAHR“ auf der Karte
        label(c, zx, zy, 'NUR 1 JAHR?', 96, 156, pop(t, T_EIN), a=1 - pr(t, T_UNW - 0.35, 0.2), size=34)
    stamp(c, 'OFT UNWIRKSAM', 540, 596, pop(t, T_UNW - 0.04, 0.30, 'thud') * (1 - pr(t, A8 - 0.25, 0.2)), size=78)
    headline(c, '3', 'JAHRE', pop(t, T_DREI7 - 0.04, 0.30, 'thud') * (1 - pr(t, A9 - 0.2, 0.2)))
    finish(c, t, SERIE)


if __name__ == '__main__':
    main(draw, SERIE, NAME)
