"""Injecte les données dans le gabarit de la vue 3D : étoiles (HYG) et, si le gabarit les attend,
contours terrestres (Natural Earth) et textures (Terre, nuages, Lune).
Usage : python -I assembler.py gabarit.html etoiles.json sortie.html [geo.json] [tex.json]"""
import sys

src, data, out = sys.argv[1], sys.argv[2], sys.argv[3]
extra = sys.argv[4:]
with open(src, encoding='utf-8') as f:
    html = f.read()


def inject(page, marker, path):
    if page.count(marker) != 1:
        sys.exit('marqueur introuvable ou en double : ' + marker)
    with open(path, encoding='utf-8') as fh:
        return page.replace(marker, fh.read().strip())


html = inject(html, '/*__STARS__*/null', data)
for marker, i in (('/*__GEO__*/null', 0), ('/*__TEX__*/null', 1)):
    if marker in html:
        if len(extra) <= i:
            sys.exit('le gabarit attend un fichier pour ' + marker)
        html = inject(html, marker, extra[i])
with open(out, 'w', encoding='utf-8', newline='\n') as f:
    f.write(html)
print('page assemblée :', round(len(html.encode('utf-8')) / 1024), 'Ko')
