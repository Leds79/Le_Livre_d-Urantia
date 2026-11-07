"""Télécharge les polices de l'atlas (Google Fonts, licence SIL OFL 1.1) et produit
une feuille fonts.css autonome (fichiers WOFF2 intégrés en data: URI, sous-ensemble latin),
pour un site qui s'affiche aussi hors ligne, y compris ouvert depuis le disque (file://).
Usage : python -I polices.py <dossier de sortie>"""
import base64
import re
import sys
import urllib.request
from pathlib import Path

OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'
CSS_URL = ('https://fonts.googleapis.com/css2?family=Alegreya+Sans:ital,wght@0,400;0,500;0,700;1,400'
           '&family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,500;1,600'
           '&family=IBM+Plex+Mono:wght@400;500&display=swap')
OFL = {
    'Alegreya Sans': 'https://raw.githubusercontent.com/google/fonts/main/ofl/alegreyasans/OFL.txt',
    'Cormorant Garamond': 'https://raw.githubusercontent.com/google/fonts/main/ofl/cormorantgaramond/OFL.txt',
    'IBM Plex Mono': 'https://raw.githubusercontent.com/google/fonts/main/ofl/ibmplexmono/OFL.txt',
}


def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


css = get(CSS_URL).decode('utf-8')
# blocs « /* latin */ @font-face {...} » : le sous-ensemble latin couvre le français (œ, ’, « », espaces fines)
blocks = re.findall(r'/\* latin \*/\s*(@font-face\s*\{[^}]*\})', css)
out, total = ['/* Polices de l’atlas : Alegreya Sans, Cormorant Garamond, IBM Plex Mono (SIL OFL 1.1, voir OFL-*.txt).',
              '   Sous-ensemble latin, intégré en data: URI pour fonctionner hors ligne. */'], 0
for b in blocks:
    url = re.search(r'url\((https://[^)]+\.woff2)\)', b).group(1)
    data = get(url)
    total += len(data)
    b = b.replace(url, 'data:font/woff2;base64,' + base64.b64encode(data).decode('ascii'))
    out.append(b)
(OUT / 'fonts.css').write_text('\n'.join(out) + '\n', encoding='utf-8')
for name, url in OFL.items():
    (OUT / ('OFL-' + name.replace(' ', '') + '.txt')).write_bytes(get(url))
print(len(blocks), 'faces ·', round(total / 1024), 'Ko de WOFF2 ·', round((OUT / 'fonts.css').stat().st_size / 1024), 'Ko de CSS')
