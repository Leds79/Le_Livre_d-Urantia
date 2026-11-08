# Reconstruire le site

Ce dossier contient les pages, les scripts et les données intermédiaires qui produisent « Le Livre d’Urantia en images ». Les étapes s’enchaînent dans cet ordre : **polices → étoiles → contours → textures → assemblage → références → site**. Les données intermédiaires (`etoiles.json`, `geo.json`, `tex.json`, `refs-urantia.js`) sont fournies : pour reconstruire le site, la dernière étape suffit.

## Reconstruire le site depuis un clone du dépôt

Depuis la racine du dépôt, dans un **autre** dossier (le script refuse d’écrire sur ses propres sources) :

```
python -I sources/construire_site.py sources ../atlas-site
```

Python 3.11 ou plus récent suffit ; aucun paquet n’est nécessaire pour cette étape. Le script trouve les pages dans `sources/`, les ressources dans le site publié (polices et Three.js dans `assets/`, README, licences et `.github/` à la racine) et assemble la vue 3D à la volée à partir de `urantia-paradis-3d.src.html` et de ses données, comme l’étape 5. Le dossier obtenu est le site complet : on peut l’ouvrir (`index.html`) ou le publier, par exemple en le copiant à la racine du dépôt.

Pour modifier une page : éditer `sources/<page>.html`, reconstruire, vérifier dans un navigateur, puis proposer la modification (voir `CONTRIBUER.md`).

## Note pour le mainteneur : les sources maîtresses

La copie de travail de l’auteur garde, hors du dépôt, les **sources maîtresses** des pages (`visuels/source/*.html`) : elles contiennent les adresses des versions publiées sur claude.ai (`artefacts.json`) et les rangées de liens `data-artefact` propres à ces versions. La construction en tire les copies nettoyées de `sources/` (adresses rendues relatives, rangées et balises `claude:` retirées). **Une contribution acceptée sur `sources/*.html` doit donc être reportée dans la source maîtresse**, sans quoi la construction suivante l’effacerait. Une page remplacée (par exemple une nouvelle version de `bible-et-livre.html`) est reprise telle quelle à la construction suivante : il suffit de remplacer la source maîtresse.

## Toute la chaîne : ce qu’il faut

- Python 3.11 ou plus récent (essayé avec 3.13), avec les paquets de `requirements.txt` : `python -m pip install -r requirements.txt` (NumPy et Pillow, pour `textures.py` seulement) ;
- Node.js 18 ou plus récent, pour le test facultatif `smoke3d.js` ;
- un dossier de travail organisé ainsi (copie de travail de l’auteur) :

```
visuels/
  lib/                three.min.js et OrbitControls.js (Three.js r128), LICENSE-three.txt
  source/             ce dossier : pages maîtresses de l’atlas, scripts, données intermédiaires,
                      hors-ligne.js et musique.js (copiés dans assets/)
    polices/          fonts.css, fichiers WOFF2 et licences OFL (produits par polices.py)
    site/             README.md, LICENCES.md, LICENSE, LICENSE-CONTENU.md, CONTRIBUER.md, .github/
                      (formulaires de tickets, modèle de demande), favicon.svg, apercu.png,
                      apple-touch-icon.png, icone-192.png, icone-512.png, icone-512-maskable.png
    artefacts.json    facultatif, non publié : adresses claude.ai des pages, rendues relatives
```

Les icônes de l’application (`icone-*.png`) et `apple-touch-icon.png` sont des rendus de `favicon.svg` par Chrome sans interface ; la version `maskable` place le dessin dans la zone sûre (80 % du diamètre) sur fond plein `#0C1120`.

Three.js r128 : https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js et https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js.

## Étapes

Commandes lancées depuis `visuels/source/`.

1. **Polices** : `python -I polices.py polices` télécharge Alegreya Sans, Cormorant Garamond et IBM Plex Mono (Google Fonts, sous-ensemble latin) et écrit un fichier WOFF2 par police, `fonts.css` et les licences OFL. Sans réseau, `python -I polices.py polices --depuis <ancienne fonts.css>` réutilise une feuille à polices intégrées.
2. **Étoiles** : `python -I etoiles.py <hygdata_v41.csv> etoiles.json`.
3. **Contours** : `python -I geo.py <dossier des fichiers Natural Earth> geo.json`.
4. **Textures** : `python -I textures.py <dossier des images> tex.json` ; le dossier contient `terre-jour.jpg`, `terre-nuit.jpg`, `lune.jpg` et `planetes/` (`jupiter.jpg`, `mars.jpg`, `mercure.jpg`, `pluton.jpg`).
5. **Assemblage de la vue 3D** : `python -I assembler.py urantia-paradis-3d.src.html etoiles.json urantia-paradis-3d.html geo.json tex.json`, puis, pour tester : `node smoke3d.js urantia-paradis-3d.html ../lib/three.min.js ../lib/OrbitControls.js`.
6. **Références** : `python -I liens_refs.py table <table des matières enregistrée> refs-urantia.js` fabrique le script à partir de la table des matières de https://www.urantia.org/fr/le-livre-durantia/lire ; `python -I liens_refs.py injecte refs-urantia.js <pages…>` le place en fin de page (bloc `<script id="refs-urantia">`, gardé dans les pages publiées sur claude.ai ; dans le site, il devient le fichier partagé `assets/refs-urantia.js`).
6 bis. **Glossaire** : les termes sont dans `glossaire-atlas.json` (définitions dans nos mots, références, citations courtes, formes repérées dans les pages). `python -I glossaire.py verifie glossaire-atlas.json` contrôle la structure et, dans la copie de travail de l’auteur (texte du livre et `outils/ub.py`), chaque référence et chaque citation (0 écart attendu) ; `python -I glossaire.py page glossaire-atlas.json glossaire.html artefacts.json` réécrit la liste de A à Z de la page, puis `python -I liens_refs.py injecte refs-urantia.js glossaire.html`. La construction injecte les données dans `assets/glossaire.js` (infobulles des pages 2D, pas de la vue 3D) et signale une liste de la page qui ne correspond plus aux données.
7. **Site** : dans la copie de travail de l’auteur, depuis le dossier qui contient `erudit/` et `site/` : `python -I erudit/visuels/source/construire_site.py erudit/visuels/source site` ; depuis un clone du dépôt : voir plus haut. Le script ajoute à chaque page la barre commune, le parcours de découverte, le pied commun (crédit, code source, licences, « Signaler une erreur sur cette page »), les métadonnées et la typographie française ; il copie les ressources, écrit `404.html`, `hors-ligne.html`, `manifest.webmanifest` et le service worker `sw.js`, puis vérifie les liens internes.

## Application installable et lecture hors ligne

- `manifest.webmanifest` (nom, icônes, couleurs) et les balises d’installation sont écrits par `construire_site.py` ; `assets/hors-ligne.js` (source : `hors-ligne.js`) enregistre le service worker, seulement en http(s), et anime l’encadré « Lire hors ligne » de l’accueil.
- `assets/musique.js` (source : `musique.js`) est chargé par chaque page : il pilote le bouton ♪ de la barre commune (attribut `data-musique`), qu’il ne démasque que si le navigateur produit le son.
- `sw.js` est **réécrit à chaque construction**. `VERSION` est l’empreinte du contenu des fichiers de l’atlas (pages, polices, Three.js, scripts, icônes, manifeste ; ni `sources/`, ni README, ni licences, ni `.git`) : dès qu’un fichier change, la version change, l’ancien cache est supprimé à l’activation, et les fichiers déjà enregistrés sont repris (copiés s’ils n’ont pas changé, téléchargés de nouveau sinon).
- À l’installation, un noyau léger est enregistré (accueil, page hors ligne, polices, scripts communs, icônes, manifeste). Les pages consultées le sont ensuite au fil de la lecture ; le bouton « Télécharger pour lire hors ligne » enregistre tout le reste. Navigations : le réseau d’abord (3 s au plus), puis la copie enregistrée, puis `hors-ligne.html`. Les autres sites (urantia.org) ne sont jamais mis en cache.

## Données d’entrée

Copies utilisées le 2026-11-07. Les images de Wikimedia Commons sont des vignettes de 2 048 px de large obtenues par l’API de Commons : Commons peut les régénérer, et leur empreinte changer.

| Données | Source | Fichier utilisé | Taille (octets) | SHA-256 |
|---|---|---|---|---|
| Catalogue d’étoiles HYG v4.1 (David Nash, CC BY-SA 4.0) | https://codeberg.org/astronexus/hyg | `hygdata_v41.csv` | 33 932 548 | `d9f69fd86bbf90a4e4d52b4c5c53eacfa6dfc0bfdef85bfd94f095e0bebe4ebd` |
| Natural Earth, terres 1:50 m (domaine public) | https://github.com/nvkelso/natural-earth-vector/tree/master/geojson | `ne_50m_land.geojson` | 1 636 166 | `e874b27a51d146452be360cafb3cc50c86001074a67d534113e6534682f9826b` |
| Natural Earth, lacs 1:110 m | idem | `ne_110m_lakes.geojson` | 36 648 | `eb02ecc86c82004fccbf979058bfabbbd6c2d07968c7844d38eb1c9152d2ffc9` |
| Natural Earth, fleuves 1:110 m | idem | `ne_110m_rivers_lake_centerlines.geojson` | 38 087 | `55aa4497405afc07cdc931b7fbe062c4d6693ba2a550c0d24899953f5d507c8d` |
| Natural Earth, fleuves 1:50 m | idem | `ne_50m_rivers_lake_centerlines.geojson` | 827 318 | `f286e0ce978fde999ca2d7a78c764be08542e19b63cded52b05c12d5173ccc51` |
| Terre de jour, NASA Blue Marble Next Generation (domaine public) | https://commons.wikimedia.org/wiki/File:Whole_world_-_land_and_oceans.jpg | `terre-jour.jpg` | 1 114 599 | `16002ce631925ee643bc50b405abca63e8b4eab8d9e0505b57f0f1dc3ac0f8c7` |
| Terre de nuit, NASA (domaine public) | https://commons.wikimedia.org/wiki/File:The_earth_at_night.jpg | `terre-nuit.jpg` | 683 992 | `b4fdd3f53133ca2352d7fb7902ec97e292fa5f61226e22387adfa32bf77b16bb` |
| Lune, NASA SVS CGI Moon Kit (domaine public) | https://svs.gsfc.nasa.gov/4720/ (`lroc_color_poles_1k.jpg`) | `lune.jpg` | 139 068 | `b246064f217f8d479df78c49c7c8595a8f5fbda008a72fd539978d2e121e0109` |
| Jupiter, Cassini PIA07782 (NASA/JPL/Space Science Institute) | https://commons.wikimedia.org/wiki/File:Jupiter_Cylindrical_Map_-_Dec_2000_PIA07782.jpg | `planetes/jupiter.jpg` | 441 285 | `6b835ddd8036ea9efd25def04f75aa60b69b096025a37eeae5e9b6978e0a2281` |
| Mars, mosaïque Viking MDIM 2.1 (NASA/JPL/USGS) | https://commons.wikimedia.org/wiki/File:Mars_Viking_MDIM21_ClrMosaic_1km.jpg | `planetes/mars.jpg` | 2 440 499 | `033ec286b543dcf699557e8ef0bce14a464f9a01776bb014f66f6f6ba1703c53` |
| Mercure, MESSENGER PIA15063 (NASA/JHUAPL/Carnegie Institution of Washington) | https://commons.wikimedia.org/wiki/File:Mercury_Global_View.jpg | `planetes/mercure.jpg` | 1 998 505 | `5b5df8550b7ede88c58583b1dcbd65e93001f1e07d8510d214462f666e00760b` |
| Pluton, New Horizons (NASA/JHUAPL/SwRI) | https://commons.wikimedia.org/wiki/File:Pluto_color_mapmosaic.jpg | `planetes/pluton.jpg` | 1 114 589 | `91b4f97b5ca54c14ed23b197b1b1893988bc246e95d45a9d51bdfda369e9a7f1` |

Autres sources : éléments orbitaux approchés du JPL (https://ssd.jpl.nasa.gov/planets/approx_pos.html, valeurs reportées dans le gabarit 3D) ; table des matières du livre sur urantia.org (pour `refs-urantia.js`) ; feuille Google Fonts indiquée dans `polices.py`.
