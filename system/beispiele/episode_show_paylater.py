"""Episode 25.11. 11:30: „Später bezahlen“ ist seit 20.11.2026 ein Kredit – PayPal fragt nach dem Einkommen.
Stil: FINN-Show (LOOK cartoon + KINO-Schnitt-Engine), Viral-Aufbau V3 mit Loop. VORLAGE für alle neuen Videos.

Aufbau jeder Szene:  i, lt, ld = K.begin(...)  ->  K.stage(...)  ->  Motive mit K.show/K.slam genau auf dem Wort  ->  K.host(...)
Regeln, die dieses Video vormacht:
  - Bild 0 ist fertig (Hook-Zeilen, Motiv, FINN) und bewegt sich sofort (Zeiger klickt auf „später“).
  - Nie länger als ca. 1 Sekunde ohne neues Ereignis auf der Bühne (Auftritt, Klick, Stempel, Zähler, Schnitt).
  - Höhepunkte (Zahl, Stempel) bekommen shake=[Wort]; betonte Wörter punch=[Wort]; Bindewörter eine Nahaufnahme (K.closeup + K.mark).
  - Letzte Einstellung = opening(loop=True): das Schlussbild ist das Startbild, der letzte Satz läuft in den Hook.
"""
import math
import render as L
import cartoon as C
import kino as K
import motive as M          # fertige Sticker-Motive (Knopf, Zeiger, Stempel, Kalender, Anzeige, Handy-Chat …)
from render import clamp, ease, ease_out, lerp
from cartoon import INK, VIO, YEL, RED, GREEN, WHITE, GREY

EDIT = 2
LOOK = 'cartoon'
KINO = True
LOOP = True
TOPIC = ''
HOOK_TEXT = 'x'                 # Platzhalter: hält die Untertitel bis HOOK_END zurück – der Hook steht als K.slam im Bild
HOOK_END = 3.26
HIGHLIGHT = ['Einkommen.', 'Kredit.', '20.', 'Kreditrecht.', 'prüfen,', '200', 'abgelehnt.', 'Ausnahme:', 'Black', 'Friday.', 'Schick']
FADE_COL = ['#000000'] * 10
# Blenden an den Satzgrenzen (Szene n beginnt mit …) – 7 = harter Schnitt, damit der Stempel „ABGELEHNT“ lange genug steht
K.SCENE_TRANS = {1: 'ink', 2: 'whip', 3: 'zoom', 4: 'ink', 5: 'whip', 6: 'zoom', 7: 'cut', 8: 'whip', 9: 'zoom'}
# Schnitte im Satz sind harte Schnitte ('cut'); Ausnahmen: Hook (Blitz), Sprung auf die Zahl (Zoom), Rückweg in den Hook (Tinte)
K.SHOT_TRANS = {(0, 1): 'snap', (2, 1): 'whip', (4, 1): 'zoom', (9, 1): 'ink'}


# ---------------------------------------------------------------- Hook (Startbild = Schlussbild)
def opening(c, lt, t, loop=False):
    """Bild 0: gelbe Strahlen, Hook-Zeilen stehen sofort, der „Später bezahlen“-Knopf wird genau auf „später“ geklickt
    (wird dunkel = gewählt), FINN groß und spricht. loop=True: Schlussbild (ruhiger Anfangszustand, damit der Loop sitzt)."""
    K.stage(c, 'yel')
    tp = 99.0 if loop else K.at(0, 'später', t, lt, 0.5)
    u = lt - tp
    press = clamp(1 - abs(u - 0.07) / 0.09)
    k0 = 1.0 if (loop or L.SAFE_CHECK) else 1 + 0.2 * math.exp(-lt * 13)               # Zeilen „setzen sich“ in den ersten Bildern
    k1 = k0 * (1 + (0.2 * math.exp(-u * 12) if u >= 0 else 0))                            # zweite Zeile zuckt beim Wort
    c.save(); c.translate(540, 310); c.scale(k0, k0); c.translate(-540, -310)
    K.slam(c, 'DU ZAHLST', lt, -9, 540, 325, 150, rot=-3, snd=None)
    c.restore()
    c.save(); c.translate(540, 480); c.scale(k1, k1); c.translate(-540, -480)
    K.slam(c, 'SPÄTER?', lt, -9, 540, 512, 160, color=WHITE, box=VIO, rot=2, snd=None)
    c.restore()
    chosen = u >= 0.07                                                                   # nach dem Klick ist der Knopf „gewählt“ (dunkel)
    M.button(c, 540, 700, h=140, press=press, fill=INK if chosen else WHITE, txt=WHITE if chosen else INK)   # endet bei y 784 – das Untertitel-Band (ab 818) bleibt frei
    if u >= 0:
        L.sfx('pop', ('klick',)); M.ring(c, 705, 722, u)
    q = ease_out(clamp(lt / max(tp, 0.15))) if not loop else 0.0
    M.cursor(c, lerp(905, 700, q), lerp(880, 718, q), 1.25)
    K.host(c, t, mood='happy', pose='up', x=500, y=1350, s=1.95, look=(0.5, -0.8))


def hook2(c, lt, t):
    """„PayPal fragt jetzt nach deinem Einkommen.“ – violett, das Eingabefeld fällt rein, die Frage knallt drüber, FINN erschrickt."""
    K.stage(c, 'vio')
    te = K.at(0, 'einkommen', t, lt, 1.3)
    hit = lt >= te
    K.slam(c, 'PAYPAL FRAGT:', lt, 0.0, 540, 325, 118, rot=-3, snd=None)
    K.show(c, lt, 0.22, 540, 705, lambda cc: M.field(cc, 540, 705), kind='drop')
    K.slam(c, 'DEIN EINKOMMEN?', lt, te, 540, 520, 124, color=INK, box=YEL, rot=2, snd=None)
    K.host(c, t, mood='shock' if hit else 'puzzled', pose='both_up' if hit else 'hips', x=500, y=1350, s=1.95,
           look=(0.2, -0.8), jump=(70 * math.exp(-(lt - te) * 7) if hit else 0))


# ---------------------------------------------------------------- Szenen
def s1(c, t, d):
    i, lt, ld = K.begin(c, 0, t, d, marks=['paypal'], shake=['einkommen'], focus=(540, 700))
    opening(c, lt, t) if i == 0 else hook2(c, lt, t)


def s2(c, t, d):                                   # Der Grund: | Seit dem 20. November ist „Später bezahlen“ ein Kredit.
    i, lt, ld = K.begin(c, 1, t, d, marks=['seit'], punch=['20'], shake=['kredit'], focus=[(540, 1150), None])
    if i == 0:                                     # Nahaufnahme FINN (Bindewort) + riesiges Fragezeichen
        K.stage(c, 'cream', 'yel')
        K.mark(c, lt, '?', 0.05, 540, 650, 540)
        K.closeup(c, t, mood='puzzled', pose='think', lean=-4)
    else:
        K.stage(c, 'cream', 'red')
        t20 = K.at(1, '20', t, lt, 0.4); tb = K.at(1, 'später', t, lt, 1.5); tk = K.at(1, 'kredit', t, lt, 2.5); hit = lt >= tk
        u20 = lt - t20 - 0.06                                                   # das Blatt springt genau auf „20.“ von 19 auf 20
        if u20 >= 0:
            L.sfx('pop', ('blatt',))
        day, sq = ('20', clamp(u20 / 0.07)) if u20 >= 0 else ('19', clamp(-u20 / 0.07))
        mv = ease(clamp((lt - tb + 0.10) / 0.30))                               # Platz machen, wenn der Knopf kommt
        cx, cs = lerp(540, 280, mv), lerp(1.22, 1.0, mv)
        K.show(c, lt, 0.0, 540, 520, lambda cc: M.calendar(cc, cx, 520, cs, day, 'NOVEMBER', sq, INK if day == '20' else '#b9b3cc'), kind='pop')
        K.show(c, lt, tb, 735, 450, lambda cc: M.button(cc, 735, 450, 470, 122), kind='right')
        K.show(c, lt, tk, 715, 610, lambda cc: M.stamp(cc, 715, 610, 'KREDIT!', 104), kind='slam', snd=None)
        K.host(c, t, mood='shock' if hit else 'happy', pose='both_up' if hit else 'up', look=(0.4, -1),
               jump=(60 * math.exp(-(lt - tk) * 7) if hit else 0))


def s3(c, t, d):                                   # So steht es im neuen Kreditrecht. | Es gilt für Klarna, PayPal und Co.
    i, lt, ld = K.begin(c, 2, t, d, marks=['gilt'], punch=['kreditrecht'])
    if i == 0:
        K.stage(c, 'cream', 'vio')
        K.show(c, lt, 0.0, 540, 520, lambda cc: M.paper(cc, 540, 520), kind='drop')
        K.show(c, lt, K.at(2, 'neuen', t, lt, 0.7), 830, 290, lambda cc: M.burst(cc, 830, 290, 120, YEL, 'NEU'), kind='pop')
        K.host(c, t, mood='happy', pose='up', look=(0.3, -1))
    else:
        K.stage(c, 'cream', 'blue')
        K.show(c, lt, 0.0, 540, 330, lambda cc: M.button(cc, 540, 330, 700, 140), kind='drop')
        for k, (w, lab, x, y, r, kind) in enumerate([('klarna', 'KLARNA', 300, 560, -4, 'left'), ('paypal', 'PAYPAL', 770, 560, 4, 'right'),
                                                     ('co', '& CO.', 540, 725, -2, 'pop')]):
            K.show(c, lt, K.at(2, w, t, lt, 0.4 + k * 0.5), x, y,
                   lambda cc, lab=lab, x=x, y=y, r=r: C.chip(cc, lab, x, y, 88, WHITE, INK, angle=r), kind=kind)
        K.host(c, t, mood='happy', pose='point_r', look=(0.5, -1))


def s4(c, t, d):                                   # Sie müssen vorher prüfen, | ob du dir das leisten kannst.
    i, lt, ld = K.begin(c, 3, t, d, marks=['ob'], step=['prüfen'], punch=['leisten'])
    K.stage(c, 'cream', 'green')
    if i == 0:
        K.show(c, lt, 0.0, 540, 570, lambda cc: M.wallet(cc, 540, 570, 1.25), kind='pop')
        mx = lerp(270, 760, 0.5 + 0.5 * math.sin(lt * 4.2 - 1.2)); my = 500 + 40 * math.sin(lt * 6.1)
        K.show(c, lt, 0.12, mx, my, lambda cc: M.magnifier(cc, mx, my), kind='pop', key='lupe')
        K.host(c, t, mood='puzzled', pose='hips', look=(0.4, -1))
    else:
        tl = K.at(3, 'leisten', t, lt, 0.6)
        v = 0.5 + 0.42 * math.sin(lt * 7.5) * math.exp(-max(0.0, lt - tl) * 3)
        K.show(c, lt, 0.0, 540, 660, lambda cc: M.gauge(cc, 540, 660, 300, v), kind='pop')
        K.host(c, t, mood='puzzled', pose='shrug', look=(0.3, -1))


def s5(c, t, d):                                   # Auch bei kleinen Beträgen | unter 200 Euro.
    i, lt, ld = K.begin(c, 4, t, d, marks=['unter'], shake=['200'])
    K.stage(c, 'vio')
    if i == 0:
        K.show(c, lt, 0.0, 540, 560, lambda cc: M.bag(cc, 540, 560 + K.wig(8, 1.4), 1.2), kind='drop')
        K.host(c, t, mood='happy', pose='up', look=(0.3, -1))
    else:
        t2 = K.at(4, '200', t, lt, 0.4); hit = lt >= t2
        K.slam(c, 'UNTER', lt, 0.0, 540, 360, 120, rot=-3, snd='pop')
        K.slam(c, '200 €', lt, t2, 540, 640, 250, color=INK, box=YEL, rot=2, snd=None)
        K.host(c, t, mood='shock' if hit else 'puzzled', pose='both_up' if hit else 'hips', look=(0.2, -1),
               jump=(60 * math.exp(-(lt - t2) * 7) if hit else 0))


def s6(c, t, d):                                   # Dafür zählen Einkommen, Ausgaben und offene Raten.
    i, lt, ld = K.begin(c, 5, t, d, punch=['einkommen', 'ausgaben', 'offene'])
    K.stage(c, 'cream', 'yel')
    K.show(c, lt, 0.0, 540, 520, lambda cc: M.slots(cc, 'DER CHECK'), kind='drop')
    for w, x, colr, kind in [('einkommen', 262, GREEN, 'plus'), ('ausgaben', 540, RED, 'minus'), ('offene', 818, YEL, 'raten')]:
        K.show(c, lt, K.at(5, w, t, lt, 1.0), x, 560,
               lambda cc, x=x, colr=colr, kind=kind: M.tile(cc, x, 560, 118, colr, kind), kind='pop')
    K.host(c, t, mood='happy', pose='up' if lt > 0.55 else 'hips', look=(0.2, -1))


def s7(c, t, d):                                   # Fällst du durch, | wird „Später bezahlen“ abgelehnt.
    i, lt, ld = K.begin(c, 6, t, d, marks=['wird'], shake=['abgelehnt'])
    K.stage(c, 'cream', 'red')
    if i == 0:
        v = 0.5 - 0.42 * ease_out(clamp(lt / 0.45)) + 0.03 * math.sin(lt * 30) * math.exp(-lt * 5)
        M.gauge(c, 540, 660, 300, v)
        K.host(c, t, mood='tired', pose='rest', look=(0.3, -1))
    else:                                          # der Zeiger klickt auf „bezahlen“ – dann knallt der Stempel drauf
        tc = K.at(6, 'bezahlen', t, lt, 0.55); ta = K.at(6, 'abgelehnt', t, lt, 0.9); no = lt >= ta
        uc = lt - tc
        M.button(c, 540, 440, fill=GREY if no else WHITE, txt='#8a84a0' if no else INK, press=clamp(1 - abs(uc - 0.05) / 0.08))
        if uc >= 0:
            L.sfx('pop', ('klick7',)); M.ring(c, 706, 462, uc)
        q = ease_out(clamp(lt / max(tc, 0.2)))
        M.cursor(c, lerp(935, 700, q), lerp(690, 458, q), 1.2)
        K.show(c, lt, ta, 540, 640, lambda cc: M.stamp(cc, 540, 640, 'ABGELEHNT', 128, RED, -8), kind='slam', snd=None)   # Stempel sitzt auf der Unterkante des Knopfs
        K.host(c, t, mood='shock' if no else 'puzzled', pose='both_up' if no else 'up', look=(0.2, -1),
               jump=(60 * math.exp(-(lt - ta) * 7) if no else 0))


def s8(c, t, d):                                   # Ausnahme: | Der Shop selbst gibt dir ein kurzes Zahlungsziel.
    i, lt, ld = K.begin(c, 7, t, d, marks=['der'], punch=['zahlungsziel'], focus=[(540, 1150), None])
    K.stage(c, 'cream', 'green')
    if i == 0:                                     # Nahaufnahme FINN (Bindewort) + riesiges Ausrufezeichen
        K.mark(c, lt, '!', 0.05, 540, 650, 540, fill=GREEN, rot=6)
        K.closeup(c, t, mood='happy', pose='up', lean=4, look=(0, -0.8))
    else:
        K.show(c, lt, 0.0, 310, 560, lambda cc: M.shop(cc, 310, 560, 1.3), kind='left')
        K.show(c, lt, K.at(7, 'gibt', t, lt, 0.7), 770, 530, lambda cc: M.invoice(cc, 770, 530, 1.12), kind='right')
        K.show(c, lt, K.at(7, 'zahlungsziel', t, lt, 1.5), 915, 335, lambda cc: M.check(cc, 915, 335, 1.15), kind='pop')
        K.host(c, t, mood='happy', pose='up', look=(0.3, -1))


def s9(c, t, d):                                   # Und am 27. November ist | Black Friday.
    i, lt, ld = K.begin(c, 8, t, d, marks=['black'], punch=['27'], shake=['black'])
    if i == 0:                                     # das Blatt vom 20. blättert hoch bis zum 27.
        K.stage(c, 'cream', 'vio')
        day = str(int(round(K.count(lt, 0.30, 20, 27, 0.5, key='tage'))))
        K.show(c, lt, 0.0, 540, 520, lambda cc: M.calendar(cc, 540, 520, 1.25, day, 'NOVEMBER'), kind='drop')
        K.host(c, t, mood='happy', pose='up', look=(0.2, -1))
    else:
        K.stage(c, 'yel')
        tb = K.at(8, 'black', t, lt, 0.06)
        K.show(c, lt, tb, 540, 500, lambda cc: M.tag(cc, 540, 500, 900, 320, INK, 'BLACK FRIDAY', WHITE, -5, 112), kind='slam', snd=None)
        for k, (x, y) in enumerate([(200, 262), (860, 268), (830, 740), (240, 735)]):
            K.show(c, lt, tb + 0.12 + k * 0.07, x, y,
                   lambda cc, x=x, y=y, k=k: C.chip(cc, '%', x, y + K.wig(8, 1.5, k), 104, RED, WHITE, angle=-10 + k * 7), kind='pop')
        K.host(c, t, mood='shock', pose='both_up', look=(0, -1), jump=60 * math.exp(-max(0.0, lt - tb) * 7))


def s10(c, t, d):                                  # Schick das jemandem, der immer später bezahlt, | und sag ihm:
    i, lt, ld = K.begin(c, 9, t, d, marks=['und'], punch=['immer'], focus=(540, 700))
    if i == 0:                                     # Chat: Video verschickt -> Antwort tippt -> „WAS?!“
        K.stage(c, 'cream', 'blue')
        t1 = K.at(9, 'schick', t, lt, 0.12); t2 = K.at(9, 'jemandem', t, lt, 0.55); t3 = K.at(9, 'immer', t, lt, 1.2)
        M.chat(c, lt, t1, t2, t3)
        fly = clamp((lt - t1) / 0.8)
        if 0 < fly < 1:
            L.sfx('swipe', ('plane',))
            M.plane(c, lerp(760, 1010, ease(fly)), lerp(400, 250, ease(fly)), 1.15, a=int(255 * (1 - fly)))
        K.host(c, t, mood='happy', pose='cheer' if lt >= t3 else 'point_r', look=(0, 0) if lt >= t3 else (0.3, -1))
    else:                                          # zurück ins Startbild – der Satz läuft in den Hook
        opening(c, lt, t, loop=True)


SCENES = [s1, s2, s3, s4, s5, s6, s7, s8, s9, s10]
