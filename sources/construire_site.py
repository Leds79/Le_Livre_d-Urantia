"""Construit le site statique « Le Livre d'Urantia en images » à partir des pages publiées.

Chaque page reçoit un squelette HTML complet ; les liens entre pages deviennent relatifs
et s'ouvrent dans le même onglet ; Three.js et les polices sont servis en local
(assets/), si bien que le site s'ouvre hors ligne (index.html) et se publie tel quel
sur GitHub Pages. Les sources de la vue 3D sont copiées dans sources/.

Usage : python -I construire_site.py <dossier source de l'atlas> <dossier du site>
Le dossier source contient les pages publiées, polices/ (fonts.css et OFL), site/ (README,
LICENCES, favicon, aperçu) ; ../lib contient Three.js et sa licence."""
import re
import shutil
import sys
from pathlib import Path

SRC, OUT = Path(sys.argv[1]), Path(sys.argv[2])
LIB = SRC.parent / 'lib'
BASE = 'https://leds79.github.io/Le_Livre_d-Urantia/'
# fichier publié, adresse de l'artefact en ligne, nom dans le site, description
PAGES = [
    ('accueil.html', 'https://claude.ai/artifact/C8kuuUiuBDqFepzcHaYzyn', 'index.html',
     'Atlas visuel du Livre d’Urantia : notre adresse dans l’univers, la vue 3D d’Urantia au Paradis, la frise du temps, la carrière ascendante, les êtres de l’univers et les concepts, avec les références du texte.'),
    ('urantia-paradis-3d.html', 'https://claude.ai/artifact/PJDHwbqKNjrjSwS8nLXAmi', 'atlas-3d.html',
     'Vue 3D : d’Urantia au Paradis, les sept superunivers, Havona, la frise du temps de Satania et d’Urantia, la carrière ascendante.'),
    ('nebadon-orvonton.html', 'https://claude.ai/artifact/ErCNNj9LZCioWoDAGPN8ru', 'nebadon-dans-orvonton.html',
     'Schéma : la place de Nébadon dans le superunivers d’Orvonton, et celle de la Voie lactée.'),
    ('familles-de-personnalites.html', 'https://claude.ai/artifact/Nboax4BBSptrGQWJZdKyxZ', 'familles-de-personnalites.html',
     'Les familles de personnalités selon le Livre d’Urantia : classifications d’Uversa et du Paradis, en arbre interactif.'),
    ('concepts.html', 'https://claude.ai/artifact/4qy2hFKTsUHbnQUZb4abT1', 'concepts-en-schemas.html',
     'Sept schémas : personnalité, mental, Ajusteur, âme, adjuvats, cercles psychiques, niveaux de réalité et morontia.'),
    ('dieu-et-deite.html', 'https://claude.ai/artifact/Dw332DFEqbZTfoqrwLk3at', 'dieu-et-deite.html',
     'Dieu et la Déité selon le Livre d’Urantia : le JE SUIS, les sept Absolus, la Trinité, les Maitres Esprits, les Déités expérientielles.'),
    ('histoire-d-urantia.html', 'https://claude.ai/artifact/URhwMaWUmndS1dMn8GeVgm', 'histoire-d-urantia.html',
     'L’histoire d’Urantia selon le livre : formation de la planète, ères de la vie, apparition et dispersion des races, sur une carte du monde.'),
    ('vie-de-jesus.html', 'https://claude.ai/artifact/Ekdw5SMkFyodpBiEc7i7UE', 'vie-de-jesus.html',
     'La vie de Jésus selon la quatrième partie du livre : une frise de 92 étapes, de l’annonce à Marie à la Pentecôte, et les cartes de ses voyages.'),
]
CDN = {
    'https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js': 'assets/lib/three.min.js',
    'https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js': 'assets/lib/OrbitControls.js',
}
SOURCES = ['urantia-paradis-3d.src.html', 'etoiles.json', 'geo.json', 'tex.json', 'assembler.py', 'etoiles.py', 'geo.py',
           'textures.py', 'polices.py', 'smoke3d.js', 'construire_site.py']
RESET = ('<style>:root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);'
         'padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0;font:14px system-ui,sans-serif}'
         'img{max-width:100%}[hidden]{display:none!important}</style>')


def esc(s):
    return s.replace('&', '&amp;').replace('"', '&quot;').replace('<', '&lt;')


present = [p for p in PAGES if (SRC / p[0]).exists()]
urlmap = {url: name for (_, url, name, _) in present if url}
problems = []
OUT.mkdir(parents=True, exist_ok=True)
for fichier, url, name, desc in present:
    html = (SRC / fichier).read_text(encoding='utf-8')
    for u, n in urlmap.items():
        html = html.replace(u, n)
    for u, n in CDN.items():
        html = html.replace(u, n)
    html = re.sub(r'<link rel="preconnect" href="https://fonts\.(googleapis|gstatic)\.com"( crossorigin)?>\s*', '', html)
    html = re.sub(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com/css2\?[^"]*">',
                  '<link rel="stylesheet" href="assets/fonts/fonts.css">', html)

    def same_tab(m):
        tag = m.group(0)
        href = re.search(r'href="([^"]*)"', tag)
        if href and re.match(r'^[a-z0-9-]+\.html(#[a-z0-9-]*)?$', href.group(1)):
            tag = tag.replace(' target="_blank"', '').replace(' rel="noopener"', '')
        return tag
    html = re.sub(r'<a\b[^>]*>', same_tab, html)
    title = re.search(r'<title>(.*?)</title>', html, re.S).group(1).strip()
    cut = html.index('</style>') + len('</style>')
    head, body = html[:cut], html[cut:]
    meta = ('<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            f'<meta name="description" content="{esc(desc)}">\n'
            '<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">\n'
            '<meta property="og:type" content="website">\n<meta property="og:locale" content="fr_FR">\n'
            f'<meta property="og:title" content="{esc(title)}">\n<meta property="og:description" content="{esc(desc)}">\n'
            f'<meta property="og:url" content="{BASE}{"" if name == "index.html" else name}">\n'
            f'<meta property="og:image" content="{BASE}assets/apercu.png">\n'
            '<meta name="twitter:card" content="summary_large_image">\n')
    page = ('<!doctype html>\n<html lang="fr">\n<head>\n' + meta + RESET + '\n' + head.strip() +
            '\n</head>\n<body>\n' + body.strip() + '\n</body>\n</html>\n')
    for bad in ('claude.ai/artifact', 'fonts.googleapis', 'fonts.gstatic', 'cdnjs.cloudflare', 'cdn.jsdelivr'):
        if bad in page:
            problems.append(f'{name} : reste une adresse « {bad} »')
    for href in re.findall(r'href="([a-z0-9-]+\.html)(?:#[^"]*)?"', page):
        if href not in {p[2] for p in present}:
            problems.append(f'{name} : lien vers une page absente ({href})')
    (OUT / name).write_text(page, encoding='utf-8')
    print(f'page : {name:32} {round(len(page.encode("utf-8")) / 1024):5} Ko')

assets = OUT / 'assets'
(assets / 'lib').mkdir(parents=True, exist_ok=True)
(assets / 'fonts').mkdir(parents=True, exist_ok=True)
for f in ('three.min.js', 'OrbitControls.js', 'LICENSE-three.txt'):
    shutil.copy2(LIB / f, assets / 'lib' / f)
for f in (SRC / 'polices').iterdir():
    shutil.copy2(f, assets / 'fonts' / f.name)
for f in ('favicon.svg', 'apercu.png'):
    if (SRC / 'site' / f).exists():
        shutil.copy2(SRC / 'site' / f, assets / f)
for f in ('README.md', 'LICENCES.md'):
    shutil.copy2(SRC / 'site' / f, OUT / f)
(OUT / '.nojekyll').write_text('', encoding='utf-8')
(OUT / 'sources').mkdir(exist_ok=True)
for f in SOURCES:
    if (SRC / f).exists():
        shutil.copy2(SRC / f, OUT / 'sources' / f)
print('\n'.join(problems) if problems else 'vérification : aucune adresse externe à remplacer, aucun lien interne cassé')
