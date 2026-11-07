"""Construit le site statique « Le Livre d'Urantia en images » à partir des pages publiées.

Chaque page reçoit un squelette HTML complet (métadonnées de partage, lien « Aller au contenu », barre de
navigation commune, parcours de découverte), une passe de typographie française, des liens relatifs qui
s'ouvrent dans le même onglet et des ressources locales (assets/) : le site s'ouvre hors ligne (index.html)
et se publie tel quel sur GitHub Pages. Les sources sont copiées dans sources/, sans les adresses claude.ai.

Usage : python -I construire_site.py <dossier source de l'atlas> <dossier du site>
Le dossier source contient les pages publiées, polices/ (fonts.css, fichiers WOFF2, OFL), site/ (README,
LICENCES, LICENSE, favicon, aperçu…), refs-urantia.js et, hors publication, artefacts.json (adresses des
pages publiées sur claude.ai) ; ../lib contient Three.js et sa licence. Détail : sources/CONSTRUIRE.md."""
import json
import re
import shutil
import struct
import sys
from pathlib import Path

SRC, OUT = Path(sys.argv[1]), Path(sys.argv[2])
LIB = SRC.parent / 'lib'
BASE = 'https://leds79.github.io/Le_Livre_d-Urantia/'
NOM_SITE = 'Le Livre d’Urantia en images'

# ── Plan de l'atlas ─────────────────────────────────────────────────────────────────────────────
# Une ligne par page, dans l'ordre de la barre commune :
#   (fichier source, nom dans le site, nom canonique, libellé court de la barre, description pour le partage)
# Le nom canonique sert au titre d'onglet, au parcours et à l'infobulle (title) de la barre ; la barre affiche
# le libellé court pour tenir sur une ligne dès 1 280 px. Pour ajouter une page : une ligne ici, et son
# adresse claude.ai dans artefacts.json si elle y est publiée.
PAGES = [
    ('accueil.html', 'index.html', 'Accueil', 'Accueil',
     'Atlas visuel du Livre d’Urantia : notre adresse dans l’univers, la vue 3D d’Urantia au Paradis, la frise du temps, la carrière ascendante, les êtres de l’univers et les concepts, avec les références du texte.'),
    ('nebadon-orvonton.html', 'nebadon-dans-orvonton.html', 'Nébadon dans Orvonton', 'Nébadon',
     'Schéma : la place de Nébadon dans le superunivers d’Orvonton, et celle de la Voie lactée.'),
    ('urantia-paradis-3d.html', 'atlas-3d.html', 'D’Urantia au Paradis (3D)', 'La 3D',
     'Vue 3D : d’Urantia au Paradis, les sept superunivers, Havona, la frise du temps de Satania et d’Urantia, la carrière ascendante.'),
    ('familles-de-personnalites.html', 'familles-de-personnalites.html', 'Familles de personnalités', 'Familles',
     'Les familles de personnalités selon le Livre d’Urantia : classifications d’Uversa et du Paradis, en arbre interactif.'),
    ('concepts.html', 'concepts-en-schemas.html', 'Concepts en schémas', 'Concepts',
     'Sept schémas : personnalité, mental, Ajusteur, âme, adjuvats, cercles psychiques, niveaux de réalité et morontia.'),
    ('dieu-et-deite.html', 'dieu-et-deite.html', 'Dieu et la Déité', 'Dieu et la Déité',
     'Dieu et la Déité selon le Livre d’Urantia : le JE SUIS, les sept Absolus, la Trinité, les Maitres Esprits, les Déités expérientielles.'),
    ('histoire-d-urantia.html', 'histoire-d-urantia.html', 'L’histoire d’Urantia', 'Histoire d’Urantia',
     'L’histoire d’Urantia selon le livre : formation de la planète, ères de la vie, apparition et dispersion des races, sur une carte du monde.'),
    ('rebellion-de-lucifer.html', 'rebellion-de-lucifer.html', 'La rébellion de Lucifer', 'La rébellion',
     'La rébellion de Lucifer selon le Livre d’Urantia : les trois échelles (Jérusem, Dalamatia, le Jardin), pourquoi Urantia est une planète isolée, le manifeste, les loyaux et les rebelles.'),
    ('vie-de-jesus.html', 'vie-de-jesus.html', 'La vie de Jésus', 'Vie de Jésus',
     'La vie de Jésus selon la quatrième partie du livre : une frise de 92 étapes, de l’annonce à Marie à la Pentecôte, et les cartes de ses voyages.'),
    ('bible-et-livre.html', 'bible-et-livre.html', 'La Bible et le Livre d’Urantia', 'La Bible',
     'Vingt parallèles entre la Bible (Crampon 1923) et le Livre d’Urantia, des origines à la Pentecôte : ce qui concorde, ce qui diffère, et ce que le livre en dit.'),
]
# Parcours de découverte (accueil), dans l'ordre : (adresse dans le site, nom canonique).
PARCOURS = [
    ('nebadon-dans-orvonton.html', 'Nébadon dans Orvonton'),
    ('atlas-3d.html', 'D’Urantia au Paradis (3D)'),
    ('atlas-3d.html#gouvernement', 'Qui gouverne quoi'),
    ('atlas-3d.html#frise', 'La frise du temps'),
    ('atlas-3d.html#carriere', 'La carrière ascendante'),
    ('familles-de-personnalites.html', 'Familles de personnalités'),
    ('concepts-en-schemas.html', 'Concepts en schémas'),
    ('dieu-et-deite.html', 'Dieu et la Déité'),
    ('histoire-d-urantia.html', 'L’histoire d’Urantia'),
    ('rebellion-de-lucifer.html', 'La rébellion de Lucifer'),
    ('vie-de-jesus.html', 'La vie de Jésus'),
    ('bible-et-livre.html', 'La Bible et le Livre d’Urantia'),
]
LIVRE = ('https://www.urantia.org/fr/le-livre-durantia/lire', 'Lire le livre (urantia.org)', 'Lire le livre')
SANS_BARRE = {'atlas-3d.html'}          # vue 3D plein écran : elle garde sa navigation propre
SANS_TYPO_JS = {'atlas-3d.html'}        # typographie du texte HTML seulement (scripts et données 3D non touchés)
APERCU_ALT = ('Le Livre d’Urantia en images : l’origine et l’organisation de l’univers, en cartes, en 3D et en schémas. '
              'Orbites concentriques autour d’un centre lumineux, sur un fond de nuit.')

CDN = {
    'https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js': 'assets/lib/three.min.js',
    'https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js': 'assets/lib/OrbitControls.js',
}
SOURCES = ['urantia-paradis-3d.src.html', 'etoiles.json', 'geo.json', 'tex.json', 'liens_refs.py', 'refs-urantia.js',
           'assembler.py', 'etoiles.py', 'geo.py', 'textures.py', 'polices.py', 'smoke3d.js', 'construire_site.py',
           'CONSTRUIRE.md', 'requirements.txt']
RACINE = ['README.md', 'LICENCES.md', 'LICENSE', 'LICENSE-CONTENU.md']      # copiés de site/ à la racine du site
ACTIFS = ['favicon.svg', 'apercu.png', 'apple-touch-icon.png']              # copiés de site/ dans assets/
RESET = ('<style>:root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);'
         'padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0;font:14px system-ui,sans-serif}'
         'img{max-width:100%}[hidden]{display:none!important}</style>')
NAV_CSS = ('<style>/* barre commune et parcours de l’atlas (construire_site.py) */'
           '.aller-contenu{position:absolute;left:-10000px;top:8px;z-index:100;padding:10px 16px;border-radius:8px;'
           'background:var(--ink);color:var(--paper);font:600 1rem/1.2 var(--font-body);text-decoration:none}'
           '.aller-contenu:focus{left:12px}'
           '.atlas-nav{background:var(--sheet);border-bottom:1px solid var(--rule)}'
           '.atlas-nav ul{list-style:none;margin:0 auto;max-width:1100px;padding:0 max(16px,env(safe-area-inset-left,0px));'
           'display:flex;flex-wrap:wrap;align-items:center;column-gap:16px}'
           '.atlas-nav li{margin:0;flex:none}'
           '.atlas-nav a{display:inline-flex;align-items:center;min-height:44px;color:var(--ink);font:500 .9rem/1.2 var(--font-body);'
           'text-decoration:none;white-space:nowrap}'
           '.atlas-nav a:hover{color:var(--gold-ink);text-decoration:underline;text-underline-offset:4px}'
           '.atlas-nav a[aria-current="page"]{color:var(--gold-ink);font-weight:700;box-shadow:inset 0 -3px var(--gold-ui,var(--gold))}'
           '.atlas-nav .livre{margin-left:auto}.atlas-nav .livre a{color:var(--muted)}'
           '@media (max-width:880px){.atlas-nav ul{flex-wrap:nowrap;overflow-x:auto;scrollbar-width:none;'
           '-webkit-mask-image:linear-gradient(90deg,#000 90%,transparent);mask-image:linear-gradient(90deg,#000 90%,transparent)}'
           '.atlas-nav ul::-webkit-scrollbar{display:none}.atlas-nav .livre{margin-left:0}.atlas-nav li:last-child{padding-right:28px}}'
           '.atlas-suite{display:grid;grid-template-columns:minmax(0,1fr) auto minmax(0,1fr);gap:12px 18px;align-items:center}'
           '.atlas-suite a{display:grid;gap:2px;padding:12px 16px;min-height:44px;border:1px solid var(--rule);border-radius:12px;'
           'background:var(--sheet);color:var(--ink);text-decoration:none}'
           '.atlas-suite a:hover{border-color:var(--muted)}'
           '.atlas-suite .s-lbl{font:500 .72rem/1.3 var(--font-mono);letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}'
           '.atlas-suite .s-nom{font:600 1.15rem/1.2 var(--font-display);color:var(--gold-ink)}'
           '.atlas-suite .suiv{text-align:right}'
           '.atlas-suite .etape{display:grid;gap:8px;justify-items:center;text-align:center}'
           '.atlas-suite .etape p{margin:0;font:500 .74rem/1.3 var(--font-mono);letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}'
           '.atlas-suite .etape a.livre{display:inline;padding:0;min-height:0;border:0;background:none;color:var(--gold-ink);'
           'font:500 .95rem/1.3 var(--font-body);text-decoration:underline;text-underline-offset:3px}'
           '@media (max-width:640px){.atlas-suite{grid-template-columns:minmax(0,1fr)}.atlas-suite .etape{order:-1;justify-items:start;text-align:left}'
           '.atlas-suite .suiv{text-align:left}}'
           'a.ref-lien{padding-block:5px}</style>')
NAV_JS = ('<script>(function(){var u=document.querySelector(".atlas-nav ul"),c=u&&u.querySelector("[aria-current]");'
          'if(c&&u.scrollWidth>u.clientWidth){var li=c.parentNode;u.scrollLeft=li.offsetLeft-(u.clientWidth-li.offsetWidth)/2;}})();</script>')


def esc(s):
    return s.replace('&', '&amp;').replace('"', '&quot;').replace('<', '&lt;')


# ── Typographie française ───────────────────────────────────────────────────────────────────────
NBSP, NNBSP = ' ', ' '


def typo(s):
    """Espace insécable devant « : » et à l'intérieur des guillemets « », espace fine insécable devant ; ! ?
    Seules les espaces déjà présentes sont remplacées (sauf dans les guillemets) : « 57:6.5 », « a:hover »,
    « 12:30 » ou une adresse ne contiennent pas d'espace devant le deux-points et restent intacts."""
    s = re.sub(r'[  ](?=:(?:[\s  ]|&nbsp;|$))', NBSP, s)
    s = re.sub(r'(?: | |&nbsp;)(?=[;!?])', NNBSP, s)
    s = re.sub(r'«[  ]', '«' + NBSP, s)
    s = re.sub(r'[  ]»', NBSP + '»', s)
    s = re.sub(r'«(?=[^\s  &<])', '«' + NBSP, s)
    s = re.sub(r'(?<=[^\s  ;>])»', NBSP + '»', s)
    return s


def typo_js(s):
    """Chaîne d'un script : seules les chaînes de texte sont retouchées (ni adresse, ni CSS, ni nombre)."""
    if '://' in s or '{' in s or not re.search(r'[A-Za-zÀ-ÿ]', s):
        return s
    return typo(s)


REGEX_APRES = set('(,=:[!&|?{};+-*%<>~^')
MOT_AVANT_REGEX = re.compile(r'(?:^|[^\w$])(?:return|typeof|case|do|else|in|of|new|delete|void|throw)\s*$')


def js_chaines(code, f):
    """Applique f au contenu de chaque chaîne '…' ou "…" d'un code JavaScript, en sautant commentaires,
    gabarits `…` et expressions régulières littérales."""
    out, i, n, prev = [], 0, len(code), ''
    while i < n:
        c = code[i]
        if c in '"\'':
            j = i + 1
            while j < n and code[j] != c and code[j] != '\n':
                j += 2 if code[j] == '\\' else 1
            out.append(c + f(code[i + 1:j]) + (code[j] if j < n else ''))
            i, prev = j + 1, c
            continue
        if c == '`':
            j = i + 1
            while j < n and code[j] != '`':
                j += 2 if code[j] == '\\' else 1
            out.append(code[i:j + 1])
            i, prev = j + 1, '`'
            continue
        if c == '/' and code[i + 1:i + 2] == '/':
            j = code.find('\n', i)
            j = n if j < 0 else j
            out.append(code[i:j])
            i = j
            continue
        if c == '/' and code[i + 1:i + 2] == '*':
            j = code.find('*/', i + 2)
            j = n if j < 0 else j + 2
            out.append(code[i:j])
            i = j
            continue
        if c == '/' and (prev == '' or prev in REGEX_APRES or MOT_AVANT_REGEX.search(code[max(0, i - 12):i])):
            j, classe = i + 1, False
            while j < n and code[j] != '\n':
                d = code[j]
                if d == '\\':
                    j += 2
                    continue
                if d == '[':
                    classe = True
                elif d == ']':
                    classe = False
                elif d == '/' and not classe:
                    break
                j += 1
            j += 1
            while j < n and code[j].isalpha():
                j += 1
            out.append(code[i:j])
            i, prev = j, '/'
            continue
        out.append(c)
        if not c.isspace():
            prev = c
        i += 1
    return ''.join(out)


JETONS = re.compile(r'<!--.*?-->|<script\b[^>]*>.*?</script>|<style\b[^>]*>.*?</style>'
                    r'|<(?:pre|code|kbd|textarea)\b[^>]*>.*?</(?:pre|code|kbd|textarea)>'
                    r'|<(?:[^>"\']|"[^"]*"|\'[^\']*\')*>', re.S | re.I)


def passe_typo(html, js=True):
    """Typographie du texte HTML (hors balises, styles et commentaires) et, si js, des chaînes des scripts
    en ligne (sauf le script partagé des références, publié à part)."""
    out, pos = [], 0
    for m in JETONS.finditer(html):
        out.append(typo(html[pos:m.start()]))
        t = m.group(0)
        if js and t[:7].lower() == '<script':
            k = t.index('>') + 1
            if 'src=' not in t[:k] and 'refs-urantia' not in t[:k]:
                t = t[:k] + js_chaines(t[k:-len('</script>')], typo_js) + t[-len('</script>'):]
        out.append(t)
        pos = m.end()
    out.append(typo(html[pos:]))
    return ''.join(out)


# ── Navigation commune ──────────────────────────────────────────────────────────────────────────
def barre(name, pages):
    lis = []
    for _, n, nom, court, _ in pages:
        cur = ' aria-current="page"' if n == name else ''
        tit = f' title="{nom}"' if court != nom else ''
        lis.append(f'<li><a href="{n}"{tit}{cur}>{court}</a></li>')
    lis.append(f'<li class="livre"><a href="{LIVRE[0]}" target="_blank" rel="noopener" '
               f'title="{LIVRE[1]}, nouvel onglet">{LIVRE[2]}&nbsp;↗</a></li>')
    return ('<a class="aller-contenu" href="#contenu">Aller au contenu</a>\n'
            f'<nav class="atlas-nav" aria-label="Pages de l’atlas"><ul>{"".join(lis)}</ul></nav>\n' + NAV_JS + '\n')


def parcours(name, presents):
    etapes = [(a, nom) for a, nom in PARCOURS if a.split('#')[0] in presents]
    adresses = [a for a, _ in etapes]
    if name not in adresses:
        return None, None
    i = adresses.index(name)
    prec = etapes[i - 1] if i else ('index.html', 'Accueil')
    suiv = etapes[i + 1] if i + 1 < len(etapes) else ('index.html', 'Accueil')
    lp = 'Étape précédente' if i else 'Retour'
    ls = 'Étape suivante' if i + 1 < len(etapes) else 'Fin du parcours'
    etape = f'Étape {i + 1} sur {len(etapes)}'
    nav = ('<nav class="atlas-suite" aria-label="Parcours de découverte">'
           f'<a class="prec" href="{prec[0]}"><span class="s-lbl">← {lp}</span><span class="s-nom">{prec[1]}</span></a>'
           f'<div class="etape"><p>Parcours de découverte · {etape}</p>'
           f'<a class="livre" href="{LIVRE[0]}" target="_blank" rel="noopener" aria-label="{LIVRE[1]}, nouvel onglet">{LIVRE[1]}&nbsp;↗</a></div>'
           f'<a class="suiv" href="{suiv[0]}"><span class="s-lbl">{ls} →</span><span class="s-nom">{suiv[1]}</span></a></nav>\n')
    return nav, etape


def assurer_main(body, name, problems):
    """Garantit un <main id="contenu"> : celui de la page, ou le conteneur .wrap converti."""
    m = re.search(r'<main\b[^>]*>', body)
    if m:
        if 'id=' not in m.group(0):
            body = body[:m.start()] + m.group(0)[:-1] + ' id="contenu">' + body[m.end():]
        return body
    m = re.search(r'<div class="wrap"[^>]*>', body)
    if not m:
        problems.append(f'{name} : ni <main> ni <div class="wrap"> pour le lien « Aller au contenu »')
        return body
    fin = body.find('<script', m.end())
    fin = len(body) if fin < 0 else fin
    k = body.rfind('</div>', m.end(), fin)
    zone = body[m.end():k]
    if k < 0 or len(re.findall(r'<div\b', zone)) != len(re.findall(r'</div>', zone)):
        problems.append(f'{name} : conteneur .wrap non apparié, <main> non posé')
        return body[:m.start()] + m.group(0).replace('<div ', '<div id="contenu" ', 1) + body[m.end():]
    ouv = m.group(0).replace('<div ', '<main id="contenu" ', 1)
    return body[:m.start()] + ouv + zone + '</main>' + body[k + len('</div>'):]


def taille_png(p):
    with open(p, 'rb') as f:
        d = f.read(24)
    return struct.unpack('>II', d[16:24])


# ── Construction ────────────────────────────────────────────────────────────────────────────────
artefacts = {}
if (SRC / 'artefacts.json').exists():
    artefacts = {k: v for k, v in json.loads((SRC / 'artefacts.json').read_text(encoding='utf-8')).items() if not k.startswith('_')}
present = [p for p in PAGES if (SRC / p[0]).exists()]
noms = {p[1] for p in present}
urlmap = {artefacts[f]: n for (f, n, _, _, _) in present if f in artefacts}
problems = []
OUT.mkdir(parents=True, exist_ok=True)
apercu_wh = taille_png(SRC / 'site' / 'apercu.png') if (SRC / 'site' / 'apercu.png').exists() else (1200, 630)


def adresses_locales(html):
    """Adresses claude.ai et CDN remplacées par des liens relatifs ; liens internes dans le même onglet."""
    for u, n in urlmap.items():
        html = html.replace(u, n)
    for u, n in CDN.items():
        html = html.replace(u, n)

    def same_tab(m):
        tag = m.group(0)
        href = re.search(r'href="([^"]*)"', tag)
        if href and re.match(r'^[a-z0-9-]+\.html(#[a-z0-9-]*)?$', href.group(1)):
            tag = tag.replace(' target="_blank"', '').replace(' rel="noopener"', '')
        return tag
    html = re.sub(r'<a\b[^>]*>', same_tab, html)
    # liens construits en JavaScript vers une page du site (var F3D = "atlas-3d.html#frise" ; '<a href=\"' + F3D + '\" target=…')
    for var, _ in re.findall(r'\bvar (\w+) = "([a-z0-9-]+\.html(?:#[a-z0-9-]*)?)"', html):
        html = html.replace(var + ' + "\\" target=\\"_blank\\" rel=\\"noopener\\"', var + ' + "\\"')
    return html


for fichier, name, nom, _, desc in present:
    html = adresses_locales((SRC / fichier).read_text(encoding='utf-8'))
    html = re.sub(r'<link rel="preconnect" href="https://fonts\.(googleapis|gstatic)\.com"( crossorigin)?>\s*', '', html)
    html = re.sub(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com/css2\?[^"]*">',
                  '<link rel="stylesheet" href="assets/fonts/fonts.css">', html)
    html = re.sub(r'<meta name="claude:[^"]*"[^>]*>\s*', '', html)
    # rangées de liens propres aux artefacts claude.ai : la barre commune les remplace dans le site
    html = re.sub(r'\s*<(p|div|span|li)\b[^>]*\sdata-artefact\b[^>]*>.*?</\1>', '', html, flags=re.S)
    titre = NOM_SITE if name == 'index.html' else f'{nom} — {NOM_SITE}'
    html = re.sub(r'<title>.*?</title>', f'<title>{titre}</title>', html, count=1, flags=re.S)
    html = passe_typo(html, js=name not in SANS_TYPO_JS)
    # script des références : un fichier partagé dans le site (les sources gardent le bloc en ligne pour claude.ai)
    html = re.sub(r'<script id="refs-urantia">.*?</script>', '<script src="assets/refs-urantia.js" defer></script>', html, flags=re.S)
    cut = html.index('</style>') + len('</style>')
    head, body = html[:cut], html[cut:]
    if name not in SANS_BARRE:
        head += NAV_CSS
        body = assurer_main(body, name, problems)
        suite, etape = parcours(name, noms)
        if suite:
            k = body.find('<footer class="foot"')
            k = k if k >= 0 else body.find('</main>')
            body = body[:k] + suite + body[k:]
            body = body.replace('<span data-etape></span>', f'<span data-etape>{etape} · </span>', 1)
        body = barre(name, present) + body.lstrip()
    url = BASE + ('' if name == 'index.html' else name)
    meta = ('<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            f'<meta name="description" content="{esc(desc)}">\n'
            f'<link rel="canonical" href="{url}">\n'
            '<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">\n'
            '<link rel="apple-touch-icon" href="assets/apple-touch-icon.png">\n'
            f'<meta property="og:type" content="website">\n<meta property="og:locale" content="fr_FR">\n'
            f'<meta property="og:site_name" content="{esc(NOM_SITE)}">\n'
            f'<meta property="og:title" content="{esc(titre)}">\n<meta property="og:description" content="{esc(desc)}">\n'
            f'<meta property="og:url" content="{url}">\n'
            f'<meta property="og:image" content="{BASE}assets/apercu.png">\n'
            f'<meta property="og:image:width" content="{apercu_wh[0]}">\n<meta property="og:image:height" content="{apercu_wh[1]}">\n'
            f'<meta property="og:image:alt" content="{esc(APERCU_ALT)}">\n'
            '<meta name="twitter:card" content="summary_large_image">\n'
            f'<meta name="twitter:image:alt" content="{esc(APERCU_ALT)}">\n')
    page = ('<!doctype html>\n<html lang="fr">\n<head>\n' + meta + RESET + '\n' + head.strip() +
            '\n</head>\n<body>\n' + body.strip() + '\n</body>\n</html>\n')
    for bad in ('claude.ai', 'fonts.googleapis', 'fonts.gstatic', 'cdnjs.cloudflare', 'cdn.jsdelivr'):
        if bad in page:
            problems.append(f'{name} : reste une adresse « {bad} »')
    for href in re.findall(r'href="([a-z0-9-]+\.html)(?:#[^"]*)?"', page):
        if href not in noms:
            problems.append(f'{name} : lien vers une page absente ({href})')
    for t in re.findall(r'<a\b[^>]*href="[a-z0-9-]+\.html[^"]*"[^>]*target="_blank"[^>]*>', page):
        problems.append(f'{name} : lien interne ouvert dans un nouvel onglet ({t[:80]})')
    if '\\" target=\\"_blank\\"' in page and re.search(r'href=\\"" \+ \w+ \+ "\\" target', page):
        problems.append(f'{name} : lien interne construit en JavaScript ouvert dans un nouvel onglet')
    (OUT / name).write_text(page, encoding='utf-8')
    print(f'page : {name:32} {round(len(page.encode("utf-8")) / 1024):5} Ko')

# Page 404 de GitHub Pages : adresses absolues, car elle est servie à n'importe quelle profondeur
liste = ''.join(f'<li><a href="{BASE}{"" if n == "index.html" else n}">{nom}</a></li>' for _, n, nom, _, _ in present)
p404 = f'''<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>Page introuvable — {NOM_SITE}</title>
<link rel="icon" href="{BASE}assets/favicon.svg" type="image/svg+xml">
<style>
:root {{ --paper: #EEF1F6; --sheet: #FFFFFF; --ink: #18213B; --muted: #56607D; --rule: #CBD2E0; --gold-ink: #8A5A00; color-scheme: light; }}
@media (prefers-color-scheme: dark) {{ :root {{ --paper: #0C1120; --sheet: #131A2E; --ink: #E6E9F2; --muted: #9AA4C0; --rule: #28314B; --gold-ink: #F4C664; color-scheme: dark; }} }}
body {{ margin: 0; background: var(--paper); color: var(--ink); font: 17px/1.6 "Segoe UI", "Helvetica Neue", Arial, sans-serif; }}
main {{ max-width: 640px; margin: 0 auto; padding: 64px 16px; display: grid; gap: 18px; }}
h1 {{ margin: 0; font: 600 2.2rem/1.1 Georgia, serif; }}
p {{ margin: 0; }}
a {{ color: var(--gold-ink); text-underline-offset: 3px; }}
ul {{ margin: 0; padding-left: 20px; display: grid; gap: 6px; }}
.home {{ display: inline-block; padding: 12px 20px; border-radius: 999px; background: var(--ink); color: var(--paper); text-decoration: none; font-weight: 600; }}
</style>
</head>
<body>
<main>
<p>{NOM_SITE}</p>
<h1>Page introuvable</h1>
<p>Cette adresse ne correspond à aucune page de l’atlas. Elle a peut-être changé de nom.</p>
<p><a class="home" href="{BASE}">Revenir à l’accueil de l’atlas</a></p>
<ul>{liste}</ul>
</main>
</body>
</html>
'''
(OUT / '404.html').write_text(passe_typo(p404, js=False), encoding='utf-8')

assets = OUT / 'assets'
(assets / 'lib').mkdir(parents=True, exist_ok=True)
fonts = assets / 'fonts'
if fonts.exists():
    shutil.rmtree(fonts)              # les anciens fichiers de polices ne doivent pas rester
fonts.mkdir(parents=True)
for f in ('three.min.js', 'OrbitControls.js', 'LICENSE-three.txt'):
    shutil.copy2(LIB / f, assets / 'lib' / f)
for f in (SRC / 'polices').iterdir():
    shutil.copy2(f, fonts / f.name)
for f in ACTIFS:
    if (SRC / 'site' / f).exists():
        shutil.copy2(SRC / 'site' / f, assets / f)
    else:
        problems.append(f'fichier absent : site/{f}')
shutil.copy2(SRC / 'refs-urantia.js', assets / 'refs-urantia.js')
for f in RACINE:
    if (SRC / 'site' / f).exists():
        shutil.copy2(SRC / 'site' / f, OUT / f)
    else:
        problems.append(f'fichier absent : site/{f}')
(OUT / '.nojekyll').write_text('', encoding='utf-8')
sources = OUT / 'sources'
sources.mkdir(exist_ok=True)
for f in SOURCES:
    if not (SRC / f).exists():
        problems.append(f'source absente : {f}')
        continue
    if f.endswith(('.html', '.py', '.js', '.md', '.txt')):
        texte = (SRC / f).read_text(encoding='utf-8')
        if f.endswith('.html'):
            texte = re.sub(r'<meta name="claude:[^"]*"[^>]*>\s*', '', adresses_locales(texte))
        (sources / f).write_text(texte, encoding='utf-8', newline='\n')
    else:
        shutil.copy2(SRC / f, sources / f)
for p in OUT.rglob('*'):
    if p.is_file() and p.suffix in ('.html', '.js', '.py', '.md', '.txt', '.css') and '.git' not in p.parts:
        if 'claude.ai/' + 'artifact' in p.read_text(encoding='utf-8', errors='ignore'):   # écrit en deux morceaux pour ne pas se signaler lui-même
            problems.append(f'{p.relative_to(OUT)} : contient encore une adresse d’artefact claude.ai')
print('\n'.join(problems) if problems else 'vérification : aucune adresse externe à remplacer, aucun lien interne cassé')
