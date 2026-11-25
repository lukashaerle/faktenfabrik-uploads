"""Episode 25.11. 17:30: Steuerbescheid ab 1.1.2027 digital – für ELSTER-Nutzer kommt kein Brief mehr; der Bescheid gilt am
vierten Tag nach Bereitstellung als bekannt gegeben (§ 122a AO n. F., BMF-Schreiben 13.08.2026), ab dann ein Monat Einspruchsfrist.
Papier nur auf Antrag (Mein ELSTER → Elektronische Bekanntgabe verwalten).
Stil: FINN-Show (LOOK cartoon + KINO), ruhiges Tempo (25.11.), Viral-Aufbau V3 mit Loop. Aufbau wie ep_kfz."""
import math
import skia
import render as L
import cartoon as C
import kino as K
import motive as M
from render import clamp, ease, ease_out, lerp
from cartoon import INK, VIO, YEL, RED, GREEN, WHITE, GREY

EDIT = 2
LOOK = 'cartoon'
KINO = True
LOOP = True
TOPIC = ''
HOOK_TEXT = 'x'                 # Platzhalter: hält die Untertitel bis HOOK_END zurück – der Hook steht als K.slam im Bild
HOOK_END = 3.39
HIGHLIGHT = ['Januar', 'Post.', 'ELSTER', 'ELSTER-Postfach.', 'Mail', 'Brief', 'Haken:', 'vierten', 'zugestellt', 'ungeöffnet.',
             'Einspruchsfrist.', 'Monat.', 'beantragen.', 'verwalten“.', 'Schick']
FADE_COL = ['#000000'] * 10
# 6 = harter Schnitt nach dem Stempel „ZUGESTELLT“; 5 = Schnitt auf die kurze Nahaufnahme
K.SCENE_TRANS = {1: 'ink', 2: 'whip', 3: 'zoom', 4: 'cut', 5: 'ink', 6: 'cut', 7: 'zoom', 8: 'whip', 9: 'zoom'}
K.SHOT_TRANS = {(0, 1): 'snap', (3, 1): 'zoom', (5, 1): 'cut', (7, 1): 'zoom', (9, 1): 'ink'}


# ---------------------------------------------------------------- kleine Motive nur für diese Folge
def screen(c, x, y, w=640, h=430, title='ELSTER'):
    """Bildschirm mit Titelleiste (Online-Finanzamt – nur Schrift, kein Logo)."""
    C.box(c, x - w / 2, y - h / 2, w, h, INK, r=34)
    C.box(c, x - w / 2 + 22, y - h / 2 + 22, w - 44, h - 44, WHITE, r=20, out=0, shadow=0)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - w / 2 + 22, y - h / 2 + 22, w - 44, 84), 20, 20), L.P(VIO))
    c.drawRect(skia.Rect.MakeXYWH(x - w / 2 + 22, y - h / 2 + 70, w - 44, 36), L.P(VIO))
    C.text(c, title, x, y - h / 2 + 84, 54, WHITE, maxw=w - 100)
    C.box(c, x - 40, y + h / 2, 80, 60, GREY, r=10, out=7, shadow=0)
    C.box(c, x - 150, y + h / 2 + 50, 300, 34, GREY, r=17, out=7, shadow=0)


def phone(c, x, y, s=1.0):
    """Handy mit leerem Bildschirm."""
    c.save(); c.translate(x, y); c.scale(s, s)
    C.box(c, -150, -270, 300, 540, INK, r=54)
    C.box(c, -128, -236, 256, 472, '#eef0ff', r=34, out=0, shadow=0)
    c.drawRoundRect(skia.Rect.MakeXYWH(-40, -256, 80, 14), 7, 7, L.P(GREY))
    c.restore()


def notice(c, x, y, k, text='1 neue Mail'):
    """Benachrichtigung, die auf dem Handy aufploppt."""
    c.save(); c.translate(x, y); c.scale(k, k)
    C.box(c, -200, -62, 400, 124, WHITE, r=30)
    C.circle(c, -132, 0, 38, YEL, out=7, shadow=0)
    p = skia.Path(); p.moveTo(-154, -12); p.lineTo(-132, 6); p.lineTo(-110, -12)
    c.drawRect(skia.Rect.MakeXYWH(-154, -16, 44, 32), L.P(WHITE)); c.drawRect(skia.Rect.MakeXYWH(-154, -16, 44, 32), L.P(INK, stroke=5))
    c.drawPath(p, L.P(INK, stroke=5))
    C.text(c, text, 40, 16, 50, INK, maxw=260)
    c.restore()


# ---------------------------------------------------------------- Hook (Startbild = Schlussbild)
def opening(c, lt, t, loop=False):
    """Bild 0: „AB JANUAR / KEIN BRIEF!“, darunter der Steuerbrief, der zum Briefkasten fliegt. loop=True: Schlussbild."""
    K.stage(c, 'yel')
    k0 = 1.0 if (loop or L.SAFE_CHECK) else 1 + 0.12 * math.exp(-lt * 13)
    c.save(); c.translate(540, 310); c.scale(k0, k0); c.translate(-540, -310)
    K.slam(c, 'AB JANUAR:', lt, -9, 540, 322, 150, rot=-3, maxw=900, snd=None)
    c.restore()
    K.slam(c, 'KEIN BRIEF MEHR!', lt, -9, 540, 500, 124, color=WHITE, box=VIO, rot=2, maxw=900, snd=None)
    fly = 0.0 if loop else ease(clamp(lt / 2.6))
    M.mailbox(c, 830, 690, 0.7)
    lx, ly = lerp(290, 560, fly), 670 - 50 * math.sin(math.pi * fly) + K.wig(5, 2.0)
    M.letter(c, lx, ly, 1.0, rot=-10 + 14 * fly)
    C.chip(c, 'STEUERBESCHEID', lx, ly + 112, 40, WHITE, INK, angle=-4)
    K.host(c, t, mood='happy', pose='up', x=480, y=1350, s=1.95, look=(0.5, -0.8))


def hook2(c, lt, t):
    """„… nicht mehr per Post.“ – violett, der Briefkasten bleibt leer, das Kreuz knallt auf „Post“."""
    K.stage(c, 'vio')
    tp = K.at(0, 'post', t, lt, 0.5); hit = lt >= tp
    K.slam(c, 'STEUERBESCHEID', lt, 0.0, 540, 305, 112, rot=-3, snd=None)
    K.show(c, lt, 0.05, 540, 640, lambda cc: M.mailbox(cc, 540, 620, 1.05), kind='pop')
    K.show(c, lt, tp, 540, 590, lambda cc: M.cross(cc, 540, 590, 1.0), kind='slam', snd='thud')
    K.host(c, t, mood='shock' if hit else 'puzzled', pose='both_up' if hit else 'hips', x=500, y=1350, s=1.95,
           look=(0.2, -0.8), jump=(70 * math.exp(-(lt - tp) * 7) if hit else 0))


# ---------------------------------------------------------------- Szenen
def s1(c, t, d):
    i, lt, ld = K.begin(c, 0, t, d, marks=['nicht'], shake=['post'], focus=(540, 700))
    opening(c, lt, t) if i == 0 else hook2(c, lt, t)


def s2(c, t, d):                                   # Das gilt, wenn du deine Steuererklärung über ELSTER machst.
    i, lt, ld = K.begin(c, 1, t, d, punch=['elster'])
    K.stage(c, 'cream', 'blue')
    te = K.at(1, 'elster', t, lt, 2.0); ts = K.at(1, 'steuererklärung', t, lt, 1.0)
    K.show(c, lt, 0.0, 540, 500, lambda cc: screen(cc, 540, 500, 640, 400, 'ELSTER'), kind='pop')
    K.show(c, lt, ts, 540, 520, lambda cc: M.doc(cc, 540, 540, 'STEUER', w=230, h=240, lines=3), kind='drop')
    K.show(c, lt, te + 0.1, 850, 330, lambda cc: M.check(cc, 850, 330, 1.0), kind='pop')
    K.host(c, t, mood='happy', pose='point_r', look=(0.4, -1))


def s3(c, t, d):                                   # Der Bescheid landet dann nur noch in deinem ELSTER-Postfach.
    i, lt, ld = K.begin(c, 2, t, d, punch=['landet'], step=['postfach'])
    K.stage(c, 'cream', 'vio')
    tl = K.at(2, 'landet', t, lt, 0.6); tp = K.at(2, 'elster', t, lt, 2.0)
    K.show(c, lt, 0.0, 540, 520, lambda cc: screen(cc, 540, 520, 660, 420, 'POSTFACH'), kind='pop')
    for k in range(3):                             # Zeilen im Postfach
        c.drawRoundRect(skia.Rect.MakeXYWH(300, 520 + k * 62, 480, 34), 17, 17, L.P('#d9dcf0'))
    drop = ease_out(clamp((lt - tl) / 0.4))
    if lt >= tl - 0.02:
        M.doc(c, 540, lerp(380, 560, drop), 'BESCHEID', w=250, h=270, lines=3)
    K.show(c, lt, tp, 830, 300, lambda cc: C.chip(cc, 'NUR DIGITAL', 830, 300, 60, YEL, INK, angle=4), kind='pop')
    K.host(c, t, mood='happy', pose='up', look=(0.2, -1))


def s4(c, t, d):                                   # Du bekommst eine Mail – | aber keinen Brief mehr.
    i, lt, ld = K.begin(c, 3, t, d, marks=['aber'], punch=['mail'], shake=['brief'])
    if i == 0:                                     # Handy, Benachrichtigung ploppt auf „Mail“
        K.stage(c, 'cream', 'green')
        tm = K.at(3, 'mail', t, lt, 0.7)
        K.show(c, lt, 0.0, 540, 520, lambda cc: phone(cc, 540, 540, 0.95), kind='pop')
        if lt >= tm:
            L.sfx('pop', ('mail',))
            notice(c, 540, 430, max(0.01, K.pop(lt - tm)))
        K.host(c, t, mood='happy', pose='point_r', look=(0.3, -1))
    else:                                          # der Briefkasten bleibt zu – Kreuz auf „Brief“
        K.stage(c, 'vio')
        tb = K.at(3, 'brief', t, lt, 0.6); hit = lt >= tb
        K.show(c, lt, 0.0, 540, 600, lambda cc: M.mailbox(cc, 540, 590, 1.1), kind='pop')
        K.show(c, lt, tb, 540, 540, lambda cc: M.cross(cc, 540, 540, 1.1), kind='slam', snd='thud')
        K.slam(c, 'KEIN BRIEF', lt, 0.05, 540, 300, 120, color=INK, box=YEL, rot=-3, snd=None)
        K.host(c, t, mood='shock' if hit else 'puzzled', pose='both_up' if hit else 'hips', look=(0.2, -1),
               jump=(60 * math.exp(-(lt - tb) * 7) if hit else 0))


def s5(c, t, d):                                   # Und jetzt kommt der Haken:
    i, lt, ld = K.begin(c, 4, t, d, focus=(540, 1150))
    K.stage(c, 'cream', 'red')
    K.mark(c, lt, '!', 0.05, 540, 650, 540, fill=RED, rot=6)
    K.closeup(c, t, mood='puzzled', pose='up', lean=4, look=(0, -0.8))


def s6(c, t, d):                                   # Am vierten Tag gilt er als zugestellt – | auch ungeöffnet.
    i, lt, ld = K.begin(c, 5, t, d, marks=['auch'], punch=['vierten'], shake=['zugestellt'])
    if i == 0:                                     # Kalender zählt 1 → 4, Stempel auf „zugestellt“
        K.stage(c, 'cream', 'red')
        tv = K.at(5, 'vierten', t, lt, 0.3); tz = K.at(5, 'zugestellt', t, lt, 1.5)
        day = str(int(round(K.count(lt, max(0.0, tv - 0.35), 1, 4, 0.5, key='tag'))))
        K.show(c, lt, 0.0, 330, 440, lambda cc: M.calendar(cc, 330, 440, 0.85, day, 'TAG'), kind='pop')
        K.show(c, lt, tv + 0.15, 790, 360, lambda cc: C.chip(cc, '4. TAG', 790, 360, 72, YEL, INK, angle=5), kind='right')
        K.show(c, lt, tz, 700, 715, lambda cc: M.stamp(cc, 700, 715, 'ZUGESTELLT', 88, RED, -5), kind='slam', snd='thud')
        K.host(c, t, mood='shock' if lt >= tz else 'happy', pose='both_up' if lt >= tz else 'point_l', look=(0, -1),
               jump=(60 * math.exp(-(lt - tz) * 7) if lt >= tz else 0))
    else:                                          # der Brief ist noch zu – trotzdem zugestellt
        K.stage(c, 'vio')
        tu = K.at(5, 'ungeöffnet', t, lt, 0.4)
        K.show(c, lt, 0.0, 540, 560, lambda cc: M.letter(cc, 540, 570 + K.wig(5, 1.6), 1.7, rot=-6), kind='pop')
        K.slam(c, 'UNGEÖFFNET', lt, tu, 540, 335, 118, color=INK, box=YEL, rot=-3, snd='thud')
        K.host(c, t, mood='shock', pose='stop', look=(0.2, -1))


def s7(c, t, d):                                   # Ab dann läuft die Einspruchsfrist. Nur ein Monat.
    i, lt, ld = K.begin(c, 6, t, d, punch=['einspruchsfrist'], shake=['monat'])
    K.stage(c, 'cream', 'yel')
    te = K.at(6, 'einspruchsfrist', t, lt, 0.8); tm = K.at(6, 'monat', t, lt, 2.6); hit = lt >= tm
    run = max(0.0, lt - 0.2)
    K.show(c, lt, 0.0, 300, 530, lambda cc: M.clock(cc, 300, 530, 165, 3 + run * 2.0, (run * 240) % 60, ring=0.6 if hit else 0.0), kind='pop')
    K.show(c, lt, te, 760, 330, lambda cc: C.chip(cc, 'EINSPRUCH', 760, 330, 62, WHITE, INK, angle=4), kind='pop')
    K.slam(c, '1 MONAT', lt, tm, 740, 600, 110, color=INK, box=YEL, rot=-4, maxw=400, snd='thud')
    K.host(c, t, mood='shock' if hit else 'puzzled', pose='both_up' if hit else 'point_l', look=(-0.2, -1),
           jump=(60 * math.exp(-(lt - tm) * 7) if hit else 0))


def s8(c, t, d):                                   # Du willst weiter Post? | Dann musst du sie beantragen.
    i, lt, ld = K.begin(c, 7, t, d, marks=['dann'], punch=['beantragen'], focus=[(540, 1150), None])
    if i == 0:                                     # Nahaufnahme FINN + Fragezeichen
        K.stage(c, 'cream', 'yel')
        K.mark(c, lt, '?', 0.05, 540, 650, 540)
        K.closeup(c, t, mood='puzzled', pose='think', lean=-4)
    else:                                          # Antrag, Haken auf „beantragen“
        K.stage(c, 'cream', 'green')
        tb = K.at(7, 'beantragen', t, lt, 0.7)
        K.show(c, lt, 0.0, 480, 520, lambda cc: M.doc(cc, 480, 520, 'ANTRAG', hl=1, hl_text='POST BITTE', w=480, h=520), kind='drop')
        K.show(c, lt, tb, 800, 380, lambda cc: M.check(cc, 800, 380, 1.15), kind='pop')
        K.host(c, t, mood='happy', pose='cheer' if lt >= tb else 'point_r', look=(0.3, -1))


def s9(c, t, d):                                   # In ELSTER, unter „Elektronische Bekanntgabe verwalten“.
    i, lt, ld = K.begin(c, 8, t, d, punch=['elster'], step=['verwalten'])
    K.stage(c, 'cream', 'blue')
    tb = K.at(8, 'elektronische', t, lt, 1.2); tv = K.at(8, 'verwalten', t, lt, 2.6)
    u = lt - tv
    K.show(c, lt, 0.0, 540, 500, lambda cc: screen(cc, 540, 500, 860, 480, 'MEIN ELSTER'), kind='pop')
    press = clamp(1 - abs(u - 0.07) / 0.09)

    def menu(cc):
        k = 1 - 0.05 * press
        cc.save(); cc.translate(540, 565); cc.scale(k, k)
        C.box(cc, -360, -110, 720, 220, GREEN if u >= 0.07 else WHITE, r=40, shadow=12 * (1 - press))
        C.text(cc, 'Elektronische', 0, -18, 66, INK, maxw=640)
        C.text(cc, 'Bekanntgabe verwalten', 0, 66, 66, INK, maxw=640)
        cc.restore()
    K.show(c, lt, tb, 540, 565, menu, kind='pop')
    if u >= 0:
        L.sfx('pop', ('klick',)); M.ring(c, 760, 610, u)
    q = ease_out(clamp((lt - tb) / max(tv - tb, 0.3)))
    if lt >= tb:
        M.cursor(c, lerp(900, 760, q), lerp(720, 610, q), 1.1)
    K.host(c, t, mood='happy', pose='point_r', look=(0.3, -1))


def s10(c, t, d):                                  # Schick das jemandem, der nie in sein Postfach schaut, | und sag ihm:
    i, lt, ld = K.begin(c, 9, t, d, marks=['und'], focus=(540, 700))
    if i == 0:                                     # Chat: Video verschickt -> Antwort tippt -> „OH NEIN!“
        K.stage(c, 'cream', 'blue')
        t1 = K.at(9, 'schick', t, lt, 0.1); t2 = K.at(9, 'jemandem', t, lt, 0.45); t3 = K.at(9, 'postfach', t, lt, 1.6)
        M.chat(c, lt, t1, t2, t3, reply='OH NEIN!')
        fly = clamp((lt - t1) / 0.8)
        if 0 < fly < 1:
            L.sfx('swipe', ('plane',))
            M.plane(c, lerp(760, 1010, ease(fly)), lerp(400, 250, ease(fly)), 1.15, a=int(255 * (1 - fly)))
        K.host(c, t, mood='happy', pose='cheer' if lt >= t3 else 'point_r', look=(0, 0) if lt >= t3 else (0.3, -1))
    else:                                          # zurück ins Startbild – der Satz läuft in den Hook
        opening(c, lt, t, loop=True)


SCENES = [s1, s2, s3, s4, s5, s6, s7, s8, s9, s10]
