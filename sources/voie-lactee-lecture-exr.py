# Voie lactée, étape 1 : lit la carte linéaire de la NASA (SVS 4851, Deep Star Maps 2020, milkyway_2020_4k_gal.exr),
# affiche sa répartition de luminance et l'enregistre en tableau NumPy RGB (float32) pour voie-lactee-conversion.py.
# Usage : python -I voie-lactee-lecture-exr.py milkyway_2020_4k_gal.exr mw.npy   (paquets numpy et opencv-python)
import os, sys
os.environ['OPENCV_IO_ENABLE_OPENEXR'] = '1'
sys.stdout.reconfigure(encoding='utf-8')
import cv2, numpy as np
p = sys.argv[1]
im = cv2.imread(p, cv2.IMREAD_UNCHANGED)
print('shape', im.shape, im.dtype)
im = im[..., ::-1].astype(np.float32)   # BGR -> RGB
L = 0.2126 * im[..., 0] + 0.7152 * im[..., 1] + 0.0722 * im[..., 2]
for q in (1, 5, 25, 50, 75, 90, 95, 99, 99.5, 99.9, 99.99, 100):
    print('p%-6s %.6g' % (q, np.percentile(L, q)))
h, w = L.shape
# profil en latitude (moyenne par ligne), et quelques zones
rows = L.mean(axis=1)
for b in (90, 60, 45, 30, 20, 10, 5, 0, -5, -10, -20, -30, -45, -60, -90):
    y = int(np.clip((90 - b) / 180 * h, 0, h - 1))
    print('b=%+3d  moyenne %.5g  médiane %.5g' % (b, rows[y], np.median(L[y])))
cx, cy = w // 2, h // 2
print('centre galactique (moy 21x21):', L[cy-10:cy+11, cx-10:cx+11].mean())
np.save(sys.argv[2], im)
print('min', im.min(), 'neg count', (im < 0).sum())
