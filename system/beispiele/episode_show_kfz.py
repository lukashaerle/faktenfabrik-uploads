"""Episode 25.11. 17:30: Kfz-Versicherung – bis Montag, 30.11., muss die Kündigung beim Versicherer ANGEKOMMEN sein.
Stil: FINN-Show (LOOK cartoon + KINO), Viral-Aufbau V3 mit Loop. Aufbau wie beispiele/episode_show_paylater.py."""
import math
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
HOOK_END = 2.77
HIGHLIGHT = ['Montag', '31.', 'Stichtag:', '30.', 'Haken:', 'nicht.', 'angekommen', 'spät.', 'Verpasst?', 'weiteres', 'Ausnahme:', 'trotzdem', 'Schick']
FADE_COL = ['#000000'] * 10
# 4 und 6 = harter Schnitt, damit Kreuz und Stempel „ZU SPÄT“ lange genug stehen
K.SCENE_TRANS = {1: 'ink', 2: 'whip', 3: 'zoom', 4: 'cut', 5: 'ink', 6: 'cut', 7: 'zoom', 8: 'whip', 9: 'zoom'}
K.SHOT_TRANS = {(0, 1): 'snap', (2, 1): 'zoom', (9, 1): 'ink'}


# ---------------------------------------------------------------- Hook (Startbild = Schlussbild)
def opening(c, lt, t, loop=False):
    """Bild 0: „BIS MONTAG / KÜNDIGEN!“, darunter der Knopf „Kfz-Versicherung“ – der Zeiger klickt genau auf „kündigen“,
    der Knopf wird grün („Gekündigt“). loop=True: Schlussbild im Anfangszustand."""
    K.stage(c, 'yel')
    tp = 99.0 if loop else K.at(0, 'kündigen', t, lt, 0.6)
    u = lt - tp
    press = clamp(1 - abs(u - 0.07) / 0.09)
    k0 = 1.0 if (loop or L.SAFE_CHECK) else 1 + 0.12 * math.exp(-lt * 13)
    k1 = k0 * (1 + (0.12 * math.exp(-u * 12) if u >= 0 else 0))
    c.save(); c.translate(540, 310); c.scale(k0, k0); c.translate(-540, -310)
    K.slam(c, 'BIS MONTAG', lt, -9, 540, 325, 150, rot=-3, maxw=900, snd=None)
    c.restore()
    c.save(); c.translate(540, 480); c.scale(k1, k1); c.translate(-540, -480)
    K.slam(c, 'KÜNDIGEN!', lt, -9, 540, 512, 160, color=WHITE, box=VIO, rot=2, maxw=850, snd=None)
    c.restore()
    done = u >= 0.07
    M.button(c, 540, 700, h=140, press=press, label='Gekündigt' if done else 'Kfz-Versicherung', fill=GREEN if done else WHITE)
    if done:
        M.check(c, 262, 700, 0.6 * min(1.0, K.pop(u - 0.07) + 0.01), color=INK)
    if u >= 0:
        L.sfx('pop', ('klick',)); M.ring(c, 705, 722, u)
    q = ease_out(clamp(lt / max(tp, 0.15))) if not loop else 0.0
    M.cursor(c, lerp(905, 700, q), lerp(880, 718, q), 1.25)
    K.host(c, t, mood='happy', pose='up', x=500, y=1350, s=1.95, look=(0.5, -0.8))


def hook2(c, lt, t):
    """„… sonst hängst du ein Jahr fest.“ – violett, das Auto fährt rein, „1 JAHR FEST“ knallt rein, Kette und Schloss
    schnappen über dem Auto zu."""
    K.stage(c, 'vio')
    tf = K.at(0, 'hängst', t, lt, 0.28); tj = K.at(0, 'ein', t, lt, 0.75); hit = lt >= tf   # Kette schnappt auf „hängst“ zu
    K.slam(c, 'SONST:', lt, 0.0, 540, 305, 120, rot=-3, snd=None)
    K.show(c, lt, 0.10, 540, 650, lambda cc: M.car(cc, 540, 662, 1.12), kind='left')
    K.slam(c, '1 JAHR FEST', lt, tj, 540, 455, 130, color=INK, box=YEL, rot=2, snd='thud')

    def locked(cc):
        M.chain(cc, 668); M.lock(cc, 540, 656, 0.9)
    K.show(c, lt, tf, 540, 668, locked, kind='slam', snd=None)
    K.host(c, t, mood='shock' if hit else 'puzzled', pose='both_up' if hit else 'hips', x=500, y=1350, s=1.95,
           look=(0.2, -0.8), jump=(70 * math.exp(-(lt - tf) * 7) if hit else 0))


# ---------------------------------------------------------------- Szenen
def s1(c, t, d):
    i, lt, ld = K.begin(c, 0, t, d, marks=['sonst'], shake=['hängst'], focus=(540, 700))
    opening(c, lt, t) if i == 0 else hook2(c, lt, t)


def s2(c, t, d):                                   # Bei den meisten Kfz-Versicherungen | endet das Jahr am 31. Dezember.
    i, lt, ld = K.begin(c, 1, t, d, marks=['endet'], punch=['kfz', '31'])
    if i == 0:                                     # das Auto fährt rein, das Schild der Versicherung ploppt drauf
        K.stage(c, 'cream', 'blue')
        K.show(c, lt, 0.0, 450, 600, lambda cc: M.car(cc, 450, 600 + K.wig(4, 2.2), 1.55), kind='left')
        K.show(c, lt, K.at(1, 'kfz', t, lt, 0.8), 880, 310, lambda cc: M.shield(cc, 880, 310 + K.wig(6, 1.4), 1.4), kind='pop')
        K.host(c, t, mood='happy', pose='point_r', look=(0.4, -1))
    else:                                          # das Blatt springt genau auf „31.“ von 30 auf 31
        K.stage(c, 'cream', 'red')
        t31 = K.at(1, '31', t, lt, 1.0); u = lt - t31 - 0.06
        if u >= 0:
            L.sfx('pop', ('blatt',))
        day, sq = ('31', clamp(u / 0.07)) if u >= 0 else ('30', clamp(-u / 0.07))
        K.show(c, lt, 0.0, 540, 520, lambda cc: M.calendar(cc, 540, 520, 1.25, day, 'DEZEMBER', sq, INK if day == '31' else '#b9b3cc'), kind='pop')
        K.show(c, lt, K.at(1, 'dezember', t, lt, 1.7), 850, 300, lambda cc: M.burst(cc, 850, 300, 124, RED, 'ENDE', WHITE), kind='pop')
        K.host(c, t, mood='happy', pose='up', look=(0.2, -1))


def s3(c, t, d):                                   # Die Kündigungsfrist ist ein Monat. | Stichtag: 30. November.
    i, lt, ld = K.begin(c, 2, t, d, marks=['stichtag'], punch=['monat'], shake=['30'])
    if i == 0:                                     # vom 31. Dezember einen Monat zurück
        K.stage(c, 'cream', 'vio')
        tm = K.at(2, 'ein', t, lt, 1.1)
        K.show(c, lt, 0.0, 790, 580, lambda cc: M.calendar(cc, 790, 580, 0.8, '31', 'DEZEMBER'), kind='drop')
        K.show(c, lt, 0.30, 290, 580, lambda cc: M.calendar(cc, 290, 580, 0.8, '?', 'NOVEMBER', col='#b9b3cc'), kind='pop')
        M.arc_arrow(c, 760, 372, 330, 372, 70, ease_out(clamp((lt - tm) / 0.35)), VIO)
        K.show(c, lt, tm + 0.1, 540, 262, lambda cc: C.chip(cc, '1 MONAT VORHER', 540, 262, 66, YEL, INK, angle=-3), kind='pop')
        K.host(c, t, mood='puzzled', pose='point_l', look=(-0.3, -1))
    else:                                          # Schlüsselzahl: aus dem „?“ wird genau auf „30.“ die 30 – mit Einschlag
        K.stage(c, 'vio')
        t30 = K.at(2, '30', t, lt, 0.8); u = lt - t30; hit = u >= 0
        day, colr = ('30', INK) if hit else ('?', '#b9b3cc')
        pk = 1.15 * (1 + 0.3 * math.exp(-u * 9)) if hit else 1.15
        K.show(c, lt, 0.0, 420, 520, lambda cc: M.calendar(cc, 420, 520, pk, day, 'NOVEMBER', 1.0, colr), kind='pop')
        K.show(c, lt, t30 + 0.18, 852, 520, lambda cc: C.chip(cc, 'MONTAG', 852, 520, 64, YEL, INK, angle=4), kind='right')
        K.host(c, t, mood='shock' if hit else 'happy', pose='both_up' if hit else 'up', look=(0.2, -1),
               jump=(60 * math.exp(-(lt - t30) * 7) if hit else 0))


def s4(c, t, d):                                   # Und jetzt der Haken: | Abschicken reicht nicht.
    i, lt, ld = K.begin(c, 3, t, d, marks=['abschicken'], punch=['reicht'], focus=[(540, 1150), None])
    K.stage(c, 'cream', 'red')
    if i == 0:                                     # Nahaufnahme FINN + rotes Ausrufezeichen
        K.mark(c, lt, '!', 0.05, 540, 650, 540, fill=RED, rot=6)
        K.closeup(c, t, mood='puzzled', pose='up', lean=4, look=(0, -0.8))
    else:                                          # der Brief fliegt los – das Kreuz knallt drauf
        tx = K.at(3, 'reicht', t, lt, 0.5); no = lt >= tx
        fly = ease_out(clamp(lt / 0.45))
        for k in range(3):                         # Tempo-Striche hinter dem Brief
            c.drawLine(lerp(120, 300, fly) - k * 30, 470 + k * 50, lerp(200, 380, fly) - k * 30, 470 + k * 50, L.P(GREY, stroke=14))
        M.letter(c, lerp(260, 600, fly), 520 - 50 * math.sin(math.pi * fly), 1.45, rot=-9)
        K.show(c, lt, tx, 600, 520, lambda cc: M.cross(cc, 600, 520, 1.25), kind='slam', snd='thud')
        K.host(c, t, mood='shock' if no else 'puzzled', pose='stop' if no else 'point_r', look=(0.3, -1))


def s5(c, t, d):                                   # Deine Kündigung muss am Montag beim Versicherer angekommen sein.
    i, lt, ld = K.begin(c, 4, t, d, punch=['montag'], step=['angekommen'])
    K.stage(c, 'cream', 'green')
    tm = K.at(4, 'montag', t, lt, 1.1); ta = K.at(4, 'angekommen', t, lt, 2.2)
    K.show(c, lt, 0.0, 830, 560, lambda cc: M.office(cc, 830, 560, 1.0), kind='pop')
    for k in range(9):                             # gepunkteter Weg vom Absender zum Versicherer
        u = k / 8
        c.drawCircle(lerp(200, 660, u), 600 - 170 * math.sin(math.pi * u), 9, L.P(GREY))
    fly = ease(clamp((lt - 0.2) / max(ta - 0.2, 0.3)))
    M.letter(c, lerp(200, 660, fly), 600 - 170 * math.sin(math.pi * fly), 0.95, rot=-12 + 22 * fly)
    K.show(c, lt, tm, 400, 290, lambda cc: C.chip(cc, 'MONTAG, 30.11.', 400, 290, 66, YEL, INK, angle=-3), kind='pop')
    K.show(c, lt, ta, 650, 400, lambda cc: M.check(cc, 650, 400, 1.2), kind='pop')
    K.host(c, t, mood='happy', pose='cheer' if lt >= ta else 'point_r', look=(0.4, -1))


def s6(c, t, d):                                   # Ein Brief, den du Montag einwirfst, ist zu spät.
    i, lt, ld = K.begin(c, 5, t, d, punch=['einwirfst'], shake=['spät'])
    K.stage(c, 'cream', 'red')
    tb = K.at(5, 'brief', t, lt, 0.26); tmo = K.at(5, 'montag', t, lt, 0.9); te = K.at(5, 'einwirfst', t, lt, 1.2); ts = K.at(5, 'spät', t, lt, 1.9)
    late = lt >= ts
    K.show(c, lt, 0.0, 360, 570, lambda cc: M.mailbox(cc, 360, 570, 1.2), kind='drop')
    drop = ease(clamp((lt - te + 0.05) / 0.28))    # der Brief fliegt in den Schlitz
    if lt < te + 0.25:
        sc = 1.0 - 0.55 * drop
        K.show(c, lt, tb, 780, 380, lambda cc: M.letter(cc, lerp(780, 360, drop), lerp(380, 478, drop), sc, rot=-8 + 8 * drop), kind='pop', key='brief')
        if drop < 0.05:
            K.show(c, lt, tmo, 780, 520, lambda cc: C.chip(cc, 'MONTAG', 780, 520, 70, YEL, INK, angle=5), kind='pop')
    elif lt < te + 0.6:
        L.sfx('pop', ('einwurf',)); M.ring(c, 360, 478, lt - te - 0.25, GREY)
    K.show(c, lt, ts, 590, 500, lambda cc: M.stamp(cc, 590, 500, 'ZU SPÄT', 156, RED, -8), kind='slam', snd=None)
    K.host(c, t, mood='shock' if late else 'happy', pose='both_up' if late else 'point_l', look=(0, -1),
           jump=(60 * math.exp(-(lt - ts) * 7) if late else 0))


def s7(c, t, d):                                   # Verpasst? | Dann bleibst du ein weiteres Jahr im alten Vertrag.
    i, lt, ld = K.begin(c, 6, t, d, marks=['dann'], shake=['jahr'], focus=[(540, 1150), None])
    if i == 0:                                     # Nahaufnahme FINN + Fragezeichen
        K.stage(c, 'cream', 'yel')
        K.mark(c, lt, '?', 0.05, 540, 650, 540)
        K.closeup(c, t, mood='puzzled', pose='think', lean=-4)
    else:                                          # der Vertrag wird angekettet
        K.stage(c, 'vio')
        tw = K.at(6, 'weiteres', t, lt, 0.8); tj = K.at(6, 'jahr', t, lt, 1.25); hit = lt >= tj
        K.show(c, lt, 0.0, 540, 500, lambda cc: M.doc(cc, 540, 500, 'VERTRAG', w=470, h=540, lines=5), kind='pop')
        K.slam(c, '+1 JAHR', lt, tw, 540, 470, 150, color=INK, box=YEL, rot=-4, maxw=560, snd='thud')

        def locked(cc):
            M.chain(cc, 650); M.lock(cc, 540, 640, 0.9)
        K.show(c, lt, tj, 540, 650, locked, kind='slam', snd=None)
        K.host(c, t, mood='shock' if hit else 'tired', pose='both_up' if hit else 'rest', look=(0.2, -1),
               jump=(60 * math.exp(-(lt - tj) * 7) if hit else 0))


def s8(c, t, d):                                   # Ausnahme: | Erhöht der Versicherer den Beitrag, darfst du trotzdem kündigen.
    i, lt, ld = K.begin(c, 7, t, d, marks=['erhöht'], punch=['beitrag', 'trotzdem'], focus=[(540, 1150), None])
    K.stage(c, 'cream', 'green')
    if i == 0:                                     # Nahaufnahme FINN + grünes Ausrufezeichen
        K.mark(c, lt, '!', 0.05, 540, 650, 540, fill=GREEN, rot=6)
        K.closeup(c, t, mood='happy', pose='up', lean=4, look=(0, -0.8))
    else:                                          # Beitrag steigt -> kündigen ist trotzdem erlaubt
        tb = K.at(7, 'beitrag', t, lt, 1.1); td = K.at(7, 'darfst', t, lt, 1.7); tt = K.at(7, 'trotzdem', t, lt, 2.0)
        ok = lt >= tt
        ay = 400 - 36 * ease_out(clamp((lt - 0.12) / 0.5))                       # der Pfeil schiebt sich hoch
        K.show(c, lt, 0.0, 280, 500, lambda cc: M.invoice(cc, 280, 500, 1.25, title='BEITRAG'), kind='left')
        K.show(c, lt, 0.12, 580, ay, lambda cc: M.arrow_up(cc, 580, ay, 1.25), kind='pop', key='pfeil')
        K.show(c, lt, tb, 330, 640, lambda cc: C.chip(cc, 'TEURER', 330, 640, 78, RED, WHITE, angle=-5), kind='pop')
        K.show(c, lt, td, 780, 690, lambda cc: M.button(cc, 780, 690, 420, 128, label='Kündigen', fill=GREEN if ok else WHITE), kind='right')
        K.show(c, lt, tt, 950, 622, lambda cc: M.check(cc, 950, 622, 1.0), kind='pop')
        K.host(c, t, mood='happy', pose='cheer' if ok else 'up', look=(0.3, -1))


def s9(c, t, d):                                   # Deinen Stichtag findest du im Versicherungsschein.
    i, lt, ld = K.begin(c, 8, t, d, punch=['versicherungsschein'])
    K.stage(c, 'cream', 'vio')
    tv = K.at(8, 'versicherungsschein', t, lt, 1.4)
    found = ease(clamp((lt - tv + 0.25) / 0.3))    # die Lupe findet die markierte Zeile
    K.show(c, lt, 0.0, 480, 520, lambda cc: M.doc(cc, 480, 520, 'DEIN VERTRAG', hl=2, hl_text='STICHTAG', w=520, h=540), kind='drop')
    wx, wy = 480 + 150 * math.sin(lt * 4.4), 430 + 110 * math.sin(lt * 5.7 + 1)
    mx, my = lerp(wx, 700, found), lerp(wy, 545, found)
    K.show(c, lt, 0.3, mx, my, lambda cc: M.magnifier(cc, mx, my, 105), kind='pop', key='lupe')
    K.host(c, t, mood='happy', pose='point_r' if lt >= tv else 'think', look=(0.3, -1))


def s10(c, t, d):                                  # Schick das jemandem mit Auto, | und sag ihm:
    i, lt, ld = K.begin(c, 9, t, d, marks=['und'], focus=(540, 700))
    if i == 0:                                     # Chat: Video verschickt -> Antwort tippt -> „OHA!“
        K.stage(c, 'cream', 'blue')
        t1 = K.at(9, 'schick', t, lt, 0.1); t2 = K.at(9, 'jemandem', t, lt, 0.45); t3 = K.at(9, 'auto', t, lt, 1.0)
        M.chat(c, lt, t1, t2, t3, reply='OHA!')
        fly = clamp((lt - t1) / 0.8)
        if 0 < fly < 1:
            L.sfx('swipe', ('plane',))
            M.plane(c, lerp(760, 1010, ease(fly)), lerp(400, 250, ease(fly)), 1.15, a=int(255 * (1 - fly)))
        K.host(c, t, mood='happy', pose='cheer' if lt >= t3 else 'point_r', look=(0, 0) if lt >= t3 else (0.3, -1))
    else:                                          # zurück ins Startbild – der Satz läuft in den Hook
        opening(c, lt, t, loop=True)


SCENES = [s1, s2, s3, s4, s5, s6, s7, s8, s9, s10]
