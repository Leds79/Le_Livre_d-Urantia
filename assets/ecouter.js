/* Écouter : lecture à voix haute de la page, par la synthèse vocale du navigateur (speechSynthesis).
   construire_site.py place dans la barre commune un bouton « Écouter » (data-ecouter) ; sur téléphone, il est dans le
   menu. Le bouton n’est montré que si le navigateur sait lire : la classe an-tts est posée sur <html> dès le début de
   la page, d’où aucun décalage de la barre. Ce script (assets/ecouter.js) :
   - lit le texte principal (<main>) bloc par bloc (titres, paragraphes, éléments de liste, légendes, citations, lignes
     de tableau), sans la barre, le pied, les références (.ref), les boutons, les formulaires, le quiz, ni ce qui est
     caché ou aria-hidden ; la lecture commence au premier bloc visible à l’écran ;
   - choisit une voix française si le navigateur en a une (celle de la langue de l’appareil d’abord : fr-CA, fr-FR…) ;
   - affiche un lecteur flottant : Lecture/Pause, Arrêt, vitesse, position (bloc lu sur le nombre de blocs) ;
   - surligne le bloc lu et le suit à l’écran : défilement doux, immédiat avec « moins d’animations », suspendu
     quelques secondes quand la personne fait défiler la page elle-même ;
   - la pause arrête la voix et reprend au début de la phrase en cours (speechSynthesis.pause est inégal selon les
     navigateurs) ; la lecture s’arrête au changement de page.
   La vue 3D n’a pas de bouton « Écouter » (voir CONSTRUIRE.md). */
(function () {
  'use strict';
  if (window.atlasEcouter) return;
  var synth = window.speechSynthesis, Enonce = window.SpeechSynthesisUtterance;
  var doc = document, html = doc.documentElement, NB = '\u00a0';
  if (!synth || !Enonce || !doc.querySelector || !doc.createTreeWalker) return;

  var BLOCS = 'h1,h2,h3,h4,h5,h6,p,li,dt,dd,figcaption,blockquote,tr';
  var EXCLUS = 'nav,footer,aside.hl,.atlas-suite,.atlas-nav,.ref,button,[role="button"]:not(.gl-mot),input,select,textarea,label,' +
    'fieldset,form,[role="toolbar"],[role="tablist"],[role="search"],svg,canvas,video,audio,iframe,script,style,noscript,template,' +
    'dialog,summary,[aria-hidden="true"],[hidden],.sr-only,.vh,.visually-hidden,.an-sr,.eyebrow,.qz,.gl-bulle,.ec-lecteur,[data-ecouter="non"]';
  var MAX = 220;                             // longueur d’un énoncé : les longs énoncés sont coupés net par certains navigateurs
  var VITESSES = [[0.75, '0,75×'], [1, '1×'], [1.25, '1,25×'], [1.5, '1,5×'], [1.75, '1,75×']];
  var CLE = 'atlas-ecouter-vitesse';
  var mqCalme = window.matchMedia ? window.matchMedia('(prefers-reduced-motion: reduce)') : { matches: false };

  var etat = 'arret', liste = [], iBloc = 0, iMorceau = 0, gen = 0, enCours = null, voix = null, vitesse = 1;
  var lecteur = null, bLp = null, bStop = null, lPos = null, lTitre = null, sel = null, lu = null, dernierGeste = 0, garde = 0;
  try { var v = parseFloat(localStorage.getItem(CLE)); if (v >= 0.5 && v <= 2) vitesse = v; } catch (e) { /* stockage indisponible */ }

  /* ── Voix ── */
  function choisirVoix() {
    var vs = [];
    try { vs = synth.getVoices() || []; } catch (e) { vs = []; }
    var langue = (navigator.language || 'fr-FR').toLowerCase(), best = null, bs = -1;
    vs.forEach(function (x) {
      var l = (x.lang || '').toLowerCase().replace('_', '-');
      if (l.indexOf('fr') !== 0) return;
      var s = 10 + (l === langue ? 4 : 0) + (l === 'fr-fr' || l === 'fr-ca' ? 1 : 0) +
        (/natural|neural|premium|enhanced|amélioré/i.test(x.name) ? 3 : 0) + (/google/i.test(x.name) ? 1 : 0) + (x.localService ? 1 : 0);
      if (s > bs) { bs = s; best = x; }
    });
    voix = best;
  }
  choisirVoix();
  if (synth.addEventListener) synth.addEventListener('voiceschanged', choisirVoix);
  else synth.onvoiceschanged = choisirVoix;

  /* ── Texte à lire ── */
  function visible(e) {
    if (!e.getClientRects().length) return false;
    var cs = getComputedStyle(e);
    return cs.visibility !== 'hidden' && cs.display !== 'none';
  }
  function texteDe(b) {
    if (b.tagName === 'TR') {                // ligne de tableau : cellules séparées par des virgules
      return toArray(b.children).map(function (c) { return c.matches(EXCLUS) ? '' : texteDe(c).trim(); }).filter(Boolean).join(', ');
    }
    var w = doc.createTreeWalker(b, 5 /* éléments et textes */, {
      acceptNode: function (n) {
        if (n.nodeType === 1) return n !== b && (n.matches(BLOCS) || n.matches(EXCLUS)) ? 2 /* rejeter */ : 3 /* passer */;
        return 1;
      }
    });
    var t = '', n, avant = null;
    while ((n = w.nextNode())) {             // deux éléments accolés (pastille « 1 », puis le titre) : une espace entre deux mots
      var v = n.nodeValue;
      if (avant && n.parentNode !== avant && /[0-9A-Za-zÀ-ÿ]$/.test(t) && /^[0-9A-Za-zÀ-ÿ]/.test(v)) t += ' ';
      t += v;
      avant = n.parentNode;
    }
    return t;
  }
  function toArray(l) { return Array.prototype.slice.call(l || []); }
  function nettoyer(t) {
    return t.replace(/\(\s*(?:\d{1,3}:\d{1,2}(?:\.\d{1,3})?(?:\s*[–-]\s*\d{1,3})?[\s,;·]*)+\)/g, '')   // (57:6.5) ou (57:6.5, 58:1.2)
      .replace(/\b\d{1,3}:\d{1,2}(?:\.\d{1,3})?(?:\s*[–-]\s*\d{1,3})?/g, '')
      .replace(/[↗→←↑↓▾▸•]/g, ' ').replace(/\s·\s/g, ', ').replace(/\s+([,.;:!?])/g, '$1')
      .replace(/[\s\u00a0\u202f]+/g, ' ').trim();
  }
  function blocs() {
    var main = doc.querySelector('main') || doc.body, out = [];
    toArray(main.querySelectorAll(BLOCS)).forEach(function (b) {
      if (b.closest(EXCLUS) || !visible(b)) return;
      var t = nettoyer(texteDe(b));
      if (t.length < 2 || !/[0-9A-Za-zÀ-ÿ]/.test(t)) return;
      out.push({ el: b, t: t, h: /^H[1-6]$/.test(b.tagName) });
    });
    return out;
  }
  function morceaux(t) {
    if (t.length <= MAX) return [t];
    var phrases = t.match(/[^.!?…]+(?:[.!?…]+[»”"’)\]]*\s*|$)/g) || [t], out = [], cur = '';
    phrases.forEach(function (p) {
      while (p.length > MAX + 60) {          // phrase très longue : coupée à une virgule ou une espace
        var k = p.lastIndexOf(', ', MAX);
        if (k < MAX / 2) k = p.lastIndexOf(' ', MAX);
        if (k < 20) k = MAX;
        if (cur) { out.push(cur.trim()); cur = ''; }
        out.push(p.slice(0, k + 1).trim());
        p = p.slice(k + 1);
      }
      if (cur && (cur + p).length > MAX) { out.push(cur.trim()); cur = ''; }
      cur += p;
    });
    if (cur.trim()) out.push(cur.trim());
    return out.filter(Boolean);
  }
  function premierVisible() {
    if ((window.scrollY || html.scrollTop) < 120) return 0;
    for (var i = 0; i < liste.length; i++) {
      var r = liste[i].el.getBoundingClientRect();
      if (r.bottom > 90) return i;
    }
    return 0;
  }
  function titreAvant(i) {                   // titre de la partie lue, pour le lecteur
    for (var k = i; k >= 0; k--) if (liste[k].h) return liste[k].t;
    return doc.title.split(' — ')[0];
  }

  /* ── Lecture ── */
  function marquer(e) {
    if (lu === e) return;
    if (lu) lu.classList.remove('ec-lu');
    lu = e;
    if (e) { e.classList.add('ec-lu'); suivre(e); }
  }
  function suivre(e) {
    if (Date.now() - dernierGeste < 4000) return;
    var r = e.getBoundingClientRect(), h = window.innerHeight, bas = h - (lecteur && !lecteur.hidden ? lecteur.offsetHeight + 36 : 24);
    if (r.top >= 70 && r.bottom <= bas) return;
    if (r.top >= 70 && r.top < bas - 40 && r.height > bas - 70) return;   // long bloc déjà commencé à l’écran
    var y = (window.scrollY || html.scrollTop) + r.top - Math.max(84, h * 0.24);
    window.scrollTo({ top: Math.max(0, y), behavior: mqCalme.matches ? 'auto' : 'smooth' });
  }
  ['wheel', 'touchmove'].forEach(function (t) { window.addEventListener(t, function () { dernierGeste = Date.now(); }, { passive: true }); });
  window.addEventListener('keydown', function (e) {
    if (/^(PageUp|PageDown|Home|End|ArrowUp|ArrowDown| )$/.test(e.key) && !(e.target && e.target.closest && e.target.closest('input,textarea,select,[contenteditable]'))) dernierGeste = Date.now();
  });

  function parler() {
    clearTimeout(garde);
    if (etat !== 'lecture') return;
    if (iBloc >= liste.length) { arreter(true); return; }
    var b = liste[iBloc];
    if (!b.m) b.m = morceaux(b.t);
    if (iMorceau >= b.m.length) { iBloc++; iMorceau = 0; parler(); return; }
    marquer(b.el);
    majLecteur();
    var u = new Enonce(b.m[iMorceau]), g = ++gen, parti = false;
    u.lang = voix ? voix.lang : 'fr-FR';
    if (voix) u.voice = voix;
    u.rate = vitesse;
    u.onstart = function () { parti = true; };
    u.onend = function () {
      if (g !== gen || etat !== 'lecture') return;
      iMorceau++;
      parler();
    };
    u.onerror = function (e) {
      if (g !== gen) return;
      var err = e && e.error;
      if (err === 'interrupted' || err === 'canceled') return;
      if (err === 'synthesis-unavailable' || err === 'synthesis-failed' || err === 'audio-hardware' || err === 'voice-unavailable' || err === 'not-allowed') {
        indisponible(err === 'not-allowed');
        return;
      }
      iMorceau++;
      parler();
    };
    enCours = u;                             // gardé en mémoire : sinon certains navigateurs perdent onend
    if (synth.paused) synth.resume();
    try { synth.speak(u); } catch (e) { indisponible(false); return; }
    // aucune voix ne démarre (navigateur sans voix) : on le dit au lieu d’attendre en silence
    garde = setTimeout(function () {
      if (g === gen && etat === 'lecture' && !parti && !synth.speaking && !(synth.getVoices() || []).length) indisponible(false);
    }, 4000);
  }
  function relancer() {                      // après cancel(), certains navigateurs ignorent un speak() immédiat
    gen++;
    synth.cancel();
    setTimeout(parler, 80);
  }
  function lire() {
    if (etat === 'lecture') return;
    if (etat === 'arret') {
      liste = blocs();
      if (!liste.length) { montrer(); annoncer('Rien à lire sur cette page.'); return; }
      iBloc = premierVisible();
      iMorceau = 0;
    }
    etat = 'lecture';
    montrer();
    majBoutons();
    relancer();
  }
  function pause() {
    if (etat !== 'lecture') return;
    etat = 'pause';
    gen++;
    clearTimeout(garde);
    synth.cancel();
    majBoutons();
    majLecteur();
  }
  function arreter(fini) {
    etat = 'arret';
    gen++;
    clearTimeout(garde);
    synth.cancel();
    marquer(null);
    majBoutons();
    if (fini === true && lecteur) { majLecteur(); annoncer('Fin de la page.'); setTimeout(function () { if (etat === 'arret') cacher(); }, 2500); }
    else cacher();
  }
  function basculer() { if (etat === 'lecture') pause(); else lire(); }
  function indisponible(refus) {
    etat = 'arret';
    gen++;
    synth.cancel();
    marquer(null);
    majBoutons();
    montrer();
    majLecteur();
    annoncer(refus ? 'Le navigateur a refusé la lecture' + NB + ': touche de nouveau Écouter.' :
      'La lecture à voix haute n’est pas disponible dans ce navigateur (aucune voix installée).');
  }

  /* ── Lecteur flottant ── */
  var CSS = '.ec-lu{background-color:rgba(201,138,18,.16);background-color:color-mix(in srgb,var(--gold,#C98A12) 15%,transparent);' +
    'box-shadow:0 0 0 6px rgba(201,138,18,.16);box-shadow:0 0 0 6px color-mix(in srgb,var(--gold,#C98A12) 15%,transparent);border-radius:3px;' +
    'transition:background-color .3s ease,box-shadow .3s ease}' +
    '.ec-lecteur{position:fixed;left:50%;bottom:max(14px,env(safe-area-inset-bottom,0px));z-index:900;transform:translateX(-50%);' +
    'display:flex;align-items:center;gap:6px;width:max-content;max-width:calc(100% - 20px);padding:6px 8px 6px 6px;' +
    'background:var(--sheet,#fff);color:var(--ink,#18213B);border:1px solid var(--rule,#CBD2E0);border-radius:999px;' +
    'box-shadow:0 18px 44px -14px rgba(6,10,24,.45),0 3px 10px rgba(6,10,24,.14);font:500 .95rem/1.2 var(--font-body,system-ui,sans-serif)}' +
    '.ec-lecteur[hidden]{display:none}' +
    '.ec-lecteur button{flex:none;display:inline-grid;place-items:center;width:44px;height:44px;margin:0;padding:0;border:0;border-radius:50%;' +
    'background:none;color:var(--ink,#18213B);cursor:pointer}' +
    '.ec-lecteur button:hover{background:var(--tint,rgba(127,127,127,.12))}' +
    '.ec-lecteur .ec-lp{background:var(--gold,#C98A12);color:var(--on-gold,#1B1405)}' +
    '.ec-lecteur .ec-lp:hover{background:var(--gold,#C98A12);filter:brightness(1.06)}' +
    '.ec-lecteur svg{width:18px;height:18px}' +
    '.ec-lecteur :focus-visible{outline:2px solid var(--gold-ink,#8A5A00);outline-offset:2px}' +
    '.ec-info{min-width:0;margin:0 6px;display:grid;gap:1px}' +
    '.ec-titre{max-width:30ch;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-weight:600}' +
    '.ec-pos{font:500 .74rem/1.2 var(--font-mono,ui-monospace,monospace);letter-spacing:.04em;color:var(--muted,#56607D)}' +
    '.ec-vit{position:relative;flex:none;display:inline-flex;align-items:center}' +
    '.ec-vit select{min-height:44px;margin:0;padding:0 26px 0 12px;border:1px solid var(--rule,#CBD2E0);border-radius:999px;' +
    'background:var(--paper,transparent);color:var(--ink,#18213B);font:500 .9rem/1 var(--font-mono,ui-monospace,monospace);' +
    '-webkit-appearance:none;appearance:none;cursor:pointer}' +
    '.ec-vit::after{content:"";position:absolute;right:11px;top:50%;width:6px;height:6px;margin-top:-5px;border:solid var(--muted,#56607D);' +
    'border-width:0 1.6px 1.6px 0;transform:rotate(45deg);pointer-events:none}' +
    '.ec-sr{position:absolute!important;width:1px;height:1px;margin:-1px;padding:0;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap;border:0}' +
    '@media (max-width:480px){.ec-titre{max-width:13ch}.ec-lecteur{gap:2px}.ec-info{margin:0 4px}}' +
    '@media (prefers-reduced-motion:reduce){.ec-lu{transition:none}}' +
    '@media print{.ec-lecteur{display:none!important}.ec-lu{background:none;box-shadow:none}}';
  var SVGNS = 'http://www.w3.org/2000/svg';
  function svg(d, plein) {
    var s = doc.createElementNS(SVGNS, 'svg');
    s.setAttribute('viewBox', '0 0 20 20');
    s.setAttribute('aria-hidden', 'true');
    s.setAttribute('focusable', 'false');
    var p = doc.createElementNS(SVGNS, 'path');
    p.setAttribute('d', d);
    if (plein) p.setAttribute('fill', 'currentColor');
    else { p.setAttribute('fill', 'none'); p.setAttribute('stroke', 'currentColor'); p.setAttribute('stroke-width', '2'); p.setAttribute('stroke-linecap', 'round'); }
    s.appendChild(p);
    return s;
  }
  var D_LIRE = 'M6.5 4.2v11.6l9.3-5.8z', D_PAUSE = 'M5.5 4.5h3v11h-3zM11.5 4.5h3v11h-3z', D_STOP = 'M5.5 5.5h9v9h-9z';
  function construire() {
    if (lecteur) return;
    var st = doc.createElement('style');
    st.id = 'ec-style';
    st.textContent = CSS;
    doc.head.appendChild(st);
    lecteur = doc.createElement('div');
    lecteur.className = 'ec-lecteur';
    lecteur.hidden = true;
    lecteur.setAttribute('role', 'region');
    lecteur.setAttribute('aria-label', 'Lecture à voix haute');
    lecteur.setAttribute('data-glossaire', 'non');
    lecteur.setAttribute('data-ecouter', 'non');
    bLp = doc.createElement('button');
    bLp.type = 'button';
    bLp.className = 'ec-lp';
    bLp.addEventListener('click', basculer);
    bStop = doc.createElement('button');
    bStop.type = 'button';
    bStop.className = 'ec-stop';
    bStop.setAttribute('aria-label', 'Arrêter la lecture');
    bStop.title = 'Arrêter la lecture';
    bStop.appendChild(svg(D_STOP, true));
    bStop.addEventListener('click', function () {        // arrêt : le focus revient au bouton « Écouter » visible
      arreter();
      var b = toArray(doc.querySelectorAll('button[data-ecouter]')).filter(function (x) { return x.getClientRects().length; })[0];
      if (b) b.focus();
    });
    var info = doc.createElement('p');
    info.className = 'ec-info';
    lTitre = doc.createElement('span');
    lTitre.className = 'ec-titre';
    lPos = doc.createElement('span');
    lPos.className = 'ec-pos';
    lPos.setAttribute('aria-live', 'polite');
    info.appendChild(lTitre);
    info.appendChild(lPos);
    var lab = doc.createElement('label');
    lab.className = 'ec-vit';
    var sr = doc.createElement('span');
    sr.className = 'ec-sr';
    sr.textContent = 'Vitesse de lecture';
    sel = doc.createElement('select');
    VITESSES.forEach(function (x) {
      var o = doc.createElement('option');
      o.value = String(x[0]);
      o.textContent = x[1];
      if (Math.abs(x[0] - vitesse) < 0.01) o.selected = true;
      sel.appendChild(o);
    });
    sel.addEventListener('change', function () {
      vitesse = parseFloat(sel.value) || 1;
      try { localStorage.setItem(CLE, String(vitesse)); } catch (e) { /* stockage indisponible */ }
      if (etat === 'lecture') relancer();
    });
    lab.appendChild(sr);
    lab.appendChild(sel);
    lecteur.appendChild(bLp);
    lecteur.appendChild(bStop);
    lecteur.appendChild(info);
    lecteur.appendChild(lab);
    doc.body.appendChild(lecteur);
  }
  function montrer() { construire(); lecteur.hidden = false; majLecteur(); }
  function cacher() { if (lecteur) lecteur.hidden = true; }
  function annoncer(t) { if (lPos) lPos.textContent = t; }
  function majLecteur() {
    if (!lecteur) return;
    bLp.textContent = '';
    bLp.appendChild(svg(etat === 'lecture' ? D_PAUSE : D_LIRE, true));
    var l = etat === 'lecture' ? 'Mettre en pause' : etat === 'pause' ? 'Reprendre la lecture' : 'Lire la page';
    bLp.setAttribute('aria-label', l);
    bLp.title = l;
    if (liste.length) {
      lTitre.textContent = (etat === 'pause' ? 'En pause · ' : '') + titreAvant(Math.min(iBloc, liste.length - 1));
      lPos.textContent = 'Passage ' + Math.min(iBloc + 1, liste.length) + ' sur ' + liste.length;
    } else lTitre.textContent = 'Écouter';
  }
  function majBoutons() {
    toArray(doc.querySelectorAll('[data-ecouter]')).forEach(function (b) {
      if (b.tagName !== 'BUTTON') return;
      b.setAttribute('data-etat', etat);     // l’intitulé change (Écouter, Pause, Reprendre) : pas d’aria-pressed en plus
      var long = b.classList.contains('an-t-btn'), lbl = b.querySelector('.an-lbl');
      var t = etat === 'lecture' ? (long ? 'Mettre la lecture en pause' : 'Pause') : etat === 'pause' ? (long ? 'Reprendre la lecture' : 'Reprendre') : (long ? 'Écouter cette page' : 'Écouter');
      if (lbl) lbl.textContent = t;
      b.title = etat === 'arret' ? 'Écouter la page, lue à voix haute' : t;
    });
  }

  doc.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('button[data-ecouter]');
    if (!b) return;
    e.preventDefault();
    basculer();
  });
  // changement de page : la voix se tait ; si la page revient du cache (retour arrière), le lecteur est en pause
  window.addEventListener('pagehide', function () { if (etat === 'lecture') pause(); gen++; try { synth.cancel(); } catch (e) { /* rien */ } });
  try { synth.cancel(); } catch (e) { /* lecture d’une page précédente */ }
  function demarrer() { majBoutons(); }
  if (doc.readyState === 'loading') doc.addEventListener('DOMContentLoaded', demarrer); else demarrer();

  window.atlasEcouter = {
    lire: lire, pause: pause, arreter: arreter, basculer: basculer,
    etat: function () { return etat; },
    position: function () { return { bloc: iBloc, morceau: iMorceau, total: liste.length, texte: liste[iBloc] ? liste[iBloc].t : '' }; },
    blocs: function () { return blocs().map(function (b) { return b.t; }); },
    voix: function () { return voix ? voix.name + ' (' + voix.lang + ')' : null; }
  };
})();
