# Contribuer à « Le Livre d’Urantia en images »

Merci de vouloir améliorer l’atlas ! Les corrections, les signalements et les idées sont bienvenus, qu’on soit lecteur de longue date ou simple curieux.

## Signaler une erreur ou proposer une idée

- **Une erreur** (citation, référence, fait, affichage, lien cassé) : le lien « Signaler une erreur sur cette page », au pied de chaque page, ouvre un formulaire déjà rempli avec le nom de la page. On peut aussi passer par l’onglet **Issues** du dépôt, puis « Signaler une erreur ». Indiquez ce qui est écrit, ce qu’il faudrait, et la référence du livre qui le justifie.
- **Une idée** (page, schéma, amélioration) : onglet **Issues**, puis « Proposer une idée ».

Un compte GitHub (gratuit) est nécessaire pour ouvrir un ticket.

## Proposer une modification

1. Copiez le dépôt avec le bouton **Fork**.
2. Modifiez les pages dans `sources/` (par exemple `sources/vie-de-jesus.html`), jamais les pages construites à la racine.
3. Reconstruisez le site dans un autre dossier et vérifiez-le dans un navigateur : depuis la racine du dépôt, `python -I sources/construire_site.py sources ../atlas-site` (détails dans [`sources/CONSTRUIRE.md`](sources/CONSTRUIRE.md)).
4. Ouvrez une **pull request** (demande de fusion) en expliquant ce qui change et pourquoi. La liste de contrôle proposée aide à ne rien oublier.

Une petite correction de texte peut aussi se faire directement dans l’interface de GitHub (icône crayon sur le fichier de `sources/`).

## Les règles du site

- **Citations exactes et vérifiées.** Toute citation reproduit le texte de la traduction française de la Fondation Urantia (édition 2024) mot pour mot, suivie de sa référence au format `fascicule:section.paragraphe` (par exemple `196:3.34`). Une paraphrase est présentée comme telle, avec sa référence.
- **Citations courtes.** Trois phrases au plus par citation, coupes marquées par « […] » : le texte reste sous le droit d’auteur de la Fondation Urantia, et le site n’en reproduit que de courts extraits. Le texte intégral se lit sur urantia.org.
- **Budget de citations.** La permission de citer de la Fondation (« Permission to Quote ») plafonne l’ensemble des citations à 25 000 mots. Le site en cite environ 22 000 : la construction affiche le total (« citations du livre : … mots ») et le signale au-delà de 24 000. Une nouvelle citation doit donc se justifier ; souvent, la référence seule suffit.
- **Orthographe rectifiée conservée.** La traduction applique l’orthographe rectifiée de 1990 (*connaitre, maitre, ile, évènement*) : on la garde dans les citations, sans la « corriger ».
- **Neutralité.** Le site explique sans prêcher : ni prosélytisme ni dénigrement. Ce que le livre ne précise pas est dit comme tel.
- **Trois registres distincts** : *le texte dit* (ce qui est écrit, avec la référence), *lecture courante* (interprétations répandues, présentées comme telles), *regard historique* (origines du livre, contexte, sources humaines).
- **Vocabulaire du texte** : *mental* (anglais *mind*) n’est pas *esprit* (*spirit*) ; on écrit *morontiel*, *Micaël*, *Maitre* (pour Jésus).

## Licences des contributions

En proposant une contribution, vous acceptez qu’elle soit publiée sous les licences du dépôt : **MIT** pour le code (`LICENSE`) et **CC BY-SA 4.0** pour le contenu (`LICENSE-CONTENU.md`). Les citations du livre restent sous le droit d’auteur de la Fondation Urantia ; le texte biblique (édition numérique de mission-web.com) sous CC BY-NC-SA 3.0.

## Code de conduite

- Restez courtois et bienveillant ; critiquez les propositions, jamais les personnes.
- Les tickets et les demandes portent sur le site : son exactitude, sa clarté, son fonctionnement. Ce n’est pas le lieu des débats de croyances, pour ou contre le livre.
- Les messages hors sujet ou irrespectueux peuvent être masqués ou fermés.

## Pour aller plus loin

La chaîne complète de construction (polices, étoiles, contours, textures, vue 3D, références, site) est décrite dans [`sources/CONSTRUIRE.md`](sources/CONSTRUIRE.md).
