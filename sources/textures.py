"""Prépare les textures d'Urantia et de la Lune pour la vue 3D, et les écrit en data: URI dans tex.json.

- jour : NASA Blue Marble Next Generation (« Whole world - land and oceans », Wikimedia Commons, domaine public) ;
- nuit : NASA, lumières des villes (« The earth at night », Wikimedia Commons, domaine public), lumières isolées ;
- nuages : IMAGE GÉNÉRÉE, illustrative (bruit fractal 3D évalué sur la sphère, avec distorsion de domaine
  et profil de nébulosité selon la latitude) ;
- Lune : NASA Scientific Visualization Studio, CGI Moon Kit (LRO), domaine public.
Usage : python -I textures.py <dossier des images> <tex.json> [aperçu-nuages.png]"""
import base64
import io
import json
import sys

import numpy as np
from PIL import Image

SRC, OUT = sys.argv[1], sys.argv[2]
PREVIEW = sys.argv[3] if len(sys.argv) > 3 else None
W, H = 2048, 1024


def uri(im, q):
    b = io.BytesIO()
    im.save(b, 'JPEG', quality=q, optimize=True, progressive=True)
    return 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode('ascii'), len(b.getvalue())


day = Image.open(f'{SRC}/terre-jour.jpg').convert('RGB').resize((W, H), Image.LANCZOS)

# Nuit : on ne garde que les lumières (luminance seuillée), teintées d'orangé
n = np.asarray(Image.open(f'{SRC}/terre-nuit.jpg').convert('RGB').resize((W, H), Image.LANCZOS), dtype=np.float32) / 255
lum = 0.2126 * n[..., 0] + 0.7152 * n[..., 1] + 0.0722 * n[..., 2]
L = np.clip((lum - 0.13) / 0.55, 0, 1) ** 1.25
night = Image.fromarray((np.stack([L, L * 0.82, L * 0.55], -1) * 255).astype(np.uint8))

# Nuages : bruit de valeur 3D (fBm) sur la sphère, sans déformation aux pôles ni couture à ±180°
lon = (np.arange(W) + 0.5) / W * 2 * np.pi - np.pi
lat = np.pi / 2 - (np.arange(H) + 0.5) / H * np.pi
LON, LAT = np.meshgrid(lon, lat)
X, Y, Z = np.cos(LAT) * np.cos(LON), np.cos(LAT) * np.sin(LON), np.sin(LAT)
rng = np.random.default_rng(1955)
PERM = rng.permutation(256)
VAL = rng.random(256)


def h(a, b, c):
    return VAL[PERM[(PERM[(PERM[a & 255] + b) & 255] + c) & 255]]


def vnoise(x, y, z):
    xi, yi, zi = np.floor(x).astype(np.int64), np.floor(y).astype(np.int64), np.floor(z).astype(np.int64)
    xf, yf, zf = x - xi, y - yi, z - zi
    u, v, w = xf * xf * (3 - 2 * xf), yf * yf * (3 - 2 * yf), zf * zf * (3 - 2 * zf)
    x00 = h(xi, yi, zi) + u * (h(xi + 1, yi, zi) - h(xi, yi, zi))
    x10 = h(xi, yi + 1, zi) + u * (h(xi + 1, yi + 1, zi) - h(xi, yi + 1, zi))
    x01 = h(xi, yi, zi + 1) + u * (h(xi + 1, yi, zi + 1) - h(xi, yi, zi + 1))
    x11 = h(xi, yi + 1, zi + 1) + u * (h(xi + 1, yi + 1, zi + 1) - h(xi, yi + 1, zi + 1))
    y0, y1 = x00 + v * (x10 - x00), x01 + v * (x11 - x01)
    return y0 + w * (y1 - y0)


def fbm(x, y, z, octaves, f0):
    s, a, f, norm = 0.0, 0.5, f0, 0.0
    for k in range(octaves):
        s = s + a * vnoise(x * f + 17.1 * k, y * f + 31.7 * k, z * f + 47.3 * k)
        norm += a
        a *= 0.5
        f *= 2.03
    return s / norm


wx = fbm(X, Y, Z, 5, 2.4)
wy = fbm(X + 5.2, Y + 1.3, Z + 7.7, 5, 2.4)
wz = fbm(X + 9.1, Y + 3.4, Z + 2.8, 5, 2.4)
nz = fbm(X + 0.75 * (wx - 0.5), Y + 0.75 * (wy - 0.5), Z + 0.75 * (wz - 0.5), 8, 5.0)
fine = fbm(X * 1.7 + 3.3, Y * 1.7 + 8.1, Z * 1.7 + 4.4, 6, 9.0)   # détail : bords effilochés
nz = (nz - nz.mean()) / nz.std() + 0.55 * ((fine - fine.mean()) / fine.std())
la = np.degrees(LAT)
al = np.abs(la)
# nébulosité : zone de convergence intertropicale, anticyclones subtropicaux plus clairs, rails des dépressions
prof = (0.0 + 0.9 * np.exp(-((la - 4) / 8) ** 2) - 0.75 * np.exp(-((al - 24) / 9) ** 2)
        + 0.65 * np.exp(-((al - 55) / 11) ** 2) - 0.2 * np.exp(-((al - 85) / 7) ** 2))
alpha = 0.92 * np.clip((nz + prof - 0.2) * 0.5, 0, 1) ** 1.2
clouds = Image.fromarray((alpha * 255).astype(np.uint8), 'L')

moon = Image.open(f'{SRC}/lune.jpg').convert('RGB')
out, sizes = {}, {}
for key, im, q in (('day', day, 84), ('night', night, 80), ('clouds', clouds, 82), ('moon', moon, 85)):
    out[key], sizes[key] = uri(im, q)
json.dump(out, open(OUT, 'w', encoding='utf-8'), separators=(',', ':'))
print('nébulosité moyenne :', round(float(alpha.mean()), 2), '·', ', '.join(f'{k} {round(v / 1024)} Ko' for k, v in sizes.items()))
if PREVIEW:
    prev = Image.composite(Image.new('RGB', (W, H), (255, 255, 255)), day, clouds).resize((1024, 512), Image.LANCZOS)
    prev.save(PREVIEW)
