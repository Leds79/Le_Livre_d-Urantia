"""Glossaire de l’atlas : contrôle des données (glossaire-atlas.json) et liste des termes de la page « Glossaire ».

Usage :
  python -I glossaire.py verifie glossaire-atlas.json [--livre <UF-FRE-001-1960-3.5.md>]
      contrôle la structure (identifiants, formes en double, renvois, thèmes, liens de l’atlas) puis, si le texte du
      livre est disponible (copie de travail de l’auteur : outils/ub.py et le fichier source), chaque référence, chaque
      citation (morceaux séparés par « […] », dans l’ordre) et chaque fragment cité entre « » dans les définitions.
      Code de sortie 1 s’il reste un écart.
  python -I glossaire.py page glossaire-atlas.json glossaire.html [artefacts.json]
      écrit dans glossaire.html, entre les marqueurs <!--GLOSSAIRE:DEBUT …--> et <!--GLOSSAIRE:FIN-->, la liste des termes
      de A à Z (définition, citation, références, liens), ainsi que l’index des lettres, les thèmes et le nombre de termes.
      Les liens vers l’atlas pointent vers les pages publiées sur claude.ai (artefacts.json) ou, à défaut, vers le site ;
      construire_site.py les rend relatifs. L’empreinte des données, inscrite dans le marqueur, est contrôlée à la
      construction : si glossaire-atlas.json change, relancer cette commande.
"""
import ast
import hashlib
import html
import importlib.util
import json
import re
import sys
import unicodedata
from pathlib import Path

ICI = Path(__file__).resolve().parent
BASE = 'https://leds79.github.io/Le_Livre_d-Urantia/'
THEMES = {   # ordre d’affichage des filtres
    'deite': 'Dieu et la Déité',
    'univers': 'L’univers',
    'etres': 'Les êtres de l’univers',
    'humain': 'L’être humain',
    'histoire': 'L’histoire d’Urantia',
    'jesus': 'Jésus et la Bible',
}
RX_REF = re.compile(r'^(\d{1,3}):(\d{1,2})\.(\d{1,3})(?:[-–](\d{1,3}))?$')
NBSP, NNBSP = ' ', ' '


# ── Outils de texte ─────────────────────────────────────────────────────────────────────────────────
def plier(s):
    """Minuscules sans accents (recherche) : même règle que le script de la page."""
    s = unicodedata.normalize('NFD', str(s))
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn').lower()
    s = s.replace('œ', 'oe').replace('æ', 'ae')
    s = re.sub('[’‘ʼ]', "'", s)
    return re.sub(r'\s+', ' ', s).strip()


def cle_forme(s):
    return re.sub(r'[\s  ]+', ' ', s).replace("'", '’').strip()


def typo(s):
    """Typographie française (comme construire_site.py) : insécable devant « : », fine devant ; ! ?, et dans « »."""
    s = re.sub(r'[  ](?=:(?:[\s ]|$))', NBSP, s)
    s = re.sub(r' (?=[;!?])', NNBSP, s)
    s = re.sub(r'«[  ]?', '«' + NBSP, s)
    s = re.sub(r'[  ]?»', NBSP + '»', s)
    return s


def e(s):
    return html.escape(typo(s), quote=False)


def attr(s):
    return html.escape(s, quote=True)


def charger(chemin):
    d = json.loads(Path(chemin).read_text(encoding='utf-8'))
    return d['termes'] if isinstance(d, dict) else d


def empreinte(chemin):
    return hashlib.sha256(Path(chemin).read_bytes().replace(b'\r\n', b'\n')).hexdigest()[:12]


def pages_du_site():
    """(fichier source, nom dans le site) de chaque page, lus dans la liste PAGES de construire_site.py."""
    src = (ICI / 'construire_site.py').read_text(encoding='utf-8')
    for noeud in ast.parse(src).body:
        if isinstance(noeud, ast.Assign) and any(getattr(t, 'id', '') == 'PAGES' for t in noeud.targets):
            return [(p[0], p[1]) for p in ast.literal_eval(noeud.value)]
    return []


# ── Contrôle ────────────────────────────────────────────────────────────────────────────────────────
def verifie(chemin, livre=None):
    termes = charger(chemin)
    ecarts, avis = [], []
    ids = [t.get('id') for t in termes]
    connus = set(ids)
    noms = {n for _, n in pages_du_site()} | {'glossaire.html'}
    for i in sorted(set(x for x in ids if ids.count(x) > 1)):
        ecarts.append(f'identifiant en double : {i}')
    vues = {}
    for t in termes:
        i = t.get('id', '?')
        for champ in ('id', 'terme', 'formes', 'anglais', 'definition', 'refs', 'theme'):
            if not t.get(champ):
                ecarts.append(f'{i} : champ « {champ} » manquant')
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', i):
            ecarts.append(f'{i} : identifiant invalide (minuscules, chiffres, tirets)')
        if t.get('theme') not in THEMES:
            ecarts.append(f'{i} : thème inconnu « {t.get("theme")} »')
        if t.get('casse', 'souple') not in ('souple', 'stricte'):
            ecarts.append(f'{i} : casse inconnue « {t.get("casse")} »')
        for f in t.get('formes', []):
            variantes = [f]
            if t.get('casse', 'souple') == 'souple' and f[:1] != f[:1].upper():
                variantes.append(f[:1].upper() + f[1:])
            for v in variantes:
                k = cle_forme(v)
                if k in vues and vues[k] != i:
                    ecarts.append(f'forme « {v} » partagée par {vues[k]} et {i}')
                vues[k] = i
        for v in t.get('voir', []):
            if v not in connus:
                ecarts.append(f'{i} : renvoi vers un terme absent ({v})')
        a = t.get('atlas')
        if a:
            page = a.get('href', '').split('#')[0]
            if page not in noms:
                ecarts.append(f'{i} : lien de l’atlas vers une page inconnue ({a.get("href")})')
            if not a.get('titre'):
                ecarts.append(f'{i} : lien de l’atlas sans titre')
        refs = t.get('refs', [])
        if not 1 <= len(refs) <= 3:
            ecarts.append(f'{i} : {len(refs)} références (1 à 3 attendues)')
        for r in refs:
            if not RX_REF.match(r):
                ecarts.append(f'{i} : référence mal formée « {r} »')
        c = t.get('citation')
        if c:
            if c.get('ref') not in refs:
                ecarts.append(f'{i} : la référence de la citation ({c.get("ref")}) n’est pas dans « refs »')
            phrases = re.findall(r'[.!?…](?:\s|$)', c.get('texte', '').replace('[…]', ''))
            if len(phrases) > 1:
                avis.append(f'{i} : citation de plus d’une phrase ?')
            if len(c.get('texte', '').split()) > 40:
                avis.append(f'{i} : citation longue ({len(c["texte"].split())} mots)')
        nmots = len(t.get('definition', '').split())
        if nmots > 60:
            avis.append(f'{i} : définition longue ({nmots} mots)')
        for champ, txt in (('definition', t.get('definition', '')), ('terme', t.get('terme', ''))):
            if NBSP in txt or NNBSP in txt:
                avis.append(f'{i} : espace insécable dans « {champ} » (la typographie est ajoutée à la construction)')
    brut = json.loads(Path(chemin).read_text(encoding='utf-8'))
    for x in (brut.get('exclusions', []) if isinstance(brut, dict) else []):
        if not isinstance(x, str) or not x.strip():
            ecarts.append(f'exclusion invalide : {x!r}')
        elif cle_forme(x) in vues:
            ecarts.append(f'exclusion « {x} » identique à une forme de {vues[cle_forme(x)]}')

    # le texte du livre : copie de travail de l’auteur seulement
    ub_py = ICI.parents[2] / 'outils' / 'ub.py'
    if livre is None and ub_py.exists():
        livre = ub_py.parent.parent / 'UF-FRE-001-1960-3.5.md'
    n_refs = n_cit = n_frag = 0
    if livre and Path(livre).exists() and ub_py.exists():
        spec = importlib.util.spec_from_file_location('ub', ub_py)
        ub = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ub)
        L = ub.Livre(str(livre))

        def para(r):
            m = RX_REF.match(r)
            if not m:
                return None
            f, s, p, fin = m.groups()
            debut = (int(f), int(s), int(p))
            if debut not in L.index:
                return None
            textes = [L.paras[L.index[debut]]['plat']]
            if fin:
                k = (int(f), int(s), int(fin))
                if k not in L.index or L.index[k] < L.index[debut]:
                    return None
                textes = [x['plat'] for x in L.paras[L.index[debut]:L.index[k] + 1]]
            return ' '.join(textes)

        def norm(s):
            return re.sub(r'\s+', ' ', s.replace(NBSP, ' ').replace(NNBSP, ' ').replace("'", '’')).strip()

        def trouve(texte, cible):
            pos = 0
            for morceau in [m.strip() for m in texte.split('[…]') if m.strip()]:
                k = cible.find(norm(morceau), pos)
                if k < 0:
                    return False
                pos = k + len(norm(morceau))
            return True

        for t in termes:
            i = t.get('id', '?')
            textes = {}
            for r in t.get('refs', []):
                p = para(r)
                n_refs += 1
                if p is None:
                    ecarts.append(f'{i} : référence introuvable dans le texte « {r} »')
                else:
                    textes[r] = norm(p)
            c = t.get('citation')
            if c and c.get('ref') in textes:
                n_cit += 1
                if not trouve(c.get('texte', ''), textes[c['ref']]):
                    ecarts.append(f'{i} : citation inexacte en {c["ref"]} : « {c.get("texte", "")[:90]}… »')
            tout = ' '.join(textes.values())
            for frag in re.findall(r'«\s*([^«»]+?)\s*»', t.get('definition', '')):
                n_frag += 1
                if not trouve(frag, tout):
                    ecarts.append(f'{i} : fragment cité absent des références : « {frag} »')
            # « dans nos mots » : pas de longue suite de mots reprise telle quelle hors guillemets
            libre = plier(re.sub(r'«[^«»]*»', ' | ', t.get('definition', '')))
            source = plier(tout)
            mots = re.findall(r"[\w’']+|\|", libre)
            for k in range(len(mots) - 7):
                fenetre = mots[k:k + 8]
                if '|' not in fenetre and ' '.join(fenetre) in source:
                    avis.append(f'{i} : définition proche du texte (« {" ".join(fenetre)} »)')
                    break
    else:
        avis.append('texte du livre absent : références et citations non contrôlées (copie de travail de l’auteur seulement)')

    print(f'{len(termes)} termes · {n_refs} références · {n_cit} citations · {n_frag} fragments dans les définitions')
    for a in avis:
        print('avis :', a)
    for x in ecarts:
        print('ÉCART :', x)
    print('écarts :', len(ecarts))
    return len(ecarts)


# ── Page « Glossaire » ──────────────────────────────────────────────────────────────────────────────
def lettre(t):
    return plier(t['terme'])[:1].upper()


def lien_atlas(href, artefacts, site2src):
    page, _, ancre = href.partition('#')
    src = site2src.get(page)
    if src and src in artefacts:
        return artefacts[src] + ('#' + ancre if ancre else '')
    return BASE + href


def entree(t, termes, artefacts, site2src):
    i = t['id']
    # recherche : le script de la page lit la vedette, l’anglais, les autres noms et la définition ; data-f ajoute les formes
    vus = plier(' '.join([t['terme']] + t.get('autres', [])))
    f = ' '.join(dict.fromkeys(x for x in (plier(x) for x in t['formes']) if x not in vus))
    h = [f'<article class="terme" id="{i}" data-theme="{t["theme"]}"' + (f' data-f="{attr(f)}"' if f else '') + '>']
    h.append('<div class="t-tete">')
    h.append(f'<h4><dfn>{e(t["terme"])}</dfn></h4>')
    if t.get('anglais'):
        h.append(f'<p class="t-en"><span class="vh">En anglais{NBSP}: </span><i lang="en">{html.escape(t["anglais"])}</i></p>')
    h.append(f'<p class="t-theme">{e(THEMES[t["theme"]])}</p>')
    h.append('</div>')
    h.append('<div class="t-corps">')
    if t.get('autres'):
        h.append(f'<p class="t-autres">Aussi{NBSP}: ' + ', '.join(e(x) for x in t['autres']) + '</p>')
    h.append(f'<p class="t-def">{e(t["definition"])}</p>')
    c = t.get('citation')
    if c:
        h.append(f'<figure class="t-cit"><blockquote><p>«{NBSP}{e(c["texte"])}{NBSP}»</p></blockquote>'
                 f'<figcaption class="ref">{c["ref"]}</figcaption></figure>')
    autres_refs = [r for r in t['refs'] if not c or r != c['ref']]
    if autres_refs:
        h.append(f'<p class="t-ou"><span class="lbl">{"Où lire aussi" if c else "Où lire"}</span> '
                 + ' '.join(f'<span class="ref">{r}</span>' for r in autres_refs) + '</p>')
    liens = []
    a = t.get('atlas')
    if a:
        liens.append(f'<a class="t-atlas" href="{attr(lien_atlas(a["href"], artefacts, site2src))}" target="_blank" rel="noopener">'
                     f'Voir dans l’atlas{NBSP}: {e(a["titre"])}</a>')
    voir = [x for x in t.get('voir', []) if x in termes]
    if voir:
        liens.append('<span class="t-voir">Voir aussi' + NBSP + ': '
                     + ', '.join(f'<a href="#{x}">{e(termes[x]["terme"])}</a>' for x in voir) + '</span>')
    if liens:
        h.append('<p class="t-liens">' + ' '.join(liens) + '</p>')
    h.append('</div>')
    h.append('</article>')
    return '\n'.join(h)


def page(chemin_json, chemin_page, chemin_artefacts=None):
    termes_l = charger(chemin_json)
    termes = {t['id']: t for t in termes_l}
    artefacts = {}
    if chemin_artefacts and Path(chemin_artefacts).exists():
        artefacts = {k: v for k, v in json.loads(Path(chemin_artefacts).read_text(encoding='utf-8')).items() if not k.startswith('_')}
    site2src = {n: f for f, n in pages_du_site()}
    tries = sorted(termes_l, key=lambda t: (plier(t['terme']), t['terme']))
    groupes = {}
    for t in tries:
        groupes.setdefault(lettre(t), []).append(t)
    blocs = []
    for L, ts in groupes.items():
        blocs.append(f'<section class="lettre" id="lettre-{L.lower()}" aria-labelledby="h-{L.lower()}">\n'
                     f'<h3 id="h-{L.lower()}">{L}</h3>\n<div class="termes">\n'
                     + '\n'.join(entree(t, termes, artefacts, site2src) for t in ts) + '\n</div>\n</section>')
    liste = '\n'.join(blocs)
    az = ''.join(f'<a href="#lettre-{L.lower()}" data-l="{L}">{L}</a>' if L in groupes else f'<span aria-hidden="true">{L}</span>'
                 for L in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    comptes = {k: sum(1 for t in termes_l if t['theme'] == k) for k in THEMES}
    themes = (f'<button type="button" data-th="tous" aria-pressed="true">Tout <span class="cnt">{len(termes_l)}</span></button>'
              + ''.join(f'<button type="button" data-th="{k}" aria-pressed="false">{e(v)} <span class="cnt">{comptes[k]}</span></button>'
                        for k, v in THEMES.items() if comptes[k]))
    h = Path(chemin_page).read_text(encoding='utf-8')
    rx = re.compile(r'<!--GLOSSAIRE:DEBUT[^>]*-->.*?<!--GLOSSAIRE:FIN-->', re.S)
    if not rx.search(h):
        sys.exit(f'marqueurs <!--GLOSSAIRE:DEBUT--> et <!--GLOSSAIRE:FIN--> introuvables dans {chemin_page}')
    h = rx.sub(lambda m: f'<!--GLOSSAIRE:DEBUT empreinte={empreinte(chemin_json)}-->\n{liste}\n<!--GLOSSAIRE:FIN-->', h)
    h = re.sub(r'<!--AZ:DEBUT-->.*?<!--AZ:FIN-->', lambda m: f'<!--AZ:DEBUT-->{az}<!--AZ:FIN-->', h, flags=re.S)
    h = re.sub(r'<!--THEMES:DEBUT-->.*?<!--THEMES:FIN-->', lambda m: f'<!--THEMES:DEBUT-->{themes}<!--THEMES:FIN-->', h, flags=re.S)
    h = re.sub(r'(<span data-gl-nombre>)\d*(</span>)', lambda m: f'{m.group(1)}{len(termes_l)}{m.group(2)}', h)
    n_cit = sum(1 for t in termes_l if t.get('citation'))
    h = re.sub(r'(<span data-gl-citations>)\d*(</span>)', lambda m: f'{m.group(1)}{n_cit}{m.group(2)}', h)
    Path(chemin_page).write_text(h, encoding='utf-8', newline='\n')
    print(f'page écrite : {chemin_page} ({len(termes_l)} termes, {len(groupes)} lettres, {n_cit} citations)')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    a = sys.argv[1:]
    if len(a) >= 2 and a[0] == 'verifie':
        livre = a[a.index('--livre') + 1] if '--livre' in a else None
        sys.exit(1 if verifie(a[1], livre) else 0)
    elif len(a) >= 3 and a[0] == 'page':
        page(a[1], a[2], a[3] if len(a) > 3 else None)
    else:
        sys.exit(__doc__)
