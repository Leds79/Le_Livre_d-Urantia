"""Index des noms de l’atlas : données (index-des-noms.json), contrôle et liste de la page « Index des noms ».

Chaque entrée : le nom dans la graphie du livre, une précision pour les homonymes, une catégorie, une identification dans
nos mots (sans citation), 1 à 3 références, les formes qui servent au compte, le nombre de paragraphes où paraît le nom,
les autres noms, les renvois, les pages de l’atlas qui en parlent et le terme du glossaire.

Usage (depuis le dossier qui contient ce script ; le texte du livre et outils/ub.py ne sont lus que dans la copie de travail
de l’auteur) :
  python -I index_des_noms.py compte index-des-noms.json
      recompte, dans le texte du livre, les paragraphes où paraît l’une des formes de chaque nom (champ « n »).
  python -I index_des_noms.py atlas index-des-noms.json [recherche.js]
      choisit les pages de l’atlas qui parlent de chaque nom (au plus trois, avec l’ancre de la section où il revient le plus),
      d’après l’index de la recherche du site construit, et le terme du glossaire qui lui correspond.
  python -I index_des_noms.py verifie index-des-noms.json
      contrôle la structure (identifiants, doublons, catégories, renvois, liens de l’atlas et du glossaire, typographie) et,
      si le texte du livre est là, chaque référence (elle existe et contient l’une des formes du nom) et chaque nombre.
      Code de sortie 1 s’il reste un écart.
  python -I index_des_noms.py page index-des-noms.json index-des-noms.html
      écrit dans la page, entre <!--NOMS:DEBUT …--> et <!--NOMS:FIN-->, la liste de A à Z, ainsi que l’index des lettres
      (<!--AZ:…-->), les catégories (<!--CATS:…-->) et les nombres (data-noms-…). Fins de ligne CRLF, espaces insécables
      écrites &nbsp;. L’empreinte des données est inscrite dans le marqueur.

Ordre de mise à jour, après une modification de index-des-noms.json : compte, puis atlas (sur un site construit récemment),
verifie (0 écart), page ; le bloc des références se pose une fois avec
  python -I liens_refs.py injecte refs-urantia.js index-des-noms.html
qui réécrit la page en fins de ligne LF : relancer alors « page », qui rétablit les fins de ligne CRLF.

Formes : chaînes exactes du texte, casse stricte, mot entier (une élision devant compte, un trait d’union fait partie du mot) ;
une forme qui commence par une minuscule vaut aussi avec une majuscule initiale ; « forme@93-98,131 » ne compte que dans ces
fascicules. Compte : « exact », « min » (seules des formes propres sont comptées : au moins N) ou « env » (formes partagées
restreintes par fascicules : environ N).
"""
import ast
import collections
import hashlib
import html
import importlib.util
import json
import re
import sys
import unicodedata
from pathlib import Path

ICI = Path(__file__).resolve().parent
CATS = {   # ordre d’affichage des filtres : (pluriel, singulier, libellé court des filtres sur téléphone)
    'etre': ('Êtres nommés', 'Être nommé', 'Êtres'),
    'ordre': ('Ordres d’êtres', 'Ordre d’êtres', 'Ordres'),
    'cosmos': ('Mondes et lieux cosmiques', 'Monde ou lieu cosmique', 'Mondes'),
    'terre': ('Lieux sur Terre', 'Lieu sur Terre', 'Lieux'),
    'peuple': ('Peuples et races', 'Peuple ou race', 'Peuples'),
    'bible': ('Personnages bibliques', 'Personnage biblique', 'Bible'),
    'histoire': ('Personnages historiques', 'Personnage historique', 'Histoire'),
    'religion': ('Religions et écoles', 'Religion ou école', 'Religions'),
}
# pages qui parcourent tout le livre (ou qui n’en parlent qu’en passant) : pas de lien « dans l’atlas » vers elles
EXCLUES = {'index.html', 'glossaire.html', 'fascicules.html', 'auteurs-et-chiffres.html', 'parcours-de-lecture.html',
           'index-des-noms.html'}
NOM_3D = 'Vue 3D'
MAX_PAGES = 3
RX_REF = re.compile(r'^(\d{1,3}):(\d{1,2})\.(\d{1,3})$')
NB = '&nbsp;'


# ── Outils de texte ─────────────────────────────────────────────────────────────────────────────────
def plier(s):
    """Minuscules sans accents ; apostrophes et traits d’union en espaces (même règle que le script de la page)."""
    s = unicodedata.normalize('NFD', str(s))
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn').lower()
    s = s.replace('œ', 'oe').replace('æ', 'ae')
    s = re.sub(r'[’‘ʼ\'\-‑]', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()


def ident_de(e):
    """Identifiant stable, sans accents : n-gabriel, n-joseph-pere-de-jesus."""
    base = plier(e['nom'] + (' ' + e['precision'] if e.get('precision') else ''))
    return 'n-' + re.sub(r'[^a-z0-9]+', '-', base).strip('-')


def typo(s):
    """Texte → HTML : échappement, puis insécables (&nbsp;) devant : ; ! ? et dans « », jamais d’espace fine."""
    s = re.sub(r'[ \u00a0\u202f]+(?=[:;!?](?:\s|$))', '\u00a0', s)
    s = re.sub(r'«[ \u00a0\u202f]*', '«\u00a0', s)
    s = re.sub(r'[ \u00a0\u202f]*»', '\u00a0»', s)
    s = s.replace('\u202f', '\u00a0')
    return html.escape(s, quote=False).replace('\u00a0', NB)


def attr(s):
    return html.escape(s, quote=True)


def nombre(n):
    return f'{n:,}'.replace(',', NB)


def charger(chemin):
    return json.loads(Path(chemin).read_text(encoding='utf-8'))


def ecrire_json(chemin, d):
    Path(chemin).write_text(json.dumps(d, ensure_ascii=False, indent=1) + '\n', encoding='utf-8', newline='\n')


def empreinte(chemin):
    return hashlib.sha256(Path(chemin).read_bytes().replace(b'\r\n', b'\n')).hexdigest()[:12]


def pages_du_site():
    """(fichier source, nom dans le site, nom canonique, nom court) de chaque page de PAGES (construire_site.py), sans l’exécuter."""
    src = (ICI / 'construire_site.py').read_text(encoding='utf-8')
    for noeud in ast.parse(src).body:
        if isinstance(noeud, ast.Assign) and any(getattr(t, 'id', '') == 'PAGES' for t in noeud.targets):
            return [tuple(p[:4]) for p in ast.literal_eval(noeud.value)]
    return []


def analyser_formes(liste):
    out = []
    for f in liste:
        f, _, p = f.partition('@')
        portee = None
        if p:
            portee = []
            for morceau in p.split(','):
                a, _, b = morceau.strip().partition('-')
                portee.append((int(a), int(b or a)))
        out.append((f.strip(), portee))
    return out


def rx_forme(f):
    variantes = [f]
    if f[:1].islower():
        variantes.append(f[:1].upper() + f[1:])
    return r'(?<![\w-])(?:' + '|'.join(re.escape(v) for v in variantes) + r')(?![\w-])'


def rx_formes(liste):
    fs = [f for f, _ in analyser_formes(liste)]
    return re.compile('|'.join(rx_forme(f) for f in fs)) if fs else None


# ── Le texte du livre (copie de travail de l’auteur) ────────────────────────────────────────────────
def livre():
    ub_py = ICI.parents[2] / 'outils' / 'ub.py'
    texte = ICI.parents[2] / 'UF-FRE-001-1960-3.5.md'
    if not (ub_py.exists() and texte.exists()):
        return None
    spec = importlib.util.spec_from_file_location('ub', ub_py)
    ub = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ub)
    return ub.Livre(str(texte))


class Compteur:
    """Paragraphes numérotés où paraît une forme (index inversé des mots, puis expression régulière)."""
    RX_TOK = re.compile(r'[^\W_]+(?:-[^\W_]+)*')

    def __init__(self, L):
        self.L = L
        self.paras = [p for p in L.paras if not p['special']]
        self.ix = collections.defaultdict(set)
        for k, p in enumerate(self.paras):
            for t in self.RX_TOK.findall(p['plat']):
                self.ix[t].add(k)
        self.memo = {}

    def candidats(self, f):
        ens = []
        for i, t in enumerate(self.RX_TOK.findall(f)):
            s = set(self.ix.get(t, ()))
            if i == 0 and t[:1].islower():
                s |= self.ix.get(t[:1].upper() + t[1:], set())
            ens.append(s)
        if not ens:
            return set()
        ens.sort(key=len)
        res = ens[0]
        for s in ens[1:3]:
            res = res & s
        return res

    def paras_de(self, formes):
        res = set()
        for f, portee in analyser_formes(formes):
            cle = (f, tuple(portee) if portee else None)
            if cle not in self.memo:
                rx = re.compile(rx_forme(f))
                self.memo[cle] = {k for k in self.candidats(f)
                                  if (not portee or any(a <= self.paras[k]['f'] <= b for a, b in portee))
                                  and rx.search(self.paras[k]['plat'])}
            res |= self.memo[cle]
        return res

    def para(self, r):
        m = RX_REF.match(r)
        if not m:
            return None
        i = self.L.index.get(tuple(int(x) for x in m.groups()))
        return None if i is None or self.L.paras[i]['special'] else self.L.paras[i]


# ── compte ──────────────────────────────────────────────────────────────────────────────────────────
def cmd_compte(chemin):
    L = livre()
    if L is None:
        sys.exit('texte du livre absent : le compte se fait dans la copie de travail de l’auteur')
    C = Compteur(L)
    d = charger(chemin)
    changes = 0
    for e in d['noms']:
        n = len(C.paras_de(e['formes']))
        if e.get('n') != n:
            e['n'] = n
            changes += 1
    ecrire_json(chemin, d)
    print(f'compte : {len(d["noms"])} noms, {changes} nombre(s) mis à jour')


# ── atlas ───────────────────────────────────────────────────────────────────────────────────────────
def lire_recherche(chemin):
    t = Path(chemin).read_text(encoding='utf-8')
    return json.loads(t[t.index('=') + 1:].rstrip().rstrip(';'))


def formes_atlas(e, homonymes):
    """Formes sûres pour repérer le nom dans les pages : sans portée, et sans le nom nu s’il est partagé."""
    fs = [f for f, p in analyser_formes(e['formes']) if not p]
    fs += [a for a in e.get('aussi', []) if a]
    if e['nom'] not in homonymes:
        fs.append(e['nom'])
    else:
        fs = [f for f in fs if f != e['nom']]
    return list(dict.fromkeys(fs))


def cmd_atlas(chemin, chemin_recherche=None):
    d = charger(chemin)
    candidats = [Path(chemin_recherche)] if chemin_recherche else [ICI.parents[2] / 'site' / 'assets' / 'recherche.js',
                                                                    ICI.parent / 'assets' / 'recherche.js']
    rj = next((c for c in candidats if c.exists()), None)
    if not rj:
        sys.exit('index de la recherche introuvable (assets/recherche.js du site construit)')
    ix = lire_recherche(rj)
    pages = {n: (court if n != 'atlas-3d.html' else NOM_3D) for _, n, _, court in pages_du_site()}
    noms_canon = {n: canon for _, n, canon, _ in pages_du_site()}
    ordre_pages = [n for _, n, _, _ in pages_du_site()]   # départage stable des égalités
    # textes par section
    textes = collections.defaultdict(list)
    for s, t in ix['T']:
        textes[s].append(t)
    sections = []   # (page, ancre, titre, texte)
    for k, (p, ancre, titre, *drap) in enumerate(ix['S']):
        page = ix['P'][p][0]
        if page in EXCLUES or page not in pages:
            continue
        cherchable = not drap or drap[0] != 'i'
        sections.append((page, ancre, titre if cherchable else '', ' '.join(textes.get(k, []))))
    # index inversé des mots des sections (casse stricte) : seules les sections qui contiennent un mot de la forme sont lues
    par_mot = collections.defaultdict(set)
    for k, (_, _, titre, texte) in enumerate(sections):
        for t in Compteur.RX_TOK.findall(titre + ' ' + texte):
            par_mot[t].add(k)

    def sections_de(fs):
        res = set()
        for f in fs:
            toks = Compteur.RX_TOK.findall(f)
            if not toks:
                continue
            ens = []
            for i, t in enumerate(toks):
                s = set(par_mot.get(t, ()))
                if i == 0 and t[:1].islower():
                    s |= par_mot.get(t[:1].upper() + t[1:], set())
                ens.append(s)
            res |= min(ens, key=len)
        return sorted(res)
    noms_comptes = collections.Counter(e['nom'] for e in d['noms'])
    homonymes = {n for n, c in noms_comptes.items() if c > 1}
    gl = json.loads((ICI / 'glossaire-atlas.json').read_text(encoding='utf-8'))['termes']
    gl_formes = {}
    for t in gl:
        for f in t['formes'] + [t['terme']]:
            gl_formes.setdefault(f, t['id'])
    for e in d['noms']:
        if 'atlas_fixe' in e:                 # choix fait à la main (homonymes, page évidente que le calcul manque)
            e['atlas'] = [[h, pages[h.split('#')[0]]] for h in e['atlas_fixe'] if h.split('#')[0] in pages]
        else:
            fs = formes_atlas(e, homonymes)
            rx = re.compile('|'.join(rx_forme(f) for f in fs)) if fs else None
            score_p, meilleure = collections.Counter(), {}
            if rx:
                for k in sections_de(fs):
                    page, ancre, titre, texte = sections[k]
                    sc = 4 * len(rx.findall(titre)) + len(rx.findall(texte))
                    if sc:
                        score_p[page] += sc
                        if sc > meilleure.get(page, (0, ''))[0]:
                            meilleure[page] = (sc, ancre)
            # la page qui porte le nom dans son titre passe devant les autres, avec un lien vers son haut (même si son texte
            # est surtout dans ses données : frises, cartes)
            titrees = {p for p in pages if p not in EXCLUES and rx and rx.search(noms_canon.get(p, ''))}
            for p in titrees:
                meilleure[p] = (10 ** 6, '')
            rangs = sorted(set(score_p) | titrees, key=lambda p: (p not in titrees, -score_p[p], ordre_pages.index(p)))
            choix = [p for p in rangs if p in titrees or score_p[p] >= 2][:MAX_PAGES]
            e['atlas'] = [[p + ('#' + meilleure[p][1] if meilleure[p][1] else ''), pages[p]] for p in choix]
        if 'glossaire_fixe' in e:
            g = e['glossaire_fixe']
        else:
            g = next((gl_formes[f] for f in [e['nom']] + e.get('aussi', []) if f in gl_formes and e['nom'] not in homonymes), None)
        if g:
            e['glossaire'] = g
        else:
            e.pop('glossaire', None)
    ecrire_json(chemin, d)
    n_at = sum(1 for e in d['noms'] if e['atlas'])
    n_gl = sum(1 for e in d['noms'] if e.get('glossaire'))
    print(f'atlas : {n_at} noms reliés à au moins une page ; glossaire : {n_gl} noms reliés ; index lu : {rj}')


# ── verifie ─────────────────────────────────────────────────────────────────────────────────────────
def ancres_de(fichier_source):
    p = ICI / fichier_source
    if not p.exists():
        return None
    return set(re.findall(r'\sid="([^"]+)"', p.read_text(encoding='utf-8')))


def cmd_verifie(chemin):
    d = charger(chemin)
    noms = d['noms']
    ecarts, avis = [], []
    pages = {n: f for f, n, _, _ in pages_du_site()}
    pages['index-des-noms.html'] = 'index-des-noms.html'
    gl_ids = {t['id'] for t in json.loads((ICI / 'glossaire-atlas.json').read_text(encoding='utf-8'))['termes']}
    ids = collections.Counter(ident_de(e) for e in noms)
    for i, c in ids.items():
        if c > 1:
            ecarts.append(f'identifiant en double : {i}')
    vedettes = {(e['nom'], e.get('precision', '')) for e in noms}
    par_nom = collections.defaultdict(list)
    for e in noms:
        par_nom[e['nom']].append(e)
    ancres_cache = {}
    for e in noms:
        i = ident_de(e)
        for champ in ('nom', 'cat', 'formes', 'ident', 'refs'):
            if not e.get(champ):
                ecarts.append(f'{i} : champ « {champ} » manquant')
        if e.get('cat') not in CATS:
            ecarts.append(f'{i} : catégorie inconnue « {e.get("cat")} »')
        if e.get('compte', 'exact') not in ('exact', 'min', 'env'):
            ecarts.append(f'{i} : compte inconnu « {e.get("compte")} »')
        if len(par_nom[e['nom']]) > 1 and not e.get('precision'):
            ecarts.append(f'{i} : homonyme sans précision')
        refs = e.get('refs', [])
        if not 1 <= len(refs) <= 3:
            ecarts.append(f'{i} : {len(refs)} références (1 à 3 attendues)')
        if len(set(refs)) != len(refs):
            ecarts.append(f'{i} : référence répétée')
        for r in refs:
            if not RX_REF.match(r):
                ecarts.append(f'{i} : référence mal formée « {r} »')
        for champ in ('nom', 'precision', 'ident'):
            v = e.get(champ, '')
            if re.search(r'[«»“”"]', v):
                ecarts.append(f'{i} : guillemets dans « {champ} » (aucune citation dans cette page)')
            if '\u202f' in v or '\u00a0' in v:
                ecarts.append(f'{i} : espace insécable dans « {champ} » (la typographie est ajoutée à la génération)')
            if "'" in v:
                avis.append(f'{i} : apostrophe droite dans « {champ} »')
        if e.get('ident', '').rstrip().endswith('.'):
            avis.append(f'{i} : point final dans l’identification')
        if len(e.get('ident', '').split()) > 24:
            avis.append(f'{i} : identification longue ({len(e["ident"].split())} mots)')
        for v in e.get('voir', []):
            m = re.fullmatch(r'(.+?)(?: \((.+)\))?', v)
            if (m.group(1), m.group(2) or '') not in vedettes:
                ecarts.append(f'{i} : renvoi vers un nom absent de l’index (« {v} »)')
        for href, titre in e.get('atlas', []):
            page, _, ancre = href.partition('#')
            if page not in pages:
                ecarts.append(f'{i} : lien de l’atlas vers une page inconnue ({href})')
                continue
            if not titre:
                ecarts.append(f'{i} : lien de l’atlas sans titre ({href})')
            if ancre:
                src = pages[page]
                if src not in ancres_cache:
                    ancres_cache[src] = ancres_de(src if src != 'urantia-paradis-3d.html' else 'urantia-paradis-3d.src.html')
                a = ancres_cache[src]
                if a is not None and ancre not in a and page != 'atlas-3d.html':
                    ecarts.append(f'{i} : ancre absente de la page ({href})')
        g = e.get('glossaire')
        if g and g not in gl_ids:
            ecarts.append(f'{i} : terme du glossaire inconnu ({g})')
    L = livre()
    n_refs = n_nb = 0
    if L is not None:
        C = Compteur(L)
        for e in noms:
            i = ident_de(e)
            rx = rx_formes(e.get('formes', []))
            for r in e.get('refs', []):
                n_refs += 1
                p = C.para(r)
                if p is None:
                    ecarts.append(f'{i} : référence introuvable dans le texte ({r})')
                elif rx is None or not rx.search(p['plat']):
                    ecarts.append(f'{i} : la référence {r} ne contient aucune forme du nom')
            for a in e.get('aussi', []):           # les autres noms doivent être ceux du livre
                if not C.paras_de([a]):
                    avis.append(f'{i} : autre nom absent du texte (« {a} »)')
            n = len(C.paras_de(e.get('formes', [])))
            n_nb += 1
            if n == 0:
                ecarts.append(f'{i} : aucune occurrence des formes')
            if e.get('n') != n:
                ecarts.append(f'{i} : nombre de paragraphes {e.get("n")} au lieu de {n} (relancer « compte »)')
    else:
        avis.append('texte du livre absent : références et nombres non contrôlés (copie de travail de l’auteur seulement)')
    comptes = collections.Counter(e.get('cat') for e in noms)
    print(f'{len(noms)} noms · ' + ' · '.join(f'{CATS[k][0]} {comptes[k]}' for k in CATS if comptes[k])
          + f' · {n_refs} références et {n_nb} nombres contrôlés dans le texte')
    for a in avis:
        print('avis :', a)
    for x in ecarts:
        print('ÉCART :', x)
    print('écarts :', len(ecarts))
    return len(ecarts)


# ── page ────────────────────────────────────────────────────────────────────────────────────────────
def lettre(e):
    return plier(e.get('tri') or e['nom'])[:1].upper()


def cle_tri(e):
    """Ordre alphabétique sans accents ; « tri » (facultatif) remplace le nom pour le classement (1-2-3 le premier → U)."""
    return (plier(e.get('tri') or e['nom']), plier(e.get('precision', '')), e['nom'])


def texte_compte(e):
    n, c = e.get('n', 0), e.get('compte', 'exact')
    mot = 'paragraphe' if n == 1 else 'paragraphes'
    pre = {'min': 'au moins' + NB, 'env': 'environ' + NB}.get(c, '')
    return f'{pre}{nombre(n)}{NB}{mot}'


def entree(e, par_vedette):
    # data-recherche="non" : la recherche du site n’indexe que le nom, l’identification, les autres noms et les références
    i = ident_de(e)
    vus = plier(' '.join([e['nom'], e.get('precision', '')] + e.get('aussi', [])))
    sup = [plier(f) for f, _ in analyser_formes(e['formes'])]
    k = ' '.join(dict.fromkeys(x for x in sup if x and not re.search(r'(?:^| )' + re.escape(x) + r'(?: |$)', vus)))
    h = [f'<li class="nom" id="{i}" data-c="{e["cat"]}"' + (f' data-k="{attr(k)}"' if k else '') + '>']
    prec = f' <span class="n-prec">({typo(e["precision"])})</span>' if e.get('precision') else ''
    h.append(f'<h4>{typo(e["nom"])}{prec}</h4><p class="n-cat" data-recherche="non">{typo(CATS[e["cat"]][1])}</p>')
    h.append(f'<p class="n-id">{typo(e["ident"])}</p>')
    if e.get('aussi'):
        h.append(f'<p class="n-aussi">Aussi{NB}: <span class="v">' + ', '.join(typo(a) for a in e['aussi']) + '</span></p>')
    h.append('<p class="n-ou"><span class="lbl" data-recherche="non">Où lire</span> ' + ' '.join(f'<span class="ref">{r}</span>' for r in e['refs'])
             + f' <span class="n-n" data-recherche="non">{texte_compte(e)}</span></p>')
    liens = [f'<a href="{attr(href)}">{typo(titre)}</a>' for href, titre in e.get('atlas', [])]
    if e.get('glossaire'):
        liens.append(f'<a class="n-gl" href="glossaire.html#{attr(e["glossaire"])}">Glossaire</a>')
    voir = []
    for v in e.get('voir', []):
        m = re.fullmatch(r'(.+?)(?: \((.+)\))?', v)
        cible = par_vedette.get((m.group(1), m.group(2) or ''))
        if cible:
            voir.append(f'<a href="#{ident_de(cible)}">{typo(v)}</a>')
    if liens or voir:
        h.append('<p class="n-liens" data-recherche="non">'
                 + (f'<span class="lbl">Dans l’atlas</span> ' + ' '.join(liens) if liens else '')
                 + ((' ' if liens else '') + f'<span class="n-voir">Voir aussi{NB}: ' + ', '.join(voir) + '</span>' if voir else '')
                 + '</p>')
    h.append('</li>')
    return ''.join(h)


def cmd_page(chemin_json, chemin_page):
    d = charger(chemin_json)
    noms = sorted(d['noms'], key=cle_tri)
    par_vedette = {(e['nom'], e.get('precision', '')): e for e in noms}
    groupes = collections.OrderedDict()
    for e in noms:
        groupes.setdefault(lettre(e), []).append(e)
    blocs = []
    for Lt, es in groupes.items():
        l = Lt.lower()
        blocs.append(f'<section class="lettre" id="lettre-{l}" aria-labelledby="h-{l}" style="--n:{len(es)}">\n'
                     f'<div class="l-tete"><h3 id="h-{l}">{Lt}</h3><a class="l-haut" href="#outils">Recherche</a></div>\n'
                     f'<ul class="noms">\n' + '\n'.join(entree(e, par_vedette) for e in es) + '\n</ul>\n</section>')
    liste = '\n'.join(blocs)
    az = ''.join(f'<a href="#lettre-{L.lower()}" data-l="{L}">{L}</a>' if L in groupes else f'<span aria-hidden="true">{L}</span>'
                 for L in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    comptes = collections.Counter(e['cat'] for e in noms)
    cats = (f'<button type="button" data-cat="tous" aria-pressed="true">Tout <span class="cnt">{nombre(len(noms))}</span></button>'
            + ''.join(f'<button type="button" data-cat="{k}" aria-pressed="false"><span class="pt" aria-hidden="true"></span>'
                      f'<span class="cl">{typo(v[0])}</span><span class="cc" aria-hidden="true">{typo(v[2])}</span> '
                      f'<span class="cnt">{nombre(comptes[k])}</span></button>'
                      for k, v in CATS.items() if comptes[k]))
    h = Path(chemin_page).read_text(encoding='utf-8')
    rx = re.compile(r'<!--NOMS:DEBUT[^>]*-->.*?<!--NOMS:FIN-->', re.S)
    if not rx.search(h):
        sys.exit(f'marqueurs <!--NOMS:DEBUT--> et <!--NOMS:FIN--> introuvables dans {chemin_page}')
    h = rx.sub(lambda m: f'<!--NOMS:DEBUT empreinte={empreinte(chemin_json)}-->\n{liste}\n<!--NOMS:FIN-->', h)
    h = re.sub(r'<!--AZ:DEBUT-->.*?<!--AZ:FIN-->', lambda m: f'<!--AZ:DEBUT-->{az}<!--AZ:FIN-->', h, flags=re.S)
    h = re.sub(r'<!--CATS:DEBUT-->.*?<!--CATS:FIN-->', lambda m: f'<!--CATS:DEBUT-->{cats}<!--CATS:FIN-->', h, flags=re.S)
    n_refs = sum(len(e['refs']) for e in noms)
    mois = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'aout', 'septembre', 'octobre', 'novembre', 'décembre']
    m = re.fullmatch(r'(\d{4})-(\d{2})-(\d{2})', d.get('date', ''))
    date = f'{int(m.group(3))}{NB}{mois[int(m.group(2)) - 1]}{NB}{m.group(1)}' if m else d.get('date', '')
    valeurs = {'total': nombre(len(noms)), 'refs': nombre(n_refs),
               'atlas': nombre(sum(1 for e in noms if e.get('atlas'))), 'date': date}
    for cle, v in valeurs.items():
        h = re.sub(r'(<span data-noms-' + cle + r'>)[^<]*(</span>)', lambda m: m.group(1) + v + m.group(2), h)
    h = h.replace('\r\n', '\n').replace('\n', '\r\n')
    if '\u202f' in h:
        sys.exit('espace fine U+202F dans la page : à remplacer par &nbsp;')
    Path(chemin_page).write_bytes(h.encode('utf-8'))
    print(f'page écrite : {chemin_page} ({len(noms)} noms, {len(groupes)} lettres, {n_refs} références)')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    a = sys.argv[1:]
    if len(a) >= 2 and a[0] == 'compte':
        cmd_compte(a[1])
    elif len(a) >= 2 and a[0] == 'atlas':
        cmd_atlas(a[1], a[2] if len(a) > 2 else None)
    elif len(a) >= 2 and a[0] == 'verifie':
        sys.exit(1 if cmd_verifie(a[1]) else 0)
    elif len(a) >= 3 and a[0] == 'page':
        cmd_page(a[1], a[2])
    else:
        sys.exit(__doc__)
