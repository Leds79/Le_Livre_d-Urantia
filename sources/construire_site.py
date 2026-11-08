"""Construit le site statique « Le Livre d'Urantia en images » à partir des pages publiées.

Chaque page reçoit un squelette HTML complet (métadonnées de partage, lien « Aller au contenu », barre de
navigation commune, parcours de découverte), une passe de typographie française, des liens relatifs qui
s'ouvrent dans le même onglet et des ressources locales (assets/) : le site s'ouvre hors ligne (index.html)
et se publie tel quel sur GitHub Pages. Les sources sont copiées dans sources/, sans les adresses claude.ai.
Le site est aussi une application web installable (PWA) : manifest.webmanifest, sw.js (service worker écrit à
chaque construction, VERSION = empreinte du contenu), hors-ligne.html, assets/hors-ligne.js et, sur l'accueil,
l'encadré « Lire hors ligne ». Chaque page porte le crédit de l'auteur et le lien du dépôt GitHub.

Usage : python -I construire_site.py <dossier source de l'atlas> <dossier du site>
Le dossier source contient les pages publiées, polices/ (fonts.css, fichiers WOFF2, OFL), site/ (README,
LICENCES, LICENSE, favicon, aperçu…), refs-urantia.js et, hors publication, artefacts.json (adresses des
pages publiées sur claude.ai) ; ../lib contient Three.js et sa licence. Détail : sources/CONSTRUIRE.md."""
import hashlib
import json
import re
import shutil
import struct
import sys
import urllib.parse
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')  # messages lisibles dans toutes les consoles
sys.stderr.reconfigure(encoding='utf-8')

SRC, OUT = Path(sys.argv[1]), Path(sys.argv[2])
# Deux dispositions possibles :
# - la copie de travail de l'auteur : visuels/source/ avec site/, polices/ et ../lib (pages maîtresses, adresses claude.ai) ;
# - un clone du dépôt : sources/ (pages nettoyées), les ressources étant celles du site publié (racine et assets/).
MODE_DEPOT = not (SRC / 'site').exists() and (SRC.parent / 'assets' / 'lib').exists()
ENTREES = SRC.parent if MODE_DEPOT else SRC / 'site'                    # README, licences, CONTRIBUER.md, .github/
ACTIFS_DIR = SRC.parent / 'assets' if MODE_DEPOT else SRC / 'site'      # favicon, icônes, aperçu
POLICES = SRC.parent / 'assets' / 'fonts' if MODE_DEPOT else SRC / 'polices'
LIB = SRC.parent / 'assets' / 'lib' if MODE_DEPOT else SRC.parent / 'lib'
if OUT.resolve() in (SRC.resolve(), SRC.parent.resolve() if MODE_DEPOT else None) or (OUT / 'sources').resolve() == SRC.resolve():
    sys.exit('Dossier de sortie refusé : il contient les sources (construction sur soi-même). '
             'Exemple, depuis la racine du dépôt : python -I sources/construire_site.py sources ../atlas-site')
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
     'Cent parallèles entre la Bible (Crampon 1923) et le Livre d’Urantia, de la Création à l’Apocalypse : ce qui concorde, ce qui diffère, et ce que le livre en dit.'),
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
# Copiés dans sources/ : de quoi reconstruire tout le site depuis un clone du dépôt. Les pages y sont nettoyées
# (adresses claude.ai rendues relatives, rangées data-artefact et balises claude: retirées).
SOURCES = [p[0] for p in PAGES if p[0] != 'urantia-paradis-3d.html'] + [
           'urantia-paradis-3d.src.html', 'etoiles.json', 'geo.json', 'tex.json', 'liens_refs.py', 'refs-urantia.js',
           'hors-ligne.js', 'musique.js', 'assembler.py', 'etoiles.py', 'geo.py', 'textures.py', 'polices.py', 'smoke3d.js',
           'construire_site.py', 'CONSTRUIRE.md', 'requirements.txt']
RACINE = ['README.md', 'LICENCES.md', 'LICENSE', 'LICENSE-CONTENU.md', 'CONTRIBUER.md']   # copiés de site/ à la racine du site
GITHUB = ['.github/ISSUE_TEMPLATE/erreur.yml', '.github/ISSUE_TEMPLATE/idee.yml', '.github/ISSUE_TEMPLATE/config.yml',
          '.github/pull_request_template.md']                                           # formulaires de tickets, modèle de demande
# Crédit et dépôt (pied commun de chaque page, sauf la vue 3D qui a son menu)
AUTEUR = 'Sylvain Leduc'
DEPOT = 'https://github.com/Leds79/Le_Livre_d-Urantia'
DEPOT_LICENCES = DEPOT + '/blob/main/LICENCES.md'
# Application installable (PWA)
NOM_COURT = 'Atlas Urantia'
THEME = {'clair': '#FFFFFF', 'sombre': '#131A2E', '3d': '#03050C', 'appli': '#0C1120'}   # barre du navigateur, écran de lancement
ICONES = [('icone-192.png', '192x192', 'any'), ('icone-512.png', '512x512', 'any'),
          ('icone-512-maskable.png', '512x512', 'maskable')]                  # rendus de favicon.svg (site/)
ACTIFS = ['favicon.svg', 'apercu.png', 'apple-touch-icon.png'] + [i[0] for i in ICONES]   # copiés de site/ dans assets/
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
           '.atlas-nav .musique{margin-left:auto}.atlas-nav .musique+.livre{margin-left:0}'
           '.atlas-musique{appearance:none;display:inline-flex;align-items:center;justify-content:center;width:44px;height:44px;'
           'margin:0;padding:0;border:0;border-radius:999px;background:none;color:var(--muted);cursor:pointer}'
           '.atlas-musique:hover{color:var(--gold-ink)}'
           '.atlas-musique:focus-visible{outline:2px solid var(--gold-ink);outline-offset:-2px}'
           '.atlas-musique[aria-pressed="true"]{color:var(--gold-ink);box-shadow:inset 0 0 0 2px var(--gold-ui,var(--gold))}'
           '.atlas-musique svg{display:block;width:20px;height:20px}'
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
           '.atlas-suite .etape a.livre{display:inline-flex;align-items:center;min-height:44px;padding:0;border:0;background:none;color:var(--gold-ink);'
           'font:500 .95rem/1.3 var(--font-body);text-decoration:underline;text-underline-offset:3px}'
           '@media (max-width:640px){.atlas-suite{grid-template-columns:minmax(0,1fr)}.atlas-suite .etape{order:-1;justify-items:start;text-align:left}'
           '.atlas-suite .suiv{text-align:left}}'
           '.atlas-credit{margin:0;display:flex;flex-wrap:wrap;align-items:center;column-gap:.45em}'
           '.atlas-credit a{display:inline-flex;align-items:center;min-height:44px;color:var(--gold-ink);'
           'text-decoration:underline;text-underline-offset:3px}'
           '.atlas-credit .atlas-note{font-size:.92em}'
           '.atlas-droits{margin:0}'
           '.atlas-droits a{padding-block:12px;color:var(--gold-ink);text-decoration:underline;text-underline-offset:3px}'
           'a.ref-lien{padding-block:5px}</style>')
def signaler(name, nom):
    """Adresse du formulaire « Signaler une erreur » (.github/ISSUE_TEMPLATE/erreur.yml), titre et page pré-remplis."""
    q = urllib.parse.urlencode({'template': 'erreur.yml', 'title': f'[Erreur] {nom}', 'page': f'{nom} ({name})'},
                               quote_via=urllib.parse.quote)
    return f'{DEPOT}/issues/new?{q}'


def pied(name, nom, droits='index.html#droits'):
    """Lignes de crédit et de droits, ajoutées à la fin du pied de chaque page (texte déjà typographié : posées après
    la passe de typographie). Les liens externes s'ouvrent dans un nouvel onglet ; le signalement demande un compte
    GitHub. La ligne de droits renvoie à la déclaration de la Fondation Urantia, sur l'accueil."""
    sep = ' <span aria-hidden="true">·</span> '
    return pied_credit(name, nom, sep) + (f'\n<p class="atlas-droits">Citations du <i>Livre d’Urantia</i>&nbsp;: traduction française '
                                          f'©&nbsp;1960 Urantia Foundation{sep}<a href="{droits}">droits</a></p>')


def pied_credit(name, nom, sep):
    return (f'<p class="atlas-credit">Une gracieuseté de {AUTEUR}{sep}'
            f'<a href="{DEPOT}" target="_blank" rel="noopener" aria-label="Code source libre sur GitHub, nouvel onglet">'
            f'Code source libre sur GitHub&nbsp;↗</a>{sep}'
            f'<a href="{DEPOT_LICENCES}" target="_blank" rel="noopener" aria-label="Licences, nouvel onglet">Licences</a>{sep}'
            f'<a href="{esc(signaler(name, nom))}" target="_blank" rel="noopener" '
            'title="Formulaire sur GitHub : un compte GitHub est nécessaire" '
            'aria-label="Signaler une erreur sur cette page, formulaire GitHub (compte nécessaire), nouvel onglet">'
            'Signaler une erreur sur cette page&nbsp;↗</a> <span class="atlas-note">(compte GitHub)</span></p>')
# Encadré « Lire hors ligne » de l'accueil (posé avant la passe de typographie ; la taille est inscrite en fin de construction)
HL_HTML = ('<aside class="hl" id="hors-ligne" aria-labelledby="hl-titre" hidden>\n'
           '<h2 id="hl-titre">Lire hors ligne</h2>\n'
           '<p class="hl-txt">Installe l’atlas comme une application, ou enregistre-le sur cet appareil pour le lire sans réseau. '
           'Les liens vers le texte du livre, sur urantia.org, demandent toujours Internet.</p>\n'
           '<div class="hl-btns">\n'
           '<button type="button" class="hl-btn hl-inst" id="hl-installer" hidden>Installer l’application</button>\n'
           '<button type="button" class="hl-btn" id="hl-telecharger">Télécharger pour lire hors ligne '
           '(≈&nbsp;__TAILLE_HORS_LIGNE__&nbsp;Mo)</button>\n'
           '</div>\n'
           '<progress id="hl-barre" max="100" value="0" aria-label="Progression du téléchargement" hidden></progress>\n'
           '<p class="hl-etat" id="hl-etat" aria-live="polite"></p>\n'
           '<p class="hl-ios" id="hl-ios" hidden>Sur iPhone ou iPad : dans Safari, touche Partager, puis « Sur l’écran d’accueil ».</p>\n'
           '</aside>\n')
HL_CSS = ('<style>/* encadré « Lire hors ligne » (construire_site.py) */'
          '.hl{padding:20px 22px;border:1px solid var(--rule);border-radius:14px;background:var(--sheet);display:grid;gap:12px;max-width:84ch}'
          '.hl h2{margin:0;font:600 1.45rem/1.15 var(--font-display);color:var(--ink)}'
          '.hl p{margin:0}.hl-txt{color:var(--muted);font-size:.98rem;line-height:1.5}'
          '.hl-btns{display:flex;flex-wrap:wrap;gap:10px}'
          '.hl-btn{appearance:none;display:inline-flex;align-items:center;min-height:44px;padding:10px 18px;border-radius:999px;'
          'border:1px solid var(--rule);background:var(--paper);color:var(--ink);font:600 .95rem/1.25 var(--font-body);cursor:pointer;text-align:left}'
          '.hl-btn:hover{border-color:var(--muted)}.hl-btn:disabled{opacity:.6;cursor:progress}'
          '.hl-inst{background:var(--gold);border-color:var(--gold);color:var(--on-gold)}'
          '.hl progress{width:100%;height:10px;accent-color:var(--gold)}'
          '.hl-etat{font-size:.95rem;color:var(--muted)}.hl-etat:empty{display:none}.hl-etat.ok{color:var(--ink);font-weight:600}'
          '.hl-ios{font-size:.92rem;color:var(--muted)}</style>')
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
    # musique douce (assets/musique.js la démasque si le navigateur produit le son)
    lis.append('<li class="musique"><button type="button" class="atlas-musique" data-musique hidden aria-pressed="false" '
               'aria-label="Musique douce"><svg viewBox="0 0 20 20" aria-hidden="true" focusable="false">'
               '<ellipse cx="7" cy="15" rx="3.6" ry="2.7" transform="rotate(-20 7 15)" fill="currentColor"/>'
               '<path d="M10.2 14.6V3.2c2.5 1.3 4.7 2.6 5.5 5.6" fill="none" stroke="currentColor" stroke-width="1.8" '
               'stroke-linecap="round" stroke-linejoin="round"/></svg></button></li>')
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


# Service worker (sw.js), complété à chaque construction : VERSION, FICHIERS (tout l'atlas), NOYAU (installation).
SW_GABARIT = r'''/* Service worker de « Le Livre d’Urantia en images » : lecture hors ligne et installation.
   Écrit par construire_site.py à chaque construction : ne pas le modifier à la main.
   VERSION est l’empreinte du contenu des fichiers listés ; elle change dès que l’un d’eux change. */
'use strict';
const VERSION = '__VERSION__';
const PREFIXE = 'atlas-urantia-';
const CACHE = PREFIXE + VERSION;
// tout l’atlas, pour le téléchargement complet : chemin → [octets, empreinte]
const FICHIERS = __FICHIERS__;
// enregistrés dès l’installation : accueil, page hors ligne, manifeste, scripts communs, icônes, polices
const NOYAU = __NOYAU__;
const HORS_LIGNE = 'hors-ligne.html';
const DELAI_RESEAU = 3000;                 // navigations : au-delà, la copie enregistrée est servie
const PORTEE = new URL('./', self.location.href).href;
const abs = (p) => new URL(p, PORTEE).href;
const EMPREINTES = abs('__atlas__/empreintes.json');   // entrées internes du cache
const COMPLET = abs('__atlas__/complet');
const LISTE = Object.keys(FICHIERS);
const TOTAL = LISTE.reduce((s, p) => s + FICHIERS[p][0], 0);
let enCours = null;

// adresse normalisée : sans requête ni ancre ; « dossier/ » devient « dossier/index.html »
function cle(u) {
  const x = new URL(u);
  x.hash = '';
  x.search = '';
  if (x.pathname.endsWith('/')) x.pathname += 'index.html';
  return x.href;
}
async function recuperer(p) {              // revalidé auprès du serveur : jamais une copie périmée du cache HTTP
  const r = await fetch(abs(p), { cache: 'no-cache' });
  if (!r.ok) throw new Error(p + ' : ' + r.status);
  return r;
}
async function present(cache, p) { return !!(await cache.match(abs(p))); }

self.addEventListener('install', (e) => {
  self.skipWaiting();
  e.waitUntil((async () => {
    const cache = await caches.open(CACHE);
    await Promise.all(NOYAU.map(async (p) => { await cache.put(abs(p), await recuperer(p)); }));
    // version précédente : ce qui y était enregistré est repris, copié s’il n’a pas changé, téléchargé de nouveau sinon
    for (const nom of (await caches.keys()).filter((k) => k.startsWith(PREFIXE) && k !== CACHE)) {
      const ancien = await caches.open(nom);
      let emp = {};
      try { const r = await ancien.match(EMPREINTES); if (r) emp = await r.json(); } catch (err) { /* tout est retéléchargé */ }
      for (const p of LISTE) {
        if (await present(cache, p)) continue;
        const r = await ancien.match(abs(p));
        if (!r) continue;
        try { await cache.put(abs(p), emp[p] === FICHIERS[p][1] ? r : await recuperer(p)); } catch (err) { /* repris au prochain téléchargement */ }
      }
    }
    await cache.put(EMPREINTES, new Response(JSON.stringify(Object.fromEntries(LISTE.map((p) => [p, FICHIERS[p][1]])))));
    let complet = true;
    for (const p of LISTE) if (!(await present(cache, p))) { complet = false; break; }
    if (complet) await cache.put(COMPLET, new Response(VERSION));
  })());
});

self.addEventListener('activate', (e) => {
  e.waitUntil((async () => {
    const vieux = (await caches.keys()).filter((k) => k.startsWith(PREFIXE) && k !== CACHE);
    await Promise.all(vieux.map((k) => caches.delete(k)));
    await self.clients.claim();
  })());
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;
  if (req.cache === 'only-if-cached' && req.mode !== 'same-origin') return;
  const u = new URL(req.url);
  if (u.origin !== self.location.origin || !req.url.startsWith(PORTEE)) return;   // autres sites (urantia.org…) : jamais en cache
  e.respondWith(req.mode === 'navigate' ? navigation(e) : ressource(e));
});

// navigations : le réseau d’abord (3 s au plus), puis la copie enregistrée, puis la page hors ligne
function navigation(e) {
  const k = cle(e.request.url);
  const reseau = fetch(e.request).then((r) => {
    if (r.ok && r.type === 'basic') {
      const copie = r.clone();
      e.waitUntil(caches.open(CACHE).then((c) => c.put(k, copie)).catch(() => {}));
    }
    return r;
  });
  e.waitUntil(reseau.then(() => {}, () => {}));
  return (async () => {
    try {
      return await Promise.race([reseau, new Promise((_, non) => setTimeout(() => non(new Error('délai')), DELAI_RESEAU))]);
    } catch (err) {
      const copie = await caches.match(k, { cacheName: CACHE });
      if (copie) return copie;
      try { return await reseau; } catch (err2) { return horsLigne(); }
    }
  })();
}

// autres ressources du site : la copie enregistrée, sinon le réseau (et la réponse est enregistrée)
async function ressource(e) {
  const k = cle(e.request.url);
  const cache = await caches.open(CACHE);
  const copie = await cache.match(k);
  if (copie) return copie;
  const r = await fetch(e.request);
  if (r.ok && r.type === 'basic') e.waitUntil(cache.put(k, r.clone()).catch(() => {}));
  return r;
}

async function horsLigne() {
  const r = await caches.match(abs(HORS_LIGNE), { cacheName: CACHE });
  const t = r ? await r.text() : '<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>Hors ligne</title></head>'
    + '<body><p>Cette page n’est pas encore enregistrée pour la lecture hors ligne.</p></body></html>';
  return new Response(t.replace('<head>', '<head><base href="' + PORTEE + '">'), { headers: { 'Content-Type': 'text/html; charset=utf-8' } });
}

// messages de la page : état de l’enregistrement, téléchargement complet (avec progression)
self.addEventListener('message', (e) => {
  const d = e.data || {};
  if (d.type === 'etat') {
    e.waitUntil(etat().then((s) => { if (e.source) e.source.postMessage(s); }));
  } else if (d.type === 'telecharger') {
    if (!enCours) enCours = telecharger().finally(() => { enCours = null; });
    e.waitUntil(enCours);
  }
});
async function diffuser(m) {
  for (const c of await self.clients.matchAll({ type: 'window', includeUncontrolled: true })) c.postMessage(m);
}
async function etat() {
  const cache = await caches.open(CACHE);
  let n = 0, octets = 0;
  for (const p of LISTE) if (await present(cache, p)) { n++; octets += FICHIERS[p][0]; }
  return { type: 'etat', version: VERSION, enregistres: n, total: LISTE.length, octets, totalOctets: TOTAL,
    complet: n === LISTE.length, enCours: !!enCours };
}
async function telecharger() {
  const cache = await caches.open(CACHE);
  const manquants = [];
  let fait = 0, octets = 0, erreurs = 0;
  for (const p of LISTE) {
    if (await present(cache, p)) { fait++; octets += FICHIERS[p][0]; } else manquants.push(p);
  }
  const point = (type) => diffuser({ type, fait, total: LISTE.length, octets, totalOctets: TOTAL, erreurs, version: VERSION });
  await point('progression');
  let i = 0;
  const ouvrier = async () => {
    while (i < manquants.length) {
      const p = manquants[i++];
      try { await cache.put(abs(p), await recuperer(p)); } catch (err) { erreurs++; }
      fait++;
      octets += FICHIERS[p][0];
      await point('progression');
    }
  };
  await Promise.all([ouvrier(), ouvrier(), ouvrier()]);
  if (!erreurs) await cache.put(COMPLET, new Response(VERSION));
  await point(erreurs ? 'erreur' : 'termine');
}
'''


# ── Construction ────────────────────────────────────────────────────────────────────────────────
artefacts = {}
if (SRC / 'artefacts.json').exists():
    artefacts = {k: v for k, v in json.loads((SRC / 'artefacts.json').read_text(encoding='utf-8')).items() if not k.startswith('_')}
MARQUES_3D = (('/*__STARS__*/null', 'etoiles.json'), ('/*__GEO__*/null', 'geo.json'), ('/*__TEX__*/null', 'tex.json'))


def lire_source(fichier):
    """Texte d'une page source. Depuis un clone du dépôt, la vue 3D est assemblée à la volée (comme assembler.py) à
    partir de son gabarit et de ses données, faute de urantia-paradis-3d.html."""
    if fichier == 'urantia-paradis-3d.html' and not (SRC / fichier).exists():
        html = (SRC / 'urantia-paradis-3d.src.html').read_text(encoding='utf-8')
        for marque, donnees in MARQUES_3D:
            if marque in html:
                html = html.replace(marque, (SRC / donnees).read_text(encoding='utf-8').strip())
        return html
    return (SRC / fichier).read_text(encoding='utf-8')


present = [p for p in PAGES if (SRC / p[0]).exists()
           or (p[0] == 'urantia-paradis-3d.html' and (SRC / 'urantia-paradis-3d.src.html').exists())]
noms = {p[1] for p in present}
urlmap = {artefacts[f]: n for (f, n, _, _, _) in present if f in artefacts}
problems = []
OUT.mkdir(parents=True, exist_ok=True)
apercu_wh = taille_png(ACTIFS_DIR / 'apercu.png') if (ACTIFS_DIR / 'apercu.png').exists() else (1200, 630)


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
    html = adresses_locales(lire_source(fichier))
    html = re.sub(r'<link rel="preconnect" href="https://fonts\.(googleapis|gstatic)\.com"( crossorigin)?>\s*', '', html)
    html = re.sub(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com/css2\?[^"]*">',
                  '<link rel="stylesheet" href="assets/fonts/fonts.css">', html)
    html = re.sub(r'<meta name="claude:[^"]*"[^>]*>\s*', '', html)
    # rangées de liens propres aux artefacts claude.ai : la barre commune les remplace dans le site
    html = re.sub(r'\s*<(p|div|span|li)\b[^>]*\sdata-artefact\b[^>]*>.*?</\1>', '', html, flags=re.S)
    titre = NOM_SITE if name == 'index.html' else f'{nom} — {NOM_SITE}'
    html = re.sub(r'<title>.*?</title>', f'<title>{titre}</title>', html, count=1, flags=re.S)
    if name == 'index.html':          # encadré « Lire hors ligne » : avec le bloc de crédit (div.fin), sinon avant le pied
        k = html.find('<div class="fin">')
        k = k + len('<div class="fin">') if k >= 0 else html.find('<footer class="foot"')
        if k < 0:
            problems.append('index.html : ni div.fin ni footer.foot pour l’encadré « Lire hors ligne »')
        else:
            html = html[:k] + '\n' + HL_HTML + html[k:]
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
        # pied commun : crédit, dépôt GitHub, licences, signalement d'erreur
        k = body.find('<footer class="foot"')
        f = body.find('</footer>', k) if k >= 0 else -1
        if f >= 0:
            body = body[:f] + pied(name, nom) + '\n' + body[f:]
        else:
            m = body.rfind('</main>')
            body = body[:m] + f'<footer class="foot">{pied(name, nom)}</footer>\n' + body[m:]
        if name == 'index.html':
            head += HL_CSS
        body = barre(name, present) + body.lstrip()
    else:
        # vue 3D : lien « Signaler une erreur » ajouté au crédit de son menu, sans toucher au gabarit
        m = re.search(r'<p class="credit">(.*?)</p>', body, flags=re.S)
        if m and 'issues/new' not in m.group(1):
            lien = (f' · <a href="{esc(signaler(name, nom))}" target="_blank" rel="noopener" '
                    'title="Formulaire sur GitHub : un compte GitHub est nécessaire">'
                    'Signaler une erreur<span aria-hidden="true">&nbsp;↗</span></a>'
                    ' · <a href="index.html#droits" title="Citations du Livre d’Urantia : © 1960 Urantia Foundation">Droits</a>')
            body = body[:m.end(1)] + lien + body[m.end(1):]
        elif not m:
            problems.append(f'{name} : pas de <p class="credit"> dans le menu, lien « Signaler une erreur » non posé')
    url = BASE + ('' if name == 'index.html' else name)
    theme = (f'<meta name="theme-color" content="{THEME["3d"]}">\n' if name in SANS_BARRE else
             f'<meta name="theme-color" content="{THEME["clair"]}" media="(prefers-color-scheme: light)">\n'
             f'<meta name="theme-color" content="{THEME["sombre"]}" media="(prefers-color-scheme: dark)">\n')
    meta = ('<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            f'<meta name="description" content="{esc(desc)}">\n'
            f'<link rel="canonical" href="{url}">\n'
            '<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">\n'
            '<link rel="apple-touch-icon" href="assets/apple-touch-icon.png">\n'
            '<link rel="manifest" href="manifest.webmanifest">\n' + theme +
            '<meta name="mobile-web-app-capable" content="yes">\n'
            '<meta name="apple-mobile-web-app-capable" content="yes">\n'
            f'<meta name="apple-mobile-web-app-title" content="{NOM_COURT}">\n'
            '<meta name="apple-mobile-web-app-status-bar-style" content="default">\n'
            f'<meta name="author" content="{AUTEUR}">\n'
            f'<meta property="og:type" content="website">\n<meta property="og:locale" content="fr_FR">\n'
            f'<meta property="og:site_name" content="{esc(NOM_SITE)}">\n'
            f'<meta property="og:title" content="{esc(titre)}">\n<meta property="og:description" content="{esc(desc)}">\n'
            f'<meta property="og:url" content="{url}">\n'
            f'<meta property="og:image" content="{BASE}assets/apercu.png">\n'
            f'<meta property="og:image:width" content="{apercu_wh[0]}">\n<meta property="og:image:height" content="{apercu_wh[1]}">\n'
            f'<meta property="og:image:alt" content="{esc(APERCU_ALT)}">\n'
            '<meta name="twitter:card" content="summary_large_image">\n'
            f'<meta name="twitter:image:alt" content="{esc(APERCU_ALT)}">\n'
            '<script src="assets/hors-ligne.js" defer></script>\n'
            '<script src="assets/musique.js" defer></script>\n')
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
<meta name="author" content="{AUTEUR}">
<title>Page introuvable — {NOM_SITE}</title>
<link rel="icon" href="{BASE}assets/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{BASE}assets/apple-touch-icon.png">
<link rel="manifest" href="{BASE}manifest.webmanifest">
<meta name="theme-color" content="{THEME['clair']}" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="{THEME['sombre']}" media="(prefers-color-scheme: dark)">
<script src="{BASE}assets/hors-ligne.js" defer></script>
<script src="{BASE}assets/musique.js" defer></script>
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
.foot {{ margin-top: 12px; border-top: 1px solid var(--rule); padding-top: 14px; font-size: .84rem; color: var(--muted); }}
.atlas-credit {{ margin: 0; display: flex; flex-wrap: wrap; align-items: center; column-gap: .45em; }}
.atlas-credit a {{ display: inline-flex; align-items: center; min-height: 44px; }}
.atlas-credit .atlas-note {{ font-size: .92em; }}
.atlas-droits {{ margin: 0; }}
.atlas-droits a {{ padding-block: 12px; }}
</style>
</head>
<body>
<main>
<p>{NOM_SITE}</p>
<h1>Page introuvable</h1>
<p>Cette adresse ne correspond à aucune page de l’atlas. Elle a peut-être changé de nom.</p>
<p><a class="home" href="{BASE}">Revenir à l’accueil de l’atlas</a></p>
<ul>{liste}</ul>
<footer class="foot">{pied('404.html', 'Page introuvable', BASE + '#droits')}</footer>
</main>
</body>
</html>
'''
(OUT / '404.html').write_text(passe_typo(p404, js=False), encoding='utf-8')

assets = OUT / 'assets'
(assets / 'lib').mkdir(parents=True, exist_ok=True)
fonts = assets / 'fonts'
if fonts.exists() and fonts.resolve() != POLICES.resolve():
    shutil.rmtree(fonts)              # les anciens fichiers de polices ne doivent pas rester
fonts.mkdir(parents=True, exist_ok=True)
for f in ('three.min.js', 'OrbitControls.js', 'LICENSE-three.txt'):
    shutil.copy2(LIB / f, assets / 'lib' / f)
for f in POLICES.iterdir():
    shutil.copy2(f, fonts / f.name)
for f in ACTIFS:
    if (ACTIFS_DIR / f).exists():
        shutil.copy2(ACTIFS_DIR / f, assets / f)
    else:
        problems.append(f'fichier absent : {ACTIFS_DIR.name}/{f}')
for f in ('refs-urantia.js', 'hors-ligne.js', 'musique.js'):
    if (SRC / f).exists():
        shutil.copy2(SRC / f, assets / f)
    else:
        problems.append(f'source absente : {f}')
for f in RACINE + GITHUB:                        # le dossier .git du site n'est jamais touché
    if (ENTREES / f).exists():
        (OUT / f).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ENTREES / f, OUT / f)
    else:
        problems.append(f'fichier absent : {f}')
(OUT / '.nojekyll').write_text('', encoding='utf-8')
sources = OUT / 'sources'
sources.mkdir(exist_ok=True)
for f in SOURCES:
    if not (SRC / f).exists():
        problems.append(f'source absente : {f}')
        continue
    if f.endswith(('.html', '.py', '.js', '.md', '.txt')):
        texte = (SRC / f).read_text(encoding='utf-8')
        if f.endswith('.html'):      # pages publiées : sans adresse claude.ai, ni balise claude:, ni rangée propre aux artefacts
            texte = re.sub(r'<meta name="claude:[^"]*"[^>]*>\s*', '', adresses_locales(texte))
            texte = re.sub(r'\s*<(p|div|span|li)\b[^>]*\sdata-artefact\b[^>]*>.*?</\1>', '', texte, flags=re.S)
        (sources / f).write_text(texte, encoding='utf-8', newline='\n')
    else:
        shutil.copy2(SRC / f, sources / f)

# ── Application installable : manifeste, page hors ligne, service worker ─────────────────────────
manifeste = {
    'id': './', 'name': NOM_SITE, 'short_name': NOM_COURT,
    'description': typo('Atlas visuel du Livre d’Urantia : l’origine et l’organisation de l’univers en cartes, '
                        'en 3D et en schémas, avec les références du texte. Se lit aussi hors ligne.'),
    'lang': 'fr', 'dir': 'ltr', 'start_url': './', 'scope': './', 'display': 'standalone',
    'background_color': THEME['appli'], 'theme_color': THEME['appli'], 'categories': ['education', 'books'],
    'icons': [{'src': 'assets/' + f, 'sizes': s, 'type': 'image/png', 'purpose': p} for f, s, p in ICONES],
}
(OUT / 'manifest.webmanifest').write_text(json.dumps(manifeste, ensure_ascii=False, indent=1) + '\n', encoding='utf-8', newline='\n')

# Page servie par le service worker pour une adresse non enregistrée, à n'importe quelle profondeur : le service worker
# y ajoute <base href> (portée du site), d'où des liens relatifs.
lignes = ''.join(f'<li data-page><a href="{"./" if n == "index.html" else n}">{nom}</a> <span class="etat"></span></li>'
                 for _, n, nom, _, _ in present)
phl = f'''<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="robots" content="noindex">
<meta name="author" content="{AUTEUR}">
<meta name="theme-color" content="{THEME['clair']}" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="{THEME['sombre']}" media="(prefers-color-scheme: dark)">
<title>Hors ligne — {NOM_SITE}</title>
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="assets/fonts/fonts.css">
<script src="assets/musique.js" defer></script>
<style>
:root {{ --paper: #EEF1F6; --sheet: #FFFFFF; --ink: #18213B; --muted: #56607D; --rule: #CBD2E0; --gold-ink: #8A5A00; color-scheme: light;
  --font-display: "Cormorant Garamond", Georgia, serif; --font-body: "Alegreya Sans", "Segoe UI", Arial, sans-serif; }}
@media (prefers-color-scheme: dark) {{ :root {{ --paper: #0C1120; --sheet: #131A2E; --ink: #E6E9F2; --muted: #9AA4C0; --rule: #28314B; --gold-ink: #F4C664; color-scheme: dark; }} }}
body {{ margin: 0; background: var(--paper); color: var(--ink); font: 17px/1.6 var(--font-body); }}
main {{ max-width: 640px; margin: 0 auto; padding: 56px 16px; display: grid; gap: 16px; }}
h1 {{ margin: 0; font: 600 2.4rem/1.1 var(--font-display); }}
h2 {{ margin: 12px 0 0; font: 600 1.4rem/1.2 var(--font-display); }}
p {{ margin: 0; }}
a {{ color: var(--gold-ink); text-underline-offset: 3px; }}
.home {{ display: inline-flex; align-items: center; min-height: 44px; padding: 0 20px; border-radius: 999px; background: var(--ink); color: var(--paper); text-decoration: none; font-weight: 600; }}
.pages {{ margin: 0; padding: 0; list-style: none; display: grid; }}
.pages a {{ display: inline-flex; align-items: center; min-height: 44px; }}
.pages .etat {{ color: var(--muted); font-size: .9rem; }}
.foot {{ margin-top: 8px; border-top: 1px solid var(--rule); padding-top: 14px; font-size: .84rem; color: var(--muted); }}
.atlas-credit {{ margin: 0; display: flex; flex-wrap: wrap; align-items: center; column-gap: .45em; }}
.atlas-credit a {{ display: inline-flex; align-items: center; min-height: 44px; }}
.atlas-credit .atlas-note {{ font-size: .92em; }}
.atlas-droits {{ margin: 0; }}
.atlas-droits a {{ padding-block: 12px; }}
</style>
</head>
<body>
<main>
<p>{NOM_SITE}</p>
<h1>Hors ligne</h1>
<p>Cette page n’est pas encore enregistrée pour la lecture hors ligne.</p>
<p>Reconnecte-toi pour l’afficher. Pour tout lire sans réseau, ouvre l’accueil avec une connexion et touche « Télécharger pour lire hors ligne ».</p>
<p><a class="home" href="./">Revenir à l’accueil de l’atlas</a></p>
<h2>Pages enregistrées sur cet appareil</h2>
<ul class="pages">{lignes}</ul>
<footer class="foot">{pied('hors-ligne.html', 'Hors ligne')}</footer>
</main>
<script>
(function () {{
  try {{
    if (!window.caches) return;
    Array.prototype.forEach.call(document.querySelectorAll('[data-page]'), function (li) {{
      var u = new URL(li.querySelector('a').href);
      if (u.pathname.slice(-1) === '/') u.pathname += 'index.html';
      caches.match(u.href).then(function (r) {{
        li.className = r ? 'ok' : 'non';
        li.querySelector('.etat').textContent = r ? '· enregistrée' : '· pas encore enregistrée';
      }});
    }});
  }} catch (e) {{ /* liste sans état */ }}
}})();
</script>
</body>
</html>
'''
(OUT / 'hors-ligne.html').write_text(passe_typo(phl, js=False), encoding='utf-8')

# Service worker : liste des fichiers de l'atlas (ni sources/, ni README, ni licences, ni .git, ni 404, ni aperçu de partage)
polices_web = ['assets/fonts/' + f.name for f in sorted(POLICES.iterdir()) if f.suffix in ('.woff2', '.css')]
icones = ['assets/' + i[0] for i in ICONES]
NOYAU_HL = (['index.html', 'hors-ligne.html', 'manifest.webmanifest', 'assets/refs-urantia.js', 'assets/hors-ligne.js',
             'assets/musique.js', 'assets/favicon.svg', 'assets/apple-touch-icon.png'] + icones + polices_web)
LISTE_HL = list(dict.fromkeys([n for _, n, _, _, _ in present] + NOYAU_HL + ['assets/lib/three.min.js', 'assets/lib/OrbitControls.js']))
absents = [p for p in LISTE_HL if not (OUT / p).exists()]
if absents:
    problems.append('hors ligne : fichiers absents ' + ', '.join(absents))
    LISTE_HL = [p for p in LISTE_HL if p not in absents]
TEXTE = ('.html', '.js', '.css', '.svg', '.webmanifest', '.json')


def contenu(p):
    d = (OUT / p).read_bytes()
    return d.replace(b'\r\n', b'\n') if p.endswith(TEXTE) else d      # tel que publié (fins de ligne LF dans le dépôt)


taille = f'{sum(len(contenu(p)) for p in LISTE_HL) / 1e6:.1f}'.replace('.', ',')
idx = OUT / 'index.html'
if idx.exists() and '__TAILLE_HORS_LIGNE__' in idx.read_text(encoding='utf-8'):
    idx.write_text(idx.read_text(encoding='utf-8').replace('__TAILLE_HORS_LIGNE__', taille), encoding='utf-8')
fichiers, empreinte = {}, hashlib.sha256()
for p in LISTE_HL:
    d = contenu(p)
    fichiers[p] = (len(d), hashlib.sha256(d).hexdigest()[:16])
    empreinte.update(p.encode('utf-8') + b'\0' + d + b'\0')
version = empreinte.hexdigest()[:12]
sw = (SW_GABARIT.replace('__VERSION__', version)
      .replace('__FICHIERS__', '{\n' + ',\n'.join(f'  {json.dumps(p)}: [{o}, "{h}"]' for p, (o, h) in fichiers.items()) + '\n}')
      .replace('__NOYAU__', json.dumps([p for p in NOYAU_HL if p in fichiers])))
(OUT / 'sw.js').write_text(sw, encoding='utf-8', newline='\n')
print(f'hors ligne : {len(fichiers)} fichiers, {taille} Mo, version {version}')

for p in OUT.rglob('*'):
    if p.is_file() and p.suffix in ('.html', '.js', '.py', '.md', '.txt', '.css', '.yml', '.webmanifest') and '.git' not in p.parts:
        if 'claude.ai/' + 'artifact' in p.read_text(encoding='utf-8', errors='ignore'):   # écrit en deux morceaux pour ne pas se signaler lui-même
            problems.append(f'{p.relative_to(OUT)} : contient encore une adresse d’artefact claude.ai')
print('\n'.join(problems) if problems else 'vérification : aucune adresse externe à remplacer, aucun lien interne cassé')
