/* Barre commune et recherche de « Le Livre d’Urantia en images ».
   construire_site.py écrit dans chaque page 2D la barre nav.atlas-nav : Accueil, quatre menus (Parcours, Thèmes,
   Le livre, Outils), puis Rechercher, Écouter et la musique. Sans JavaScript, chaque menu est un details/summary qui
   s’ouvre seul. Ce script (assets/navigation.js) :
   - remplace chaque details par un bouton « disclosure » (aria-expanded, aria-controls) suivi de son panneau. Au
     bureau, un menu s’ouvre au clic (pas au survol) ; Échap le ferme et rend le focus au bouton ; un clic ailleurs
     ou le focus qui s’en va le ferment aussi ; ↑ ↓ Début Fin parcourent ses liens ;
   - sous 1 000 px, ouvre le tiroir (bouton Menu) : groupes en accordéons, celui de la page ouverte d’emblée, reste de
     la page inerte, focus gardé dans le tiroir, Échap ou le voile pour fermer, focus rendu au bouton Menu ;
   - ouvre la recherche (bouton Rechercher, « / » ou Ctrl+K) dans une boite de dialogue. L’index (assets/recherche.js,
     écrit à la construction) n’est chargé qu’à la première ouverture. La recherche ignore la casse et les accents et
     porte sur le début des mots ; les résultats sont groupés par page, avec un extrait où le mot est surligné ;
     ↑ ↓ puis Entrée ouvrent le passage (lien vers son ancre). Une référence tapée (57:6.5) propose le passage sur
     urantia.org et les pages de l’atlas qui la citent.
   Dans la vue 3D, qui garde sa navigation propre, une entrée « Rechercher dans l’atlas » est ajoutée en tête de son
   menu (details#menu .menu-panel), et « / » ou Ctrl+K ouvrent la même recherche. */
(function () {
  'use strict';
  if (window.atlasNav || !document.querySelector || !window.addEventListener || !Array.prototype.forEach) return;

  var doc = document, html = doc.documentElement, NB = '\u00a0';
  var moi = doc.currentScript && doc.currentScript.src;
  var ASSETS = moi ? moi.replace(/[^\/]*$/, '') : 'assets/';
  var SVGNS = 'http://www.w3.org/2000/svg';
  function mq(q) { return window.matchMedia ? window.matchMedia(q) : { matches: false }; }
  function suivreMq(m, f) { if (m.addEventListener) m.addEventListener('change', f); else if (m.addListener) m.addListener(f); }
  var mqTel = mq('(max-width: 999.98px)'), mqCalme = mq('(prefers-reduced-motion: reduce)');
  function toArray(l) { return Array.prototype.slice.call(l || []); }
  function el(tag, cls, txt) {
    var e = doc.createElement(tag);
    if (cls) e.className = cls;
    if (txt !== undefined && txt !== null) e.textContent = txt;
    return e;
  }
  function icone(d, cls) {           // petite icône SVG au trait, décorative
    var s = doc.createElementNS(SVGNS, 'svg');
    s.setAttribute('viewBox', '0 0 20 20');
    s.setAttribute('aria-hidden', 'true');
    s.setAttribute('focusable', 'false');
    s.setAttribute('class', cls || 'an-ic');
    d.split('|').forEach(function (x) {
      var p = doc.createElementNS(SVGNS, x.charAt(0) === 'c' ? 'circle' : 'path');
      if (x.charAt(0) === 'c') { var v = x.slice(1).split(','); p.setAttribute('cx', v[0]); p.setAttribute('cy', v[1]); p.setAttribute('r', v[2]); }
      else p.setAttribute('d', x);
      p.setAttribute('fill', 'none');
      p.setAttribute('stroke', 'currentColor');
      p.setAttribute('stroke-width', '1.8');
      p.setAttribute('stroke-linecap', 'round');
      p.setAttribute('stroke-linejoin', 'round');
      s.appendChild(p);
    });
    return s;
  }
  var I_LOUPE = 'c8.6,8.6,5.4|M12.7 12.7l4 4', I_FERMER = 'M5.5 5.5l9 9M14.5 5.5l-9 9', I_EXT = 'M8 4.5H4.5v11h11V12|M11 3.5h5.5V9|M16.5 3.5L9 11';
  function saisie(t) { return !!(t && (t.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName))); }
  var bloqueurs = 0;
  function bloquer(oui) {                    // page figée sous le tiroir ou la recherche, sans saut dû à la barre de défilement
    bloqueurs = Math.max(0, bloqueurs + (oui ? 1 : -1));
    if (bloqueurs && !html.classList.contains('an-bloque')) {
      var w = window.innerWidth - html.clientWidth;
      html.classList.add('an-bloque');
      if (w > 0) doc.body.style.paddingRight = w + 'px';
    } else if (!bloqueurs) {
      html.classList.remove('an-bloque');
      doc.body.style.paddingRight = '';
    }
  }
  function focusables(racine) {
    return toArray(racine.querySelectorAll('a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea, [tabindex]:not([tabindex="-1"])'))
      .filter(function (x) { return !x.hidden && x.getClientRects().length > 0 && !x.closest('[hidden],[inert]'); });
  }

  /* ════════════ Barre : menus déroulants et tiroir ════════════ */
  var nav = doc.querySelector('nav.atlas-nav');
  var groupes = [], deroule = null;          // deroule : menu ouvert au bureau (un seul à la fois)
  var tiroir = null, bMenu = null, voile = null, tiroirOuvert = false, inertes = [];

  function liensDe(g) { return toArray(g.p.querySelectorAll('a[href]')).filter(function (a) { return a.getClientRects().length > 0; }); }
  function fermerGroupe(g, rendreFocus) {
    if (!g || g.b.getAttribute('aria-expanded') !== 'true') return;
    g.b.setAttribute('aria-expanded', 'false');
    g.p.hidden = true;
    g.p.style.left = '';
    if (deroule === g) deroule = null;
    if (rendreFocus) g.b.focus();
  }
  function ouvrirGroupe(g) {
    if (!mqTel.matches && deroule && deroule !== g) fermerGroupe(deroule);
    g.b.setAttribute('aria-expanded', 'true');
    g.p.hidden = false;
    if (!mqTel.matches) { deroule = g; recaler(g); }
  }
  function recaler(g) {                      // le panneau reste dans la fenêtre
    g.p.style.left = '';
    var r = g.p.getBoundingClientRect(), max = html.clientWidth - 12;
    if (r.right > max) g.p.style.left = Math.round(Math.max(12 - r.left, max - r.right)) + 'px';
  }
  function preparerGroupe(li) {
    var d = li.querySelector('details'), s = d && d.querySelector('summary'), p = d && d.querySelector('.an-panneau');
    if (!d || !s || !p) return;
    var b = doc.createElement('button');
    b.type = 'button';
    b.className = s.className;
    while (s.firstChild) b.appendChild(s.firstChild);
    b.setAttribute('aria-expanded', 'false');
    b.setAttribute('aria-controls', p.id);
    p.hidden = true;
    li.insertBefore(b, d);
    li.insertBefore(p, d);
    li.removeChild(d);
    var g = { li: li, b: b, p: p };
    groupes.push(g);
    b.addEventListener('click', function () {
      if (b.getAttribute('aria-expanded') === 'true') fermerGroupe(g); else ouvrirGroupe(g);
    });
    b.addEventListener('keydown', function (e) {
      if (mqTel.matches) return;
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        e.preventDefault();
        ouvrirGroupe(g);
        var l = liensDe(g);
        if (l.length) l[e.key === 'ArrowDown' ? 0 : l.length - 1].focus();
      }
    });
    p.addEventListener('keydown', function (e) {
      if (mqTel.matches) return;
      var l = liensDe(g), i = l.indexOf(doc.activeElement), k = e.key;
      if (k === 'ArrowDown' || k === 'ArrowUp' || k === 'Home' || k === 'End') {
        e.preventDefault();
        if (!l.length) return;
        if (k === 'Home') i = 0;
        else if (k === 'End') i = l.length - 1;
        else i = (i + (k === 'ArrowDown' ? 1 : -1) + l.length) % l.length;
        l[i].focus();
      }
    });
    li.addEventListener('focusout', function (e) {
      if (!mqTel.matches && e.relatedTarget && !li.contains(e.relatedTarget)) fermerGroupe(g);
    });
  }

  function creerVoile() {
    var v = el('div', 'an-voile');
    v.hidden = true;
    v.addEventListener('click', function () { fermerTiroir(); });
    nav.appendChild(v);
    return v;
  }
  function ouvrirTiroir() {
    if (tiroirOuvert || !tiroir) return;
    tiroirOuvert = true;
    if (!tiroir.getAttribute('data-vu')) {     // première ouverture : le groupe de la page affichée est déroulé
      tiroir.setAttribute('data-vu', '1');
      groupes.forEach(function (g) { if (g.li.classList.contains('an-ici')) ouvrirGroupe(g); });
    }
    voile = voile || creerVoile();
    tiroir.setAttribute('role', 'dialog');
    tiroir.setAttribute('aria-modal', 'true');
    tiroir.setAttribute('aria-label', 'Menu de l’atlas');
    bMenu.setAttribute('aria-expanded', 'true');
    bloquer(true);
    inertes = [];
    function rendreInerte(c) {
      if (c === nav || c === tiroir || c === voile || c.hasAttribute('inert') || /^(SCRIPT|STYLE|LINK)$/.test(c.tagName)) return;
      c.setAttribute('inert', '');
      inertes.push(c);
    }
    toArray(doc.body.children).forEach(rendreInerte);
    toArray(tiroir.parentNode.children).forEach(rendreInerte);
    voile.hidden = false;
    void tiroir.offsetWidth;                 // départ de la transition
    tiroir.classList.add('ouvert');
    voile.classList.add('ouvert');
    var f = tiroir.querySelector('.an-fermer');
    if (f) f.focus();
  }
  function fermerTiroir(rendreFocus) {
    if (!tiroirOuvert) return;
    tiroirOuvert = false;
    tiroir.classList.remove('ouvert');
    if (voile) voile.classList.remove('ouvert');
    tiroir.removeAttribute('role');
    tiroir.removeAttribute('aria-modal');
    tiroir.removeAttribute('aria-label');
    bMenu.setAttribute('aria-expanded', 'false');
    bloquer(false);
    inertes.forEach(function (c) { c.removeAttribute('inert'); });
    inertes = [];
    setTimeout(function () { if (!tiroirOuvert && voile) voile.hidden = true; }, mqCalme.matches ? 0 : 280);
    if (rendreFocus !== false) bMenu.focus();
  }

  function preparerBarre() {
    toArray(nav.querySelectorAll('.an-g')).forEach(preparerGroupe);
    tiroir = nav.querySelector('.an-tiroir');
    bMenu = nav.querySelector('.an-menu');
    if (tiroir && bMenu) {
      bMenu.addEventListener('click', function () { if (tiroirOuvert) fermerTiroir(); else ouvrirTiroir(); });
      var bf = tiroir.querySelector('.an-fermer');
      if (bf) bf.addEventListener('click', function () { fermerTiroir(); });
      tiroir.addEventListener('keydown', function (e) {
        if (!tiroirOuvert) return;
        if (e.key === 'Escape') { e.preventDefault(); e.stopPropagation(); fermerTiroir(); return; }
        if (e.key !== 'Tab') return;
        var f = focusables(tiroir);
        if (!f.length) return;
        var i = f.indexOf(doc.activeElement);
        if (e.shiftKey && i <= 0) { e.preventDefault(); f[f.length - 1].focus(); }
        else if (!e.shiftKey && i === f.length - 1) { e.preventDefault(); f[0].focus(); }
      });
      tiroir.addEventListener('click', function (e) {     // un lien suivi ou « Écouter » : le tiroir se ferme
        var a = e.target.closest && e.target.closest('a[href], [data-ecouter]');
        if (a && tiroirOuvert) fermerTiroir(false);
      });
    }
    // bureau : clic ailleurs, Échap
    doc.addEventListener('pointerdown', function (e) {
      if (deroule && !deroule.li.contains(e.target)) fermerGroupe(deroule);
    }, true);
    doc.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && deroule && !mqTel.matches) {
        var g = deroule;
        fermerGroupe(g, g.li.contains(doc.activeElement));
      }
    });
    window.addEventListener('resize', function () { if (deroule) recaler(deroule); });
    suivreMq(mqTel, function () {             // passage bureau ↔ téléphone : tout se referme
      fermerTiroir(false);
      groupes.forEach(function (g) { fermerGroupe(g); });
    });
    // « Lire hors ligne » : seulement là où l’atlas peut s’enregistrer (http(s), service worker)
    var peut = 'serviceWorker' in navigator && /^https?:$/.test(location.protocol) && window.isSecureContext !== false;
    if (!peut) toArray(nav.querySelectorAll('a[href$="#hors-ligne"]')).forEach(function (a) { var li = a.closest('li'); if (li) li.hidden = true; });
  }
  // arrivée sur l’accueil par « Lire hors ligne » : l’encadré, caché sans service worker, est montré par hors-ligne.js
  function versHorsLigne() {
    if (location.hash !== '#hors-ligne') return;
    var b = doc.getElementById('hors-ligne');
    if (b && !b.hidden) requestAnimationFrame(function () { b.scrollIntoView({ block: 'start' }); });
  }

  /* ════════════ Recherche ════════════ */
  var RX_REF = /^\s*(\d{1,3})\s*:\s*(\d{1,2})(?:\s*[.,]\s*(\d{1,3}))?\s*$/;
  var RX_DIACR = /[\u0300-\u036f]/g, RX_NONMOT = /[^a-z0-9]+/g, RX_MOT = /^[a-z0-9]+$/;
  var VIDES = { le: 1, la: 1, les: 1, l: 1, de: 1, d: 1, du: 1, des: 1, un: 1, une: 1, et: 1, en: 1, a: 1, au: 1, aux: 1, ou: 1,
    sur: 1, par: 1, pour: 1, que: 1, qui: 1, ce: 1, se: 1, sa: 1, son: 1, ses: 1, dans: 1, est: 1, il: 1, elle: 1, s: 1, n: 1, qu: 1 };
  var MAX_PAGE = 3, MAX_TOTAL = 24, EXTRAIT = 170;
  var D = null, chargement = null, erreurIndex = false;
  var R = { dlg: null, champ: null, liste: null, etat: null, opts: [], actif: -1, avant: null, minuterie: 0, derniere: '' };

  function norm(s) {
    return (' ' + String(s).normalize('NFD').replace(RX_DIACR, '').toLowerCase().replace(/œ/g, 'oe').replace(/æ/g, 'ae')
      .replace(RX_NONMOT, ' ') + ' ').replace(/ {2,}/g, ' ');
  }
  function preparerIndex(x) {
    var t0 = performance.now(), n = x.S.length, textes = new Array(n), i;
    for (i = 0; i < x.T.length; i++) {
      var s = x.T[i][0];
      (textes[s] || (textes[s] = [])).push(i);
    }
    var hs = new Array(n), hx = new Array(n), tn = new Array(x.T.length);
    for (i = 0; i < n; i++) {
      hs[i] = x.S[i][3] === 'i' ? ' ' : norm(x.S[i][2]);   // titre hérité du contexte : affiché, pas cherché
      var l = textes[i] || [], parts = new Array(l.length);
      for (var k = 0; k < l.length; k++) parts[k] = tn[l[k]] = norm(x.T[l[k]][1]);
      hx[i] = parts.join('|');
      textes[i] = l;
    }
    D = { P: x.P, S: x.S, T: x.T, R: x.R || {}, U: x.U || [], hs: hs, hx: hx, tn: tn, textes: textes, msPrep: performance.now() - t0 };
  }
  function chargerIndex() {                   // promesse : vrai si l’index est prêt ; un échec permet un nouvel essai plus tard
    if (D) return Promise.resolve(true);
    if (chargement) return chargement;
    chargement = new Promise(function (ok, non) {
      if (window.ATLAS_RECHERCHE) { ok(); return; }
      var s = doc.createElement('script');
      s.src = ASSETS + 'recherche.js';
      s.async = true;
      s.onload = function () { window.ATLAS_RECHERCHE ? ok() : non(new Error('index vide')); };
      s.onerror = function () { if (s.parentNode) s.parentNode.removeChild(s); non(new Error('index introuvable')); };
      doc.head.appendChild(s);
    }).then(function () {
      preparerIndex(window.ATLAS_RECHERCHE);
      try {                                   // mise en route : la première frappe ne paie pas la compilation
        var r = chercher('ajusteur pensee');
        if (r && r.pages && r.pages[0]) plages(meilleurTexte(r.pages[0].items[0], r.toks), r.toks);
      } catch (e) { /* sans importance */ }
      erreurIndex = false;
      return true;
    }, function () {
      erreurIndex = true;
      chargement = null;
      return false;
    });
    return chargement;
  }

  // ── Recherche proprement dite ──
  function mots(q) {
    var t = norm(q).trim().split(' ').filter(Boolean);
    var u = t.filter(function (m) { return !VIDES[m] && (m.length > 1 || /\d/.test(m)); });
    return { tous: t, utiles: u.length ? u : t };
  }
  function chercher(q) {
    var t0 = performance.now(), m = RX_REF.exec(q);
    if (m) return chercherRef(+m[1], +m[2], m[3] ? +m[3] : 0, t0);
    var w = mots(q), toks = w.utiles;
    if (!toks.length || !D) return null;
    if (toks.every(function (t) { return t.length < 2 && !/\d/.test(t); })) return { type: 'court', ms: performance.now() - t0 };
    var pre = toks.map(function (t) { return ' ' + t; });
    var phrase = w.tous.length > 1 ? ' ' + w.tous.join(' ') + ' ' : null, exact = ' ' + toks.join(' ') + ' ';
    var hs = D.hs, hx = D.hx, S = D.S, res = [];
    for (var s = 0, n = S.length; s < n; s++) {
      var a = hs[s], b = hx[s], sc = 0, ok = true;
      for (var k = 0; k < pre.length; k++) {
        var t = pre[k], ia = a.indexOf(t), ib = b.indexOf(t);
        if (ia < 0 && ib < 0) { ok = false; break; }
        if (ia >= 0) sc += a.charCodeAt(ia + t.length) === 32 ? 30 : 20;
        if (ib >= 0) {
          sc += b.charCodeAt(ib + t.length) === 32 ? 6 : 4;
          for (var c = 1, j = ib; c < 6 && (j = b.indexOf(t, j + 1)) >= 0;) c++;
          sc += c;
        }
      }
      if (!ok) continue;
      if (phrase && (a.indexOf(phrase) >= 0 || b.indexOf(phrase) >= 0)) sc += 25;
      if (a === exact) sc += S[s][3] === 'g' ? 50 : 40;        // titre identique à la recherche ; à égalité, le terme du glossaire d’abord
      if (!S[s][1]) sc += 8;                                   // la page elle-même
      res.push(sc * 65536 + 65535 - s);                        // score, puis ordre du document (s < 65 536)
    }
    res.sort(function (x, y) { return y - x; });
    var pages = [], parPage = {}, total = res.length;
    for (var r = 0; r < res.length; r++) {
      var si = 65535 - res[r] % 65536;
      var p = S[si][0];
      var g = parPage[p];
      if (!g) { g = parPage[p] = { p: p, items: [], reste: 0 }; pages.push(g); }
      g.items.length < MAX_PAGE ? g.items.push(si) : g.reste++;
    }
    var shown = 0;
    pages.forEach(function (g) {
      var place = Math.max(0, MAX_TOTAL - shown);
      if (g.items.length > place) { g.reste += g.items.length - place; g.items = g.items.slice(0, place); }
      shown += g.items.length;
    });
    return { type: 'mots', toks: toks, pages: pages.filter(function (g) { return g.items.length; }), total: total,
      nbPages: pages.length, ms: performance.now() - t0 };
  }
  function lienLivre(f, s, p) {
    var slug = D && D.U[f];
    return slug ? 'https://www.urantia.org/fr/le-livre-d-urantia/' + slug + '#U' + f + '_' + s + '_' + (p || 0) : null;
  }
  function chercherRef(f, s, p, t0) {
    var ref = f + ':' + s + (p ? '.' + p : ''), liste = (D && D.R[f + ':' + s]) || [], exacts = [], sections = [], vus = {};
    liste.forEach(function (x) {              // x = [section, de, à] ; de = 0 : toute la section
      var cle = x[0];
      if (!p) { if (!vus[cle]) { vus[cle] = 1; exacts.push(x); } return; }
      if (x[1] && x[1] <= p && p <= x[2]) { if (!vus[cle]) { vus[cle] = 1; exacts.push(x); } }
      else if (!x[1]) sections.push(x);
    });
    sections = sections.filter(function (x) { return !vus[x[0]] && (vus[x[0]] = 1); });
    var pages = [], parPage = {};
    exacts.concat(sections).forEach(function (x) {
      var pg = D.S[x[0]][0], g = parPage[pg];
      if (!g) { g = parPage[pg] = { p: pg, items: [], reste: 0, cite: [] }; pages.push(g); }
      if (g.items.length < MAX_PAGE) { g.items.push(x[0]); g.cite.push(x); } else g.reste++;
    });
    return { type: 'ref', ref: ref, f: f, s: s, par: p, lien: lienLivre(f, s, p), pages: pages, total: exacts.length + sections.length,
      ms: performance.now() - (t0 || performance.now()) };
  }

  // ── Extraits et surlignage ──
  var CAR = Object.create(null);               // forme cherchable de chaque caractère (mémorisée)
  function carNorm(c) {
    var k = CAR[c];
    if (k === undefined) {
      k = c.normalize('NFD').replace(RX_DIACR, '').toLowerCase();
      if (k === 'œ') k = 'oe'; else if (k === 'æ') k = 'ae';
      if (k && !RX_MOT.test(k)) k = ' ';
      CAR[c] = k;
    }
    return k;
  }
  function plages(texte, toks) {               // positions (dans le texte d’origine) des débuts de mots cherchés
    var n = '', map = [];
    for (var i = 0; i < texte.length; i++) {
      var k = carNorm(texte.charAt(i));
      if (!k) continue;
      for (var j = 0; j < k.length; j++) { n += k.charAt(j); map.push(i); }
    }
    var h = ' ' + n, out = [];
    toks.forEach(function (t) {
      var q = ' ' + t, x = -1;
      while ((x = h.indexOf(q, x + 1)) >= 0) out.push([map[x], map[x + t.length - 1] + 1]);
    });
    out.sort(function (a, b) { return a[0] - b[0] || b[1] - a[1]; });
    var fus = [];
    out.forEach(function (r) { var d = fus[fus.length - 1]; if (d && r[0] <= d[1]) d[1] = Math.max(d[1], r[1]); else fus.push(r.slice()); });
    return fus;
  }
  function surligner(cible, texte, pl, de, a) {  // texte[de:a] avec <mark> sur les plages
    var pos = de;
    pl.forEach(function (r) {
      var x = Math.max(r[0], de), y = Math.min(r[1], a);
      if (y <= x) return;
      if (x > pos) cible.appendChild(doc.createTextNode(texte.slice(pos, x)));
      cible.appendChild(el('mark', '', texte.slice(x, y)));
      pos = y;
    });
    if (pos < a) cible.appendChild(doc.createTextNode(texte.slice(pos, a)));
  }
  function extrait(cible, texte, toks) {
    var pl = plages(texte, toks), de = 0, a = texte.length;
    if (a > EXTRAIT) {
      var c = pl.length ? pl[0][0] : 0;
      de = Math.max(0, c - 55);
      if (de > 0) { var sp = texte.indexOf(' ', de); de = sp >= 0 && sp < c ? sp + 1 : de; }
      a = Math.min(texte.length, de + EXTRAIT);
      if (a < texte.length) { var sp2 = texte.lastIndexOf(' ', a); a = sp2 > c ? sp2 : a; }
    }
    if (de > 0) cible.appendChild(doc.createTextNode('…'));
    surligner(cible, texte, pl, de, a);
    if (a < texte.length) cible.appendChild(doc.createTextNode('…'));
  }
  function meilleurTexte(s, toks) {            // le paragraphe de la section qui contient le plus de mots cherchés
    var l = D.textes[s], best = -1, bs = -1;
    for (var i = 0; i < l.length; i++) {
      var h = D.tn[l[i]], sc = 0;
      toks.forEach(function (t) { if (h.indexOf(' ' + t) >= 0) sc++; });
      if (sc > bs) { bs = sc; best = l[i]; }
      if (sc === toks.length) break;
    }
    return best >= 0 ? D.T[best][1] : '';
  }

  // ── Boite de dialogue ──
  var CSS = '.an-sr{position:absolute!important;width:1px;height:1px;margin:-1px;padding:0;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap;border:0}' +
    'html.an-bloque,html.an-bloque body{overflow:hidden}' +
    /* page couverte par la recherche ou le tiroir : ses animations s’arrêtent (moins de travail à chaque frappe) */
    'html.an-bloque main *,html.an-bloque main *::before,html.an-bloque main *::after{animation-play-state:paused!important}' +
    '.an-rech{position:fixed;inset:0;width:100%;height:100%;max-width:none;max-height:none;margin:0;padding:0;border:0;' +
    'background:transparent;color:var(--ink,#18213B);overflow:hidden;font:400 1rem/1.45 var(--font-body,system-ui,sans-serif)}' +
    '.an-rech:not([open]){display:none}' +
    '.an-rech::backdrop{background:rgba(6,10,22,.55)}' +
    '.an-rech.an-sans-modal{z-index:2147482000;background:rgba(6,10,22,.55)}' +
    '.an-rech-boite{position:relative;display:flex;flex-direction:column;width:min(720px,calc(100% - 32px));max-height:min(80vh,760px);' +
    'margin:min(9vh,88px) auto 0;background:var(--sheet,var(--panel-solid,#fff));border:1px solid var(--rule,var(--panel-line,#CBD2E0));' +
    'border-radius:18px;box-shadow:0 32px 80px -24px rgba(4,8,20,.55),0 6px 18px rgba(4,8,20,.18);overflow:hidden}' +
    '.an-rech-champ{display:flex;align-items:center;gap:10px;padding:8px 10px 8px 18px;border-bottom:1px solid var(--rule,var(--panel-line,#CBD2E0))}' +
    '.an-rech-champ .an-ic{flex:none;width:22px;height:22px;color:var(--gold-ink,#8A5A00)}' +
    '.an-rech-champ input{flex:1;min-width:0;height:52px;margin:0;padding:0;border:0;background:none;color:var(--ink,#18213B);' +
    'font:500 1.15rem/1.2 var(--font-body,system-ui,sans-serif);outline:none;-webkit-appearance:none;appearance:none}' +
    '.an-rech-champ input::placeholder{color:var(--muted,#56607D);opacity:1}' +
    '.an-rech-champ input::-webkit-search-cancel-button{-webkit-appearance:none;display:none}' +
    '.an-rech-x{flex:none;display:inline-flex;align-items:center;justify-content:center;gap:6px;min-width:44px;height:44px;padding:0 10px;' +
    'border:0;border-radius:10px;background:none;color:var(--muted,#56607D);font:500 .78rem/1 var(--font-mono,ui-monospace,monospace);cursor:pointer}' +
    '.an-rech-x:hover{background:var(--tint,rgba(160,175,220,.14));color:var(--ink,#18213B)}' +
    '.an-rech-x .an-ic{width:18px;height:18px;color:inherit}' +
    '.an-rech-x kbd{font:inherit;padding:2px 6px;border:1px solid var(--rule,var(--panel-line,#CBD2E0));border-radius:6px}' +
    '.an-rech-res{flex:1 1 auto;min-height:0;overflow-y:auto;overscroll-behavior:contain;padding:4px 8px 12px;contain:layout style paint}' +
    '.an-rech-res:empty{display:none}' +
    '.an-r-groupe{margin:0;padding:0;content-visibility:auto;contain-intrinsic-size:auto 220px}' +
    '.an-r-page{display:flex;align-items:baseline;justify-content:space-between;gap:12px;margin:14px 12px 6px;' +
    'font:600 .76rem/1.3 var(--font-mono,ui-monospace,monospace);letter-spacing:.08em;text-transform:uppercase;color:var(--muted,#56607D)}' +
    '.an-r-tag{flex:none;font-weight:500;letter-spacing:.06em;color:var(--gold-ink,#8A5A00)}' +
    '.an-r-opt{display:grid;gap:3px;padding:10px 14px;border-radius:12px;color:var(--ink,#18213B);text-decoration:none;cursor:pointer;scroll-margin:10px 0}' +
    '.an-r-opt:hover{background:var(--tint,rgba(160,175,220,.12))}' +
    '.an-r-opt[aria-selected="true"]{background:var(--tint,rgba(160,175,220,.16));box-shadow:inset 3px 0 0 var(--gold-ui,var(--gold,#C98A12))}' +
    '.an-r-titre{font:600 1.02rem/1.3 var(--font-body,system-ui,sans-serif);color:var(--ink,#18213B)}' +
    '.an-r-titre .an-ic{display:inline-block;width:14px;height:14px;margin-left:4px;vertical-align:-1px;color:var(--muted,#56607D)}' +
    '.an-r-ext{font:400 .93rem/1.45 var(--font-body,system-ui,sans-serif);color:var(--muted,#56607D)}' +
    '.an-r-plus{margin:2px 14px 0;font-size:.86rem;color:var(--muted,#56607D)}' +
    '.an-r-ref{font:500 .85em/1 var(--font-mono,ui-monospace,monospace);color:var(--gold-ink,#8A5A00);white-space:nowrap}' +
    '.an-rech mark{background:rgba(201,138,18,.28);background:color-mix(in srgb,var(--gold,#C98A12) 30%,transparent);color:inherit;' +
    'border-radius:3px;padding:0 1px;box-decoration-break:clone;-webkit-box-decoration-break:clone}' +
    '.an-rech-etat{margin:0;padding:10px 18px;border-top:1px solid var(--rule,var(--panel-line,#CBD2E0));font-size:.92rem;color:var(--muted,#56607D)}' +
    '.an-rech-etat:empty{display:none}' +
    '.an-rech-vide{padding:18px 18px 8px;display:grid;gap:12px;color:var(--muted,#56607D);font-size:.95rem}' +
    '.an-rech-vide p{margin:0}' +
    '.an-rech-ex{display:flex;flex-wrap:wrap;gap:8px}' +
    '.an-rech-ex button{display:inline-flex;align-items:center;min-height:44px;padding:0 14px;border:1px solid var(--rule,var(--panel-line,#CBD2E0));' +
    'border-radius:999px;background:none;color:var(--ink,#18213B);font:500 .95rem/1 var(--font-body,system-ui,sans-serif);cursor:pointer}' +
    '.an-rech-ex button:hover{border-color:var(--muted,#56607D)}' +
    '.an-rech-pied{display:flex;flex-wrap:wrap;gap:6px 16px;padding:9px 18px 11px;border-top:1px solid var(--rule,var(--panel-line,#CBD2E0));' +
    'font:400 .8rem/1.3 var(--font-body,system-ui,sans-serif);color:var(--muted,#56607D)}' +
    '.an-rech-pied kbd{display:inline-block;min-width:1.6em;margin-right:3px;padding:1px 5px;border:1px solid var(--rule,var(--panel-line,#CBD2E0));' +
    'border-radius:5px;font:500 .75rem/1.3 var(--font-mono,ui-monospace,monospace);text-align:center}' +
    '.an-rech :focus-visible{outline:2px solid var(--gold-ink,#8A5A00);outline-offset:2px}' +
    '.an-rech-champ input:focus-visible{outline:none}' +
    '@media (max-width:640px){.an-rech-boite{width:100%;height:100%;max-height:none;margin:0;border:0;border-radius:0;' +
    'padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}' +
    '.an-rech-champ{padding-left:14px}.an-rech-x kbd{display:none}.an-rech-pied{display:none}}' +
    /* vue 3D : entrée du menu */
    '.an-3d-chercher{display:flex;align-items:center;gap:10px;width:100%;min-height:44px;margin:0 0 10px;padding:8px 10px;' +
    'border:1px solid var(--panel-line,rgba(160,175,220,.24));border-radius:10px;background:none;color:var(--ink,#E8EBF5);' +
    'font:500 .95rem/1.2 var(--font-body,system-ui,sans-serif);text-align:left;cursor:pointer}' +
    '.an-3d-chercher:hover{border-color:var(--gold,#F0B33C)}' +
    '.an-3d-chercher:focus-visible{outline:2px solid var(--gold-ink,#F6C766);outline-offset:2px}' +
    '.an-3d-chercher .an-ic{width:18px;height:18px;color:var(--gold-ink,#F6C766)}' +
    '.an-3d-chercher kbd{margin-left:auto;padding:1px 6px;border:1px solid var(--panel-line,rgba(160,175,220,.24));border-radius:5px;' +
    'font:500 .75rem/1.3 var(--font-mono,ui-monospace,monospace);color:var(--muted,#A4ADC8)}' +
    '@media (hover:none){.an-3d-chercher kbd{display:none}}' +
    '@media print{.an-rech{display:none!important}}';
  function styler() {
    if (doc.getElementById('an-rech-style')) return;
    var st = el('style');
    st.id = 'an-rech-style';
    st.textContent = CSS;
    doc.head.appendChild(st);
  }

  function construireDialogue() {
    styler();
    var d = el('dialog', 'an-rech');
    d.setAttribute('aria-labelledby', 'an-rech-titre');
    d.setAttribute('data-glossaire', 'non');
    d.setAttribute('data-ecouter', 'non');
    var boite = el('div', 'an-rech-boite');
    var titre = el('h2', 'an-sr', 'Rechercher dans l’atlas');
    titre.id = 'an-rech-titre';
    var champ = el('div', 'an-rech-champ');
    champ.appendChild(icone(I_LOUPE));
    var inp = el('input');
    inp.type = 'search';
    inp.id = 'an-rech-q';
    inp.setAttribute('role', 'combobox');
    inp.setAttribute('aria-autocomplete', 'list');
    inp.setAttribute('aria-expanded', 'false');
    inp.setAttribute('aria-controls', 'an-rech-liste');
    inp.setAttribute('aria-describedby', 'an-rech-aide');
    inp.setAttribute('aria-label', 'Rechercher dans l’atlas');
    inp.setAttribute('autocomplete', 'off');
    inp.setAttribute('autocapitalize', 'off');
    inp.setAttribute('spellcheck', 'false');
    inp.setAttribute('enterkeyhint', 'search');
    inp.placeholder = 'Un mot, un nom, une référence (57:6.5)…';
    champ.appendChild(inp);
    var x = el('button', 'an-rech-x');
    x.type = 'button';
    x.setAttribute('aria-label', 'Fermer la recherche');
    x.appendChild(el('kbd', '', 'Échap'));
    x.appendChild(icone(I_FERMER));
    champ.appendChild(x);
    var liste = el('div', 'an-rech-res');
    liste.id = 'an-rech-liste';
    liste.setAttribute('role', 'listbox');
    liste.setAttribute('aria-label', 'Résultats de la recherche');
    var vide = el('div', 'an-rech-vide');
    var etat = el('p', 'an-rech-etat');
    etat.setAttribute('role', 'status');
    etat.setAttribute('aria-live', 'polite');
    var pied = el('p', 'an-rech-pied');
    pied.id = 'an-rech-aide';
    [['↑', '↓', 'choisir'], ['Entrée', 'ouvrir'], ['Échap', 'fermer']].forEach(function (k) {
      var s = el('span');
      k.slice(0, -1).forEach(function (t) { s.appendChild(el('kbd', '', t)); });
      s.appendChild(doc.createTextNode(' ' + k[k.length - 1]));
      pied.appendChild(s);
    });
    boite.appendChild(titre);
    boite.appendChild(champ);
    boite.appendChild(vide);
    boite.appendChild(liste);
    boite.appendChild(etat);
    boite.appendChild(pied);
    d.appendChild(boite);
    doc.body.appendChild(d);
    R.dlg = d; R.champ = inp; R.liste = liste; R.etat = etat; R.vide = vide;
    remplirVide();

    inp.addEventListener('input', function () {
      cancelAnimationFrame(R.minuterie);
      R.minuterie = requestAnimationFrame(function () { lancer(inp.value); });
    });
    inp.addEventListener('keydown', function (e) {
      var k = e.key;
      if (k === 'ArrowDown' || k === 'ArrowUp') {
        e.preventDefault();
        if (!R.opts.length) return;
        var i = R.actif < 0 ? (k === 'ArrowDown' ? 0 : R.opts.length - 1) : (R.actif + (k === 'ArrowDown' ? 1 : -1) + R.opts.length) % R.opts.length;
        activer(i);
      } else if (k === 'Enter') {
        e.preventDefault();
        if (R.derniere !== inp.value && D) { cancelAnimationFrame(R.minuterie); lancer(inp.value); }   // frappe pas encore affichée
        if (R.actif >= 0) suivre(R.opts[R.actif], true);
        else if (R.opts.length) suivre(R.opts[0], true);
      } else if (k === 'Home' && e.ctrlKey && R.opts.length) { e.preventDefault(); activer(0); }
      else if (k === 'End' && e.ctrlKey && R.opts.length) { e.preventDefault(); activer(R.opts.length - 1); }
    });
    x.addEventListener('click', function () { fermerRecherche(); });
    d.addEventListener('click', function (e) {
      if (e.target === d) { fermerRecherche(); return; }
      var o = e.target.closest && e.target.closest('.an-r-opt');
      if (o) { e.preventDefault(); suivre(o, false); }
    });
    d.addEventListener('keydown', function (e) {
      e.stopPropagation();                  // la vue 3D ne doit pas réagir aux touches de la recherche
      if (e.key === 'Escape') { e.preventDefault(); fermerRecherche(); }
      else if (e.key === 'Tab') {             // le focus reste dans la boite (sans showModal)
        var f = focusables(d);
        if (!f.length) return;
        var i = f.indexOf(doc.activeElement);
        if (e.shiftKey && i <= 0) { e.preventDefault(); f[f.length - 1].focus(); }
        else if (!e.shiftKey && i === f.length - 1) { e.preventDefault(); f[0].focus(); }
      }
    });
    d.addEventListener('cancel', function (e) { e.preventDefault(); fermerRecherche(); });
  }
  function remplirVide() {
    var v = R.vide;
    v.textContent = '';
    v.appendChild(el('p', '', 'Cherche dans toutes les pages de l’atlas, le glossaire et la vue 3D. Les accents et les majuscules ne comptent pas.'));
    var ex = el('div', 'an-rech-ex');
    ['Ajusteur de Pensée', 'Havona', 'séraphins', 'Melchizédek', '15:14.5'].forEach(function (t) {
      var b = el('button', '', t);
      b.type = 'button';
      b.addEventListener('click', function () { R.champ.value = t; lancer(t); R.champ.focus(); });
      ex.appendChild(b);
    });
    var p = el('p', '', 'Exemples' + NB + ':');
    v.appendChild(p);
    v.appendChild(ex);
  }

  function activer(i) {
    if (R.actif >= 0 && R.opts[R.actif]) R.opts[R.actif].setAttribute('aria-selected', 'false');
    R.actif = i;
    var o = R.opts[i];
    if (!o) { R.champ.removeAttribute('aria-activedescendant'); return; }
    o.setAttribute('aria-selected', 'true');
    R.champ.setAttribute('aria-activedescendant', o.id);
    var l = R.liste, av = o.previousElementSibling, rl = l.getBoundingClientRect();
    var haut = (av && av.classList.contains('an-r-page') ? av : o).getBoundingClientRect().top, bas = o.getBoundingClientRect().bottom;
    if (haut < rl.top + 2) l.scrollTop -= rl.top + 2 - haut;
    else if (bas > rl.bottom - 2) l.scrollTop += bas - rl.bottom + 2;
  }
  function suivre(o) {
    if (o.getAttribute('target') === '_blank') { window.open(o.href, '_blank', 'noopener'); return; }
    var u;
    try { u = new URL(o.href, location.href); } catch (e) { return; }
    fermerRecherche(false);
    var memePage = u.pathname === location.pathname || (u.pathname.replace(/index\.html$/, '') === location.pathname.replace(/index\.html$/, ''));
    if (memePage && u.search === location.search) {
      if (u.hash && u.hash !== location.hash) { location.hash = u.hash; return; }
      var c = u.hash ? doc.getElementById(decodeURIComponent(u.hash.slice(1))) : null;
      if (c) c.scrollIntoView({ behavior: mqCalme.matches ? 'auto' : 'smooth', block: 'start' });
      else if (!u.hash) window.scrollTo({ top: 0, behavior: mqCalme.matches ? 'auto' : 'smooth' });
      if (u.hash) try { window.dispatchEvent(new HashChangeEvent('hashchange', { oldURL: location.href, newURL: location.href })); } catch (e) { /* rien */ }
      return;
    }
    location.href = u.href;
  }

  function option(href, ext) {
    var a = el('a', 'an-r-opt');
    a.href = href;
    a.id = 'an-ro-' + R.opts.length;
    a.setAttribute('role', 'option');
    a.setAttribute('aria-selected', 'false');
    a.tabIndex = -1;
    if (ext) { a.target = '_blank'; a.rel = 'noopener'; }
    R.opts.push(a);
    return a;
  }
  function adresse(s) { var x = D.S[s], p = D.P[x[0]]; return p[0] + (x[1] ? '#' + x[1] : ''); }
  function groupe(p, n) {
    var g = el('div', 'an-r-groupe');
    g.setAttribute('role', 'group');
    var t = el('p', 'an-r-page');
    t.id = 'an-rg-' + n;
    t.appendChild(el('span', '', D.P[p][1]));
    if (D.P[p][2]) t.appendChild(el('span', 'an-r-tag', D.P[p][2]));
    g.setAttribute('aria-labelledby', t.id);
    g.appendChild(t);
    return g;
  }
  function afficher(r, q) {
    var l = R.liste;
    if (l.scrollTop) l.scrollTop = 0;         // avant de vider : la mise en page est encore à jour
    l.textContent = '';
    R.opts = [];
    R.actif = -1;
    R.champ.removeAttribute('aria-activedescendant');
    R.vide.hidden = !!q;
    if (!q) { R.etat.textContent = ''; R.champ.setAttribute('aria-expanded', 'false'); return; }
    if (!r) { R.etat.textContent = ''; R.champ.setAttribute('aria-expanded', 'false'); return; }
    if (r.type === 'court') {
      R.etat.textContent = 'Continue' + NB + ': deux lettres au moins.';
      R.champ.setAttribute('aria-expanded', 'false');
      return;
    }
    if (r.type === 'ref') {
      if (r.lien) {
        var g0 = el('div', 'an-r-groupe');
        g0.setAttribute('role', 'group');
        g0.setAttribute('aria-label', 'Le livre');
        var a0 = option(r.lien, true), t0 = el('span', 'an-r-titre', 'Lire ' + r.ref + ' sur urantia.org');
        t0.appendChild(icone(I_EXT));
        a0.appendChild(t0);
        a0.appendChild(el('span', 'an-r-ext', 'Le texte du livre, sur le site de la Fondation Urantia (nouvel onglet)'));
        g0.appendChild(a0);
        l.appendChild(g0);
      }
      r.pages.forEach(function (pg, n) {
        var g = groupe(pg.p, n);
        pg.items.forEach(function (s, k) {
          var a = option(adresse(s)), x = pg.cite[k];
          a.appendChild(el('span', 'an-r-titre', D.S[s][2] || D.P[pg.p][1]));
          var e = el('span', 'an-r-ext');
          var cite = x[1] ? r.f + ':' + r.s + '.' + x[1] + (x[2] > x[1] ? '–' + x[2] : '') : r.f + ':' + r.s;
          e.appendChild(doc.createTextNode(x[1] || !r.par ? 'Cite ' : 'Cite la section '));
          e.appendChild(el('span', 'an-r-ref', cite));
          a.appendChild(e);
          g.appendChild(a);
        });
        if (pg.reste) g.appendChild(el('p', 'an-r-plus', 'et ' + pg.reste + ' autre' + (pg.reste > 1 ? 's' : '') + ' passage' + (pg.reste > 1 ? 's' : '') + ' dans cette page'));
        l.appendChild(g);
      });
      R.etat.textContent = !r.lien ? 'Le livre n’a pas de fascicule ' + r.f + '.' :
        r.total ? (r.total > 1 ? r.total + ' passages de l’atlas citent ' : 'Un passage de l’atlas cite ') + r.ref + (r.pages.length > 1 ? ', dans ' + r.pages.length + ' pages.' : '.') :
        'Aucune page de l’atlas ne cite ' + r.ref + NB + ': le passage reste à lire sur urantia.org.';
    } else {
      r.pages.forEach(function (pg, n) {
        var g = groupe(pg.p, n);
        pg.items.forEach(function (s) {
          var a = option(adresse(s)), titre = D.S[s][2] || D.P[pg.p][1];
          var ti = el('span', 'an-r-titre');
          extrait(ti, titre, r.toks);
          a.appendChild(ti);
          var tx = meilleurTexte(s, r.toks);
          if (tx) { var e = el('span', 'an-r-ext'); extrait(e, tx, r.toks); a.appendChild(e); }
          g.appendChild(a);
        });
        if (pg.reste) g.appendChild(el('p', 'an-r-plus', 'et ' + pg.reste + ' autre' + (pg.reste > 1 ? 's' : '') + ' passage' + (pg.reste > 1 ? 's' : '') + ' dans cette page'));
        l.appendChild(g);
      });
      R.etat.textContent = r.total ? (r.total > 1 ? r.total + ' passages' : 'Un passage') + ' dans ' + (r.nbPages > 1 ? r.nbPages + ' pages' : 'une page') +
        (r.total > MAX_TOTAL ? NB + ': les plus pertinents d’abord.' : '.') :
        'Aucun résultat pour «' + NB + q.trim() + NB + '». Essaie un autre mot, ou le début d’un mot.';
    }
    R.champ.setAttribute('aria-expanded', R.opts.length ? 'true' : 'false');
  }
  function lancer(q) {
    R.derniere = q;
    if (!q.trim()) { afficher(null, ''); return; }
    if (!D) {
      R.etat.textContent = 'Chargement de l’index…';
      chargerIndex().then(function (pret) {
        if (pret && D) { if (R.derniere === q) lancer(q); }
        else R.etat.textContent = 'La recherche n’est pas disponible' + NB + ': son index n’a pas pu être chargé (hors ligne' + NB + '?). Réessaie avec une connexion.';
      });
      return;
    }
    var r = chercher(q);
    R.dernierTemps = r ? r.ms : 0;
    afficher(r, q);
  }

  function ouvrirRecherche(texte) {
    if (!R.dlg) construireDialogue();
    if (R.dlg.open) { R.champ.focus(); return; }
    if (tiroirOuvert) fermerTiroir(false);
    if (deroule) fermerGroupe(deroule);
    R.avant = doc.activeElement;
    bloquer(true);
    if (typeof R.dlg.showModal === 'function') R.dlg.showModal();
    else { R.dlg.setAttribute('open', ''); R.dlg.classList.add('an-sans-modal'); }
    if (typeof texte === 'string') R.champ.value = texte;
    R.champ.focus();
    R.champ.select();
    chargerIndex();
    if (R.champ.value) lancer(R.champ.value);
  }
  function fermerRecherche(rendreFocus) {
    if (!R.dlg || !R.dlg.open) return;
    if (typeof R.dlg.close === 'function' && !R.dlg.classList.contains('an-sans-modal')) R.dlg.close();
    else R.dlg.removeAttribute('open');
    bloquer(false);
    if (rendreFocus === false) return;
    var a = R.avant;
    if (a && a.focus && a.getClientRects().length && !a.closest('[hidden]')) a.focus();
    else { var s = doc.querySelector('#menu > summary, .an-chercher'); if (s && s.focus) s.focus(); }
  }

  /* ════════════ Mise en place ════════════ */
  function demarrer() {
    if (nav) preparerBarre();
    // vue 3D : entrée du menu
    var menu3d = !nav && doc.querySelector('#menu .menu-panel');
    if (menu3d && !menu3d.querySelector('.an-3d-chercher')) {
      styler();
      var b = el('button', 'an-3d-chercher');
      b.type = 'button';
      b.setAttribute('data-chercher', '');
      b.setAttribute('aria-keyshortcuts', '/ Control+K');
      b.appendChild(icone(I_LOUPE));
      b.appendChild(el('span', '', 'Rechercher dans l’atlas'));
      b.appendChild(el('kbd', '', '/'));
      menu3d.insertBefore(b, menu3d.firstChild);
      // le menu ouvert montre l’entrée de recherche : l’index se charge déjà (au toucher, il n’y a pas de survol)
      var menu = menu3d.closest('details');
      if (menu) menu.addEventListener('toggle', function () { if (menu.open) chargerIndex(); });
    }
    // l’index se charge dès qu’on approche du bouton (survol, focus, toucher) : la boite s’ouvre prête
    function prevenir(e) { if (e.target.closest && e.target.closest('[data-chercher]')) chargerIndex(); }
    doc.addEventListener('pointerover', prevenir, { passive: true });
    doc.addEventListener('focusin', prevenir);
    doc.addEventListener('click', function (e) {
      var b = e.target.closest && e.target.closest('[data-chercher]');
      if (!b) return;
      e.preventDefault();
      var m = b.closest('details[open]');
      if (m && !m.classList.contains('an-d')) m.open = false;   // menu de la vue 3D
      ouvrirRecherche();
    });
    doc.addEventListener('keydown', function (e) {
      if (e.defaultPrevented || e.altKey) return;
      var k = e.key;
      if ((k === 'k' || k === 'K') && (e.ctrlKey || e.metaKey) && !e.shiftKey) { e.preventDefault(); ouvrirRecherche(); return; }
      if (k === '/' && !e.ctrlKey && !e.metaKey && !saisie(e.target)) { e.preventDefault(); ouvrirRecherche(); }
    });
    // liens externes ouverts dans un nouvel onglet : annoncés aux lecteurs d’écran s’ils ne le disent pas déjà
    if (!nav) styler();
    toArray(doc.querySelectorAll('a[target="_blank"]')).forEach(function (a) {
      var t = (a.getAttribute('aria-label') || '') + ' ' + (a.getAttribute('title') || '') + ' ' + a.textContent;
      if (/nouvel(le)? (onglet|fenêtre)/i.test(t)) return;
      if (a.hasAttribute('aria-label')) a.setAttribute('aria-label', a.getAttribute('aria-label') + ', nouvel onglet');
      else a.appendChild(el('span', 'an-sr', ' (nouvel onglet)'));
    });
    versHorsLigne();
  }
  if (doc.readyState === 'loading') doc.addEventListener('DOMContentLoaded', demarrer); else demarrer();
  window.addEventListener('pagehide', function () { if (tiroirOuvert) fermerTiroir(false); });

  window.atlasNav = {
    ouvrirRecherche: ouvrirRecherche,
    fermerRecherche: fermerRecherche,
    chargerIndex: chargerIndex,
    chercher: function (q) { return D ? chercher(q) : null; },
    // essais et mesures : une frappe complète (recherche + affichage), dialogue ouvert et index chargé ; en ms
    mesurer: function (q) {
      if (!D || !R.dlg) return -1;
      var t0 = performance.now();
      R.champ.value = q;
      lancer(q);
      void R.liste.offsetHeight;             // styles et mise en page des résultats comptés aussi
      return performance.now() - t0;
    },
    index: function () { return D; },
    ouvrirTiroir: function () { ouvrirTiroir(); },
    fermerTiroir: function () { fermerTiroir(); },
    norm: norm
  };
})();
