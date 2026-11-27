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
    M.car(c, x, y, s)  ·  M.shield(c, x, y, s)          Auto · Schutzschild mit Haken (Versicherung)
    M.lock(c, x, y, s)  ·  M.chain(c, y)                Vorhängeschloss · Kette quer durchs Bild („du hängst fest“)
    M.letter(c, x, y, s, rot)  ·  M.mailbox(c, x, y, s)  ·  M.office(c, x, y, s)   Brief · Briefkasten · Bürohaus (Versicherer, Amt, Firma)
    M.cross(c, x, y, s)  ·  M.arrow_up(c, x, y, s)      rotes Kreuz („reicht nicht“) · Pfeil nach oben („wird teurer“)
    M.arc_arrow(c, x0, y0, x1, y1, bend, k)            Bogenpfeil von A nach B, wächst mit k = 0..1
    M.doc(c, x, y, 'VERTRAG', hl=2, hl_text='STICHTAG') Dokument mit Kopfzeile; Zeile hl gelb markiert (mit Wort)
    M.pricecard(c, x, y, 'Prime-Abo', '89,90 €')       breite Karte: links Bezeichnung, rechts Preis in farbiger Pille
    M.gavel(c, x, y, s, hit)  ·  M.coin(c, x, y, r)     Richterhammer (hit 0..1 = schlägt zu) · Euro-Münze
    M.person(c, x, y, s, col)  ·  M.crowd(c, lt, t0)    Figur · Menschenmenge, die nacheinander aufploppt (Sammelklage, „145.000 Leute“)
    M.euro(v)  ·  M.thousands(v)                        Zahl als Text: 89.9 -> „89,90 €“ · 145000 -> „145.000“

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


# ---------------------------------------------------------------- Vertrag / Versicherung / Post (aus dem Video „Kfz-Versicherung“, 25.11.)
def car(c, x, y, s=1.0, col=VIO):
    """Auto von der Seite (fährt nach rechts)."""
    c.save(); c.translate(x, y); c.scale(s, s)
    p = skia.Path(); p.moveTo(-232, 44); p.lineTo(-232, -8); p.cubicTo(-228, -40, -195, -52, -150, -56); p.lineTo(-96, -132)
    p.cubicTo(-86, -146, -72, -152, -52, -152); p.lineTo(72, -152); p.cubicTo(96, -152, 112, -142, 126, -122); p.lineTo(172, -56)
    p.cubicTo(216, -50, 236, -30, 236, 2); p.lineTo(236, 44); p.close()
    C.path(c, p, col)
    for pts in (((-122, -62), (-80, -124), (-8, -124), (-8, -62)), ((14, -62), (14, -124), (72, -124), (120, -62))):
        w = skia.Path(); w.moveTo(*pts[0])
        for q in pts[1:]:
            w.lineTo(*q)
        w.close(); c.drawPath(w, P('#bfe6ff')); c.drawPath(w, P(INK, stroke=8))
    C.box(c, 198, -30, 34, 28, YEL, r=10, out=6, shadow=0); C.box(c, -230, -26, 24, 26, RED, r=8, out=6, shadow=0)
    c.drawLine(-40, -20, 0, -20, P(INK, stroke=8))                                  # Türgriff
    for wx in (-138, 142):
        c.drawCircle(wx, 50, 58, P(INK)); c.drawCircle(wx, 50, 26, P(GREY)); c.drawCircle(wx, 50, 26, P(INK, stroke=6))
    c.restore()


def shield(c, x, y, s=1.0, col=GREEN, mark=True):
    """Schutzschild (Versicherung) mit Haken."""
    p = skia.Path(); p.moveTo(0, -92); p.lineTo(80, -62); p.lineTo(80, 6); p.cubicTo(80, 56, 40, 86, 0, 102)
    p.cubicTo(-40, 86, -80, 56, -80, 6); p.lineTo(-80, -62); p.close()
    c.save(); c.translate(x, y); c.scale(s, s); C.path(c, p, col, out=9, shadow=9)
    if mark:
        q = skia.Path(); q.moveTo(-34, 2); q.lineTo(-10, 28); q.lineTo(36, -26)
        c.drawPath(q, P(INK, stroke=24)); c.drawPath(q, P(WHITE, stroke=13))
    c.restore()


def lock(c, x, y, s=1.0, col=YEL):
    """Vorhängeschloss (geschlossen), Mitte = (x, y)."""
    c.save(); c.translate(x, y + 32 * s); c.scale(s, s)
    u = skia.Path(); u.moveTo(-52, 6); u.lineTo(-52, -34); u.cubicTo(-52, -104, 52, -104, 52, -34); u.lineTo(52, 6)
    c.drawPath(u, P(INK, stroke=40)); c.drawPath(u, P(GREY, stroke=20))
    C.box(c, -92, -6, 184, 146, col, r=28)
    c.drawCircle(0, 52, 18, P(INK)); c.drawRoundRect(skia.Rect.MakeXYWH(-8, 56, 16, 44), 6, 6, P(INK))
    c.restore()


def chain(c, y, x0=-20, x1=1100, n=11, col=GREY):
    """Kette quer durchs Bild auf Höhe y (liegende und stehende Glieder im Wechsel)."""
    step = (x1 - x0) / n
    for k in range(n + 1):
        x = x0 + k * step
        if k % 2 == 0:
            r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - step * 0.62, y - 30, step * 1.24, 60), 30, 30)
        else:
            r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - 16, y - 20, 32, 40), 14, 14)
        c.drawRRect(r, P(INK, stroke=30)); c.drawRRect(r, P(col, stroke=13))


def letter(c, x, y, s=1.0, rot=0.0):
    """Briefumschlag."""
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    C.box(c, -130, -86, 260, 172, WHITE, r=18)
    p = skia.Path(); p.moveTo(-124, -78); p.lineTo(0, 14); p.lineTo(124, -78); c.drawPath(p, P(INK, stroke=9))
    c.restore()


def cross(c, x, y, s=1.0, col=RED):
    """Dickes rotes Kreuz („nein“, „reicht nicht“)."""
    for stroke, colr, grow in ((True, INK, 12), (False, col, 0)):
        for a in (45, -45):
            c.save(); c.translate(x + (10 if stroke else 0) * 0, y); c.rotate(a)
            w, h = 320 * s + 2 * grow, 64 * s + 2 * grow
            c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), h / 3, h / 3), P(colr))
            c.restore()


def mailbox(c, x, y, s=1.0, col=VIO):
    """Briefkasten auf einem Pfosten (ohne Logo), Schlitz oben."""
    c.save(); c.translate(x, y); c.scale(s, s)
    C.box(c, -20, 70, 40, 190, GREY, r=12, out=8, shadow=8)
    C.box(c, -160, -130, 320, 220, col, r=44)
    c.drawRoundRect(skia.Rect.MakeXYWH(-104, -84, 208, 30), 15, 15, P(INK))
    C.box(c, -70, -10, 140, 56, WHITE, r=14, out=7, shadow=0)
    for k in range(2):
        c.drawLine(-48, 8 + k * 18, 48 - 30 * k, 8 + k * 18, P(GREY, stroke=9))
    c.restore()


def office(c, x, y, s=1.0, sign=True):
    """Bürohaus (Versicherer, Amt, Firma) mit Schild-Zeichen auf dem Dach."""
    c.save(); c.translate(x, y); c.scale(s, s)
    C.box(c, -150, -210, 300, 420, WHITE, r=20)
    for r_ in range(4):
        for k in range(3):
            C.box(c, -112 + k * 84, -176 + r_ * 78, 56, 50, '#bfe6ff', r=8, out=6, shadow=0)
    C.box(c, -36, 122, 72, 88, VIO, r=10, out=7, shadow=0)
    c.restore()
    if sign:
        shield(c, x, y - 250 * s, 0.62 * s)


def arrow_up(c, x, y, s=1.0, col=RED):
    """Dicker Pfeil nach oben („wird teurer“)."""
    p = skia.Path(); p.moveTo(0, -120); p.lineTo(92, -10); p.lineTo(38, -10); p.lineTo(38, 120); p.lineTo(-38, 120); p.lineTo(-38, -10); p.lineTo(-92, -10); p.close()
    c.save(); c.translate(x, y); c.scale(s, s); C.path(c, p, col, out=9, shadow=10); c.restore()


def arc_arrow(c, x0, y0, x1, y1, bend=160, k=1.0, col=VIO, w=16):
    """Bogenpfeil von (x0, y0) nach (x1, y1), nach oben gewölbt (bend); k = 0..1 lässt ihn wachsen."""
    k = clamp(k)
    if k <= 0.02:
        return
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2 - bend
    pt = lambda u: ((1 - u) ** 2 * x0 + 2 * (1 - u) * u * cx + u * u * x1, (1 - u) ** 2 * y0 + 2 * (1 - u) * u * cy + u * u * y1)
    p = skia.Path(); p.moveTo(*pt(0)); n = 28
    for j in range(1, int(n * k) + 1):
        p.lineTo(*pt(j / n))
    c.drawPath(p, P(INK, stroke=w + 12)); c.drawPath(p, P(col, stroke=w))
    ex, ey = pt(k); bx, by = pt(max(0.0, k - 0.06)); a = math.atan2(ey - by, ex - bx)
    h = skia.Path(); h.moveTo(ex + 46 * math.cos(a), ey + 46 * math.sin(a))
    h.lineTo(ex + 40 * math.cos(a + 2.2), ey + 40 * math.sin(a + 2.2)); h.lineTo(ex + 40 * math.cos(a - 2.2), ey + 40 * math.sin(a - 2.2)); h.close()
    c.drawPath(h, P(col)); c.drawPath(h, P(INK, stroke=9))


def doc(c, x, y, title='VERTRAG', hl=None, hl_text='', w=460, h=540, lines=5):
    """Dokument mit violetter Kopfzeile. hl = Nummer der Zeile, die gelb markiert ist (0 = erste); hl_text = Wort in der Markierung."""
    C.box(c, x - w / 2, y - h / 2, w, h, WHITE, r=30)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - w / 2 + 5, y - h / 2 + 5, w - 10, 100), 26, 26), P(VIO))
    c.drawRect(skia.Rect.MakeXYWH(x - w / 2 + 5, y - h / 2 + 60, w - 10, 46), P(VIO))
    C.text(c, title, x, y - h / 2 + 80, 56, WHITE, maxw=w - 60)
    gap = (h - 190) / lines
    for k in range(lines):
        ly = y - h / 2 + 160 + k * gap
        if hl is not None and k == hl:
            C.box(c, x - w / 2 + 36, ly - 34, w - 72, 68, YEL, r=16, out=7, shadow=0)
            if hl_text:
                C.text(c, hl_text, x, ly + 17, 46, INK, maxw=w - 110)
        else:
            c.drawLine(x - w / 2 + 50, ly, x + w / 2 - 50 - (90 if k % 2 else 0), ly, P(GREY, stroke=17))


# ---------------------------------------------------------------- Preis / Gericht / Menschen (aus dem Video „Amazon Prime“, 25.11.)
def euro(v, dec=2):
    """89.9 -> '89,90 €' (deutsche Schreibweise)."""
    return (f'{v:.{dec}f}'.replace('.', ',')) + ' €'


def thousands(v):
    """145000 -> '145.000'."""
    return f'{int(round(v)):,}'.replace(',', '.')


def pricecard(c, x, y, label='Abo', price='89,90 €', w=780, h=140, pcol=YEL, ptxt=INK):
    """Breite Karte (Pille): links die Bezeichnung, rechts der Preis in einer farbigen Pille."""
    C.box(c, x - w / 2, y - h / 2, w, h, WHITE, r=h / 2)
    pw = w * 0.43
    C.text(c, label, x - w / 2 + (w - pw) / 2 + 6, y + h * 0.16, h * 0.42, INK, maxw=w - pw - 70)
    C.box(c, x + w / 2 - pw - 14, y - h / 2 + 14, pw, h - 28, pcol, r=(h - 28) / 2, out=7, shadow=0)
    C.text(c, price, x + w / 2 - pw / 2 - 14, y + h * 0.165, h * 0.44, ptxt, maxw=pw - 44)


def gavel(c, x, y, s=1.0, hit=0.0):
    """Richterhammer über einem Sockel; hit 0..1 = Hammer schlägt nach unten."""
    c.save(); c.translate(x, y); c.scale(s, s)
    C.box(c, -170, 150, 340, 50, '#8f5429', r=16)
    C.box(c, -120, 116, 240, 44, '#b9743f', r=14, out=8, shadow=0)
    c.save(); c.translate(120, 60); c.rotate(-38 + 30 * clamp(hit)); c.translate(-120, -60)
    C.box(c, -40, 34, 300, 36, '#b9743f', r=16, out=8, shadow=8)                    # Stiel
    C.box(c, -150, -40, 150, 190, '#8f5429', r=24)                                  # Kopf
    for yy in (-12, 100):
        c.drawRoundRect(skia.Rect.MakeXYWH(-146, yy, 142, 22), 8, 8, P(YEL))
    c.restore(); c.restore()


def coin(c, x, y, r=60):
    """Euro-Münze."""
    C.circle(c, x, y, r, YEL, out=8, shadow=7)
    c.drawCircle(x, y, r * 0.74, P(YEL_D, stroke=6))
    C.text(c, '€', x, y + r * 0.36, r * 1.05, INK)


def person(c, x, y, s=1.0, col=VIO):
    """Einfache Figur (Kopf + Körper)."""
    c.save(); c.translate(x, y); c.scale(s, s)
    p = skia.Path(); p.moveTo(-52, 86); p.cubicTo(-52, 10, -30, -6, 0, -6); p.cubicTo(30, -6, 52, 10, 52, 86); p.close()
    C.path(c, p, col, out=8, shadow=7)
    C.circle(c, 0, -44, 36, '#ffe1c4', out=8, shadow=0)
    c.restore()


def crowd(c, lt, t0=0.0, n=12, cols=6, x0=165, y0=400, dx=150, dy=190, s=1.0, stagger=0.045, colors=(VIO, YEL, GREEN, '#4f8cff', RED)):
    """Menschenmenge: n Figuren in Reihen, ploppen nacheinander auf (ab t0, Abstand stagger)."""
    for k in range(n):
        u = lt - t0 - k * stagger
        if u <= 0:
            continue
        if k % 3 == 0:
            L.sfx('pop', ('crowd', k // 3, round(t0, 2)))
        q = min(1.0, K.pop(u))
        x = x0 + (k % cols) * dx + (dx / 2 if (k // cols) % 2 else 0); y = y0 + (k // cols) * dy
        person(c, x, y + 8 * math.sin(L.NOW * 3 + k), s * max(q, 0.01), colors[k % len(colors)])


# ---------------------------------------------------------------- Körper / Verdauung (Mythos oder Fakt? #1, 26.11.2026)
STOM = '#ff9db5'          # Magen-Rosa
GUM = '#ff5d8f'           # Kaugummi-Pink


def stomach(c, x, y, s=1.0, fill=STOM, tube=True):
    """Magen als J-förmige Bohne mit Speiseröhre oben links und Ausgang unten rechts (Mitte ca. bei x, y).
    Rückgabe: Punkte (oben = Speiseröhren-Eingang, mitte = Magen-Mitte, aus = Ausgang) in Bild-Koordinaten."""
    c.save(); c.translate(x, y); c.scale(s, s)
    if tube:
        C.box(c, -78, -300, 64, 200, fill, r=30, out=9, shadow=0)
    p = skia.Path()
    p.moveTo(-70, -130); p.cubicTo(-190, -120, -210, 60, -110, 130); p.cubicTo(-10, 200, 150, 180, 190, 90)
    p.cubicTo(205, 50, 175, 20, 140, 40); p.cubicTo(80, 80, 20, 50, 15, -10); p.cubicTo(10, -80, 20, -135, -70, -130)
    p.close(); C.path(c, p, fill, out=10, shadow=12)
    q = skia.Path(); q.moveTo(-120, -40); q.cubicTo(-140, 30, -100, 90, -40, 110)
    c.drawPath(q, P(WHITE, 150, stroke=14))
    C.box(c, 160, 52, 90, 50, fill, r=24, out=9, shadow=0)
    c.restore()
    return dict(oben=(x - 46 * s, y - 290 * s), mitte=(x - 60 * s, y + 30 * s), aus=(x + 235 * s, y + 77 * s))


def gum(c, x, y, r=60, rot=0.0, face=False):
    """Kaugummi-Kugel (pink, mit Glanz und Kau-Falten)."""
    c.save(); c.translate(x, y); c.rotate(rot)
    p = skia.Path()
    for k in range(13):
        a = k / 12 * 2 * math.pi; rr = r * (1 + 0.07 * math.sin(3 * a + 0.6))
        (p.moveTo if k == 0 else p.lineTo)(rr * math.cos(a), rr * math.sin(a))
    p.close(); C.path(c, p, GUM, out=max(6, r * 0.12), shadow=r * 0.14)
    c.drawArc(skia.Rect.MakeXYWH(-r * 0.6, -r * 0.6, r * 1.2, r * 1.2), 200, 70, False, P(WHITE, 220, stroke=max(4, r * 0.16)))
    for a in (0.3, 2.2):
        c.drawArc(skia.Rect.MakeXYWH(-r * 0.35 + 18 * math.cos(a), -r * 0.2, r * 0.6, r * 0.5), 20, 120, False,
                  P(INK, 150, stroke=max(3, r * 0.06)))
    if face:
        c.drawCircle(-r * 0.3, -r * 0.05, r * 0.1, P(INK)); c.drawCircle(r * 0.3, -r * 0.05, r * 0.1, P(INK))
    c.restore()


def kernel(c, x, y, s=1.0, rot=0.0):
    """Maiskorn (gelber Tropfen)."""
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    p = skia.Path(); p.moveTo(0, -46); p.cubicTo(40, -44, 44, 10, 26, 36); p.cubicTo(14, 52, -14, 52, -26, 36)
    p.cubicTo(-44, 10, -40, -44, 0, -46); p.close(); C.path(c, p, YEL, out=7, shadow=6)
    c.drawOval(skia.Rect.MakeXYWH(-12, 10, 24, 22), P('#fff3c4'))
    c.restore()


def gut_path(x0=90, x1=990, y=560, amp=90, n=2.5):
    """Wellen-Weg durch den Darm (für Bewegungen): Funktion u (0..1) -> (x, y)."""
    return lambda u: (x0 + (x1 - x0) * u, y + amp * math.sin(u * n * 2 * math.pi))


def gut(c, f, k=1.0, col='#ffc2d1'):
    """Darm-Schlauch entlang der Weg-Funktion f (von gut_path), wächst mit k."""
    p = skia.Path(); m = 60
    for i in range(int(m * k) + 1):
        x, y = f(i / m); (p.moveTo if i == 0 else p.lineTo)(x, y)
    c.drawPath(p, P(INK, stroke=118)); c.drawPath(p, P(col, stroke=96))
    c.drawPath(p, P(WHITE, 90, stroke=16))


def doctor(c, x, y, s=1.0):
    """Ärztin: Figur im weißen Kittel mit Stirnspiegel (keine echte Person)."""
    c.save(); c.translate(x, y); c.scale(s, s)
    pth = skia.Path(); pth.moveTo(-58, 90); pth.cubicTo(-58, 8, -32, -8, 0, -8); pth.cubicTo(32, -8, 58, 8, 58, 90); pth.close()
    C.path(c, pth, WHITE, out=8, shadow=7)
    c.drawLine(0, 0, 0, 88, P(GREY, stroke=6))
    C.box(c, 14, 24, 26, 30, '#bfe6ff', r=6, out=5, shadow=0)
    C.circle(c, 0, -48, 38, '#ffe1c4', out=8, shadow=0)
    c.drawArc(skia.Rect.MakeXYWH(-40, -94, 80, 50), 180, 180, False, P('#5b3a29', stroke=18))
    C.circle(c, 0, -80, 15, '#dbe7f2', out=5, shadow=0)
    c.drawCircle(-12, -46, 4.5, P(INK)); c.drawCircle(12, -46, 4.5, P(INK))
    c.drawArc(skia.Rect.MakeXYWH(-12, -40, 24, 14), 20, 140, False, P(INK, stroke=4))
    c.restore()


def bubble(c, x, y, w, h, text, size=64, fill=WHITE, txt=INK, tail=(-1, 1)):
    """Sprechblase mit Zipfel (tail = Richtung)."""
    p = skia.Path(); bx = x + tail[0] * w * 0.25
    p.moveTo(bx - 26, y + h / 2 - 4); p.lineTo(bx + tail[0] * 60, y + h / 2 + 64 * tail[1]); p.lineTo(bx + 30, y + h / 2 - 4); p.close()
    C.path(c, p, fill, out=8, shadow=0)
    C.box(c, x - w / 2, y - h / 2, w, h, fill, r=min(h / 2, 44), out=8, shadow=9)
    c.drawRect(skia.Rect.MakeXYWH(bx - 22, y + h / 2 - 14, 48, 14), P(fill))
    C.text(c, text, x, y + size * 0.36, size, txt, maxw=w - 50)


# ---------------------------------------------------------------- Kälte & Erkältung (27.11.2026, Mythos oder Fakt? #2)
def thermo(c, x, y, s=1.0, v=0.5, col=RED, label=None):
    """Thermometer, Füllstand v (0..1). label = Text in einer Pille rechts daneben (z. B. '4 °C')."""
    c.save(); c.translate(x, y); c.scale(s, s)
    C.box(c, -42, -230, 84, 330, WHITE, r=42, out=10, shadow=10)
    C.circle(c, 0, 130, 70, col, out=10, shadow=8)
    h = 270 * clamp(v)
    c.drawRoundRect(skia.Rect.MakeXYWH(-18, 110 - h, 36, h + 30), 18, 18, P(col))
    for k in range(5):
        yy = -190 + k * 60
        c.drawLine(10, yy, 34, yy, P(INK, stroke=6))
    c.restore()
    if label:
        C.chip(c, label, x + 150 * s, y - 60 * s, 54 * s, WHITE, INK, angle=4)


def flake(c, x, y, r=40, rot=0.0, col=WHITE, a=255):
    """Schneeflocke (sechs Arme) mit dunklem Umriss."""
    c.save(); c.translate(x, y); c.rotate(rot)
    for st, cc in ((max(5, r * 0.32), INK), (max(3, r * 0.16), col)):
        pa = P(cc, a, stroke=st)
        for k in range(6):
            an = math.radians(k * 60)
            ex, ey = r * math.cos(an), r * math.sin(an)
            c.drawLine(0, 0, ex, ey, pa)
            for f in (0.55,):
                mx, my = ex * f, ey * f
                for d in (-1, 1):
                    b = an + d * math.radians(40)
                    c.drawLine(mx, my, mx + r * 0.32 * math.cos(b), my + r * 0.32 * math.sin(b), pa)
    c.restore()


def snow(c, T, n=14, y0=160, y1=820, seed=3, a=255):
    """Leise fallende Flocken im Bühnenbereich (bewegt sich immer)."""
    for k in range(n):
        ph = (k * 0.61803 + seed * 0.13) % 1
        x = 90 + (k * 137 + seed * 53) % 900 + 22 * math.sin(T * 1.3 + k)
        y = y0 + ((ph + T * (0.10 + 0.03 * (k % 3))) % 1) * (y1 - y0)
        flake(c, x, y, 16 + 8 * (k % 3), rot=T * 0.8 + k, a=a)


def virus(c, x, y, r=110, col=None, face=True, rot=0.0):
    """Virus als Sticker: Kugel mit Noppen, optional mit frechem Gesicht."""
    col = col or K.SF
    c.save(); c.translate(x, y); c.rotate(rot)
    for k in range(10):
        an = math.radians(k * 36)
        ex, ey = (r + 34) * math.cos(an), (r + 34) * math.sin(an)
        c.drawLine(r * 0.8 * math.cos(an), r * 0.8 * math.sin(an), ex, ey, P(INK, stroke=16))
        C.circle(c, ex, ey, 20, YEL, out=7, shadow=0)
    C.circle(c, 0, 0, r, col, out=11, shadow=10)
    for (dx, dy, rr) in ((-0.4, 0.35, 0.16), (0.42, -0.4, 0.12), (0.2, 0.5, 0.09)):
        c.drawCircle(dx * r, dy * r, rr * r, P(mixc(col, INK, 0.25)))
    if face:
        for dx in (-0.3, 0.3):
            C.circle(c, dx * r, -0.12 * r, 0.16 * r, WHITE, out=6, shadow=0)
            c.drawCircle(dx * r + 4, -0.1 * r, 0.07 * r, P(INK))
        p = skia.Path(); p.moveTo(-0.3 * r, 0.22 * r); p.quadTo(0, 0.42 * r, 0.3 * r, 0.22 * r)
        c.drawPath(p, P(INK, stroke=9))
    c.restore()


def nose(c, x, y, s=1.0, cold=0.0):
    """Große Comic-Nase im Profil; cold 0..1 färbt sie bläulich-kalt."""
    col = mixc('#ffcfb0', '#9fd3ff', clamp(cold))
    c.save(); c.translate(x, y); c.scale(s, s)
    p = skia.Path(); p.moveTo(-120, -200); p.cubicTo(-60, -120, 40, 20, 120, 70); p.cubicTo(150, 92, 130, 140, 80, 140)
    p.lineTo(-40, 140); p.cubicTo(-120, 140, -150, 90, -120, 40); p.close()
    C.path(c, p, col, out=11, shadow=10)
    c.drawOval(skia.Rect.MakeXYWH(-40, 100, 70, 30), P(mixc(col, INK, 0.45)))
    c.drawArc(skia.Rect.MakeXYWH(-130, 30, 110, 110), 120, 120, False, P(mixc(col, INK, 0.35), stroke=8))
    c.restore()


def tissues(c, x, y, s=1.0, col=None):
    """Taschentuch-Box mit herausschauendem Tuch."""
    col = col or K.SF
    c.save(); c.translate(x, y); c.scale(s, s)
    p = skia.Path(); p.moveTo(-40, -60); p.cubicTo(-70, -150, 10, -170, 0, -110); p.cubicTo(30, -170, 90, -130, 40, -60); p.close()
    C.path(c, p, WHITE, out=8, shadow=0)
    C.box(c, -170, -70, 340, 190, col, r=26)
    c.drawRoundRect(skia.Rect.MakeXYWH(-80, -62, 160, 26), 13, 13, P(INK))
    c.drawLine(-170, 40, 170, 40, P(mixc(col, WHITE, 0.4), stroke=14))
    c.restore()


def vesicles(c, x, y, n, T, spread=260, col=None, a=255):
    """Viele winzige Abwehr-Bläschen, die um (x, y) schweben – n = Anzahl."""
    col = col or K.SF
    for k in range(int(n)):
        an = k * 2.39996
        rr = spread * math.sqrt((k + 0.5) / 60.0)
        bx = x + rr * math.cos(an) + 10 * math.sin(T * 2 + k)
        by = y + rr * 0.62 * math.sin(an) + 10 * math.cos(T * 1.7 + k * 0.7)
        rad = 15 + 5 * (k % 3)
        c.drawCircle(bx, by, rad + 5, P(INK, a))
        c.drawCircle(bx, by, rad, P(mixc(col, WHITE, 0.35), a))
        c.drawCircle(bx - rad * 0.35, by - rad * 0.35, rad * 0.28, P(WHITE, a))
