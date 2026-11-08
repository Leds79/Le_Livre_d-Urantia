/* Musique des sphères : nappe sonore douce générée en direct par le navigateur (Web Audio).
   Composition originale, sans fichier audio ni droit d'auteur : accords lents en ré, cloches
   lointaines sur la gamme pentatonique, réverbération. Désactivée par défaut ; un bouton portant
   l'attribut data-musique l'active ou la coupe, et le choix est retenu sur l'appareil. */
(function (root) {
  'use strict';

  var CLE = 'atlas-musique';
  var ACCORDS = [
    [50, 57, 64, 66],   // ré, quinte, neuvième, tierce
    [47, 54, 62, 69],   // si mineur septième
    [43, 50, 57, 59],   // sol, neuvième
    [45, 52, 59, 64]    // la suspendu
  ];
  var CLOCHES = [74, 76, 78, 81, 83, 86, 88]; // pentatonique de ré, octaves aiguës
  var DUREE_ACCORD = 14, RECOUVREMENT = 6;

  function hz(m) { return 440 * Math.pow(2, (m - 69) / 12); }

  // Le moteur fonctionne sur tout contexte audio, y compris hors ligne (pour les tests).
  function Moteur(ctx, opts) {
    opts = opts || {};
    this.ctx = ctx;
    this.hasard = opts.hasard || Math.random;
    var sortie = ctx.createGain(); sortie.gain.value = 0; this.sortie = sortie;
    var comp = ctx.createDynamicsCompressor();
    comp.threshold.value = -20; comp.knee.value = 20; comp.ratio.value = 3; comp.attack.value = 0.08; comp.release.value = 0.8;
    var filtre = ctx.createBiquadFilter(); filtre.type = 'lowpass'; filtre.frequency.value = 2200; filtre.Q.value = 0.4;
    var reverb = ctx.createConvolver(); reverb.buffer = this.impulsion(7, 2.4);
    var mouille = ctx.createGain(); mouille.gain.value = 0.6;
    var sec = ctx.createGain(); sec.gain.value = 0.55;
    this.bus = ctx.createGain();
    this.bus.connect(filtre); filtre.connect(sec); filtre.connect(reverb); reverb.connect(mouille);
    sec.connect(comp); mouille.connect(comp); comp.connect(sortie); sortie.connect(ctx.destination);
    var lfo = ctx.createOscillator(), lfoG = ctx.createGain();
    lfo.frequency.value = 0.025; lfoG.gain.value = 600; lfo.connect(lfoG); lfoG.connect(filtre.frequency); lfo.start();
    this.prochainAccord = ctx.currentTime + 0.1;
    this.prochaineCloche = ctx.currentTime + 3;
    this.numero = 0;
  }
  Moteur.prototype.impulsion = function (duree, chute) {
    var ctx = this.ctx, taux = ctx.sampleRate, n = Math.floor(taux * duree), buf = ctx.createBuffer(2, n, taux);
    for (var c = 0; c < 2; c++) {
      var d = buf.getChannelData(c);
      for (var i = 0; i < n; i++) d[i] = (this.hasard() * 2 - 1) * Math.pow(1 - i / n, chute);
    }
    return buf;
  };
  Moteur.prototype.panoramique = function (v) {
    if (this.ctx.createStereoPanner) { var p = this.ctx.createStereoPanner(); p.pan.value = v; return p; }
    return this.ctx.createGain();
  };
  Moteur.prototype.nappe = function (t, duree, midi) {
    var ctx = this.ctx, g = ctx.createGain(), p = this.panoramique((this.hasard() * 2 - 1) * 0.6);
    var crete = 0.08, attaque = 4.5, extinction = 6;
    g.gain.setValueAtTime(0, t);
    g.gain.linearRampToValueAtTime(crete, t + attaque);
    g.gain.setValueAtTime(crete, t + duree - extinction);
    g.gain.linearRampToValueAtTime(0, t + duree);
    g.connect(p); p.connect(this.bus);
    var formes = ['sine', 'triangle'], ecarts = [-6, 6], poids = [0.65, 0.35];
    for (var k = 0; k < 2; k++) {
      var o = ctx.createOscillator(), og = ctx.createGain();
      o.type = formes[k]; o.frequency.value = hz(midi); o.detune.value = ecarts[k] + (this.hasard() * 4 - 2);
      og.gain.value = poids[k];
      o.connect(og); og.connect(g); o.start(t); o.stop(t + duree + 0.1);
    }
  };
  Moteur.prototype.cloche = function (t, midi) {
    var ctx = this.ctx, g = ctx.createGain(), p = this.panoramique((this.hasard() * 2 - 1) * 0.8);
    var crete = 0.045 + this.hasard() * 0.035, chute = 3 + this.hasard() * 3;
    g.gain.setValueAtTime(0.0001, t);
    g.gain.exponentialRampToValueAtTime(crete, t + 0.02);
    g.gain.exponentialRampToValueAtTime(0.0001, t + chute);
    g.connect(p); p.connect(this.bus);
    var partiels = [[1, 1], [2.76, 0.18], [5.4, 0.06]];
    for (var k = 0; k < partiels.length; k++) {
      var o = ctx.createOscillator(), og = ctx.createGain();
      o.type = 'sine'; o.frequency.value = hz(midi) * partiels[k][0]; og.gain.value = partiels[k][1];
      o.connect(og); og.connect(g); o.start(t); o.stop(t + chute + 0.1);
    }
  };
  // Programme les évènements jusqu'à t1 (secondes, horloge du contexte).
  Moteur.prototype.programmer = function (t1) {
    var t0 = this.ctx.currentTime;
    while (this.prochainAccord < t1) {
      var a = ACCORDS[this.numero % ACCORDS.length], debut = Math.max(this.prochainAccord, t0), duree = DUREE_ACCORD + RECOUVREMENT;
      for (var i = 0; i < a.length; i++) this.nappe(debut, duree, a[i]);
      if (this.numero % 2 === 0) this.nappe(debut, duree, a[0] - 12);
      this.numero++; this.prochainAccord += DUREE_ACCORD;
    }
    while (this.prochaineCloche < t1) {
      this.cloche(Math.max(this.prochaineCloche, t0), CLOCHES[Math.floor(this.hasard() * CLOCHES.length)]);
      this.prochaineCloche += 2.5 + this.hasard() * 5;
    }
  };
  Moteur.prototype.fondu = function (vers, duree) {
    var g = this.sortie.gain, maintenant = this.ctx.currentTime;
    g.cancelScheduledValues(maintenant); g.setValueAtTime(g.value, maintenant); g.linearRampToValueAtTime(vers, maintenant + duree);
  };

  var AC = root.AudioContext || root.webkitAudioContext;
  var ctx = null, moteur = null, minuterie = null, active = false, volume = 0.9;

  function retenir(v) { try { root.localStorage.setItem(CLE, v ? '1' : '0'); } catch (e) { /* stockage indisponible */ } }
  function voulue() { try { return root.localStorage.getItem(CLE) === '1'; } catch (e) { return false; } }
  function tic() { if (moteur) moteur.programmer(ctx.currentTime + 8); }
  function boucle(oui) { clearInterval(minuterie); minuterie = oui ? setInterval(tic, 2000) : null; }

  function synchroniser() {
    var els = document.querySelectorAll('[data-musique]');
    for (var i = 0; i < els.length; i++) {
      els[i].setAttribute('aria-pressed', active ? 'true' : 'false');
      els[i].setAttribute('title', active ? 'Couper la musique douce' : 'Écouter une musique douce');
    }
  }
  function demarrer() {
    if (!AC) return false;
    if (!ctx) { ctx = new AC(); moteur = new Moteur(ctx); }
    if (ctx.resume) ctx.resume();
    active = true; tic(); boucle(true); moteur.fondu(volume, 3); synchroniser();
    return true;
  }
  function arreter() {
    active = false; synchroniser();
    if (!ctx) return;
    boucle(false); moteur.fondu(0, 1.5);
    setTimeout(function () { if (!active && ctx.suspend) ctx.suspend(); }, 1700);
  }
  function basculer() {
    if (active) { arreter(); retenir(false); } else if (demarrer()) retenir(true);
  }

  document.addEventListener('click', function (e) {
    var b = e.target.closest ? e.target.closest('[data-musique]') : null;
    if (b) { e.preventDefault(); basculer(); }
  });
  // Onglet caché : fondu et mise en veille ; retour : reprise.
  document.addEventListener('visibilitychange', function () {
    if (!ctx || !active) return;
    if (document.hidden) {
      boucle(false); moteur.fondu(0, 0.5);
      setTimeout(function () { if (document.hidden && ctx.suspend) ctx.suspend(); }, 600);
    } else {
      if (ctx.resume) ctx.resume();
      tic(); boucle(true); moteur.fondu(volume, 2);
    }
  });
  // Si la musique était active sur la page précédente, elle reprend au premier geste
  // (les navigateurs interdisent le son avant une action de la personne).
  if (AC && voulue()) {
    var types = ['pointerdown', 'keydown', 'touchstart'];
    var armer = function (e) {
      if (e.target.closest && e.target.closest('[data-musique]')) return;
      types.forEach(function (t) { document.removeEventListener(t, armer, true); });
      demarrer();
    };
    types.forEach(function (t) { document.addEventListener(t, armer, true); });
  }
  // Les boutons sont écrits avec l'attribut hidden : ils n'apparaissent que si ce script est chargé
  // et que le navigateur sait produire le son (ils restent cachés sur les versions sans le script).
  function preparer() {
    var els = document.querySelectorAll('[data-musique]');
    for (var i = 0; i < els.length; i++) els[i].hidden = !AC;
    synchroniser();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', preparer);
  else preparer();

  root.atlasMusique = {
    Moteur: Moteur,
    basculer: basculer,
    demarrer: demarrer,
    arreter: arreter,
    regler: function (v) { volume = Math.max(0, Math.min(1, v)); if (active && moteur) moteur.fondu(volume, 0.3); },
    estActive: function () { return active; }
  };
})(window);
