"""Extrait du catalogue HYG v4.1 les étoiles utiles à la vue 3D.

Repère de la scène : x vers le centre galactique (Sagittaire), y vers le pôle Nord galactique,
z = -y galactique (repère direct). Distances en années-lumière.
Sortie : JSON compact {sky, skyNames, loc, locNames}.
"""
import csv
import json
import math
import sys

SRC, OUT = sys.argv[1], sys.argv[2]
PC2LY = 3.261563777
# Matrice équatorial J2000 -> galactique (documentation Hipparcos)
T = ((-0.0548755604, -0.8734370902, -0.4838350155),
     (0.4941094279, -0.4448296300, 0.7469822445),
     (-0.8676661490, -0.1980763734, 0.4559837762))

FR = {
    'Sirius': 'Sirius', 'Canopus': 'Canopus', 'Arcturus': 'Arcturus', 'Rigil Kentaurus': 'Alpha du Centaure',
    'Vega': 'Véga', 'Capella': 'Capella', 'Rigel': 'Rigel', 'Procyon': 'Procyon', 'Betelgeuse': 'Bételgeuse',
    'Achernar': 'Achernar', 'Hadar': 'Hadar', 'Altair': 'Altaïr', 'Acrux': 'Acrux', 'Aldebaran': 'Aldébaran',
    'Spica': 'Spica', 'Antares': 'Antarès', 'Pollux': 'Pollux', 'Fomalhaut': 'Fomalhaut', 'Deneb': 'Deneb',
    'Mimosa': 'Mimosa', 'Regulus': 'Régulus', 'Adhara': 'Adhara', 'Castor': 'Castor', 'Shaula': 'Shaula',
    'Gacrux': 'Gacrux', 'Bellatrix': 'Bellatrix', 'Elnath': 'Elnath', 'Miaplacidus': 'Miaplacidus',
    'Alnilam': 'Alnilam', 'Alnitak': 'Alnitak', 'Mintaka': 'Mintaka', 'Saiph': 'Saiph', 'Polaris': 'Polaris',
    'Proxima Centauri': 'Proxima du Centaure', "Barnard's Star": 'Étoile de Barnard', 'Dubhe': 'Dubhe',
    'Alkaid': 'Alkaid', 'Mizar': 'Mizar', 'Alioth': 'Alioth', 'Kochab': 'Kochab', 'Algol': 'Algol',
    'Mirfak': 'Mirfak', 'Alphard': 'Alphard', 'Denebola': 'Denebola', 'Rasalhague': 'Rasalhague',
    'Toliman': 'Alpha du Centaure B', 'Wolf 359': 'Wolf 359', 'Lalande 21185': 'Lalande 21185',
    'Ran': 'Epsilon Eridani', 'Tau Ceti': 'Tau Ceti',
}


def to_scene(x, y, z):
    gx = T[0][0] * x + T[0][1] * y + T[0][2] * z
    gy = T[1][0] * x + T[1][1] * y + T[1][2] * z
    gz = T[2][0] * x + T[2][1] * y + T[2][2] * z
    return gx, gz, -gy


def num(s, default=None):
    try:
        return float(s)
    except (TypeError, ValueError):
        return default


sky, sky_names, loc, loc_names = [], [], [], []
with open(SRC, newline='', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        if row['id'] == '0':
            continue  # le Soleil
        mag = num(row['mag'])
        ra, dec = num(row['ra']), num(row['dec'])
        if mag is None or ra is None or dec is None:
            continue
        ci = num(row['ci'], 0.6)
        proper = (row['proper'] or '').strip()
        name = FR.get(proper, proper)
        # 1) ciel à l'œil nu : direction seulement
        if mag <= 6.0:
            a, d = math.radians(ra * 15.0), math.radians(dec)
            sx, sy, sz = to_scene(math.cos(d) * math.cos(a), math.cos(d) * math.sin(a), math.sin(d))
            if name and (mag <= 1.6 or proper == 'Polaris'):
                sky_names.append([len(sky) // 5, name])
            sky.extend([round(sx, 4), round(sy, 4), round(sz, 4), round(mag, 1), round(ci, 2)])
        # 2) voisinage en 3D : distance connue
        dist = num(row['dist'])
        absmag = num(row['absmag'])
        if dist is None or dist <= 0 or dist >= 100000 or absmag is None:
            continue
        ly = dist * PC2LY
        if ly <= 60 or (mag <= 6.5 and ly <= 3500):
            x, y, z = num(row['x'], 0.0), num(row['y'], 0.0), num(row['z'], 0.0)
            px, py, pz = to_scene(x * PC2LY, y * PC2LY, z * PC2LY)
            if name and (mag <= 2.6 or ly <= 12):
                loc_names.append([len(loc) // 5, name, round(ly, 1)])
            loc.extend([round(px, 2), round(py, 2), round(pz, 2), round(absmag, 1), round(ci, 2)])

data = {'sky': sky, 'skyNames': sky_names, 'loc': loc, 'locNames': loc_names}
with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
print('ciel :', len(sky) // 5, 'étoiles,', len(sky_names), 'noms')
print('voisinage :', len(loc) // 5, 'étoiles,', len(loc_names), 'noms')
print('taille JSON :', round(len(json.dumps(data, ensure_ascii=False, separators=(',', ':'))) / 1024), 'Ko')
