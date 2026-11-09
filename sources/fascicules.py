"""Page « Le livre fascicule par fascicule » (fascicules.html) et rapport de couverture (../couverture-du-livre.md).

Pour le lecteur : chacun des 197 fascicules, avec son auteur déclaré, sa durée de lecture, le lien vers son texte sur
urantia.org et les pages de l'atlas qui en parlent ; une mosaïque montre ce que l'atlas couvre du livre.
Pour nous : le rapport dit quels fascicules l'atlas traite peu ou pas, et propose des pages pour combler les manques.

À relancer à chaque construction, car de nouvelles pages arrivent ; depuis le dossier qui contient erudit/ :
    python -I erudit/visuels/source/fascicules.py
puis construire le site (construire_site.py). Option : --essai DOSSIER écrit la page et le rapport dans DOSSIER.

Données lues :
  - erudit/carte-du-livre.md : numéro, titre, auteur déclaré, nombre de mots de chaque fascicule ;
  - refs-urantia.js : la page de chaque fascicule sur urantia.org ;
  - construire_site.py : la liste PAGES (fichier source, nom dans le site, nom canonique…), lue sans être exécutée ;
  - les pages sources de l'atlas listées dans PAGES et présentes (la vue 3D : son gabarit urantia-paradis-3d.src.html),
    sauf le glossaire et « Les auteurs déclarés et le livre en chiffres », qui parcourent tout le livre, et cette page ;
  - le texte du livre (UF-FRE-001-1960-3.5.md), s'il est là : seulement ses ancres, pour vérifier que chaque référence
    existe ; rien n'en est recopié.
Comptage : une référence est un passage « fascicule:section.paragraphe » (ou fascicule:section, ou une plage) cité dans
la page : dans un élément .ref, dans le texte, ou dans une chaîne d'un script (données de la vue 3D, des frises…). Une
forme courte (« 30:2 ») n'est gardée que dans un .ref, entre parenthèses ou dans une liste de références ; un verset
biblique (« Jean 14:2 ») est écarté. Chaque référence distincte compte une fois par page. Le lien vers une page vise
la section (enfant de <main>, ou bloc de la vue 3D) qui réunit au moins la moitié des références du fascicule.
Paliers de couverture : bien couvert 12 et plus, moyen 4 à 11, peu 1 à 3, aucune référence.
La page est un fragment, comme les autres pages sources (fins de ligne CRLF, script des références injecté à la fin) ;
elle n'est réécrite que si son contenu change (la date du relevé reste alors la même)."""
import ast
import datetime
import hashlib
import html as html_lib
import json
import os
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from html.parser import HTMLParser
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

SRC = Path(__file__).resolve().parent                  # visuels/source
ERUDIT = SRC.parent.parent
RACINE = ERUDIT.parent
CARTE = ERUDIT / 'carte-du-livre.md'
TEXTE = Path(os.environ.get('UB_SOURCE') or RACINE / 'UF-FRE-001-1960-3.5.md')
REFS_JS = SRC / 'refs-urantia.js'
CONSTRUIRE = SRC / 'construire_site.py'
PAGE = 'fascicules.html'
RAPPORT = 'couverture-du-livre.md'
URANTIA = 'https://www.urantia.org/fr/le-livre-d-urantia/'

EXCLUES = {'glossaire.html', 'index-des-noms.html', 'auteurs-et-chiffres.html', PAGE}   # parcourent tout le livre (et cette page elle-même)
GABARIT_3D = ('urantia-paradis-3d.html', 'urantia-paradis-3d.src.html')
SEUILS = (1, 4, 12)                                    # peu : 1 à 3 ; moyen : 4 à 11 ; bien couvert : 12 et plus
MOTS_MINUTE = 200
PARTIES = [(0, 'Introduction', 'Introduction', [0]),
           (1, 'Partie I', 'L’univers central et les superunivers', range(1, 32)),
           (2, 'Partie II', 'L’univers local', range(32, 57)),
           (3, 'Partie III', 'L’histoire d’Urantia', range(57, 120)),
           (4, 'Partie IV', 'La vie et les enseignements de Jésus', range(120, 197))]
CHIFFRES_ROMAINS = {0: '', 1: 'I', 2: 'II', 3: 'III', 4: 'IV'}
NIVEAUX = [('Aucune page', 'Pas encore dans l’atlas', 'aucune référence'),
           ('Peu', 'Peu couvert', '1 à 3 références'),
           ('Moyen', 'Moyennement couvert', '4 à 11 références'),
           ('Bien couvert', 'Bien couvert', '12 références et plus')]

# Pages annoncées dont la source n'est pas encore là : leurs fascicules sont « en cours » dans le rapport (ils ne sont pas
# comptés, faute de page). Une fois la source présente, la page est relevée comme les autres.
EN_COURS = [
    ('jerusem-et-edentia.html', 'Jérusem, Édentia et les mondes des maisons', [43, 44, 45, 46, 47, 48]),
    ('avenir-d-une-planete.html', 'L’avenir d’une planète', [49, 50, 51, 52, 55]),
    ('institutions-humaines.html', 'L’évolution des institutions humaines', [68, 69, 70, 71, 72, 81, 82, 83, 84]),
    ('melchizedek-et-religions.html', 'Melchizédek et les religions du monde', [93, 94, 95, 96, 97, 98]),
]

# Propositions pour combler les manques (rapport) : une page ou une section, ses fascicules faibles, ses voisins, et ce
# qu'elle montrerait (intitulés des sections du texte vérifiés avec outils/ub.py le 2026-11-08). L'état de chacune est
# recalculé à chaque relevé ; une proposition dont tous les fascicules ont au moins 4 références est « comblée ».
PROPOSITIONS = [
    ('Le Père, le Fils et l’Esprit', 'nouvelle page (Thèmes), à côté de « Dieu et la Déité »',
     [1, 4, 5, 6, 8, 104], [3, 7, 9],
     'Les trois personnes du Paradis une à une : le nom, la réalité et la personnalité du Père, le Fils et son ministère '
     'de l’amour du Père, l’Esprit « Dieu d’action », leurs relations avec l’univers et avec chaque personne '
     '(le chemin vers Dieu, la vraie adoration), puis la croissance du concept de Trinité (trinités, triunités, '
     'triodités) ; « Dieu et la Déité » part des Absolus et de la Trinité, cette page partirait des personnes.'),
    ('Le supercontrôle de l’évolution', 'section de « L’histoire d’Urantia »',
     [65], [58, 62, 63],
     'Comment, selon le livre, les Porteurs de Vie conduisent la vie d’un monde : leurs fonctions, « l’aventure '
     'd’Urantia », les vicissitudes et les techniques de l’évolution de la vie, et les niveaux évolutionnaires du mental, '
     'en tête de la frise des ères de la vie.'),
    ('La religion vécue', 'nouvelle page (Thèmes), suite de « L’évolution de la religion »',
     [99, 100, 102], [101, 103],
     'La religion personnelle selon le livre : la croissance religieuse et spirituelle, les signes d’une vie religieuse, '
     'les assurances et la certitude de la foi, la réalité de l’expérience religieuse, et la religion face à la '
     'reconstruction sociale et aux institutions.'),
    ('Les années cachées de Jésus', 'nouvelle page (Thèmes), entre « La vie de Jésus » et ses cartes',
     [127, 128, 129, 133], [124, 126, 130, 132],
     'De l’adolescence à trente ans : Jésus chef de famille après la mort de Joseph, Rébecca, l’épisode de Damas, puis le '
     'voyage avec Gonod et son fils Ganid, de Joppé à Rome par Alexandrie et Carthage, et le retour par Corinthe, Athènes, '
     'Éphèse, Chypre et Antioche, sur une frise et une carte, avec les discours de chaque étape.'),
    ('Les grands discours de Jésus', 'section de « Les enseignements de Jésus »',
     [153, 156, 160, 161, 175, 178], [180, 181],
     'Le sermon historique de Capharnaüm, l’enseignement à Sidon et à Tyr, la philosophie grecque de Rodan et ses '
     'entretiens sur la personnalité de Dieu et la nature divine de Jésus, le dernier discours au temple et le discours '
     'sur la filiation et la citoyenneté : chacun résumé, avec son lieu, son auditoire et ses références.'),
    ('Après la Pentecôte', 'nouvelle page (Thèmes) ou dernière section de « Les enseignements de Jésus »',
     [195], [194, 196],
     'Ce que le livre dit de la suite : l’influence grecque et romaine sur le christianisme naissant, les âges de '
     'ténèbres, puis le problème moderne, le matérialisme, le totalitarisme laïque, le problème du christianisme et '
     'l’avenir, avec ce qu’en dit l’histoire.'),
]
# Fascicules faibles hors propositions et hors pages en cours : où les rattacher.
RATTACHEMENTS = {
    27: 'une section de « Le Paradis et Havona » (les sept ordres de supernaphins primaires : instigateurs de repos, '
        'interprètes d’éthique, conducteurs d’adoration…)',
    109: 'une section de « La destinée humaine » (Ajusteurs autonomes, Ajusteurs et types de mortels, destinée des '
         'Ajusteurs Personnalisés)',
}

RX_REF = re.compile(r'(?<![\w:.])(\d{1,3}):(\d{1,2})(?:\.(\d{1,3}))?(?:\s*[–‑-]\s*(\d{1,3})(?:[.:](\d{1,3}))?)?(?![\d:])')
BIBLE = set('''genese gn exode ex levitique lv nombres nb deuteronome dt josue jos juges jg ruth rt samuel sam rois
chroniques ch esdras esd nehemie ne tobie tb judith jdt esther est maccabees mac job jb psaume psaumes ps proverbes pr
ecclesiaste qo cantique ct sagesse sg siracide si ecclesiastique isaie is jeremie jr lamentations lm baruch ba ezechiel ez
daniel dn osee os joel jl amos am abdias ab jonas jon michee mi nahum na habacuc ha sophonie so aggee ag zacharie za
malachie ml matthieu mt marc mc luc lc jean jn actes ac romains rm corinthiens co galates ga ephesiens ep philippiens ph
colossiens col thessaloniciens th timothee tm tite tt philemon phm hebreux he jacques jc pierre jude apocalypse ap'''.split())
VIDES = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}
FERMENT_P = {'address', 'article', 'aside', 'blockquote', 'details', 'div', 'dl', 'fieldset', 'figcaption', 'figure', 'footer',
             'form', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'header', 'hr', 'main', 'menu', 'nav', 'ol', 'p', 'pre', 'section',
             'table', 'ul'}
ANCRABLES = {'section', 'article', 'aside'}
NB = '&nbsp;'


# ── Données ─────────────────────────────────────────────────────────────────────────────────────
def plier(s):
    s = unicodedata.normalize('NFD', s)
    return ''.join(c for c in s if unicodedata.category(c) != 'Mn').lower().replace('’', "'")


def lire_carte():
    """{n: (titre, auteur, mots)} d'après la table « Les 197 fascicules » de la carte du livre."""
    if not CARTE.exists():
        sys.exit(f'Carte du livre introuvable : {CARTE} (la régénérer : python outils/ub.py plan --md)')
    f = {}
    for l in CARTE.read_text(encoding='utf-8').splitlines():
        m = re.match(r'\|\s*(\d{1,3})\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*[\d–-]+\s*\|\s*\d+\s*\|\s*\d+\s*\|\s*(\d+)\s*\|\s*$', l)
        if m:
            f[int(m.group(1))] = (m.group(2).strip(), m.group(3).strip(), int(m.group(4)))
    manque = [n for n in range(197) if n not in f]
    if manque:
        sys.exit(f'Carte du livre incomplète, fascicules absents : {manque}')
    return f


def lire_adresses():
    """Page de chaque fascicule sur urantia.org (table de refs-urantia.js)."""
    m = re.search(r'var S = (\[.*?\]);', REFS_JS.read_text(encoding='utf-8'), re.S)
    s = json.loads(m.group(1)) if m else []
    if len(s) != 197:
        sys.exit(f'Table des fascicules introuvable ou incomplète dans {REFS_JS.name}')
    return s


def lire_pages():
    """PAGES de construire_site.py, lu sans l'exécuter : [(source, nom dans le site, nom canonique, nom court, desc)]."""
    arbre = ast.parse(CONSTRUIRE.read_text(encoding='utf-8'))
    for n in arbre.body:
        if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'PAGES' for t in n.targets):
            return [tuple(p) for p in ast.literal_eval(n.value)]
    sys.exit('Liste PAGES introuvable dans construire_site.py')


def lire_structure():
    """{(fascicule, section): {paragraphes}} d'après les ancres du texte (U57_6_5), ou None s'il n'est pas là."""
    if not TEXTE.exists():
        return None
    st = defaultdict(set)
    for f, s, p in re.findall(r'<a name="U(\d+)_(\d+)_(\d+)"></a>', TEXTE.read_text(encoding='utf-8')):
        st[(int(f), int(s))].add(int(p))
    return st


def source_de(src):
    """Fichier à relever pour une page de PAGES (la vue 3D : son gabarit, plus léger, qui porte les mêmes textes)."""
    if src == GABARIT_3D[0] and (SRC / GABARIT_3D[1]).exists():
        return GABARIT_3D[1]
    return src


# ── Relevé des références d'une page ─────────────────────────────────────────────────────────────
def chaines_js(code, base):
    """Chaînes littérales d'un script ('…', "…", `…`) avec leur position ; commentaires et expressions régulières sautés."""
    out, i, n, prev = [], 0, len(code), ''
    while i < n:
        c = code[i]
        if c in '"\'`':
            j = i + 1
            while j < n and code[j] != c and (c == '`' or code[j] != '\n'):
                j += 2 if code[j] == '\\' else 1
            out.append((code[i + 1:j], base + i + 1))
            i, prev = j + 1, c
            continue
        if c == '/' and code[i + 1:i + 2] == '/':
            j = code.find('\n', i)
            i = n if j < 0 else j
            continue
        if c == '/' and code[i + 1:i + 2] == '*':
            j = code.find('*/', i + 2)
            i = n if j < 0 else j + 2
            continue
        if c == '/' and (prev == '' or prev in '(,=:[!&|?{};+-*%<>~^' or
                         re.search(r'(?:^|[^\w$])(?:return|typeof|case|do|else|in|of|new|delete|void|throw)\s*$',
                                   code[max(0, i - 12):i])):
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
            i, prev = j, '/'
            continue
        if not c.isspace():
            prev = c
        i += 1
    return out


class Releve:
    """Références d'une page : {fascicule: {référence: chaîne d'ancres}}, intitulés des ancres, et références écartées."""
    def __init__(self, structure):
        self.st = structure
        self.refs = defaultdict(dict)
        self.etiquettes = {}
        self.ecartees = Counter()

    def existe(self, f, s, p):
        if f > 196:
            return False
        if self.st is None:
            return True
        return (f, s) in self.st and (p is None or p in self.st[(f, s)])

    def lire(self, texte, chaine=(), dans_ref=False, js=False):
        for m in RX_REF.finditer(texte):
            f, s, p = m.group(1), m.group(2), m.group(3)
            if any(len(x) > 1 and x[0] == '0' for x in (f, s, p) if x):
                self.ecartees[('zéro initial (heure, code)', m.group(0))] += 1
                continue
            if p is None:                                  # forme courte (fascicule:section) : prudence
                avant = texte[max(0, m.start() - 40):m.start()]
                mot = re.search(r'([^\W\d_]+)\.?\s*$', avant)
                if mot and plier(mot.group(1)) in BIBLE:
                    self.ecartees[('verset biblique', f'{mot.group(1)} {m.group(0)}')] += 1
                    continue
                if not dans_ref:
                    av = avant.rstrip('  \t\r\n')
                    ap = texte[m.end():m.end() + 3].lstrip('  \t\r\n')
                    liste = js and not re.sub(r'[\s ;·,–‑-]+', '', RX_REF.sub('', re.sub(r'<[^>]*>', '', texte)))
                    if not (liste or av[-1:] in '([{;·,' or ap[:1] in ')]};·,'):
                        self.ecartees[('forme courte hors d’une liste de références', m.group(0))] += 1
                        continue
            if not self.existe(int(f), int(s), int(p) if p else None):
                self.ecartees[('passage absent du livre', m.group(0))] += 1
                continue
            cle = re.sub(r'\s+', '', m.group(0)).replace('‑', '-').replace('–', '-')
            d = self.refs[int(f)]
            if cle not in d or (chaine and not d[cle]):
                d[cle] = tuple(chaine)


class LecteurHTML(HTMLParser):
    """Texte d'une page dont scripts, styles et commentaires sont retirés : références (.ref, texte) avec la chaîne des
    blocs à identifiant (section, article, aside, non cachés, hors d'un details fermé) qui les contiennent, et le premier
    titre de chacun de ces blocs."""
    def __init__(self, releve):
        super().__init__(convert_charrefs=True)
        self.r, self.pile, self.titre = releve, [], None

    def handle_starttag(self, tag, attrs):
        a = {k: (v or '') for k, v in attrs}
        if self.pile and self.pile[-1]['tag'] == 'p' and tag in FERMENT_P:
            self.pile.pop()
        if tag == 'li' and self.pile and self.pile[-1]['tag'] == 'li':
            self.pile.pop()
        parent = self.pile[-1] if self.pile else {'dedans': False, 'bloque': False}
        cls = a.get('class', '').split()
        e = {'tag': tag, 'ref': 'ref' in cls, 'ancre': '',
             'dedans': parent['dedans'] or tag == 'main' or (tag == 'div' and 'wrap' in cls),
             'bloque': parent['bloque'] or 'hidden' in a or a.get('aria-hidden') == 'true'
                       or (parent.get('tag') == 'details' and parent.get('ferme', False))}
        if tag == 'details':
            e['ferme'] = 'open' not in a
        if tag in ANCRABLES and a.get('id') and parent['dedans'] and not e['bloque']:
            e['ancre'] = a['id']
        if tag in ('h1', 'h2', 'h3', 'h4') and self.titre is None:
            anc = self.chaine()
            if anc and anc[-1] not in self.r.etiquettes:
                self.titre = [anc[-1], tag, []]
        if tag not in VIDES:
            self.pile.append(e)

    def handle_endtag(self, tag):
        if self.titre and tag == self.titre[1]:
            t = re.sub(r'\s+', ' ', ''.join(self.titre[2])).strip()
            t = re.sub(r'^[^\w«(]+', '', t)
            if t:
                self.r.etiquettes[self.titre[0]] = t
            self.titre = None
        for i in range(len(self.pile) - 1, -1, -1):
            if self.pile[i]['tag'] == tag:
                del self.pile[i:]
                return

    def chaine(self):
        return tuple(e['ancre'] for e in self.pile if e['ancre'])

    def handle_data(self, d):
        if self.titre:
            self.titre[2].append(d)
        self.r.lire(d, self.chaine(), dans_ref=any(e['ref'] for e in self.pile))


def ancres_3d(h):
    """Vue 3D : plages de son script → ancre de la vue (#nebadon, #frise, #jupiter…) et intitulé, comme l'index de la
    recherche du site : niveaux du zoom (INFO et HASH_LV), vue en coupe, panneaux (gouvernement, frise, carrière), fiches
    des astres. Ces ancres sont celles que la vue 3D sait ouvrir (applyHash)."""
    plages = []
    hl = re.search(r"const HASH_LV = \[([^\]]*)\]", h)
    niveaux = re.findall(r"'([a-z-]+)'", hl.group(1)) if hl else []
    info = re.search(r'const INFO = \[(.*?)\n  \];', h, re.S)
    if info and niveaux:
        debuts = list(re.finditer(r"\n\s*\{ h: '((?:[^'\\]|\\.)*)'", info.group(0)))
        for k, m in enumerate(debuts[:len(niveaux)]):
            fin = debuts[k + 1].start() if k + 1 < len(debuts) else len(info.group(0))
            plages.append((info.start() + m.start(), info.start() + fin, niveaux[k], html_lib.unescape(m.group(1))))
    boutons = {}
    for b, ancre in (('t-gov', 'gouvernement'), ('t-time', 'frise'), ('t-asc', 'carriere'), ('t-coupe', 'coupe')):
        m = re.search(r'id="' + b + r'"[^>]*>([^<]*)<', h)
        if m:
            boutons[ancre] = html_lib.unescape(m.group(1)).strip()
    for nom, ancre in (('COUPE', 'coupe'), ('GOV', 'gouvernement'), ('EV', 'frise'), ('ERAS', 'frise'), ('ASC', 'carriere')):
        m = re.search(r'\n  const ' + nom + r' = ', h)
        if m:
            fin = h.find('\n  const ', m.end())
            plages.append((m.start(), fin if fin > 0 else len(h), ancre, boutons.get(ancre, '')))
    corps = list(re.finditer(r"\n    (\w+): \{ n: '((?:[^'\\]|\\.)*)', k: '", h))
    for k, m in enumerate(corps):
        fin = corps[k + 1].start() if k + 1 < len(corps) else min(len(h), m.end() + 6000)
        plages.append((m.start(), fin, m.group(1), html_lib.unescape(m.group(2))))
    return plages


def releve_page(fichier, structure):
    h = (SRC / fichier).read_text(encoding='utf-8')
    r = Releve(structure)
    plages = ancres_3d(h) if fichier in GABARIT_3D else []
    for _, _, anc, lab in plages:
        if lab:
            r.etiquettes.setdefault(anc, lab)
    for m in re.finditer(r'<script\b([^>]*)>(.*?)</script>', h, re.S):
        if 'refs-urantia' in m.group(1) or re.search(r'\bsrc=', m.group(1)):
            continue
        for s, pos in chaines_js(m.group(2), m.start(2)):
            s = s.replace('\\"', '"').replace("\\'", "'")
            anc = next((p[2] for p in plages if p[0] <= pos < p[1]), '')
            r.lire(html_lib.unescape(s), (anc,) if anc else (),
                   dans_ref=bool(re.search(r'class="[^"]*\bref\b', s)), js=True)
    lh = LecteurHTML(r)
    lh.feed(re.sub(r'<script\b.*?</script>|<style\b.*?</style>|<!--.*?-->', ' ', h, flags=re.S))
    lh.close()
    return r


def meilleure_ancre(chaines):
    """Ancre la plus précise qui réunit au moins la moitié des références d'un fascicule dans la page ('' : haut de page)."""
    total, choix, niveau = len(chaines), (), 0
    while True:
        c = Counter(ch[niveau] for ch in chaines if len(ch) > niveau and ch[:niveau] == choix)
        if not c:
            return choix[-1] if choix else ''
        anc, n = c.most_common(1)[0]
        if n * 2 < total:
            return choix[-1] if choix else ''
        choix, niveau = choix + (anc,), niveau + 1


# ── Mise en forme ───────────────────────────────────────────────────────────────────────────────
def e(s):
    return html_lib.escape(str(s), quote=True)


def nombre(n, sep=' '):
    return f'{n:,}'.replace(',', sep)


def duree(minutes, sep=NB):
    if minutes < 60:
        return f'{minutes}{sep}min'
    h, m = divmod(int(round(minutes / 5.0) * 5), 60)
    return f'{h}{sep}h' + (f'{sep}{m:02d}' if m else '')


def niveau(n):
    return 0 if n < SEUILS[0] else 1 if n < SEUILS[1] else 2 if n < SEUILS[2] else 3


def pluriel(n, s, p=None):
    return s if n < 2 else (p or s + 's')


def date_fr(iso):
    mois = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'aout', 'septembre', 'octobre', 'novembre',
            'décembre']
    a, m, j = (int(x) for x in iso.split('-'))
    return f'{"1er" if j == 1 else j} {mois[m - 1]} {a}'


def plage_texte(ns):
    """[43, 44, 45, 47] → « 43–45, 47 »."""
    ns, out, i = sorted(ns), [], 0
    while i < len(ns):
        j = i
        while j + 1 < len(ns) and ns[j + 1] == ns[j] + 1:
            j += 1
        out.append(str(ns[i]) if i == j else f'{ns[i]}–{ns[j]}')
        i = j + 1
    return ', '.join(out)


# ── Feuille de style et script de la page ───────────────────────────────────────────────────────
POLICES = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
           '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
           '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Alegreya+Sans:ital,wght@0,400;0,500;0,700;1,400'
           '&family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,500;1,600&family=IBM+Plex+Mono:wght@400;500&display=swap">')

CSS = r'''/* Page écrite par fascicules.py : ne pas la modifier à la main, relancer le script.
   Mise en page : le livre fascicule par fascicule. En tête, le propos et quelques chiffres ; puis la vue d’ensemble
   (mosaïque des 197 fascicules : chaque case se remplit selon ce que l’atlas en dit) ; puis la liste, par parties
   repliables, avec recherche et filtres. Largeur utile : 1100 px.
   Couverture : une seule teinte (bleu) en trois paliers de clarté, validés pour une échelle ordinale (validateur dataviz
   --ordinal : clarté monotone, écarts ≥ 0,06, premier palier ≥ 2:1 sur la surface, en clair et en sombre). La hauteur
   du remplissage redit le palier et le texte le nomme : la couleur n’est jamais seule. L’or reste l’accent des liens
   et du focus. */
:root {
  --paper: #EEF1F6;    /* fond : papier bleuté */
  --sheet: #FFFFFF;    /* surfaces */
  --tint: #E4E9F2;     /* survol, panneaux */
  --ink: #18213B;      /* encre bleu nuit */
  --muted: #56607D;    /* texte secondaire */
  --rule: #CBD2E0;     /* filets */
  --rule-ctl: #7D88A3; /* bordure des commandes, cases vides */
  --gold: #C98A12;     /* accent */
  --gold-ink: #8A5A00; /* or, en texte */
  --gold-soft: #FBF4E4;
  /* Couverture par l’atlas : peu, moyen, bien (une teinte, du clair au foncé ; s’inverse en sombre) */
  --n1: #86B6EF; --n2: #2A78D6; --n3: #104281; --on-n3: #FFFFFF;
  --n1-bord: #3987E5;  /* contour des cases « peu » : un cran plus foncé que leur remplissage, 3,6:1 sur la surface */
  --shadow: 0 10px 28px rgba(12, 17, 32, .18);
  --font-display: "Cormorant Garamond", "Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif;
  --font-body: "Alegreya Sans", "Segoe UI", "Helvetica Neue", Arial, sans-serif;
  --font-mono: "IBM Plex Mono", ui-monospace, "Cascadia Mono", Consolas, monospace;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --paper: #0C1120; --sheet: #131A2E; --tint: #1A2239; --ink: #E6E9F2; --muted: #9AA4C0;
    --rule: #28314B; --rule-ctl: #6A769C; --gold: #EDB03A; --gold-ink: #F4C664; --gold-soft: #221F17;
    --n1: #256ABF; --n2: #5598E7; --n3: #B7D3F6; --on-n3: #0C1120; --n1-bord: #256ABF;
    --shadow: 0 10px 28px rgba(0, 0, 0, .5);
    color-scheme: dark;
  }
}
:root[data-theme="dark"] {
  --paper: #0C1120; --sheet: #131A2E; --tint: #1A2239; --ink: #E6E9F2; --muted: #9AA4C0;
  --rule: #28314B; --rule-ctl: #6A769C; --gold: #EDB03A; --gold-ink: #F4C664; --gold-soft: #221F17;
  --n1: #256ABF; --n2: #5598E7; --n3: #B7D3F6; --on-n3: #0C1120; --n1-bord: #256ABF;
  --shadow: 0 10px 28px rgba(0, 0, 0, .5);
  color-scheme: dark;
}

*, *::before, *::after { box-sizing: border-box; }
[hidden] { display: none !important; }
html { scroll-padding-top: 16px; }
body { margin: 0; background: var(--paper); color: var(--ink); font-family: var(--font-body); font-size: 17px; line-height: 1.6; }
.wrap {
  max-width: 1100px; margin: 0 auto;
  padding-left: max(16px, env(safe-area-inset-left, 0px));
  padding-right: max(16px, env(safe-area-inset-right, 0px));
  padding-block: 44px 56px;
  display: grid; gap: 64px;
}
.wrap > * { min-width: 0; }
h1, h2, h3 { margin: 0; font-family: var(--font-display); font-weight: 600; line-height: 1.08; text-wrap: balance; }
h1 { font-size: clamp(2.4rem, 5.6vw, 4rem); letter-spacing: -0.005em; }
h2 { font-size: clamp(1.8rem, 3.6vw, 2.6rem); }
p { margin: 0; }
.eyebrow, .label { font: 500 .76rem/1.3 var(--font-mono); letter-spacing: .12em; text-transform: uppercase; color: var(--muted); }
:focus-visible { outline: 2px solid var(--gold-ink); outline-offset: 3px; border-radius: 4px; }
a { color: var(--gold-ink); text-underline-offset: 3px; }
.sr-only { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0, 0, 0, 0); white-space: nowrap; border: 0; }
.chev { width: 10px; height: 10px; border-right: 2px solid var(--muted); border-bottom: 2px solid var(--muted); transform: rotate(45deg); transition: transform .15s ease; flex: none; margin: 0 8px 4px 2px; }
details[open] > summary .chev { transform: rotate(-135deg); margin-bottom: 0; margin-top: 4px; }

/* En-tête */
.hero { display: grid; grid-template-columns: minmax(0, 1.45fr) minmax(0, 1fr); gap: 44px; align-items: end; }
.hero-text { display: grid; gap: 22px; min-width: 0; }
.lede { font-size: 1.22rem; line-height: 1.5; max-width: 56ch; }
.actions { display: flex; flex-wrap: wrap; gap: 10px 14px; align-items: center; }
.cta { display: inline-flex; align-items: center; gap: 10px; min-height: 44px; max-width: 100%; padding: 10px 18px; border-radius: 999px; border: 1px solid var(--ink); background: var(--ink); color: var(--paper); font: 500 1.02rem/1.25 var(--font-body); text-decoration: none; }
.cta:hover { background: var(--gold-ink); border-color: var(--gold-ink); color: var(--sheet); }
.cta.second { background: transparent; color: var(--ink); border-color: var(--rule-ctl); }
.cta.second:hover { background: var(--sheet); border-color: var(--ink); color: var(--ink); }
.cta .ar { font-family: var(--font-mono); }
.kpi { background: var(--sheet); border: 1px solid var(--rule); border-radius: 12px; padding: 18px 20px; display: grid; gap: 14px; min-width: 0; }
.kpi dl { margin: 0; display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px 18px; }
.kpi dl > div { display: flex; flex-direction: column; gap: 2px; border-top: 1px solid var(--rule); padding-top: 10px; min-width: 0; }
.kpi dt { order: 2; font: 500 .72rem/1.3 var(--font-mono); letter-spacing: .1em; text-transform: uppercase; color: var(--muted); }
.kpi dd { order: 1; margin: 0; font: 700 clamp(1.7rem, 3.2vw, 2.15rem)/1.05 var(--font-body); white-space: nowrap; font-variant-numeric: lining-nums; }
.kpi .note { font-size: .84rem; color: var(--muted); line-height: 1.45; }

/* Sections */
section { scroll-margin-top: 12px; }
.sec-head { display: grid; gap: 12px; max-width: 74ch; }
.hint { color: var(--muted); font-size: .98rem; }

/* Vue d’ensemble : la mosaïque */
.feature { background: var(--sheet); border: 1px solid var(--rule); border-top: 4px solid var(--n2); border-radius: 14px; padding: 28px 28px 30px; display: grid; gap: 22px; }
.feature > * { min-width: 0; }
.leg { list-style: none; margin: 0; padding: 0; display: flex; flex-wrap: wrap; gap: 10px 24px; font-size: .95rem; }
.leg li { display: inline-flex; align-items: center; gap: 10px; }
.leg .c { width: 26px; height: 26px; min-height: 0; aspect-ratio: auto; padding: 0; flex: none; }
.lg-t { display: grid; line-height: 1.25; }
.lg-t small { font-size: .8rem; color: var(--muted); }
.lg-n { font: 600 .82rem/1 var(--font-mono); font-variant-numeric: tabular-nums; padding: 4px 8px; border-radius: 999px; background: var(--paper); border: 1px solid var(--rule); }
.mo { position: relative; display: grid; gap: 18px; }
.mo-part { display: grid; gap: 8px; }
.mo-lab { display: flex; flex-wrap: wrap; align-items: baseline; gap: 2px 12px; }
.mo-lab b { font: 600 1.2rem/1.15 var(--font-display); }
.mo-lab span { font-size: .86rem; color: var(--muted); }
.mo-cases { display: grid; grid-template-columns: repeat(auto-fill, minmax(44px, 1fr)); gap: 4px; }
.c { position: relative; display: grid; justify-items: center; align-content: start; min-width: 0; min-height: 44px; aspect-ratio: 1; padding-top: 5px; border: 1.5px solid var(--c-bord, var(--rule)); border-radius: 7px; background: var(--sheet); color: var(--ink); font: 600 .78rem/1 var(--font-mono); font-variant-numeric: tabular-nums lining-nums; text-decoration: none; overflow: hidden; }
.c::before { content: ""; position: absolute; left: 0; right: 0; bottom: 0; height: 0; background: var(--c-fill, transparent); }
.c > span { position: relative; }
.c.n1 { --c-fill: var(--n1); --c-bord: var(--n1-bord); }
.c.n1::before { height: 30%; }
.c.n2 { --c-fill: var(--n2); --c-bord: var(--n2); }
.c.n2::before { height: 58%; }
.c.n3 { --c-fill: var(--n3); --c-bord: var(--n3); color: var(--on-n3); }
.c.n3::before { height: 100%; }
.c.n0 { background: transparent; border-style: dashed; --c-bord: var(--rule-ctl); color: var(--muted); }
a.c { cursor: pointer; }
a.c:hover { box-shadow: 0 0 0 2px var(--ink); }
a.c:focus-visible { outline: 3px solid var(--gold-ink); outline-offset: 2px; border-radius: 7px; z-index: 2; }
a.c.off { opacity: .2; }
.mo-aide { font-size: .88rem; color: var(--muted); }
.bulle { position: absolute; z-index: 20; left: 0; top: 0; width: max-content; max-width: min(19rem, calc(100vw - 48px)); background: var(--sheet); color: var(--ink); border: 1px solid var(--rule-ctl); border-radius: 10px; box-shadow: var(--shadow); padding: 10px 14px 12px; display: grid; gap: 3px; font-size: .9rem; line-height: 1.35; pointer-events: none; }
.bulle .b-k { font: 500 .72rem/1.3 var(--font-mono); letter-spacing: .08em; text-transform: uppercase; color: var(--muted); }
.bulle .b-t { font: 600 1.14rem/1.2 var(--font-display); }
.bulle .b-v { font-weight: 700; }
.bulle .b-p { color: var(--muted); font-size: .86rem; }

/* Version tableau de la mosaïque */
details.tv { border: 1px solid var(--rule); border-radius: 12px; background: var(--paper); }
details.tv > summary { list-style: none; display: flex; align-items: center; justify-content: space-between; gap: 12px; min-height: 48px; padding: 10px 16px; cursor: pointer; font-weight: 600; }
details.tv > summary::-webkit-details-marker { display: none; }
details.tv > summary::marker { content: ""; }
.tv-scroll { overflow: auto; max-height: min(70vh, 640px); border-top: 1px solid var(--rule); background: var(--sheet); border-radius: 0 0 12px 12px; }
.tv-scroll:focus-visible { outline-offset: -2px; }
table { width: 100%; border-collapse: collapse; font-size: .92rem; }
th, td { text-align: left; padding: 4px 12px; border-bottom: 1px solid var(--rule); vertical-align: middle; }
thead th { position: sticky; top: 0; z-index: 1; background: var(--sheet); padding-block: 10px; font: 500 .72rem/1.3 var(--font-mono); letter-spacing: .08em; text-transform: uppercase; color: var(--muted); white-space: nowrap; }
tbody th { font-weight: 500; }
tbody th a { display: inline-flex; align-items: center; min-height: 44px; }
th.nb, tbody td:nth-child(1), tbody td:nth-child(4), tbody td:nth-child(5) { text-align: right; font-variant-numeric: tabular-nums; }
tbody td:nth-child(6) { white-space: nowrap; }

/* La liste : outils */
.outils { display: grid; gap: 14px; background: var(--sheet); border: 1px solid var(--rule); border-radius: 12px; padding: 18px; }
.champ { display: grid; gap: 6px; max-width: 40rem; }
.champ label { font-weight: 600; }
.champ input { width: 100%; min-height: 48px; padding: 10px 14px; border: 1px solid var(--rule-ctl); border-radius: 10px; background: var(--paper); color: var(--ink); font: 400 1.05rem/1.3 var(--font-body); }
.champ input::placeholder { color: var(--muted); opacity: 1; }
.champ input:focus-visible { outline: 2px solid var(--gold-ink); outline-offset: 2px; }
.filtres { display: grid; gap: 10px; }
.groupe-f { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; }
.groupe-f > span { font: 500 .74rem/1.3 var(--font-mono); letter-spacing: .1em; text-transform: uppercase; color: var(--muted); min-width: 7.5rem; }
.chip { appearance: none; display: inline-flex; align-items: center; gap: 8px; min-height: 44px; padding: 6px 14px; border: 1px solid var(--rule-ctl); border-radius: 999px; background: var(--paper); color: var(--ink); font: 500 .95rem/1.2 var(--font-body); cursor: pointer; }
.chip:hover { border-color: var(--ink); }
.chip .ct { font: 500 .78rem/1 var(--font-mono); color: var(--muted); }
.chip[aria-pressed="true"] { background: var(--ink); border-color: var(--ink); color: var(--paper); }
.chip[aria-pressed="true"] .ct { color: inherit; opacity: .85; }
.etat-l { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 8px 14px; border-top: 1px solid var(--rule); padding-top: 12px; }
.etat { font-size: .98rem; color: var(--muted); }
.etat b { color: var(--ink); font-weight: 700; }
.btns { display: flex; flex-wrap: wrap; gap: 8px; }
.btn { appearance: none; display: inline-flex; align-items: center; justify-content: center; min-height: 44px; padding: 8px 16px; border-radius: 999px; border: 1px solid var(--rule-ctl); background: var(--paper); color: var(--ink); font: 600 .95rem/1.2 var(--font-body); cursor: pointer; }
.btn:hover { border-color: var(--ink); }

/* La liste : parties repliables */
.parties { display: grid; margin-top: 18px; }
details.partie { border-top: 1px solid var(--rule); }
details.partie:last-child { border-bottom: 1px solid var(--rule); }
details.partie > summary { list-style: none; display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 6px 16px; align-items: center; min-height: 64px; padding: 16px 6px; cursor: pointer; }
details.partie > summary::-webkit-details-marker { display: none; }
details.partie > summary::marker { content: ""; }
details.partie > summary:hover .p-t { color: var(--gold-ink); }
.p-tx { display: grid; gap: 2px; min-width: 0; }
.p-r { font: 500 .74rem/1.3 var(--font-mono); letter-spacing: .1em; text-transform: uppercase; color: var(--muted); }
.p-t { font: 600 clamp(1.4rem, 2.8vw, 1.8rem)/1.15 var(--font-display); }
.p-m { font-size: .92rem; color: var(--muted); }
.p-bar { display: flex; gap: 2px; height: 8px; width: min(100%, 26rem); margin-top: 8px; }
.p-bar i { display: block; height: 100%; border-radius: 2px; background: var(--c-fill); }
.p-bar i.n1 { --c-fill: var(--n1); }
.p-bar i.n2 { --c-fill: var(--n2); }
.p-bar i.n3 { --c-fill: var(--n3); }
.p-bar i.n0 { background: repeating-linear-gradient(135deg, var(--rule-ctl) 0 2px, transparent 2px 5px); }
details.partie > .fxs { list-style: none; margin: 0; padding: 4px 0 24px; display: grid; gap: 8px; }

/* Un fascicule */
.fx { display: grid; grid-template-columns: 3rem minmax(0, 1fr) auto; gap: 4px 16px; align-items: start; background: var(--sheet); border: 1px solid var(--rule); border-radius: 12px; padding: 12px 14px 14px; scroll-margin: 24px; }
.fx:focus { outline: none; }
.fx:focus-visible { outline: 2px solid var(--gold-ink); outline-offset: 2px; }
.fx > .c { width: 3rem; min-height: 3rem; padding-top: 7px; font-size: .86rem; }
.fx-corps { display: grid; gap: 2px; min-width: 0; }
.fx-t { font-size: 1.3rem; line-height: 1.2; overflow-wrap: anywhere; }
.fx-a { font-size: .92rem; color: var(--muted); }
.fx-at { display: grid; gap: 6px; margin-top: 6px; }
.fx-cv { font-size: .92rem; }
.fx-cv b { font-weight: 700; }
.fx-pages { list-style: none; margin: 0; padding: 0; display: flex; flex-wrap: wrap; gap: 6px; }
.fx-pages li { min-width: 0; max-width: 100%; }
.fx-pages a { display: inline-flex; flex-direction: column; justify-content: center; min-height: 44px; max-width: 100%; padding: 5px 12px; border: 1px solid var(--rule); border-radius: 10px; background: var(--paper); color: var(--ink); text-decoration: none; line-height: 1.25; }
.fx-pages a:hover { border-color: var(--n2); background: var(--sheet); }
.fx-pages b { font-weight: 600; font-size: .92rem; color: var(--gold-ink); }
.fx-pages i { font-style: normal; font-size: .8rem; color: var(--muted); }
.fx-plus { appearance: none; min-height: 44px; padding: 5px 14px; border: 1px dashed var(--rule-ctl); border-radius: 10px; background: transparent; color: var(--ink); font: 500 .92rem/1.2 var(--font-body); cursor: pointer; }
.fx-plus:hover { border-style: solid; border-color: var(--ink); }
.fx-lire { display: inline-flex; align-items: center; min-height: 44px; padding: 0 16px; border: 1px solid var(--ink); border-radius: 999px; color: var(--ink); font-weight: 600; font-size: .95rem; text-decoration: none; white-space: nowrap; }
.fx-lire:hover { background: var(--ink); color: var(--paper); }
.fx-lire .ar { font-family: var(--font-mono); }
.fx.flash { animation: flash 1.6s ease 1; }
@keyframes flash { 0%, 100% { box-shadow: 0 0 0 0 transparent; } 30% { box-shadow: 0 0 0 4px color-mix(in srgb, var(--gold) 55%, transparent); } }
.foot { border-top: 1px solid var(--rule); padding-top: 18px; font-size: .84rem; color: var(--muted); max-width: 84ch; display: grid; gap: 6px; }

@media (prefers-reduced-motion: reduce) {
  .chev { transition: none; }
  .fx.flash { animation: none; }
}
@media (max-width: 860px) {
  .hero { grid-template-columns: minmax(0, 1fr); gap: 28px; }
}
@media (max-width: 640px) {
  body { font-size: 16px; }
  .wrap { gap: 52px; }
  .feature { padding: 20px 12px 22px; }
  .mo-cases { gap: 3px; }
  .outils { padding: 14px; }
  .groupe-f > span { min-width: 0; width: 100%; }
  .fx { grid-template-columns: 2.6rem minmax(0, 1fr); gap: 4px 12px; padding: 12px 12px 14px 10px; }
  .fx > .c { width: 2.6rem; min-height: 2.6rem; padding-top: 6px; font-size: .8rem; }
  .fx-t { font-size: 1.2rem; }
  .fx-lire { grid-column: 2; justify-self: start; margin-top: 8px; }
}
@media print {
  .outils, .tv, .fx-plus, .actions { display: none !important; }
}'''

JS = r'''(function () {
  "use strict";
  /* Liste des fascicules : recherche (casse et accents ignorés, début des mots ; un nombre = un numéro de fascicule),
     filtres par partie et par couverture, parties repliables ; mosaïque : flèches du clavier (une seule case dans
     l’ordre de tabulation), bulle au survol et au clavier, un clic mène au fascicule. Sans JavaScript, tout reste
     lisible : les parties s’ouvrent d’un clic et les cases sont des liens. */
  var d = document;
  if (!d.querySelector || !window.addEventListener) return;
  var parties = Array.prototype.slice.call(d.querySelectorAll("details.partie[data-p]"));
  var lis = Array.prototype.slice.call(d.querySelectorAll("li.fx[data-n]"));
  if (!parties.length || !lis.length) return;
  var mo = d.getElementById("mo");
  var cases = mo ? Array.prototype.slice.call(mo.querySelectorAll("a.c[data-n]")) : [];
  var lignes = Array.prototype.slice.call(d.querySelectorAll("#tableau tbody tr[data-n]"));
  var calme = !!(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);
  var NIV = ["Pas encore dans l’atlas", "Peu couvert", "Moyennement couvert", "Bien couvert"];
  var PARTIE = ["Introduction", "Partie I", "Partie II", "Partie III", "Partie IV"];

  function plier(s) {
    s = String(s).toLowerCase();
    try { s = s.normalize("NFD").replace(/[̀-ͯ]/g, ""); } catch (e) { /* navigateur ancien : accents gardés */ }
    return s.replace(/œ/g, "oe").replace(/æ/g, "ae");
  }
  function esc(s) { return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); }

  /* Les fascicules, lus dans la page */
  var F = {};
  lis.forEach(function (li) {
    var n = +li.getAttribute("data-n"), t = li.querySelector(".fx-ti"), a = li.querySelector(".fx-a"), b = li.querySelector(".fx-pages b");
    F[n] = { n: n, li: li, p: li.getAttribute("data-p"), niv: +li.getAttribute("data-niv") || 0,
      r: +li.getAttribute("data-r") || 0, g: +li.getAttribute("data-g") || 0, ok: true,
      titre: t ? t.textContent : "", haut: b ? b.textContent : "", partie: li.closest("details.partie"),
      mots: plier(n + " " + (t ? t.textContent : "") + " " + (a ? a.textContent : "")).split(/[^a-z0-9]+/).filter(Boolean) };
  });

  /* « et N autres » : les pages au-delà des trois premières */
  Array.prototype.forEach.call(d.querySelectorAll("button.fx-plus"), function (bt) {
    var ul = bt.closest("ul"), extra = ul ? Array.prototype.slice.call(ul.querySelectorAll("li.x")) : [];
    if (!extra.length) return;
    extra.forEach(function (x) { x.hidden = true; });
    bt.parentNode.hidden = false;
    bt.addEventListener("click", function () {
      extra.forEach(function (x) { x.hidden = false; });
      bt.parentNode.hidden = true;
      var a = extra[0].querySelector("a");
      if (a) a.focus();
    });
  });

  /* Recherche et filtres */
  var outils = d.getElementById("outils"), q = d.getElementById("q"), etat = d.getElementById("etat");
  var raz = d.getElementById("raz"), tout = d.getElementById("tout");
  var chipsP = Array.prototype.slice.call(d.querySelectorAll("button[data-fp]"));
  var chipsC = Array.prototype.slice.call(d.querySelectorAll("button[data-fc]"));
  var E = { q: "", p: "", c: "" }, avant = null, minuterie = 0;

  function jetons(s) {
    var m = /^\s*(\d{1,3})\s*[:.]\s*\d/.exec(s);          // une référence tapée (57:6.5) : son fascicule
    if (m) return [m[1]];
    return plier(s).split(/[^a-z0-9]+/).filter(Boolean);
  }
  function retenu(f, js) {
    if (E.p !== "" && f.p !== E.p) return false;
    if (E.c === "oui" && !f.niv) return false;
    if (E.c === "non" && f.niv) return false;
    for (var i = 0; i < js.length; i++) {
      var t = js[i], ok = false;
      if (/^\d+$/.test(t)) { if (f.n !== +t) return false; continue; }
      for (var k = 0; k < f.mots.length && !ok; k++) if (f.mots[k].indexOf(t) === 0) ok = true;
      if (!ok) return false;
    }
    return true;
  }
  function majTout() {
    if (!tout) return;
    var vis = parties.filter(function (p) { return !p.hidden; });
    var ouverts = vis.length > 0 && vis.every(function (p) { return p.open; });
    tout.textContent = ouverts ? "Tout fermer" : "Tout ouvrir";
  }
  function appliquer() {
    var actifs = !!(E.q || E.p !== "" || E.c), js = jetons(E.q), n = 0, parP = {};
    if (actifs && !avant) avant = parties.map(function (p) { return p.open; });
    lis.forEach(function (li) {
      var f = F[+li.getAttribute("data-n")];
      f.ok = retenu(f, js);
      li.hidden = !f.ok;
      if (f.ok) { n++; parP[f.p] = (parP[f.p] || 0) + 1; }
    });
    if (actifs) parties.forEach(function (p) { var k = parP[p.getAttribute("data-p")] || 0; p.hidden = !k; p.open = k > 0; });
    else if (avant) { parties.forEach(function (p, i) { p.hidden = false; p.open = avant[i]; }); avant = null; }
    cases.forEach(function (c) { var f = F[+c.getAttribute("data-n")]; c.classList.toggle("off", actifs && !(f && f.ok)); });
    lignes.forEach(function (tr) { var f = F[+tr.getAttribute("data-n")]; tr.hidden = actifs && !(f && f.ok); });
    if (etat) etat.innerHTML = !actifs ? "<b>" + lis.length + "</b> fascicules" :
      n ? "<b>" + n + "</b> fascicule" + (n > 1 ? "s" : "") + " sur " + lis.length : "Aucun fascicule ne correspond.";
    if (raz) raz.hidden = !actifs;
    majTout();
  }
  function presser(groupe, b) { groupe.forEach(function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); }); }
  function effacer() {
    E.q = ""; E.p = ""; E.c = "";
    if (q) q.value = "";
    if (chipsP[0]) presser(chipsP, chipsP[0]);
    if (chipsC[0]) presser(chipsC, chipsC[0]);
    appliquer();
  }
  chipsP.forEach(function (b) { b.addEventListener("click", function () { E.p = b.getAttribute("data-fp"); presser(chipsP, b); appliquer(); }); });
  chipsC.forEach(function (b) { b.addEventListener("click", function () { E.c = b.getAttribute("data-fc"); presser(chipsC, b); appliquer(); }); });
  if (q) q.addEventListener("input", function () {
    clearTimeout(minuterie);
    minuterie = setTimeout(function () { E.q = q.value.trim(); appliquer(); }, 220);
  });
  if (raz) raz.addEventListener("click", function () { effacer(); if (q) q.focus(); });
  if (tout) tout.addEventListener("click", function () {
    var vis = parties.filter(function (p) { return !p.hidden; });
    var ouvrir = !vis.every(function (p) { return p.open; });
    vis.forEach(function (p) { p.open = ouvrir; });
    majTout();
  });
  parties.forEach(function (p) { p.addEventListener("toggle", majTout); });

  /* Aller à un fascicule (case de la mosaïque, ligne du tableau, adresse #f57) */
  function aller(n, doux) {
    var f = F[n];
    if (!f) return;
    if (f.li.hidden) effacer();
    if (f.partie && !f.partie.open) f.partie.open = true;
    if (!f.li.hasAttribute("tabindex")) f.li.tabIndex = -1;
    f.li.scrollIntoView({ block: "center", behavior: doux && !calme ? "smooth" : "auto" });
    try { f.li.focus({ preventScroll: true }); } catch (e) { f.li.focus(); }
    f.li.classList.remove("flash");
    void f.li.offsetWidth;
    f.li.classList.add("flash");
    setTimeout(function () { f.li.classList.remove("flash"); }, 1700);
  }
  d.addEventListener("click", function (ev) {
    if (ev.defaultPrevented || ev.button || ev.metaKey || ev.ctrlKey || ev.shiftKey || ev.altKey) return;
    var a = ev.target.closest && ev.target.closest('a[href^="#f"]');
    var m = a && /^#f(\d{1,3})$/.exec(a.getAttribute("href"));
    if (!m || !F[+m[1]]) return;
    ev.preventDefault();
    aller(+m[1], true);
    try { history.pushState(null, "", "#f" + m[1]); } catch (e) { /* adresse inchangée */ }
  });
  function depuisAdresse(doux) {
    var h = location.hash || "", m = /^#f(\d{1,3})$/.exec(h);
    if (m && F[+m[1]]) { aller(+m[1], doux); return; }
    m = /^#partie-(\d)$/.exec(h);
    var p = m && d.getElementById("partie-" + m[1]);
    if (p) { p.open = true; p.scrollIntoView({ block: "start" }); }
  }
  window.addEventListener("hashchange", function () { depuisAdresse(true); });

  /* La mosaïque : clavier et bulle */
  if (mo && cases.length) {
    var actif = 0;
    cases.forEach(function (c, i) { c.tabIndex = i ? -1 : 0; });
    var voisin = function (i, sens) {
      var r = cases[i].getBoundingClientRect(), x = r.left + r.width / 2, rang = null, best = null, ecart = 1e9;
      for (var k = i + sens; k >= 0 && k < cases.length; k += sens) {
        var s = cases[k].getBoundingClientRect();
        if (Math.abs(s.top - r.top) < 3) continue;                      // même rangée
        if (rang === null) rang = s.top; else if (Math.abs(s.top - rang) > 3) break;
        var dx = Math.abs(s.left + s.width / 2 - x);
        if (dx < ecart) { ecart = dx; best = k; }
      }
      return best;
    };
    mo.addEventListener("keydown", function (ev) {
      var i = cases.indexOf(ev.target), j = null;
      if (i < 0) return;
      switch (ev.key) {
        case "ArrowRight": j = i + 1; break;
        case "ArrowLeft": j = i - 1; break;
        case "ArrowDown": j = voisin(i, 1); break;
        case "ArrowUp": j = voisin(i, -1); break;
        case "Home": j = 0; break;
        case "End": j = cases.length - 1; break;
        default: return;
      }
      ev.preventDefault();
      if (j === null || j < 0 || j >= cases.length) return;
      cases[j].focus();
    });
    var bulle = d.createElement("div");
    bulle.className = "bulle";
    bulle.setAttribute("aria-hidden", "true");
    bulle.hidden = true;
    mo.appendChild(bulle);
    var montrer = function (c) {
      var f = F[+c.getAttribute("data-n")];
      if (!f) return;
      bulle.innerHTML = '<span class="b-k">' + (f.n ? "Fascicule " + f.n + " · " + PARTIE[+f.p] : "Introduction") + "</span>" +
        '<span class="b-t">' + esc(f.titre) + '</span><span class="b-v">' + NIV[f.niv] + "</span>" +
        (f.niv ? '<span class="b-p">' + f.r + " référence" + (f.r > 1 ? "s" : "") + " dans " + f.g + " page" + (f.g > 1 ? "s" : "") +
          (f.haut ? ", surtout « " + esc(f.haut) + " »" : "") + "</span>" : "");
      bulle.hidden = false;
      var r = c.getBoundingClientRect(), m = mo.getBoundingClientRect(), b = bulle.getBoundingClientRect();
      var x = Math.max(0, Math.min(r.left - m.left + r.width / 2 - b.width / 2, m.width - b.width));
      var y = r.top - b.height - 10 > 8 ? r.top - m.top - b.height - 10 : r.bottom - m.top + 10;
      bulle.style.left = Math.round(x) + "px";
      bulle.style.top = Math.round(y) + "px";
    };
    var cacher = function () { bulle.hidden = true; };
    mo.addEventListener("focusin", function (ev) {
      var i = cases.indexOf(ev.target);
      if (i < 0) return;
      if (i !== actif) { cases[actif].tabIndex = -1; actif = i; cases[i].tabIndex = 0; }
      var visible = true;
      try { visible = ev.target.matches(":focus-visible"); } catch (e) { /* sélecteur inconnu : bulle montrée */ }
      if (visible) montrer(ev.target); else cacher();
    });
    mo.addEventListener("focusout", cacher);
    mo.addEventListener("mouseover", function (ev) { var c = ev.target.closest && ev.target.closest("a.c[data-n]"); if (c) montrer(c); });
    mo.addEventListener("mouseout", function (ev) {
      var c = ev.target.closest && ev.target.closest("a.c[data-n]");
      if (c && !(ev.relatedTarget && c.contains(ev.relatedTarget))) cacher();
    });
    window.addEventListener("scroll", cacher, { passive: true });
  }

  if (outils) outils.hidden = false;
  appliquer();
  if (location.hash) depuisAdresse(false);
})();'''


# ── Relevé de l'atlas ───────────────────────────────────────────────────────────────────────────
def relever():
    """Relevé complet : fascicules, pages relevées, références par fascicule et par page, ancres choisies."""
    carte, adresses, pages, structure = lire_carte(), lire_adresses(), lire_pages(), lire_structure()
    connus = {p[0] for p in pages} | set(GABARIT_3D)
    releves, absentes = [], []
    for src, name, nom, court, desc in pages:
        if name in EXCLUES or src in EXCLUES:
            continue
        fichier = source_de(src)
        if not (SRC / fichier).exists():
            absentes.append((src, name, nom))
            continue
        r = releve_page(fichier, structure)
        releves.append({'src': src, 'fichier': fichier, 'name': name, 'nom': nom, 'court': court, 'r': r})
    hors = sorted(p.name for p in SRC.glob('*.html') if p.name not in connus and p.name != PAGE
                  and not re.search(r'test|essai|brouillon|copie|sauvegarde|\.bak', p.name, re.I))
    fasc = {}
    for n in range(197):
        titre, auteur, mots = carte[n]
        lp = []
        for k, pg in enumerate(releves):
            d = pg['r'].refs.get(n)
            if not d:
                continue
            anc = meilleure_ancre(list(d.values()))
            lab = pg['r'].etiquettes.get(anc, '') if anc else ''
            lp.append({'k': k, 'name': pg['name'], 'nom': pg['nom'], 'n': len(d), 'ancre': anc, 'lab': lab})
        lp.sort(key=lambda x: (-x['n'], x['k']))
        total = sum(x['n'] for x in lp)
        partie = next(p for p, _, _, ns in PARTIES if n in ns)
        fasc[n] = {'n': n, 'titre': titre, 'auteur': auteur, 'mots': mots, 'min': max(1, round(mots / MOTS_MINUTE)),
                   'partie': partie, 'pages': lp, 'refs': total, 'niv': niveau(total),
                   'url': URANTIA + adresses[n]}
    en_cours = {}
    noms_pages = {p[1]: p[2] for p in pages}
    for fichier, titre, ns in EN_COURS:
        present = any(p[0] == fichier or p[1] == fichier for p in pages if (SRC / source_de(p[0])).exists())
        if not present:
            for n in ns:
                en_cours[n] = (noms_pages.get(fichier, titre), fichier)
    return {'fasc': fasc, 'pages': releves, 'absentes': absentes, 'hors': hors, 'en_cours': en_cours,
            'structure': structure is not None}


# ── La page ─────────────────────────────────────────────────────────────────────────────────────
def libelle_page(pg):
    return 'Accueil de l’atlas' if pg['name'] == 'index.html' else pg['nom']


def lien_page(p):
    return p['name'] + (f'#{p["ancre"]}' if p['ancre'] else '')


def texte_couverture(f):
    if not f['niv']:
        return 'Pas encore dans l’atlas.'
    g = len(f['pages'])
    return (f'<b>{NIVEAUX[f["niv"]][1]}</b>{NB}: {f["refs"]} {pluriel(f["refs"], "référence")} '
            f'dans {g} {pluriel(g, "page")} de l’atlas')


def html_fascicule(f):
    n, niv = f['n'], f['niv']
    titre = e(f['titre'])
    puces = []
    for k, p in enumerate(f['pages']):
        lab = p['lab']
        if len(lab) > 48:
            lab = lab[:46].rsplit(' ', 1)[0].rstrip(' ,;:–') + '…'
        detail = (e(lab) + ' · ' if lab else '') + f'{p["n"]}{NB}réf.'
        cl = ' class="x"' if k >= 3 else ''
        puces.append(f'<li{cl}><a href="{e(lien_page(p))}"><b>{e(p["nom"] if p["name"] != "index.html" else "Accueil de l’atlas")}</b>'
                     f'<i>{detail}</i></a></li>')
    reste = len(f['pages']) - 3
    if reste > 0:
        puces.append(f'<li class="plus" hidden><button type="button" class="fx-plus">et {reste} '
                     f'{pluriel(reste, "autre")}</button></li>')
    pages = (f'<ul class="fx-pages" aria-label="Dans l’atlas">{"".join(puces)}</ul>'
             if puces else '')
    num = 'Introduction' if n == 0 else f'Fascicule {n}'
    return (f'<li class="fx" id="f{n}" data-n="{n}" data-p="{f["partie"]}" data-niv="{niv}" data-r="{f["refs"]}" '
            f'data-g="{len(f["pages"])}">'
            f'<span class="c n{niv}" aria-hidden="true"><span>{n}</span></span>'
            f'<div class="fx-corps"><h3 class="fx-t"><span class="sr-only">{num}{NB}: </span><span class="fx-ti">{titre}</span></h3>'
            f'<p class="fx-a">{e(f["auteur"])} · environ {f["min"]}{NB}min de lecture</p>'
            f'<div class="fx-at" data-recherche="non"><p class="fx-cv">{texte_couverture(f)}</p>{pages}</div></div>'
            f'<a class="fx-lire" href="{e(f["url"])}" target="_blank" rel="noopener">Lire sur urantia.org'
            f'<span class="ar" aria-hidden="true">{NB}↗</span><span class="sr-only">{NB}: {num.lower() if n else "l’Introduction"}'
            f' (nouvel onglet)</span></a></li>')


def construire_page(R, date):
    fasc = R['fasc']
    tous = [fasc[n] for n in range(197)]
    cpt = Counter(f['niv'] for f in tous)
    cites = 197 - cpt[0]
    nb_pages = len(R['pages'])
    heures = round(sum(f['mots'] for f in tous) / MOTS_MINUTE / 60)
    jour = date_fr(date)

    # Mosaïque : une rangée de cases par partie
    groupes = []
    for p, court, long_, ns in PARTIES:
        fs = [fasc[n] for n in ns]
        dans = sum(1 for f in fs if f['niv'])
        cases = []
        for f in fs:
            nom = 'Introduction' if f['n'] == 0 else f'{f["n"]}, {f["titre"]}'
            etat = NIVEAUX[f['niv']][1].lower() if f['niv'] else 'pas encore dans l’atlas'
            cases.append(f'<a class="c n{f["niv"]}" href="#f{f["n"]}" data-n="{f["n"]}" aria-label="{e(nom)}{NB}: {etat}">'
                         f'<span>{f["n"]}</span></a>')
        if p == 0:
            lab = f'<b>Introduction</b><span>fascicule 0 · {NIVEAUX[fs[0]["niv"]][1].lower()}</span>'
        else:
            lab = (f'<b>{court}</b><span>{e(long_)} · {ns[0]} à {ns[-1]}</span>'
                   f'<span>{dans} sur {len(fs)} dans l’atlas</span>')
        groupes.append(f'<div class="mo-part" role="group" aria-labelledby="mo-p{p}"><p class="mo-lab" id="mo-p{p}">{lab}</p>'
                       f'<div class="mo-cases">{"".join(cases)}</div></div>')
    legende = ''.join(f'<li><span class="c n{k}" aria-hidden="true"></span><span class="lg-t">{NIVEAUX[k][0]}'
                      f'<small>{NIVEAUX[k][2] if k else "pas encore dans l’atlas"}</small></span>'
                      f'<b class="lg-n">{cpt[k]}<span class="sr-only"> {pluriel(cpt[k], "fascicule")}</span></b></li>'
                      for k in (3, 2, 1, 0))

    # Tableau (version accessible de la mosaïque)
    lignes = []
    for f in tous:
        lignes.append(f'<tr data-n="{f["n"]}"><td>{f["n"]}</td><th scope="row"><a href="#f{f["n"]}">{e(f["titre"])}</a></th>'
                      f'<td>{CHIFFRES_ROMAINS[f["partie"]] or "Intr."}</td><td>{f["refs"]}</td>'
                      f'<td>{len(f["pages"])}</td><td>{NIVEAUX[f["niv"]][1]}</td></tr>')

    # Filtres
    chips_p = ['<button type="button" class="chip" data-fp="" aria-pressed="true">Toutes</button>']
    for p, court, long_, ns in PARTIES:
        chips_p.append(f'<button type="button" class="chip" data-fp="{p}" aria-pressed="false" title="{e(long_)}">'
                       f'{court}<span class="ct">{len(list(ns))}</span></button>')
    chips_c = ['<button type="button" class="chip" data-fc="" aria-pressed="true">Tous</button>',
               f'<button type="button" class="chip" data-fc="oui" aria-pressed="false">Couverts par l’atlas<span class="ct">{cites}</span></button>',
               f'<button type="button" class="chip" data-fc="non" aria-pressed="false">Non couverts<span class="ct">{cpt[0]}</span></button>']

    # Parties repliables
    parties = []
    for p, court, long_, ns in PARTIES:
        fs = [fasc[n] for n in ns]
        c = Counter(f['niv'] for f in fs)
        dans = len(fs) - c[0]
        minutes = sum(f['mots'] for f in fs) / MOTS_MINUTE
        barre = ''.join(f'<i class="n{k}" style="flex-grow:{c[k]}"></i>' for k in (3, 2, 1, 0) if c[k])
        if p == 0:
            tete = ('<span class="p-r">Fascicule 0</span><span class="p-t">Introduction</span>'
                    f'<span class="p-m">environ {duree(round(minutes))} de lecture · '
                    f'{NIVEAUX[fs[0]["niv"]][1].lower()}</span>')
        else:
            bien = f', dont {c[3]} bien {pluriel(c[3], "couvert")}' if c[3] else ''
            tete = (f'<span class="p-r">{court} · fascicules {ns[0]} à {ns[-1]}</span><span class="p-t">{e(long_)}</span>'
                    f'<span class="p-m">environ {duree(round(minutes))} de lecture · {dans} sur {len(fs)} dans l’atlas{bien}</span>')
        parties.append(f'<details class="partie" id="partie-{p}" data-p="{p}"><summary><span class="p-tx">{tete}'
                       f'<span class="p-bar" aria-hidden="true">{barre}</span></span><i class="chev" aria-hidden="true"></i></summary>\n'
                       f'<ol class="fxs">\n' + '\n'.join(html_fascicule(f) for f in fs) + '\n</ol></details>')

    corps = f'''<main class="wrap" id="contenu" lang="fr" data-releve="{date}">

  <header class="hero">
    <div class="hero-text">
      <p class="eyebrow"><span data-etape></span>Le Livre d’Urantia · les 197 fascicules</p>
      <h1>Le livre fascicule par fascicule</h1>
      <p class="lede">Les 197 fascicules du livre, de l’Introduction à «{NB}La foi de Jésus{NB}»{NB}: pour chacun, l’auteur que le texte lui donne, le temps de lecture, le lien vers son texte sur le site de la <span data-glossaire="non">Fondation Urantia</span>, et les pages de l’atlas qui en parlent.</p>
      <div class="actions" data-recherche="non">
        <a class="cta" href="#vue">Voir ce que couvre l’atlas <span class="ar" aria-hidden="true">↓</span></a>
        <a class="cta second" href="#liste">Aller à la liste <span class="ar" aria-hidden="true">↓</span></a>
      </div>
    </div>
    <aside class="kpi" aria-label="Le livre et l’atlas en chiffres" data-recherche="non">
      <dl>
        <div><dt>fascicules</dt><dd>197</dd></div>
        <div><dt>cités dans l’atlas</dt><dd>{cites}</dd></div>
        <div><dt>bien couverts</dt><dd>{cpt[3]}</dd></div>
        <div><dt>de lecture</dt><dd>≈{NB}{heures}{NB}h</dd></div>
      </dl>
      <p class="note">Relevé du {jour} dans {nb_pages} pages de l’atlas. Durées estimées à {MOTS_MINUTE} mots par minute.</p>
    </aside>
  </header>

  <section id="vue" class="feature" aria-labelledby="h-vue">
    <div class="sec-head">
      <p class="eyebrow">Vue d’ensemble</p>
      <h2 id="h-vue">Ce que l’atlas couvre du livre</h2>
      <p>Chaque case est un fascicule, dans l’ordre du livre. Plus elle est pleine, plus l’atlas en parle{NB}: elle compte les passages du fascicule que citent ses pages. Une case vide attend encore sa page. Touche une case pour aller au fascicule.</p>
    </div>
    <ul class="leg" aria-label="Légende de la mosaïque" data-recherche="non">{legende}</ul>
    <div class="mo" id="mo" role="group" aria-label="Mosaïque des 197 fascicules" aria-describedby="mo-aide" data-recherche="non" data-glossaire="non">
      {"".join(groupes)}
    </div>
    <p class="mo-aide" id="mo-aide" data-recherche="non">Au clavier{NB}: Tab jusqu’à la mosaïque, puis les flèches pour passer d’un fascicule à l’autre{NB}; Entrée mène au fascicule.</p>
    <details class="tv" id="tableau" data-recherche="non" data-glossaire="non">
      <summary><span>La mosaïque sous forme de tableau</span><i class="chev" aria-hidden="true"></i></summary>
      <div class="tv-scroll" role="region" aria-labelledby="tv-titre" tabindex="0">
        <table>
          <caption class="sr-only" id="tv-titre">Les 197 fascicules{NB}: partie, références dans l’atlas, nombre de pages et couverture</caption>
          <thead><tr><th scope="col" class="nb">N°</th><th scope="col">Titre</th><th scope="col">Partie</th><th scope="col" class="nb">Références</th><th scope="col" class="nb">Pages</th><th scope="col">Couverture</th></tr></thead>
          <tbody>
{chr(10).join(lignes)}
          </tbody>
        </table>
      </div>
    </details>
  </section>

  <section id="liste" aria-labelledby="h-liste">
    <div class="sec-head">
      <p class="eyebrow">Les quatre parties et l’Introduction</p>
      <h2 id="h-liste">Les 197 fascicules</h2>
      <p class="hint">Ouvre une partie, ou cherche un fascicule par son titre, son numéro ou son auteur. «{NB}Lire sur urantia.org{NB}» ouvre le texte dans un nouvel onglet{NB}; les autres liens mènent aux pages de l’atlas, triées selon le nombre de passages qu’elles citent.</p>
    </div>
    <div class="outils" id="outils" data-recherche="non" hidden>
      <div class="champ" role="search">
        <label for="q">Chercher un fascicule</label>
        <input type="search" id="q" placeholder="Titre, numéro ou auteur" autocomplete="off" spellcheck="false" aria-describedby="etat">
      </div>
      <div class="filtres">
        <div class="groupe-f" role="group" aria-labelledby="f-partie"><span id="f-partie">Partie</span>{"".join(chips_p)}</div>
        <div class="groupe-f" role="group" aria-labelledby="f-cv"><span id="f-cv">Dans l’atlas</span>{"".join(chips_c)}</div>
      </div>
      <div class="etat-l">
        <p class="etat" id="etat" role="status"><b>197</b> fascicules</p>
        <div class="btns"><button type="button" class="btn" id="raz" hidden>Tout afficher</button><button type="button" class="btn" id="tout">Tout ouvrir</button></div>
      </div>
    </div>
    <div class="parties" id="parties" data-glossaire="non">
{chr(10).join(parties)}
    </div>
  </section>

  <footer class="foot">
    <p>Titres, auteurs et nombres de mots{NB}: <i>Le Livre d’Urantia</i>, traduction française de la <span data-glossaire="non">Fondation Urantia</span>, édition 2024{NB}; l’auteur indiqué est celui que le livre déclare pour chaque fascicule. Durées estimées à {MOTS_MINUTE} mots par minute, arrondies.</p>
    <p>Couverture{NB}: passages cités (fascicule:section.paragraphe) dans {nb_pages} pages de l’atlas, relevés le {jour}{NB}; un passage compte une fois par page. Le glossaire et «{NB}Les auteurs déclarés et le livre en chiffres{NB}», qui parcourent tout le livre, ne sont pas comptés. Paliers{NB}: peu, 1 à 3 références{NB}; moyen, 4 à 11{NB}; bien couvert, 12 et plus.</p>
    <p>Les liens «{NB}Lire sur urantia.org{NB}» ouvrent le texte sur le site de la <span data-glossaire="non">Fondation Urantia</span>.</p>
  </footer>

</main>'''
    tete = (f'<title>Le livre fascicule par fascicule</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n'
            f'{POLICES}\n<style>\n{CSS}\n</style>\n')
    page = tete + '\n' + corps + '\n<script>\n' + JS + '\n</script>\n'
    bloc = '\n<script id="refs-urantia">\n' + REFS_JS.read_text(encoding='utf-8').strip() + '\n</script>\n'
    page = page.rstrip('\n') + '\n' + bloc                 # comme liens_refs.py injecte
    page = page.replace('\r\n', '\n')
    if ' ' in page or '&#8239;' in page:
        sys.exit('Espace fine insécable trouvée dans la page : à remplacer par l’insécable ordinaire.')
    return page


# ── Le rapport ──────────────────────────────────────────────────────────────────────────────────
def construire_rapport(R, date):
    fasc, en_cours = R['fasc'], R['en_cours']
    tous = [fasc[n] for n in range(197)]
    cpt = Counter(f['niv'] for f in tous)
    aucun = [f for f in tous if f['niv'] == 0]
    peu = [f for f in tous if f['niv'] == 1]
    dans_prop = {n for _, _, ns, _, _ in PROPOSITIONS for n in ns}

    def etat(f):
        if f['n'] in en_cours:
            nom, fichier = en_cours[f['n']]
            return f'en cours : « {nom} » (`{fichier}`)'
        for k, (titre, _, ns, _, _) in enumerate(PROPOSITIONS, 1):
            if f['n'] in ns:
                return f'à couvrir : proposition {k}'
        if f['n'] in RATTACHEMENTS:
            return 'à couvrir : voir « Hors propositions »'
        return 'à couvrir'

    L = ['# Couverture du livre par l’atlas', '',
         f'> Rapport **généré** par `python -I erudit/visuels/source/fascicules.py`, avec la page `fascicules.html` : '
         f'ne pas l’éditer à la main, relancer le script après l’ajout ou la modification d’une page. Relevé du {date}.', '',
         'Une **référence** est un passage cité sous la forme `fascicule:section.paragraphe` (ou `fascicule:section`, ou une '
         'plage) dans une page de l’atlas : dans un élément `.ref`, dans le texte, ou dans les données d’un script (vue 3D, '
         'frises). Chaque référence distincte compte une fois par page ; le total d’un fascicule additionne ses pages. '
         f'Paliers : **bien couvert** {SEUILS[2]} et plus, **moyen** {SEUILS[1]} à {SEUILS[2] - 1}, '
         f'**peu** {SEUILS[0]} à {SEUILS[1] - 1}, **aucune** référence.', '',
         '## En bref', '']
    total_refs = sum(f['refs'] for f in tous)
    L.append(f'- **{len(R["pages"])} pages** relevées, **{nombre(total_refs)} références** distinctes (page par page), '
             f'dans **{197 - cpt[0]} fascicules sur 197**.')
    nb_ec = sum(1 for f in aucun if f['n'] in en_cours)
    nb_ec_peu = sum(1 for f in peu if f['n'] in en_cours)
    L.append(f'- Bien couverts : **{cpt[3]}** · moyens : **{cpt[2]}** · peu couverts : **{cpt[1]}**'
             f'{f" (dont {nb_ec_peu} en cours)" if nb_ec_peu else ""} · sans référence : **{cpt[0]}**'
             f'{f" (dont {nb_ec} en cours)" if nb_ec else ""}.')
    reste = [f for f in aucun + peu if f['n'] not in en_cours]
    L.append(f'- Hors pages en cours, **{len(reste)} fascicules** restent à couvrir (0 à {SEUILS[1] - 1} références) : '
             + ', '.join(str(f['n']) for f in sorted(reste, key=lambda x: x['n'])) + '.')
    L += ['', '| Partie | Fascicules | Bien | Moyen | Peu | Aucune | Peu ou aucune, page en cours |', '|---|---:|---:|---:|---:|---:|---:|']
    for p, court, long_, ns in PARTIES:
        fs = [fasc[n] for n in ns]
        c = Counter(f['niv'] for f in fs)
        ec = sum(1 for f in fs if f['n'] in en_cours and f['niv'] <= 1)
        L.append(f'| {court if p else "Introduction"}{" — " + long_ if p else ""} | {len(fs)} | {c[3]} | {c[2]} | {c[1]} | {c[0]} | {ec} |')
    L += ['', 'Pages relevées (références distinctes, fascicules cités) :', '']
    for pg in sorted(R['pages'], key=lambda x: -sum(len(d) for d in x['r'].refs.values())):
        n = sum(len(d) for d in pg['r'].refs.values())
        L.append(f'- {libelle_page(pg)} (`{pg["name"]}`{", lue dans " + pg["fichier"] if pg["fichier"] != pg["src"] else ""}) : '
                 f'{nombre(n)} références, {len(pg["r"].refs)} fascicules')

    L += ['', f'## Fascicules sans aucune référence ({len(aucun)})', '',
          '| N° | Titre | Auteur déclaré | Mots | État |', '|---:|---|---|---:|---|']
    for f in aucun:
        L.append(f'| {f["n"]} | {f["titre"]} | {f["auteur"]} | {nombre(f["mots"])} | {etat(f)} |')
    L += ['', f'## Fascicules peu couverts : {SEUILS[0]} à {SEUILS[1] - 1} références ({len(peu)})', '',
          '| N° | Titre | Réf. | Pages qui le citent | État |', '|---:|---|---:|---|---|']
    for f in peu:
        qui = ', '.join(f'{libelle_page(p)} ({p["n"]})' for p in f['pages'])
        L.append(f'| {f["n"]} | {f["titre"]} | {f["refs"]} | {qui} | {etat(f)} |')

    L += ['', '## Propositions : pages ou sections à créer', '',
          'Par grands sujets, de la partie I à la partie IV ; les fascicules des pages en cours en sont exclus. L’état est '
          'recalculé à chaque relevé : une proposition est **comblée** quand tous ses fascicules ont au moins '
          f'{SEUILS[1]} références.', '']
    for k, (titre, genre, ns, voisins, phrase) in enumerate(PROPOSITIONS, 1):
        fs = [fasc[n] for n in ns]
        comblee = all(f['refs'] >= SEUILS[1] for f in fs)
        L.append(f'### {k}. « {titre} » — {genre}{" (comblée)" if comblee else ""}')
        L.append('')
        L.append('- Fascicules : ' + ' · '.join(f'**{f["n"]}** {f["titre"]} ({f["refs"]} réf.)' for f in fs))
        if voisins:
            L.append('- À relier : ' + ', '.join(f'{fasc[n]["n"]} ({fasc[n]["refs"]} réf.)' for n in voisins))
        L.append(f'- Ce qu’elle montrerait : {phrase}')
        L.append('')
    hors = [f for f in reste if f['n'] not in dans_prop]
    if hors:
        L.append('**Hors propositions** : ' + ' ; '.join(
            f'{f["n"]} « {f["titre"]} » ({f["refs"]} réf.) → {RATTACHEMENTS.get(f["n"], "à rattacher à une page existante")}'
            for f in hors) + '.')
        L.append('')

    L += ['## Pages en préparation', '',
          'Elles ne sont pas comptées tant que leur source manque ; leurs fascicules sont marqués « en cours » ci-dessus.', '',
          '| Page | Fichier | Fascicules | État |', '|---|---|---|---|']
    for fichier, titre, ns in EN_COURS:
        enc = any(en_cours.get(n, ('', ''))[1] == fichier for n in ns)
        L.append(f'| {titre} | `{fichier}` | {plage_texte(ns)} | {"en cours (source absente)" if enc else "présente : relevée"} |')
    autres = [a for a in R['absentes'] if a[0] not in {x[0] for x in EN_COURS}]
    if autres:
        L.append('')
        L.append('Autres pages annoncées dans `construire_site.py` dont la source manque (non comptées) : '
                 + ', '.join(f'« {nom} » (`{src}`)' for src, _, nom in autres) + '.')

    L += ['', '## Méthode et contrôles', '',
          '- Pages relevées : celles de la liste `PAGES` de `construire_site.py` dont la source est présente, sauf le '
          'glossaire et « Les auteurs déclarés et le livre en chiffres », qui parcourent tout le livre, et la page '
          '`fascicules.html` elle-même ; la vue 3D est lue dans son gabarit `urantia-paradis-3d.src.html` (mêmes textes).',
          '- Lu : le texte de la page (éléments `.ref` compris), et les chaînes de ses scripts, hors commentaires et hors '
          'script commun des références ; ni les styles, ni les attributs (`data-ref`, `data-bible`…).',
          '- Formes courtes (`30:2`) gardées dans un `.ref`, entre parenthèses ou dans une liste de références ; écartées '
          'ailleurs, comme les versets bibliques (« Jean 14:2 ») et les nombres à zéro initial (heures).',
          '- Liens de la page : vers la section (`section`, `article` ou `aside` à identifiant, non cachés) ou le bloc de la '
          'vue 3D (niveau, panneau, astre) qui réunit au moins la moitié des références du fascicule ; sinon, le haut de la page.']
    ecartees = Counter()
    for pg in R['pages']:
        for (motif, txt), k in pg['r'].ecartees.items():
            ecartees[(motif, pg['name'])] += k
    if R['structure']:
        L.append('- Chaque référence est vérifiée dans le texte du livre (ancres du fichier source) : un passage absent est écarté.')
    else:
        L.append('- Texte du livre absent : les références n’ont pas pu être vérifiées une à une.')
    if ecartees:
        L.append('- Écartées : ' + ' ; '.join(f'{k} × {motif} ({name})' for (motif, name), k in sorted(ecartees.items())) + '.')
        absents = [(pg['name'], txt) for pg in R['pages'] for (motif, txt), k in pg['r'].ecartees.items()
                   if motif == 'passage absent du livre']
        if absents:
            L.append('- **À corriger dans les pages** (passages absents du livre) : '
                     + ', '.join(f'`{txt}` ({name})' for name, txt in absents) + '.')
    else:
        L.append('- Aucune référence écartée.')
    if R['hors']:
        L.append('- Pages du dossier source hors de `PAGES`, non relevées : ' + ', '.join(f'`{h}`' for h in R['hors']) + '.')
    return '\n'.join(L) + '\n'


# ── Écriture ────────────────────────────────────────────────────────────────────────────────────
def ecrire(chemin, fabrique, date):
    """Écrit le fichier (fins de ligne CRLF) s'il change ; avec la date du relevé précédent si rien d'autre ne change."""
    ancien = chemin.read_bytes() if chemin.exists() else b''
    m = re.search(rb'(?:data-releve="|Relev\xc3\xa9 du )(\d{4}-\d{2}-\d{2})', ancien)
    if m and m.group(1).decode() != date:
        essai = fabrique(m.group(1).decode()).replace('\n', '\r\n').encode('utf-8')
        if essai == ancien:
            return False
    neuf = fabrique(date).replace('\n', '\r\n').encode('utf-8')
    if neuf == ancien:
        return False
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_bytes(neuf)
    return True


def main():
    args = sys.argv[1:]
    sortie_page, sortie_rapport = SRC / PAGE, SRC.parent / RAPPORT
    if args[:1] == ['--essai'] and len(args) == 2:
        sortie_page, sortie_rapport = Path(args[1]) / PAGE, Path(args[1]) / RAPPORT
    elif args:
        sys.exit(__doc__)
    date = datetime.date.today().isoformat()
    R = relever()
    p = ecrire(sortie_page, lambda d: construire_page(R, d), date)
    r = ecrire(sortie_rapport, lambda d: construire_rapport(R, d), date)
    fasc = R['fasc']
    cpt = Counter(f['niv'] for f in fasc.values())
    taille = sortie_page.stat().st_size if sortie_page.exists() else 0
    print(f'{PAGE} : {"écrite" if p else "inchangée"} ({round(taille / 1024)} Ko) · {RAPPORT} : {"écrit" if r else "inchangé"}')
    print(f'{len(R["pages"])} pages relevées · {197 - cpt[0]} fascicules sur 197 cités · bien {cpt[3]}, moyen {cpt[2]}, '
          f'peu {cpt[1]}, aucune référence {cpt[0]} (dont {sum(1 for n in R["en_cours"] if fasc[n]["niv"] == 0)} en cours)')
    for src, name, nom in R['absentes']:
        print(f'avertissement : source absente, page non relevée : {src} (« {nom} »)')
    for h in R['hors']:
        print(f'avertissement : {h} est dans le dossier source mais pas dans PAGES : non relevée')
    if not R['structure']:
        print('avertissement : texte du livre absent, références non vérifiées une à une')


if __name__ == '__main__':
    main()
