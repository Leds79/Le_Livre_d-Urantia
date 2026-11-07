(function () {
  'use strict';
  // Références cliquables : chaque « fascicule:section.paragraphe » d’un élément .ref ouvre le passage sur urantia.org
  var BASE = 'https://www.urantia.org/fr/le-livre-d-urantia/';
  var S = ["introduction","fascicule-1-le-pere-universel","fascicule-2-la-nature-de-dieu","fascicule-3-les-attributs-de-dieu","fascicule-4-relations-de-dieu-avec-l-univers","fascicule-5-relations-de-dieu-avec-l-individu","fascicule-6-le-fils-eternel","fascicule-7-position-du-fils-eternel-par-rapport-l-univers","fascicule-8-l-esprit-infini","fascicule-9-position-de-l-esprit-infini-par-rapport-l-univers","fascicule-10-la-trinite-du-paradis","fascicule-11-l-ile-eternelle-du-paradis","fascicule-12-l-univers-des-univers","fascicule-13-les-spheres-sacrees-du-paradis","fascicule-14-l-univers-central-et-divin","fascicule-15-les-sept-superunivers","fascicule-16-les-sept-maitres-esprits","fascicule-17-les-sept-groupes-d-esprits-supremes","fascicule-18-les-personnalites-supremes-de-la-trinite","fascicule-19-les-etres-coordonnes-d-origine-trinitaire","fascicule-20-les-fils-paradisiaques-de-dieu","fascicule-21-les-fils-paradisiaques-createurs","fascicule-22-les-fils-de-dieu-trinitises","fascicule-23-les-messagers-solitaires","fascicule-24-personnalites-superieures-de-l-esprit-infini","fascicule-25-les-armees-des-messagers-de-l-espace","fascicule-26-les-esprits-tutelaires-de-l-univers-central","fascicule-27-le-ministere-des-supernaphins-primaires","fascicule-28-esprits-tutelaires-des-superunivers","fascicule-29-les-directeurs-de-pouvoir-de-l-univers","fascicule-30-personnalites-du-grand-univers","fascicule-31-le-corps-de-la-finalite","fascicule-32-l-evolution-des-univers-local","fascicule-33-administration-de-l-univers-local","fascicule-34-l-esprit-mere-de-l-univers-local","fascicule-35-les-fils-de-dieu-de-l-univers-local","fascicule-36-les-porteurs-de-vie","fascicule-37-personnalites-de-l-univers-local","fascicule-38-esprits-tutelaires-de-l-univers-local","fascicule-39-les-armees-seraphiques","fascicule-40-les-fils-ascendants-de-dieu","fascicule-41-aspects-physiques-de-l-univers-local","fascicule-42-energie-mental-et-matiere","fascicule-43-les-constellations","fascicule-44-les-artisans-celestes","fascicule-45-l-administration-du-systeme-local","fascicule-46-le-siege-du-systeme-local","fascicule-47-les-sept-mondes-des-maisons","fascicule-48-la-vie-morontielle","fascicule-49-les-mondes-habites","fascicule-50-les-princes-planetaires","fascicule-51-les-adams-planetaires","fascicule-52-epoques-planetaires-des-mortels","fascicule-53-la-rebellion-de-lucifer","fascicule-54-problemes-de-la-rebellion-de-lucifer","fascicule-55-les-spheres-de-lumiere-et-de-vie","fascicule-56-unite-universelle","fascicule-57-l-origine-d-urantia","fascicule-58-l-etablissement-de-la-vie-sur-urantia","fascicule-59-l-ere-de-la-vie-marine-sur-urantia","fascicule-60-urantia-pendant-l-ere-de-la-vie-terrestre-primitive","fascicule-61-l-ere-des-mammiferes-sur-urantia","fascicule-62-les-races-l-aurore-de-l-homme-primitif","fascicule-63-la-premiere-famille-humaine","fascicule-64-les-races-evolutionnaires-de-couleur","fascicule-65-le-supercontrole-de-l-evolution","fascicule-66-le-prince-planetaire-d-urantia","fascicule-67-la-rebellion-planetaire","fascicule-68-l-aurore-de-la-civilisation","fascicule-69-les-institutions-humaines-primitives","fascicule-70-l-evolution-du-gouvernement-humain","fascicule-71-developpement-de-l-etat","fascicule-72-le-gouvernement-sur-une-planete-voisine","fascicule-73-le-jardin-d-eden","fascicule-74-adam-et-eve","fascicule-75-la-faute-d-adam-et-d-eve","fascicule-76-le-second-jardin","fascicule-77-les-creatures-medianes","fascicule-78-la-race-violette-apres-les-jours-d-adam","fascicule-79-l-expansion-andite-en-orient","fascicule-80-l-expansion-andite-en-occident","fascicule-81-developpement-de-la-civilisation-moderne","fascicule-82-l-evolution-du-mariage","fascicule-83-l-institution-du-mariage","fascicule-84-le-mariage-et-la-vie-familiale","fascicule-85-les-origines-de-l-adoration","fascicule-86-l-evolution-primitive-de-la-religion","fascicule-87-les-cultes-des-fantomes","fascicule-88-fetiches-charmes-et-magie","fascicule-89-peche-sacrifice-et-expiation","fascicule-90-shamanism-le-chamanisme-medecine-men-et-pretres","fascicule-91-l-evolution-de-la-priere","fascicule-92-l-evolution-ulterieure-de-la-religion","fascicule-93-machiventa-melchizedek","fascicule-94-les-enseignements-de-melchizedek-en-orient","fascicule-95-les-enseignements-de-melchizedek-dans-le-levant","fascicule-96-yahweh-le-dieu-des-hebreux","fascicule-97-l-evolution-du-concept-de-dieu-chez-les-hebreux","fascicule-98-les-enseignements-de-melchizedek-en-occident","fascicule-99-les-problemes-sociaux-de-la-religion","fascicule-100-la-religion-dans-l-experience-humaine","fascicule-101-la-nature-reelle-de-la-religion","fascicule-102-les-fondements-de-la-foi-religieuse","fascicule-103-la-realite-de-l-experience-religieuse","fascicule-104-croissance-du-concept-de-trinite","fascicule-105-deite-et-realite","fascicule-106-niveaux-de-realite-de-l-univers","fascicule-107-origine-et-nature-des-ajusteurs-de-pensee","fascicule-108-mission-et-ministere-des-ajusteurs-de-pensee","fascicule-109-position-des-ajusteurs-par-rapport-aux-creatures-de-l-univers","fascicule-110-position-des-ajusteurs-par-rapport-aux-mortels-individuels","fascicule-111-l-ajusteur-et-l-ame","fascicule-112-la-survie-de-la-personnalite","fascicule-113-les-gardiens-seraphiques-de-la-destinee","fascicule-114-le-gouvernement-planetaire-des-seraphins","fascicule-115-l-etre-supreme","fascicule-116-le-tout-puissant-supreme","fascicule-117-dieu-le-supreme","fascicule-118-le-supreme-et-l-ultime-temps-et-espace","fascicule-119-les-effusions-du-christ-micael","fascicule-120-l-effusion-de-micael-sur-urantia","fascicule-121-l-epoque-de-l-effusion-de-micael","fascicule-122-naissance-et-petite-enfance-de-jesus","fascicule-123-la-prime-enfance-de-jesus","fascicule-124-la-derniere-partie-de-l-enfance-de-jesus","fascicule-125-jesus-jerusalem","fascicule-126-les-deux-annees-cruciales","fascicule-127-les-annees-d-adolescence","fascicule-128-la-vie-de-jeune-homme-de-jesus","fascicule-129-suite-de-la-vie-d-adulte-de-jesus","fascicule-130-sur-le-chemin-de-rome","fascicule-131-les-religions-du-monde","fascicule-132-le-sejour-rome","fascicule-133-le-retour-de-rome","fascicule-134-les-annees-de-transition","fascicule-135-jean-le-baptiste","fascicule-136-le-bapteme-et-les-quarante-jours","fascicule-137-sejour-d-attente-en-galilee","fascicule-138-la-formation-des-messagers-du-royaume","fascicule-139-les-douze-apotres","fascicule-140-l-ordination-des-douze","fascicule-141-le-commencement-de-l-oeuvre-publique","fascicule-142-la-paque-jerusalem","fascicule-143-traversee-de-la-samarie","fascicule-144-gilboa-et-dans-la-decapole","fascicule-145-quatre-journees-memorables-capharnaum","fascicule-146-la-premiere-tournee-de-predication-en-galilee","fascicule-147-l-intermede-de-la-visite-jerusalem","fascicule-148-la-formation-d-evangelistes-bethsaide","fascicule-149-la-seconde-tournee-de-predication","fascicule-150-la-troisieme-tournee-de-predication","fascicule-151-sejour-et-enseignement-au-bord-de-la-mer","fascicule-152-les-prodromes-de-la-crise-de-capharnaum","fascicule-153-la-crise-capharnaum","fascicule-154-derniers-jours-capharnaum","fascicule-155-en-fuite-travers-la-galilee-du-nord","fascicule-156-le-sejour-tyr-et-sidon","fascicule-157-cesaree-de-philippe","fascicule-158-le-mont-de-la-transfiguration","fascicule-159-la-tournee-en-decapole","fascicule-160-rodan-d-alexandrie","fascicule-161-suite-des-discussions-avec-rodan","fascicule-162-la-fete-des-tabernacles","fascicule-163-l-ordination-des-soixante-dix-magadan","fascicule-164-la-fete-de-la-dedicace","fascicule-165-la-mission-en-peree-commence","fascicule-166-derniere-tournee-en-peree-du-nord","fascicule-167-la-visite-philadelphie","fascicule-168-la-resurrection-de-lazare","fascicule-169-derniers-enseignements-pella","fascicule-170-le-royaume-des-cieux","fascicule-171-sur-le-chemin-de-jerusalem","fascicule-172-l-entree-jerusalem","fascicule-173-le-lundi-jerusalem","fascicule-174-le-mardi-matin-au-temple","fascicule-175-le-dernier-discours-au-temple","fascicule-176-le-mardi-soir-sur-le-mont-olivet","fascicule-177-mercredi-jour-de-repos","fascicule-178-le-dernier-jour-au-camp","fascicule-179-le-dernier-souper","fascicule-180-le-discours-d-adieu","fascicule-181-ultimes-exhortations-et-avertissements","fascicule-182-gethsemani","fascicule-183-jesus-trahi-et-arrete","fascicule-184-devant-le-tribunal-du-sanhedrin","fascicule-185-le-jugement-devant-pilate","fascicule-186-peu-avant-la-crucifixion","fascicule-187-la-crucifixion","fascicule-188-l-heure-du-tombeau","fascicule-189-la-resurrection","fascicule-190-les-apparitions-morontielles-de-jesus","fascicule-191-apparitions-aux-apotres-et-d-autres-disciples","fascicule-192-apparitions-en-galilee","fascicule-193-apparitions-finales-et-ascension","fascicule-194-l-effusion-de-l-esprit-de-verite","fascicule-195-apres-la-pentecote","fascicule-196-la-foi-de-jesus"];   // page de chaque fascicule, de l’Introduction (0) au fascicule 196
  var RX = /(\d{1,3}):(\d{1,2})(?:\.(\d{1,3}))?(?:\s*[–-]\s*\d{1,3})?/g;
  function link(el) {
    var t = el.textContent;
    if (el.getAttribute('data-lk') === t) return;                       // déjà fait, texte inchangé
    if (el.closest('a, button, [role="button"]') || el.querySelector('a')) return;
    var frag = document.createDocumentFragment(), last = 0, n = 0, m;
    RX.lastIndex = 0;
    while ((m = RX.exec(t))) {
      var p = +m[1];
      if (!S[p]) continue;
      if (m.index > last) frag.appendChild(document.createTextNode(t.slice(last, m.index)));
      var a = document.createElement('a');
      a.className = 'ref-lien';
      a.href = BASE + S[p] + '#U' + p + '_' + (+m[2]) + '_' + (m[3] ? +m[3] : 0);
      a.target = '_blank';
      a.rel = 'noopener';
      a.title = 'Lire ' + m[0] + ' sur urantia.org';
      a.textContent = m[0];
      frag.appendChild(a);
      last = m.index + m[0].length;
      n++;
    }
    if (!n) return;
    if (last < t.length) frag.appendChild(document.createTextNode(t.slice(last)));
    el.textContent = '';
    el.appendChild(frag);
    el.setAttribute('data-lk', el.textContent);
  }
  function scan(node) {
    if (!node || node.nodeType !== 1) return;
    if (node.classList.contains('ref')) link(node);
    var l = node.querySelectorAll('.ref');
    for (var i = 0; i < l.length; i++) link(l[i]);
  }
  function refOf(node) { var e = node && (node.nodeType === 1 ? node : node.parentNode); return e && e.closest ? e.closest('.ref') : null; }
  function start() {
    try {
      var st = document.createElement('style');
      st.textContent = 'a.ref-lien{color:inherit;text-decoration:underline dotted;text-decoration-thickness:1px;text-underline-offset:2px;pointer-events:auto}' +
        'a.ref-lien:hover,a.ref-lien:focus-visible{color:var(--gold-ink,inherit);text-decoration-style:solid}';
      document.head.appendChild(st);
      scan(document.body);
      if (!window.MutationObserver) return;
      new MutationObserver(function (list) {
        for (var i = 0; i < list.length; i++) {
          var mu = list[i];
          if (mu.type === 'characterData') { var r = refOf(mu.target); if (r) link(r); continue; }
          for (var j = 0; j < mu.addedNodes.length; j++) {
            var nd = mu.addedNodes[j];
            if (nd.nodeType === 1) scan(nd); else { var r2 = refOf(nd); if (r2) link(r2); }
          }
        }
      }).observe(document.body, { childList: true, subtree: true, characterData: true });
    } catch (e) { /* les références restent en texte simple */ }
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
})();
