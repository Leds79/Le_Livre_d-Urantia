/* Lecture hors ligne et installation de « Le Livre d’Urantia en images ».
   construire_site.py place ce script dans chaque page du site (assets/hors-ligne.js) et écrit sw.js à la racine.
   - Enregistre le service worker, seulement en http(s), dans un contexte sûr et si le navigateur le permet :
     ouvert en file://, le site fonctionne sans lui.
   - Lancé depuis l’écran d’accueil (application installée), demande l’enregistrement de tout l’atlas.
   - Sur l’accueil, anime l’encadré « Lire hors ligne » : installation, téléchargement complet, progression. */
(function () {
  'use strict';
  if (!('serviceWorker' in navigator) || !/^https?:$/.test(location.protocol) || window.isSecureContext === false) return;
  var moi = document.currentScript && document.currentScript.src;
  if (!moi) return;
  var racine = new URL('../', moi);                   // assets/hors-ligne.js → racine du site
  var sw = new URL('sw.js', racine);
  if (sw.origin !== location.origin) return;          // page 404 vue ailleurs que sur le site : pas d’enregistrement croisé
  var NB = ' ';

  function autonome() {
    return (window.matchMedia && window.matchMedia('(display-mode: standalone)').matches) || navigator.standalone === true;
  }
  function envoyer(m) {
    return navigator.serviceWorker.ready.then(function (reg) { if (reg.active) reg.active.postMessage(m); });
  }
  function mo(o) { return (o / 1e6).toFixed(1).replace('.', ','); }

  window.addEventListener('load', function () {
    navigator.serviceWorker.register(sw.href, { scope: racine.href }).catch(function () { /* le site reste consultable en ligne */ });
  });
  if (autonome()) envoyer({ type: 'telecharger' });   // application installée : tout enregistrer

  var boite = document.getElementById('hors-ligne');
  if (!boite) {
    window.addEventListener('appinstalled', function () { envoyer({ type: 'telecharger' }); });
    return;
  }

  /* ---------- encadré « Lire hors ligne » (accueil) ---------- */
  var bInst = document.getElementById('hl-installer');
  var bTel = document.getElementById('hl-telecharger');
  var barre = document.getElementById('hl-barre');
  var etat = document.getElementById('hl-etat');
  var ios = document.getElementById('hl-ios');
  var invite = null, enCours = false, palier = -1, chien = 0;
  boite.hidden = false;
  var estIOS = /iP(hone|ad|od)/.test(navigator.userAgent) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
  if (estIOS && !autonome()) ios.hidden = false;

  function annoncer(t, ok) { etat.textContent = t; etat.classList.toggle('ok', !!ok); }
  function surveiller() {          // un service worker arrêté en cours de route reprend où il en était
    clearTimeout(chien);
    chien = setTimeout(function () { if (enCours) { envoyer({ type: 'telecharger' }); surveiller(); } }, 20000);
  }
  function occupe() { enCours = true; bTel.disabled = true; barre.hidden = false; surveiller(); }
  function lancer() {
    if (enCours) return;
    palier = -1;
    occupe();
    annoncer('Préparation du téléchargement…');
    if (navigator.storage && navigator.storage.persist) navigator.storage.persist().catch(function () { /* stockage ordinaire */ });
    envoyer({ type: 'telecharger' });
  }
  function pret(deja) {
    enCours = false; clearTimeout(chien);
    barre.hidden = true; bTel.hidden = true;
    annoncer((deja ? 'Déjà enregistré' : 'Prêt') + NB + ': tout l’atlas fonctionne sans réseau.', true);
  }

  bTel.addEventListener('click', lancer);
  window.addEventListener('beforeinstallprompt', function (ev) { ev.preventDefault(); invite = ev; bInst.hidden = false; });
  bInst.addEventListener('click', function () {
    if (!invite) return;
    invite.prompt();
    invite.userChoice.then(function () { invite = null; bInst.hidden = true; }, function () { invite = null; bInst.hidden = true; });
  });
  window.addEventListener('appinstalled', function () { invite = null; bInst.hidden = true; lancer(); });

  navigator.serviceWorker.addEventListener('message', function (ev) {
    var d = ev.data || {};
    if (d.type === 'etat') {
      if (d.complet) pret(true);
      else if (d.enCours) occupe();
    } else if (d.type === 'progression') {
      occupe();
      var pc = d.totalOctets ? Math.round(100 * d.octets / d.totalOctets) : 0;
      barre.value = pc;
      var p = Math.floor(pc / 25);                       // annonce tous les 25 % : les lecteurs d’écran ne sont pas submergés
      if (p !== palier) {
        palier = p;
        annoncer('Téléchargement' + NB + ': ' + mo(d.octets) + NB + 'Mo sur ' + mo(d.totalOctets) + NB + 'Mo (' + pc + NB + '%)');
      }
    } else if (d.type === 'termine') {
      pret(false);
    } else if (d.type === 'erreur') {
      enCours = false; clearTimeout(chien);
      bTel.disabled = false; barre.hidden = true;
      annoncer('Téléchargement incomplet' + NB + ': ' + (d.erreurs > 1 ? d.erreurs + ' fichiers n’ont pas pu être enregistrés'
        : 'un fichier n’a pas pu être enregistré') + '. Réessaie avec une connexion.');
    }
  });
  if (navigator.serviceWorker.startMessages) navigator.serviceWorker.startMessages();
  envoyer({ type: 'etat' });
})();
