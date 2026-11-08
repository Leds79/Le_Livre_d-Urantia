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
  var DONNEES = /*__GLOSSAIRE__*/null;
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
