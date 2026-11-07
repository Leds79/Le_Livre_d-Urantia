# Le Livre d’Urantia en images

Un atlas visuel et interactif pour comprendre l’origine et l’organisation de l’univers selon *Le Livre d’Urantia* : notre adresse dans l’univers, une vue en 3D d’Urantia jusqu’au Paradis, la frise du temps de Satania et d’Urantia, la carrière ascendante, les êtres de l’univers et les grands concepts du livre.

**Consulter en ligne :** https://constructoai.github.io/Le_Livre_d-Urantia/

## Les pages

| Page | Ce qu’on y voit |
|---|---|
| [Accueil](index.html) | notre adresse dans l’univers, un parcours de découverte en sept étapes, le plan du livre |
| [D’Urantia au Paradis, en 3D](atlas-3d.html) | zoom de la Terre jusqu’au-delà du maitre univers : vraies étoiles, superunivers en galaxies, Havona, vue en coupe, Déité ; « Qui gouverne quoi » ; frise du temps ; carrière ascendante |
| [Nébadon dans Orvonton](nebadon-dans-orvonton.html) | la place de notre univers local, et celle de la Voie lactée |
| [Familles de personnalités](familles-de-personnalites.html) | les êtres de l’univers selon les classifications d’Uversa (30:2) et du Paradis (30:1) |
| [Concepts en schémas](concepts-en-schemas.html) | personnalité, mental, Ajusteur, âme, adjuvats, cercles psychiques, niveaux de réalité, morontia |
| [Dieu et la Déité](dieu-et-deite.html) | le JE SUIS et les sept Absolus, la Trinité, les Sept Maitres Esprits, Dieu le Septuple, les Déités expérientielles |
<!--PAGES-A-VENIR-->

La vue 3D accepte des liens directs : `atlas-3d.html#lune`, `#nebadon`, `#orvonton`, `#havona`, `#paradis`, `#frise`, `#carriere`, `#gouvernement`, `#coupe`, `#deite`.

## Consulter hors ligne

Téléchargez le dépôt (bouton **Code**, puis **Download ZIP**), décompressez-le et ouvrez `index.html` dans un navigateur récent. Tout fonctionne sans connexion : Three.js et les polices sont inclus. Seuls les liens vers le texte du livre, sur urantia.org, demandent Internet.

## Méthode

- Chaque affirmation renvoie au texte, au format fascicule:section.paragraphe (par exemple 15:14.5).
- Trois registres sont distingués : ce que le texte dit, les lectures courantes, le regard historique.
- Les citations sont courtes et exactes ; le reste est paraphrasé, avec sa référence.
- Ce que le livre ne précise pas est dit ; en 3D, les positions et les formes schématiques sont signalées comme telles.

## Avertissement

Aide à l’étude indépendante, sans lien officiel avec la Fondation Urantia. Le texte cité est la traduction française du *Livre d’Urantia* publiée par la Fondation Urantia (édition 2024) ; le site n’en reproduit que de courtes citations, toujours référencées. Le texte intégral se lit sur [urantia.org](https://www.urantia.org/fr/le-livre-durantia/lire).

## Sources de la vue 3D

Le dossier `sources/` contient le gabarit de la vue 3D, les données d’étoiles (`etoiles.json`) et de contours terrestres (`geo.json`), et les scripts qui les produisent et les assemblent : `etoiles.py`, `geo.py`, `textures.py`, `polices.py`, `assembler.py`, `construire_site.py`. `smoke3d.js` exécute la vue 3D hors navigateur pour détecter les erreurs.

## Données et licences

Voir [LICENCES.md](LICENCES.md).
