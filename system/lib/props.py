"""FAKTENFABRIK – Look „STUDIO“: Objekte (Props) für die 3D-Bühne.

Jede Funktion gibt eine Liste von Flächen zurück, gebaut um den Ursprung (0, 0, 0), stehend auf y = 0.
Hinstellen:   st.add(PR.setze(PR.eimer(), x=-120, z=40))
Eigene Objekte: aus box(), prism(), frustum(), sphere() bauen (siehe studio.py) – Vorbild sind die Funktionen hier.

Aufkleber (Schrift/Zeichnung auf einer Fläche) = decal: (Ursprung, U, V, zeichenfunktion). Die Zeichenfunktion bekommt
ein Canvas, auf dem 1 Einheit = 1 Welt-Einheit ist; (0, 0) ist die linke obere Ecke der Fläche.
    oben(x0, z0, y, fn)     Oberseite: u nach rechts (+x), v nach vorn (+z)
    vorn(x0, y1, z, fn)     Vorderseite (+z): u nach rechts, v nach unten
    seite(x, y1, z1, fn)    rechte Seite (+x): u nach hinten, v nach unten
"""
from math import sin, cos, pi, radians

import numpy as np
import skia

from studio import (ACC, ACC_D, ACC_L, GOLD, GOLD_D, INK, MUTE, OBJ, OBJ_CREAM, OBJ_DARK, OBJ_GREY, OBJ_GREY_D, PETROL, PETROL_D, WHITE,
                    C, P, box, circle, clamp, face, font, frustum, lerp, lin, prism, relayer, rot, rrect, rrpoly, sphere, text, tw, xf)


def oben(x0, z0, y, fn):
    return (np.array([x0, y + 0.3, z0], float), np.array([1.0, 0, 0]), np.array([0, 0, 1.0]), fn)


def vorn(x0, y1, z, fn):
    return (np.array([x0, y1, z + 0.3], float), np.array([1.0, 0, 0]), np.array([0, -1.0, 0]), fn)


def seite(x, y1, z1, fn):
    return (np.array([x + 0.3, y1, z1], float), np.array([0, 0, -1.0]), np.array([0, -1.0, 0]), fn)


def setze(F, x=0.0, z=0.0, y=0.0, ry=0.0, rx=0.0, rz=0.0, scale=1.0):
    """Objekt verschieben und drehen (Grad). ry = um die Hochachse, rx = zum Betrachter kippen."""
    R = rot(rx, ry, rz, scale) if (rx or ry or rz or scale != 1.0) else None
    return xf(F, R, (x, y, z))


# ---------------------------------------------------------------- Karte / Gutschein
KW, KD = 372, 236


def gutschein_decal(titel='GUTSCHEIN', betrag='50 €', zeile=None, durch=0.0, band=ACC):
    """Aufdruck für karte(): Geschenkband + Schleife, Titel, Betrag. zeile = kleine Zeile unten (z. B. 'GÜLTIG: 1 JAHR'), durch 0..1 streicht sie durch."""
    def fn(c):
        c.drawRect(skia.Rect.MakeWH(KW, KD), lin(0, 0, KW, KD, [C(WHITE, 0.0), C('#5C6F7A', 0.10)]))
        c.drawRect(skia.Rect.MakeXYWH(46, 0, 40, KD), P(band)); c.drawRect(skia.Rect.MakeXYWH(46, 0, 7, KD), P('#000000', 0.10))
        for sx in (-1, 1):
            c.save(); c.translate(66, 112 if not zeile else 96); c.scale(sx, 1)
            pth = skia.Path(); pth.moveTo(0, 0); pth.cubicTo(18, -34, 62, -40, 58, -6); pth.cubicTo(56, 14, 22, 10, 0, 0); pth.close()
            c.drawPath(pth, P(ACC_D)); c.restore()
        rrect(c, 52, 98 if not zeile else 82, 28, 28, 7, P('#A82E14'))
        if zeile:
            text(c, titel, 132, 62, font('black', 31), P(INK), 'l', 2.5)
            text(c, betrag, 128, 150, font('black', 92), P(INK), 'l', -2)
            f = font('mono', 25); wz = tw(zeile, f, 1.5)
            rrect(c, 124, 172, wz + 24, 44, 8, P('#EEF1F3')); text(c, zeile, 136, 203, f, P(INK), 'l', 1.5)
            if durch > 0:
                c.drawLine(118, 194, 118 + (wz + 36) * clamp(durch), 194, P(ACC, 1.0, stroke=9))
        else:
            text(c, titel, 132, 84, font('black', 35), P(INK), 'l', 2.5)
            text(c, betrag, 128, 190, font('black', 106), P(INK), 'l', -2)
    return fn


def karte(decal=None, w=KW, d=KD, th=9, col=OBJ, r=20, layer=6):
    """Flache Karte (Gutschein, Ticket, Preisschild …), liegend um den Ursprung. decal = Zeichenfunktion für die Oberseite (w × d Einheiten)."""
    dec = oben(-w / 2, -d / 2, th, decal) if decal else None
    return prism(rrpoly(w, d, r), 0, th, col, layer=layer, decal=dec)


# ---------------------------------------------------------------- Mülleimer mit Klappdeckel
BH, BR0, BR1, BRL = 236, 100, 126, 136


def eimer(d=0.0, offen=0.0, col=OBJ_GREY, col_rille=OBJ_GREY_D):
    """Mülleimer. d = wie weit er in die Plattform gefahren ist (0 … BH + 30), offen = Deckelwinkel in Grad (0 zu, 92 ganz auf)."""
    top = BH - d; F = []
    F += frustum(0, 0, BR0, BR1, -d, top, col, 56, layer=2, alt=(4, col_rille), clip=True)
    F += frustum(0, 0, BR1 + 6, BR1 + 6, top - 18, top, '#F1F3F5', 56, layer=3, clip=True)
    if top > 1:
        r = BR1 - 8
        def inner(c):
            c.drawRect(skia.Rect.MakeWH(2 * r, 2 * r), lin(0, 0, 0, 2 * r, [C('#35424A'), C('#141C20'), C('#0B1013')], [0, 0.55, 1]))
        F += prism(circle(0, 0, r, 56), top + 0.3, top + 0.4, '#10181C', layer=4, sides=False, flat=True, decal=oben(-r, -r, top + 0.2, inner))
    if offen <= 0.01:
        F += frustum(0, 0, BRL, BRL, top, top + 12, '#E3E7EB', 56, layer=5, clip=True)
        F += frustum(0, 0, BRL - 22, BRL - 40, top + 12, top + 22, '#E3E7EB', 56, layer=5, top_col='#F6F8F9', clip=True)
    else:
        def under(c):
            c.drawCircle(BRL, BRL, BRL - 15, P('#C3CAD1')); c.drawCircle(BRL, BRL, BRL - 15, P('#9AA4AD', 0.6, stroke=3)); c.drawCircle(BRL, BRL, BRL - 52, P('#D2D8DD'))
        lid = frustum(0, BRL, BRL, BRL, 0, 12, '#E3E7EB', 56, layer=5, bottom='#DCE1E5') + frustum(0, BRL, BRL - 22, BRL - 40, 12, 22, '#E3E7EB', 56, layer=5, top_col='#F6F8F9')
        for fc in lid:
            if fc['n'][1] < -0.5:
                fc['decal'] = (np.array([-BRL, -0.3, 0.0]), np.array([1.0, 0, 0]), np.array([0, 0, 1.0]), under)
        from studio import Rx
        F += xf(lid, Rx(radians(-offen)), (0, top, -BRL))
    return F


EIMER_DECKEL_Y = BH + 22        # Höhe, auf der etwas auf dem geschlossenen Deckel liegt


# ---------------------------------------------------------------- Blöcke, Balken, Zeitstrahl
def block(x0, x1, z0, z1, h, col=OBJ_CREAM, txt=None, txt_col=INK, size=66, schrift='cond', layer=2, y0=0.0):
    """Quader mit optionaler Schrift auf der Oberseite (Jahresblock, Balken, Sockel). h = Höhe (wächst mit rise())."""
    h = max(1.0, h); dec = None
    if txt:
        w, d = x1 - x0, z1 - z0
        def fn(c):
            text(c, txt, w / 2, d / 2 + size * 0.36, font(schrift, size), P(txt_col, 0.92 if txt_col == INK else 1.0), 'c', 1.5)
        dec = oben(x0, z0, y0 + h, fn)
    return box(x0, x1, z0, z1, y0, y0 + h, col, layer=layer, decal=dec)


def streifen(x0, x1, z0, z1, y, dicke=8, col=ACC, texte=(), txt_col=WHITE, size=66):
    """Farbiger Streifen, der über Blöcke wächst. texte = [(x_mitte, 'text'), …] in Welt-x."""
    def fn(c):
        for xm, s in texte:
            text(c, s, xm - x0, (z1 - z0) / 2 + size * 0.36, font('cond', size), P(txt_col), 'c', 1.5)
    return box(x0, max(x0 + 2, x1), z0, z1, y, y + dicke, col, layer=3, decal=oben(x0, z0, y + dicke, fn))


def nadel(col=WHITE, h=64, r=23):
    """Markier-Nadel: Kugel auf dünnem Stab (steht mit dem Stabfuß auf y = 0)."""
    return relayer(frustum(0, 0, 3.2, 3.2, 0, h, '#C9D0D6', 10), 7) + relayer(sphere(0, h + r * 0.7, 0, r, col, 18, 9), 7)


def fahne(h=172, k=1.0, col='#F25A3F'):
    """Zielfahne: Stab der Höhe h, Wimpel klappt mit k 0..1 aus (zeigt nach links)."""
    F = frustum(0, 0, 5.5, 5.5, 0, h, OBJ_CREAM, 14, layer=5)
    if k > 0 and h > 90:
        F.append(face([[0, h - 4, 0], [0, h - 84, 0], [-150 * k, h - 44, 0]], [0, 0, 1.0], col, 5, None, True))
    return F


# ---------------------------------------------------------------- Tischkalender, Tafel, Paket, Münzen
def kalender(tag='31', monat='DEZ', w=190, h=210, d=54, col=OBJ, k=1.0):
    """Abreißkalender-Block, steht aufrecht und zeigt nach vorn: farbiger Kopf mit Monat, große Tageszahl.
    k 0..1 = wie weit er aus der Plattform gefahren ist (mit rise()/sink())."""
    hh = max(1.0, h * clamp(k, 0, 1.3))
    def fn(c):
        c.drawRect(skia.Rect.MakeWH(w, 62), P(ACC))
        for x in (w * 0.28, w * 0.72):
            c.drawCircle(x, 20, 8, P('#7A1E0C'))
        text(c, monat, w / 2, 52, font('cond', 40), P(WHITE), 'c', 3)
        text(c, tag, w / 2, h - 34, font('black', 118), P(INK), 'c', -2)
    F = box(-w / 2, w / 2, -d / 2, d / 2, 0, hh, col, layer=2)
    for fc in F:
        if fc['n'][2] > 0.9:
            fc['decal'] = vorn(-w / 2, hh, d / 2, fn)
    return F


def tafel(fn, w=420, h=300, d=18, fuss=46, col=OBJ, rahmen=OBJ_DARK):
    """Stehende Tafel, zeigt nach vorn. fn(c) zeichnet flach auf w × h Einheiten – für Tests, Diagramme, alles Flache."""
    F = box(-w / 2 - 10, w / 2 + 10, -d / 2, d / 2, fuss - 10, fuss + h + 10, rahmen, layer=2)
    F += box(-w / 2, w / 2, d / 2, d / 2 + 2, fuss, fuss + h, col, layer=3)
    for fc in F:
        if fc['layer'] == 3 and fc['n'][2] > 0.9:
            fc['decal'] = vorn(-w / 2, fuss + h, d / 2 + 2, fn)
    for sx in (-1, 1):
        F += box(sx * w * 0.32 - 9, sx * w * 0.32 + 9, -30, 30, 0, fuss - 10, rahmen, layer=2)
    return F


def paket(w=200, d=160, h=140, col='#D9B98A', label=None):
    """Karton/Packung. label = Zeichenfunktion für die Vorderseite (w × h)."""
    F = box(-w / 2, w / 2, -d / 2, d / 2, 0, h, col, layer=2)
    for fc in F:
        if label and fc['n'][2] > 0.9:
            fc['decal'] = vorn(-w / 2, h, d / 2, label)
        if fc['n'][1] > 0.9:
            fc['decal'] = oben(-w / 2, -d / 2, h, lambda c: c.drawRect(skia.Rect.MakeXYWH(w / 2 - 12, 0, 24, d), P('#B8935E', 0.8)))
    return F


def muenzen(n=5, r=46, dicke=13, col=GOLD, rand=GOLD_D):
    """Münzstapel aus n Münzen."""
    F = []
    for i in range(n):
        def top(c, r=r):
            c.drawCircle(r, r, r - 9, P(rand, 0.55, stroke=4))
        F += frustum(0, 0, r, r, i * dicke, (i + 1) * dicke - 2, rand, 28, layer=2, top_col=col)
        F[-1]['decal'] = oben(-r, -r, (i + 1) * dicke - 2, top)
    return F


# ---------------------------------------------------------------- Kommode mit Schublade
def schublade(k=1.0, karten=3, w=330, d=210, h=170, hoch=1.0):
    """Kleine Kommode; die Schublade fährt mit k 0..1 nach vorn heraus, darin liegen Gutscheine.
    hoch 0..1 = wie weit die Kommode aus der Plattform gefahren ist (mit rise()/sink())."""
    h0 = h; h = max(1.0, h0 * clamp(hoch, 0, 1.2)); out = 168 * clamp(k) if hoch >= 0.98 else 0.0; z1 = d / 2
    def slot(c):
        rrect(c, 22, 30, w - 44, h0 - 64, 8, P('#0D1E22'))
    F = box(-w / 2, w / 2, -d / 2, d / 2, 0, h, OBJ_GREY, layer=2)
    for fc in F:
        if fc['n'][2] > 0.9:
            fc['decal'] = vorn(-w / 2, h, z1, slot)
    x0, x1, y0, y1 = -w / 2 + 24, w / 2 - 24, 36, h0 - 36
    if hoch >= 0.98:
        D = []
        if out > 2:
            D += box(x0, x1, z1, z1 + out, y0, y0 + 8, '#C7CED5', layer=3)                                 # Boden
            D += box(x0, x0 + 9, z1, z1 + out, y0, y1 - 12, '#E9EDF0', layer=3) + box(x1 - 9, x1, z1, z1 + out, y0, y1 - 12, '#E9EDF0', layer=3)
            for i in range(karten):                                                                       # Gutscheine in der Schublade
                cw, cd = 150, 95; zc = z1 + out * (0.30 + 0.22 * i) - 10
                if zc < z1 + out - 30:
                    def mini(c, cw=cw, cd=cd):
                        c.drawRect(skia.Rect.MakeXYWH(18, 0, 16, cd), P(ACC)); text(c, '€', cw * 0.62, cd * 0.72, font('black', 58), P(INK), 'c')
                    kf = prism(rrpoly(cw, cd, 9), 0, 5, WHITE, layer=4, decal=oben(-cw / 2, -cd / 2, 5, mini))
                    D += xf(kf, rot(rx=34, ry=(-14, 9, -5)[i % 3]), ((-52, 30, 64)[i % 3] * 0.9, y0 + 34 + 5 * i, zc))
        D += box(x0 - 10, x1 + 10, z1 + out, z1 + out + 14, y0 - 12, y1, '#F4F6F7', layer=5)             # Blende (zu = bündig vor dem Fach)
        D += frustum(0, z1 + out + 22, 13, 13, (y0 + y1) / 2 - 5, (y0 + y1) / 2 + 8, PETROL, 16, layer=6)
        F += D
    return F
