"""Injecte les données dans le gabarit de la vue 3D : étoiles (HYG) et, si le gabarit
les attend, contours terrestres (Natural Earth).
Usage : python -I assembler.py gabarit.html etoiles.json sortie.html [geo.json]"""
import sys

src, data, out = sys.argv[1], sys.argv[2], sys.argv[3]
geo = sys.argv[4] if len(sys.argv) > 4 else None
with open(src, encoding='utf-8') as f:
    html = f.read()


def inject(page, marker, path):
    if page.count(marker) != 1:
        sys.exit('marqueur introuvable ou en double : ' + marker)
    with open(path, encoding='utf-8') as fh:
        return page.replace(marker, fh.read().strip())


html = inject(html, '/*__STARS__*/null', data)
if '/*__GEO__*/null' in html:
    if not geo:
        sys.exit('le gabarit attend aussi geo.json')
    html = inject(html, '/*__GEO__*/null', geo)
with open(out, 'w', encoding='utf-8', newline='\n') as f:
    f.write(html)
print('page assemblée :', round(len(html.encode('utf-8')) / 1024), 'Ko')
