# Redesign-Labor 28.11.2026 – drei Test-Looks ohne Maskottchen

**Nicht Teil der Produktion.** Die täglichen Läufe benutzen weiter `system/WORKFLOW.md` und `system/lib/`.
Dieser Ordner hält nur die drei 10-Sekunden-Testclips fest, bis Lukas einen Look gewählt hat.

Gleiches Thema (Gutschein, Kleingedruckt #4), gleiche Jesco-Aufnahme (`audio/voice_raw.mp3`, eine Aufnahme,
Pause nach dem Hook gekürzt), gleiche Musik („Chill Wave“), 1080×1920, 30 fps, 10,0 s.

| Datei | Look | Kurz |
|---|---|---|
| `look_klar.py` | 1 KLAR | helle, präzise Flach-Infografik: Linien, wenig Farbe, Rot als Akzent, Untertitel in dunkler Pille |
| `look_mini.py` | 2 MINIATUR | kleine 3D-Welt (eigener Mini-3D-Zeichner), Petrol-Grund, Licht und Schatten, langsame Kamerafahrt |
| `look_kino.py` | 3 KINO | dunkle Bühne, ein Lichtkegel, Hauptobjekt mit Perspektive, Serifenschrift |
| `core.py` | – | gemeinsamer Kern: Schriften, Easing, Untertitel, Rendern, Ton |

Bauen: `python3 look_klar.py render` (ebenso `look_mini.py`, `look_kino.py`) → `out/LOOK*.mp4`.
Vorschau: `python3 look_mini.py sheet` (Kontaktbogen) oder `big 0 1.85 4.6 9.9` (große Einzelbilder).

Braucht: python3, skia-python, numpy, ffmpeg und die Schrift Inter Display (Paket `fonts-inter`, liegt unter
`/usr/share/fonts/opentype/inter/`; alternativ nach `fonts/inter/` legen). Die übrigen Schriften liegen in `fonts/`
(IBM Plex Mono, Instrument Serif, DM Serif Display, Barlow Condensed – alle SIL Open Font License, Quelle github.com/google/fonts).

Fakten im Clip (Verbraucherzentrale): Gutscheine verjähren grundsätzlich nach drei Jahren; die Frist beginnt am Ende
des Jahres, in dem der Gutschein gekauft wurde (Kauf 03/2023 → einlösbar bis 31.12.2026).

Regeln, die alle drei Looks einhalten: kein Maskottchen, kein Gelb als Hauptfarbe, wenig Text, ruhiger Hook,
kein gesprochener Serien-Vorspann (Reihe nur als Kopfzeile), das Bild hüpft und wackelt nicht.
