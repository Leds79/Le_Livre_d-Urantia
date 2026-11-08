"""Construit le site statique « Le Livre d'Urantia en images » à partir des pages publiées.

Chaque page reçoit un squelette HTML complet (métadonnées de partage, lien « Aller au contenu », barre de
navigation commune, parcours de découverte), une passe de typographie française, des liens relatifs qui
s'ouvrent dans le même onglet et des ressources locales (assets/) : le site s'ouvre hors ligne (index.html)
et se publie tel quel sur GitHub Pages. Les sources sont copiées dans sources/, sans les adresses claude.ai.
Le site est aussi une application web installable (PWA) : manifest.webmanifest, sw.js (service worker écrit à
chaque construction, VERSION = empreinte du contenu), hors-ligne.html, assets/hors-ligne.js et, sur l'accueil,
l'encadré « Lire hors ligne ». Chaque page porte le crédit de l'auteur et le lien du dépôt GitHub. Le glossaire
(glossaire.html, glossaire-atlas.json) a sa page, dans le menu « Outils », et ses infobulles dans les pages 2D
(assets/glossaire.js, avec les données injectées à la construction) ; le quiz (assets/quiz.js, quiz-atlas.json)
suit les étapes du parcours.
La barre commune regroupe les pages en menus (Accueil · Parcours · Thèmes · Le livre · Outils), avec à droite
Rechercher, Écouter et la musique ; sous 1 000 px, une barre compacte ouvre un tiroir (assets/navigation.js).
La recherche lit un index écrit à chaque construction (assets/recherche.js) ; « Écouter » lit la page à voix
haute (assets/ecouter.js, synthèse vocale du navigateur).

Usage : python -I construire_site.py <dossier source de l'atlas> <dossier du site>
Le dossier source contient les pages publiées, polices/ (fonts.css, fichiers WOFF2, OFL), site/ (README,
LICENCES, LICENSE, favicon, aperçu…), refs-urantia.js et, hors publication, artefacts.json (adresses des
pages publiées sur claude.ai) ; ../lib contient Three.js et sa licence. Détail : sources/CONSTRUIRE.md."""
import hashlib
import html as html_lib
import json
import re
import shutil
import struct
import subprocess
import sys
import urllib.parse
from html.parser import HTMLParser
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
# Une ligne par page : (fichier source, nom dans le site, nom canonique, nom court, description pour le partage).
# Le nom canonique sert au titre d'onglet, aux menus, au parcours et à la recherche ; le nom court, à la barre compacte
# du téléphone. Une page dont la source n'existe pas (encore) est ignorée avec un avertissement, sans faire échouer la
# construction : absente des menus, de la recherche et du service worker, et les liens qui la visent restent du texte
# simple jusqu'à son arrivée. Pour ajouter une page : une ligne ici, sa place dans PARCOURS ou dans MENUS (plus bas),
# et son adresse claude.ai dans artefacts.json si elle y est publiée.
PAGES = [
    ('accueil.html', 'index.html', 'Accueil', 'Accueil',
     'Atlas visuel du Livre d’Urantia : notre adresse dans l’univers, la vue 3D d’Urantia au Paradis, la frise du temps, la carrière ascendante, les êtres de l’univers et les concepts, avec les références du texte.'),
    ('nebadon-orvonton.html', 'nebadon-dans-orvonton.html', 'Nébadon dans Orvonton', 'Nébadon dans Orvonton',
     'Schéma : la place de Nébadon dans le superunivers d’Orvonton, et celle de la Voie lactée.'),
    ('urantia-paradis-3d.html', 'atlas-3d.html', 'D’Urantia au Paradis (3D)', 'La 3D',
     'Vue 3D : d’Urantia au Paradis, les sept superunivers, Havona, la frise du temps de Satania et d’Urantia, la carrière ascendante.'),
    ('familles-de-personnalites.html', 'familles-de-personnalites.html', 'Familles de personnalités', 'Familles de personnalités',
     'Les familles de personnalités selon le Livre d’Urantia : classifications d’Uversa et du Paradis, en arbre interactif.'),
    ('concepts.html', 'concepts-en-schemas.html', 'Concepts en schémas', 'Concepts en schémas',
     'Sept schémas : personnalité, mental, Ajusteur, âme, adjuvats, cercles psychiques, niveaux de réalité et morontia.'),
    ('dieu-et-deite.html', 'dieu-et-deite.html', 'Dieu et la Déité', 'Dieu et la Déité',
     'Dieu et la Déité selon le Livre d’Urantia : le JE SUIS, les sept Absolus, la Trinité, les Maitres Esprits, les Déités expérientielles.'),
    ('destinee-humaine.html', 'destinee-humaine.html', 'La destinée humaine', 'La destinée humaine',
     'Que devient-on à la mort, selon le livre ? L’Ajusteur de Pensée, l’âme, la personnalité, le réveil sur les mondes des maisons et la fusion, en un schéma de sept étapes.'),
    ('histoire-d-urantia.html', 'histoire-d-urantia.html', 'L’histoire d’Urantia', 'L’histoire d’Urantia',
     'L’histoire d’Urantia selon le livre : formation de la planète, ères de la vie, apparition et dispersion des races, sur une carte du monde.'),
    ('rebellion-de-lucifer.html', 'rebellion-de-lucifer.html', 'La rébellion de Lucifer', 'La rébellion de Lucifer',
     'La rébellion de Lucifer selon le Livre d’Urantia : les trois échelles (Jérusem, Dalamatia, le Jardin), pourquoi Urantia est une planète isolée, le manifeste, les loyaux et les rebelles.'),
    ('vie-de-jesus.html', 'vie-de-jesus.html', 'La vie de Jésus', 'La vie de Jésus',
     'La vie de Jésus selon la quatrième partie du livre : une frise de 92 étapes, de l’annonce à Marie à la Pentecôte, et les cartes de ses voyages.'),
    ('bible-et-livre.html', 'bible-et-livre.html', 'La Bible et le Livre d’Urantia', 'La Bible et le livre',
     'Cent parallèles entre la Bible (Crampon 1923) et le Livre d’Urantia, de la Création à l’Apocalypse : ce qui concorde, ce qui diffère, et ce que le livre en dit.'),
    ('pere-fils-esprit.html', 'pere-fils-esprit.html', 'Le Père, le Fils et l’Esprit', 'Père, Fils et Esprit',
     'Le Père, le Fils et l’Esprit selon le Livre d’Urantia : le Père Universel, le Fils Éternel et l’Esprit Infini, les trois personnes de la Déité, avec les références du texte.'),
    ('paradis-et-havona.html', 'paradis-et-havona.html', 'Le Paradis et Havona', 'Le Paradis et Havona',
     'Le Paradis et Havona selon le Livre d’Urantia : l’ile éternelle au centre de tout et l’univers parfait d’un milliard de mondes qui l’entoure, en schémas.'),
    ('etre-supreme.html', 'etre-supreme.html', 'L’Être Suprême', 'L’Être Suprême',
     'L’Être Suprême selon le Livre d’Urantia : un Dieu qui évolue, qui tient sa personne de la Trinité et grandit avec l’expérience des créateurs et des créatures, en schémas, avec ce que le texte laisse ouvert.'),
    ('effusions-de-micael.html', 'effusions-de-micael.html', 'Les sept effusions de Micaël', 'Les effusions de Micaël',
     'Les sept effusions de Micaël selon le Livre d’Urantia : sept fois la vie de ses propres créatures, de Melchizédek à Jésus sur Urantia, et ce qu’elles ont changé, avec les références du texte.'),
    ('jerusem-et-edentia.html', 'jerusem-et-edentia.html', 'Jérusem, Édentia et les mondes des maisons', 'Jérusem et Édentia',
     'Jérusem, Édentia et les mondes des maisons selon le Livre d’Urantia : les premiers lieux qu’il décrit après la mort, la capitale du système et ses mondes des maisons, puis la capitale de la constellation, en cartes et en schémas.'),
    ('les-anges.html', 'les-anges.html', 'Les anges', 'Les anges',
     'Les anges selon le Livre d’Urantia : qui ils sont, leur vie, les chérubins, les sept ordres de séraphins et l’ange gardien, avec les références du texte.'),
    ('avenir-d-une-planete.html', 'avenir-d-une-planete.html', 'L’avenir d’une planète', 'L’avenir d’une planète',
     'L’avenir d’une planète selon le Livre d’Urantia : les âges qu’ouvrent tour à tour les Fils divins sur un monde habité, jusqu’à l’ère de lumière et de vie, et ce qui s’est passé autrement sur Urantia.'),
    ('institutions-humaines.html', 'institutions-humaines.html', 'L’évolution des institutions humaines', 'Institutions humaines',
     'L’évolution des institutions humaines selon le Livre d’Urantia : l’industrie, la propriété, l’État et le mariage, nés d’une lente évolution des coutumes, de la horde à l’État représentatif et au foyer.'),
    ('evolution-religion.html', 'evolution-religion.html', 'L’évolution de la religion', 'Évolution de la religion',
     'L’évolution de la religion selon le Livre d’Urantia : de la peur et du besoin d’adorer à la foi en un Père qui aime, en huit étapes, puis la religion vécue.'),
    ('religion-vecue.html', 'religion-vecue.html', 'La religion vécue', 'La religion vécue',
     'La religion vécue selon le Livre d’Urantia : la religion comme expérience personnelle, la foi et ce qu’elle produit dans une vie, avec les références du texte.'),
    ('melchizedek-et-religions.html', 'melchizedek-et-religions.html', 'Melchizédek et les religions du monde', 'Melchizédek et les religions',
     'Machiventa Melchizédek et les religions du monde selon le Livre d’Urantia : le sage de Salem, l’idée d’un Dieu unique portée de l’Islande au Japon et sa trace dans les grandes traditions, sur une carte et une frise.'),
    ('annees-cachees-de-jesus.html', 'annees-cachees-de-jesus.html', 'Les années cachées de Jésus', 'Les années cachées',
     'Les années cachées de Jésus selon le Livre d’Urantia : son enfance, sa jeunesse, son métier et ses voyages, jusqu’au début de son ministère public, avec les références du texte.'),
    ('douze-apotres.html', 'douze-apotres.html', 'Les douze apôtres', 'Les douze apôtres',
     'Les douze apôtres selon le Livre d’Urantia : l’âge, le métier, le rôle, les forces et les faiblesses de chacun, et ce qu’il devint après la Pentecôte.'),
    ('enseignements-de-jesus.html', 'enseignements-de-jesus.html', 'Les enseignements de Jésus', 'Enseignements de Jésus',
     'Les enseignements de Jésus selon la quatrième partie du Livre d’Urantia : quinze grands enseignements du Maitre, rangés par thème, avec ses mots, ses références et les épisodes où il les donne.'),
    ('apres-la-pentecote.html', 'apres-la-pentecote.html', 'Après la Pentecôte', 'Après la Pentecôte',
     'Après la Pentecôte selon le Livre d’Urantia : l’effusion de l’Esprit de Vérité, la diffusion du message et la naissance du christianisme, avec les références du texte.'),
    ('histoire-du-livre.html', 'histoire-du-livre.html', 'D’où vient ce livre ?', 'D’où vient ce livre ?',
     'D’où vient le Livre d’Urantia ? Ce qu’il dit de lui-même, ce que racontent ses premiers lecteurs, ce qu’en disent les critiques : chaque voix avec ses sources, sans trancher.'),
    ('auteurs-et-chiffres.html', 'auteurs-et-chiffres.html', 'Les auteurs déclarés et le livre en chiffres', 'Auteurs et chiffres',
     'Les auteurs déclarés du Livre d’Urantia, fascicule par fascicule, puis le livre mesuré : ses parties, ses longueurs, ses mots.'),
    ('science-et-histoire.html', 'science-et-histoire.html', 'La science et l’histoire face au livre', 'Science et histoire',
     'Le Livre d’Urantia face à la science et à l’histoire : ses affirmations confrontées aux connaissances actuelles, avec les références du texte.'),
    ('fascicules.html', 'fascicules.html', 'Le livre fascicule par fascicule', 'Fascicule par fascicule',
     'Le Livre d’Urantia fascicule par fascicule : pour chacun des 197 fascicules, l’auteur que le texte lui donne, le temps de lecture, le lien vers son texte et les pages de l’atlas qui en parlent.'),
    ('parcours-de-lecture.html', 'parcours-de-lecture.html', 'Parcours de lecture', 'Parcours de lecture',
     'Cinq itinéraires de lecture du Livre d’Urantia, fascicule par fascicule : durée estimée, lien vers le texte, pages de l’atlas à voir en chemin, et une case « Lu » gardée sur l’appareil.'),
    ('glossaire.html', 'glossaire.html', 'Glossaire', 'Glossaire',
     'Glossaire du Livre d’Urantia : les termes du livre de A à Z, avec une définition simple, l’anglais d’origine, une courte citation et les références du texte.'),
]
# Glossaire : sa page est dans le menu « Outils », hors du parcours numéroté ; ses infobulles (assets/glossaire.js,
# données de glossaire-atlas.json injectées à la place du marqueur) sont chargées par les pages 2D.
GLOSSAIRE = 'glossaire.html'
GLOSSAIRE_JS, GLOSSAIRE_JSON, MARQUE_GLOSSAIRE = 'glossaire.js', 'glossaire-atlas.json', '/*__GLOSSAIRE__*/null'
# Quiz « Teste tes connaissances » : assets/quiz.js, avec les données de quiz-atlas.json injectées à la place du marqueur ;
# chargé par les pages du parcours de découverte (la vue 3D, étapes 2 à 5, l'ouvre depuis son menu).
QUIZ_JS, QUIZ_JSON, MARQUE_QUIZ = 'quiz.js', 'quiz-atlas.json', '/*__QUIZ__*/null'
# Scripts communs copiés dans assets/ : références, hors ligne, musique, barre et recherche, lecture à voix haute.
SCRIPTS = ['refs-urantia.js', 'hors-ligne.js', 'musique.js', 'navigation.js', 'ecouter.js']
RECHERCHE_JS = 'recherche.js'            # index de la recherche, écrit à chaque construction (assets/recherche.js)
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
    ('destinee-humaine.html', 'La destinée humaine'),
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
           'urantia-paradis-3d.src.html', 'etoiles.json', 'geo.json', 'tex.json', 'liens_refs.py'] + SCRIPTS + [
           GLOSSAIRE_JS, GLOSSAIRE_JSON, 'glossaire.py', QUIZ_JS, QUIZ_JSON, 'assembler.py', 'etoiles.py', 'geo.py',
           'textures.py', 'voie-lactee-lecture-exr.py', 'voie-lactee-conversion.py', 'polices.py', 'fascicules.py', 'smoke3d.js',
           'construire_site.py', 'CONSTRUIRE.md', 'requirements.txt']
RACINE = ['README.md', 'LICENCES.md', 'LICENSE', 'LICENSE-CONTENU.md', 'CONTRIBUER.md']   # copiés de site/ à la racine du site
GITHUB = ['.github/ISSUE_TEMPLATE/erreur.yml', '.github/ISSUE_TEMPLATE/idee.yml', '.github/ISSUE_TEMPLATE/config.yml',
          '.github/pull_request_template.md']                                           # formulaires de tickets, modèle de demande
# Crédit et dépôt (pied commun de chaque page, sauf la vue 3D qui a son menu)
AUTEUR = 'Sylvain Leduc'
DEPOT = 'https://github.com/Leds79/Le_Livre_d-Urantia'
DEPOT_LICENCES = DEPOT + '/blob/main/LICENCES.md'
# ── Menus de la barre commune ───────────────────────────────────────────────────────────────────
# Barre : Accueil, Parcours (les étapes de PARCOURS), puis les menus ci-dessous ; à droite, Rechercher, Écouter et la
# musique. Un menu : (clé, titre, nom du groupe, entrées). Le nom du groupe remplace « Étape N sur 13 » dans le bandeau
# d'une page hors parcours. Une entrée : (adresse d'une page de PAGES, aide) ou (adresse, libellé, aide) pour un autre
# lien ; un lien externe s'ouvre dans un nouvel onglet ; SIGNALER : le formulaire pré-rempli pour la page affichée.
# Une chaîne seule ouvre un sous-groupe titré (colonnes côte à côte au bureau, intertitres dans le tiroir). Une page
# absente (source pas encore là) est omise du menu, un sous-groupe vide aussi. Pas plus de quinze entrées à plat.
SIGNALER = '#signaler'
MENUS = [
    ('themes', 'Thèmes', 'Thème', [                  # trois sous-groupes : trois colonnes au bureau, intertitres dans le tiroir
        'L’univers',
        ('pere-fils-esprit.html', 'Les trois personnes de la Déité'),
        ('paradis-et-havona.html', 'L’ile centrale et l’univers parfait'),
        ('etre-supreme.html', 'Un Dieu qui grandit avec l’expérience'),
        ('jerusem-et-edentia.html', 'La capitale de Satania, les mondes des maisons et Édentia'),
        ('les-anges.html', 'Séraphins, chérubins et anges gardiens'),
        'Urantia et l’humanité',
        ('avenir-d-une-planete.html', 'Les âges d’un monde habité, et le nôtre'),
        ('institutions-humaines.html', 'D’où viennent l’industrie, la propriété, l’État et le mariage ?'),
        ('evolution-religion.html', 'De la peur à la foi, en huit étapes'),
        ('religion-vecue.html', 'La foi dans l’expérience humaine'),
        ('melchizedek-et-religions.html', 'Le sage de Salem et le Dieu unique'),
        'Micaël et Jésus',
        ('effusions-de-micael.html', 'Sept fois la vie de ses créatures'),
        ('annees-cachees-de-jesus.html', 'Enfance, jeunesse et voyages'),
        ('douze-apotres.html', 'Qui ils étaient, ce qu’ils devinrent'),
        ('enseignements-de-jesus.html', 'Quinze enseignements, rangés par thème'),
        ('apres-la-pentecote.html', 'L’Esprit de Vérité et les premiers croyants'),
    ]),
    ('livre', 'Le livre', 'Le livre', [
        ('histoire-du-livre.html', 'Son origine, ses témoins, ses critiques'),
        ('auteurs-et-chiffres.html', 'Qui présente chaque fascicule ; le livre mesuré'),
        ('science-et-histoire.html', 'Ses affirmations face aux connaissances'),
        ('bible-et-livre.html', 'Cent parallèles, de la Genèse à l’Apocalypse'),
        (LIVRE[0], 'Lire le livre sur urantia.org', 'Le texte intégral, sur le site de la Fondation Urantia'),
    ]),
    ('outils', 'Outils', 'Outil', [
        ('fascicules.html', 'Les 197 fascicules et les pages de l’atlas'),
        ('parcours-de-lecture.html', 'Cinq itinéraires, fascicule par fascicule'),
        ('glossaire.html', 'Les mots du livre, de A à Z'),
        ('index.html#hors-ligne', 'Lire hors ligne', 'Installer l’atlas ou l’enregistrer sur l’appareil'),
        (SIGNALER, 'Signaler une erreur', 'Sur cette page ; un compte GitHub est nécessaire'),
        (DEPOT + '/blob/main/CONTRIBUER.md', 'Contribuer sur GitHub', 'Proposer une correction ou une idée'),
    ]),
]
# Application installable (PWA)
NOM_COURT = 'Atlas Urantia'
THEME = {'clair': '#FFFFFF', 'sombre': '#131A2E', '3d': '#03050C', 'appli': '#0C1120'}   # barre du navigateur, écran de lancement
ICONES = [('icone-192.png', '192x192', 'any'), ('icone-512.png', '512x512', 'any'),
          ('icone-512-maskable.png', '512x512', 'maskable')]                  # rendus de favicon.svg (site/)
ACTIFS = ['favicon.svg', 'apercu.png', 'apple-touch-icon.png'] + [i[0] for i in ICONES]   # copiés de site/ dans assets/
RESET = ('<style>:root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);'
         'padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0;font:14px system-ui,sans-serif}'
         'img{max-width:100%}[hidden]{display:none!important}</style>')
# Barre commune (menus, tiroir), bandeau du parcours et pied : feuille posée dans chaque page 2D, une règle par ligne
# ici, sur une seule ligne dans la page. Comportement : assets/navigation.js (source : navigation.js).
NAV_CSS_SRC = r'''
/* barre commune, menus, tiroir, bandeau et pied de l’atlas (construire_site.py ; comportement : assets/navigation.js) */
.aller-contenu{position:absolute;left:-10000px;top:8px;z-index:1100;padding:10px 16px;border-radius:8px;background:var(--ink);color:var(--paper);font:600 1rem/1.2 var(--font-body);text-decoration:none}
.aller-contenu:focus{left:12px}
.an-sr{position:absolute!important;width:1px;height:1px;margin:-1px;padding:0;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap;border:0}
html.an-bloque,html.an-bloque body{overflow:hidden}
html.an-bloque main *,html.an-bloque main *::before,html.an-bloque main *::after{animation-play-state:paused!important}
.atlas-nav{position:relative;z-index:100;background:var(--sheet);border-bottom:1px solid var(--rule);color:var(--ink);font:500 1rem/1.25 var(--font-body)}
.an-barre{display:flex;align-items:center;gap:2px;max-width:1100px;min-height:64px;margin:0 auto;padding:0 max(16px,env(safe-area-inset-right,0px)) 0 max(16px,env(safe-area-inset-left,0px))}
.atlas-nav ul,.atlas-nav ol{list-style:none;margin:0;padding:0}
.atlas-nav li,.atlas-nav p{margin:0}
.atlas-nav a{color:inherit;text-decoration:none}
.atlas-nav svg{display:block;flex:none}
.atlas-nav :focus-visible{outline:2px solid var(--gold-ink);outline-offset:2px;border-radius:10px}
.an-ic{width:20px;height:20px}
.an-emb{width:28px;height:28px;border-radius:8px}
.an-accueil,.an-g-btn,.an-ecouter,.an-menu{position:relative;display:inline-flex;align-items:center;gap:8px;min-height:44px;margin:0;padding:0 12px;border:0;border-radius:10px;background:none;color:var(--ink);font:600 1rem/1 var(--font-body);white-space:nowrap;cursor:pointer;-webkit-tap-highlight-color:transparent}
.an-accueil{padding-left:6px;margin-right:4px}
.an-g-btn{list-style:none}
.an-g-btn::-webkit-details-marker{display:none}
.an-g-btn::marker{content:""}
.an-accueil:hover,.an-g-btn:hover,.an-ecouter:hover,.an-menu:hover{background:var(--tint)}
.an-g-btn[aria-expanded="true"],.an-d[open]>.an-g-btn{background:var(--tint)}
.an-chev{width:12px;height:12px;color:var(--muted);transition:transform .2s ease}
.an-g-btn[aria-expanded="true"] .an-chev,.an-d[open]>.an-g-btn .an-chev{transform:rotate(180deg)}
.an-accueil[aria-current="page"]::after,.an-ici>.an-g-btn::after,.an-ici>.an-d>.an-g-btn::after{content:"";position:absolute;left:12px;right:12px;bottom:2px;height:3px;border-radius:2px;background:var(--gold-ui,var(--gold))}
.an-accueil[aria-current="page"]::after{left:42px}
.an-tiroir{display:flex;align-items:center;min-width:0}
.an-liste{display:flex;align-items:center;gap:2px}
.an-g{position:relative}
.an-l-accueil,.an-t-tete,.an-t-pied,.an-page,.an-menu{display:none}
.an-panneau{position:absolute;top:calc(100% + 10px);left:0;z-index:110;min-width:340px;padding:8px;background:var(--sheet);border:1px solid var(--rule);border-radius:16px;box-shadow:0 26px 56px -18px rgba(8,13,30,.36),0 4px 14px rgba(8,13,30,.1)}
.an-p-tete{display:flex;justify-content:space-between;gap:16px;margin:6px 10px 8px;font:500 .72rem/1.3 var(--font-mono);letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}
.an-items{display:grid;gap:2px}
.an-items a{display:grid;gap:3px;min-height:44px;padding:10px 12px;border-radius:10px}
.an-items a:hover,.an-etapes a:hover{background:var(--tint)}
.an-nom{font:600 1rem/1.25 var(--font-body);color:var(--ink)}
.an-aide{font:400 .87rem/1.3 var(--font-body);color:var(--muted)}
.an-ext{margin-left:.35em;font-weight:500;color:var(--muted)}
.an-items a[aria-current="page"],.an-etapes a[aria-current="page"]{background:var(--tint);background:color-mix(in srgb,var(--gold) 15%,transparent)}
.an-items a[aria-current="page"] .an-nom,.an-etapes a[aria-current="page"] .an-et{color:var(--gold-ink)}
.an-p-parcours{width:640px}
.an-p-groupes{display:grid;grid-template-columns:repeat(var(--an-cols,3),minmax(0,1fr));width:min(880px,calc(100vw - 24px));padding:10px 6px}
.an-sg{min-width:0;padding:0 6px}
.an-sg+.an-sg{border-left:1px solid var(--rule)}
.an-sg-t{margin:6px 12px 6px;font:500 .72rem/1.3 var(--font-mono);letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}
.an-etapes{display:grid;grid-template-columns:1fr 1fr;grid-template-rows:repeat(var(--an-rangs,7),auto);grid-auto-flow:column;gap:2px 8px}
.an-etapes a{display:flex;align-items:center;gap:12px;min-height:44px;padding:6px 10px;border-radius:10px}
.an-num{flex:none;display:grid;place-items:center;width:28px;height:28px;border:1.5px solid var(--gold-ui,var(--gold));border-radius:50%;font:500 .8rem/1 var(--font-mono);color:var(--gold-ink)}
.an-etapes a[aria-current="page"] .an-num{background:var(--gold);border-color:var(--gold);color:var(--on-gold)}
.an-et{font:500 .98rem/1.25 var(--font-body);color:var(--ink)}
.an-3d{margin-left:auto;padding:2px 7px;border:1px solid var(--rule);border-radius:999px;font:500 .68rem/1.3 var(--font-mono);letter-spacing:.06em;color:var(--muted)}
.an-actions{display:flex;align-items:center;gap:4px;margin-left:auto;padding-left:8px}
.an-chercher{display:none;align-items:center;gap:10px;min-width:210px;min-height:44px;margin:0 4px 0 0;padding:0 8px 0 14px;border:1px solid var(--rule);border-radius:999px;background:var(--paper);color:var(--muted);font:500 .97rem/1 var(--font-body);cursor:pointer;-webkit-tap-highlight-color:transparent}
html.an-js .an-chercher{display:inline-flex}
.an-chercher:hover{border-color:var(--muted);color:var(--ink)}
.an-chercher .an-ic{width:18px;height:18px;color:var(--gold-ink)}
.an-chercher kbd{margin-left:auto;padding:2px 8px;border:1px solid var(--rule);border-radius:6px;background:var(--sheet);font:500 .78rem/1.3 var(--font-mono);color:var(--muted)}
.an-ecouter{display:none}
html.an-tts .an-ecouter{display:inline-flex}
.an-ecouter .an-ic{color:var(--gold-ink)}
.an-ecouter[data-etat="lecture"],.an-ecouter[data-etat="pause"]{background:var(--tint);color:var(--gold-ink)}
.atlas-musique{appearance:none;display:inline-flex;align-items:center;justify-content:center;width:44px;height:44px;margin:0;padding:0;border:0;border-radius:999px;background:none;color:var(--muted);cursor:pointer}
html:not(.an-son) .atlas-musique{display:none}
.atlas-musique:hover{color:var(--gold-ink);background:var(--tint)}
.atlas-musique[aria-pressed="true"]{color:var(--gold-ink);box-shadow:inset 0 0 0 2px var(--gold-ui,var(--gold))}
.atlas-musique svg{width:20px;height:20px}
.an-voile{position:fixed;inset:0;z-index:1000;background:rgba(6,10,22,.5);opacity:0;transition:opacity .26s ease}
.an-voile.ouvert{opacity:1}
.an-t-titre{flex:1;display:flex;align-items:center;gap:10px;font:600 1.22rem/1.15 var(--font-display);color:var(--ink)}
.an-fermer{flex:none;display:inline-grid;place-items:center;width:44px;height:44px;margin:0;padding:0;border:0;border-radius:50%;background:none;color:var(--ink);cursor:pointer}
.an-fermer:hover{background:var(--tint)}
.an-t-btn{display:flex;align-items:center;gap:12px;width:100%;min-height:48px;margin:0;padding:0 16px;border:1px solid var(--rule);border-radius:12px;background:var(--paper);color:var(--ink);font:600 1rem/1.2 var(--font-body);text-align:left;cursor:pointer}
.an-t-btn .an-ic,.an-t-btn svg{width:20px;height:20px;color:var(--gold-ink)}
.an-t-btn[aria-pressed="true"],.an-t-btn[data-etat="lecture"],.an-t-btn[data-etat="pause"]{border-color:var(--gold-ui,var(--gold));color:var(--gold-ink)}
html:not(.an-tts) .an-t-ecouter,html:not(.an-son) .atlas-musique-t{display:none}
@media (max-width:999.98px){
html.an-js .an-barre{min-height:56px;gap:4px;padding-left:max(6px,env(safe-area-inset-left,0px));padding-right:max(6px,env(safe-area-inset-right,0px))}
html.an-js .an-menu{display:inline-flex;padding:0 14px 0 10px}
html.an-js .an-accueil{display:none}
html.an-js .an-page{display:block;flex:1 1 auto;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font:600 1.04rem/1.2 var(--font-body);color:var(--ink);text-align:center}
html.an-js .an-actions{margin-left:0;padding-left:0}
html.an-js .an-actions .an-ecouter,html.an-js .an-actions .atlas-musique{display:none}
html.an-js .an-chercher{min-width:0;margin:0;padding:0 12px;border-color:transparent;background:none;color:var(--ink)}
html.an-js .an-chercher .an-lbl,html.an-js .an-chercher kbd{display:none}
html.an-js .an-chercher .an-ic{width:22px;height:22px;color:var(--ink)}
html.an-js .an-tiroir{position:fixed;top:0;bottom:0;left:0;z-index:1001;display:flex;flex-direction:column;align-items:stretch;width:min(88vw,400px);padding:env(safe-area-inset-top,0px) 0 env(safe-area-inset-bottom,0px) env(safe-area-inset-left,0px);background:var(--sheet);box-shadow:24px 0 60px -20px rgba(4,8,20,.5);overflow-y:auto;overscroll-behavior:contain;transform:translateX(-104%);visibility:hidden;transition:transform .26s cubic-bezier(.2,.8,.2,1),visibility 0s linear .26s}
html.an-js .an-tiroir.ouvert{transform:none;visibility:visible;transition:transform .26s cubic-bezier(.2,.8,.2,1)}
html.an-js .an-t-tete{position:sticky;top:0;z-index:1;display:flex;align-items:center;gap:12px;padding:8px 8px 8px 18px;background:var(--sheet);border-bottom:1px solid var(--rule)}
html.an-js .an-liste{display:block;padding:6px 0 10px}
html.an-js .an-l-accueil{display:block}
html.an-js .an-l-accueil a{display:flex;align-items:center;min-height:52px;padding:0 22px;font:600 1.06rem/1.2 var(--font-body)}
html.an-js .an-l-accueil a[aria-current="page"]{color:var(--gold-ink);box-shadow:inset 3px 0 0 var(--gold-ui,var(--gold))}
html.an-js .an-g{position:static;border-top:1px solid var(--rule)}
html.an-js .an-g-btn{display:flex;width:100%;justify-content:space-between;min-height:54px;padding:0 22px;border-radius:0;font-size:1.06rem}
html.an-js .an-g-btn:hover{background:var(--tint)}
html.an-js .an-g-btn::after{display:none}
html.an-js .an-ici>.an-g-btn>span::after{content:"";display:inline-block;width:7px;height:7px;margin-left:10px;border-radius:50%;background:var(--gold-ui,var(--gold));vertical-align:2px}
html.an-js .an-panneau{position:static;width:auto;min-width:0;margin:0;padding:0 10px 12px;border:0;border-radius:0;background:none;box-shadow:none}
html.an-js .an-p-tete{display:none}
html.an-js .an-p-groupes{display:block;width:auto;padding:0 10px 12px}
html.an-js .an-sg{padding:0}
html.an-js .an-sg+.an-sg{border-left:0;margin-top:4px;padding-top:4px;border-top:1px dashed var(--rule)}
html.an-js .an-sg-t{margin:12px 12px 4px}
html.an-js .an-p-groupes .an-aide{display:none}
html.an-js .an-p-groupes .an-items a{align-content:center;padding-top:8px;padding-bottom:8px}
html.an-js .an-etapes{grid-template-columns:minmax(0,1fr);grid-template-rows:none;grid-auto-flow:row}
html.an-js .an-items a,html.an-js .an-etapes a{padding-left:12px}
html.an-js .an-t-pied{display:grid;gap:10px;margin-top:auto;padding:14px 16px 18px;border-top:1px solid var(--rule)}
html:not(.an-js) .an-barre{flex-wrap:wrap;position:relative;padding-block:4px}
html:not(.an-js) .an-tiroir,html:not(.an-js) .an-liste{flex-wrap:wrap}
html:not(.an-js) .an-g{position:static}
html:not(.an-js) .an-panneau{left:8px;right:8px;width:auto;min-width:0}
html:not(.an-js) .an-p-groupes{display:block}
html:not(.an-js) .an-sg+.an-sg{border-left:0}
html:not(.an-js) .an-etapes{grid-template-columns:minmax(0,1fr);grid-template-rows:none;grid-auto-flow:row}
}
@media (prefers-reduced-motion:reduce){.an-tiroir,.an-tiroir.ouvert,.an-voile,.an-chev{transition:none!important}}
@media print{.atlas-nav,.aller-contenu{display:none!important}}
.atlas-suite{display:grid;grid-template-columns:minmax(0,1fr) auto minmax(0,1fr);gap:12px 18px;align-items:center}
.atlas-suite a{display:grid;gap:2px;padding:12px 16px;min-height:44px;border:1px solid var(--rule);border-radius:12px;background:var(--sheet);color:var(--ink);text-decoration:none}
.atlas-suite a:hover{border-color:var(--muted)}
.atlas-suite .s-lbl{font:500 .72rem/1.3 var(--font-mono);letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}
.atlas-suite .s-nom{font:600 1.15rem/1.2 var(--font-display);color:var(--gold-ink)}
.atlas-suite .suiv{text-align:right}
.atlas-suite .etape{display:grid;gap:8px;justify-items:center;text-align:center}
.atlas-suite .etape p{margin:0;font:500 .74rem/1.3 var(--font-mono);letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}
.atlas-suite .etape a.livre{display:inline-flex;align-items:center;min-height:44px;padding:0;border:0;background:none;color:var(--gold-ink);font:500 .95rem/1.3 var(--font-body);text-decoration:underline;text-underline-offset:3px}
.atlas-suite-seule{grid-template-columns:minmax(0,1fr)}
@media (max-width:640px){.atlas-suite{grid-template-columns:minmax(0,1fr)}.atlas-suite .etape{order:-1;justify-items:start;text-align:left}.atlas-suite .suiv{text-align:left}}
.atlas-credit{margin:0;display:flex;flex-wrap:wrap;align-items:center;column-gap:.45em}
.atlas-credit a{display:inline-flex;align-items:center;min-height:44px;color:var(--gold-ink);text-decoration:underline;text-underline-offset:3px}
.atlas-credit .atlas-note{font-size:.92em}
.atlas-droits{margin:0}
.atlas-droits a{padding-block:12px;color:var(--gold-ink);text-decoration:underline;text-underline-offset:3px}
a.ref-lien{padding-block:5px}
'''
NAV_CSS = '<style>' + ''.join(l.strip() for l in NAV_CSS_SRC.strip().splitlines()) + '</style>'


def signaler(name, nom):
    """Adresse du formulaire « Signaler une erreur » (.github/ISSUE_TEMPLATE/erreur.yml), titre et page pré-remplis."""
    q = urllib.parse.urlencode({'template': 'erreur.yml', 'title': f'[Erreur] {nom}', 'page': f'{nom} ({name})'},
                               quote_via=urllib.parse.quote)
    return f'{DEPOT}/issues/new?{q}'


def pied(name, nom, droits='index.html#droits', base=''):
    """Lignes de crédit et de droits, ajoutées à la fin du pied de chaque page (texte déjà typographié : posées après
    la passe de typographie). Les liens externes s'ouvrent dans un nouvel onglet ; le signalement demande un compte
    GitHub. La ligne de droits renvoie à la déclaration de la Fondation Urantia, sur l'accueil, puis au glossaire
    (base : préfixe des adresses du site, pour la page 404 servie à n'importe quelle profondeur)."""
    sep = ' <span aria-hidden="true">·</span> '
    lien_gl = f'{sep}<a href="{base}{GLOSSAIRE}">glossaire des termes</a>' if GLOSSAIRE in noms and name != GLOSSAIRE else ''
    return pied_credit(name, nom, sep) + (f'\n<p class="atlas-droits">Citations du <i>Livre d’Urantia</i>&nbsp;: traduction française '
                                          f'©&nbsp;1960 Urantia Foundation{sep}<a href="{droits}">droits</a>{lien_gl}</p>')


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
# En tête de chaque page à barre : classes posées avant le premier affichage (pas de décalage de la barre). an-js : la
# barre compacte et le tiroir sont pilotés par navigation.js ; an-tts : le navigateur sait lire à voix haute (bouton
# « Écouter ») ; an-son : il sait produire le son (bouton ♪ ; musique.js le confirme).
TETE_JS = ('<script>(function(d,w){var c=d.documentElement.classList;c.add("an-js");'
           'if(w.speechSynthesis&&w.SpeechSynthesisUtterance)c.add("an-tts");'
           'if(w.AudioContext||w.webkitAudioContext)c.add("an-son")})(document,window)</script>')


def esc(s):
    return s.replace('&', '&amp;').replace('"', '&quot;').replace('<', '&lt;')


# ── Typographie française ───────────────────────────────────────────────────────────────────────
NBSP = ' '
# Les polices du site (Alegreya Sans, Cormorant Garamond, IBM Plex Mono) n'ont pas l'espace fine insécable
# (U+202F) : elle s'afficherait presque nulle. On emploie partout l'espace insécable ordinaire.
NNBSP = NBSP


def espaces_lisibles(s):
    """Remplace l'espace fine insécable (absente des polices du site) par l'insécable ordinaire."""
    return (s.replace(' ', ' ').replace('&#8239;', '&#160;')
             .replace('&#x202F;', '&#160;').replace('&#x202f;', '&#160;'))


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
def icone(d, cls='an-ic', vb='0 0 20 20', larg='1.8'):
    """Icône SVG au trait, décorative (aria-hidden)."""
    return (f'<svg class="{cls}" viewBox="{vb}" aria-hidden="true" focusable="false"><path d="{d}" fill="none" '
            f'stroke="currentColor" stroke-width="{larg}" stroke-linecap="round" stroke-linejoin="round"/></svg>')


# Emblème (le dessin de favicon.svg) et icônes de la barre
EMBLEME = ('<svg class="an-emb" viewBox="0 0 64 64" aria-hidden="true" focusable="false"><rect width="64" height="64" rx="14" fill="#0C1120"/>'
           '<ellipse cx="32" cy="33" rx="27" ry="15" fill="none" stroke="#9DB0F0" stroke-opacity=".55" stroke-width="2.6"/>'
           '<ellipse cx="32" cy="33" rx="18" ry="10" fill="none" stroke="#9DB0F0" stroke-opacity=".9" stroke-width="2.6"/>'
           '<ellipse cx="32" cy="33" rx="8" ry="4" fill="#F6C766"/><circle cx="51" cy="19" r="3.6" fill="#F0B33C"/></svg>')
I_MENU = icone('M3.5 5.5h13M3.5 10h13M3.5 14.5h13')
I_FERMER = icone('M5.5 5.5l9 9M14.5 5.5l-9 9')
I_CHEVRON = icone('M3 4.5l3 3 3-3', 'an-chev', '0 0 12 12', '1.6')
I_LOUPE = ('<svg class="an-ic" viewBox="0 0 20 20" aria-hidden="true" focusable="false"><circle cx="8.6" cy="8.6" r="5.4" fill="none" '
           'stroke="currentColor" stroke-width="1.8"/><path d="M12.7 12.7l4 4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>')
I_ECOUTER = ('<svg class="an-ic" viewBox="0 0 20 20" aria-hidden="true" focusable="false"><path d="M3.5 7.6h2.8L10 4.7v10.6l-3.7-2.9H3.5z" '
             'fill="currentColor"/><path d="M13.1 7.3a3.8 3.8 0 0 1 0 5.4M15.5 5a7 7 0 0 1 0 10" fill="none" stroke="currentColor" '
             'stroke-width="1.6" stroke-linecap="round"/></svg>')
I_MUSIQUE = ('<svg viewBox="0 0 20 20" aria-hidden="true" focusable="false">'
             '<ellipse cx="7" cy="15" rx="3.6" ry="2.7" transform="rotate(-20 7 15)" fill="currentColor"/>'
             '<path d="M10.2 14.6V3.2c2.5 1.3 4.7 2.6 5.5 5.6" fill="none" stroke="currentColor" stroke-width="1.8" '
             'stroke-linecap="round" stroke-linejoin="round"/></svg>')


def menu_groupe(cle, titre, contenu, ici, cls='', style=''):
    """Un menu de la barre : details/summary (utilisable sans JavaScript), que navigation.js remplace par un bouton
    « disclosure » (aria-expanded) suivi de son panneau."""
    style = f' style="{style}"' if style else ''
    return (f'<li class="an-g{" an-ici" if ici else ""}"><details class="an-d"><summary class="an-g-btn"><span>{titre}</span>{I_CHEVRON}</summary>'
            f'<div class="an-panneau{cls}" id="an-p-{cle}"{style}>{contenu}</div></details></li>')


def contenu_menu(cle, entrees, name, nom, par_nom):
    """Panneau d'un menu de MENUS : (html, page affichée dedans ?, nombre de sous-groupes titrés). Une chaîne ouvre un
    sous-groupe : intertitre, et liste nommée par lui (aria-labelledby) ; les sous-groupes vides sont omis."""
    blocs, bloc = [], [None, [], False]
    for e in entrees:
        if isinstance(e, str):
            blocs.append(bloc)
            bloc = [e, [], False]
            continue
        h, ici = entree_menu(e, name, nom, par_nom)
        if h:
            bloc[1].append(h)
            bloc[2] = bloc[2] or ici
    blocs = [b for b in blocs + [bloc] if b[1]]
    ici = any(b[2] for b in blocs)
    if not any(b[0] for b in blocs):
        return ''.join(f'<ul class="an-items">{"".join(b[1])}</ul>' for b in blocs), ici, 0
    html = ''
    for k, (titre, items, _) in enumerate(blocs, 1):
        ident = f'an-sg-{cle}-{k}'
        tete = f'<p class="an-sg-t" id="{ident}">{typo(titre)}</p>' if titre else ''
        nomme = f' aria-labelledby="{ident}"' if titre else ''
        html += f'<div class="an-sg">{tete}<ul class="an-items"{nomme}>{"".join(items)}</ul></div>'
    return html, ici, len(blocs)


def entree_menu(e, name, nom, par_nom):
    """<li> d'une entrée de menu (voir MENUS) et vrai si c'est la page affichée ; ('', False) si sa page est absente."""
    if len(e) == 2:                                       # page de l'atlas : nom canonique tiré de PAGES
        adr, aide = e
        if adr.split('#')[0] not in par_nom:
            return '', False
        lib = par_nom[adr.split('#')[0]][2]
    else:
        adr, lib, aide = e
        if adr == SIGNALER:
            adr = signaler(name, nom)
    ext = '://' in adr
    if not ext and adr.split('#')[0] not in par_nom:
        return '', False
    ici = not ext and adr == name
    attrs = (' target="_blank" rel="noopener"' if ext else '') + (' aria-current="page"' if ici else '')
    fleche = '<span class="an-ext" aria-hidden="true">↗</span>' if ext else ''
    sr = '<span class="an-sr"> (nouvel onglet)</span>' if ext else ''
    return (f'<li><a href="{esc(adr)}"{attrs}><span class="an-nom">{typo(lib)}{fleche}</span>'
            f'<span class="an-aide">{typo(aide)}</span>{sr}</a></li>'), ici


def barre(name, nom, court, pages):
    """Barre commune : Accueil · Parcours · Thèmes · Le livre · Outils, puis Rechercher, Écouter et la musique.
    Au bureau (1 000 px et plus), sur une ligne, avec des menus déroulants ; en dessous, barre compacte (Menu, nom court de
    la page, Rechercher) et tiroir où les menus deviennent des accordéons. Page affichée : aria-current, et son menu marqué.
    Sans JavaScript, chaque menu est un details/summary (navigation.js en fait un bouton « disclosure »)."""
    par_nom = {p[1]: p for p in pages}
    # Parcours de découverte : les étapes présentes, numérotées
    etapes = [(a, n) for a, n in PARCOURS if a.split('#')[0] in par_nom]
    lis = []
    for i, (a, n) in enumerate(etapes, 1):
        cur = ' aria-current="page"' if a == name else ''
        tag = '<span class="an-3d" title="Dans la vue 3D">3D</span>' if a.startswith('atlas-3d.html#') else ''
        lis.append(f'<li><a href="{a}"{cur}><span class="an-num">{i}</span><span class="an-et">{typo(n)}</span>{tag}</a></li>')
    groupes = [menu_groupe('parcours', 'Parcours',
                           f'<p class="an-p-tete"><span>Parcours de découverte</span><span>{len(etapes)} étapes</span></p>'
                           f'<ol class="an-etapes" style="--an-rangs:{(len(etapes) + 1) // 2}">{"".join(lis)}</ol>',
                           any(a == name for a, _ in etapes), ' an-p-parcours')]
    for cle, titre, _, entrees in MENUS:
        contenu, ici, colonnes = contenu_menu(cle, entrees, name, nom, par_nom)
        if contenu:
            groupes.append(menu_groupe(cle, titre, contenu, ici, ' an-p-groupes' if colonnes else '',
                                       f'--an-cols:{colonnes}' if colonnes else ''))
    cur = ' aria-current="page"' if name == 'index.html' else ''
    return ('<a class="aller-contenu" href="#contenu">Aller au contenu</a>\n'
            '<nav class="atlas-nav" aria-label="Atlas"><div class="an-barre">'
            f'<button type="button" class="an-menu" aria-expanded="false" aria-controls="an-tiroir">{I_MENU}<span>Menu</span></button>'
            f'<a class="an-accueil" href="index.html"{cur}>{EMBLEME}<span>Accueil</span></a>'
            f'<p class="an-page" aria-hidden="true">{typo(court)}</p>'
            '<div class="an-tiroir" id="an-tiroir">'
            f'<div class="an-t-tete"><p class="an-t-titre">{EMBLEME}<span>{NOM_SITE}</span></p>'
            f'<button type="button" class="an-fermer" aria-label="Fermer le menu">{I_FERMER}</button></div>'
            f'<ul class="an-liste"><li class="an-l-accueil"><a href="index.html"{cur}>Accueil</a></li>{"".join(groupes)}</ul>'
            '<div class="an-t-pied">'
            f'<button type="button" class="an-t-btn an-t-ecouter" data-ecouter>{I_ECOUTER}'
            '<span class="an-lbl">Écouter cette page</span></button>'
            f'<button type="button" class="an-t-btn atlas-musique-t" data-musique aria-pressed="false">{I_MUSIQUE}<span>Musique douce</span></button>'
            '</div></div>'
            '<div class="an-actions">'
            '<button type="button" class="an-chercher" data-chercher aria-keyshortcuts="/ Control+K" aria-label="Rechercher dans l’atlas">'
            f'{I_LOUPE}<span class="an-lbl" aria-hidden="true">Rechercher</span><kbd aria-hidden="true">/</kbd></button>'
            f'<button type="button" class="an-ecouter" data-ecouter>{I_ECOUTER}<span class="an-lbl">Écouter</span></button>'
            f'<button type="button" class="atlas-musique" data-musique aria-pressed="false" aria-label="Musique douce">{I_MUSIQUE}</button>'
            '</div></div></nav>\n')


def groupe_de(name):
    """Groupe d'une page hors parcours, d'après MENUS (« Thème », « Le livre », « Outil »), ou None."""
    for _, _, groupe, entrees in MENUS:
        if any(not isinstance(e, str) and e[0] == name for e in entrees):
            return groupe
    return None


def parcours(name, presents):
    """Bandeau de fin de page : l'étape du parcours, avec la précédente et la suivante ; hors parcours, le nom du groupe
    de la page, sans précédent ni suivant. Renvoie (bandeau, mention pour <span data-etape>) ou (None, None)."""
    etapes = [(a, nom) for a, nom in PARCOURS if a.split('#')[0] in presents]
    adresses = [a for a, _ in etapes]
    livre = (f'<a class="livre" href="{LIVRE[0]}" target="_blank" rel="noopener" aria-label="{LIVRE[1]}, nouvel onglet">'
             f'{LIVRE[1]}&nbsp;↗</a>')
    if name not in adresses:
        groupe = groupe_de(name) if name != 'index.html' else None
        if not groupe:
            return None, None
        return f'<div class="atlas-suite atlas-suite-seule"><div class="etape"><p>{groupe}</p>{livre}</div></div>\n', groupe
    i = adresses.index(name)
    prec = etapes[i - 1] if i else ('index.html', 'Accueil')
    suiv = etapes[i + 1] if i + 1 < len(etapes) else ('index.html', 'Accueil')
    lp = 'Étape précédente' if i else 'Retour'
    ls = 'Étape suivante' if i + 1 < len(etapes) else 'Fin du parcours'
    etape = f'Étape {i + 1} sur {len(etapes)}'
    nav = ('<nav class="atlas-suite" aria-label="Parcours de découverte">'
           f'<a class="prec" href="{prec[0]}"><span class="s-lbl">← {lp}</span><span class="s-nom">{prec[1]}</span></a>'
           f'<div class="etape"><p>Parcours de découverte · {etape}</p>{livre}</div>'
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


# ── Index de recherche (assets/recherche.js) ────────────────────────────────────────────────────
# Écrit à chaque construction à partir des pages construites. Une page est découpée en « sections » : le haut de page,
# chaque intertitre (h1 à h4) et chaque bloc qui porte un identifiant (carte, partie) ; une section a une ancre (son
# identifiant, celui de son intertitre ou du bloc qui le contient) et des textes : paragraphes, éléments de liste,
# légendes, citations, lignes de tableau. S'y ajoutent les termes du glossaire (glossaire-atlas.json), les niveaux,
# astres et panneaux de la vue 3D (tirés de son script), et les références citées par chaque section (.ref), pour la
# recherche d'une référence (57:6.5). Exclus : barre, pied, bandeau, boutons, formulaires, SVG, ce qui est aria-hidden.
# Format : window.ATLAS_RECHERCHE = {P, S, T, R, U}
#   P : [[adresse, nom, étiquette], …]       étiquette : « Étape 4 », « Vue 3D », « Thème », « Le livre », « Outil »
#   S : [[page, ancre, titre(, type)], …]    ancre '' : haut de page ; type 'g' glossaire, '3' vue 3D,
#                                            'i' titre hérité (affiché, pas cherché)
#   T : [[section, texte], …]                R : {"57:6": [[section, de, à], …]} (de = 0 : toute la section)
#   U : page de chaque fascicule sur urantia.org (table de refs-urantia.js)
VIDES_HTML = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}
FERMENT_P = {'address', 'article', 'aside', 'blockquote', 'details', 'dialog', 'div', 'dl', 'fieldset', 'figcaption', 'figure',
             'footer', 'form', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'header', 'hgroup', 'hr', 'main', 'menu', 'nav', 'ol', 'p',
             'pre', 'section', 'table', 'ul'}
IX_EXCLUS = {'script', 'style', 'noscript', 'template', 'svg', 'button', 'input', 'select', 'textarea', 'label', 'nav', 'footer',
             'dialog', 'form', 'fieldset', 'canvas', 'iframe', 'video', 'audio', 'math', 'option', 'img', 'picture'}
IX_CLASSES = {'sr-only', 'vh', 'visually-hidden', 'an-sr', 'eyebrow', 'atlas-suite', 'hl', 'qz', 'toc', 'sommaire'}
IX_ROLES = {'tablist', 'toolbar', 'search', 'menu', 'menubar', 'dialog', 'alertdialog'}
IX_TITRES = {'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}
IX_INLINE = {'a', 'abbr', 'b', 'bdi', 'bdo', 'cite', 'code', 'data', 'del', 'dfn', 'em', 'i', 'ins', 'kbd', 'mark', 'q', 's',
             'samp', 'small', 'span', 'strong', 'sub', 'sup', 'time', 'u', 'var', 'wbr', 'br'}
IX_MAX = 500                               # longueur maximale d'un texte (coupé à une espace, avec « … »)
RX_REF = re.compile(r'(\d{1,3}):(\d{1,2})(?:\.(\d{1,3}))?(?:\s*[–-]\s*(\d{1,3})(?:[.:](\d{1,3}))?)?')
RX_BLANCS = re.compile(r'[ \t\r\n\f\v]+')  # l'espace insécable (typographie) est gardée


class Noeud:
    __slots__ = ('tag', 'attrs', 'enfants', 'parent')

    def __init__(self, tag, attrs, parent):
        self.tag, self.attrs, self.enfants, self.parent = tag, attrs, [], parent


class Arbre(HTMLParser):
    """Arbre d'une page, avec les fermetures implicites courantes (<p> fermé par un bloc, <li>, <dt>, <dd>)."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.racine = Noeud('#', {}, None)
        self.pile = [self.racine]

    def handle_starttag(self, tag, attrs):
        haut = self.pile[-1].tag
        if (haut == 'p' and tag in FERMENT_P) or (tag == 'li' and haut == 'li') or (tag in ('dt', 'dd') and haut in ('dt', 'dd')):
            self.pile.pop()
        n = Noeud(tag, {k: (v or '') for k, v in attrs}, self.pile[-1])
        self.pile[-1].enfants.append(n)
        if tag not in VIDES_HTML:
            self.pile.append(n)

    def handle_startendtag(self, tag, attrs):
        self.pile[-1].enfants.append(Noeud(tag, {k: (v or '') for k, v in attrs}, self.pile[-1]))

    def handle_endtag(self, tag):
        for i in range(len(self.pile) - 1, 0, -1):
            if self.pile[i].tag == tag:
                del self.pile[i:]
                return

    def handle_data(self, d):
        self.pile[-1].enfants.append(d)


def texte_brut(n):
    return ''.join(c if isinstance(c, str) else texte_brut(c) for c in n.enfants)


# Frontières d'éléments accolés, sans espace dans le HTML mais séparés à l'écran (pastille « 1 » puis titre, libellé en
# bloc puis texte) : JOINT entre deux éléments ou une pastille et son texte (une espace entre deux mots) ; JOINT_FAIBLE
# entre un élément et un texte (une espace seulement entre une minuscule et une majuscule : « Pentecôte|Ce jour-là »,
# mais ni « XX|e siècle », ni « Ajusteur|s »).
JOINT, JOINT_FAIBLE = '\x00', '\x01'
PASTILLE = re.compile(r'\s*[\d★☆•?]{1,3}\s*')


def accole(enfants, k):
    """Marque à poser avant l'enfant k (voir JOINT) ; '' si ni l'un ni l'autre."""
    if not k:
        return ''
    a, c = enfants[k - 1], enfants[k]
    if isinstance(a, str) and isinstance(c, str):
        return ''
    if not isinstance(a, str) and not isinstance(c, str):
        return JOINT
    return JOINT if PASTILLE.fullmatch(texte_brut(a if not isinstance(a, str) else c)) else JOINT_FAIBLE


def joints(t):
    t = re.sub(r'(?<=[^\W_])\x00[\x00\x01]*(?=[^\W_])', ' ', t)
    t = re.sub(r'(?<=[a-zà-ÿ])[\x00\x01]+(?=[A-ZÀ-Ý])', ' ', t)
    return t.replace(JOINT, '').replace(JOINT_FAIBLE, '')


def a_un_titre(n):
    return any(not isinstance(c, str) and (c.tag in IX_TITRES or a_un_titre(c)) for c in n.enfants)


def trouver(n, tag):
    for c in n.enfants:
        if not isinstance(c, str):
            if c.tag == tag:
                return c
            r = trouver(c, tag)
            if r:
                return r
    return None


class Indexeur:
    """Découpe une page construite en sections et textes (voir plus haut)."""
    def __init__(self, ix, page, nom, desc, sauter=()):
        self.ix, self.p, self.sauter = ix, page, set(sauter)
        self.vide, self.provisoire = {}, {}
        self.s = self.nouvelle('', nom)
        if desc:
            self.ajouter(desc)

    def nouvelle(self, ancre, titre, provisoire=False):
        self.ix['S'].append([self.p, ancre, titre])
        s = len(self.ix['S']) - 1
        self.vide[s], self.provisoire[s] = True, provisoire
        return s

    def ajouter(self, t):
        t = RX_BLANCS.sub(' ', joints(t)).strip(' ·,;')
        if not re.search(r'[^\W\d_]', t) or (len(t) < 16 and not re.search(r'\d', t)):   # libellés d'interface courts
            return
        if len(t) > IX_MAX:
            t = t[:IX_MAX].rsplit(' ', 1)[0].rstrip(' ,;:') + '…'
        if self.ix['T'] and self.ix['T'][-1] == [self.s, t]:
            return
        self.ix['T'].append([self.s, t])
        self.vide[self.s] = False

    def refs(self, texte):
        noter_refs(self.ix['R'], self.s, texte)

    def exclu(self, n):
        a = n.attrs
        if n.tag in IX_EXCLUS or a.get('aria-hidden') == 'true' or a.get('data-recherche') == 'non' or a.get('id') in self.sauter:
            return True
        if a.get('role') in IX_ROLES or 'aria-live' in a or a.get('aria-label', '').startswith('Sommaire'):
            return True                          # interface, messages d'état, sommaires (doublons des intertitres)
        return bool(IX_CLASSES.intersection(a.get('class', '').split()))

    def inline(self, n, buf):
        """Texte d'un titre : sans les zones exclues ; ses références sont notées."""
        for k, c in enumerate(n.enfants):
            j = accole(n.enfants, k)
            if j:
                buf.append(j)
            if isinstance(c, str):
                buf.append(c)
            elif 'ref' in c.attrs.get('class', '').split():
                self.refs(texte_brut(c))
                buf.append(texte_brut(c))
            elif not self.exclu(c):
                self.inline(c, buf)
        return buf

    def titre(self, h, t):
        s = self.s
        if self.provisoire[s] and self.vide[s]:    # premier intertitre d'un bloc à identifiant : il le nomme
            self.ix['S'][s][2], self.provisoire[s] = t, False
            return
        self.s = self.nouvelle(h.attrs.get('id') or self.ix['S'][s][1], t)

    def marcher(self, n, buf):
        for k, c in enumerate(n.enfants):
            j = accole(n.enfants, k)                     # éléments accolés (pastille « 1 » et titre…) : voir JOINT
            if j:
                buf.append(j)
            if isinstance(c, str):
                buf.append(c)
                continue
            if 'ref' in c.attrs.get('class', '').split():   # référence : notée, et gardée dans le texte
                self.refs(texte_brut(c))
                buf.append(texte_brut(c))
                continue
            if self.exclu(c):
                continue
            tag = c.tag
            if tag in IX_TITRES:
                self.ajouter(''.join(buf))
                buf.clear()
                t = RX_BLANCS.sub(' ', joints(''.join(self.inline(c, [])))).strip()
                if t:
                    self.titre(c, t)
                continue
            if tag in ('td', 'th'):
                if ''.join(buf).strip():
                    buf.append(' · ')
                self.marcher(c, buf)
                continue
            if tag in IX_INLINE:
                if tag == 'br':
                    buf.append(' ')
                else:
                    self.marcher(c, buf)
                continue
            # bloc de texte (p, li, dd, figcaption, tr…) ou conteneur (div, section, ul, table…) : textes séparés
            self.ajouter(''.join(buf))
            buf.clear()
            ident, sauve = c.attrs.get('id', ''), None
            if ident and ident != 'contenu' and a_un_titre(c):   # bloc à identifiant avec intertitre (carte, partie) :
                sauve = self.s                                   # une section, le temps du bloc
                self.s = self.nouvelle(ident, self.ix['S'][sauve][2], provisoire=True)
            local = []
            self.marcher(c, local)
            self.ajouter(''.join(local))
            if sauve is not None:
                self.s = sauve


def noter_refs(R, s, texte):
    """Références d'un texte (57:6.5, 57:6.3–5, 57:6.3–7.2, 57:6) dans R, pour la section s."""
    for m in RX_REF.finditer(texte):
        f, sec = int(m.group(1)), int(m.group(2))
        a = int(m.group(3)) if m.group(3) else 0
        fin, fin2 = m.group(4), m.group(5)
        plages = []
        if fin and fin2:                             # 57:6.3–7.2 : jusqu'à une autre section
            s2 = int(fin)
            plages = [(sec, a, 999)] + [(k, 0, 0) for k in range(sec + 1, s2)] + [(s2, 1, int(fin2))]
        elif fin and a:                              # 57:6.3–5
            plages = [(sec, a, max(a, int(fin)))]
        elif fin:                                    # 57:6–8 : des sections entières
            plages = [(k, 0, 0) for k in range(sec, max(sec, int(fin)) + 1)]
        else:
            plages = [(sec, a, a)]
        for k, de, a2 in plages:
            liste = R.setdefault(f'{f}:{k}', [])
            if [s, de, a2] not in liste:
                liste.append([s, de, a2])


def index_glossaire(ix, page):
    """Les termes du glossaire, une section chacun (ancre = identifiant du terme dans glossaire.html)."""
    d = json.loads((SRC / GLOSSAIRE_JSON).read_text(encoding='utf-8'))
    for t in (d['termes'] if isinstance(d, dict) else d):
        ix['S'].append([page, t.get('id', ''), typo(t['terme']), 'g'])
        s = len(ix['S']) - 1
        ix['T'].append([s, typo(t['definition'])])
        if t.get('anglais'):
            ix['T'].append([s, f'En anglais{NBSP}: {t["anglais"]}'])
        if t.get('citation'):
            ix['T'].append([s, f'«{NBSP}{typo(t["citation"]["texte"])}{NBSP}» ({t["citation"]["ref"]})'])
            noter_refs(ix['R'], s, t['citation']['ref'])
        for r in t.get('refs', []):
            noter_refs(ix['R'], s, r)


# Vue 3D : niveaux (HASH_LV et INFO de son script), astres (BODY), panneaux (boutons t-…), Havona et le Paradis.
LIEUX_3D = [('havona', 'Havona', 'L’univers central, autour de l’Ile du Paradis.'),
            ('paradis', 'Le Paradis', 'L’Ile centrale, au cœur du maitre univers.')]
PANNEAUX_3D = [('t-gov', 'gouvernement'), ('t-time', 'frise'), ('t-asc', 'carriere'), ('t-coupe', 'coupe'), ('t-deite', 'deite')]


def js_texte(s):
    """Texte lisible d'une chaîne littérale du script 3D (échappements, balises, entités, références entre accolades)."""
    s = s.replace("\\'", "'").replace('\\"', '"')
    s = re.sub(r'<[^>]+>', ' ', s)
    return RX_BLANCS.sub(' ', html_lib.unescape(s)).strip()


def index_3d(ix, page, html):
    S, T = ix['S'], ix['T']
    lit = r"'((?:[^'\\]|\\.)*)'"
    hashs = re.search(r"const HASH_LV = \[([^\]]*)\]", html)
    info = re.search(r'const INFO = \[(.*?)\n  \];', html, re.S)
    n = 0
    if hashs and info:
        ancres = re.findall(r"'([a-z-]+)'", hashs.group(1))
        lignes = [l for l in info.group(1).split('\n') if re.match(r'\s*\{ h: ', l)]
        for ancre, l in zip(ancres, lignes):
            h = re.match(r"\s*\{ h: " + lit, l)
            S.append([page, ancre, js_texte(h.group(1)), '3'])
            s = len(S) - 1
            p = re.search(r"\bp: " + lit, l)
            if p:
                T.append([s, js_texte(re.sub(r'\{(\d{1,3}:[\d.–-]+)\}', ' ', p.group(1)))])
            for r in re.findall(r"REF\('([^']*)'\)", l):
                noter_refs(ix['R'], s, r)
            n += 1
    corps = list(re.finditer(r"\n    (\w+): \{ n: " + lit + r", k: " + lit + r", e: " + lit, html))
    for k, m in enumerate(corps):
        deja = [i for i, x in enumerate(S) if x[0] == page and x[1] == m.group(1)]   # #urantia : niveau et astre
        if deja:
            s = deja[0]
        else:
            S.append([page, m.group(1), js_texte(m.group(2)), '3'])
            s = len(S) - 1
        T.append([s, js_texte(m.group(4))])
        fin = corps[k + 1].start() if k + 1 < len(corps) else m.end() + 3000    # jusqu'à l'astre suivant
        bloc = html[m.end():min(fin, m.end() + 6000)]
        for b in re.findall(r"BR\(" + lit + r"\)", bloc):
            for r in re.findall(r'\{(\d{1,3}:[\d.–-]+)\}', b):
                noter_refs(ix['R'], s, r)
            T.append([s, js_texte(re.sub(r'\s*\{\d{1,3}:[\d.–-]+\}', '', b))])
        n += 1
    for ancre, titre, texte in LIEUX_3D:
        S.append([page, ancre, titre, '3'])
        T.append([len(S) - 1, texte])
    for bouton, ancre in PANNEAUX_3D:
        m = re.search(r'id="' + bouton + r'"[^>]*title="([^"]*)"[^>]*>([^<]*)<', html)
        if m:
            S.append([page, ancre, html_lib.unescape(m.group(2)).strip(), '3'])
            T.append([len(S) - 1, html_lib.unescape(m.group(1)).split(':', 1)[-1].strip()])
            n += 1
    if not n:
        print('avertissement : vue 3D : niveaux et astres introuvables dans son script, seuls Havona et le Paradis sont indexés')


def etiquette(name):
    """Étiquette d'une page dans les résultats : son étape, la vue 3D, ou son groupe."""
    if name == 'index.html':
        return ''
    if name == 'atlas-3d.html':
        return 'Vue 3D'
    etapes = [a for a, _ in PARCOURS if a.split('#')[0] in noms]
    if name in etapes:
        return f'Étape {etapes.index(name) + 1}'
    return groupe_de(name) or ''


def ecrire_index(construites):
    """assets/recherche.js, à partir des pages construites ; renvoie (pages, sections, textes, octets)."""
    ix = {'P': [], 'S': [], 'T': [], 'R': {}}
    for name, nom, desc, page in construites:
        ix['P'].append([name, nom, etiquette(name)])
        p = len(ix['P']) - 1
        if name in SANS_BARRE:
            ix['S'].append([p, '', nom])
            ix['T'].append([len(ix['S']) - 1, desc])
            index_3d(ix, p, page)
            continue
        arbre = Arbre()
        arbre.feed(page)
        arbre.close()
        main = trouver(arbre.racine, 'main') or trouver(arbre.racine, 'body') or arbre.racine
        ixr = Indexeur(ix, p, nom, desc, sauter=('liste',) if name == GLOSSAIRE else ())
        debut = len(ix['T'])
        buf = []
        ixr.marcher(main, buf)
        ixr.ajouter(''.join(buf))
        compte = {}                                  # libellés répétés dans la page (« Ce qui concorde »…) : retirés
        for _, x in ix['T'][debut:]:
            compte[x] = compte.get(x, 0) + 1
        ix['T'][debut:] = [e for e in ix['T'][debut:] if compte[e[1]] < 4]
        for s, prov in ixr.provisoire.items():      # bloc sans intertitre : titre du contexte, affiché mais pas cherché
            if prov:
                ix['S'][s].append('i')
        if name == GLOSSAIRE and (SRC / GLOSSAIRE_JSON).exists():
            index_glossaire(ix, p)
    # sections sans texte ni titre propre (blocs d'interface) retirées, indices renumérotés
    avec_texte = {s for s, _ in ix['T']} | {s for l in ix['R'].values() for s, _, _ in l}
    garder = [i for i, x in enumerate(ix['S']) if i in avec_texte or (x[2] and x[-1] != 'i' and x[2] != 'Sommaire')]
    neuf = {v: k for k, v in enumerate(garder)}
    ix['S'] = [ix['S'][i] for i in garder]
    ix['T'] = [[neuf[s], t] for s, t in ix['T'] if s in neuf]
    ix['R'] = {k: [[neuf[s], a, b] for s, a, b in v if s in neuf] for k, v in ix['R'].items()}
    ix['R'] = {k: v for k, v in ix['R'].items() if v}
    # table des fascicules de refs-urantia.js (liens vers urantia.org)
    m = re.search(r'var S = (\[.*?\]);', (SRC / 'refs-urantia.js').read_text(encoding='utf-8'), re.S)
    ix['U'] = json.loads(m.group(1)) if m else []
    if not m:
        problems.append('recherche : table des fascicules introuvable dans refs-urantia.js')
    js = ('/* Index de la recherche de « Le Livre d’Urantia en images », écrit par construire_site.py à chaque construction :\n'
          '   ne pas le modifier à la main. Chargé par assets/navigation.js à la première recherche. */\n'
          'window.ATLAS_RECHERCHE=' + json.dumps(ix, ensure_ascii=False, separators=(',', ':')) + ';\n')
    js = espaces_lisibles(js)
    (OUT / 'assets' / RECHERCHE_JS).write_text(js, encoding='utf-8', newline='\n')
    return len(ix['P']), len(ix['S']), len(ix['T']), len(js.encode('utf-8'))


# ── Construction ────────────────────────────────────────────────────────────────────────────────
# Page « Le livre fascicule par fascicule » (fascicules.html) : régénérée d'abord par fascicules.py, pour suivre les pages
# arrivées depuis (le générateur ne réécrit ses fichiers que si quelque chose a changé ; il écrit aussi
# ../couverture-du-livre.md, hors du site). Il lit la carte du livre de la copie de travail de l'auteur : depuis un clone
# du dépôt, la page de sources/ est reprise telle quelle. Une erreur du générateur ne bloque pas la construction.
GENERATEUR = SRC / 'fascicules.py'


def regenerer_fascicules():
    if not GENERATEUR.exists():
        return
    if MODE_DEPOT:
        print('fascicules.py : non lancé (clone du dépôt) ; fascicules.html est reprise telle quelle')
        return
    try:
        r = subprocess.run([sys.executable, '-I', str(GENERATEUR.resolve())], cwd=str(SRC.resolve().parents[2]), capture_output=True,
                           text=True, encoding='utf-8', errors='replace', timeout=600)
    except (OSError, subprocess.SubprocessError) as e:
        print(f'avertissement : fascicules.py non lancé ({e}) ; la page fascicules.html existante est gardée')
        return
    for ligne in (r.stdout or '').splitlines():
        print('fascicules.py : ' + ligne)
    if r.returncode:
        fin = ((r.stderr or '').strip().splitlines() or ['erreur sans message'])[-1]
        print(f'avertissement : fascicules.py a échoué (code {r.returncode} : {fin}) ; la page fascicules.html existante est gardée')


regenerer_fascicules()
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


def source_presente(fichier):
    return (SRC / fichier).exists() or (fichier == 'urantia-paradis-3d.html' and (SRC / 'urantia-paradis-3d.src.html').exists())


# Liste robuste : une page sans source est ignorée (avertissement), ses liens restent en texte jusqu'à son arrivée.
present = [p for p in PAGES if source_presente(p[0])]
A_VENIR = {p[1]: p for p in PAGES if not source_presente(p[0])}
for f, n, nom, _, _ in A_VENIR.values():
    print(f'avertissement : source absente, page ignorée pour l’instant : {f} (« {nom} »)')
noms = {p[1] for p in present}
urlmap = {artefacts[f]: n for (f, n, _, _, _) in present if f in artefacts}
problems = []
GL_ACTIF = (SRC / GLOSSAIRE_JS).exists() and (SRC / GLOSSAIRE_JSON).exists()   # infobulles du glossaire dans les pages 2D
QZ_ACTIF = (SRC / QUIZ_JS).exists() and (SRC / QUIZ_JSON).exists()             # quiz des étapes du parcours
QZ_PAGES = {a.split('#')[0] for a, _ in PARCOURS}                              # pages des 13 étapes, vue 3D comprise


def liens_a_venir(html, name):
    """Lien vers une page annoncée dont la source n'est pas encore là : son texte reste, sans lien (pas de lien cassé)."""
    vus = []

    def sans_lien(m):
        if m.group(1) not in A_VENIR:
            return m.group(0)
        vus.append(m.group(1))
        return f'<span class="lien-a-venir">{m.group(2)}</span>'
    html = re.sub(r'<a\b[^>]*?\shref="([a-z0-9-]+\.html)(?:#[^"]*)?"[^>]*>(.*?)</a>', sans_lien, html, flags=re.S)
    for cible in sorted(set(vus)):
        print(f'avertissement : {name} : {vus.count(cible)} lien(s) vers {cible} (page à venir) laissé(s) en texte simple')
    return html


def empreinte_glossaire():
    """Empreinte des données du glossaire, inscrite par glossaire.py dans la page (liste des termes à jour ?)."""
    return hashlib.sha256((SRC / GLOSSAIRE_JSON).read_bytes().replace(b'\r\n', b'\n')).hexdigest()[:12]


def donnees_glossaire():
    """Données des infobulles, compactes et typographiées, pour assets/glossaire.js ; contrôles au passage."""
    d = json.loads((SRC / GLOSSAIRE_JSON).read_text(encoding='utf-8'))
    termes = d['termes'] if isinstance(d, dict) else d
    exclusions = d.get('exclusions', []) if isinstance(d, dict) else []      # expressions à ne jamais marquer
    out, vus, formes = [], set(), {}
    for t in termes:
        i = t.get('id', '')
        if i in vus:
            problems.append(f'glossaire : identifiant en double ({i})')
        vus.add(i)
        a = t.get('atlas') or {}
        if a and a.get('href', '').split('#')[0] in A_VENIR:
            print(f'avertissement : glossaire : {i} renvoie vers une page à venir ({a.get("href")}), lien omis pour l’instant')
            a = {}
        elif a and a.get('href', '').split('#')[0] not in noms:
            problems.append(f'glossaire : {i} renvoie vers une page absente ({a.get("href")})')
        for f in t.get('formes', []):
            k = re.sub(r'\s+', ' ', f).replace("'", '’')
            if formes.get(k, i) != i:
                problems.append(f'glossaire : forme « {f} » partagée par {formes[k]} et {i}')
            formes[k] = i
        o = {'i': i, 't': typo(t['terme']), 'e': t.get('anglais', ''), 'd': typo(t['definition']), 'r': t.get('refs', []),
             'f': t.get('formes', [])}
        if t.get('casse') == 'stricte':
            o['s'] = 1
        if t.get('citation'):
            o['c'] = [typo(t['citation']['texte']), t['citation']['ref']]
        if a:
            o['a'] = [a['href'], typo(a.get('titre', ''))]
        out.append(o)
    return json.dumps({'termes': out, 'exclusions': exclusions}, ensure_ascii=False, separators=(',', ':'))
OUT.mkdir(parents=True, exist_ok=True)
apercu_wh = taille_png(ACTIFS_DIR / 'apercu.png') if (ACTIFS_DIR / 'apercu.png').exists() else (1200, 630)


def adresses_locales(html):
    """Adresses claude.ai et CDN remplacées par des liens relatifs ; liens internes dans le même onglet. Un lien vers
    une page du site publié (BASE…, utile dans une page claude.ai quand la page visée n'y est pas publiée) devient
    relatif lui aussi."""
    for u, n in urlmap.items():
        html = html.replace(u, n)
    for u, n in CDN.items():
        html = html.replace(u, n)
    html = re.sub(r'href="' + re.escape(BASE) + r'([a-z0-9-]+\.html)(#[^"]*)?"',
                  lambda m: f'href="{m.group(1)}{m.group(2) or ""}"' if m.group(1) in noms else m.group(0), html)

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


construites = []                     # (adresse, nom, description, page) : matière de l'index de recherche
for fichier, name, nom, court, desc in present:
    html = liens_a_venir(adresses_locales(lire_source(fichier)), name)
    html = re.sub(r'<link rel="preconnect" href="https://fonts\.(googleapis|gstatic)\.com"( crossorigin)?>\s*', '', html)
    html = re.sub(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com/css2\?[^"]*">',
                  '<link rel="stylesheet" href="assets/fonts/fonts.css">', html)
    html = re.sub(r'<meta name="claude:[^"]*"[^>]*>\s*', '', html)
    # rangées de liens propres aux artefacts claude.ai : la barre commune les remplace dans le site
    html = re.sub(r'\s*<(p|div|span|li)\b[^>]*\sdata-artefact\b[^>]*>.*?</\1>', '', html, flags=re.S)
    titre = NOM_SITE if name == 'index.html' else f'{nom} — {NOM_SITE}'
    html = re.sub(r'<title>.*?</title>', f'<title>{titre}</title>', html, count=1, flags=re.S)
    if name == GLOSSAIRE:             # liste des termes écrite par glossaire.py : à jour avec glossaire-atlas.json ?
        m = re.search(r'<!--GLOSSAIRE:DEBUT empreinte=([0-9a-f]+)-->', html)
        if (SRC / GLOSSAIRE_JSON).exists() and (not m or m.group(1) != empreinte_glossaire()):
            problems.append('glossaire.html : liste des termes à régénérer '
                            '(python -I glossaire.py page glossaire-atlas.json glossaire.html artefacts.json)')
        html = re.sub(r'<!--(?:GLOSSAIRE|AZ|THEMES):(?:DEBUT|FIN)[^>]*-->\n?', '', html)
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
        suite, etape = parcours(name, noms)     # étape du parcours, ou groupe (Thème, Le livre, Outil) hors parcours
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
        body = barre(name, nom, court, present) + body.lstrip()
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
    desc_t, titre_t = typo(desc), typo(titre)
    meta = ('<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            + ('' if name in SANS_BARRE else TETE_JS + '\n') +
            f'<meta name="description" content="{esc(desc_t)}">\n'
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
            f'<meta property="og:title" content="{esc(titre_t)}">\n<meta property="og:description" content="{esc(desc_t)}">\n'
            f'<meta property="og:url" content="{url}">\n'
            f'<meta property="og:image" content="{BASE}assets/apercu.png">\n'
            f'<meta property="og:image:width" content="{apercu_wh[0]}">\n<meta property="og:image:height" content="{apercu_wh[1]}">\n'
            f'<meta property="og:image:alt" content="{esc(APERCU_ALT)}">\n'
            '<meta name="twitter:card" content="summary_large_image">\n'
            f'<meta name="twitter:image:alt" content="{esc(APERCU_ALT)}">\n'
            '<script src="assets/hors-ligne.js" defer></script>\n'
            '<script src="assets/musique.js" defer></script>\n'
            '<script src="assets/navigation.js" defer></script>\n' +      # barre, tiroir, recherche (vue 3D : entrée de son menu)
            ('' if name in SANS_BARRE else '<script src="assets/ecouter.js" defer></script>\n') +   # lecture à voix haute : pages 2D
            ('<script src="assets/glossaire.js" defer></script>\n'          # infobulles : pages 2D, sauf le glossaire lui-même
             if GL_ACTIF and name not in SANS_BARRE and name != GLOSSAIRE else '') +
            ('<script src="assets/quiz.js" defer></script>\n'               # quiz : pages des étapes du parcours
             if QZ_ACTIF and name in QZ_PAGES else ''))
    page = ('<!doctype html>\n<html lang="fr">\n<head>\n' + meta + RESET + '\n' + head.strip() +
            '\n</head>\n<body>\n' + body.strip() + '\n</body>\n</html>\n')
    construites.append((name, nom, desc_t, page))
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
    (OUT / name).write_text(espaces_lisibles(page), encoding='utf-8')
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
<footer class="foot">{pied('404.html', 'Page introuvable', BASE + '#droits', BASE)}</footer>
</main>
</body>
</html>
'''
(OUT / '404.html').write_text(espaces_lisibles(passe_typo(p404, js=False)), encoding='utf-8')

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
for f in SCRIPTS:
    if (SRC / f).exists():
        shutil.copy2(SRC / f, assets / f)
    else:
        problems.append(f'source absente : {f}')
if GL_ACTIF:                                     # infobulles du glossaire : le script, avec ses données à la place du marqueur
    gl_js = (SRC / GLOSSAIRE_JS).read_text(encoding='utf-8')
    if gl_js.count(MARQUE_GLOSSAIRE) != 1:
        problems.append(f'{GLOSSAIRE_JS} : marqueur des données introuvable ou en double ({MARQUE_GLOSSAIRE})')
    else:
        (assets / GLOSSAIRE_JS).write_text(gl_js.replace(MARQUE_GLOSSAIRE, espaces_lisibles(donnees_glossaire())), encoding='utf-8', newline='\n')
else:
    problems.append(f'glossaire : {GLOSSAIRE_JS} ou {GLOSSAIRE_JSON} absent, infobulles non posées')
if QZ_ACTIF:                                     # quiz : le script, avec ses données (compactes) à la place du marqueur
    qz_js = (SRC / QUIZ_JS).read_text(encoding='utf-8')
    qz = json.loads((SRC / QUIZ_JSON).read_text(encoding='utf-8'))
    for e in qz.get('etapes', []):
        if e.get('page') not in noms:
            problems.append(f'quiz : étape {e.get("n")}, page absente du site ({e.get("page")})')
    if qz_js.count(MARQUE_QUIZ) != 1:
        problems.append(f'{QUIZ_JS} : marqueur des données introuvable ou en double ({MARQUE_QUIZ})')
    else:                                        # espaces fines insécables (absentes des polices) remplacées, code et données
        (assets / QUIZ_JS).write_text(espaces_lisibles(qz_js.replace(MARQUE_QUIZ, json.dumps(qz, ensure_ascii=False, separators=(',', ':')))),
                                      encoding='utf-8', newline='\n')
else:
    problems.append(f'quiz : {QUIZ_JS} ou {QUIZ_JSON} absent, quiz non posés')
ix_stats = ecrire_index(construites)              # assets/recherche.js
print(f'recherche : {ix_stats[0]} pages, {ix_stats[1]} sections, {ix_stats[2]} textes, {ix_stats[3] / 1024:.0f} Ko')
for f in RACINE + GITHUB:                        # le dossier .git du site n'est jamais touché
    if (ENTREES / f).exists():
        (OUT / f).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ENTREES / f, OUT / f)
        if f == 'README.md' and A_VENIR:              # tableau des pages : lignes des pages à venir retirées (pas de lien cassé)
            lignes = (ENTREES / f).read_text(encoding='utf-8').split('\n')
            garde = [l for l in lignes if not re.match(r'\| \[[^\]]*\]\((' + '|'.join(map(re.escape, A_VENIR)) + r')\)', l)]
            (OUT / f).write_text('\n'.join(garde), encoding='utf-8', newline='\n')
    else:
        problems.append(f'fichier absent : {f}')
(OUT / '.nojekyll').write_text('', encoding='utf-8')
sources = OUT / 'sources'
sources.mkdir(exist_ok=True)
for f in SOURCES:
    if not (SRC / f).exists():
        if not any(p[0] == f for p in A_VENIR.values()):   # page à venir : déjà signalée par un avertissement
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
(OUT / 'hors-ligne.html').write_text(espaces_lisibles(passe_typo(phl, js=False)), encoding='utf-8')

# Service worker : liste des fichiers de l'atlas (ni sources/, ni README, ni licences, ni .git, ni 404, ni aperçu de partage)
polices_web = ['assets/fonts/' + f.name for f in sorted(POLICES.iterdir()) if f.suffix in ('.woff2', '.css')]
icones = ['assets/' + i[0] for i in ICONES]
NOYAU_HL = (['index.html', 'hors-ligne.html', 'manifest.webmanifest'] + ['assets/' + f for f in SCRIPTS] +
            (['assets/' + GLOSSAIRE_JS] if GL_ACTIF else []) + (['assets/' + QUIZ_JS] if QZ_ACTIF else []) +
            ['assets/favicon.svg', 'assets/apple-touch-icon.png'] + icones + polices_web)
# l'index de la recherche n'est pas dans le noyau (il n'est chargé qu'à l'ouverture de la recherche) : enregistré à sa
# première utilisation, ou par le téléchargement complet
LISTE_HL = list(dict.fromkeys([n for _, n, _, _, _ in present] + NOYAU_HL + ['assets/' + RECHERCHE_JS,
                                                                            'assets/lib/three.min.js', 'assets/lib/OrbitControls.js']))
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
# Budget de citations. La déclaration « Permission to Quote » de la Fondation Urantia permet de citer sa traduction
# jusqu'à 25 000 mots dans une même œuvre (avec au moins autant de mots propres et 5 000 mots consécutifs au plus).
# Par prudence, le site entier compte comme une seule œuvre. On compte chaque passage distinct placé entre « » et
# suivi de près d'une référence p:s.a ; au-delà de 24 000 mots, la construction le signale.
PLAFOND_CITATIONS, ALERTE_CITATIONS = 25000, 24000


def mots_cites_du_livre():
    mot, refp, vus = re.compile(r"[A-Za-zÀ-ÿœŒ0-9’'-]+"), re.compile(r'\b\d{1,3}:\d{1,2}\.\d{1,3}'), {}
    for p in OUT.glob('*.html'):
        if p.name in ('404.html', 'hors-ligne.html'):
            continue
        t = re.sub(r'<style.*?</style>', ' ', p.read_text(encoding='utf-8'), flags=re.S)
        txt = html_lib.unescape(re.sub(r'<[^>]+>', ' ', t)).replace('\u00a0', ' ')
        for m in re.finditer(r'«\s*(.*?)\s*»', txt, flags=re.S):
            q = m.group(1)
            if len(q) <= 4000 and refp.search(txt[m.end():m.end() + 90]):
                vus[re.sub(r'\W+', ' ', q.lower()).strip()] = len(mot.findall(q))
    return sum(vus.values()), len(vus)


cites, n_cites = mots_cites_du_livre()
print(f'citations du livre : {cites} mots en {n_cites} passages distincts (plafond {PLAFOND_CITATIONS} mots)')
if cites > ALERTE_CITATIONS:
    problems.append(f'citations : {cites} mots du livre cités, proche ou au-delà du plafond de {PLAFOND_CITATIONS} mots '
                    '(« Permission to Quote ») ; raccourcir des citations ou demander une permission écrite')
print('\n'.join(problems) if problems else 'vérification : aucune adresse externe à remplacer, aucun lien interne cassé')
