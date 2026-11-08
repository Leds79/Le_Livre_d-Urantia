/* Quiz « Teste tes connaissances » de l’atlas : cinq questions par étape du parcours de découverte, sur ce que la
   page enseigne, selon le livre. Une question à la fois ; après chaque réponse, juste ou faux, une explication et sa
   référence ; à la fin, le score, le rappel des bonnes réponses et « Recommencer ».

   Où le bloc apparait :
   - pages 2D : à la fin du contenu de <main>, avant la navigation du parcours (.atlas-suite) et le pied de page ;
   - vue 3D (atlas-3d.html, étapes 2 à 5) : une entrée « Quiz » dans le menu (details#menu .menu-panel, après la liste
     des pages) ouvre une boite de dialogue, sur le quiz du mode affiché (vue générale, Qui gouverne quoi, frise,
     carrière), modifiable ; tout élément [data-quiz-ouvrir] de la page l’ouvre aussi (data-quiz-ouvrir="4" : étape 4).
   Quelle étape :
   - attribut data-quiz sur un élément : data-quiz="7" ou data-quiz="3,4,5" (numéros d’étape) ; sur <html> ou <body>,
     il choisit seulement l’étape ; sur un autre élément, le bloc se place dans cet élément ; data-quiz="non" : rien ;
   - sinon, le nom du fichier de la page (champ « page » des données ; les noms des sources maîtresses sont reconnus).
   Rien n’est ajouté si la page n’a pas de questions.

   Données : quiz-atlas.json, injecté à la construction (construire_site.py) à la place du marqueur ci-dessous. Tout
   est donc dans ce fichier : il marche hors ligne (service worker) et même ouvert depuis le disque (file://).
   Les références (span.ref) deviennent des liens vers urantia.org grâce à refs-urantia.js, qui suit les ajouts.
   Le glossaire (glossaire.js) ne touche pas au bloc (data-glossaire="non"). */
(function () {
  'use strict';
  var DONNEES = {"version":1,"source":"Le Livre d’Urantia, traduction française de la Fondation Urantia, édition 2024 ; références fascicule:section.paragraphe vérifiées avec outils/ub.py.","etapes":[{"n":1,"titre":"Nébadon dans Orvonton","page":"nebadon-dans-orvonton.html","ancre":"","questions":[{"q":"Selon le livre, quel est le numéro d’Urantia dans le système de Satania ?","choix":["24","70","606","619"],"bonne":2,"explication":"Urantia « porte le numéro 606 dans le groupe planétaire ou système de Satania », qui compte présentement 619 mondes habités.","ref":"15:14.5"},{"q":"Selon le livre, environ combien de mondes habités ou habitables compte un système local ?","choix":["Environ mille","Environ dix mille","Environ un million","Environ un milliard"],"bonne":0,"explication":"L’unité de base du supergouvernement, appelée système, « est formée d’environ mille mondes habités ou habitables ».","ref":"15:2.3"},{"q":"Selon le livre, où se situe Nébadon dans le superunivers d’Orvonton ?","choix":["Au centre, autour d’Uversa","Très excentré, près de la lisière extérieure","Au cœur de la Voie lactée","En dehors d’Orvonton, près d’Andromède"],"bonne":1,"explication":"Le livre précise que Nébadon est « présentement très excentré et proche de la lisière extérieure d’Orvonton ».","ref":"32:2.11"},{"q":"Selon le livre, que représente la Voie lactée pour le superunivers d’Orvonton ?","choix":["Son noyau central","Notre univers local, Nébadon","L’univers central, Havona","Un superunivers voisin"],"bonne":0,"explication":"Pour le livre, le vaste système d’étoiles de la Voie lactée « représente le noyau central d’Orvonton », le septième superunivers.","ref":"15:3.1"},{"q":"Selon le livre, quel est le statut de la cosmologie qu’il présente ?","choix":["Elle est inspirée et définitive","Elle est confirmée par l’astronomie actuelle","Elle n’est pas inspirée et devra en partie être revue"],"bonne":2,"explication":"Les révélateurs préviennent que beaucoup de leurs affirmations sur les sciences physiques devront être revues, et que la cosmologie révélée ici n’est pas inspirée.","ref":"101:4.2"}]},{"n":2,"titre":"D’Urantia au Paradis","page":"atlas-3d.html","ancre":"","questions":[{"q":"Selon le livre, comment s’appelle la famille planétaire de notre soleil ?","choix":["Monmatia","Satania","Andronover","Angona"],"bonne":0,"explication":"Monmatia est le « nom de la famille planétaire de votre soleil », c’est-à-dire le système solaire auquel appartient Urantia.","ref":"57:5.3"},{"q":"Selon le livre, combien de sphères compte Havona, l’univers central ?","choix":["Sept","Cent mille","Un milliard","Mille milliards"],"bonne":2,"explication":"Havona, éternel et « sans commencement ni fin », consiste en un milliard de sphères d’une perfection sublime, avec l’Ile du Paradis en son centre.","ref":"12:1.10"},{"q":"Selon le livre, quel est le seul élément stationnaire du maitre univers ?","choix":["Uversa","L’Ile du Paradis","Salvington","Jérusem"],"bonne":1,"explication":"Tout tourne dans le maitre univers, sauf le centre même de Havona, « l’éternelle Ile du Paradis, le centre de gravité ».","ref":"12:4.1"},{"q":"Selon le livre, en combien d’ellipses concentriques le maitre univers existe-t-il ?","choix":["Trois","Six","Sept","Douze"],"bonne":1,"explication":"Le maitre univers existe en « six ellipses concentriques » autour de l’Ile centrale : Havona, les sept superunivers et quatre niveaux d’espace extérieur.","ref":"12:1.3–9"},{"q":"Selon le livre, à quoi ressemblerait le profil d’une section verticale de l’espace total ?","choix":["À une sphère pleine","À une spirale à sept bras","À une pyramide","À une croix de Malte"],"bonne":3,"explication":"Le profil d’une section verticale de l’espace total « ressemblerait un peu à une croix de Malte », dont les bras horizontaux figurent l’univers.","ref":"11:7.3"}]},{"n":3,"titre":"Qui gouverne quoi","page":"atlas-3d.html","ancre":"gouvernement","questions":[{"q":"Selon le livre, qui a reçu l’autorité d’agir à la place de Micaël comme Prince Planétaire d’Urantia ?","choix":["Caligastia","Adam","Machiventa Melchizédek","Van"],"bonne":2,"explication":"L’autorité de vice-gérant pour agir à la place de Micaël comme Prince Planétaire « a été récemment conférée à Machiventa Melchizédek ».","ref":"114:1.2"},{"q":"Selon le livre, qui est le souverain actuel du système de Satania ?","choix":["Lucifer","Caligastia","Gabriel","Lanaforge"],"bonne":3,"explication":"Le souverain du système est Lanaforge, « numéro 2 709 de l’ordre primaire et successeur de l’apostat Lucifer ».","ref":"45:3.2"},{"q":"Selon le livre, qui régit une constellation comme Norlatiadek ?","choix":["Trois Anciens des Jours","Un Fils Créateur","Trois Très Hauts, des Fils Vorondadeks","Un Prince Planétaire"],"bonne":2,"explication":"Chaque constellation a un siège architectural et « est régie par trois Fils de l’ordre des Vorondadeks, les Très Hauts ».","ref":"15:2.4"},{"q":"Selon le livre, qui sont le père et la mère d’un univers local ?","choix":["Adam et Ève","Gabriel et Emmanuel de Salvington","Les Anciens des Jours et les Très Hauts","Le Fils Créateur et la Divine Ministre"],"bonne":3,"explication":"Les univers locaux ont une double supervision : leur père est le Fils Créateur, et leur mère la Divine Ministre, l’Esprit Créatif de l’univers local.","ref":"33:5.1"},{"q":"Selon le livre, combien d’Anciens des Jours régissent chaque superunivers ?","choix":["Un","Trois","Sept","Vingt-quatre"],"bonne":1,"explication":"Chaque superunivers est régi par trois Anciens des Jours, « chefs exécutifs conjoints du supergouvernement ».","ref":"15:10.3"}]},{"n":4,"titre":"La frise du temps","page":"atlas-3d.html","ancre":"frise","questions":[{"q":"Selon le livre, de quelle nébuleuse notre soleil est-il issu ?","choix":["Andronover","Andromède","Angona","Monmatia"],"bonne":0,"explication":"Notre soleil, né il y a 6 milliards d’années, est l’un des derniers soleils issus de la nébuleuse d’Andronover, qui en produisit plus d’un million.","ref":"57:4.8"},{"q":"Selon le livre, il y a environ combien de temps Lucifer proclama-t-il son manifeste ?","choix":["Environ un million d’années","Environ 500 000 ans","Environ 200 000 ans","Environ 37 000 ans"],"bonne":2,"explication":"Le manifeste de Lucifer fut proclamé au conclave annuel de Satania, sur la mer de verre, « il y a environ deux-cent-mille ans du temps d’Urantia ».","ref":"53:4.1"},{"q":"Selon le livre, combien de Princes Planétaires se rallièrent à Lucifer dans la rébellion ?","choix":["Sept","Douze","Vingt-quatre","Trente-sept"],"bonne":3,"explication":"La rébellion eut lieu à l’échelle du système : trente-sept Princes Planétaires séparatistes firent passer, dans une large mesure, l’administration de leurs mondes du côté de l’archirebelle.","ref":"53:7.1"},{"q":"Selon le livre, à quelle date Jésus naquit-il ?","choix":["Le 14 janvier de l’an 26","Le 21 aout de l’an 7 av. J.-C.","Le 7 avril de l’an 30"],"bonne":1,"explication":"Selon le texte, c’est « à midi le 21 aout de l’an 7 av. J.-C. » que Marie accoucha d’un enfant mâle, Jésus de Nazareth.","ref":"122:8.1"},{"q":"Selon le livre, quelle mesure isole encore partiellement le système de Satania des autres systèmes ?","choix":["Les corps de gravité obscurs","La zone de calme qui entoure les superunivers","Une quarantaine de Norlatiadek"],"bonne":2,"explication":"Même si Urantia retrouvait les circuits du système, l’ensemble de Satania « reste soumis à une quarantaine de Norlatiadek, qui l’isole partiellement de tous les autres systèmes ».","ref":"46:8.2"}]},{"n":5,"titre":"La carrière ascendante","page":"atlas-3d.html","ancre":"carriere","questions":[{"q":"Selon le livre, combien y a-t-il de mondes des maisons ?","choix":["Trois","Sept","Douze","Soixante-dix"],"bonne":1,"explication":"Le nom de mondes des maisons s’applique plus spécifiquement « aux sept satellites du monde numéro un », parmi les cinquante-six mondes qui entourent Jérusem.","ref":"47:0.1"},{"q":"Selon le livre, après les mondes des maisons, dans quel ordre l’ascendeur passe-t-il par ces trois capitales ?","choix":["Salvington, Édentia, puis Jérusem","Édentia, Jérusem, puis Salvington","Jérusem, Salvington, puis Édentia","Jérusem, Édentia, puis Salvington"],"bonne":3,"explication":"La formation se poursuit des mondes des maisons et des sphères de Jérusem jusqu’aux 70 royaumes d’Édentia, puis aux 490 sphères entourant Salvington.","ref":"37:6.2"},{"q":"Selon le livre, que maitrise surtout l’ascendeur pendant son séjour sur Édentia ?","choix":["La langue d’Uversa","La physique supérieure","L’art de l’adoration","L’éthique de groupe"],"bonne":3,"explication":"Le séjour sur Édentia et ses sphères associées se passe « principalement à maitriser l’éthique de groupe », le secret de bonnes relations entre personnalités.","ref":"43:8.3"},{"q":"Selon le livre, d’où partent toujours les diplômés dirigés sur Havona ?","choix":["De Jérusem","Des rivages d’Uversa","D’Édentia","De Salvington"],"bonne":1,"explication":"Les pèlerins sont rééduqués dans les sept universités d’Uversa, et « on fait toujours partir directement des rivages d’Uversa les diplômés qui sont dirigés sur Havona ».","ref":"15:7.10"},{"q":"Selon le livre, où se réveillent les pèlerins qui s’endorment sur le premier cercle de Havona ?","choix":["Sur le premier monde des maisons","Sur Uversa","Sur les rives du Paradis","Sur le septième circuit de Havona"],"bonne":2,"explication":"Au terme de leur séjour, les pèlerins parfaits « s’endorment sur le premier cercle de Havona, mais se réveillent sur les rives du Paradis ».","ref":"26:11.6"}]},{"n":6,"titre":"Familles de personnalités","page":"familles-de-personnalites.html","ancre":"","questions":[{"q":"Selon le livre, d’après quoi les êtres vivants sont-ils classés au Paradis ?","choix":["D’après leurs relations avec les Déités du Paradis","D’après leur rang dans le gouvernement des superunivers","D’après la date de leur création","D’après leur planète natale"],"bonne":0,"explication":"Au Paradis, les êtres vivants sont classés selon leurs relations, inhérentes ou atteintes, avec les Déités ; lors des grands rassemblements, on les groupe souvent par origine trine, duelle ou unique.","ref":"30:1.1"},{"q":"Selon le livre, en combien de grandes divisions la famille divine des êtres vivants est-elle enregistrée sur Uversa ?","choix":["Trois","Cinq","Dix","Sept"],"bonne":3,"explication":"Le registre d’Uversa compte sept grandes divisions, des Déités du Paradis jusqu’au Corps de Citoyenneté Permanente.","ref":"30:2.1–8"},{"q":"Selon le livre, quels Fils sont les bâtisseurs et les chefs des univers locaux ?","choix":["Les Fils Magistraux (Avonals)","Les Fils Melchizédeks","Les Fils Instructeurs de la Trinité","Les Fils Créateurs (Micaëls)"],"bonne":3,"explication":"D’origine duelle, incorporant les caractéristiques du Père et du Fils, les Fils Créateurs sont « les bâtisseurs et les chefs des univers locaux du temps et de l’espace ».","ref":"21:0.1"},{"q":"Selon le livre, qui crée les séraphins ?","choix":["L’Esprit-Mère de l’univers","Le Fils Créateur seul","Les Anciens des Jours","Les Porteurs de Vie"],"bonne":0,"explication":"Le texte l’affirme : « Les séraphins sont créés par l’Esprit-Mère de l’univers », dans son premier effort solitaire de reproduction d’esprits.","ref":"38:1.1"},{"q":"Selon le livre, quels mortels sont seuls enrôlés dans le Corps des Mortels de la Finalité ?","choix":["Les mortels fusionnés avec l’Esprit","Les mortels fusionnés avec le Père","Les mortels fusionnés avec le Fils"],"bonne":1,"explication":"Parmi toutes les créatures du grand univers, « seuls les individus qui ont fusionné avec le Père sont enrôlés dans le Corps des Mortels de la Finalité ».","ref":"30:4.31"}]},{"n":7,"titre":"Concepts en schémas","page":"concepts-en-schemas.html","ancre":"","questions":[{"q":"Selon le livre, quelle réalité nait de l’Ajusteur, qui en est le père, et du mental matériel, qui en est la mère ?","choix":["La personnalité","Le corps","L’âme","Le Saint-Esprit"],"bonne":2,"explication":"Quand la créature choisit de faire la volonté du Père, l’esprit intérieur devient le père d’une nouvelle réalité, l’âme morontielle, dont le mental matériel est la mère.","ref":"0:5.10"},{"q":"Selon le livre, laquelle de ces trois influences d’esprit habite le mental humain ?","choix":["L’Esprit de Vérité","Le Saint-Esprit","L’Ajusteur de Pensée"],"bonne":2,"explication":"Les Ajusteurs habitent le mental mortel comme partie intégrante de ce mental ; l’esprit du Fils Créateur et celui de l’Esprit-Mère ne l’habitent pas ainsi.","ref":"34:5.6 ; 194:2.11"},{"q":"Selon le livre, quel est le plus élevé des sept esprits-mentaux adjuvats ?","choix":["L’esprit d’adoration","L’esprit de connaissance","L’esprit d’intuition","L’esprit de sagesse"],"bonne":3,"explication":"Le septième adjuvat, l’esprit de sagesse, est « le plus élevé des sept » : c’est lui qui coordonne et articule le travail de tous les autres.","ref":"36:5.12"},{"q":"Selon le livre, à partir de quel cercle psychique l’Ajusteur peut-il, en général, parler directement avec l’être humain ?","choix":["Le premier","Le troisième","Le cinquième","Le septième"],"bonne":0,"explication":"« Généralement, l’Ajusteur ne peut parler directement et immédiatement avec vous avant que vous ayez atteint le premier cercle », le cercle final d’accomplissement progressif.","ref":"110:6.15"},{"q":"Selon le livre, où se situe la morontia ?","choix":["Au-delà du niveau spirituel","Entre le matériel et le spirituel","Au-dessous du niveau matériel","Au niveau absolu du Paradis"],"bonne":1,"explication":"La morontia désigne « un vaste niveau intermédiaire entre le matériel et le spirituel » ; la chaine du tissu morontiel est spirituelle, sa trame matérielle.","ref":"0:5.12"}]},{"n":8,"titre":"Dieu et la Déité","page":"dieu-et-deite.html","ancre":"","questions":[{"q":"Selon le livre, que dénote toujours le mot « Dieu » ?","choix":["La personnalité","Une force impersonnelle","L’Ile du Paradis","L’énergie-matière"],"bonne":0,"explication":"Le texte distingue les deux mots : « Le mot Dieu dénote toujours la personnalité », alors que le mot Déité peut se référer ou non à des personnalités.","ref":"0:2.10"},{"q":"Selon le livre, quelle réalité non personnelle est la source effective des univers physiques ?","choix":["L’Ile du Paradis","Le Fils Éternel","Les Sept Maitres Esprits","L’Absolu de Déité"],"bonne":0,"explication":"Dérivée de la Déité sans qu’on puisse la dire Déité, l’Ile est, dit le texte, « la source effective des univers physiques — passés, présents et futurs ».","ref":"0:4.12"},{"q":"Selon le livre, à qui revient l’application de la loi, c’est-à-dire la justice ?","choix":["Au Père Universel seul","Au Fils Éternel seul","À l’Esprit Infini seul","À la Trinité du Paradis"],"bonne":3,"explication":"Le Père est l’origine de la loi, le Fils l’administre, l’Esprit la révèle ; quant à son application, la justice, elle « tombe dans le domaine de la Trinité du Paradis ».","ref":"10:6.1"},{"q":"Selon le livre, quelle Déité est « le Dieu du temps et de l’espace », qui s’actualise ou évolue ?","choix":["Dieu le Suprême","Dieu l’Ultime","Dieu l’Absolu","Le Fils Éternel"],"bonne":0,"explication":"Dieu le Suprême est « le Dieu du temps et de l’espace, s’actualisant ou évoluant », le Dieu expérientiel des créatures évolutionnaires.","ref":"0:2.15"},{"q":"Selon le livre, quel Absolu unifie le déifié et le non déifié ?","choix":["L’Absolu de Déité","L’Absolu Universel","L’Absolu Non Qualifié"],"bonne":1,"explication":"Septième des Absolus, l’Absolu Universel unifie le déifié et le non déifié et met en corrélation l’absolu et le relatif.","ref":"105:3.8"}]},{"n":9,"titre":"La destinée humaine","page":"destinee-humaine.html","ancre":"","questions":[{"q":"Selon le livre, de qui l’Ajusteur de Pensée émane-t-il directement ?","choix":["De l’Esprit-Mère de l’univers local","Du Fils Créateur","Des Sept Maitres Esprits","Du Père Universel"],"bonne":3,"explication":"Tous s’accordent sur leur origine : les Ajusteurs émanent directement du Père Universel ; ce ne sont pas des êtres créés, mais des entités de fragmentation, présence factuelle du Dieu infini.","ref":"107:1.2"},{"q":"Selon le livre, après quel évènement l’Ajusteur de Pensée est-il affecté à l’enfant ?","choix":["Sa naissance","Ses premiers mots","Sa première décision morale","Son entrée dans l’âge adulte"],"bonne":2,"explication":"Les Ajusteurs se portent volontaires, mais ne sont affectés qu’après la première décision morale de l’enfant ; sur Urantia, ils arrivent en moyenne juste avant six ans.","ref":"108:2.1"},{"q":"Selon le livre, combien d’espèces de morts faut-il distinguer pour la survie de la personnalité ?","choix":["Une seule","Trois","Deux","Sept"],"bonne":1,"explication":"On ne reconnait d’ordinaire qu’une mort, la cessation physique, mais le texte en distingue trois : spirituelle (de l’âme), intellectuelle (du mental) et physique (corps et mental).","ref":"112:3.1–4"},{"q":"Selon le livre, à la mort, à qui l’âme morontielle est-elle confiée ?","choix":["À l’Ajusteur de Pensée","Aux médians","Au Prince Planétaire","Au gardien séraphique de la destinée"],"bonne":3,"explication":"À la mort, le corps retourne au monde élémental, l’Ajusteur part pour Divinington avec la mémoire transcrite, et l’âme morontielle est confiée au gardien de la destinée.","ref":"112:3.5"},{"q":"Selon le livre, qu’est-ce qui constitue la résurrection des survivants endormis ?","choix":["La réunion de l’âme morontielle et de l’Ajusteur","La réunion du corps physique et du mental matériel","L’union de l’âme et de son gardien séraphique","Le retour de l’Ajusteur dans un autre mental"],"bonne":0,"explication":"La résurrection des survivants endormis est la réunion de l’âme morontielle, confiée aux séraphins, et du mental spirituel confié à l’Ajusteur, qui reconstitue la personnalité.","ref":"47:3.3"}]},{"n":10,"titre":"L’histoire d’Urantia","page":"histoire-d-urantia.html","ancre":"","questions":[{"q":"Selon le livre, qui implanta la vie sur Urantia, il y a 550 millions d’années ?","choix":["Les médians","Les séraphins","Les Porteurs de Vie","Les Fils Matériels"],"bonne":2,"explication":"Il y a 550 millions d’années, les Porteurs de Vie revinrent sur Urantia et implantèrent les modèles originels de vie dans les eaux de la planète.","ref":"58:4.2"},{"q":"Selon le livre, comment s’appelaient les deux premiers êtres humains ?","choix":["Adam et Ève","Andon et Fonta","Van et Amadon","Caïn et Abel"],"bonne":1,"explication":"Le message des archanges reconnaissant Urantia comme monde habité annonçait que « les parents de cette nouvelle race seront appelés Andon et Fonta ».","ref":"63:0.1–2"},{"q":"Selon le livre, de quelle famille descendent les six races de couleur d’Urantia ?","choix":["La famille Sangik","La famille de Nod","La famille d’Adam et Ève","La famille de Van"],"bonne":0,"explication":"Chez les Badonites des hautes terres, un couple eut des enfants exceptionnellement intelligents : « Ce fut la famille Sangik, ancêtre des six races colorées d’Urantia ».","ref":"64:5.2"},{"q":"Selon le livre, qu’arriva-t-il à Dalamatia, la cité du Prince Planétaire, après la rébellion ?","choix":["Elle devint la cité de Babel","Un raz de marée l’engloutit","Les Andites l’incendièrent","Elle fut ensevelie sous les glaces"],"bonne":1,"explication":"Cent-soixante-deux ans après la rébellion, un raz de marée balaya Dalamatia, et le quartier général planétaire s’enfonça au-dessous du niveau de la mer.","ref":"67:5.4"},{"q":"Selon le livre, où se trouvait le premier Jardin d’Éden, préparé pour Adam et Ève ?","choix":["Sur une ile du golfe Persique","Près du lac Van","Au sud-est de la mer Caspienne","Sur une péninsule de la côte orientale de la Méditerranée"],"bonne":3,"explication":"Parmi trois sites proposés, dont une ile du golfe Persique, le comité choisit presque à l’unanimité une longue péninsule étroite de la côte orientale de la Méditerranée.","ref":"73:3.1–2"}]},{"n":11,"titre":"La rébellion de Lucifer","page":"rebellion-de-lucifer.html","ancre":"","questions":[{"q":"Selon le livre, quelle fonction Lucifer exerçait-il avant sa rébellion ?","choix":["Souverain du système de Satania","Prince Planétaire d’Urantia","Fils Créateur de Nébadon","Très Haut Père de la constellation"],"bonne":0,"explication":"Depuis Jérusem, Lucifer administrait un grand système de 607 mondes habités ; le texte l’appelle « le Souverain déchu et déposé de Satania ».","ref":"53:1.1 ; 53:1.3"},{"q":"Selon le livre, que prétendait Lucifer au sujet du Père Universel dans son manifeste ?","choix":["Qu’il punissait trop durement les mortels","Qu’il n’existait pas réellement","Qu’il avait confié Nébadon à Gabriel","Qu’il avait abandonné Satania"],"bonne":1,"explication":"La première rubrique de la Déclaration de Liberté affirmait que le Père Universel n’existait pas réellement et qu’il était « un mythe inventé par les Fils du Paradis ».","ref":"53:3.1–2"},{"q":"Selon le livre, quel Prince Planétaire d’Urantia suivit Lucifer dans la rébellion ?","choix":["Caligastia","Van","Machiventa Melchizédek","Lanaforge"],"bonne":0,"explication":"Lors d’une inspection, Satan informa Caligastia de la Déclaration de Liberté de Lucifer, et le Prince accepta de trahir la planète dès que la rébellion serait annoncée.","ref":"67:1.1–2"},{"q":"Selon le livre, pourquoi Urantia est-elle une planète isolée ?","choix":["Parce qu’Adam et Ève ont échoué dans leur mission","Parce qu’elle est trop éloignée de Jérusem","Parce qu’elle n’a jamais reçu d’Ajusteurs de Pensée","Parce que son Prince Planétaire a suivi Lucifer dans la rébellion"],"bonne":3,"explication":"Comme Urantia suivit son Prince dans la rébellion, les circuits aboutissant aux mondes déchus furent coupés, pour que Lucifer ne puisse pas les employer à propager son plan.","ref":"53:7.3 ; 67:2.3"},{"q":"Selon le livre, où se trouvait Lucifer à l’époque où les fascicules furent rédigés ?","choix":["Caché sur Urantia","Réhabilité sur Édentia","Prisonnier sur un satellite des sphères du Père, autour de Jérusem","En exil sur Panoptia"],"bonne":2,"explication":"Quand Micaël devint le chef confirmé de Nébadon, les agents des Anciens des Jours emprisonnèrent Lucifer, resté depuis prisonnier sur le satellite numéro 1 des sphères du Père entourant Jérusem.","ref":"53:9.2"}]},{"n":12,"titre":"La vie de Jésus","page":"vie-de-jesus.html","ancre":"","questions":[{"q":"Selon le livre, dans quelle ville Joseph et Marie se réfugièrent-ils avec Jésus pour échapper au massacre des enfants de Bethléem ?","choix":["Alexandrie","Damas","Rome","Jéricho"],"bonne":0,"explication":"Prévenus par un messager de Zacharie, Joseph et Marie quittèrent Bethléem la nuit avant le massacre et séjournèrent deux années entières à Alexandrie, en Égypte.","ref":"122:10.4"},{"q":"Selon le livre, avec qui Jésus fit-il son voyage autour du monde romain, en l’an 22 et en l’an 23 ?","choix":["Gonod et son fils Ganid","Pierre et André","Zébédée et ses fils","Lazare et ses sœurs"],"bonne":0,"explication":"Jésus quitta Jérusalem le 26 avril de l’an 22 avec deux natifs des Indes, Gonod et son fils Ganid, et leur fit ses adieux à Charax en l’an 23.","ref":"130:0.1"},{"q":"Selon le livre, qui Jean baptisa-t-il dans le Jourdain en même temps que Jésus ?","choix":["Philippe et Nathanael","Pierre et André","Nicodème et Joseph d’Arimathie","Ses frères Jacques et Jude"],"bonne":3,"explication":"À midi, le 14 janvier de l’an 26, Jean baptisa dans le Jourdain Jésus et ses deux frères, Jacques et Jude.","ref":"135:8.6"},{"q":"Selon le livre, quel jour Jésus sortit-il du tombeau sous sa forme morontielle ?","choix":["Le vendredi 7 avril de l’an 30","Le dimanche 9 avril de l’an 30","Le mardi 4 avril de l’an 30","Le jeudi 18 mai de l’an 30"],"bonne":1,"explication":"À trois heures deux minutes, « ce dimanche 9 avril de l’an 30 », la forme morontielle ressuscitée de Jésus sortit du tombeau neuf de Joseph d’Arimathie.","ref":"189:1.1"},{"q":"Selon le livre, combien de croyants étaient en prière quand vint l’Esprit de Vérité, le jour de la Pentecôte ?","choix":["Douze","Soixante-dix","Cent-vingt","Cinq-cents"],"bonne":2,"explication":"Le jour de la Pentecôte, vers une heure de l’après-midi, les cent-vingt croyants en prière perçurent une présence étrange, que Pierre reconnut comme la venue de l’Esprit de Vérité.","ref":"194:0.1–2 ; 194:1.1"}]},{"n":13,"titre":"La Bible et le Livre d’Urantia","page":"bible-et-livre.html","ancre":"","questions":[{"q":"Selon le Livre d’Urantia, qui était le père de Caïn ?","choix":["Van","Cano","Nod","Sérapatatia"],"bonne":1,"explication":"Pour le livre, Caïn n’était pas le fils d’Adam : son père, de race nodite, était Cano, « le père de Caïn encore à naitre ».","ref":"75:5.3 ; 76:2.4"},{"q":"Selon le Livre d’Urantia, quelle inondation Noé a-t-il connue ?","choix":["Le raz de marée qui engloutit Dalamatia","Une crue du fleuve qui emporta son village","L’engloutissement de la péninsule d’Éden"],"bonne":1,"explication":"Le livre écarte tout déluge universel depuis l’établissement de la vie : une crue annuelle, accrue par de fortes pluies, emporta le village de Noé, sauvé avec sa proche famille.","ref":"78:7.4–5"},{"q":"Selon le Livre d’Urantia, d’où vient le nom de Babel ?","choix":["De Bablot, architecte et bâtisseur de la tour","De Nod, chef des Nodites","De Daligastia, associé du Prince","De Dilmun, la cité des Nodites"],"bonne":0,"explication":"La nouvelle ville devait porter le nom de Bablot, architecte et bâtisseur de la tour ; le site s’appela plus tard Bablod, puis Babel.","ref":"77:3.3"},{"q":"Selon le Livre d’Urantia, sur quoi s’est construite la légende de l’étoile de Bethléem ?","choix":["Le passage d’une comète","L’explosion d’une étoile lointaine","Des conjonctions de Jupiter et de Saturne","Une aurore boréale"],"bonne":2,"explication":"« Ces hommes sages ne virent pas d’étoile pour les guider vers Bethléem » : la légende naquit de trois conjonctions de Jupiter et de Saturne, en l’an 7 av. J.-C.","ref":"122:8.7"},{"q":"Selon le Livre d’Urantia, quel est le seul miracle de la nature que Jésus accomplit après l’avoir sciemment projeté ?","choix":["Les noces de Cana","La tempête apaisée","La multiplication des pains","La pêche au bord du lac"],"bonne":2,"explication":"Pour le repas d’environ cinq-mille personnes, le texte parle du « premier et unique miracle de la nature que Jésus accomplit après l’avoir sciemment projeté ».","ref":"152:2.9–10"}]}]};
  if (!DONNEES || !DONNEES.etapes || !DONNEES.etapes.length || !document.querySelector || !document.addEventListener) return;

  var NB = ' ', FINE = ' ';
  // noms des sources maîtresses (visuels/source) -> nom de la page dans le site
  var ALIAS = { 'nebadon-orvonton.html': 'nebadon-dans-orvonton.html', 'concepts.html': 'concepts-en-schemas.html',
    'urantia-paradis-3d.html': 'atlas-3d.html', 'urantia-paradis-3d.src.html': 'atlas-3d.html', 'accueil.html': 'index.html' };
  // vue 3D : ancre de l’étape -> bouton du mode
  var MODES_3D = { gouvernement: 't-gov', frise: 't-time', carriere: 't-asc' };
  var SVGNS = 'http://www.w3.org/2000/svg';
  var ICONES = { ok: 'M4 10.6l3.9 3.9L16.2 6', ko: 'M5.5 5.5l9 9M14.5 5.5l-9 9' };

  var ETAPES = DONNEES.etapes.filter(function (e) { return e && e.questions && e.questions.length; });
  if (!ETAPES.length) return;
  var TOTAL = DONNEES.etapes.length;

  function el(tag, cls, txt) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (txt !== undefined && txt !== null) e.textContent = txt;
    return e;
  }
  function icone(nom) {
    var s = document.createElementNS(SVGNS, 'svg');
    s.setAttribute('viewBox', '0 0 20 20');
    s.setAttribute('aria-hidden', 'true');
    s.setAttribute('focusable', 'false');
    s.setAttribute('class', 'qz-ic');
    var p = document.createElementNS(SVGNS, 'path');
    p.setAttribute('d', ICONES[nom]);
    p.setAttribute('fill', 'none');
    p.setAttribute('stroke', 'currentColor');
    p.setAttribute('stroke-width', '2.4');
    p.setAttribute('stroke-linecap', 'round');
    p.setAttribute('stroke-linejoin', 'round');
    s.appendChild(p);
    return s;
  }
  function ref(r) { return el('span', 'ref', r); }
  function focaliser(e) { if (!e) return; try { e.focus({ preventScroll: true }); } catch (x) { e.focus(); } }
  function nombre(n) { return n === 5 ? 'Cinq' : String(n); }

  // ── Quelle(s) étape(s) pour cette page ────────────────────────────────────────────────────────────
  function nomFichier() {
    var f = '';
    try { f = decodeURIComponent((location.pathname || '').split('/').pop() || ''); } catch (x) { f = ''; }
    f = (f || 'index.html').toLowerCase();
    return ALIAS[f] || f;
  }
  function parNumeros(v) {
    var ns = String(v).split(/[\s,;]+/).map(Number);
    return ETAPES.filter(function (e) { return ns.indexOf(e.n) >= 0; });
  }

  // ── Styles (jetons de couleur de la page, avec des valeurs de repli lisibles) ─────────────────────
  function styles() {
    if (document.getElementById('quiz-atlas-css')) return;
    var st = el('style');
    st.id = 'quiz-atlas-css';
    var sombre = '--qz-ok:#6FD49A;--qz-ok-soft:#12291D;--qz-ko:#FF8A80;--qz-ko-soft:#331716;--qz-on:#0C1120;';
    st.textContent =
      '.qz{--qz-bg:var(--sheet,#FFFFFF);--qz-fond:var(--paper,#EEF1F6);--qz-ink:var(--ink,#18213B);--qz-muted:var(--muted,#56607D);' +
      '--qz-rule:var(--rule,#CBD2E0);--qz-acc:var(--gold-ink,#8A5A00);--qz-ui:var(--gold,#C98A12);--qz-on-ui:var(--on-gold,#1B1405);' +
      '--qz-ok:#17703F;--qz-ok-soft:#E5F4EA;--qz-ko:#B3261E;--qz-ko-soft:#FBE9E7;--qz-on:#FFFFFF;' +
      'color:var(--qz-ink);font-family:var(--font-body,"Alegreya Sans","Segoe UI",Arial,sans-serif)}' +
      '@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .qz{' + sombre + '}}' +
      ':root[data-theme="dark"] .qz,.qz.qz-nuit{' + sombre + '}' +
      '.qz.qz-nuit{--qz-bg:var(--panel-solid,#0D1224);--qz-fond:#070A16;--qz-ink:var(--ink,#E8EBF5);--qz-muted:var(--muted,#A4ADC8);' +
      '--qz-rule:var(--panel-line,rgba(160,175,220,.24));--qz-acc:var(--gold-ink,#F6C766);--qz-ui:var(--gold,#F0B33C);--qz-on-ui:var(--on-gold,#1B1405);color-scheme:dark}' +
      '.qz *,.qz *::before,.qz *::after{box-sizing:border-box}' +
      '.qz [hidden]{display:none!important}' +
      'section.qz{max-width:52rem;background:var(--qz-bg);border:1px solid var(--qz-rule);border-top:4px solid var(--qz-ui);border-radius:14px;' +
      'padding:22px 24px 24px;display:grid;gap:16px;scroll-margin-top:12px}' +
      '.qz-sur{margin:0;font:500 .76rem/1.3 var(--font-mono,ui-monospace,Consolas,monospace);letter-spacing:.12em;text-transform:uppercase;color:var(--qz-muted)}' +
      '.qz-titre{margin:0;font:600 clamp(1.7rem,3.4vw,2.3rem)/1.1 var(--font-display,"Cormorant Garamond",Georgia,serif);color:var(--qz-ink)}' +
      '.qz-intro{margin:0;color:var(--qz-muted);font-size:1rem;line-height:1.5;max-width:62ch}' +
      '.qz-tete{display:grid;gap:8px}' +
      '.qz-points{list-style:none;margin:0;padding:0;display:flex;gap:6px;scroll-margin-top:16px}' +
      '.qz-points li{width:26px;height:6px;border-radius:999px;background:var(--qz-rule)}' +
      '.qz-points li.cur{background:var(--qz-ui)}.qz-points li.ok{background:var(--qz-ok)}.qz-points li.ko{background:var(--qz-ko)}' +
      '.qz-form{margin:0;display:grid;gap:14px}' +
      '.qz-fs{margin:0;padding:0;border:0;min-width:0}' +
      '.qz-legend{float:left;width:100%;padding:0;margin:0 0 12px;display:grid;gap:4px}' +
      '.qz-num{font:500 .74rem/1.3 var(--font-mono,ui-monospace,Consolas,monospace);letter-spacing:.1em;text-transform:uppercase;color:var(--qz-acc)}' +
      '.qz-q{font:600 1.32rem/1.3 var(--font-display,"Cormorant Garamond",Georgia,serif);color:var(--qz-ink);text-wrap:pretty}' +
      '.qz-choix{clear:both;display:grid;gap:8px}' +
      '.qz-opt{display:grid;grid-template-columns:1.3rem minmax(0,1fr) auto;gap:4px 12px;align-items:center;min-height:48px;padding:10px 14px;' +
      'border:1px solid var(--qz-rule);border-radius:10px;background:var(--qz-fond);color:var(--qz-ink);font-size:1.02rem;line-height:1.35;cursor:pointer;' +
      'transition:border-color .15s ease,background-color .15s ease}' +
      '.qz-opt:hover{border-color:var(--qz-muted)}' +
      '.qz-opt input{appearance:none;-webkit-appearance:none;margin:0;width:1.3rem;height:1.3rem;border:2px solid var(--qz-muted);border-radius:50%;' +
      'background:var(--qz-bg);display:grid;place-items:center;cursor:pointer}' +
      '.qz-opt input::after{content:"";width:.6rem;height:.6rem;border-radius:50%;background:var(--qz-ui);transform:scale(0);transition:transform .12s ease}' +
      '.qz-opt input:checked{border-color:var(--qz-ui)}.qz-opt input:checked::after{transform:scale(1)}' +
      '.qz-opt input:focus-visible{outline:2px solid var(--qz-acc);outline-offset:3px}' +
      '.qz-opt.choisi{border-color:var(--qz-ui);background:var(--qz-bg)}' +
      '.qz-opt .qz-et{display:none;align-items:center;gap:4px;font:600 .8rem/1.2 var(--font-body,inherit);white-space:nowrap}' +
      '.qz-ic{width:1.1rem;height:1.1rem;flex:none}' +
      '.qz-fini .qz-opt{cursor:default}.qz-fini .qz-opt:hover{border-color:var(--qz-rule)}' +
      '.qz-fini .qz-opt input{cursor:default}' +
      '.qz-opt.bonne{border-color:var(--qz-ok);background:var(--qz-ok-soft)}.qz-opt.bonne .qz-et{display:inline-flex;color:var(--qz-ok)}' +
      '.qz-opt.bonne input{border-color:var(--qz-ok)}.qz-opt.bonne input::after{background:var(--qz-ok)}' +
      '.qz-opt.fausse{border-color:var(--qz-ko);background:var(--qz-ko-soft)}.qz-opt.fausse .qz-et{display:inline-flex;color:var(--qz-ko)}' +
      '.qz-opt.fausse input{border-color:var(--qz-ko)}.qz-opt.fausse input::after{background:var(--qz-ko)}' +
      '.qz-retour{display:grid;gap:6px}.qz-retour:empty{display:none}' +
      '.qz-verdict{margin:0;display:flex;align-items:flex-start;gap:8px;font-weight:700;font-size:1.05rem;line-height:1.35}' +
      '.qz-verdict.ok{color:var(--qz-ok)}.qz-verdict.ko{color:var(--qz-ko)}.qz-verdict.info{color:var(--qz-ink);font-weight:600}' +
      '.qz-verdict .qz-ic{width:1.35rem;height:1.35rem;margin-top:.02rem}' +
      '.qz-verdict b{font-weight:700;color:var(--qz-ink)}' +
      '.qz-expl{margin:0;line-height:1.5;max-width:66ch}' +
      '.qz .ref{font-family:var(--font-mono,ui-monospace,Consolas,monospace);font-size:.8em;font-style:normal;color:var(--qz-muted);letter-spacing:0;white-space:nowrap}' +
      '.qz .ref a.ref-lien{display:inline-block;padding-block:13px;margin-block:-13px}' +
      '.qz-actions{display:flex;flex-wrap:wrap;gap:10px;align-items:center}' +
      '.qz-btn{appearance:none;display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:44px;padding:10px 20px;border-radius:999px;' +
      'border:1px solid var(--qz-ink);background:var(--qz-ink);color:var(--qz-bg);font:600 1rem/1.25 var(--font-body,inherit);cursor:pointer}' +
      '.qz-btn:hover{background:var(--qz-acc);border-color:var(--qz-acc)}' +
      '.qz-btn:focus-visible,.qz-onglets button:focus-visible,.qz-x:focus-visible,.qz-fin:focus-visible{outline:2px solid var(--qz-acc);outline-offset:3px}' +
      '.qz-fin{display:grid;gap:14px;border-radius:10px}' +
      '.qz-fin:focus{outline:none}' +
      '.qz-score{margin:0;display:flex;align-items:baseline;flex-wrap:wrap;gap:6px 14px}' +
      '.qz-score b{font:600 3rem/1 var(--font-display,"Cormorant Garamond",Georgia,serif);color:var(--qz-ink)}' +
      '.qz-score span{font-size:1.05rem;color:var(--qz-muted)}' +
      '.qz-mot{margin:0;font-weight:700;font-size:1.1rem}' +
      '.qz-bilan-t{margin:4px 0 0;font:500 .74rem/1.3 var(--font-mono,ui-monospace,Consolas,monospace);letter-spacing:.1em;text-transform:uppercase;color:var(--qz-muted)}' +
      '.qz-bilan{list-style:none;margin:0;padding:0;display:grid;gap:8px}' +
      '.qz-bilan li{display:grid;grid-template-columns:1.4rem minmax(0,1fr);gap:2px 10px;align-items:start;padding:10px 12px;border:1px solid var(--qz-rule);' +
      'border-radius:10px;background:var(--qz-fond);font-size:.96rem;line-height:1.4}' +
      '.qz-bilan .qz-ic{width:1.25rem;height:1.25rem;margin-top:1px}' +
      '.qz-bilan li.ok .qz-ic{color:var(--qz-ok)}.qz-bilan li.ko .qz-ic{color:var(--qz-ko)}' +
      '.qz-bilan .qz-bq{font-weight:600}.qz-bilan .qz-br{color:var(--qz-muted)}.qz-bilan .qz-br b{color:var(--qz-ink);font-weight:600}' +
      '.qz-sr{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}' +
      /* vue 3D : entrée du menu et boite de dialogue */
      '.qz-menu{margin:10px 0 4px}' +
      '.qz-menu .qz-ouvrir{appearance:none;display:grid;gap:1px;width:100%;min-height:44px;padding:8px 10px;border:1px solid var(--panel-line,rgba(160,175,220,.24));' +
      'border-radius:10px;background:transparent;color:var(--gold-ink,#F6C766);font:600 .95rem/1.25 var(--font-body,inherit);text-align:left;cursor:pointer}' +
      '.qz-menu .qz-ouvrir span{font-weight:400;font-size:.84rem;color:var(--muted,#A4ADC8)}' +
      '.qz-menu .qz-ouvrir:hover{border-color:var(--gold,#F0B33C)}' +
      '.qz-menu .qz-ouvrir:focus-visible{outline:2px solid var(--gold-ink,#F6C766);outline-offset:2px}' +
      'dialog.qz-dlg{width:min(42rem,calc(100vw - 16px));max-width:none;max-height:calc(100vh - 16px);max-height:calc(100dvh - 16px);margin:auto;padding:0;' +
      'border:1px solid var(--qz-rule);border-radius:16px;background:var(--qz-bg);color:var(--qz-ink);box-shadow:0 18px 60px rgba(0,0,0,.5);overflow:hidden}' +
      'dialog.qz-dlg[open]{display:flex;flex-direction:column}' +
      'dialog.qz-dlg::backdrop{background:rgba(3,5,12,.66)}' +
      '.qz-dlg-h{display:flex;align-items:flex-start;justify-content:space-between;gap:12px;padding:16px 16px 10px 22px;border-bottom:1px solid var(--qz-rule)}' +
      '.qz-dlg-h .qz-titre{font-size:clamp(1.5rem,5vw,1.9rem)}' +
      '.qz-x{appearance:none;flex:none;width:44px;height:44px;border:1px solid var(--qz-rule);border-radius:999px;background:transparent;color:var(--qz-ink);' +
      'font:400 1.5rem/1 var(--font-body,inherit);cursor:pointer}' +
      '.qz-x:hover{border-color:var(--qz-muted)}' +
      '.qz-dlg-c{overflow:auto;overscroll-behavior:contain;padding:14px 22px 22px;display:grid;gap:16px}' +
      '.qz-dlg section.qz{max-width:none;border:0;border-radius:0;padding:0;background:transparent}' +
      '.qz-onglets{display:flex;flex-wrap:wrap;gap:6px}' +
      '.qz-onglets button{appearance:none;min-height:44px;padding:8px 14px;border:1px solid var(--qz-rule);border-radius:999px;background:transparent;' +
      'color:var(--qz-ink);font:500 .92rem/1.2 var(--font-body,inherit);cursor:pointer}' +
      '.qz-onglets button:hover{border-color:var(--qz-muted)}' +
      '.qz-onglets button[aria-pressed="true"]{background:var(--qz-ui);border-color:var(--qz-ui);color:var(--qz-on-ui);font-weight:700}' +
      '@media (max-width:560px){section.qz{padding:18px 16px 20px}.qz-q{font-size:1.2rem}.qz-opt{padding:10px 12px;gap:4px 10px}' +
      '.qz-dlg-h{padding:12px 10px 8px 16px}.qz-dlg-c{padding:12px 16px 18px}}' +
      '@media (prefers-reduced-motion:reduce){.qz-opt,.qz-opt input::after{transition:none}}' +
      '@media (forced-colors:active){.qz-opt.bonne,.qz-opt.fausse{border-width:3px}.qz-points li{border:1px solid CanvasText}}' +
      '@media print{.qz,.qz-menu{display:none!important}}';
    document.head.appendChild(st);
  }

  // ── Un quiz (une étape) dans un conteneur ─────────────────────────────────────────────────────────
  // opts : { titre: true|false (titre et intro du bloc), dialogue: true|false }
  function Quiz(racine, etape, opts) {
    var Q = etape.questions, n = Q.length, i = 0, reponses = [], etat = 'question';
    var id = 'qz-' + etape.n + (opts.dialogue ? '-d' : '');
    racine.textContent = '';
    if (opts.titre) {
      var tete = el('div', 'qz-tete');
      tete.appendChild(el('p', 'qz-sur', 'Étape ' + etape.n + ' sur ' + TOTAL + ' · ' + etape.titre));
      var h = el('h2', 'qz-titre', 'Teste tes connaissances');
      h.id = id + '-titre';
      tete.appendChild(h);
      tete.appendChild(el('p', 'qz-intro', nombre(n) + ' questions sur ce que montre cette page, selon le livre. ' +
        'Après chaque réponse, une explication renvoie au passage du livre.'));
      racine.appendChild(tete);
      racine.setAttribute('aria-labelledby', h.id);
    } else {
      racine.appendChild(el('p', 'qz-intro', nombre(n) + ' questions sur «' + NB + etape.titre + NB + '», selon le livre. ' +
        'Après chaque réponse, une explication renvoie au passage du livre.'));
    }
    var points = el('ol', 'qz-points');
    points.setAttribute('aria-hidden', 'true');
    for (var k = 0; k < n; k++) points.appendChild(el('li'));
    racine.appendChild(points);
    var zone = el('div', 'qz-zone');
    racine.appendChild(zone);

    function majPoints() {
      Array.prototype.forEach.call(points.children, function (li, j) {
        li.className = j < reponses.length ? (reponses[j] === Q[j].bonne ? 'ok' : 'ko') : (j === i && etat !== 'fin' ? 'cur' : '');
      });
    }

    function afficherQuestion(focus) {
      etat = 'question';
      var q = Q[i];
      zone.textContent = '';
      var form = el('form', 'qz-form');
      form.setAttribute('novalidate', '');
      var fs = el('fieldset', 'qz-fs');
      var lg = el('legend', 'qz-legend');
      lg.appendChild(el('span', 'qz-num', 'Question ' + (i + 1) + ' sur ' + n));
      lg.appendChild(el('span', 'qz-q', q.q));
      fs.appendChild(lg);
      var choix = el('div', 'qz-choix');
      var radios = [];
      q.choix.forEach(function (c, j) {
        var lab = el('label', 'qz-opt');
        var r = el('input');
        r.type = 'radio';
        r.name = id + '-r';
        r.value = String(j);
        radios.push(r);
        lab.appendChild(r);
        lab.appendChild(el('span', 'qz-lib', c));
        var et = el('span', 'qz-et');
        lab.appendChild(et);
        r.addEventListener('change', function () {
          radios.forEach(function (x) { x.parentNode.classList.toggle('choisi', x.checked); });
        });
        choix.appendChild(lab);
      });
      fs.appendChild(choix);
      form.appendChild(fs);
      var retour = el('div', 'qz-retour');
      retour.setAttribute('aria-live', 'polite');
      form.appendChild(retour);
      var act = el('div', 'qz-actions');
      var btn = el('button', 'qz-btn', 'Valider');
      btn.type = 'submit';
      act.appendChild(btn);
      form.appendChild(act);
      zone.appendChild(form);
      majPoints();

      form.addEventListener('submit', function (e) {
        e.preventDefault();
        if (etat === 'question') {
          var choisi = -1;
          radios.forEach(function (r, j) { if (r.checked) choisi = j; });
          if (choisi < 0) {
            retour.textContent = '';
            var p = el('p', 'qz-verdict info', 'Choisis une réponse, puis valide.');
            retour.appendChild(p);
            focaliser(radios[0]);
            return;
          }
          corriger(choisi, form, fs, radios, retour, btn);
        } else {
          i++;
          if (i < n) { afficherQuestion(true); defiler(); } else { afficherFin(); }
        }
      });
      if (focus) focaliser(radios[0]);
    }

    function corriger(choisi, form, fs, radios, retour, btn) {
      var q = Q[i], juste = choisi === q.bonne;
      reponses.push(choisi);
      etat = 'corrige';
      // le bouton garde le focus (il change seulement de libellé), puis les choix sont figés
      if (document.activeElement && fs.contains(document.activeElement)) focaliser(btn);
      btn.textContent = i + 1 < n ? 'Question suivante' : 'Voir mon score';
      radios.forEach(function (r, j) {
        var lab = r.parentNode, et = lab.querySelector('.qz-et');
        lab.classList.remove('choisi');
        if (j === q.bonne) {
          lab.classList.add('bonne');
          et.appendChild(icone('ok'));
          et.appendChild(el('span', '', j === choisi ? 'Ta réponse' : 'Bonne réponse'));
        } else if (j === choisi) {
          lab.classList.add('fausse');
          et.appendChild(icone('ko'));
          et.appendChild(el('span', '', 'Ta réponse'));
        }
      });
      fs.disabled = true;
      form.classList.add('qz-fini');
      retour.textContent = '';
      var v = el('p', 'qz-verdict ' + (juste ? 'ok' : 'ko')), vt = el('span');
      v.appendChild(icone(juste ? 'ok' : 'ko'));
      if (juste) vt.textContent = 'Juste' + FINE + '!';
      else {
        vt.appendChild(document.createTextNode('Pas tout à fait. La bonne réponse' + NB + ': '));
        vt.appendChild(el('b', '', q.choix[q.bonne]));
        vt.appendChild(document.createTextNode('.'));
      }
      v.appendChild(vt);
      retour.appendChild(v);
      var x = el('p', 'qz-expl', q.explication + ' ');
      x.appendChild(ref(q.ref));
      retour.appendChild(x);
      majPoints();
    }

    function afficherFin() {
      etat = 'fin';
      var bons = 0;
      reponses.forEach(function (r, j) { if (r === Q[j].bonne) bons++; });
      zone.textContent = '';
      majPoints();
      var fin = el('div', 'qz-fin');
      fin.tabIndex = -1;
      var sc = el('p', 'qz-score');
      sc.appendChild(el('span', 'qz-sr', 'Ton score' + NB + ': '));
      sc.appendChild(el('b', '', bons + ' sur ' + n));
      sc.appendChild(el('span', '', bons === n ? 'toutes les réponses sont justes' : bons + ' réponse' + (bons > 1 ? 's' : '') + ' juste' + (bons > 1 ? 's' : '')));
      fin.appendChild(sc);
      fin.appendChild(el('p', 'qz-mot', bons === n ? 'Sans faute' + NB + ': bravo' + FINE + '!' : bons >= n - 1 ? 'Très bien' + FINE + '!' :
        bons * 2 >= n ? 'Bien' + FINE + '! Les explications ci-dessous complètent le reste.' :
          'Un bon début' + NB + ': relis la page et réessaie quand tu veux.'));
      fin.appendChild(el('p', 'qz-bilan-t', 'Les bonnes réponses'));
      var ol = el('ol', 'qz-bilan');
      Q.forEach(function (q, j) {
        var ok = reponses[j] === q.bonne, li = el('li', ok ? 'ok' : 'ko');
        li.appendChild(icone(ok ? 'ok' : 'ko'));
        var d = el('div');
        d.appendChild(el('span', 'qz-sr', (ok ? 'Juste' : 'Faux') + NB + ': '));
        d.appendChild(el('span', 'qz-bq', q.q));
        var br = el('div', 'qz-br');
        br.appendChild(document.createTextNode('Réponse' + NB + ': '));
        br.appendChild(el('b', '', q.choix[q.bonne]));
        br.appendChild(document.createTextNode(' '));
        br.appendChild(ref(q.ref));
        d.appendChild(br);
        li.appendChild(d);
        ol.appendChild(li);
      });
      fin.appendChild(ol);
      var act = el('div', 'qz-actions');
      var again = el('button', 'qz-btn', 'Recommencer');
      again.type = 'button';
      again.addEventListener('click', function () { i = 0; reponses = []; afficherQuestion(true); defiler(); });
      act.appendChild(again);
      fin.appendChild(act);
      zone.appendChild(fin);
      defiler();
      focaliser(fin);
    }

    // la nouvelle question reste en vue (sans à-coup si l’utilisateur préfère moins d’animations)
    function defiler() {
      if (!points.getBoundingClientRect || !points.scrollIntoView) return;
      var calme = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      var r = points.getBoundingClientRect(), haut = window.innerHeight || 800;
      if (!opts.dialogue && r.top >= 0 && r.top <= haut * 0.5) return;
      try { points.scrollIntoView({ behavior: calme ? 'auto' : 'smooth', block: opts.dialogue ? 'nearest' : 'start' }); } catch (x) { points.scrollIntoView(true); }
    }

    afficherQuestion(false);
  }

  // ── Pages 2D : le bloc à la fin du contenu ────────────────────────────────────────────────────────
  function blocEnLigne(etapes, conteneur) {
    var etape = etapes[0];
    var sec = el('section', 'qz');
    sec.id = 'teste-tes-connaissances';
    sec.setAttribute('data-glossaire', 'non');
    sec.setAttribute('data-etape-quiz', String(etape.n));
    if (conteneur) { conteneur.appendChild(sec); }
    else {
      var main = document.getElementById('contenu') || document.querySelector('main') || document.body;
      var avant = null;
      for (var c = main.firstElementChild; c; c = c.nextElementSibling) {
        if (c.classList.contains('atlas-suite') || (c.tagName === 'FOOTER' && !avant)) { avant = c; if (c.classList.contains('atlas-suite')) break; }
      }
      if (avant) main.insertBefore(sec, avant); else main.appendChild(sec);
    }
    if (etapes.length > 1) {
      // plusieurs étapes demandées (data-quiz="3,4") : un choix au-dessus du quiz
      var zone = el('div');
      var tabs = onglets(etapes, etape, function (e) { Quiz(zone, e, { titre: false }); });
      sec.appendChild(el('h2', 'qz-titre', 'Teste tes connaissances'));
      sec.appendChild(tabs);
      sec.appendChild(zone);
      Quiz(zone, etape, { titre: false });
    } else {
      Quiz(sec, etape, { titre: true });
    }
  }

  function onglets(etapes, actif, choisir) {
    var g = el('div', 'qz-onglets');
    g.setAttribute('role', 'group');
    g.setAttribute('aria-label', 'Choisir le quiz');
    etapes.forEach(function (e) {
      var b = el('button', '', e.titre);
      b.type = 'button';
      b.setAttribute('aria-pressed', String(e === actif));
      b.addEventListener('click', function () {
        Array.prototype.forEach.call(g.children, function (x) { x.setAttribute('aria-pressed', String(x === b)); });
        choisir(e);
      });
      g.appendChild(b);
    });
    return g;
  }

  // ── Vue 3D : une entrée du menu, une boite de dialogue ────────────────────────────────────────────
  function etapeCourante3D(etapes) {
    var h = (location.hash || '').slice(1).toLowerCase();
    for (var k = 0; k < etapes.length; k++) {
      var a = etapes[k].ancre, b = a && MODES_3D[a] && document.getElementById(MODES_3D[a]);
      if (b && b.getAttribute('aria-pressed') === 'true') return etapes[k];
    }
    for (var m = 0; m < etapes.length; m++) if (etapes[m].ancre && etapes[m].ancre === h) return etapes[m];
    for (var j = 0; j < etapes.length; j++) if (!etapes[j].ancre) return etapes[j];
    return etapes[0];
  }

  function menu3D(etapes, panneau) {
    var dlg = el('dialog', 'qz qz-dlg qz-nuit');
    if (typeof dlg.showModal !== 'function') return false;
    dlg.setAttribute('aria-labelledby', 'qz-dlg-titre');
    dlg.setAttribute('data-glossaire', 'non');
    var h = el('div', 'qz-dlg-h');
    var ht = el('div', 'qz-tete');
    ht.appendChild(el('p', 'qz-sur', 'Vue 3D · ' + etapes.length + ' quiz de ' + etapes[0].questions.length + ' questions'));
    var t = el('h2', 'qz-titre', 'Teste tes connaissances');
    t.id = 'qz-dlg-titre';
    ht.appendChild(t);
    h.appendChild(ht);
    var x = el('button', 'qz-x', '×');
    x.type = 'button';
    x.setAttribute('aria-label', 'Fermer le quiz');
    h.appendChild(x);
    dlg.appendChild(h);
    var corps = el('div', 'qz-dlg-c');
    dlg.appendChild(corps);
    document.body.appendChild(dlg);

    var bloc = el('section', 'qz qz-nuit');
    var origine = null;
    function ouvrir(e) {
      corps.textContent = '';
      var actif = e || etapeCourante3D(etapes);
      corps.appendChild(onglets(etapes, actif, function (k) { Quiz(bloc, k, { titre: false, dialogue: true }); }));
      corps.appendChild(bloc);
      Quiz(bloc, actif, { titre: false, dialogue: true });
      dlg.showModal();
      corps.scrollTop = 0;
      focaliser(corps.querySelector('.qz-onglets [aria-pressed="true"]'));
    }
    x.addEventListener('click', function () { dlg.close(); });
    dlg.addEventListener('click', function (e) { if (e.target === dlg) dlg.close(); });   // clic sur le fond
    // les raccourcis clavier de la vue 3D ne doivent pas agir sous la boite de dialogue
    dlg.addEventListener('keydown', function (e) { e.stopPropagation(); });
    dlg.addEventListener('close', function () { if (origine) focaliser(origine); });

    var boite = el('div', 'qz-menu');
    boite.setAttribute('data-glossaire', 'non');
    boite.appendChild(el('h3', '', 'Quiz'));
    var b = el('button', 'qz-ouvrir');
    b.type = 'button';
    b.appendChild(document.createTextNode('Teste tes connaissances'));
    b.appendChild(el('span', '', etapes.length + ' quiz de ' + etapes[0].questions.length + ' questions, un par mode'));
    b.setAttribute('aria-haspopup', 'dialog');
    boite.appendChild(b);
    var liste = panneau.querySelector(':scope > ul');
    if (liste && liste.nextSibling) panneau.insertBefore(boite, liste.nextSibling); else panneau.appendChild(boite);
    b.addEventListener('click', function () {
      var menu = panneau.closest('details');
      origine = menu ? menu.querySelector('summary') : b;
      if (menu) menu.open = false;
      ouvrir(null);
    });
    // autre déclencheur possible dans la page : <button data-quiz-ouvrir> (étape du mode affiché) ou data-quiz-ouvrir="4"
    document.addEventListener('click', function (e) {
      var d = e.target && e.target.closest && e.target.closest('[data-quiz-ouvrir]');
      if (!d) return;
      e.preventDefault();
      var v = d.getAttribute('data-quiz-ouvrir'), choix = v ? parNumeros(v)[0] : null;
      origine = d;
      ouvrir(choix && etapes.indexOf(choix) >= 0 ? choix : null);
    });
    return true;
  }

  // ── Démarrage ─────────────────────────────────────────────────────────────────────────────────────
  function demarrer() {
    try {
      if (document.querySelector('section.qz[data-etape-quiz], .qz-menu')) return;   // déjà posé (script chargé deux fois)
      var marque = document.querySelector('[data-quiz]');
      var v = marque ? marque.getAttribute('data-quiz') : '';
      if (v && v.trim().toLowerCase() === 'non') return;
      var etapes = v ? parNumeros(v) : [];
      var fichier = nomFichier();
      if (!etapes.length) etapes = ETAPES.filter(function (e) { return (e.page || '').toLowerCase() === fichier; });
      if (!etapes.length) return;                                   // cette page n’a pas de questions
      var conteneur = marque && marque !== document.documentElement && marque !== document.body ? marque : null;
      var panneau = !conteneur && document.querySelector('details#menu .menu-panel');
      styles();
      if (panneau && etapes.length > 1) { menu3D(etapes, panneau); return; }   // vue 3D : par le menu seulement
      blocEnLigne(etapes, conteneur);
    } catch (e) { /* la page reste entière sans le quiz */ }
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', demarrer);
  else demarrer();
})();
