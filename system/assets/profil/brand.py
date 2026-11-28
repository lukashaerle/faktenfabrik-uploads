"""FAKTENFABRIK – Profilbild und YouTube-Banner im Look „STUDIO“ (ohne Maskottchen).

    python3 brand.py        -> profilbild_studio.png (1080×1080), profilbild_studio_rund.png (Vorschau im Kreis),
                               youtube_banner_studio.png (2560×1440, sicherer Bereich 1546×423 in der Mitte)
Zeichen: die kleine Fabrik (Sheddach + Schornstein) auf der Petrol-Bühne.
"""
import os
import sys
from math import radians

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'lib'))
import numpy as np      # noqa
import skia             # noqa
from studio import *    # noqa
import props as PR      # noqa

HERE = os.path.dirname(os.path.abspath(__file__))


def fabrik():
    """Kleine Fabrik um den Ursprung: Halle, Sheddach mit drei Zähnen, Schornstein."""
    w, d, h = 300, 190, 118
    def front(c):
        for i in range(3):
            rrect(c, 28 + i * 86, 30, 62, 46, 7, P(PETROL_D))
            c.drawRect(skia.Rect.MakeXYWH(28 + i * 86, 30, 62, 16), P('#000000', 0.18))
    def side(c):
        rrect(c, 60, 34, 70, 84, 6, P(PETROL_D))
    F = box(-w / 2, w / 2, -d / 2, d / 2, 0, h, OBJ_CREAM, layer=2)
    for fc in F:
        if fc['n'][2] > 0.9:
            fc['decal'] = PR.vorn(-w / 2, h, d / 2, front)
        if fc['n'][0] > 0.9:
            fc['decal'] = PR.seite(w / 2, h, d / 2, side)
    tw_, th_ = w / 3, 74
    for i in range(3):                                                    # Sheddach: drei Zähne, die schräge Fläche (Koralle) zeigt zum Betrachter
        x0, x1 = -w / 2 + i * tw_, -w / 2 + (i + 1) * tw_; z0, z1 = -d / 2, d / 2
        n_s = np.array([th_, tw_, 0.0]); n_s /= np.linalg.norm(n_s)
        F.append(face([[x0, h + th_, z0], [x1, h, z0], [x1, h, z1], [x0, h + th_, z1]], n_s, ACC, 3, None, True))
        F.append(face([[x0, h, z1], [x1, h, z1], [x0, h + th_, z1]], [0, 0, 1.0], OBJ_CREAM, 3))
    cx, cz = w / 2 - 56, -d / 2 + 46
    F += frustum(cx, cz, 30, 26, h, h + 190, OBJ_CREAM, 28, layer=4) + frustum(cx, cz, 29, 28, h + 150, h + 172, ACC, 28, layer=5)
    F += prism(circle(cx, cz, 19, 24), h + 190.2, h + 190.4, '#0D1E22', layer=6, sides=False, flat=True)
    L = np.array([-0.42, 0.80, 0.43])
    for (dx, dy, r) in ((-30, 238, 27), (-78, 268, 36)):                   # zwei Wölkchen (hell, weich schattiert)
        for fc in sphere(cx + dx, h + dy, cz - 6, r, '#FFFFFF', 32, 16):
            fc['flat'] = True; fc['layer'] = 7; fc['col'] = mix('#B4C6CC', '#FFFFFF', clamp(0.55 + 0.6 * float(np.dot(fc['n'], L)))); F.append(fc)
    return F


def szene(c, cx, cy, sc, yaw=30, pitch=32, r_plat=292, plat=PETROL, schatten=True):
    cam = Cam(radians(yaw), radians(pitch), sc, cx, cy)
    P_ = frustum(0, 0, r_plat, r_plat, -46, 0, plat, 72, layer=0) + frustum(0, 0, r_plat - 16, r_plat - 16, -74, -46, PETROL_D, 72, layer=-1)
    if schatten:
        sh = fpath(cam, [(x, -74, z) for x, z in circle(0, 0, r_plat - 6, 60)])
        c.save(); c.translate(0, 60 * sc); c.drawPath(sh, P('#061A1E', 0.35, blur=34 * sc)); c.restore()
    draw_faces(c, cam, P_)
    top = fpath(cam, [(x, 0, z) for x, z in circle(0, 0, r_plat, 72)])
    c.drawPath(top, P(PETROL_L, 0.55, stroke=2.5 * sc))
    F = fabrik()
    pts = np.vstack([f['p'] for f in F if f['layer'] < 7])[::3]
    P2 = [(float(p[0]), float(p[2])) for p in pts] + [(float(p[0]) + LX * max(0, p[1]), float(p[2]) + LZ * max(0, p[1])) for p in pts]
    c.save(); c.clipPath(top, True)
    from studio import _hull
    c.drawPath(fpath(cam, [(x, 0.4, z) for x, z in _hull(P2)]), P('#020F12', 0.36, blur=10 * sc)); c.restore()
    draw_faces(c, cam, F)


def profilbild(out, size=1080):
    s = skia.Surface(size, size); c = s.getCanvas(); k = size / 1080
    c.drawRect(skia.Rect.MakeWH(size, size), lin(0, 0, size, size, [C('#1F6470'), C('#134650'), C('#0C3038')], [0, 0.55, 1]))
    c.drawRect(skia.Rect.MakeWH(size, size), rad(size * 0.42, size * 0.36, size * 0.75, [C('#FFFFFF', 0.10), C('#FFFFFF', 0.0)]))
    szene(c, 548 * k, 772 * k, 1.86 * k, r_plat=250, plat='#2A7480')
    s.makeImageSnapshot().save(out, skia.kPNG); print('geschrieben:', out)
    return s.makeImageSnapshot()


def rund(img, out, d=1080):
    s = skia.Surface(d + 160, d + 160); c = s.getCanvas(); c.clear(C('#FFFFFF'))
    c.save(); p = skia.Path(); p.addCircle(d / 2 + 80, d / 2 + 80, d / 2); c.clipPath(p, True); c.drawImage(img, 80, 80); c.restore()
    for i, (dd, x) in enumerate(((110, 150), (64, 300), (40, 400))):          # so klein wie in den Apps
        y = d + 80 - dd / 2 - 20
        c.save(); q = skia.Path(); q.addCircle(x, y, dd / 2 + 4); c.drawPath(q, P('#FFFFFF')); q2 = skia.Path(); q2.addCircle(x, y, dd / 2); c.clipPath(q2, True)
        c.drawImageRect(img, skia.Rect.MakeXYWH(x - dd / 2, y - dd / 2, dd, dd), skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear)); c.restore()
    s.makeImageSnapshot().save(out, skia.kPNG); print('geschrieben:', out)


def banner_yt(out):
    BW, BH = 2560, 1440
    s = skia.Surface(BW, BH); c = s.getCanvas()
    c.drawRect(skia.Rect.MakeWH(BW, BH), P(PAPER)); c.drawRect(skia.Rect.MakeWH(BW, BH), rad(1280, 720, 1500, [C(WHITE, 0.7), C(WHITE, 0.0)]))
    for gy in range(40, BH, 80):
        for gx in range(40, BW, 80):
            c.drawCircle(gx, gy, 3, P(INK, 0.07))
    # sicherer Bereich: x 507–2053, y 508–931
    x0 = 548; f = font('black', 132)
    text(c, 'FAKTENFABRIK', x0, 664, f, P(INK), 'l', -2)
    w = f.measureText('FAKTENFABRIK') - 22
    c.drawLine(x0 + 4, 694, x0 + 4 + w, 694, P(ACC, 1.0, stroke=11, butt=True))
    text(c, 'Nützliches Wissen in 30 Sekunden.', x0 + 2, 776, font('bold', 56), P(INK), 'l')
    chip(c, 'TÄGLICH NEU', x0 + 2, 818, font('mono', 30), WHITE, ACC, padx=20, pady=14, r=10, track=4)
    text(c, '11:30 · 17:30 · 20:00', x0 + 296, 856, font('mono', 30), P(INK, 0.85), 'l', 3)
    szene(c, 1846, 800, 0.66, r_plat=292)
    s.makeImageSnapshot().save(out, skia.kPNG); print('geschrieben:', out)


if __name__ == '__main__':
    img = profilbild(os.path.join(HERE, 'profilbild_studio.png'))
    rund(img, os.path.join(HERE, 'profilbild_studio_rund.png'))
    banner_yt(os.path.join(HERE, 'youtube_banner_studio.png'))
