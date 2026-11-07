# Le Livre d’Urantia en images

Un atlas visuel et interactif pour comprendre l’origine et l’organisation de l’univers selon *Le Livre d’Urantia* : notre adresse dans l’univers, une vue en 3D d’Urantia jusqu’au Paradis, la frise du temps de Satania et d’Urantia, la carrière ascendante, les êtres de l’univers et les grands concepts du livre.

**Consulter en ligne :** https://leds79.github.io/Le_Livre_d-Urantia/

## Les pages

| Page | Ce qu’on y voit |
|---|---|
| [Accueil](index.html) | notre adresse dans l’univers, un parcours de découverte en douze étapes, le plan du livre |
| [Nébadon dans Orvonton](nebadon-dans-orvonton.html) | la place de notre univers local, et celle de la Voie lactée |
| [D’Urantia au Paradis (3D)](atlas-3d.html) | zoom de la Terre jusqu’au-delà du maitre univers : vraies étoiles, superunivers en galaxies, Havona, vue en coupe, Déité ; Qui gouverne quoi ; La frise du temps ; La carrière ascendante |
| [Familles de personnalités](familles-de-personnalites.html) | les êtres de l’univers selon les classifications d’Uversa (30:2) et du Paradis (30:1) |
| [Concepts en schémas](concepts-en-schemas.html) | personnalité, mental, Ajusteur, âme, adjuvats, cercles psychiques, niveaux de réalité, morontia |
| [Dieu et la Déité](dieu-et-deite.html) | le JE SUIS et les sept Absolus, la Trinité, les Sept Maitres Esprits, Dieu le Septuple, les Déités expérientielles |
| [L’histoire d’Urantia](histoire-d-urantia.html) | frise des époques, de la nébuleuse d’Andronover à la fin des glaces ; carte des migrations humaines en 22 épisodes |
| [La rébellion de Lucifer](rebellion-de-lucifer.html) | les trois échelles (Jérusem, Dalamatia, le Jardin), pourquoi Urantia est une planète isolée, le manifeste, les loyaux et les rebelles |
| [La vie de Jésus](vie-de-jesus.html) | frise de 92 étapes, de l’annonce à Marie à la Pentecôte ; cartes de Palestine, de la Méditerranée et de l’Orient |
| [La Bible et le Livre d’Urantia](bible-et-livre.html) | vingt parallèles entre la Bible (Crampon 1923) et le livre, des origines à la Pentecôte : ce qui concorde, ce qui diffère |
<!--PAGES-A-VENIR-->

Chaque page porte la même barre de navigation ; les pages du parcours de découverte indiquent leur étape et mènent à la précédente et à la suivante.

La vue 3D accepte des liens directs (`atlas-3d.html#…`) :

- niveaux : `#urantia`, `#monmatia`, `#satania`, `#norlatiadek`, `#nebadon`, `#ensa`, `#splandon`, `#orvonton`, `#grand-univers`, `#espace-exterieur`, `#maitre-univers`, `#au-dela`, `#havona`, `#paradis` ;
- astres : `#soleil`, `#mercure`, `#venus`, `#lune`, `#mars`, `#asteroides`, `#jupiter`, `#saturne`, `#uranus`, `#neptune`, `#pluton`, `#halley` ;
- panneaux : `#gouvernement` (Qui gouverne quoi), `#frise` (La frise du temps), `#carriere` (La carrière ascendante), `#coupe` (vue en coupe), `#deite` (Déité).

## Consulter hors ligne

Téléchargez le dépôt (bouton **Code**, puis **Download ZIP**), décompressez-le et ouvrez `index.html` dans un navigateur récent. Tout fonctionne sans connexion : Three.js et les polices sont inclus. Seuls les liens vers le texte du livre, sur urantia.org, demandent Internet.

## Méthode

- Chaque affirmation renvoie au texte, au format fascicule:section.paragraphe (par exemple 15:14.5). Les références sont cliquables : elles ouvrent le passage sur urantia.org.
- Trois registres sont distingués : ce que le texte dit, les lectures courantes, le regard historique.
- Les citations sont courtes et exactes ; le reste est paraphrasé, avec sa référence.
- Ce que le livre ne précise pas est dit ; en 3D, les positions et les formes schématiques sont signalées comme telles.

## Avertissement

Aide à l’étude indépendante, sans lien officiel avec la Fondation Urantia. Le texte cité est la traduction française du *Livre d’Urantia* publiée par la Fondation Urantia (édition 2024) ; le site n’en reproduit que de courtes citations, toujours référencées. Le texte intégral se lit sur [urantia.org](https://www.urantia.org/fr/le-livre-durantia/lire).

## Sources

Le dossier `sources/` contient de quoi reconstruire le site, avec la marche à suivre dans `sources/CONSTRUIRE.md` et les dépendances Python dans `sources/requirements.txt` :

- le gabarit de la vue 3D (`urantia-paradis-3d.src.html`) et ses données : étoiles (`etoiles.json`), contours terrestres (`geo.json`), textures (`tex.json`) ;
- les scripts qui les produisent et les assemblent : `polices.py`, `etoiles.py`, `geo.py`, `textures.py`, `assembler.py` ;
- les références cliquables : `liens_refs.py` fabrique `refs-urantia.js`, le script qui relie chaque référence au passage correspondant sur urantia.org ;
- `construire_site.py`, qui produit le site à partir des pages ;
- `smoke3d.js`, qui exécute la vue 3D hors navigateur pour détecter les erreurs.

## Licences

Code sous licence MIT (`LICENSE`) ; contenu sous licence CC BY-SA 4.0 (`LICENSE-CONTENU.md`), hors citations du livre et données de tiers. Détail des données, bibliothèques et crédits : [LICENCES.md](LICENCES.md).
