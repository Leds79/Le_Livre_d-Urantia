# Voie lactée (NASA SVS 4851, milkyway_2020_4k_gal.exr, linéaire) -> image 8 bits sRGB, sans le grain des étoiles faibles.
# Médiane (retire les étoiles ponctuelles : la scène dessine les vraies étoiles à part), flou léger, plancher, épaule douce.
# Usage : python -I voie-lactee-conversion.py mw.npy sortie.webp largeur qualite expo plancher median flou [apercu.png]
# Réglages du site : python -I voie-lactee-conversion.py mw.npy voie-lactee.webp 4096 82 1.7 0.0075 5 0.9
# (mw.npy : écrit par voie-lactee-lecture-exr.py ; paquets numpy, opencv-python et Pillow)
import os, sys
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np, cv2
from PIL import Image
src, out, W, Q, EXPO, FLOOR, MED, BL = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), float(sys.argv[5]), float(sys.argv[6]), int(sys.argv[7]), float(sys.argv[8])
im = np.load(src).astype(np.float32)
raw = im
if MED > 1:
    im = np.dstack([cv2.medianBlur(np.ascontiguousarray(im[..., c]), MED) for c in range(3)])
if BL > 0:
    im = cv2.GaussianBlur(im, (0, 0), BL)
# lissage adaptatif : là où le signal est faible (hors de la bande), le grain du fond est remplacé par un dégradé lisse
strong = cv2.GaussianBlur(raw, (0, 0), 7.0)
ls = 0.2126 * strong[..., 0] + 0.7152 * strong[..., 1] + 0.0722 * strong[..., 2]
t = np.clip((ls - 0.012) / (0.045 - 0.012), 0, 1); w = (t * t * (3 - 2 * t))[..., None]
im = strong * (1 - w) + im * w
im = np.maximum(im - FLOOR, 0.0) * EXPO
lum = 0.2126 * im[..., 0] + 0.7152 * im[..., 1] + 0.0722 * im[..., 2]
im = im / (1.0 + lum / 0.9)[..., None]
a = np.clip(im, 0, 1)
srgb = np.where(a <= 0.0031308, 12.92 * a, 1.055 * np.power(a, 1 / 2.4) - 0.055)
u8 = (srgb * 255 + 0.5).astype(np.uint8)
img = Image.fromarray(np.ascontiguousarray(u8), 'RGB')
H = W // 2
if img.size != (W, H):
    img = img.resize((W, H), Image.LANCZOS)
img.save(out, 'WEBP', quality=Q, method=6)
print(out, img.size, os.path.getsize(out), 'octets')
if len(sys.argv) > 9:
    img.crop((W * 1700 // 4096, H * 800 // 2048, W * 2700 // 4096, H * 1300 // 2048)).save(sys.argv[9])
    img.crop((W * 2900 // 4096, H * 300 // 2048, W * 3900 // 4096, H * 800 // 2048)).save(sys.argv[9].replace('.png', '-haut.png'))
