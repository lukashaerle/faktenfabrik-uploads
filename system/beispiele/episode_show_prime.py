"""Episode 25.11. 20:00: Amazon Prime – der BGH hat die Preiserhöhung von 2022 gekippt (1.10.2026, Az. III ZR 205/25);
Geld zurück gibt es nur über die Sammelklage der Verbraucherzentrale (Klageregister, kostenlos).
Stil: FINN-Show (LOOK cartoon + KINO), Viral-Aufbau V3 mit Loop. Aufbau wie beispiele/episode_show_paylater.py.
Marke nur als schlichte Schrift („AMAZON PRIME“), kein Logo, keine Markenfarben.

Besonderheit: Die EINE Aufnahme wurde umgeschnitten (keine zweite Generierung): Der Satz „Du hast zu viel Geld gezahlt.“
steht jetzt vorn (Hook endet nach 1,5 s statt 4,1 s), das zweite „2022“ ist herausgeschnitten (Szene 4: 4,6 s statt 5,9 s).
Lehre: keine Jahreszahl im Hook – „zweitausendzweiundzwanzig“ dauert allein 1,3 Sekunden.
"""
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
HOOK_END = 1.51
HIGHLIGHT = ['Prime', '2022?', 'Bundesgerichtshof', 'gekippt.', '69', '89', 'unwirksam.', '20', 'Aber:', 'nichts', 'Sammelklage', 'Klageregister', 'kostenlos.', '145.000', 'Schick']
FADE_COL = ['#000000'] * 10
# 1 = Blitz-Schnitt direkt nach dem Hook · 5 = harter Schnitt, damit der Stempel „UNWIRKSAM“ lange genug steht
K.SCENE_TRANS = {1: 'snap', 2: 'ink', 3: 'whip', 4: 'zoom', 5: 'cut', 6: 'ink', 7: 'whip', 8: 'zoom', 9: 'whip'}
K.SHOT_TRANS = {(3, 1): 'zoom', (5, 1): 'zoom', (9, 1): 'ink'}


# ---------------------------------------------------------------- Hook (Startbild = Schlussbild)
def opening(c, lt, t, loop=False):
    """Bild 0: „DU HAST ZU VIEL / GELD GEZAHLT!“ steht sofort, darunter die Preis-Karte – der Preis läuft in der ersten
    halben Sekunde von 69,00 auf 89,90 € hoch und wird rot, auf „gezahlt“ ploppt der Unterschied auf.
    loop=True: Schlussbild im Anfangszustand."""
    K.stage(c, 'yel')
    k0 = 1.0 if (loop or L.SAFE_CHECK) else 1 + 0.12 * math.exp(-lt * 13)
    c.save(); c.translate(540, 310); c.scale(k0, k0); c.translate(-540, -310)
    K.slam(c, 'DU HAST ZU VIEL', lt, -9, 540, 322, 150, rot=-3, maxw=900, snd=None)
    c.restore()
    c.save(); c.translate(540, 480); c.scale(k0, k0); c.translate(-540, -480)
    K.slam(c, 'GELD GEZAHLT!', lt, -9, 540, 508, 160, color=WHITE, box=VIO, rot=2, maxw=850, snd=None)
    c.restore()
    v = 69.0 if loop else K.count(lt, 0.15, 69.0, 89.9, 0.55, key='preis')
    high = v > 89.0
    M.pricecard(c, 540, 700, 'Prime-Abo', M.euro(v), pcol=RED if high else YEL, ptxt=WHITE if high else INK)
    if not loop:
        K.show(c, lt, K.at(0, 'gezahlt', t, lt, 0.95), 925, 836, lambda cc: M.burst(cc, 925, 836, 106, RED, '+20,90', WHITE), kind='pop')
    K.host(c, t, mood='happy', pose='up', x=500, y=1350, s=1.95, look=(0.5, -0.8))


# ---------------------------------------------------------------- Szenen
def s1(c, t, d):                                   # Du hast zu viel Geld gezahlt.
    i, lt, ld = K.begin(c, 0, t, d, shake=['geld'], focus=(540, 700))
    opening(c, lt, t)


def s2(c, t, d):                                   # Prime vor September 2022?
    i, lt, ld = K.begin(c, 1, t, d, punch=['september', '2022'])
    K.stage(c, 'vio')
    ts = K.at(1, 'september', t, lt, 0.66); ty = K.at(1, '2022', t, lt, 1.09)
    K.slam(c, 'PRIME SCHON VOR', lt, 0.0, 540, 318, 124, rot=-3, snd=None)
    yr = int(round(K.count(lt, ty, 2026, 2022, 0.8, key='jahr')))      # das Blatt blättert zurück bis 2022
    bump = 0.97 * (1 + (0.22 * math.exp(-(lt - ts) * 9) if lt >= ts else 0))
    if lt >= ts:
        L.sfx('thud', ('blatt',))
    K.show(c, lt, 0.05, 540, 582, lambda cc: M.calendar(cc, 540, 582, bump, '15', f'SEPT. {yr}'), kind='pop')
    K.show(c, lt, ty + 0.85, 870, 420, lambda cc: M.burst(cc, 870, 420, 100, YEL, '?', INK), kind='pop')
    K.host(c, t, mood='puzzled', pose='point_r' if lt >= ts else 'hips', look=(0.3, -1))


def s3(c, t, d):                                   # Der Bundesgerichtshof hat die | Preiserhöhung am 1. Oktober gekippt.
    i, lt, ld = K.begin(c, 2, t, d, marks=['preiserhöhung'], punch=['bundesgerichtshof'], shake=['gekippt'])
    if i == 0:                                     # der Hammer fällt
        K.stage(c, 'cream', 'vio')
        tb = K.at(2, 'bundesgerichtshof', t, lt, 0.26)
        hit = clamp((lt - tb - 0.25) / 0.12) - clamp((lt - tb - 0.45) / 0.25)
        K.show(c, lt, 0.0, 540, 500, lambda cc: M.gavel(cc, 520, 480, 1.35, hit), kind='drop')
        if lt >= tb + 0.37:
            L.sfx('thud', ('hammer',)); M.ring(c, 420, 650, lt - tb - 0.37, GREY)
        K.show(c, lt, tb, 540, 262, lambda cc: C.chip(cc, 'BUNDESGERICHTSHOF', 540, 262, 64, VIO, WHITE, angle=-2), kind='pop')
        K.host(c, t, mood='happy', pose='up', look=(0.2, -1))
    else:                                          # die Preis-Karte: Pfeil nach oben – „GEKIPPT“
        K.stage(c, 'cream', 'red')
        t1 = K.at(2, '1', t, lt, 0.9); tk = K.at(2, 'gekippt', t, lt, 1.6); hit = lt >= tk
        K.show(c, lt, 0.0, 540, 400, lambda cc: M.pricecard(cc, 540, 400, 'Prime-Abo', '89,90 €', pcol=GREY if hit else RED, ptxt=INK if hit else WHITE), kind='pop')
        if not hit:
            K.show(c, lt, 0.12, 860, 620, lambda cc: M.arrow_up(cc, 860, 620 + K.wig(8, 2.2), 0.9), kind='pop', key='hoch')
        K.show(c, lt, t1, 300, 262, lambda cc: C.chip(cc, '1. OKTOBER', 300, 262, 70, YEL, INK, angle=-4), kind='left')
        K.show(c, lt, tk, 540, 575, lambda cc: M.stamp(cc, 540, 575, 'GEKIPPT', 156, RED, -8), kind='slam', snd=None)   # sitzt auf der Unterkante der Karte
        K.host(c, t, mood='shock' if hit else 'happy', pose='both_up' if hit else 'point_r', look=(0.2, -1),
               jump=(60 * math.exp(-(lt - tk) * 7) if hit else 0))


def s4(c, t, d):                                   # Amazon hatte den Preis erhöht – | von 69 auf 89 Euro 90 im Jahr.
    i, lt, ld = K.begin(c, 3, t, d, marks=['von'], punch=['erhöht', '69'], shake=['89'])
    if i == 0:                                     # der Preis geht hoch
        K.stage(c, 'cream', 'blue')
        te = K.at(3, 'erhöht', t, lt, 1.1)
        rise = ease_out(clamp((lt - te + 0.1) / 0.35))
        K.show(c, lt, 0.0, 540, 640, lambda cc: M.pricecard(cc, 540, 640, 'Prime-Abo', 'teurer' if lt >= te else 'Preis', pcol=RED if lt >= te else YEL, ptxt=WHITE if lt >= te else INK), kind='drop')
        K.show(c, lt, K.at(3, 'amazon', t, lt, 0.15), 540, 262, lambda cc: C.chip(cc, 'AMAZON PRIME', 540, 262, 66, WHITE, INK, angle=-2), kind='pop')
        K.show(c, lt, te - 0.1, 540, 450, lambda cc: M.arrow_up(cc, 540, 480 - 40 * rise, 1.0), kind='pop', key='hoch')
        K.host(c, t, mood='puzzled', pose='up', look=(0.2, -1))
    else:                                          # Schlüsselzahl: 69 -> 89,90
        K.stage(c, 'vio')
        t69 = K.at(3, '69', t, lt, 0.3); t89 = K.at(3, '89', t, lt, 1.3); tj = K.at(3, 'im', t, lt, 2.6); hit = lt >= t89
        K.slam(c, '69 €', lt, t69, 540, 370, 150, rot=-3, snd='pop')
        K.slam(c, '89,90 €', lt, t89, 540, 650, 210, color=INK, box=YEL, rot=2, maxw=820, snd=None)
        K.show(c, lt, tj, 850, 762, lambda cc: C.chip(cc, 'IM JAHR', 850, 762, 54, WHITE, INK, angle=-4), kind='pop')
        K.host(c, t, mood='shock' if hit else 'puzzled', pose='both_up' if hit else 'hips', look=(0.2, -1),
               jump=(60 * math.exp(-(lt - t89) * 7) if hit else 0))


def s5(c, t, d):                                   # Doch die Klausel dafür im Kleingedruckten war unwirksam.
    i, lt, ld = K.begin(c, 4, t, d, punch=['kleingedruckten'], shake=['unwirksam'])
    K.stage(c, 'cream', 'red')
    tk = K.at(4, 'kleingedruckten', t, lt, 1.2); tu = K.at(4, 'unwirksam', t, lt, 2.1); no = lt >= tu
    found = ease(clamp((lt - tk + 0.2) / 0.3))     # die Lupe findet die Klausel
    K.show(c, lt, 0.0, 470, 520, lambda cc: M.doc(cc, 470, 520, 'AGB', hl=3 if lt >= tk - 0.05 else None, hl_text='KLAUSEL', w=520, h=540), kind='drop')
    wx, wy = 470 + 150 * math.sin(lt * 4.4), 430 + 110 * math.sin(lt * 5.7 + 1)
    mx, my = lerp(wx, 700, found), lerp(wy, 610, found)
    if not no:
        K.show(c, lt, 0.25, mx, my, lambda cc: M.magnifier(cc, mx, my, 105), kind='pop', key='lupe')
    K.show(c, lt, tu, 540, 450, lambda cc: M.stamp(cc, 540, 450, 'UNWIRKSAM', 132, RED, -8), kind='slam', snd=None)   # über der markierten Klausel
    K.host(c, t, mood='shock' if no else 'puzzled', pose='both_up' if no else 'think', look=(0.3, -1),
           jump=(60 * math.exp(-(lt - tu) * 7) if no else 0))


def s6(c, t, d):                                   # Für Jahreszahler sind das | 20 Euro 90 zu viel – jedes Jahr.
    i, lt, ld = K.begin(c, 5, t, d, marks=['20'], punch=['jedes'], shake=['20'])
    if i == 0:                                     # die Rechnung: 89,90 – 69 = ?
        K.stage(c, 'cream', 'yel')
        ts = K.at(5, 'sind', t, lt, 0.9)
        K.slam(c, '89,90 €', lt, 0.0, 600, 370, 140, rot=0, snd=None)                  # wie im Schulheft untereinander
        K.slam(c, '– 69,00 €', lt, 0.28, 566, 530, 140, rot=0, snd='pop')
        if lt >= 0.5:
            w = 640 * ease_out(clamp((lt - 0.5) / 0.25)); c.drawLine(860 - w, 582, 860, 582, L.P(INK, stroke=16))
        K.show(c, lt, ts, 540, 700, lambda cc: C.chip(cc, '= ?', 540, 700, 112, YEL, INK, angle=-2), kind='pop')
        K.host(c, t, mood='puzzled', pose='think', look=(0.2, -1))
    else:                                          # Schlüsselzahl: 20,90 € zu viel – jedes Jahr
        K.stage(c, 'vio')
        tz = K.at(5, 'zu', t, lt, 1.1); tj = K.at(5, 'jedes', t, lt, 1.9)
        K.slam(c, '20,90 €', lt, 0.06, 540, 500, 230, color=INK, box=YEL, rot=-2, maxw=860, snd=None)
        K.show(c, lt, tz, 540, 268, lambda cc: C.chip(cc, 'ZU VIEL', 540, 268, 84, RED, WHITE, angle=-3), kind='pop')
        for k, yr in enumerate(('2023', '2024', '2025', '2026')):
            K.show(c, lt, tj - 0.4 + k * 0.09, 195 + k * 230, 700, lambda cc, k=k, yr=yr: C.chip(cc, yr, 195 + k * 230, 700, 60, WHITE, INK, angle=-4 + k * 3), kind='pop')
        K.host(c, t, mood='shock', pose='both_up', look=(0.2, -1), jump=60 * math.exp(-max(0.0, lt - 0.06) * 7))


def s7(c, t, d):                                   # Aber: | Von selbst zahlt Amazon nichts zurück.
    i, lt, ld = K.begin(c, 6, t, d, marks=['von'], punch=['nichts'], focus=[(540, 1150), None])
    K.stage(c, 'cream', 'red')
    if i == 0:                                     # Nahaufnahme FINN + rotes Ausrufezeichen
        K.mark(c, lt, '!', 0.05, 540, 650, 540, fill=RED, rot=6)
        K.closeup(c, t, mood='puzzled', pose='up', lean=4, look=(0, -0.8))
    else:                                          # die Münze kommt nicht an – Kreuz drauf
        tn = K.at(6, 'nichts', t, lt, 1.3); no = lt >= tn
        K.show(c, lt, 0.0, 250, 330, lambda cc: C.chip(cc, 'AMAZON', 250, 330, 76, WHITE, INK, angle=-3), kind='left')
        K.show(c, lt, 0.0, 820, 600, lambda cc: M.wallet(cc, 820, 600, 0.95), kind='right')
        M.arc_arrow(c, 300, 420, 690, 520, 120, ease_out(clamp((lt - 0.25) / 0.6)), GREY, 14)
        if not no:
            u = ease_out(clamp((lt - 0.3) / max(tn - 0.3, 0.3))) * 0.5
            M.coin(c, (1 - u) ** 2 * 300 + 2 * (1 - u) * u * 495 + u * u * 690, (1 - u) ** 2 * 420 + 2 * (1 - u) * u * 350 + u * u * 520, 52)
        K.show(c, lt, tn, 495, 440, lambda cc: M.cross(cc, 495, 440, 1.15), kind='slam', snd='thud')
        K.host(c, t, mood='tired' if no else 'puzzled', pose='shrug' if no else 'point_r', look=(0.3, -1))


def s8(c, t, d):                                   # Dafür läuft eine Sammelklage der Verbraucherzentrale. | Trag dich ins Klageregister ein.
    i, lt, ld = K.begin(c, 7, t, d, marks=['trag'], punch=['sammelklage', 'klageregister'])
    if i == 0:                                     # viele schließen sich zusammen
        K.stage(c, 'cream', 'blue')
        tsk = K.at(7, 'sammelklage', t, lt, 0.85); tv = K.at(7, 'verbraucherzentrale', t, lt, 1.6)
        M.crowd(c, lt, 0.05, n=11, cols=6, x0=165, y0=470, dx=150, dy=180, s=1.0)
        K.show(c, lt, tsk, 540, 268, lambda cc: C.chip(cc, 'SAMMELKLAGE', 540, 268, 84, VIO, WHITE, angle=-2), kind='pop')
        K.show(c, lt, tv, 540, 770, lambda cc: C.chip(cc, 'VERBRAUCHERZENTRALE', 540, 770, 52, WHITE, INK, angle=2), kind='pop')
        K.host(c, t, mood='happy', pose='cheer' if lt >= tsk else 'up', look=(0.2, -1))
    else:                                          # eintragen: Zeiger klickt, Haken erscheint
        K.stage(c, 'cream', 'green')
        tr = K.at(7, 'klageregister', t, lt, 0.75); te = K.at(7, ('ein', 1), t, lt, 1.5); done = lt >= te
        K.show(c, lt, 0.0, 450, 520, lambda cc: M.doc(cc, 450, 520, 'KLAGEREGISTER', hl=2, hl_text='DEIN NAME' if lt >= tr else '', w=540, h=540), kind='pop')
        q = ease_out(clamp(lt / max(tr, 0.2)))
        if lt >= tr:
            L.sfx('pop', ('klick7',)); M.ring(c, 560, 530, lt - tr)
        M.cursor(c, lerp(930, 560, q), lerp(720, 530, q), 1.2)
        K.show(c, lt, te, 800, 470, lambda cc: M.check(cc, 800, 470, 1.5), kind='pop')
        K.host(c, t, mood='happy', pose='cheer' if done else 'point_r', look=(0.3, -1))


def s9(c, t, d):                                   # Das ist kostenlos. | Rund 145.000 haben es schon getan.
    i, lt, ld = K.begin(c, 8, t, d, marks=['rund'], punch=['kostenlos', 'haben'])
    if i == 0:                                     # 0 €
        K.stage(c, 'cream', 'green')
        tk = K.at(8, 'kostenlos', t, lt, 0.4)
        K.slam(c, '0 €', lt, tk, 540, 560, 260, color=INK, box=GREEN, rot=-3, snd='thud')
        K.show(c, lt, tk + 0.2, 850, 330, lambda cc: M.check(cc, 850, 330, 1.2), kind='pop')
        K.host(c, t, mood='happy', pose='cheer' if lt >= tk else 'up', look=(0.2, -1))
    else:                                          # der Zähler läuft auf 145.000, die Menge wächst
        K.stage(c, 'vio')
        tc = K.at(8, '145', t, lt, 0.35)
        v = K.count(lt, tc, 0, 145000, 1.25, key='leute')
        M.crowd(c, lt, tc, n=12, cols=6, x0=165, y0=560, dx=150, dy=150, s=0.8, stagger=0.09)
        K.slam(c, M.thousands(v), lt, tc - 0.02, 540, 400, 190, color=INK, box=YEL, rot=-2, maxw=820, snd=None)
        K.host(c, t, mood='happy', pose='both_up' if lt >= tc + 1.25 else 'up', look=(0.2, -1))


def s10(c, t, d):                                  # Schick das jemandem, der seit Jahren Prime hat, | und sag ihm:
    i, lt, ld = K.begin(c, 9, t, d, marks=['und'], punch=['jahren'], focus=(540, 700))
    if i == 0:                                     # Chat: Video verschickt -> Antwort tippt -> „WAS?!“
        K.stage(c, 'cream', 'blue')
        t1 = K.at(9, 'schick', t, lt, 0.12); t2 = K.at(9, 'jemandem', t, lt, 0.5); t3 = K.at(9, 'jahren', t, lt, 1.25)
        M.chat(c, lt, t1, t2, t3, reply='WAS?!')
        fly = clamp((lt - t1) / 0.8)
        if 0 < fly < 1:
            L.sfx('swipe', ('plane',))
            M.plane(c, lerp(760, 1010, ease(fly)), lerp(400, 250, ease(fly)), 1.15, a=int(255 * (1 - fly)))
        K.host(c, t, mood='happy', pose='cheer' if lt >= t3 else 'point_r', look=(0, 0) if lt >= t3 else (0.3, -1))
    else:                                          # zurück ins Startbild – der Satz läuft in den Hook
        opening(c, lt, t, loop=True)


SCENES = [s1, s2, s3, s4, s5, s6, s7, s8, s9, s10]
