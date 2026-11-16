"""Vorlage Titelbild (freigegeben): Bärtierchen-Folge.
Im Episodenordner als thumb.py anpassen und mit `python3 thumb.py` ausführen.
Videobezug ist Pflicht: Hauptobjekt und FINN stammen aus Standbildern DIESES Videos,
Headline greift den Hook des Videos auf."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from thumbnail import *

# 1) Ausschnitte aus Standbildern des Videos (python3 ../lib/pipeline.py still <szene> <sek>)
STILL = sys.argv[1] if len(sys.argv) > 1 else 'still_2_3.0.png'
tardi = cutout(STILL, (225, 650, 920, 1010))        # Hauptobjekt
finn_ = cutout(STILL, (20, 1530, 370, 1810))         # FINN

# 2) Hintergrund passend zum Thema (hier: Weltall)
im = gradient([(0.0, (8, 10, 32)), (0.6, (36, 22, 84)), (1.0, (14, 40, 96))])
im = stars(im)
im = glow(im, [140, 760, 940, 1360])
im = planet_arc(im)

# 3) Hauptobjekt groß in die Mitte, FINN unten links mit Sprechblase
im, (w, h) = place(im, tardi, ((W - int(tardi.width * 1.2)) // 2 + 60, 850), scale=1.2, rotate=8, halo=(255, 230, 150))
im, _ = place(im, finn_, (30, 1330), scale=1.15, flip=True)
im = speech(im, "WAS?!", (60, 1190))

# 4) Marke, Headline (2 Zeilen), Nachsatz
im = brand(im)
im = headline(im, "ÜBERLEBT", "DAS WELTALL")
im = subpill(im, "…ohne Raumanzug!")

save(im, 'thumb.png')
