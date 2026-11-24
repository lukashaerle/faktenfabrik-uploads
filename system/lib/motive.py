"""MOTIVE – fertige Bildbausteine im Sticker-Stil für den FINN-Show-Look (25.11.2026).

    import motive as M
    M.button(c, 540, 700)                       Knopf (Pille) mit Beschriftung, press 0..1 = gedrückt
    M.cursor(c, x, y)  ·  M.ring(c, x, y, u)    Mauszeiger  ·  Klick-Ring (u = Sekunden seit dem Klick)
    M.stamp(c, x, y, 'ABGELEHNT')               Stempel-Kasten (rot, schräg) – mit K.show(kind='slam') auf das Wort setzen
    M.field(c, x, y)                            Eingabefeld mit blinkender Schreibmarke und €
    M.calendar(c, x, y, s, '20', 'NOVEMBER')    Kalenderblatt (sq = Stauchung der Zahl zum Umblättern, col = Farbe der Zahl)
    M.paper(c, x, y, title='KREDITRECHT')       Gesetzblatt mit §
    M.burst(c, x, y, r, fill, 'NEU')            Zacken-Stern mit Wort
    M.wallet(c, x, y, s)  ·  M.magnifier(c, x, y)  ·  M.bag(c, x, y, s)   Geldbeutel · Lupe · Einkaufstüte mit €
    M.gauge(c, x, y, r, v)                      Anzeige rot–gelb–grün, Zeiger bei v (0..1)
    M.tile(c, x, y, r, fill, 'plus'|'minus'|'raten')   runde Kachel mit Zeichen
    M.slots(c, 'DER CHECK')                     Karte mit drei leeren Feldern (Mitten: M.SLOT_X, y = M.SLOT_Y, Radius M.SLOT_R)
    M.shop(c, x, y, s)  ·  M.invoice(c, x, y, s)  ·  M.check(c, x, y, s)   Laden · Rechnung · grüner Haken
    M.tag(c, x, y, w, h, fill, 'BLACK FRIDAY')  Preisschild
    M.plane(c, x, y, s)                         Papierflieger (für „Schick das …“)
    M.chat(c, lt, t1, t2, t3, reply='WAS?!')    Handy mit Chat: Video verschickt -> Antwort tippt -> Antwort ploppt auf
    M.pump(c, x, y, s, '1,89')  ·  M.clock(c, x, y, r, hh, mm)  ·  M.sign(...)  ·  M.station(...)   Zapfsäule · Uhr · Preistafel · Mini-Tankstelle

Regeln: keine Logos, keine Markenfiguren. Markennamen nur als schlichte Schrift (z. B. C.chip(c, 'PAYPAL', …)), wenn der Fakt sie braucht.
Neue Motive hier ergänzen (gleicher Stil: C.box / C.circle / C.path mit dunklem Umriss und versetztem Schatten), nicht in episode.py.
"""
import math
import render as L
import cartoon as C
import kino as K
from render import skia, P, clamp, ease_out, mixc
from cartoon import INK, VIO, VIO_L, YEL, YEL_D, RED, GREEN, WHITE, CREAM, GREY

SLOT_X, SLOT_Y, SLOT_R = (262, 540, 818), 560, 118


def button(c, x, y, w=760, h=150, label='Später bezahlen', fill=WHITE, txt=INK, press=0.0):
    s = 1 - 0.06 * press
    c.save(); c.translate(x, y); c.scale(s, s)
    C.box(c, -w / 2, -h / 2, w, h, fill, r=h / 2, shadow=14 * (1 - press))
    C.text(c, label, 0, h * 0.17, h * 0.46, txt, maxw=w - 90)
    c.restore()


def cursor(c, x, y, s=1.0):
    p = skia.Path(); p.moveTo(0, 0); p.lineTo(0, 96); p.lineTo(26, 74); p.lineTo(46, 118); p.lineTo(66, 108); p.lineTo(46, 66); p.lineTo(78, 66); p.close()
    c.save(); c.translate(x, y); c.scale(s, s); C.path(c, p, WHITE, out=9, shadow=9); c.restore()


def ring(c, x, y, u, col=INK):
    """Klick-Ring: breitet sich in 0,45 s aus und verblasst."""
    if 0 <= u < 0.45:
        c.drawCircle(x, y, 40 + 260 * u, P(col, int(255 * (1 - u / 0.45)), stroke=12))


def stamp(c, x, y, text, size=120, color=RED, rot=-9):
    f, size = C.fit(text, size, 800); w = f.measureText(text)
    c.save(); c.translate(x, y); c.rotate(rot)
    r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-w / 2 - 36, -size * 0.72, w + 72, size * 1.3), 22, 22)
    c.drawRRect(r, P(WHITE, 240)); c.drawRRect(r, P(color, stroke=14))
    c.drawString(text, -w / 2, size * 0.3, f, P(color))
    c.restore()


def field(c, x, y, w=640, h=120):
    """Eingabefeld mit blinkender Schreibmarke."""
    C.box(c, x - w / 2, y - h / 2, w, h, WHITE, r=28)
    if int(L.NOW * 3) % 2 == 0:
        c.drawRect(skia.Rect.MakeXYWH(x - w / 2 + 44, y - 36, 10, 72), P(INK))
    for k in range(4):
        c.drawCircle(x - w / 2 + 110 + k * 62, y + 2, 13, P(GREY))
    C.text(c, '€', x + w / 2 - 74, y + 30, 84, INK)


def calendar(c, x, y, s, day, mon, sq=1.0, col=INK):
    """Kalenderblatt. sq = Stauchung der Zahl (0..1) für das Umblättern."""
    c.save(); c.translate(x, y); c.scale(s, s)
    C.box(c, -200, -200, 400, 420, WHITE, r=40)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-200, -200, 400, 120), 40, 40), P(RED))
    c.drawRect(skia.Rect.MakeXYWH(-200, -120, 400, 40), P(RED))
    c.drawLine(-200, -80, 200, -80, P(INK, stroke=10))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-200, -200, 400, 420), 40, 40), P(INK, stroke=10))
    C.text(c, mon, 0, -118, 64, WHITE, maxw=340)
    c.save(); c.translate(0, 62); c.scale(1, max(sq, 0.04)); c.translate(0, -62)
    C.text(c, day, 0, 140, 220, col)
    c.restore()
    for sx in (-1, 1):
        C.box(c, sx * 110 - 16, -236, 32, 76, GREY, r=16, out=7, shadow=0)
    c.restore()


def paper(c, x, y, w=520, h=560, title='KREDITRECHT'):
    """Gesetzblatt mit Paragrafen-Zeichen."""
    C.box(c, x - w / 2, y - h / 2, w, h, WHITE, r=30)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - w / 2 + 5, y - h / 2 + 5, w - 10, 100), 26, 26), P(VIO))
    c.drawRect(skia.Rect.MakeXYWH(x - w / 2 + 5, y - h / 2 + 60, w - 10, 46), P(VIO))
    C.text(c, title, x, y - h / 2 + 80, 56, WHITE, maxw=w - 60)
    C.text(c, '§', x - 105, y + 180, 320, INK)
    for k in range(4):
        c.drawLine(x + 45, y - 80 + k * 66, x + 205 - (60 if k == 3 else 0), y - 80 + k * 66, P(GREY, stroke=17))


def burst(c, x, y, r, fill, text, txt=INK, n=12):
    p = skia.Path()
    for k in range(n * 2):
        a = k * math.pi / n + L.NOW * 0.7; rr = r if k % 2 == 0 else r * 0.78
        (p.moveTo if k == 0 else p.lineTo)(x + rr * math.cos(a), y + rr * math.sin(a))
    p.close(); C.path(c, p, fill, out=9, shadow=10)
    C.text(c, text, x, y + r * 0.2, r * 0.56, txt, maxw=r * 1.4)


def wallet(c, x, y, s=1.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    for k, colr in enumerate((GREEN, '#7ee0b8')):
        C.box(c, -150 + k * 44, -160 - k * 30, 250, 140, colr, r=14, out=8, shadow=0)
    C.box(c, -200, -90, 400, 240, '#b9743f', r=36)
    C.box(c, 90, -8, 150, 84, '#8f5429', r=30, out=8, shadow=0)
    c.drawCircle(128, 34, 14, P(YEL)); c.drawCircle(128, 34, 14, P(INK, stroke=6))
    c.restore()


def magnifier(c, x, y, r=120):
    c.drawLine(x + r * 0.7, y + r * 0.7, x + r * 1.8, y + r * 1.8, P(INK, stroke=48))
    c.drawLine(x + r * 0.7, y + r * 0.7, x + r * 1.8, y + r * 1.8, P(YEL_D, stroke=28))
    C.circle(c, x, y, r, '#e3f2ff', out=14, shadow=10)
    c.drawArc(skia.Rect.MakeXYWH(x - r * 0.62, y - r * 0.62, r * 1.24, r * 1.24), 200, 60, False, P(WHITE, 235, stroke=12))


def gauge(c, x, y, r, v):
    """Prüf-Anzeige rot–gelb–grün, Zeiger bei v (0 = rot … 1 = grün)."""
    rect = skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r)
    c.drawArc(rect, 180, 180, False, P(INK, stroke=78, cap=False))
    for k, colr in enumerate((RED, YEL, GREEN)):
        c.drawArc(rect, 181.5 + k * 60, 57, False, P(colr, stroke=56, cap=False))
    a = math.radians(180 + 180 * clamp(v))
    c.drawLine(x, y, x + (r - 24) * math.cos(a), y + (r - 24) * math.sin(a), P(INK, stroke=24))
    C.circle(c, x, y, 36, WHITE, out=10, shadow=0)


def bag(c, x, y, s=1.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    c.drawArc(skia.Rect.MakeXYWH(-80, -235, 160, 170), 180, 180, False, P(INK, stroke=24))
    C.box(c, -165, -150, 330, 340, YEL, r=26)
    C.circle(c, 0, 20, 70, WHITE, out=8, shadow=0); C.text(c, '€', 0, 56, 100, INK)
    c.restore()


def tile(c, x, y, r, fill, kind):
    """Runde Kachel: 'plus' = Einkommen, 'minus' = Ausgaben, 'raten' = offene Raten (drei Balken, einer bezahlt)."""
    C.circle(c, x, y, r, fill)
    c.save(); c.translate(x, y); c.scale(r / 148, r / 148)
    if kind == 'raten':
        for k in range(3):
            C.box(c, -84 + k * 60, -52, 46, 104, INK if k == 0 else WHITE, r=12, out=8, shadow=0)
    else:
        c.drawRoundRect(skia.Rect.MakeXYWH(-96, -13, 70, 26), 9, 9, P(WHITE))
        if kind == 'plus':
            c.drawRoundRect(skia.Rect.MakeXYWH(-74, -35, 26, 70), 9, 9, P(WHITE))
        C.text(c, '€', 38, 40, 116, WHITE)
    c.restore()


def slots(c, title='DER CHECK'):
    """Karte mit drei leeren Feldern (füllen sich nacheinander, z. B. mit M.tile) und Reiter-Etikett."""
    C.box(c, 96, 330, 888, 430, WHITE, r=54)
    for x in SLOT_X:
        c.drawCircle(x, SLOT_Y, SLOT_R, P(CREAM)); c.drawCircle(x, SLOT_Y, SLOT_R, P(GREY, stroke=9))
    C.chip(c, title, 540, 338, 62, VIO, WHITE, angle=-2)


def shop(c, x, y, s=1.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    C.box(c, -190, -110, 380, 300, WHITE, r=20)
    for k in range(5):
        C.box(c, -200 + k * 80, -190, 80, 100, RED if k % 2 == 0 else WHITE, r=14, out=8, shadow=0)
    C.box(c, -150, -40, 130, 150, '#bfe6ff', r=12, out=8, shadow=0)
    C.box(c, 30, -40, 110, 230, VIO, r=12, out=8, shadow=0)
    c.drawCircle(120, 80, 9, P(YEL))
    c.restore()


def invoice(c, x, y, s=1.0, title='RECHNUNG'):
    c.save(); c.translate(x, y); c.scale(s, s)
    C.box(c, -150, -190, 300, 380, WHITE, r=22)
    C.text(c, title, 0, -118, 44, INK, maxw=260)
    for k in range(4):
        c.drawLine(-110, -56 + k * 50, 110 - (50 if k == 3 else 0), -56 + k * 50, P(GREY, stroke=15))
    c.restore()


def check(c, x, y, s=1.0, color=GREEN):
    c.save(); c.translate(x, y); c.scale(s, s)
    C.circle(c, 0, 0, 70, color)
    p = skia.Path(); p.moveTo(-32, 2); p.lineTo(-8, 28); p.lineTo(36, -24)
    c.drawPath(p, P(INK, stroke=24)); c.drawPath(p, P(WHITE, stroke=13))
    c.restore()


def tag(c, x, y, w, h, fill, text, txt=WHITE, rot=-6, size=100):
    """Preisschild (z. B. „BLACK FRIDAY“)."""
    c.save(); c.translate(x, y); c.rotate(rot)
    p = skia.Path(); p.moveTo(-w / 2, 0); p.lineTo(-w / 2 + h * 0.45, -h / 2); p.lineTo(w / 2, -h / 2); p.lineTo(w / 2, h / 2); p.lineTo(-w / 2 + h * 0.45, h / 2); p.close()
    C.path(c, p, fill)
    c.drawCircle(-w / 2 + h * 0.4, 0, h * 0.09, P(CREAM)); c.drawCircle(-w / 2 + h * 0.4, 0, h * 0.09, P(INK, stroke=7))
    C.text(c, text, h * 0.24, size * 0.36, size, txt, maxw=w - h * 0.85)
    c.restore()


def plane(c, x, y, s, a=255):
    p = skia.Path(); p.moveTo(-90, 10); p.lineTo(110, -60); p.lineTo(20, 70); p.lineTo(0, 20); p.close()
    c.save(); c.translate(x, y); c.scale(s, s); C.path(c, p, WHITE, out=8, shadow=8, a=a); c.restore()


def chat(c, lt, t1, t2, t3, reply='WAS?!'):
    """Handy mit Chat: (1) das Video wird verschickt (violette Blase mit Mini-Bild), (2) die Antwort tippt (drei Punkte),
    (3) die Antwort (reply, höchstens ca. 6 Zeichen) ploppt auf. t1..t3 = Zeiten ab dem letzten Schnitt."""
    C.box(c, 300, 236, 480, 560, WHITE, r=66)                                   # Gehäuse
    C.box(c, 326, 290, 428, 456, VIO_L, r=34, out=7, shadow=0)                  # Display
    c.drawRoundRect(skia.Rect.MakeXYWH(480, 256, 120, 16), 8, 8, P(INK))

    def sent(cc):
        C.box(cc, 496, 312, 236, 190, VIO, r=34, out=7, shadow=7)
        C.box(cc, 520, 334, 188, 146, YEL, r=20, out=6, shadow=0)
        p = skia.Path(); p.moveTo(594, 377); p.lineTo(646, 407); p.lineTo(594, 437); p.close()
        cc.drawPath(p, P(WHITE)); cc.drawPath(p, P(INK, stroke=7))
    K.show(c, lt, t1, 614, 407, sent, kind='pop', key='gesendet')
    if t2 <= lt < t3:                                                           # „… schreibt“
        k = min(1.0, K.pop(lt - t2))
        c.save(); c.translate(424, 584); c.scale(max(k, 0.01), max(k, 0.01)); c.translate(-424, -584)
        C.box(c, 346, 540, 156, 88, WHITE, r=42, out=7, shadow=7)
        for n in range(3):
            c.drawCircle(388 + n * 36, 584 + 7 * math.sin(L.NOW * 11 - n * 0.9), 12, P(INK))
        c.restore()

    def answer(cc):
        C.box(cc, 346, 528, 300, 122, WHITE, r=46, out=7, shadow=7)
        C.text(cc, reply, 496, 616, 78, INK, maxw=272)
    K.show(c, lt, t3, 496, 589, answer, kind='pop', key='antwort')


# ---------------------------------------------------------------- Auto / Tanken (aus dem Video „Tanken“ vom 24.11.)
def pump(c, x, y, s, price='1,89', jump=0.0, hand=True, label='DIESEL'):
    """Zapfsäule mit Preisanzeige. jump 0..1 = Anzeige springt (rot) nach oben."""
    c.save(); c.translate(x, y); c.scale(s, s)
    C.box(c, -170, -330, 340, 640, YEL, r=40)                      # Gehäuse
    C.box(c, -130, -280, 260, 170, INK, r=24, shadow=0, out=0)     # Display
    col = mixc(GREEN, RED, clamp(jump))
    f, sz = C.fit(price, 104, 230)
    dy = -14 * math.sin(clamp(jump) * math.pi)
    c.drawString(price, -f.measureText(price) / 2, -158 + dy, f, P(col))
    C.box(c, -110, -60, 220, 70, WHITE, r=18, out=7, shadow=0)
    C.text(c, label, 0, -10, 40, INK)
    C.box(c, -200, 290, 400, 60, GREY, r=20, shadow=8)            # Sockel
    if hand:                                                       # Zapfhahn-Schlauch
        p = skia.Path(); p.moveTo(170, 60); p.cubicTo(300, 80, 290, 250, 210, 260)
        c.drawPath(p, P(INK, stroke=34)); c.drawPath(p, P('#3a3060', stroke=20))
        C.box(c, 150, -10, 80, 120, INK, r=18, shadow=0, out=0)
    c.restore()


def clock(c, x, y, r, hh, mm, ring=0.0, face=WHITE):
    """Wanduhr / Wecker; ring > 0 = wackelt (klingelt)."""
    wob = math.sin(L.NOW * 40) * 4 * ring
    c.save(); c.translate(x, y); c.rotate(wob)
    for sx in (-1, 1):
        C.circle(c, sx * r * 0.62, -r * 0.92, r * 0.2, RED, out=8, shadow=8)
    C.circle(c, 0, 0, r, face)
    for i in range(12):
        a = math.radians(i * 30)
        l = 26 if i % 3 == 0 else 14
        c.drawLine((r - 24) * math.sin(a), -(r - 24) * math.cos(a), (r - 24 - l) * math.sin(a), -(r - 24 - l) * math.cos(a), P(INK, stroke=9 if i % 3 == 0 else 6))
    am = math.radians(mm * 6); ah = math.radians((hh % 12) * 30 + mm * 0.5)
    c.drawLine(0, 0, r * 0.48 * math.sin(ah), -r * 0.48 * math.cos(ah), P(INK, stroke=18))
    c.drawLine(0, 0, r * 0.72 * math.sin(am), -r * 0.72 * math.cos(am), P(VIO, stroke=12))
    C.circle(c, 0, 0, 16, YEL, out=6, shadow=0)
    c.restore()


def sign(c, x, y, w, h, label, value, col=INK, fill=WHITE):
    """Preis-Schild / Tafel mit Überschrift und großem Wert."""
    C.box(c, x - w / 2, y - h / 2, w, h, fill, r=30)
    C.text(c, label, x, y - h / 2 + 64, 46, INK)
    C.text(c, value, x, y + h / 2 - 40, 120, col, maxw=w - 40)


def station(c, x, y, s, k=1.0):
    """Mini-Tankstelle (Dach + Säule), z. B. viele davon für eine Zählung."""
    if k <= 0:
        return
    sc = s * (0.6 + 0.4 * ease_out(clamp(k)))
    c.save(); c.translate(x, y); c.scale(sc, sc)
    C.box(c, -60, -70, 120, 30, RED, r=10, out=6, shadow=5)
    c.drawRect(skia.Rect.MakeXYWH(-48, -40, 12, 70), P(INK))
    c.drawRect(skia.Rect.MakeXYWH(36, -40, 12, 70), P(INK))
    C.box(c, -22, -20, 44, 60, YEL, r=8, out=6, shadow=0)
    c.restore()
