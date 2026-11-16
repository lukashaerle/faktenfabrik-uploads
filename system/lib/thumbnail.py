"""FAKTENFABRIK Thumbnail-Baukasten (Titelbild für TikTok, Instagram, YouTube).

Stil (von Lukas freigegeben, Vorlage: beispiele/thumb_baertierchen.py):
  - Hintergrund passend zum Thema (Weltall, Meer, Labor, Körper, Küche ...)
  - Hauptfigur/Hauptobjekt AUS DEM VIDEO groß in der Mitte (Ausschnitt aus einem Standbild)
  - FINN aus dem Video unten links, reagiert (Sprechblase "WAS?!", "WIE BITTE?!" ...)
  - Weißer Marken-Pill "FAKTENFABRIK" oben
  - Headline 2 Zeilen, Poppins 900, dicke Navy-Kontur: Zeile 1 weiß, Zeile 2 gelb
  - Weißer Pill mit kurzem Nachsatz ("…ohne Raumanzug!")
  - Alles Wichtige zwischen y=330 und y=1600 (Instagram-Raster 4:5 und TikTok-Profil 3:4 schneiden oben/unten ab)

Benutzung im Episodenordner (siehe WORKFLOW.md, Schritt 9b):
  python3 ../lib/pipeline.py still <szene> <sek>     -> Standbild mit Hauptobjekt / FINN
  thumb.py schreiben (Vorlage beispiele/thumb_baertierchen.py), ausführen -> thumb.png + thumb_vorschau.png
  thumb.png wird als YouTube-Thumbnail (thumbnailImageId) genutzt und Lukas zur Freigabe gezeigt.
  prepend() NICHT benutzen: Lukas will kein Standbild vor dem Video.
"""
import os, sys, random, subprocess, json
from PIL import Image, ImageDraw, ImageFont, ImageFilter

LIB = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1920
NAVY = (18, 26, 58)
YEL = (255, 204, 41)
WHITE = (255, 255, 255)


def font(size, weight=900):
    return ImageFont.truetype(os.path.join(LIB, f'Poppins-{weight}.ttf'), size)


# ---------------------------------------------------------------- Hintergründe
def gradient(stops, size=(W, H)):
    """stops = [(0.0,(r,g,b)), (0.6,(r,g,b)), (1.0,(r,g,b))] -> RGBA-Bild."""
    w, h = size
    im = Image.new('RGB', size); d = ImageDraw.Draw(im)
    for y in range(h):
        t = y / h
        for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
            if p0 <= t <= p1:
                k = (t - p0) / max(p1 - p0, 1e-6)
                d.line([(0, y), (w, y)], fill=tuple(int(c0[i] + (c1[i] - c0[i]) * k) for i in range(3)))
                break
    return im.convert('RGBA')


def glow(im, box, color=(120, 90, 255, 90), blur=120):
    g = Image.new('RGBA', im.size, (0, 0, 0, 0))
    ImageDraw.Draw(g).ellipse(box, fill=color)
    return Image.alpha_composite(im, g.filter(ImageFilter.GaussianBlur(blur)))


def stars(im, n=260, seed=7):
    d = ImageDraw.Draw(im); random.seed(seed)
    for _ in range(n):
        x, y = random.randint(0, W), random.randint(0, H)
        r = random.choice([1, 1, 1, 2, 2, 3])
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, random.randint(120, 255)))
    return im


def bubbles(im, n=40, seed=3):
    d = ImageDraw.Draw(im); random.seed(seed)
    for _ in range(n):
        x, y, r = random.randint(0, W), random.randint(0, H), random.randint(6, 26)
        d.ellipse([x - r, y - r, x + r, y + r], outline=(255, 255, 255, random.randint(60, 140)), width=3)
    return im


def rays(im, alpha=45):
    """Lichtstrahlen von oben (Meer, Bühne)."""
    r = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(r)
    for x in range(-200, W + 200, 170):
        d.polygon([(x, 0), (x + 70, 0), (x + 260, H), (x + 120, H)], fill=(255, 255, 255, alpha))
    return Image.alpha_composite(im, r.filter(ImageFilter.GaussianBlur(25)))


def sunburst(im, center=(W // 2, 1050), color=(255, 255, 255, 28), n=24):
    r = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(r)
    import math
    for i in range(n):
        a0 = 2 * math.pi * i / n; a1 = a0 + math.pi / n
        L = 2500
        d.polygon([center, (center[0] + L * math.cos(a0), center[1] + L * math.sin(a0)),
                   (center[0] + L * math.cos(a1), center[1] + L * math.sin(a1))], fill=color)
    return Image.alpha_composite(im, r)


def planet_arc(im, top=1640, R=1300, ocean=(30, 110, 200), land=(52, 140, 96), atmo=(90, 180, 255, 160)):
    """Erdbogen am unteren Rand (Weltall-Themen)."""
    cx, cy = W // 2, top + R
    a = Image.new('RGBA', im.size, (0, 0, 0, 0))
    ImageDraw.Draw(a).ellipse([cx - R - 40, cy - R - 40, cx + R + 40, cy + R + 40], fill=atmo)
    im = Image.alpha_composite(im, a.filter(ImageFilter.GaussianBlur(30)))
    m = Image.new('L', im.size, 0); ImageDraw.Draw(m).ellipse([cx - R, cy - R, cx + R, cy + R], fill=255)
    e = Image.new('RGBA', im.size, (0, 0, 0, 0)); ed = ImageDraw.Draw(e)
    ed.ellipse([cx - R, cy - R, cx + R, cy + R], fill=ocean + (255,))
    for (x, y, w, h) in [(120, top + 60, 260, 90), (520, top + 20, 340, 120), (880, top + 80, 200, 80), (300, top + 160, 200, 70)]:
        ed.ellipse([x, y, x + w, y + h], fill=land + (255,))
    e.putalpha(Image.composite(e.getchannel('A'), Image.new('L', im.size, 0), m))
    im = Image.alpha_composite(im, e)
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
    for yy in range(top, H):
        sd.line([(0, yy), (W, yy)], fill=(0, 0, 30, int(150 * (yy - top) / (H - top))))
    sh.putalpha(Image.composite(sh.getchannel('A'), Image.new('L', im.size, 0), m))
    return Image.alpha_composite(im, sh)


def floor(im, y=1600, color=(20, 30, 60, 200)):
    f = Image.new('RGBA', im.size, (0, 0, 0, 0))
    ImageDraw.Draw(f).rectangle([0, y, W, H], fill=color)
    return Image.alpha_composite(im, f.filter(ImageFilter.GaussianBlur(8)))


# ------------------------------------------------------ Ausschnitte aus Standbildern
def cutout(frame_path, box, out=None, thr=38, extra_seeds=()):
    """Figur/Objekt aus einem Standbild ausschneiden: Hintergrund wird von den Rändern
    der box per Flood-Fill entfernt. box = (x0, y0, x1, y1) im 1080x1920-Bild.
    Gibt RGBA zurück. Ergebnis immer ansehen; bei Resten thr erhöhen (bis ~60) oder
    die box enger setzen; frisst es in die Figur, thr senken."""
    fr = Image.open(frame_path).convert('RGB')
    c = fr.crop(box).copy(); w, h = c.size; key = (255, 0, 255)
    seeds = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1), (w // 2, 0), (w // 2, h - 1),
             (0, h // 2), (w - 1, h // 2), (w // 4, 0), (3 * w // 4, 0), (w // 4, h - 1), (3 * w // 4, h - 1)]
    for p in list(seeds) + list(extra_seeds):
        if c.getpixel(p) != key:
            ImageDraw.floodfill(c, p, key, thresh=thr)
    m = Image.new('L', (w, h), 0); mp = m.load(); cp = c.load()
    for y in range(h):
        for x in range(w):
            if cp[x, y] != key:
                mp[x, y] = 255
    alpha = m.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1))
    res = fr.crop(box).convert('RGBA'); res.putalpha(alpha)
    bb = alpha.getbbox()
    if bb:
        res = res.crop(bb)
    if out:
        res.save(out)
    return res


def place(im, sprite, xy, scale=1.0, rotate=0, flip=False, halo=None, halo_size=25):
    """sprite (RGBA oder Pfad) einsetzen. halo=(r,g,b) für Leuchtrand."""
    s = Image.open(sprite).convert('RGBA') if isinstance(sprite, str) else sprite
    if scale != 1.0:
        s = s.resize((int(s.width * scale), int(s.height * scale)), Image.LANCZOS)
    if flip:
        s = s.transpose(Image.FLIP_LEFT_RIGHT)
    if rotate:
        s = s.rotate(rotate, expand=True, resample=Image.BICUBIC)
    layer = Image.new('RGBA', im.size, (0, 0, 0, 0))
    if halo:
        h = Image.new('RGBA', s.size, halo + (255,))
        h.putalpha(s.getchannel('A').filter(ImageFilter.MaxFilter(halo_size | 1)).filter(ImageFilter.GaussianBlur(18)))
        layer.paste(h, xy, h)
    layer.paste(s, xy, s)
    return Image.alpha_composite(im, layer), s.size


# ------------------------------------------------------------------ Texte
def brand(im, y=318):
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([W // 2 - 190, y, W // 2 + 190, y + 64], radius=32, fill=(255, 255, 255, 235))
    d.text((W // 2, y + 33), "FAKTENFABRIK", font=font(34, 800), fill=NAVY, anchor="mm")
    return im


def fit_size(txt, size, maxw=1000, weight=900, stroke=14):
    while size > 40 and font(size, weight).getlength(txt) + 2 * stroke > maxw:
        size -= 4
    return size


def headline(im, line1, line2, y1=500, y2=655, size1=168, size2=128, color1=WHITE, color2=YEL):
    """2-zeilige Headline, Größen werden automatisch verkleinert, falls zu breit."""
    d = ImageDraw.Draw(im)
    for y, txt, s, col in [(y1, line1, size1, color1), (y2, line2, size2, color2)]:
        if txt:
            s = fit_size(txt, s)
            d.text((W // 2, y), txt, font=font(s), fill=col, anchor="mm", stroke_width=14, stroke_fill=NAVY)
    return im


def subpill(im, txt, y=742, size=52):
    d = ImageDraw.Draw(im)
    size = fit_size(txt, size, maxw=900, weight=800, stroke=0)
    w = int(font(size, 800).getlength(txt)) + 90
    d.rounded_rectangle([W // 2 - w // 2, y, W // 2 + w // 2, y + 90], radius=45, fill=WHITE, outline=NAVY, width=6)
    d.text((W // 2, y + 46), txt, font=font(size, 800), fill=NAVY, anchor="mm")
    return im


def speech(im, txt, xy=(60, 1190), tail='right'):
    """Gelbe Sprechblase mit Navy-Rand, Spitze nach unten."""
    d = ImageDraw.Draw(im); bx, by = xy
    f = font(58); w = int(f.getlength(txt)) + 70
    d.rounded_rectangle([bx, by, bx + w, by + 110], radius=55, fill=YEL, outline=NAVY, width=8)
    tx = bx + int(w * 0.6) if tail == 'right' else bx + int(w * 0.25)
    d.polygon([(tx, by + 100), (tx + 50, by + 165), (tx + 60, by + 100)], fill=YEL)
    d.line([(tx, by + 106), (tx + 50, by + 165), (tx + 60, by + 106)], fill=NAVY, width=8)
    d.text((bx + w // 2, by + 58), txt, font=f, fill=NAVY, anchor="mm")
    return im


# ------------------------------------------------------------------ Ausgabe
def save(im, path='thumb.png'):
    """Speichert thumb.png und thumb_vorschau.png (9:16, Instagram 4:5, TikTok 3:4).
    Die Vorschau IMMER ansehen: Headline, Figur und FINN müssen in allen drei Zuschnitten sichtbar sein."""
    im = im.convert('RGB'); im.save(path, optimize=True)
    sm = im.resize((360, 640))
    ig = im.crop((0, (H - 1350) // 2, W, (H - 1350) // 2 + 1350)).resize((288, 360))
    tt = im.crop((0, (H - 1440) // 2, W, (H - 1440) // 2 + 1440)).resize((270, 360))
    pv = Image.new('RGB', (1000, 700), (30, 30, 30)); pd = ImageDraw.Draw(pv)
    pv.paste(sm, (20, 45)); pv.paste(ig, (420, 45)); pv.paste(tt, (728, 45))
    lf = font(20, 800)
    pd.text((20, 12), "Vollbild 9:16", font=lf, fill='white')
    pd.text((420, 12), "Instagram-Raster 4:5", font=lf, fill='white')
    pd.text((728, 12), "TikTok-Profil 3:4", font=lf, fill='white')
    pv.save(os.path.splitext(path)[0] + '_vorschau.png')
    return path


def prepend(video, thumb, seconds=0.5):
    """Setzt das Titelbild als erste 0,5 s vor das Video (wird so zum Cover auf
    TikTok/Instagram/YouTube). Überschreibt das Video, Original bleibt als *_ohne_thumb.mp4."""
    probe = json.loads(subprocess.check_output(
        ['ffprobe', '-v', 'error', '-show_streams', '-of', 'json', video]))
    v = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    a = next((s for s in probe['streams'] if s['codec_type'] == 'audio'), None)
    fps = v.get('r_frame_rate', '30/1')
    sr = a.get('sample_rate', '44100') if a else '44100'
    base = os.path.splitext(video)[0]
    orig = base + '_ohne_thumb.mp4'
    if not os.path.exists(orig):
        os.rename(video, orig)
    fc = (f"[0:v]scale={v['width']}:{v['height']},format=yuv420p,fps={fps},setsar=1[t];"
          f"[1:v]fps={fps},format=yuv420p,setsar=1[m];"
          f"[t][2:a][m][1:a]concat=n=2:v=1:a=1[v][a]")
    cmd = ['ffmpeg', '-y', '-v', 'error',
           '-loop', '1', '-t', str(seconds), '-i', thumb,
           '-i', orig,
           '-f', 'lavfi', '-t', str(seconds), '-i', f'anullsrc=r={sr}:cl=stereo',
           '-filter_complex', fc, '-map', '[v]', '-map', '[a]',
           '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p',
           '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', video]
    subprocess.check_call(cmd)
    return video


if __name__ == '__main__':
    if len(sys.argv) >= 4 and sys.argv[1] == 'prepend':
        print(prepend(sys.argv[2], sys.argv[3]))
    else:
        print(__doc__)
