"""Prépare les textures d'Urantia et de la Lune pour la vue 3D, et les écrit en data: URI dans tex.json.

- jour : NASA Blue Marble Next Generation (« Whole world - land and oceans », Wikimedia Commons, domaine public) ;
- nuit : NASA, lumières des villes (« The earth at night », Wikimedia Commons, domaine public), lumières isolées ;
- planètes : cartes NASA (Jupiter, Mars, Mercure, Pluton) et images générées (Soleil, Vénus, Saturne, Uranus, Neptune, anneaux), voir plus bas ;
- nuages : IMAGE GÉNÉRÉE, illustrative (bruit fractal 3D évalué sur la sphère, avec distorsion de domaine
  et profil de nébulosité selon la latitude) ;
- Lune : NASA Scientific Visualization Studio, CGI Moon Kit (LRO), domaine public.
Usage : python -I textures.py <dossier des images> <tex.json> [aperçu-nuages.png]"""
import base64
import io
import json
import os
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

# ---------- Planètes du système solaire (vue 3D, clic sur une planète) ----------
# Cartes réelles, domaine public, dans <dossier>/planetes : Jupiter (Cassini, PIA07782), Mars (Viking MDIM21),
# Mercure (MESSENGER, PIA15063, niveaux de gris teintés), Pluton (New Horizons ; calotte sud jamais photographiée,
# complétée par un ton neutre). IMAGES GÉNÉRÉES d'après les photographies : Vénus (sommet des nuages), Saturne (bandes,
# hexagone polaire), Uranus, Neptune, Soleil (granulation, taches), profils radiaux des anneaux de Saturne et d'Uranus
# (rayons des anneaux d'après les mesures des sondes Voyager et Cassini).
PL = f'{SRC}/planetes'
planet_preview = []
if os.path.isdir(PL):
    PW, PH = 1024, 512
    lon2 = (np.arange(PW) + 0.5) / PW * 2 * np.pi - np.pi
    lat2 = np.pi / 2 - (np.arange(PH) + 0.5) / PH * np.pi
    LO2, LA2 = np.meshgrid(lon2, lat2)
    X2, Y2, Z2 = np.cos(LA2) * np.cos(LO2), np.cos(LA2) * np.sin(LO2), np.sin(LA2)
    lat_d, lon_d = np.degrees(LA2), np.degrees(LO2)
    C = lambda *v: np.array(v, dtype=np.float32)

    def z(a):
        return (a - a.mean()) / (a.std() + 1e-9)

    def to_img(a, size=None):
        im = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8), 'RGB')
        return im.resize(size, Image.LANCZOS) if size else im

    def load(name):
        return np.asarray(Image.open(f'{PL}/{name}.jpg').convert('RGB').resize((PW, PH), Image.LANCZOS), dtype=np.float32) / 255

    def sphere_dist(la0, lo0):
        a, b = np.radians(la0), np.radians(lo0)
        return np.degrees(np.arccos(np.clip(np.sin(LA2) * np.sin(a) + np.cos(LA2) * np.cos(a) * np.cos(LO2 - b), -1, 1)))

    P = {}
    P['jupiter'] = (to_img(load('jupiter')), 84)
    P['mars'] = (to_img(load('mars') * C(1.05, 0.97, 0.89)), 84)          # mosaïque Viking un peu rosée : teinte réchauffée
    me = np.asarray(Image.open(f'{PL}/mercure.jpg').convert('L').resize((PW, PH), Image.LANCZOS), dtype=np.float32) / 255
    lo, hi = np.percentile(me, 1), np.percentile(me, 99.6)
    me = np.clip((me - lo) / (hi - lo), 0, 1) ** 0.85 * 0.74 + 0.1
    P['mercure'] = (to_img(me[..., None] * C(1.0, 0.94, 0.86)), 84)
    pl = load('pluton')
    from PIL import ImageFilter
    dark = (pl.max(axis=-1) < 0.07) & (lat_d < 0)
    band = pl[(lat_d < -8) & (lat_d > -30) & ~dark]
    fill = np.median(band, axis=0) * 0.92
    nfill = fbm(X2 * 1.3 + 2.1, Y2 * 1.3 + 0.7, Z2 * 1.3 + 5.5, 5, 3.0)
    fill_img = fill[None, None, :] * (1 + 0.1 * z(nfill))[..., None]
    mask = np.asarray(Image.fromarray((dark * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(5)), dtype=np.float32)[..., None] / 255
    mask = np.maximum(mask, dark[..., None].astype(np.float32))
    P['pluton'] = (to_img(pl * (1 - mask) + fill_img * mask), 84)

    # Vénus : sommet des nuages, presque uniforme, traînées zonales très douces
    nv = z(fbm(X2, Y2, Z2 * 3.6, 6, 2.2)) + 0.5 * z(fbm(X2 * 2 + 3, Y2 * 2 + 1, Z2 * 7, 5, 3.0))
    ven = C(0.95, 0.88, 0.71) * (1 + 0.03 * nv)[..., None] * (1 - 0.06 * (np.abs(lat_d) / 90) ** 2)[..., None]
    P['venus'] = (to_img(ven, (512, 256)), 82)

    # Saturne : bandes claires et ceintures un peu brunes, zone équatoriale pâle, hexagone polaire bleuté
    r_ = np.radians(lat_d)
    bands = 0.5 * np.sin(r_ * 9.3 + 0.6) + 0.3 * np.sin(r_ * 17.7 + 1.9) + 0.2 * np.sin(r_ * 31.0 + 0.4) + 0.12 * np.sin(r_ * 57.0 + 2.2)
    turb = z(fbm(X2 * 1.2, Y2 * 1.2, Z2 * 10.0, 6, 3.0))
    k = np.clip(0.55 + 0.32 * (bands + 0.22 * turb), 0, 1)[..., None]
    sat = C(0.90, 0.81, 0.62) * k + C(0.74, 0.62, 0.45) * (1 - k)
    eq = np.exp(-(lat_d / 11) ** 2)[..., None]
    sat = sat * (1 - 0.35 * eq) + C(0.94, 0.87, 0.70) * 0.35 * eq
    rho = 90 - lat_d
    rh = 12.5 / np.cos(np.radians(((lon_d % 60) + 60) % 60 - 30))
    hexa = np.clip((rh - rho) / 1.5, 0, 1)[..., None]
    sat = sat * (1 - 0.75 * hexa) + C(0.60, 0.65, 0.70) * 0.75 * hexa
    sat = sat * (1 - 0.25 * np.clip((lat_d + 70) / -20, 0, 1))[..., None] + C(0.80, 0.74, 0.60) * 0.25 * np.clip((lat_d + 70) / -20, 0, 1)[..., None]
    P['saturne'] = (to_img(sat), 82)

    # Uranus : cyan pâle, presque uniforme, bandes à peine visibles, calotte nord un peu plus claire
    nu = z(fbm(X2, Y2, Z2 * 5, 4, 2.0))
    ura = C(0.68, 0.86, 0.89) * (1 + 0.015 * nu + 0.025 * np.cos(np.radians(lat_d) * 6))[..., None]
    ura = ura * (1 + 0.07 * np.clip((lat_d - 55) / 25, 0, 1))[..., None]
    P['uranus'] = (to_img(ura, (512, 256)), 82)

    # Neptune : bleu profond, bandes sombres, cirrus blancs de méthane, petite tache sombre (illustratifs)
    nn = z(fbm(X2 * 1.2, Y2 * 1.2, Z2 * 7, 6, 2.5))
    nep = C(0.36, 0.55, 0.88) * (1 + 0.06 * nn)[..., None]
    nep = nep * (1 - 0.13 * np.exp(-((lat_d + 22) / 8) ** 2) - 0.08 * np.exp(-((np.abs(lat_d) - 55) / 10) ** 2))[..., None]
    cir = fbm(X2 * 2 + 4, Y2 * 2 + 1, Z2 * 14, 5, 3.0)
    cm = np.clip((cir - 0.6) * 5, 0, 1) * (np.exp(-((lat_d + 40) / 5) ** 2) + 0.6 * np.exp(-((lat_d - 26) / 4) ** 2))
    nep = nep * (1 - cm[..., None]) + C(0.90, 0.94, 1.0) * cm[..., None]
    nep = nep * (1 - 0.4 * np.exp(-(sphere_dist(-21, 40) / 4.5) ** 2))[..., None]
    P['neptune'] = (to_img(nep), 82)

    # Soleil : granulation et supergranulation, quelques taches (le cycle de onze ans et demi, 57:5.2)
    g = z(fbm(X2, Y2, Z2, 5, 28.0)) + 0.6 * z(fbm(X2 + 7, Y2 + 2, Z2 + 9, 4, 7.0))
    sun = C(1.0, 0.86, 0.56) * (0.93 + 0.035 * g)[..., None]
    for la0, lo0, s0 in ((14, -40, 1.6), (16, -36, 1.0), (-12, 70, 1.3), (-15, 75, 0.8)):
        d = sphere_dist(la0, lo0)
        sun = sun * (1 - 0.75 * np.exp(-(d / s0) ** 2) - 0.25 * np.exp(-(d / (s0 * 2.2)) ** 2))[..., None]
    P['soleil'] = (to_img(sun, (512, 256)), 84)

    for key, (im, q) in P.items():
        out[key], sizes[key] = uri(im, q)
        planet_preview.append(im.resize((256, 128), Image.LANCZOS))

    # Anneaux : profils radiaux (couleur et opacité) ; Saturne de 1,11 à 2,34 rayons équatoriaux, Uranus de 1,60 à 2,03
    def ring_png(rmin, rmax, regions, seed):
        n = 1024
        r = rmin + (np.arange(n) + 0.5) / n * (rmax - rmin)
        rg = np.random.default_rng(seed)
        jit = np.convolve(rg.normal(size=n + 8), np.ones(5) / 5, 'same')[4:n + 4]
        a = np.zeros(n, np.float32)
        col = np.zeros((n, 3), np.float32)
        for r0, r1, a0, a1, c, j in regions:
            m = (r >= r0) & (r < r1) if r1 - r0 > (rmax - rmin) / n else (np.abs(r - (r0 + r1) / 2) <= (rmax - rmin) / n / 2 + 1e-9)
            t = np.clip((r - r0) / max(r1 - r0, 1e-9), 0, 1)
            a[m] = np.clip((a0 + (a1 - a0) * t + j * jit)[m], 0, 1)
            col[m] = np.array(c, np.float32) * (1 + 0.6 * j * jit[m, None])
        rgba = np.concatenate([np.clip(col, 0, 1), a[:, None]], 1)
        im = Image.fromarray((np.repeat(rgba[None], 4, 0) * 255).astype(np.uint8), 'RGBA')
        b = io.BytesIO()
        im.save(b, 'PNG', optimize=True)
        return 'data:image/png;base64,' + base64.b64encode(b.getvalue()).decode('ascii'), len(b.getvalue())

    SAT_R = [  # r0, r1 (rayons de Saturne), opacité début, fin, couleur, variation
        (1.110, 1.236, 0.03, 0.04, (0.45, 0.42, 0.38), 0.01),          # anneau D
        (1.239, 1.527, 0.10, 0.16, (0.55, 0.50, 0.44), 0.06),          # anneau C
        (1.2900, 1.2925, 0.0, 0.0, (0, 0, 0), 0.0),                    # division de Colombo
        (1.4505, 1.4530, 0.0, 0.0, (0, 0, 0), 0.0),                    # division de Maxwell
        (1.527, 1.640, 0.62, 0.78, (0.84, 0.77, 0.64), 0.08),          # anneau B
        (1.640, 1.750, 0.88, 0.93, (0.87, 0.80, 0.67), 0.05),
        (1.750, 1.880, 0.95, 0.98, (0.88, 0.81, 0.68), 0.03),
        (1.880, 1.951, 0.86, 0.80, (0.85, 0.78, 0.66), 0.05),
        (1.951, 1.995, 0.01, 0.02, (0.36, 0.34, 0.30), 0.005),         # division de Cassini (lacune de Huygens)
        (1.9715, 1.9735, 0.30, 0.30, (0.6, 0.57, 0.5), 0.0),           # annelet de Huygens
        (1.995, 2.027, 0.09, 0.12, (0.40, 0.37, 0.33), 0.03),
        (2.027, 2.269, 0.60, 0.47, (0.80, 0.75, 0.64), 0.05),          # anneau A
        (2.2115, 2.2169, 0.0, 0.0, (0, 0, 0), 0.0),                    # division d'Encke
        (2.2647, 2.2655, 0.15, 0.15, (0.8, 0.75, 0.64), 0.0),          # division de Keeler
        (2.269, 2.320, 0.012, 0.012, (0.5, 0.48, 0.44), 0.004),        # division de Roche
        (2.3245, 2.3275, 0.55, 0.55, (0.86, 0.83, 0.76), 0.0),         # anneau F
    ]
    URA_R = [(r - 0.0006, r + 0.0006, al, al, (0.32, 0.32, 0.33), 0.0) for r, al in
             ((1.6369, 0.18), (1.6526, 0.2), (1.6656, 0.2), (1.7496, 0.35), (1.7864, 0.35), (1.8458, 0.18), (1.8634, 0.22), (1.8898, 0.35))]
    URA_R.append((1.9990, 2.0035, 0.7, 0.7, (0.36, 0.36, 0.37), 0.0))  # anneau epsilon
    out['anneaux'], sizes['anneaux'] = ring_png(1.11, 2.34, SAT_R, 1655)
    out['anneauxU'], sizes['anneauxU'] = ring_png(1.60, 2.03, URA_R, 1977)
json.dump(out, open(OUT, 'w', encoding='utf-8'), separators=(',', ':'))
print('nébulosité moyenne :', round(float(alpha.mean()), 2), '·', ', '.join(f'{k} {round(v / 1024)} Ko' for k, v in sizes.items()))
if PREVIEW:
    prev = Image.composite(Image.new('RGB', (W, H), (255, 255, 255)), day, clouds).resize((1024, 512), Image.LANCZOS)
    prev.save(PREVIEW)
    if planet_preview:
        M = Image.new('RGB', (1024, 128 * ((len(planet_preview) + 3) // 4)), (20, 20, 30))
        for i, im in enumerate(planet_preview):
            M.paste(im, ((i % 4) * 256, (i // 4) * 128))
        M.save(PREVIEW.replace('.png', '-planetes.png'))
