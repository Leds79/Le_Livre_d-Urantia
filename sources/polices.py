"""Polices de l'atlas (Google Fonts, licence SIL OFL 1.1) : fichiers WOFF2 séparés et feuille fonts.css.

Sous-ensemble latin (il couvre le français : œ, ’, « », espaces fines). Chaque fichier n'est écrit qu'une
fois : quand Google sert le même fichier pour plusieurs graisses (police variable, comme Cormorant Garamond),
une seule règle @font-face le déclare avec une plage de graisses (font-weight: 500 700). Les fichiers se
chargent aussi depuis le disque (file://), car ils sont à côté de fonts.css (assets/fonts/ dans le site).

Usage :
  python -I polices.py <dossier de sortie>                      télécharge les polices et les licences OFL
  python -I polices.py <dossier de sortie> --depuis <fonts.css>  réutilise une feuille à polices intégrées
                                                                 en data: URI (sans réseau)"""
import base64
import hashlib
import re
import sys
import urllib.request
from pathlib import Path

OUT = Path(sys.argv[1])
DEPUIS = sys.argv[sys.argv.index('--depuis') + 1] if '--depuis' in sys.argv else None
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


def faces():
    """(famille, style, graisse, unicode-range, octets WOFF2) pour chaque règle latine."""
    if DEPUIS:
        css = Path(DEPUIS).read_text(encoding='utf-8')
        blocks = re.findall(r'@font-face\s*\{[^}]*\}', css)
    else:
        css = get(CSS_URL).decode('utf-8')
        blocks = re.findall(r'/\* latin \*/\s*(@font-face\s*\{[^}]*\})', css)
    out = []
    for b in blocks:
        fam = re.search(r"font-family:\s*'([^']+)'", b).group(1)
        style = re.search(r'font-style:\s*(\w+)', b).group(1)
        poids = int(re.search(r'font-weight:\s*(\d+)', b).group(1))
        plage = re.search(r'unicode-range:\s*([^;]+);', b).group(1).strip()
        data = re.search(r'base64,([A-Za-z0-9+/=]+)', b)
        octets = base64.b64decode(data.group(1)) if data else get(re.search(r'url\((https://[^)]+\.woff2)\)', b).group(1))
        out.append((fam, style, poids, plage, octets))
    return out


OUT.mkdir(parents=True, exist_ok=True)
groupes = {}                                   # même fichier → une seule règle
for fam, style, poids, plage, octets in faces():
    cle = (fam, style, hashlib.sha256(octets).hexdigest())
    g = groupes.setdefault(cle, {'fam': fam, 'style': style, 'poids': [], 'plage': plage, 'octets': octets})
    g['poids'].append(poids)
for ancien in OUT.glob('*.woff2'):
    ancien.unlink()
lignes = ['/* Polices de l’atlas : Alegreya Sans, Cormorant Garamond, IBM Plex Mono (SIL OFL 1.1, voir OFL-*.txt).',
          '   Sous-ensemble latin, un fichier WOFF2 par police ; polices variables déclarées avec une plage de graisses. */']
total = 0
for g in groupes.values():
    p = sorted(set(g['poids']))
    graisse = str(p[0]) if len(p) == 1 else f'{p[0]} {p[-1]}'
    nom = re.sub(r'\W+', '-', g['fam'].lower()).strip('-') + '-' + graisse.replace(' ', '-') + ('-italic' if g['style'] == 'italic' else '') + '.woff2'
    (OUT / nom).write_bytes(g['octets'])
    total += len(g['octets'])
    lignes.append('@font-face {\n'
                  f"  font-family: '{g['fam']}';\n  font-style: {g['style']};\n  font-weight: {graisse};\n  font-display: swap;\n"
                  f"  src: url({nom}) format('woff2');\n  unicode-range: {g['plage']};\n}}")
(OUT / 'fonts.css').write_text('\n'.join(lignes) + '\n', encoding='utf-8')
if not DEPUIS:
    for name, url in OFL.items():
        (OUT / ('OFL-' + name.replace(' ', '') + '.txt')).write_bytes(get(url))
print(len(groupes), 'fichiers WOFF2 ·', round(total / 1024), 'Ko · fonts.css', round((OUT / 'fonts.css').stat().st_size / 1024, 1), 'Ko')
