/* Glossaire de l’atlas : dans le texte courant d’une page, la première occurrence de chaque terme du livre
   devient un bouton discret, souligné en pointillé, qui ouvre sa définition : une bulle au bureau, un tiroir en
   bas de l’écran sur téléphone (terme, anglais, définition, citation, références, liens).
   Jamais dans les titres, la barre, les liens, les boutons, les citations (« … », blockquote, q), les références
   (.ref), le SVG, les formulaires ni le pied de page ; jamais dans un élément caché.
   Les données (glossaire-atlas.json) sont injectées à la construction (construire_site.py) à la place du marqueur
   ci-dessous ; les références de la bulle deviennent des liens vers urantia.org grâce à refs-urantia.js.
   Aucun décalage de mise en page : les mots restent en ligne (span role="button"), la bulle est en position fixe. */
(function () {
  'use strict';
  var DONNEES = {"termes":[{"i":"absolu-de-deite","t":"Absolu de Déité","e":"Deity Absolute","d":"L’un des sept Absolus : tout le potentiel de Déité, que le Père a distingué de l’infini par son libre choix et où se déroulent toutes les activités divines. Il semble être l’activateur tout-puissant de l’univers.","r":["105:3.6","0:11.6","0:11.4"],"f":["Absolu de Déité"],"c":["Il est l’Absolu Qualifié par contraste avec l’Absolu Non Qualifié.","0:11.6"],"a":["dieu-et-deite.html#s1","Dieu et la Déité"]},{"i":"absolu-non-qualifie","t":"Absolu Non Qualifié","e":"Unqualified Absolute","d":"L’un des sept Absolus : toute la réalité non déifiée et non personnelle, à l’état de potentiel. Statique et en attente, il a une présence sans limites ; il parait être le mécanicien parfait de l’univers, quand l’Absolu de Déité en serait l’activateur.","r":["105:3.7","0:11.7","0:11.4"],"f":["Absolu Non Qualifié"],"c":["L’Absolu Non Qualifié est donc dépourvu de personnalité, de divinité et de toute prérogative de créateur.","0:11.7"],"a":["dieu-et-deite.html#s1","Dieu et la Déité"]},{"i":"absolu-universel","t":"Absolu Universel","e":"Universal Absolute","d":"L’un des sept Absolus : il unifie le déifié et le non déifié, c’est-à-dire l’Absolu de Déité et l’Absolu Non Qualifié, et relie l’absolu au relatif. Par lui, le fini peut coexister avec l’infini ; il équilibre aussi les tensions entre le temps et l’éternité.","r":["105:3.8","0:11.13","0:11.15"],"f":["Absolu Universel"],"c":["En dernière analyse et en compréhension finale, les trois ne sont qu’un Absolu.","0:11.15"],"a":["dieu-et-deite.html#s1","Dieu et la Déité"]},{"i":"absonite","t":"absonite","e":"absonite","d":"Niveau de réalité situé entre le fini et l’absolu : des choses et des êtres sans commencement ni fin, qui dépassent le temps et l’espace. Ils ne sont pas créés mais extériorisés ; le livre y rattache l’Ultimité de la Déité.","r":["0:1.12","10:5.5","42:10.7"],"f":["absonite","absonites"],"c":["Au Paradis, le mental est absolu ; dans Havona, il est absonite ; dans Orvonton, il est fini.","42:10.7"],"a":["concepts-en-schemas.html#s5","Concepts en schémas"]},{"i":"acteur-conjoint","t":"Acteur Conjoint","e":"Conjoint Actor","d":"Autre nom de l’Esprit Infini, Troisième Personne de la Déité : le Père et le Fils agissent ensemble en lui et par lui. Il unit les énergies cosmiques du Paradis aux énergies spirituelles du Fils et dispense le mental.","r":["8:5.5","105:3.5","9:1.1"],"f":["Acteur Conjoint"],"c":["En tant qu’Acteur Conjoint, il est le coreprésentant et partenaire exécutif du Père-Fils.","9:1.1"],"a":["dieu-et-deite.html#s2","Dieu et la Déité"]},{"i":"adam-et-eve","t":"Adam et Ève","e":"Adam and Eve","d":"Fils et Fille Matériels envoyés sur Urantia pour élever biologiquement les races humaines ; ils arrivèrent 37 848 ans avant l’an 1934. Leur mission échoua en partie après leur défaillance, mais leurs descendants enrichirent beaucoup l’humanité.","r":["51:0.1","74:0.1","75:8.1"],"f":["Adam et Ève","Fils Matériels","Fils Matériel","Fille Matérielle","Filles Matérielles","Adam","Ève"],"c":["Ces Fils, car il y en a deux — le Fils et la Fille Matériels — sont généralement appelés Adam et Ève sur une planète.","51:0.1"],"a":["rebellion-de-lucifer.html#echelles","La rébellion de Lucifer"]},{"i":"adamites","t":"Adamites","e":"Adamites","d":"Descendants d’Adam et Ève, appelés aussi race violette, établis en Mésopotamie autour du second jardin. Vers l’an 15 000 av. J.-C., mêlés aux Nodites et aux Sangiks, ils donnèrent naissance au peuple andite.","r":["76:3.8","78:0.2","78:3.1"],"f":["Adamites","adamites","adamite","race violette"],"c":["Les Adamites dépassaient considérablement les peuplades environnantes en accomplissements culturels et en développement intellectuel.","76:3.8"],"a":["histoire-d-urantia.html#h-carte","L’histoire d’Urantia"]},{"i":"ajusteur-de-pensee","t":"Ajusteur de Pensée","e":"Thought Adjuster","d":"Fragment du Père Universel venu habiter le mental humain ; sur Urantia, il arrive en moyenne juste avant six ans, après le premier choix moral de l’enfant. Si l’homme le choisit, il peut s’unir à lui pour toujours.","r":["107:0.3","108:2.1","107:0.6"],"f":["Ajusteur de Pensée","Ajusteurs de Pensée","Ajusteur","Ajusteurs","Moniteur de Mystère","Moniteurs de Mystère"],"c":["L’Ajusteur est l’infaillible compas cosmique de l’homme, orientant toujours et surement l’âme vers Dieu.","107:0.6"],"a":["destinee-humaine.html#don","La destinée humaine"]},{"i":"ame","t":"âme","e":"soul","d":"Réalité nouvelle qui grandit en l’homme à mesure qu’il choisit de faire la volonté de Dieu : l’Ajusteur en est le père, le mental humain la mère. Elle n’est ni matérielle ni spirituelle, mais morontielle.","r":["0:5.10","0:5.9","111:2.3"],"f":["âme","âmes"],"c":["C’est l’âme émergente et immortelle destinée à survivre à la mort physique et à commencer l’ascension du Paradis.","0:5.10"],"a":["concepts-en-schemas.html#s1","Concepts en schémas"]},{"i":"anciens-des-jours","t":"Anciens des Jours","e":"Ancients of Days","d":"Les dirigeants des sept superunivers : vingt-et-un êtres issus de la Trinité, tous créés en même temps, qui gouvernent par groupes de trois. C’est à eux qu’appartient notamment le jugement de la rébellion de Lucifer.","r":["18:3.4","15:10.3","53:1.2"],"f":["Anciens des Jours"],"c":["Chaque superunivers est régi par trois Anciens des Jours, chefs exécutifs conjoints du supergouvernement.","15:10.3"],"a":["atlas-3d.html#gouvernement","D’Urantia au Paradis (3D)"]},{"i":"andites","t":"Andites","e":"Andites","d":"Peuple né en Mésopotamie du mélange des Adamites avec les Nodites et les Sangiks. Leurs migrations successives portèrent la culture du second jardin en Eurasie et en Afrique du Nord ; ils quittèrent leur foyer vers 2 000 ans av. J.-C.","r":["78:0.1","78:0.2","78:5.2"],"f":["Andites","andites","andite"],"c":["De cette région partirent les hommes et les femmes qui inaugurèrent les activités des temps historiques et accélérèrent prodigieusement les progrès culturels sur Urantia.","78:0.1"],"a":["histoire-d-urantia.html#h-carte","L’histoire d’Urantia"]},{"i":"andon-et-fonta","t":"Andon et Fonta","e":"Andon and Fonta","d":"Les deux premiers êtres humains, des jumeaux nés « 993 419 ans avant l’année 1934 », ancêtres de tous les humains. Ils ne reçurent ces noms que lorsqu’ils fusionnèrent avec leur Ajusteur de Pensée.","r":["63:0.3","62:5.1","63:1.1"],"f":["Andon et Fonta","Andon","Fonta"],"c":["Andon est le nom nébadonien qui signifie « la première créature semblable au Père et montrant une soif de perfection humaine ».","63:0.3"],"a":["histoire-d-urantia.html#h-carte","L’histoire d’Urantia"]},{"i":"andonites","t":"Andonites","e":"Andonites","d":"Les premiers humains, descendants d’Andon et Fonta, au teint bistré, qui se protégeaient du froid avec des peaux de bêtes et se dispersèrent vers le nord. La famille Sangik, ancêtre des races de couleur, naquit plus tard parmi eux.","r":["63:4.1","63:5.1","64:5.1-2"],"f":["Andonites","andonites","andonite"],"a":["histoire-d-urantia.html#h-carte","L’histoire d’Urantia"]},{"i":"archanges","t":"archanges","e":"archangels","d":"Ordre élevé d’êtres spirituels de l’univers local, enfants du Fils Créateur et de l’Esprit-Mère, voués à la survie des mortels. Lors des résurrections, un archange fait l’appel des défunts ; leur circuit de communication fonctionne aujourd’hui sur Urantia.","r":["37:3.1","37:3.6","114:5.4"],"f":["archanges","archange"],"c":["C’est l’archange de la résurrection parfois dénommé « l’archange de Micaël ».","37:3.6"],"a":["familles-de-personnalites.html#h-tree","Familles de personnalités"]},{"i":"ascendeurs","t":"ascendeurs","e":"ascenders","d":"Les survivants mortels, appelés aussi pèlerins ascendants, qui montent de monde en monde vers le Paradis : mondes des maisons, Jérusem, Édentia, Salvington, capitales de secteur, Uversa, puis Havona.","r":["30:4.1","15:7.5-10","14:6.38"],"f":["ascendeurs","ascendeur","mortels ascendants","mortel ascendant","pèlerins ascendants"],"c":["Havona est le but d’éducation préparadisiaque de tous les ascendeurs mortels.","14:6.38"],"a":["atlas-3d.html#carriere","D’Urantia au Paradis (3D)"]},{"i":"avonals","t":"Avonals","e":"Avonals","d":"Fils Magistraux : deuxième ordre de Fils du Paradis, nés du Fils Éternel et de l’Esprit Infini. Ils clôturent les dispensations des mondes habités, y accomplissent des missions et s’y incarnent comme Fils d’effusion, chacun au moins une fois.","r":["20:2.1","20:2.5-7","35:0.1"],"f":["Avonals","Avonal","Fils Magistraux","Fils Magistral"],"c":["Les Avonals sont des ministres et des juges planétaires, les magistrats des royaumes de l’espace-temps — de toutes les races, pour tous les mondes et dans tous les univers.","20:2.1"],"a":["familles-de-personnalites.html#h-tree","Familles de personnalités"]},{"i":"caligastia","t":"Caligastia","e":"Caligastia","d":"Prince Planétaire d’Urantia, arrivé il y a environ cinq-cent-mille ans pour diriger l’humanité primitive. Il rallia la rébellion de Lucifer, puis refusa le pardon offert par Micaël ; il n’a aucun pouvoir sur le mental de qui ne le désire pas.","r":["66:0.2","53:1.4","53:8.6"],"f":["Caligastia"],"c":["Le « diable » n’est autre que Caligastia, le Prince Planétaire déposé d’Urantia et Fils de l’ordre secondaire des Lanonandeks.","53:1.4"],"a":["rebellion-de-lucifer.html#echelles","La rébellion de Lucifer"]},{"i":"cano","t":"Cano","e":"Cano","d":"Brillant chef nodite d’une colonie voisine du Jardin. Convaincu par le projet de Sérapatatia, il rencontra Ève en secret, puis périt peu après avec sa colonie ; il était le père de Caïn, né ensuite.","r":["75:3.7","75:3.8","75:5.3"],"f":["Cano"],"c":["Cano était très bien disposé envers le régime adamique ; en fait, il était le sincère chef spirituel des Nodites des environs qui souhaitaient des relations amicales avec le Jardin.","75:3.7"],"a":["bible-et-livre.html#p-eve","La Bible et le Livre d’Urantia"]},{"i":"censeurs-universels","t":"Censeurs Universels","e":"Universal Censors","d":"Êtres issus de la Trinité du Paradis, chargés du jugement divin dans tout le grand univers. Ils sont huit milliards : un sur chacun des mondes de Havona et un milliard par superunivers. Même les Anciens des Jours ne jugent qu’avec leur concours.","r":["19:4.1","19:4.2","19:4.3"],"f":["Censeurs Universels","Censeur Universel"],"c":["Ces êtres uniques sont le jugement de la Déité.","19:4.1"],"a":["familles-de-personnalites.html#h-tree","Familles de personnalités"]},{"i":"cercles-psychiques","t":"cercles psychiques","e":"psychic circles","d":"Les sept niveaux de croissance de la personnalité humaine pendant la vie terrestre, franchis du septième au premier. Au troisième, on reçoit un gardien séraphique personnel ; les franchir prépare la fusion avec l’Ajusteur, sans en tenir lieu.","r":["110:6.1","110:6.3","110:6.14"],"f":["cercles psychiques","cercle psychique","sept cercles","cercles cosmiques"],"c":["Les cercles psychiques ne sont ni exclusivement intellectuels ni entièrement morontiels ; ils concernent le statut de personnalité, les accomplissements mentaux, la croissance de l’âme et l’accord avec l’Ajusteur.","110:6.3"],"a":["concepts-en-schemas.html#s4","Concepts en schémas"]},{"i":"cherubins","t":"chérubins","e":"cherubim","d":"Anges de l’univers local, de même origine que les séraphins mais de l’ordre le plus humble. Associés par paires aux sanobins, ils assistent les séraphins, sans les suivre hors de l’univers local.","r":["38:7.1","38:7.2","38:7.3"],"f":["chérubins","chérubin"],"c":["Ils sont magnifiquement intelligents, merveilleusement efficaces, touchants d’affection et presque humains.","38:7.1"],"a":["familles-de-personnalites.html#h-tree","Familles de personnalités"]},{"i":"conseillers-divins","t":"Conseillers Divins","e":"Divine Counselors","d":"Êtres issus de la Trinité qui forment le conseil de la Déité pour les superunivers : vingt-et-un milliards, trois milliards par superunivers. Un Conseiller Divin d’Orvonton signe l’Introduction du livre, et plusieurs fascicules de la partie I sont présentés par un Conseiller Divin.","r":["19:3.1","0:12.14","1:7.9"],"f":["Conseillers Divins","Conseiller Divin"],"c":["Ils ne sont pas le reflet du divin conseil de la Trinité ; ils sont ce conseil.","19:3.1"],"a":["familles-de-personnalites.html#h-tree","Familles de personnalités"]},{"i":"constellation","t":"constellation","e":"constellation","d":"Au sens propre au livre, et non au sens astronomique : division d’un univers local, gouvernée par trois Vorondadeks, les Très Hauts. Un univers local en compte cent ; la nôtre est Norlatiadek.","r":["15:2.4","43:0.1","15:14.6"],"f":["constellation","constellations"],"c":["Cent systèmes (environ cent-mille planètes habitables) forment une constellation.","15:2.4"],"a":["nebadon-dans-orvonton.html#h-zoom","Nébadon dans Orvonton"]},{"i":"corps-de-gravite-obscurs","t":"corps de gravité obscurs","e":"dark gravity bodies","d":"Énormes masses obscures qui forment deux ceintures autour de Havona, tournant en sens contraires. Insensibles à la lumière, elles cachent l’univers central aux mondes du temps et en équilibrent la gravité.","r":["14:1.14","14:1.15","12:1.10"],"f":["corps de gravité obscurs","corps de gravité"],"c":["Ces corps de gravité obscurs ne réfléchissent pas la lumière et ne l’absorbent pas non plus […]","14:1.14"],"a":["atlas-3d.html#havona","D’Urantia au Paradis (3D)"]},{"i":"dalamatia","t":"Dalamatia","e":"Dalamatia","d":"Cité du Prince Planétaire, bâtie en Mésopotamie près du golfe Persique d’alors ; centre mondial de culture, elle fut nommée en l’honneur de Daligastia. Après la rébellion, elle fut engloutie par la mer.","r":["66:3.1","66:3.3","67:5.2"],"f":["Dalamatia"],"c":["Le noyau de l’établissement du prince était une cité très simple mais très belle, enclose dans une muraille de douze mètres de haut.","66:3.3"],"a":["histoire-d-urantia.html#h-carte","L’histoire d’Urantia"]},{"i":"daligastia","t":"Daligastia","e":"Daligastia","d":"Fils Lanonandek secondaire, adjoint-associé du Prince Planétaire Caligastia. Lors de la rébellion, c’est lui qui convoqua les dix conseils d’Urantia, sommés de lui remettre tous leurs pouvoirs pour le compte de Caligastia.","r":["66:2.2","67:2.1","53:8.6"],"f":["Daligastia"],"c":["Le dernier acte de Micaël avant de quitter Urantia fut d’offrir son pardon à Caligastia et Daligastia, mais ils dédaignèrent cette affectueuse proposition.","53:8.6"],"a":["rebellion-de-lucifer.html#echelles","La rébellion de Lucifer"]},{"i":"daynals","t":"Daynals","e":"Daynals","d":"Fils du Paradis issus de la Trinité, appelés aussi Fils Instructeurs de la Trinité. Ni créateurs, ni juges, ni administrateurs, ils enseignent : leur ministère favorise le progrès moral et spirituel des créatures qui montent vers le Paradis.","r":["20:7.1","20:7.3","35:0.1"],"f":["Daynals","Daynal","Fils Instructeurs de la Trinité","Fils Instructeurs"],"c":["Ils sont les éducateurs universels, et se consacrent à l’éveil spirituel et à la gouverne morale de tous les royaumes.","20:7.3"],"a":["familles-de-personnalites.html#h-tree","Familles de personnalités"]},{"i":"defaillance","t":"défaillance","e":"default","d":"Nom que le livre donne à la faute d’Adam et Ève. Pressée d’améliorer les peuples voisins, Ève s’unit en secret au chef nodite Cano, sur le conseil de Sérapatatia ; Adam choisit ensuite délibérément de partager son sort.","r":["75:3.5-8","75:5.2","75:8.1"],"f":["défaillance"],"c":["Adam et Ève furent vraiment déchus de leur état supérieur de filiation matérielle jusqu’à l’humble statut des hommes mortels ; mais ce ne fut pas la chute de l’homme.","75:8.1"],"a":["bible-et-livre.html#p-eve","La Bible et le Livre d’Urantia"]},{"i":"deite","t":"Déité","e":"Deity","d":"Source de tout ce qui est divin. La Déité peut être personnelle, et l’on parle alors de Dieu, mais aussi prépersonnelle ou superpersonnelle. Elle peut exister de toujours, comme dans le Fils Éternel, ou émerger par l’expérience, comme l’Être Suprême.","r":["0:1.2","0:1.14-15","0:2.10"],"f":["Déité","Déités"],"c":["Le mot Déité peut se référer ou non à des personnalités de divinité.","0:2.10"],"a":["dieu-et-deite.html#s2","Dieu et la Déité"]},{"i":"dieu-le-septuple","t":"Dieu le Septuple","e":"God the Sevenfold","d":"Association des Déités du Paradis et de leurs associés créateurs, telle que la rencontrent les créatures du temps et de l’espace, en sept niveaux : Fils Créateurs, Anciens des Jours, Sept Maitres Esprits, Être Suprême, puis Dieu l’Esprit, Dieu le Fils et Dieu le Père.","r":["0:8.1-8","0:2.16","0:8.9"],"f":["Dieu le Septuple"],"c":["Cette personnalisation septuple de la Déité dans le temps et l’espace et pour les sept superunivers, rend l’homme mortel capable d’atteindre la présence de Dieu, qui est esprit.","0:8.9"],"a":["dieu-et-deite.html#s5","Dieu et la Déité"]},{"i":"dieu-l-absolu","t":"Dieu l’Absolu","e":"God the Absolute","d":"Troisième Déité expérientielle, la plus éloignée de toute actualisation : elle résulterait de l’unification d’une seconde Trinité expérientielle, la Trinité Absolue. Le livre la rattache à l’Absolu de Déité et hésite à en dire davantage.","r":["0:10.1","0:10.2","0:2.18"],"f":["Dieu l’Absolu"],"c":["Dieu l’Absolu est le but d’aboutissement et de réalisation de tous les êtres superabsonites.","0:10.2"],"a":["dieu-et-deite.html#s6","Dieu et la Déité"]},{"i":"dieu-l-ultime","t":"Dieu l’Ultime","e":"God the Ultimate","d":"Deuxième Déité expérientielle, encore en voie d’actualisation : Dieu agissant au-delà du temps et de l’espace, sur le niveau absonite. Il émergera pleinement quand sera unifiée la Trinité Ultime, dont l’Être Suprême fera partie.","r":["0:9.2","0:12.6","0:2.17"],"f":["Dieu l’Ultime","Ultime"],"c":["L’Ultime est l’unification de la Trinité du Paradis comprise par les êtres absonites.","0:9.2"],"a":["dieu-et-deite.html#s6","Dieu et la Déité"]},{"i":"divinite","t":"divinité","e":"divinity","d":"Qualité caractéristique de la Déité, qui unifie et coordonne. Dans la personnalité, elle se traduit en amour, miséricorde et ministère ; sur les niveaux impersonnels, en justice, pouvoir et souveraineté. Tout ce qui est divin n’est pas pour autant Déité.","r":["0:1.16","0:1.17","0:1.15"],"f":["divinité","divinités"],"c":["La divinité est intelligible aux créatures en tant que vérité, beauté et bonté.","0:1.17"],"a":["concepts-en-schemas.html#s5","Concepts en schémas"]},{"i":"edentia","t":"Édentia","e":"Edentia","d":"Capitale de notre constellation, Norlatiadek, et siège des Très Hauts : un monde architectural environ cent fois plus grand qu’Urantia. Les ascendeurs y font étape après Jérusem.","r":["43:0.2","15:7.6"],"f":["Édentia"],"c":["Édentia, siège de votre constellation de Norlatiadek, a soixante-dix satellites de culture et d’entrainement social.","15:7.6"],"a":["atlas-3d.html#norlatiadek","D’Urantia au Paradis (3D)"]},{"i":"effusion","t":"effusion","e":"bestowal","d":"Pour un Fils divin, le fait de vivre la vie de ses propres créatures en prenant leur forme. Micaël s’est effusé sept fois, la dernière sur Urantia. Le mot désigne aussi le don d’un esprit, comme l’effusion de l’Esprit de Vérité.","r":["120:0.1","119:0.3","52:5.6"],"f":["effusion","effusions"],"c":["Vivre une vie identique à celle qu’il impose aux êtres intelligents de sa propre création, donc de s’effuser dans la similitude de ses divers ordres d’êtres créés […]","120:0.1"],"a":["vie-de-jesus.html","La vie de Jésus"]},{"i":"ensa","t":"Ensa","e":"Ensa","d":"Notre secteur mineur, le troisième du secteur majeur de Splandon. Il réunit cent univers locaux, dont Nébadon, et a pour capitale Uminor la troisième.","r":["15:14.7","15:14.6","15:3.5"],"f":["Ensa"],"c":["Le centre de rotation de votre secteur mineur est situé fort loin dans l’énorme et dense nuage stellaire du Sagittaire […]","15:3.5"],"a":["atlas-3d.html#ensa","D’Urantia au Paradis (3D)"]},{"i":"espace-exterieur","t":"espace extérieur","e":"outer space","d":"Les quatre immenses niveaux d’espace qui entourent le grand univers, au-delà d’une zone de calme relatif. Des énergies colossales s’y organisent : ces niveaux, encore inhabités, sont destinés à recevoir de futurs univers.","r":["12:1.14","12:1.16","0:0.6"],"f":["espace extérieur","niveaux d’espace extérieur","niveau d’espace extérieur"],"c":["Ces formidables roues de forces énergétiques sont situées dans le premier niveau d’espace extérieur, une ceinture continue d’activité cosmique entourant la totalité de la création connue, organisée et habitée.","12:1.14"],"a":["atlas-3d.html#espace-exterieur","D’Urantia au Paradis (3D)"]},{"i":"esprit","t":"esprit","e":"spirit","d":"Traduit l’anglais spirit, à ne pas confondre avec le mental (mind) : est esprit tout ce qui répond au circuit d’esprit du Fils Éternel. Chez l’homme, l’esprit qui l’habite est l’Ajusteur de Pensée.","r":["0:6.1","0:5.9","42:12.12"],"f":["esprit","esprits"],"s":1,"c":["L’esprit est l’architecte, le mental est le constructeur, le corps est le bâtiment matériel.","42:12.12"],"a":["concepts-en-schemas.html#s6","Concepts en schémas"]},{"i":"esprit-de-verite","t":"Esprit de Vérité","e":"Spirit of Truth","d":"Esprit que Jésus, le Fils Créateur, a envoyé à sa place après son départ, le jour de la Pentecôte. Il vit dans le croyant, l’aide à saisir la vérité et a préparé tout mental normal à recevoir l’Ajusteur.","r":["194:2.1","194:3.1","194:2.3"],"f":["Esprit de Vérité"],"c":["Le Fils Créateur, dans la chair, a révélé Dieu aux hommes ; l’Esprit de Vérité, dans le cœur, révèle le Fils Créateur aux hommes.","194:3.1"],"a":["concepts-en-schemas.html#s2","Concepts en schémas"]},{"i":"esprit-infini","t":"Esprit Infini","e":"Infinite Spirit","d":"Troisième Personne de la Déité, issue de l’action commune du Père et du Fils. Source du mental pour toutes les créatures, il révèle la miséricorde du Fils par ses nombreux enfants.","r":["8:0.3","0:2.14","105:3.5"],"f":["Esprit Infini","Dieu l’Esprit"],"c":["À l’instant même où Dieu le Père et Dieu le Fils conçoivent conjointement une action identique et infinie […] l’Esprit Infini, en possession de tous ses moyens, jaillit instantanément à l’existence.","8:0.3"],"a":["dieu-et-deite.html#s2","Dieu et la Déité"]},{"i":"esprit-mere","t":"Esprit-Mère de l’univers local","e":"Universe Mother Spirit (Local Universe Mother Spirit)","d":"Compagne du Fils Créateur dans chaque univers local : une représentation personnelle de l’Esprit Infini, associée à toute son œuvre de création. Ses enfants, les sept esprits-mentaux adjuvats, servent le mental des créatures.","r":["34:1.1","34:0.1","36:5.1"],"f":["Esprit-Mère de l’univers local","Esprit-Mère de l’Univers","Esprit-Mère","Esprits-Mères","Divine Ministre","Divines Ministres","Esprit Créatif","Esprits Créatifs"],"c":["L’Esprit Créatif individualisé, auxiliaire du Fils Créateur, est devenu son associée créative personnelle, l’Esprit-Mère de l’univers local.","34:1.1"],"a":["concepts-en-schemas.html#s1","Concepts en schémas"]},{"i":"adjuvats","t":"esprits-mentaux adjuvats","e":"adjutant mind-spirits","d":"Les sept esprits par lesquels l’Esprit-Mère de l’univers local sert le mental des êtres vivants, de l’intuition à la sagesse ; ils ressemblent davantage à des circuits qu’à des êtres. Les cinq premiers agissent chez l’animal, les sept chez l’être humain.","r":["36:5.1","36:5.2-4","42:10.4"],"f":["esprits-mentaux adjuvats","esprit-mental adjuvat","adjuvats","adjuvat"],"c":["Les adjuvats sont les enfants de l’Esprit-Mère de l’Univers et constituent son ministère personnel auprès du mental matériel des royaumes.","36:5.1"],"a":["concepts-en-schemas.html#s3","Concepts en schémas"]},{"i":"etat-major","t":"état-major du Prince","e":"corporeal staff","d":"Les cent membres corporels qui accompagnaient Caligastia : des volontaires ascendants de Jérusem, dotés sur Urantia de corps physiques. Lors de la rébellion, quarante restèrent loyaux, dont Van ; les soixante autres suivirent Nod.","r":["66:2.3-5","67:3.2","67:4.2"],"f":["état-major corporel","état-major du Prince","état-major du prince","état-major"],"c":["Ils travaillèrent de tout cœur pour le Prince rebelle, mais s’aperçurent bientôt qu’ils étaient privés du soutien des circuits vitaux du système.","67:4.2"],"a":["rebellion-de-lucifer.html#camps","La rébellion de Lucifer"]},{"i":"etre-supreme","t":"Être Suprême","e":"Supreme Being","d":"Le Dieu du temps et de l’espace, encore en train d’émerger : une Déité expérientielle qui grandit avec les accomplissements des Créateurs et des créatures du grand univers. Plus la volonté de Dieu est faite, plus son potentiel devient réel.","r":["0:2.15","117:0.1","117:1.1"],"f":["Être Suprême","Dieu le Suprême","Tout-Puissant Suprême","Suprême"],"c":["Il est la surâme du grand univers, la conscience du cosmos fini, le parachèvement de la réalité finie et la personnification de l’expérience Créateur-créature.","117:1.1"],"a":["dieu-et-deite.html#s6","Dieu et la Déité"]},{"i":"existentiel","t":"existentiel","e":"existential","d":"Se dit de ce qui existe de toute éternité, sans commencement : avant tout le Père, le Fils et l’Esprit. Le livre l’oppose à expérientiel, qui qualifie ce qui se réalise peu à peu par l’expérience, comme l’Être Suprême.","r":["0:7.3","0:7.1","0:1.14"],"f":["existentiel","existentielle","existentiels","existentielles","existentiellement"],"c":["Dieu le Père, Dieu le Fils et Dieu l’Esprit sont éternels — sont des êtres existentiels […]","0:7.1"],"a":["dieu-et-deite.html#s6","Dieu et la Déité"]},{"i":"experientiel","t":"expérientiel","e":"experiential","d":"Se dit de ce qui devient réel par l’expérience et la croissance : cela commence dans le temps, mais peut durer sans fin. L’Être Suprême et Dieu l’Ultime sont des Déités expérientielles, encore en voie d’actualisation.","r":["0:7.4-6","0:4.9"],"f":["expérientiel","expérientielle","expérientiels","expérientielles","expérientiellement"],"c":["La Déité Paradisiaque est existentielle, mais le Suprême et l’Ultime qui émergent sont expérientiels.","0:4.9"],"a":["dieu-et-deite.html#s6","Dieu et la Déité"]},{"i":"fils-createur","t":"Fils Créateur","e":"Creator Son","d":"Fils divin issu de l’union du Père Universel et du Fils Éternel, qui bâtit et gouverne un univers local. Chacun est unique ; tous appartiennent à l’ordre des Micaëls, et celui de notre univers, Nébadon, est Micaël.","r":["21:0.1","21:0.3","32:0.1"],"f":["Fils Créateur","Fils Créateurs","Micaëls"],"c":["Ces créateurs et souverains d’univers sont d’origine duelle, incorporant les caractéristiques de Dieu le Père et Dieu le Fils.","21:0.1"],"a":["atlas-3d.html#gouvernement","D’Urantia au Paradis (3D)"]},{"i":"fils-de-l-homme","t":"Fils de l’Homme","e":"Son of Man","d":"Titre que Jésus choisit pour se désigner, inspiré selon le livre d’un passage du Livre d’Énoch plutôt que de Daniel. Il souligne que le Fils Créateur a vécu en homme véritable, né d’une femme.","r":["126:3.6","126:3.8","128:1.2"],"f":["Fils de l’Homme","Fils de l’homme"],"c":["Et même maintenant qu’il préside avec une autorité souveraine aux destinées d’un univers, il porte encore, parmi ses nombreux titres bien gagnés, celui de Fils de l’Homme.","128:1.2"],"a":["bible-et-livre.html#p-daniel","La Bible et le Livre d’Urantia"]},{"i":"fils-eternel","t":"Fils Éternel","e":"Eternal Son","d":"Deuxième Personne de la Déité : l’expression parfaite et personnelle du Père, que le livre appelle aussi le Verbe. Les forces de l’esprit convergent en lui, et il est l’archétype absolu de toute personnalité.","r":["6:0.1","0:3.15","105:3.3"],"f":["Fils Éternel","Dieu le Fils","Fils Originel"],"c":["Nulle personnalité ne peut espérer atteindre le Père Universel sinon par son Fils Éternel.","105:3.3"],"a":["dieu-et-deite.html#s2","Dieu et la Déité"]},{"i":"fils-trinitises","t":"Fils Trinitisés","e":"Trinitized Sons of God","d":"Troisième groupe de Fils de Dieu, à côté des Fils descendants et ascendants. Leur point commun est d’avoir été trinitisés, ou embrassés par la Trinité, comme les mortels parfaits devenus Puissants Messagers, éprouvés dans leur loyauté.","r":["22:0.1","20:0.5","22:2.1"],"f":["Fils Trinitisés","Fils de Dieu Trinitisés","fils trinitisés"],"c":["Les Fils Trinitisés sont un groupe d’origine complexe comprenant tous les êtres embrassés par la Trinité du Paradis, même s’ils ne sont pas issus directement de la Trinité.","20:0.5"],"a":["familles-de-personnalites.html#h-tree","Familles de personnalités"]},{"i":"finalitaires","t":"finalitaires","e":"finaliters","d":"Les ascendeurs parvenus au Paradis au terme de leur ascension, surtout des mortels fusionnés avec leur Ajusteur, réunis dans le Corps de la Finalité. Ils servent aujourd’hui dans les univers du temps ; les auteurs disent ignorer leur destinée finale.","r":["31:0.1","31:0.11","31:3.2"],"f":["finalitaires","finalitaire","Corps de la Finalité"],"c":["Il y a en permanence une ou plusieurs compagnies de finalitaires mortels en service sur Urantia.","31:0.11"],"a":["atlas-3d.html#carriere","D’Urantia au Paradis (3D)"]},{"i":"fusion","t":"fusion","e":"fusion","d":"Union éternelle de l’âme humaine avec l’Ajusteur de Pensée. Elle se produit habituellement après la mort, sur les mondes des maisons ; certains mortels fusionnent plutôt avec l’Esprit ou le Fils.","r":["112:7.2","47:8.3","40:9.1"],"f":["fusion","fusionner","fusionna","fusionnent","fusionnés"],"c":["Et cette fusion constitue le mystère qui fait que Dieu et l’homme sont un […]","112:7.2"],"a":["destinee-humaine.html#fusion","La destinée humaine"]},{"i":"gabriel","t":"Gabriel","e":"Gabriel","d":"Premier-né de l’univers local de Nébadon, appelé la Radieuse Étoile du Matin, et chef exécutif de cet univers. Selon le récit du livre, c’est aussi lui qui annonça à Marie la naissance de Jésus.","r":["33:4.1-5","53:5.4","122:3.1"],"f":["Gabriel de Salvington","Gabriel","Radieuse Étoile du Matin"],"c":["Puis, en conseil avec les Très Hauts, il décida d’assumer le commandement des armées loyales de Satania.","53:5.4"],"a":["familles-de-personnalites.html#h-tree","Familles de personnalités"]},{"i":"grand-univers","t":"grand univers","e":"grand universe","d":"Ensemble de l’univers central, Havona, et des sept superunivers qui l’entourent : la partie de la création aujourd’hui organisée et habitée, avec quelque sept mille milliards de mondes habitables. Il fait partie du maitre univers.","r":["0:0.6","15:2.9","12:1.13"],"f":["grand univers"],"c":["Et c’est près de cette frontière extérieure, dans un coin éloigné de cette magnifique création, que votre univers local poursuit son existence mouvementée.","12:1.13"],"a":["atlas-3d.html#grand-univers","D’Urantia au Paradis (3D)"]},{"i":"havona","t":"Havona","e":"Havona","d":"Univers central, parfait et éternel, au cœur duquel repose l’Ile du Paradis. Les créations du temps et de l’espace tournent autour de lui ; les ascendeurs y sont formés, circuit après circuit, avant d’atteindre le Paradis.","r":["14:0.1","14:1.9","14:3.4"],"f":["Havona"],"c":["Le milliard de mondes de Havona est disposé en sept circuits concentriques qui entourent immédiatement les trois circuits des satellites du Paradis.","14:1.9"],"a":["atlas-3d.html#havona","D’Urantia au Paradis (3D)"]},{"i":"isolement","t":"isolement d’Urantia","e":"isolation","d":"Coupure des circuits qui reliaient Urantia au reste du système, survenue quand Caligastia rallia la rébellion de Lucifer. La planète reste techniquement isolée, mais, pour chacun, cela compte peu depuis la venue de l’Esprit de Vérité.","r":["67:2.3","114:5.4"],"f":["isolement","planète isolée","planètes isolées","monde isolé","mondes isolés"],"c":["Entretemps, les circuits du système avaient été coupés ; Urantia était isolée.","67:2.3"],"a":["rebellion-de-lucifer.html#isolement","La rébellion de Lucifer"]},{"i":"eden","t":"Jardin d’Éden","e":"Garden of Eden","d":"Siège préparé pour Adam et Ève par Van et ses compagnons, sur une longue péninsule de la Méditerranée orientale. Son nom rappelle la beauté d’Édentia ; la péninsule fut plus tard engloutie par la mer.","r":["73:3.1","73:4.1","73:7.1"],"f":["Jardin d’Éden","Éden","premier jardin","premier Éden"],"c":["Telle fut la fin de la plus belle création naturelle qu’Urantia ait jamais abritée.","73:7.1"],"a":["bible-et-livre.html#p-jardin","La Bible et le Livre d’Urantia"]},{"i":"je-suis","t":"JE SUIS","e":"I AM","d":"Concept philosophique de l’Infini : le Père Universel envisagé comme cause première de toute réalité, avant toute différenciation. Il répond au besoin humain de se représenter un commencement. Le livre emploie aussi ces mots pour le nom divin dévoilé à Moïse.","r":["105:1.1-5","0:3.23","182:1.9"],"f":["JE SUIS"],"c":["Le concept du JE SUIS est une concession philosophique que nous faisons au mental fini de l’homme lié au temps et enchainé à l’espace […]","0:3.23"],"a":["dieu-et-deite.html#s1","Dieu et la Déité"]},{"i":"jerusem","t":"Jérusem","e":"Jerusem","d":"Capitale du système local de Satania, monde architectural presque cent fois plus grand qu’Urantia. Autour d’elle tournent sept mondes de transition, parmi les satellites desquels se trouvent les sept mondes des maisons, première étape des humains après la mort.","r":["46:0.1","45:0.1","15:7.5"],"f":["Jérusem"],"c":["[…] le siège du système est vraiment le ciel imaginé par la majorité des croyants religieux du vingtième siècle.","46:0.1"],"a":["atlas-3d.html#satania","D’Urantia au Paradis (3D)"]},{"i":"lanaforge","t":"Lanaforge","e":"Lanaforge","d":"Fils Lanonandek primaire, actuel Souverain du système de Satania, envoyé pour succéder à Lucifer. Lors d’une rébellion antérieure dans Nébadon, il était resté fidèle à Micaël alors que son supérieur faisait défection.","r":["45:3.2","45:2.3","53:7.13"],"f":["Lanaforge"],"c":["Avec l’arrivée de Lanaforge, les archirebelles furent détrônés et dépouillés de tout pouvoir de gouvernement.","53:7.13"],"a":["rebellion-de-lucifer.html#statut","La rébellion de Lucifer"]},{"i":"lanonandeks","t":"Lanonandeks","e":"Lanonandeks","d":"Troisième ordre de Fils de l’univers local, créés par le Fils Créateur et l’Esprit-Mère, puis formés par les Melchizédeks. Lucifer et Satan appartenaient à leur rang primaire, Caligastia au rang secondaire.","r":["35:8.1","35:8.2","53:1.4"],"f":["Lanonandeks","Lanonandek","Fils Lanonandeks","Fils Lanonandek"],"c":["[…] ils sont surtout connus comme Souverains de Systèmes, gouvernant les systèmes locaux, et comme Princes Planétaires, chefs administratifs des mondes habités.","35:8.1"],"a":["familles-de-personnalites.html#h-tree","Familles de personnalités"]},{"i":"lucifer","t":"Lucifer","e":"Lucifer","d":"Fils Lanonandek primaire, brillant souverain du système de Satania. Avec son premier assistant, Satan, il se dressa contre le Père Universel et contre Micaël, et lança la rébellion qui porte son nom.","r":["53:0.1","53:2.1","53:9.2"],"f":["Lucifer"],"c":["Quand Micaël devint le chef confirmé de Nébadon, Lucifer fut mis en prison par les agents des Anciens des Jours d’Uversa […]","53:9.2"],"a":["rebellion-de-lucifer.html","La rébellion de Lucifer"]},{"i":"machiventa","t":"Machiventa Melchizédek","e":"Machiventa Melchizedek","d":"Melchizédek venu vivre parmi les humains à Salem « 1 973 ans avant la naissance de Jésus », pour y raviver la croyance en un Dieu unique ; Abraham devint son disciple. Il a reçu depuis le titre de Prince Planétaire vice-gérant d’Urantia.","r":["93:2.1","93:3.1","93:10.5"],"f":["Machiventa Melchizédek","Machiventa","Melchizédek"],"c":["Son arrivée n’eut rien de spectaculaire ; nul œil humain ne fut témoin de sa matérialisation.","93:2.1"],"a":["bible-et-livre.html#p-melchisedech","La Bible et le Livre d’Urantia"]},{"i":"maitre","t":"Maitre","e":"Master","d":"Titre que le texte donne très souvent à Jésus, comme le faisaient ses apôtres et ses disciples. Le mot s’écrit ici sans accent circonflexe, selon l’orthographe rectifiée de 1990.","r":["129:1.11","139:1.2"],"f":["Maitre"],"c":["[…] Zébédée avait beaucoup d’ouvriers, et ce fut parmi ces travailleurs que, pour la première fois, Jésus fut appelé « le Maitre ».","129:1.11"],"a":["vie-de-jesus.html","La vie de Jésus"]},{"i":"maitre-univers","t":"maitre univers","e":"master universe","d":"L’ensemble de la création, disposé autour du Paradis en six ellipses concentriques : Havona, les sept superunivers, puis quatre niveaux d’espace extérieur, encore inhabités, où de futurs univers sont en formation.","r":["12:1.3","0:0.6","12:1.16"],"f":["maitre univers","Maitre Univers"],"c":["[…] nous considérons le maitre univers, tel qu’il existe et qu’il est administré comme ayant des limitations, comme étant nettement délimité et borné à ses lisières extérieures par l’espace ouvert.","12:1.16"],"a":["atlas-3d.html#maitre-univers","D’Urantia au Paradis (3D)"]},{"i":"maitres-organisateurs-de-force","t":"Maitres Organisateurs de Force","e":"Master Force Organizers","d":"Êtres du Paradis, ni créateurs ni créatures, qui façonnent l’énergie de l’espace : ils font passer la force primordiale sous l’emprise de la gravité du Paradis et lancent les nébuleuses. L’un d’eux a déclenché la formation de la nébuleuse d’Andronover.","r":["29:5.1","29:5.5","57:1.6"],"f":["Maitres Organisateurs de Force","Maitre Organisateur de Force","organisateurs de force","organisateur de force"],"c":["Les Maitres Organisateurs de Force Primaires sont les manipulateurs des forces spatiales primordiales ou fondamentales de l’Absolu Non Qualifié ; ce sont des créateurs de nébuleuses.","29:5.5"],"a":["familles-de-personnalites.html#h-tree","Familles de personnalités"]},{"i":"manifeste-de-lucifer","t":"manifeste de Lucifer","e":"Lucifer manifesto","d":"Proclamation de la rébellion, faite sur Jérusem il y a environ deux-cent-mille ans. Elle niait l’existence du Père Universel, contestait l’autorité de Micaël et des Anciens des Jours, et attaquait le plan d’ascension des mortels.","r":["53:3.1","53:3.2-6","53:4.1"],"f":["manifeste de Lucifer","Déclaration Luciférienne de Liberté","Déclaration de Liberté"],"c":["Le manifeste de Lucifer fut proclamé au conclave annuel de Satania, sur la mer de verre […]","53:4.1"],"a":["rebellion-de-lucifer.html#manifeste","La rébellion de Lucifer"]},{"i":"medians","t":"médians","e":"midwayers","d":"Êtres présents sur la plupart des mondes habités de Nébadon, à mi-chemin entre les mortels et les anges. Urantia en compte deux ordres, nés aux temps de Dalamatia puis d’Adam ; un médian secondaire a rédigé le récit de la vie de Jésus.","r":["77:0.1","77:0.2","121:0.1"],"f":["médians","créatures médianes"],"c":["Elles paraissent être un accident du temps, mais sont si répandues et apportent une aide si précieuse que nous les avons acceptées […]","77:0.1"],"a":["familles-de-personnalites.html#h-tree","Familles de personnalités"]},{"i":"melchizedeks","t":"Melchizédeks","e":"Melchizedeks","d":"Ordre de Fils de l’univers local, à mi-chemin entre la Divinité et les créatures les plus humbles. Surnommés « Fils de secours », ils interviennent dans les situations d’urgence ; douze d’entre eux administrèrent Urantia après la chute de Caligastia.","r":["35:2.1","93:0.1","67:6.5"],"f":["Melchizédeks","Fils Melchizédeks","Père Melchizédek","Manovandet Melchizédek","un Melchizédek"],"c":["En fait, toutes les formes de vie intelligente trouvent en ces Fils des amis compréhensifs, des instructeurs sympathiques et des conseillers avisés.","35:2.1"],"a":["familles-de-personnalites.html#h-tree","Familles de personnalités"]},{"i":"mental","t":"mental","e":"mind","d":"Traduit l’anglais mind, à ne pas confondre avec l’esprit (spirit) : l’intelligence, qui vient de l’Esprit Infini. Chez l’homme, il est prêté pour la vie physique, et l’usage qu’on en fait engage la vie éternelle.","r":["0:6.1","111:1.5"],"f":["mental"],"c":["Le mental est à peu près tout ce que vous possédez de réalité universelle qui soit soumise à votre volonté.","111:1.5"],"a":["concepts-en-schemas.html#s6","Concepts en schémas"]},{"i":"messagers-solitaires","t":"Messagers Solitaires","e":"Solitary Messengers","d":"Ordre le plus ancien des Personnalités Supérieures de l’Esprit Infini, qui les a créés seul. Ils portent rapidement les messages urgents dans tout le grand univers, plus vite que les séraphins ; leur nombre est fixe, mais le texte n’en donne pas le total.","r":["23:0.1-2","23:2.1","23:3.1-2"],"f":["Messagers Solitaires","Messager Solitaire"],"c":["Entre eux, ils n’ont ni organisation ni gouvernement d’aucune sorte ; ils sont des Messagers Solitaires.","23:2.1"],"a":["familles-de-personnalites.html#h-tree","Familles de personnalités"]},{"i":"micael","t":"Micaël","e":"Michael","d":"Le Fils Créateur de notre univers local, Nébadon. Pour en recevoir la pleine souveraineté, il s’est effusé sept fois sous la forme de ses propres créatures ; la septième et dernière fois, il a vécu sur Urantia comme un homme.","r":["33:1.1","119:0.3","32:0.3"],"f":["Micaël de Nébadon","Micaël de Salvington","Christ Micaël","Micaël"],"c":["Urantia appartient à un univers local dont le souverain est l’homme-Dieu de Nébadon, Jésus de Nazareth et Micaël de Salvington.","32:0.3"],"a":["vie-de-jesus.html","La vie de Jésus"]},{"i":"mondes-des-maisons","t":"mondes des maisons","e":"mansion worlds","d":"Les sept satellites du premier monde de transition de Jérusem, où les humains se réveillent après la mort. On y corrige les lacunes de la vie terrestre ; le nom rappelle les « nombreuses maisons » dont Jésus a parlé.","r":["47:0.1","15:7.5","47:3.8"],"f":["mondes des maisons","monde des maisons"],"c":["À la manière dont le mot ciel a été employé sur Urantia, il a quelquefois désigné ces sept mondes des maisons […]","15:7.5"],"a":["destinee-humaine.html#maisons","La destinée humaine"]},{"i":"monmatia","t":"Monmatia","e":"Monmatia","d":"Nom de notre système solaire : le Soleil et sa famille de planètes, dont Urantia. Son origine est exceptionnelle : moins d’un pour cent des systèmes planétaires d’Orvonton sont nés de la même façon.","r":["57:5.3","57:6.9"],"f":["Monmatia"],"c":["Vers cette époque, votre système solaire fut inscrit sur le registre physique de Nébadon et reçut le nom de Monmatia.","57:6.9"],"a":["atlas-3d.html#monmatia","D’Urantia au Paradis (3D)"]},{"i":"morontia","t":"morontia","e":"morontia","d":"Niveau de réalité qui s’étend entre le monde matériel et celui de l’esprit (adjectif : morontiel). Après la mort, le survivant le traverse en recevant 570 corps morontiels successifs, du système local jusqu’à Salvington, avant de devenir esprit.","r":["0:5.12","48:1.5","48:1.1"],"f":["morontia","morontiel","morontielle","morontiels","morontielles"],"c":["Morontia est un terme désignant un vaste niveau intermédiaire entre le matériel et le spirituel.","0:5.12"],"a":["concepts-en-schemas.html#s7","Concepts en schémas"]},{"i":"nebadon","t":"Nébadon","e":"Nebadon","d":"Notre univers local, dont le souverain est Micaël, le Fils Créateur qui a vécu sur Urantia en Jésus. Il comptait 3 840 101 planètes habitées à la dernière inscription et se trouve près du bord extérieur d’Orvonton.","r":["32:0.3","32:2.9","32:2.11"],"f":["Nébadon"],"c":["L’organisation des demeures planétaires est encore en voie de progrès dans Nébadon, car cet univers est en vérité un jeune amas dans les royaumes stellaires et planétaires d’Orvonton.","32:2.9"],"a":["atlas-3d.html#nebadon","D’Urantia au Paradis (3D)"]},{"i":"andronover","t":"nébuleuse d’Andronover","e":"Andronover nebula","d":"Immense nébuleuse dont la formation commença il y a 875 milliards d’années. Plus d’un million de soleils en sont issus, dont le nôtre, né il y a environ six milliards d’années.","r":["57:1.6","57:4.8","57:4.9"],"f":["nébuleuse d’Andronover","Andronover"],"c":["Désormais, la grande nébuleuse d’Andronover n’existe plus, mais elle vit toujours dans les nombreux soleils et les familles planétaires qui ont leur origine dans ce nuage-mère de l’espace.","57:4.9"],"a":["histoire-d-urantia.html#h-frise","L’histoire d’Urantia"]},{"i":"nodites","t":"Nodites","e":"Nodites","d":"Peuple issu des soixante membres de l’état-major du Prince qui avaient suivi Caligastia, et nommé d’après leur chef, Nod. Les Nodites formèrent la huitième race d’Urantia et furent longtemps en guerre avec les Adamites.","r":["67:4.2","73:1.3","75:5.9"],"f":["Nodites","nodites","nodite","Nod"],"c":["Les descendants de ces membres furent connus longtemps sous le nom de Nodites, et leur lieu d’habitation comme « pays de Nod ».","67:4.2"],"a":["histoire-d-urantia.html#h-carte","L’histoire d’Urantia"]},{"i":"norlatiadek","t":"Norlatiadek","e":"Norlatiadek","d":"Notre constellation, numéro 70 de l’univers local de Nébadon, dont fait partie le système de Satania. Elle est gouvernée depuis Édentia par les Très Hauts, les Pères de la Constellation.","r":["15:14.6","43:0.2"],"f":["Norlatiadek"],"c":["Votre constellation, Norlatiadek, est composée de cent systèmes locaux ; elle possède un monde-siège appelé Édentia.","15:14.6"],"a":["atlas-3d.html#norlatiadek","D’Urantia au Paradis (3D)"]},{"i":"orvonton","t":"Orvonton","e":"Orvonton","d":"Le septième superunivers, auquel appartient notre univers local, Nébadon ; sa capitale est Uversa. Presque toutes les étoiles visibles à l’œil nu en font partie, et la Voie lactée en forme le « noyau central ».","r":["15:3.1","0:0.5","15:3.4"],"f":["Orvonton"],"c":["Si vous pouviez examiner le superunivers d’Orvonton depuis un emplacement très éloigné dans l’espace, vous reconnaitriez immédiatement les dix secteurs majeurs de la septième galaxie.","15:3.4"],"a":["nebadon-dans-orvonton.html","Nébadon dans Orvonton"]},{"i":"paradis","t":"Paradis","e":"Paradise (Isle of Paradise)","d":"Le centre immobile et éternel de toute la création, où demeurent le Père, le Fils et l’Esprit : une Ile immense, à la fois matérielle et spirituelle, d’où proviennent les univers physiques et vers laquelle converge leur gravité.","r":["11:0.1","0:4.12","0:3.13"],"f":["Ile du Paradis","Paradis","Ile"],"c":["L’Ile du Paradis a un emplacement dans l’univers mais pas de position dans l’espace.","0:4.12"],"a":["atlas-3d.html#paradis","D’Urantia au Paradis (3D)"]},{"i":"pentecote","t":"Pentecôte","e":"Pentecost","d":"Fête juive au cours de laquelle, selon le livre, l’Esprit de Vérité vint sur les disciples de Jésus réunis à Jérusalem. Depuis ce jour, cet esprit est répandu sur tous les humains, et tout mental normal capable de choix moral reçoit un Ajusteur.","r":["194:1.1","194:3.9","108:2.3"],"f":["Pentecôte"],"c":["Le jour de la Pentecôte marqua le grand effort de l’esprit pour libérer la religion de Jésus des entraves juives dont elle avait hérité.","194:3.9"],"a":["bible-et-livre.html#p-pentecote","La Bible et le Livre d’Urantia"]},{"i":"pere-universel","t":"Père Universel","e":"Universal Father","d":"Première Personne de la Déité, « le Dieu de toute la création » : la Source-Centre Première de toutes choses et le Père de toute personnalité. Les créatures du temps cherchent à le connaitre et à l’atteindre au Paradis.","r":["1:0.1","105:3.2","1:0.3"],"f":["Père Universel","Dieu le Père","Père Éternel"],"c":["Pensez d’abord à Dieu comme à un créateur, puis comme à un contrôleur, et enfin comme à un soutien infini.","1:0.1"],"a":["dieu-et-deite.html#s2","Dieu et la Déité"]},{"i":"perfecteurs-de-sagesse","t":"Perfecteurs de Sagesse","e":"Perfectors of Wisdom","d":"Êtres issus de la Trinité du Paradis qui personnifient la sagesse divine dans les superunivers. Ils sont sept milliards, un milliard par superunivers, au service des Anciens des Jours ; au besoin, ils agissent en trio avec un Censeur Universel et des Conseillers Divins.","r":["19:2.1-2","19:2.3","19:3.3"],"f":["Perfecteurs de Sagesse","Perfecteur de Sagesse"],"c":["Elles ne reflètent pas la sagesse de la Trinité du Paradis, elles sont cette sagesse.","19:2.3"],"a":["familles-de-personnalites.html#h-tree","Familles de personnalités"]},{"i":"personnalite","t":"personnalité","e":"personality","d":"Don unique du Père Universel, qui fait d’un être une personne ; au pluriel, le mot désigne souvent les êtres eux-mêmes. Elle n’est ni le corps, ni le mental, ni l’esprit, ni l’âme, mais elle unifie l’ensemble de l’individu.","r":["0:5.11","112:0.1","112:0.3"],"f":["personnalité","personnalités"],"c":["[…] une partie de vous reste toujours absolument inchangée ; c’est la personnalité — la permanence en présence du changement.","112:0.1"],"a":["concepts-en-schemas.html#s1","Concepts en schémas"]},{"i":"personnalites-supremes-de-la-trinite","t":"Personnalités Suprêmes de la Trinité","e":"Supreme Trinity Personalities","d":"Sept ordres d’administrateurs issus de la Trinité, créés une fois pour toutes : Secrets de Suprématie Trinitisés, Éternels, Anciens, Perfections, Récents, Unions et Fidèles des Jours. Leur administration s’étend des sphères du Père, près du Paradis, jusqu’aux capitales des univers locaux.","r":["18:0.1-8","18:0.9","18:0.10"],"f":["Personnalités Suprêmes de la Trinité","Personnalité Suprême de la Trinité","Secrets de Suprématie Trinitisés","Secrets de Suprématie","Éternels des Jours","Éternel des Jours","Perfections des Jours","Perfection des Jours","Récents des Jours","Récent des Jours","Unions des Jours","Union des Jours","Fidèles des Jours","Fidèle des Jours"],"c":["Elles représentent la justice et sont le jugement exécutoire de la Trinité du Paradis.","18:0.10"],"a":["familles-de-personnalites.html#h-tree","Familles de personnalités"]},{"i":"porteurs-de-vie","t":"Porteurs de Vie","e":"Life Carriers","d":"Fils de l’univers local chargés de concevoir la vie physique et de l’établir sur les planètes, où ils restent pour veiller à son évolution. Sur Urantia, ils l’élaborèrent sur place et l’implantèrent dans les mers il y a 550 millions d’années.","r":["36:0.1","58:4.1","58:4.2"],"f":["Porteurs de Vie","Porteur de Vie"],"c":["La vie sur Urantia est unique et a son origine sur cette planète.","58:4.1"],"a":["histoire-d-urantia.html#h-frise","L’histoire d’Urantia"]},{"i":"prince-planetaire","t":"Prince Planétaire","e":"Planetary Prince","d":"Fils Lanonandek secondaire chargé de gouverner un monde habité dès les débuts de son humanité. Celui d’Urantia, Caligastia, est déchu ; c’est désormais Micaël qui détient le titre de Prince Planétaire d’Urantia.","r":["50:0.1","50:1.1","93:10.6"],"f":["Prince Planétaire","Princes Planétaires"],"c":["Sur un monde nouvellement habité, le Prince Planétaire est le seul représentant dont la divinité soit complète.","50:1.1"],"a":["rebellion-de-lucifer.html#echelles","La rébellion de Lucifer"]},{"i":"quarantaine","t":"quarantaine","e":"quarantine","d":"Mise à l’écart des mondes ou des systèmes tombés dans la rébellion, partiellement coupés du reste de la création pour la protéger. Le système de Satania y fut placé dès la révolte de Lucifer, et Urantia reste en quarantaine spirituelle partielle.","r":["3:1.10","67:3.1","28:7.4"],"f":["quarantaine"],"c":["Tout ceci, comme c’est le cas pour Urantia, est une réaction spirituellement défensive de la majorité des mondes.","3:1.10"],"a":["rebellion-de-lucifer.html#isolement","La rébellion de Lucifer"]},{"i":"sangiks","t":"races Sangik","e":"Sangik races","d":"Les six races de couleur — rouge, orangée, jaune, verte, bleue et indigo — issues des dix-neuf enfants d’une même famille, la famille Sangik, née il y a environ 500 000 ans dans les hautes terres du nord-ouest de l’Inde.","r":["64:5.2","64:5.1","64:5.3"],"f":["races Sangik","races sangik","races sangiks","famille Sangik","sangiks","sangik"],"c":["[…] leur peau manifestait en outre une tendance extraordinaire à prendre différentes couleurs quand elle était exposée à la lumière solaire.","64:5.3"],"a":["histoire-d-urantia.html#h-carte","L’histoire d’Urantia"]},{"i":"royaume-des-cieux","t":"royaume des cieux","e":"kingdom of heaven","d":"Thème central de l’enseignement de Jésus, qui disait aussi royaume de Dieu. Le livre y voit surtout une réalité spirituelle intérieure, fondée sur la paternité de Dieu et la fraternité des hommes, et non un royaume terrestre.","r":["170:0.1","170:1.13","170:2.1"],"f":["royaume des cieux","royaume de Dieu"],"c":["Mais, à ses apôtres, il enseigna toujours le royaume comme embrassant l’expérience personnelle d’un homme par rapport à ses contemporains sur terre et au Père dans les cieux.","170:1.13"],"a":["bible-et-livre.html#p-ivraie-seneve","La Bible et le Livre d’Urantia"]},{"i":"saint-esprit","t":"Saint-Esprit","e":"Holy Spirit","d":"Le circuit spirituel de l’Esprit-Mère, propre à chaque univers local : l’esprit de sa présence sur les mondes habités. Il agit sur l’homme bien avant la venue de l’Esprit de Vérité et des Ajusteurs ; le livre le distingue de l’Esprit Infini, présent partout.","r":["8:5.3","36:5.16","103:0.1"],"f":["Saint-Esprit"],"c":["La première dotation supramentale de l’homme est la mise en circuit de sa personnalité dans le Saint-Esprit de l’Esprit Créatif de l’univers […]","103:0.1"],"a":["concepts-en-schemas.html#s2","Concepts en schémas"]},{"i":"salvington","t":"Salvington","e":"Salvington","d":"Capitale de Nébadon, notre univers local, située au centre d’énergie massique de cet univers et quartier général de Micaël. C’est là que les ascendeurs reçoivent leur formation spirituelle, après la formation sociale de la constellation.","r":["32:2.4","32:2.5","15:7.7"],"f":["Salvington"],"c":["Salvington, capitale de Nébadon, votre univers local, est entourée de dix groupes universitaires de quarante-neuf sphères chacun.","15:7.7"],"a":["atlas-3d.html#nebadon","D’Urantia au Paradis (3D)"]},{"i":"satan","t":"Satan","e":"Satan","d":"Fils Lanonandek primaire, premier assistant de Lucifer, avec qui il régnait sur Jérusem et qu’il suivit dans la rébellion. Il est aujourd’hui détenu avec lui sur les mondes-prisons de Jérusem.","r":["53:1.4","53:2.1","53:9.4"],"f":["Satan"],"c":["On a très peu entendu parler de Lucifer sur Urantia parce qu’il délégua Satan, son premier lieutenant, pour plaider sa cause sur votre planète.","53:1.4"],"a":["rebellion-de-lucifer.html#camps","La rébellion de Lucifer"]},{"i":"satania","t":"Satania","e":"Satania","d":"Notre système local, numéro 24 de la constellation de Norlatiadek : 619 mondes habités, dont Urantia, avec Jérusem pour capitale. Son ancien souverain, Lucifer, s’y est rebellé.","r":["15:14.5","15:14.6","53:1.3"],"f":["Satania"],"c":["Lucifer est maintenant le Souverain déchu et déposé de Satania.","53:1.3"],"a":["atlas-3d.html#satania","D’Urantia au Paradis (3D)"]},{"i":"second-jardin","t":"second jardin","e":"second garden","d":"Nouvel établissement fondé par Adam, Ève et leurs partisans entre le Tigre et l’Euphrate, en Mésopotamie, après qu’ils eurent abandonné le premier jardin. Il resta pendant près de trente-mille ans le berceau de la civilisation.","r":["76:0.1","76:1.4","78:0.1"],"f":["second jardin","Second Jardin","second Éden","nouvel Éden"],"c":["Ils avaient trouvé le premier jardin partiellement préparé pour eux, mais il leur fallut créer le second par le travail de leurs propres mains […]","76:1.4"],"a":["histoire-d-urantia.html#h-carte","L’histoire d’Urantia"]},{"i":"secteur-majeur","t":"secteur majeur","e":"major sector","d":"Grande division d’un superunivers, gouvernée par trois Perfections des Jours depuis un siège grandiose. Orvonton en compte dix ; le nôtre, Splandon, est le cinquième.","r":["15:2.7","15:2.8","15:14.7"],"f":["secteur majeur","secteurs majeurs"],"c":["Cent secteurs mineurs (environ cent-milliards de planètes habitables) forment un secteur majeur.","15:2.7"],"a":["nebadon-dans-orvonton.html#h-zoom","Nébadon dans Orvonton"]},{"i":"secteur-mineur","t":"secteur mineur","e":"minor sector","d":"Division d’un secteur majeur, administrée par trois Récents des Jours depuis un monde-siège. Chaque secteur majeur en compte cent ; le nôtre est Ensa.","r":["15:2.6","15:2.7","15:14.7"],"f":["secteur mineur","secteurs mineurs"],"c":["Cent univers locaux (environ un milliard de planètes habitables) constituent un secteur mineur du gouvernement du superunivers.","15:2.6"],"a":["nebadon-dans-orvonton.html#h-zoom","Nébadon dans Orvonton"]},{"i":"sept-absolus","t":"sept Absolus","e":"Seven Absolutes of Infinity","d":"Les sept réalités éternelles sur lesquelles repose toute réalité : le Père (Source-Centre Première), le Fils Éternel, l’Esprit Infini, l’Ile du Paradis, l’Absolu de Déité, l’Absolu Universel et l’Absolu Non Qualifié. Le livre les présente en séquence, mais aucun n’a eu de commencement.","r":["105:3.1","0:3.1-8","105:3.10"],"f":["Sept Absolus de l’Infinité","sept Absolus","Sept Absolus","Absolus"],"c":["Les sept relations primordiales à l’intérieur du JE SUIS s’éternisent sous l’aspect des Sept Absolus de l’Infinité.","105:3.1"],"a":["dieu-et-deite.html#s1","Dieu et la Déité"]},{"i":"maitres-esprits","t":"Sept Maitres Esprits","e":"Seven Master Spirits","d":"Les sept personnalités primaires de l’Esprit Infini. Chaque Maitre Esprit exprime l’une des sept associations possibles du Père, du Fils et de l’Esprit et imprègne de sa nature l’un des sept superunivers ; le Septième, qui unit les trois, régit le nôtre, Orvonton.","r":["16:0.1","16:5.1","16:3.20"],"f":["Sept Maitres Esprits","Maitres Esprits","Maitre Esprit"],"c":["[…] il y a juste sept possibilités d’association, et seulement sept, qui soient inhérentes à trois Déités.","16:0.1"],"a":["dieu-et-deite.html#s4","Dieu et la Déité"]},{"i":"serapatatia","t":"Sérapatatia","e":"Serapatatia","d":"Chef nodite de la confédération syrienne, devenu proche d’Adam et Ève. Impatient de voir des résultats, il suggéra à Ève de donner aux Nodites un chef ayant du sang violet, projet qui mena à la défaillance.","r":["75:3.1","75:3.5","75:3.6"],"f":["Sérapatatia"],"c":["Il y a lieu de souligner de nouveau que Sérapatatia était complètement honnête et totalement sincère dans toutes ses propositions.","75:3.6"],"a":["bible-et-livre.html#p-eve","La Bible et le Livre d’Urantia"]},{"i":"seraphins","t":"séraphins","e":"seraphim","d":"Anges de l’univers local, créés par l’Esprit-Mère, qui servent auprès des mondes et des mortels. Certains deviennent les gardiens de la destinée d’une personne ; à la mort, c’est à son gardien que l’âme est confiée.","r":["38:1.1","113:1.1","112:3.5"],"f":["séraphins","séraphin","séraphique","séraphiques"],"c":["L’enseignement au sujet des anges gardiens n’est pas un mythe ; certains groupes d’êtres humains ont effectivement des anges personnels.","113:1.1"],"a":["familles-de-personnalites.html#h-tree","Familles de personnalités"]},{"i":"source-centre","t":"Source-Centre","e":"Source and Center (First Source and Center…)","d":"Nom que le livre donne aux réalités premières, à la fois sources et centres : la Source-Centre Première est le Père Universel, la Deuxième le Fils Éternel, la Troisième l’Esprit Infini ; l’Ile du Paradis en est une aussi. Gravité, esprit et mental convergent vers elles.","r":["105:3.2-5","0:3.11","0:3.13-15"],"f":["Source-Centre Première","Source-Centre Deuxième","Source-Centre Troisième","Source-Centre du Paradis","Source-Centre","Sources-Centres"],"c":["La Source-Centre Première est donc primordiale dans tous les domaines : déifiés ou non déifiés, personnels ou impersonnels, actuels ou potentiels, finis ou infinis.","0:3.11"],"a":["dieu-et-deite.html#s1","Dieu et la Déité"]},{"i":"splandon","t":"Splandon","e":"Splandon","d":"Notre secteur majeur, le cinquième d’Orvonton : il réunit cent secteurs mineurs, dont le nôtre, Ensa. Sa capitale est Umajor la cinquième.","r":["15:14.7","15:7.9"],"f":["Splandon"],"c":["Umajor la cinquième, siège de Splandon, votre secteur majeur, est entourée par les soixante-dix sphères d’enseignement intellectuel supérieur des superunivers.","15:7.9"],"a":["atlas-3d.html#splandon","D’Urantia au Paradis (3D)"]},{"i":"superunivers","t":"superunivers","e":"superuniverse","d":"Chacune des sept immenses créations évolutionnaires qui entourent Havona et forment avec lui le grand univers. Chaque superunivers est gouverné par trois Anciens des Jours depuis sa capitale ; le nôtre est Orvonton.","r":["15:2.8","0:0.5","15:2.9"],"f":["superunivers","superuniversel","superuniverselle","superuniversels","superuniverselles"],"c":["Dix secteurs majeurs (environ mille milliards de planètes habitables) constituent un superunivers.","15:2.8"],"a":["atlas-3d.html#grand-univers","D’Urantia au Paradis (3D)"]},{"i":"suprematie","t":"Suprématie","e":"Supremacy","d":"Premier niveau où la Déité s’identifie aux créatures et agit sur le grand univers du temps et de l’espace. C’est le niveau de l’Être Suprême, Déité expérientielle qui unit la créature au Créateur.","r":["0:1.9","0:1.11"],"f":["Suprématie"],"c":["Le niveau de Déité de la Suprématie peut être conçu comme une fonction relative aux existences finies.","0:1.11"],"a":["concepts-en-schemas.html#s5","Concepts en schémas"]},{"i":"survie","t":"survie","e":"survival","d":"Le fait, pour la personnalité humaine, de continuer à vivre après la mort, sous une forme morontielle. Elle n’est pas automatique : elle dépend des décisions sincères et persévérantes de la personne dans sa quête de Dieu.","r":["112:2.20","112:5.2","47:3.3"],"f":["survie","survivant","survit"],"c":["Et c’est la réunion de l’âme morontielle confiée aux séraphins et du mental spirituel confié à l’Ajusteur qui reconstitue la personnalité de la créature […]","47:3.3"],"a":["destinee-humaine.html#schema","La destinée humaine"]},{"i":"systeme-local","t":"système local","e":"local system","d":"Unité de base de l’organisation de l’univers, gouvernée par un Souverain Systémique depuis sa capitale : environ mille mondes habités ou habitables. Cent systèmes forment une constellation ; le nôtre est Satania.","r":["15:2.3","15:2.4","15:14.6"],"f":["système local","systèmes locaux"],"c":["On appelle système cet ensemble de mille mondes aptes à entretenir la vie, mais, dans les systèmes jeunes, seul un nombre relativement restreint de ces mondes peut être habité.","15:2.3"],"a":["nebadon-dans-orvonton.html#h-zoom","Nébadon dans Orvonton"]},{"i":"trinite-du-paradis","t":"Trinité du Paradis","e":"Paradise Trinity","d":"Union éternelle du Père, du Fils et de l’Esprit en une seule Déité. Le livre lui reconnait des fonctions plutôt que des attributs, comme l’administration de la justice. Deux autres Trinités, expérientielles, sont encore en formation : l’Ultime et l’Absolue.","r":["0:12.2-5","10:5.1","10:4.3"],"f":["Trinité du Paradis","Trinité Paradisiaque","Trinité","Trinités"],"c":["La Trinité est une association de personnes infinies fonctionnant impersonnellement, mais sans contrevenir à la personnalité.","10:4.3"],"a":["dieu-et-deite.html#s3","Dieu et la Déité"]},{"i":"triunites","t":"triunités","e":"triunities","d":"Associations de fonction entre les Absolus, par lesquelles le Père Universel, membre de chacune, exerce un contrôle personnel sur les grandes fonctions de l’infinité. Le livre en décrit sept ; la première réunit le Père, le Fils et l’Esprit agissant ensemble en tant que personnes.","r":["104:4.1","104:3.18","104:3.14"],"f":["triunités","triunité"],"c":["Les triunités n’en sont pas moins réelles, très réelles.","104:3.18"],"a":["dieu-et-deite.html#s3","Dieu et la Déité"]},{"i":"ultimite","t":"Ultimité","e":"Ultimacy","d":"Niveau où la Déité agit en rapport avec les réalités absonites, au-delà du temps et de l’espace, à l’échelle du maitre univers. C’est le second niveau expérientiel de la Déité, celui de Dieu l’Ultime.","r":["0:1.12","0:1.10","0:2.17"],"f":["Ultimité"],"c":["Où que ce soit dans le maitre univers, quand le temps et l’espace sont transcendés, ce phénomène absonite est un acte de l’Ultimité de la Déité.","0:1.12"],"a":["concepts-en-schemas.html#s5","Concepts en schémas"]},{"i":"univers-local","t":"univers local","e":"local universe","d":"Création d’un Fils Créateur, un Micaël, associé à un Esprit-Mère : il s’étend aussi loin que la présence de cet Esprit. Le nôtre est Nébadon.","r":["32:0.1","15:2.5","41:0.1"],"f":["univers local","univers locaux"],"c":["Cent constellations (environ dix-millions de planètes habitables) constituent un univers local.","15:2.5"],"a":["nebadon-dans-orvonton.html#h-zoom","Nébadon dans Orvonton"]},{"i":"urantia","t":"Urantia","e":"Urantia","d":"Nom que le livre donne à notre planète, la Terre, et qui figure dans son titre. C’est le monde habité numéro 606 du système de Satania, dans l’univers local de Nébadon.","r":["15:14.5","0:0.5","43:0.1"],"f":["Urantia"],"c":["Votre monde, Urantia, est l’une des nombreuses planètes habitées similaires comprises dans l’univers local de Nébadon.","0:0.5"],"a":["atlas-3d.html#urantia","D’Urantia au Paradis (3D)"]},{"i":"uversa","t":"Uversa","e":"Uversa","d":"Capitale du superunivers d’Orvonton, d’où les ascendeurs partent pour Havona après une dernière préparation. C’est sur l’ordre des Anciens des Jours d’Uversa qu’une commission de vingt-quatre administrateurs d’Orvonton a présenté les fascicules 1 à 31 du livre.","r":["15:7.10","31:10.22","0:0.5"],"f":["Uversa"],"c":["Uversa, siège d’Orvonton, votre superunivers, est immédiatement entourée par les sept universités supérieures de haute éducation spirituelle pour les créatures volitives ascendantes.","15:7.10"],"a":["atlas-3d.html#orvonton","D’Urantia au Paradis (3D)"]},{"i":"van-et-amadon","t":"Van et Amadon","e":"Van and Amadon","d":"Van, membre loyal de l’état-major du Prince, et Amadon, son associé humain descendant d’Andon et Fonta, résistèrent à la rébellion de Caligastia. Maintenus en vie plus de cent-cinquante-mille ans, ils préparèrent ensuite la venue d’Adam et Ève.","r":["67:3.8","67:6.4","73:2.3"],"f":["Van et Amadon","Van","Amadon","Amadonites"],"c":["Amadon est le héros humain le plus remarquable de la rébellion de Lucifer.","67:3.8"],"a":["rebellion-de-lucifer.html#camps","La rébellion de Lucifer"]},{"i":"vorondadeks","t":"Vorondadeks","e":"Vorondadeks","d":"Ordre de Fils de l’univers local qui gouvernent les constellations sous le titre de Très Hauts ; le Très Haut régnant est appelé Père de la Constellation. Un observateur Vorondadek réside sur chaque monde isolé, dont Urantia.","r":["35:6.1","35:6.2","43:5.17"],"f":["Vorondadeks","Vorondadek","Très Hauts","Très Haut","Pères de la Constellation","Père de la Constellation","Pères des Constellations"],"c":["Les cent Pères des Constellations, les chefs actuels présidant les gouvernements des constellations, constituent le cabinet consultatif suprême du Fils Créateur.","35:6.2"],"a":["familles-de-personnalites.html#h-tree","Familles de personnalités"]},{"i":"yahweh","t":"Yahweh","e":"Yahweh","d":"Nom du Dieu des Hébreux. Le livre retrace l’évolution de ce concept : d’un dieu tribal de la nature, élargi par Moïse, jusqu’au Créateur suprême et Père aimant de toute l’humanité ; la vie de Jésus l’amplifia encore.","r":["96:1.3","96:4.2","97:10.8"],"f":["Yahweh"],"c":["Yahweh était le dieu des tribus palestiniennes du Sud, qui associèrent ce concept de la déité au mont Horeb, le volcan du Sinaï.","96:1.3"],"a":["bible-et-livre.html#p-sinai","La Bible et le Livre d’Urantia"]}],"exclusions":["adjuvats dodécuples"]};
  if (!DONNEES || !DONNEES.termes || !DONNEES.termes.length || !document.querySelector || !window.Map || !document.createTreeWalker) return;

  var SVGNS = 'http://www.w3.org/2000/svg';
  var NB = ' ';
  var PAGE_GLOSSAIRE = 'glossaire.html';
  // zones interdites : titres, barre, liens, boutons, citations, formulaires, pied, code, médias
  var NON_BALISES = {
    H1: 1, H2: 1, H3: 1, H4: 1, H5: 1, H6: 1, HGROUP: 1, NAV: 1, A: 1, BUTTON: 1, SUMMARY: 1, LABEL: 1, LEGEND: 1, CAPTION: 1, TH: 1,
    INPUT: 1, TEXTAREA: 1, SELECT: 1, OPTION: 1, OPTGROUP: 1, DATALIST: 1, OUTPUT: 1, METER: 1, PROGRESS: 1,
    BLOCKQUOTE: 1, Q: 1, CITE: 1, FOOTER: 1, SCRIPT: 1, STYLE: 1, NOSCRIPT: 1, TEMPLATE: 1, CODE: 1, PRE: 1, KBD: 1, SAMP: 1, VAR: 1,
    IFRAME: 1, CANVAS: 1, VIDEO: 1, AUDIO: 1, OBJECT: 1, EMBED: 1, MATH: 1, DIALOG: 1, DFN: 1, ABBR: 1, TITLE: 1
  };
  var NON_ROLES = {
    button: 1, link: 1, tab: 1, tablist: 1, menu: 1, menubar: 1, menuitem: 1, menuitemcheckbox: 1, menuitemradio: 1, option: 1,
    listbox: 1, heading: 1, navigation: 1, contentinfo: 1, 'switch': 1, checkbox: 1, radio: 1, combobox: 1, textbox: 1,
    searchbox: 1, slider: 1, spinbutton: 1, tree: 1, treeitem: 1, tooltip: 1, dialog: 1, alertdialog: 1, status: 1, alert: 1,
    log: 1, marquee: 1, timer: 1, toolbar: 1, img: 1
  };
  var NON_CLASSES = ['ref', 'bref', 'foot', 'vh', 'sr-only', 'visually-hidden', 'eyebrow', 'label', 'ctl-lbl', 'atlas-nav',
    'atlas-suite', 'atlas-credit', 'atlas-droits', 'aller-contenu', 'gl-mot', 'gl-bulle', 'gl-voile', 'gl-non'];
  // conteneurs « bloc » : l’état des guillemets « … » ne passe pas d’un bloc à l’autre
  var BLOCS = {
    P: 1, LI: 1, DD: 1, DT: 1, TD: 1, TH: 1, FIGCAPTION: 1, DIV: 1, SECTION: 1, ARTICLE: 1, ASIDE: 1, HEADER: 1, MAIN: 1, BODY: 1,
    FIGURE: 1, DETAILS: 1, UL: 1, OL: 1, DL: 1, TABLE: 1, TR: 1, TBODY: 1, FORM: 1, FIELDSET: 1, NAV: 1, FOOTER: 1, BLOCKQUOTE: 1
  };

  var MOT;   // un « mot » : lettres et chiffres, avec traits d’union internes (Esprit-Mère, état-major)
  try { MOT = new RegExp('[\\p{L}\\p{N}]+(?:[-‑][\\p{L}\\p{N}]+)*', 'gu'); } catch (e) {
    MOT = /[0-9A-Za-zÀ-ÖØ-öø-ɏŒœ]+(?:[-‑][0-9A-Za-zÀ-ÖØ-öø-ɏŒœ]+)*/g;
  }
  function cle(s) { return String(s).replace(/[\s  ]+/g, ' ').replace(/'/g, '’').replace(/‑/g, '-'); }
  function mots(s) {
    var r = [], m, w;
    MOT.lastIndex = 0;
    while ((m = MOT.exec(s))) { w = m[0]; r.push({ w: w.indexOf('‑') < 0 ? w : w.replace(/‑/g, '-'), s: m.index, e: m.index + w.length }); }
    return r;
  }
  function majuscule(s) { return s.charAt(0).toUpperCase() + s.slice(1); }

  // ── Index des formes : premier mot → variantes (les plus longues d’abord) ─────────────────────────
  var TERMES = Object.create(null), INDEX = new Map();
  DONNEES.termes.forEach(function (t) {
    if (!t || !t.i || !t.f) return;
    TERMES[t.i] = t;
    t.f.forEach(function (f) {
      var vars = [f], c = f.charAt(0);
      if (!t.s && c !== c.toUpperCase()) vars.push(majuscule(f));   // forme en minuscule : aussi en début de phrase
      vars.forEach(function (v) {
        var toks = mots(v).map(function (x) { return x.w; });
        if (!toks.length) return;
        if (!INDEX.has(toks[0])) INDEX.set(toks[0], []);
        INDEX.get(toks[0]).push({ id: t.i, toks: toks, cle: cle(v) });
      });
    });
  });
  // expressions à ne jamais marquer (ex. « adjuvats dodécuples », un autre ordre) : reconnues comme formes, sans terme
  (DONNEES.exclusions || []).forEach(function (v) {
    var toks = mots(v).map(function (x) { return x.w; });
    if (!toks.length) return;
    if (!INDEX.has(toks[0])) INDEX.set(toks[0], []);
    INDEX.get(toks[0]).push({ id: null, toks: toks, cle: cle(v) });
  });
  var PREMIERS = [];
  INDEX.forEach(function (l, k) {
    l.sort(function (a, b) { return b.toks.length - a.toks.length || b.cle.length - a.cle.length; });
    PREMIERS.push(k);
  });
  if (!PREMIERS.length) return;
  // tri rapide des nœuds de texte : seul un texte qui contient l’un des premiers mots est découpé en mots
  var PRE = new RegExp(PREMIERS.sort(function (a, b) { return b.length - a.length; }).map(function (k) {
    return k.replace(/[.*+?^${}()|[\]\\]/g, '\\$&').replace(/-/g, '[-\u2011]');
  }).join('|'));

  // ── Zones permises ─────────────────────────────────────────────────────────────────────────────────
  var RX_CLASSES = new RegExp('(?:^|\\s)(?:' + NON_CLASSES.join('|') + ')(?=\\s|$)');
  function exclu(el) {
    if (NON_BALISES[el.tagName] || el.namespaceURI === SVGNS) return true;
    if (!el.hasAttributes()) return false;                 // cas le plus courant : rien d’autre à lire
    var c = el.getAttribute('class');
    if (c && RX_CLASSES.test(c)) return true;
    if (el.hasAttribute('hidden') || el.hasAttribute('inert') || el.hasAttribute('contenteditable') || el.hasAttribute('aria-live') ||
      el.hasAttribute('onclick') || el.getAttribute('aria-hidden') === 'true' || el.getAttribute('data-glossaire') === 'non') return true;
    var r = el.getAttribute('role');
    if (r && NON_ROLES[r]) return true;
    var ti = el.getAttribute('tabindex');
    if (ti !== null && +ti >= 0) return true;
    var lg = el.getAttribute('lang');
    return !!(lg && !/^fr(-|$)/i.test(lg));
  }
  function blocDe(n) { var e = n.parentNode; while (e && e.nodeType === 1 && !BLOCS[e.tagName]) e = e.parentNode; return e; }
  // plages entre guillemets d’un texte, l’état (profondeur) venant du nœud précédent du même bloc
  function guillemets(s, d) {
    var r = [], a = d > 0 ? 0 : -1;
    for (var i = 0; i < s.length; i++) {
      var c = s.charCodeAt(i);
      if (c === 0xAB || c === 0x201C) { if (d === 0) a = i; d++; }
      else if ((c === 0xBB || c === 0x201D) && d > 0) { d--; if (d === 0) { r.push([a, i + 1]); a = -1; } }
    }
    if (d > 0) r.push([a < 0 ? 0 : a, s.length]);
    return { r: r, d: d };
  }
  function cite(g, a, b) { if (!g) return false; for (var i = 0; i < g.r.length; i++) if (a < g.r[i][1] && b > g.r[i][0]) return true; return false; }
  // texte admissible : visible, et dont le parent n’est pas une boite flex ou grille (y poser un bouton créerait un
  // nouvel élément de la boite et décalerait la mise en page)
  var vues = null, RX_BOITE = /^(?:inline-)?(?:flex|grid)$/;
  function admissible(el) {
    var v = vues.get(el);
    if (v !== undefined) return v;
    try {
      v = el.checkVisibility ? el.checkVisibility({ checkVisibilityCSS: true, visibilityProperty: true }) : el.getClientRects().length > 0;
      if (v) v = !RX_BOITE.test(getComputedStyle(el).display);
    } catch (e) { v = true; }
    vues.set(el, v);
    return v;
  }

  // ── Repérage (lecture seule), puis pose des boutons en une passe ───────────────────────────────────
  // Parcours des seuls nœuds de texte (sans filtre JavaScript, plus rapide) ; l’exclusion d’un élément est mémorisée
  // et vaut pour tout son sous-arbre.
  var zones = null;
  function bloque(e) {
    if (!e || e === document.body || e.nodeType !== 1) return false;
    var v = zones.get(e);
    if (v === undefined) { v = exclu(e) || bloque(e.parentNode); zones.set(e, v); }
    return v;
  }
  // Le repérage est découpé en tranches de 8 ms au plus (aucune tâche longue, même sur la page Bible) ; fin(trouves)
  // est appelée à la fin. La durée de travail cumulée est mesurée (performance.measure « glossaire »).
  var TRANCHE = 8;
  function reperer(cherches, reste, fin) {
    var trouves = [], travail = 0, tranches = 0;
    vues = new Map();
    zones = new Map();
    var w = document.createTreeWalker(document.body, 4 /* textes */);
    var suivant = null, bloc = null, prof = 0;
    function tranche() {
      var t0 = performance.now(), limite = t0 + TRANCHE, compte = 0;
      tranches++;
      while (reste > 0) {
        if (!suivant && !(suivant = w.nextNode())) break;
        if ((++compte & 31) === 0 && performance.now() > limite) {     // la suite à la prochaine tranche
          travail += performance.now() - t0;
          bientot(tranche);
          return;
        }
        if (suivant.parentNode) traiter(suivant);
        suivant = null;
      }
      travail += performance.now() - t0;
      vues = zones = null;
      fin(trouves, travail, tranches);
    }
    tranche();
    function traiter(n) {
      var s = n.nodeValue;
      if (s.length < 2 || bloque(n.parentNode)) return;
      var b = blocDe(n);
      if (b !== bloc) { bloc = b; prof = 0; }
      var g = (prof > 0 || /[«»“”]/.test(s)) ? guillemets(s, prof) : null;
      if (g) prof = g.d;
      if (!PRE.test(s)) return;
      var vu = null, ts = mots(s);
      for (var i = 0; i < ts.length && reste > 0; i++) {
        var cands = INDEX.get(ts[i].w);
        if (!cands) continue;
        for (var k = 0; k < cands.length; k++) {
          var v = cands[k], nt = v.toks.length;
          if (i + nt > ts.length) continue;
          var ok = true;
          for (var j = 1; j < nt && ok; j++) ok = ts[i + j].w === v.toks[j];
          if (!ok) continue;
          var a = ts[i].s, z = ts[i + nt - 1].e;
          if (nt > 1 && cle(s.slice(a, z)) !== v.cle) continue;
          // forme reconnue : la plus longue l’emporte, même si son terme est déjà posé (ou si c’est une exclusion)
          if (v.id && cherches[v.id] && !cite(g, a, z)) {
            if (vu === null) vu = admissible(n.parentNode);
            if (vu) { trouves.push({ n: n, a: a, l: z - a, id: v.id }); cherches[v.id] = false; reste--; }
          }
          i += nt - 1;
          break;
        }
        if (vu === false) break;
      }
    }
  }
  var marques = Object.create(null);   // id → bouton posé
  function creerMot(id) {
    var s = document.createElement('span');
    s.className = 'gl-mot';
    s.setAttribute('role', 'button');
    s.setAttribute('tabindex', '0');
    s.setAttribute('aria-haspopup', 'dialog');
    s.setAttribute('aria-expanded', 'false');
    s.setAttribute('aria-controls', 'gl-bulle');
    s.setAttribute('data-gl', id);
    s.addEventListener('click', surClic);
    s.addEventListener('keydown', surTouche);
    return s;
  }
  function poser(trouves) {
    var n = 0;
    for (var k = trouves.length - 1; k >= 0; k--) {          // de la fin vers le début : les positions restent justes
      var t = trouves[k], tx = t.n;
      if (!tx.parentNode || tx.nodeValue.length < t.a + t.l || (marques[t.id] && marques[t.id].isConnected)) continue;
      var m = tx.splitText(t.a);
      m.splitText(t.l);
      var s = creerMot(t.id);
      m.parentNode.replaceChild(s, m);
      s.appendChild(m);
      marques[t.id] = s;
      n++;
    }
    return n;
  }
  var enCours = false, encore = false;
  function balayer(fin) {
    if (enCours) { encore = true; return; }
    var cherches = Object.create(null), reste = 0;
    for (var id in TERMES) if (!marques[id] || !marques[id].isConnected) { cherches[id] = true; reste++; delete marques[id]; }
    if (!reste) { if (fin) fin(0, 0, 0); return; }
    enCours = true;
    reperer(cherches, reste, function (trouves, travail, tranches) {   // lecture seule : la mise en page n’est calculée qu’une fois
      var t1 = performance.now(), n = 0;
      if (trouves.length) { styler(); n = poser(trouves); }
      if (observateur) observateur.takeRecords();          // nos propres changements ne relancent pas le repérage
      enCours = false;
      if (fin) fin(n, travail + performance.now() - t1, tranches);
      if (encore) { encore = false; planifier(); }
    });
  }
  function styler() {                       // feuille de style posée après le repérage (sinon recalcul de toute la page)
    if (document.getElementById('gl-style')) return;
    var st = document.createElement('style');
    st.id = 'gl-style';
    st.textContent = CSS;
    document.head.appendChild(st);
  }

  // ── Bulle (bureau) et tiroir (téléphone) ───────────────────────────────────────────────────────────
  var bulle = null, voile = null, defil, elT, elEn, elEnI, elD, elC, elCp, elCr, elO, elL, fleche, btnX;
  var courant = null, ouvert = false, tiroir = false, minuterieFermeture = null, pointClic = null;
  var mqTel = window.matchMedia ? window.matchMedia('(max-width: 640px)') : { matches: false };
  var mqCalme = window.matchMedia ? window.matchMedia('(prefers-reduced-motion: reduce)') : { matches: false };
  function el(tag, cls, parent) { var e = document.createElement(tag); if (cls) e.className = cls; if (parent) parent.appendChild(e); return e; }
  function construire() {
    voile = el('div', 'gl-voile', document.body);
    voile.hidden = true;
    voile.setAttribute('aria-hidden', 'true');
    voile.addEventListener('click', function () { fermer(true); });
    bulle = el('div', 'gl-bulle', document.body);
    bulle.id = 'gl-bulle';
    bulle.hidden = true;
    bulle.setAttribute('role', 'dialog');
    bulle.setAttribute('aria-modal', 'false');
    bulle.setAttribute('aria-labelledby', 'gl-t');
    bulle.setAttribute('aria-describedby', 'gl-d');
    bulle.setAttribute('tabindex', '-1');
    bulle.setAttribute('data-glossaire', 'non');
    fleche = el('span', 'gl-fleche', bulle);
    fleche.setAttribute('aria-hidden', 'true');
    el('span', 'gl-poignee', bulle).setAttribute('aria-hidden', 'true');
    defil = el('div', 'gl-defil', bulle);
    el('p', 'gl-sur', defil).textContent = 'Glossaire · selon le Livre d’Urantia';
    elT = el('p', 'gl-t', defil);
    elT.id = 'gl-t';
    elT.setAttribute('role', 'heading');
    elT.setAttribute('aria-level', '2');
    elEn = el('p', 'gl-en', defil);
    elEn.appendChild(document.createTextNode('En anglais' + NB + ': '));
    elEnI = el('i', '', elEn);
    elEnI.setAttribute('lang', 'en');
    elD = el('p', 'gl-d', defil);
    elD.id = 'gl-d';
    elC = el('figure', 'gl-c', defil);
    elCp = el('p', '', el('blockquote', '', elC));
    elCr = el('figcaption', '', elC);
    elO = el('p', 'gl-o', defil);
    elL = el('p', 'gl-l', defil);
    btnX = el('button', 'gl-x', bulle);
    btnX.type = 'button';
    btnX.setAttribute('aria-label', 'Fermer la définition');
    btnX.innerHTML = '<svg viewBox="0 0 20 20" width="18" height="18" aria-hidden="true" focusable="false"><path d="M5 5l10 10M15 5L5 15" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"/></svg>';
    btnX.addEventListener('click', function () { fermer(true); });
    bulle.addEventListener('keydown', function (e) {
      if (e.key !== 'Tab') return;                         // la tabulation reste dans la bulle tant qu’elle est ouverte
      var f = Array.prototype.filter.call(bulle.querySelectorAll('a[href], button'), function (x) { return !x.hidden && x.getClientRects().length; });
      if (!f.length) return;
      var i = f.indexOf(document.activeElement);
      if (e.shiftKey && (i <= 0)) { e.preventDefault(); f[f.length - 1].focus(); }
      else if (!e.shiftKey && (i === f.length - 1 || i < 0)) { e.preventDefault(); f[0].focus(); }
    });
    bulle.addEventListener('click', function (e) {          // un lien vers une ancre de la même page referme la bulle
      var a = e.target.closest && e.target.closest('a[href^="#"]');
      if (a) fermer(false);
    });
    // tiroir : glisser vers le bas le referme
    var y0 = null;
    bulle.addEventListener('touchstart', function (e) { y0 = tiroir && defil.scrollTop <= 0 && e.touches.length === 1 ? e.touches[0].clientY : null; }, { passive: true });
    bulle.addEventListener('touchmove', function (e) {
      if (y0 === null) return;
      var dy = e.touches[0].clientY - y0;
      if (dy > 0) bulle.style.transform = 'translateY(' + Math.round(dy) + 'px)';
    }, { passive: true });
    bulle.addEventListener('touchend', function (e) {
      if (y0 === null) return;
      var dy = (e.changedTouches[0] || {}).clientY - y0;
      y0 = null;
      bulle.style.transform = '';
      if (dy > 70) fermer(true);
    });
  }
  function ici() { var p = location.pathname.split('/').pop(); return p || 'index.html'; }
  function remplir(t) {
    elT.textContent = t.t;
    elEn.hidden = !t.e;
    elEnI.textContent = t.e || '';
    elD.textContent = t.d;
    elC.hidden = !t.c;
    elCr.textContent = '';
    if (t.c) {
      elCp.textContent = '«' + NB + t.c[0] + NB + '»';
      el('span', 'ref', elCr).textContent = t.c[1];
    }
    elO.textContent = '';
    var r = (t.r || []).filter(function (x) { return !t.c || x !== t.c[1]; });   // la référence de la citation est déjà sous elle
    elO.hidden = !r.length;
    if (r.length) {
      el('span', 'gl-lbl', elO).textContent = t.c ? 'Où lire aussi' : 'Où lire';
      r.forEach(function (x, i) {
        if (i) elO.appendChild(document.createTextNode(' '));
        el('span', 'ref', elO).textContent = x;
      });
    }
    elL.textContent = '';
    if (t.a && t.a[0]) {
      var p = t.a[0].split('#'), a;
      if (p[0] !== ici()) {
        a = el('a', 'gl-atlas', elL);
        a.href = t.a[0];
        a.textContent = 'Voir dans l’atlas' + NB + ': ' + t.a[1];
      } else if (p[1]) {
        a = el('a', 'gl-atlas', elL);
        a.href = '#' + p[1];
        a.textContent = 'Voir sur cette page';
      }
    }
    var g = el('a', 'gl-tout', elL);
    g.href = PAGE_GLOSSAIRE + '#' + t.i;
    g.textContent = 'Tout le glossaire';
  }
  function rectDe(s) {
    var rs = s.getClientRects();
    if (!rs.length) return null;
    if (pointClic) for (var i = 0; i < rs.length; i++) {
      var r = rs[i];
      if (pointClic.y >= r.top - 2 && pointClic.y <= r.bottom + 2 && pointClic.x >= r.left - 2 && pointClic.x <= r.right + 2) return r;
    }
    return rs[0];
  }
  function placer() {
    if (!ouvert || tiroir) return;
    if (!courant || !courant.isConnected) { fermer(false); return; }
    var r = rectDe(courant);
    var vw = document.documentElement.clientWidth || window.innerWidth, vh = window.innerHeight;
    if (!r || r.bottom < 0 || r.top > vh) { fermer(false); return; }
    var marge = 12, ecart = 10;
    var dessous = vh - r.bottom - ecart - marge, dessus = r.top - ecart - marge;
    var naturel = defil.scrollHeight + 2;                    // hauteur du contenu, bordures comprises
    var haut = naturel > dessous && dessus > dessous;
    var place = Math.max(haut ? dessus : dessous, 140);
    var mh = naturel > place ? place + 'px' : '';
    if (defil.style.maxHeight !== mh) defil.style.maxHeight = mh;
    var bw = bulle.offsetWidth, bh = bulle.offsetHeight;
    var x = Math.round(Math.max(marge, Math.min(r.left + r.width / 2 - bw / 2, vw - bw - marge)));
    var y = Math.round(haut ? r.top - ecart - bh : r.bottom + ecart);
    bulle.style.left = x + 'px';
    bulle.style.top = y + 'px';
    fleche.style.left = Math.round(Math.max(18, Math.min(r.left + r.width / 2 - x, bw - 18))) + 'px';
    bulle.classList.toggle('gl-haut', haut);
  }
  function ouvrir(s, parClavier) {
    var t = TERMES[s.getAttribute('data-gl')];
    if (!t) return;
    if (!bulle) construire();
    if (ouvert && courant === s) { fermer(true); return; }
    if (courant && courant !== s) courant.setAttribute('aria-expanded', 'false');
    clearTimeout(minuterieFermeture);
    courant = s;
    remplir(t);
    tiroir = !!mqTel.matches;
    bulle.classList.toggle('gl-tiroir', tiroir);
    bulle.setAttribute('aria-modal', tiroir ? 'true' : 'false');   // le tiroir, avec son voile, est modal ; la bulle ne l’est pas
    bulle.classList.remove('gl-ouvert', 'gl-haut');
    bulle.style.left = bulle.style.top = '';
    defil.style.maxHeight = '';
    voile.hidden = !tiroir;
    bulle.hidden = false;
    ouvert = true;
    s.setAttribute('aria-expanded', 'true');
    placer();
    if (mqCalme.matches) { bulle.classList.add('gl-ouvert'); voile.classList.add('gl-ouvert'); }
    else {
      void bulle.offsetWidth;                                // départ de la transition
      bulle.classList.add('gl-ouvert');
      voile.classList.add('gl-ouvert');
    }
    defil.scrollTop = 0;
    try { bulle.focus({ preventScroll: true }); } catch (e) { bulle.focus(); }
    if (parClavier) bulle.classList.add('gl-clavier'); else bulle.classList.remove('gl-clavier');
  }
  function fermer(rendreFocus) {
    if (!ouvert) return;
    ouvert = false;
    var s = courant;
    if (s) s.setAttribute('aria-expanded', 'false');
    bulle.classList.remove('gl-ouvert');
    voile.classList.remove('gl-ouvert');
    var fin = function () { if (!ouvert) { bulle.hidden = true; voile.hidden = true; } };
    if (mqCalme.matches) fin(); else minuterieFermeture = setTimeout(fin, 230);
    if (rendreFocus && s && s.isConnected) { try { s.focus({ preventScroll: true }); } catch (e) { s.focus(); } }
    courant = null;
  }
  function surClic(e) {
    e.preventDefault();
    e.stopPropagation();                                   // le conteneur de la page ne réagit pas au clic sur le mot
    pointClic = e.detail ? { x: e.clientX, y: e.clientY } : null;
    ouvrir(e.currentTarget, !e.detail);
  }
  function surTouche(e) {
    if (e.key === 'Enter' || e.key === ' ' || e.key === 'Spacebar') {
      e.preventDefault();
      e.stopPropagation();
      pointClic = null;
      ouvrir(e.currentTarget, true);
    }
  }

  // ── Style : jetons de couleur de la page (clair et sombre), sans décalage de mise en page ─────────
  var CSS = '.gl-mot{cursor:pointer;text-decoration-line:underline;text-decoration-style:dotted;text-decoration-thickness:1.25px;' +
    'text-underline-offset:.26em;text-decoration-color:var(--gold-ui,var(--gold,currentColor));' +
    'text-decoration-color:color-mix(in srgb,var(--gold-ui,var(--gold,currentColor)) 85%,transparent);border-radius:3px;' +
    '-webkit-tap-highlight-color:transparent;transition:background-color .15s ease}' +
    '.gl-mot:hover,.gl-mot[aria-expanded="true"]{background-color:rgba(201,138,18,.16);' +
    'background-color:color-mix(in srgb,var(--gold,#C98A12) 18%,transparent);text-decoration-style:solid}' +
    '.gl-mot:focus{outline:none}.gl-mot:focus-visible{outline:2px solid var(--gold-ink,currentColor);outline-offset:2px}' +
    '.gl-voile{position:fixed;top:0;right:0;bottom:0;left:0;z-index:2147483000;background:rgba(6,10,22,.42);opacity:0;transition:opacity .22s ease}' +
    '.gl-voile.gl-ouvert{opacity:1}' +
    '.gl-bulle{position:fixed;z-index:2147483001;left:-9999px;top:0;box-sizing:border-box;width:min(370px,calc(100vw - 24px));margin:0;padding:0;' +
    'border:1px solid var(--rule,#CBD2E0);border-radius:14px;background:var(--sheet,#fff);color:var(--ink,#18213B);' +
    'box-shadow:var(--shadow,0 10px 30px rgba(0,0,0,.2)),0 1px 2px rgba(0,0,0,.1);font:400 1rem/1.5 var(--font-body,system-ui,sans-serif);' +
    'text-align:left;letter-spacing:0;text-transform:none;opacity:0;transform:translateY(5px);transition:opacity .15s ease-out,transform .15s ease-out}' +
    '.gl-bulle.gl-haut{transform:translateY(-5px)}.gl-bulle.gl-ouvert{opacity:1;transform:none}' +
    '.gl-bulle:focus{outline:none}.gl-bulle.gl-clavier:focus-visible{outline:2px solid var(--gold-ink,currentColor);outline-offset:2px}' +
    '.gl-bulle *,.gl-bulle *::before,.gl-bulle *::after{box-sizing:border-box}' +
    '.gl-defil{max-height:calc(100vh - 24px);overflow:auto;overscroll-behavior:contain;padding:14px 18px 10px;border-radius:inherit}' +
    '.gl-fleche{position:absolute;top:-7px;left:50%;width:12px;height:12px;margin-left:-6px;background:var(--sheet,#fff);' +
    'border:1px solid var(--rule,#CBD2E0);border-width:1px 0 0 1px;border-radius:3px 0 0 0;transform:rotate(45deg);pointer-events:none}' +
    '.gl-haut .gl-fleche{top:auto;bottom:-7px;border-width:0 1px 1px 0;border-radius:0 0 3px 0}' +
    '.gl-poignee{display:none}' +
    '.gl-bulle p{margin:0}' +
    '.gl-bulle .gl-sur{margin:0 40px 6px 0;font:500 .66rem/1.35 var(--font-mono,ui-monospace,monospace);letter-spacing:.11em;text-transform:uppercase;color:var(--muted,#56607D)}' +
    '.gl-bulle .gl-t{margin:0 36px 0 0;font:600 1.45rem/1.12 var(--font-display,Georgia,serif);color:var(--ink,#18213B);text-wrap:balance}' +
    '.gl-bulle .gl-en{margin-top:3px;font-size:.86rem;line-height:1.35;color:var(--muted,#56607D)}' +
    '.gl-bulle .gl-en i{font-style:italic;color:var(--ink,#18213B)}' +
    '.gl-bulle .gl-d{margin-top:10px;font-size:1rem;line-height:1.5}' +
    '.gl-bulle .gl-c{margin:12px 0 0;padding:1px 0 1px 12px;border-left:2px solid var(--gold-ui,var(--gold,#C98A12))}' +
    '.gl-bulle .gl-c blockquote{margin:0;padding:0;border:0;background:none}' +
    '.gl-bulle .gl-c p{font:italic 500 1.08rem/1.38 var(--font-display,Georgia,serif);color:var(--ink,#18213B)}' +
    '.gl-bulle .gl-c figcaption{margin-top:2px}' +
    '.gl-bulle .gl-o{margin-top:10px;display:flex;flex-wrap:wrap;align-items:baseline;column-gap:12px;row-gap:0}' +
    '.gl-bulle .gl-lbl{font:500 .66rem/1.35 var(--font-mono,ui-monospace,monospace);letter-spacing:.11em;text-transform:uppercase;color:var(--muted,#56607D)}' +
    '.gl-bulle .ref{font:500 .8rem/1.3 var(--font-mono,ui-monospace,monospace);color:var(--muted,#56607D);white-space:nowrap;letter-spacing:0;font-style:normal}' +
    '.gl-bulle a.ref-lien{display:inline-block;padding-block:11px;color:var(--gold-ink,#8A5A00);text-decoration:underline dotted;text-underline-offset:3px}' +
    '.gl-bulle a.ref-lien:hover{text-decoration-style:solid}' +
    '.gl-bulle .gl-c figcaption a.ref-lien{padding-block:8px}' +
    '.gl-bulle .gl-l{margin-top:6px;padding-top:6px;border-top:1px solid var(--rule,#CBD2E0);display:flex;flex-wrap:wrap;align-items:center;column-gap:18px}' +
    '.gl-bulle .gl-l a{display:inline-flex;align-items:center;min-height:44px;color:var(--gold-ink,#8A5A00);font:600 .93rem/1.25 var(--font-body,system-ui,sans-serif);' +
    'text-decoration:underline;text-underline-offset:3px}' +
    '.gl-bulle .gl-l a:hover{text-decoration-thickness:2px}' +
    '.gl-bulle .gl-l a.gl-atlas::after{content:"\\00a0\\2192"}' +
    '.gl-bulle a:focus-visible,.gl-x:focus-visible{outline:2px solid var(--gold-ink,currentColor);outline-offset:2px;border-radius:4px}' +
    '.gl-x{appearance:none;-webkit-appearance:none;position:absolute;top:4px;right:4px;width:44px;height:44px;margin:0;padding:0;border:0;' +
    'border-radius:999px;background:none;color:var(--muted,#56607D);cursor:pointer;display:grid;place-items:center}' +
    '.gl-x:hover{color:var(--ink,#18213B);background:var(--tint,rgba(127,127,127,.12))}' +
    '.gl-x svg{display:block}' +
    '.gl-bulle.gl-tiroir{left:0;right:0;top:auto;bottom:0;width:auto;border-width:1px 0 0;border-radius:18px 18px 0 0;opacity:1;' +
    'transform:translateY(105%);transition:transform .24s cubic-bezier(.2,.8,.2,1);padding-bottom:env(safe-area-inset-bottom,0px)}' +
    '.gl-bulle.gl-tiroir.gl-ouvert{transform:none}' +
    '.gl-tiroir .gl-fleche{display:none}' +
    '.gl-tiroir .gl-poignee{display:block;width:42px;height:4px;margin:9px auto 0;border-radius:2px;background:var(--rule,#CBD2E0)}' +
    '.gl-tiroir .gl-defil{max-height:min(74vh,620px);padding:8px max(18px,env(safe-area-inset-left,0px)) 8px max(18px,env(safe-area-inset-right,0px))}' +
    '.gl-tiroir .gl-x{top:10px;right:6px}' +
    '.gl-tiroir .gl-t{font-size:1.6rem}' +
    '@media (prefers-reduced-motion:reduce){.gl-mot,.gl-voile,.gl-bulle,.gl-bulle.gl-tiroir{transition:none}}' +
    '@media (forced-colors:active){.gl-mot{text-decoration-color:CanvasText}.gl-bulle{border:1px solid CanvasText}}' +
    '@media print{.gl-mot{text-decoration:none;background:none}.gl-bulle,.gl-voile{display:none!important}}';

  // ── Démarrage ──────────────────────────────────────────────────────────────────────────────────────
  var observateur = null, minuterieReprise = null;
  function dansNosZones(n) {
    for (var e = n && (n.nodeType === 1 ? n : n.parentNode); e && e !== document.body; e = e.parentNode) {
      if (e.nodeType === 1 && (e === bulle || e === voile || e.namespaceURI === SVGNS || exclu(e))) return true;
    }
    return false;
  }
  function surMutation(liste) {
    for (var i = 0; i < liste.length; i++) {
      var mu = liste[i];
      if (dansNosZones(mu.target)) continue;
      for (var j = 0; j < mu.removedNodes.length; j++) {
        var r = mu.removedNodes[j];
        if (r.nodeType === 1 && (r.classList.contains('gl-mot') || r.querySelector('.gl-mot'))) return planifier();
      }
      for (var k = 0; k < mu.addedNodes.length; k++) {
        var a = mu.addedNodes[k];
        if (a.nodeType === 1 || (a.nodeType === 3 && /[A-Za-zÀ-ÿ]{3}/.test(a.nodeValue))) return planifier();
      }
    }
  }
  function planifier() { clearTimeout(minuterieReprise); minuterieReprise = setTimeout(reprendre, 450); }
  function reprendre() {
    try { balayer(); } catch (e) { enCours = false; /* la page reste lisible sans les nouveaux mots */ }
  }
  function demarrer() {
    try {
      if (document.querySelector('[data-glossaire-page]')) return;      // la page du glossaire n’en a pas besoin
      var t0 = performance.now();
      balayer(function (n, travail, tranches) {
        // mesure : durée de travail cumulée du premier repérage (en tranches de 8 ms au plus)
        try { performance.measure('glossaire', { start: t0, duration: travail, detail: { termes: n, tranches: tranches } }); } catch (e) { /* facultatif */ }
      });
      document.addEventListener('keydown', function (e) {
        if (ouvert && (e.key === 'Escape' || e.key === 'Esc')) { e.preventDefault(); e.stopPropagation(); fermer(true); }
      }, true);
      document.addEventListener('click', function (e) {
        if (ouvert && bulle && !bulle.contains(e.target) && e.target !== courant) fermer(false);
      });
      var attente = false;
      var suivre = function (e) {
        if (e && e.target && e.target.nodeType === 1 && bulle && bulle.contains(e.target)) return;   // défilement dans la bulle
        if (!attente && ouvert && !tiroir) { attente = true; requestAnimationFrame(function () { attente = false; placer(); }); }
      };
      document.addEventListener('scroll', suivre, { capture: true, passive: true });
      window.addEventListener('resize', function () {
        if (ouvert && tiroir !== !!mqTel.matches) fermer(false); else suivre();
      });
      if (window.MutationObserver) {
        observateur = new MutationObserver(surMutation);
        observateur.observe(document.body, { childList: true, subtree: true });
      }
    } catch (e) { /* le glossaire reste inactif ; la page fonctionne sans lui */ }
  }
  function bientot(f) { if (window.requestIdleCallback) window.requestIdleCallback(f, { timeout: 700 }); else setTimeout(f, 40); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', function () { bientot(demarrer); });
  else bientot(demarrer);
})();
