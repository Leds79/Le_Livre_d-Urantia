/* Service worker de « Le Livre d’Urantia en images » : lecture hors ligne et installation.
   Écrit par construire_site.py à chaque construction : ne pas le modifier à la main.
   VERSION est l’empreinte du contenu des fichiers listés ; elle change dès que l’un d’eux change. */
'use strict';
const VERSION = '84c39fb05175';
const PREFIXE = 'atlas-urantia-';
const CACHE = PREFIXE + VERSION;
// tout l’atlas, pour le téléchargement complet : chemin → [octets, empreinte]
const FICHIERS = {
  "index.html": [153720, "f85af26b618147d0"],
  "nebadon-dans-orvonton.html": [74734, "fda9d76314098add"],
  "atlas-3d.html": [2557806, "580d470f46ec623d"],
  "familles-de-personnalites.html": [123980, "5601594ee2dccba3"],
  "concepts-en-schemas.html": [111038, "c4c43cee392299c0"],
  "dieu-et-deite.html": [97005, "9d09cea30c94ddaf"],
  "destinee-humaine.html": [147861, "e46052155736c1d8"],
  "histoire-d-urantia.html": [200306, "d928003e298a43af"],
  "rebellion-de-lucifer.html": [154797, "78c9db11dd29900f"],
  "vie-de-jesus.html": [138380, "f526c785fc8263b1"],
  "bible-et-livre.html": [451208, "2661990045aa8274"],
  "pere-fils-esprit.html": [152140, "f4566e9d21da1f83"],
  "paradis-et-havona.html": [181976, "645eced0d974e7b9"],
  "etre-supreme.html": [178090, "66f2dd78868c465c"],
  "effusions-de-micael.html": [149384, "e554a1c834deb4b2"],
  "jerusem-et-edentia.html": [272785, "082a2652dc5ef5a7"],
  "les-anges.html": [164001, "a57604f0f369c347"],
  "avenir-d-une-planete.html": [172032, "49d8c717db542dfa"],
  "institutions-humaines.html": [201268, "70c3e2c65a23fd1d"],
  "evolution-religion.html": [121817, "fa4820ed6bce0aaf"],
  "religion-vecue.html": [162989, "c2e148efaadba8cb"],
  "melchizedek-et-religions.html": [200426, "fcd4bb3012d63e07"],
  "annees-cachees-de-jesus.html": [210215, "37ac0198aad273b3"],
  "douze-apotres.html": [146974, "a08fe75bde6f5157"],
  "enseignements-de-jesus.html": [210397, "465c339f4f171772"],
  "apres-la-pentecote.html": [156610, "b66bfe88ef1da0e8"],
  "histoire-du-livre.html": [137959, "8b3517279179804b"],
  "auteurs-et-chiffres.html": [269891, "ff4e517c9c9aa91a"],
  "science-et-histoire.html": [514776, "f27ee1b39a9a677f"],
  "fascicules.html": [398039, "599134903db27139"],
  "parcours-de-lecture.html": [166804, "cc1fe422ae386397"],
  "glossaire.html": [198986, "acb6a393a054ba0b"],
  "index-des-noms.html": [791347, "b02e638ef73a4027"],
  "hors-ligne.html": [8133, "6bc92026df1da2a1"],
  "manifest.webmanifest": [840, "3d1ea890c7f7d469"],
  "assets/refs-urantia.js": [12035, "5d4e6af5f83a9141"],
  "assets/hors-ligne.js": [5241, "d9b44df9a17c61f0"],
  "assets/musique.js": [8725, "036b5f1d0e719ff8"],
  "assets/navigation.js": [45568, "a6983cbd126c1138"],
  "assets/ecouter.js": [19790, "e89bc5bf97adbae3"],
  "assets/glossaire.js": [102505, "195b736752a827c3"],
  "assets/quiz.js": [58589, "28ba0e3645d69457"],
  "assets/favicon.svg": [440, "272fe83973cfb82d"],
  "assets/apple-touch-icon.png": [8093, "bb9210212b2e3f22"],
  "assets/icone-192.png": [9405, "208d49b2cf6fc956"],
  "assets/icone-512.png": [27264, "b7cf8acbaf882dda"],
  "assets/icone-512-maskable.png": [18966, "64bb37960a456493"],
  "assets/fonts/alegreya-sans-400-italic.woff2": [24380, "5dd7c3e61cb1b653"],
  "assets/fonts/alegreya-sans-400.woff2": [23708, "b2a5a35a2563a2f9"],
  "assets/fonts/alegreya-sans-500.woff2": [23928, "55b61d22cc7afd0b"],
  "assets/fonts/alegreya-sans-700.woff2": [23976, "5acd19a588614d23"],
  "assets/fonts/cormorant-garamond-500-600-italic.woff2": [39260, "6f2f5c3b1abc3d0b"],
  "assets/fonts/cormorant-garamond-500-700.woff2": [37640, "d80df8ff5aecd299"],
  "assets/fonts/fonts.css": [3095, "2bc36a19d6658921"],
  "assets/fonts/ibm-plex-mono-400.woff2": [14708, "08949f728dc52d52"],
  "assets/fonts/ibm-plex-mono-500.woff2": [14888, "01d285447409c8a5"],
  "assets/recherche.js": [1594600, "9eeb09cb97ac995d"],
  "assets/lib/three.min.js": [603445, "9274bbcec8d96168"],
  "assets/lib/OrbitControls.js": [26375, "02bb4ade710f3e60"]
};
// enregistrés dès l’installation : accueil, page hors ligne, manifeste, scripts communs, icônes, polices
const NOYAU = ["index.html", "hors-ligne.html", "manifest.webmanifest", "assets/refs-urantia.js", "assets/hors-ligne.js", "assets/musique.js", "assets/navigation.js", "assets/ecouter.js", "assets/glossaire.js", "assets/quiz.js", "assets/favicon.svg", "assets/apple-touch-icon.png", "assets/icone-192.png", "assets/icone-512.png", "assets/icone-512-maskable.png", "assets/fonts/alegreya-sans-400-italic.woff2", "assets/fonts/alegreya-sans-400.woff2", "assets/fonts/alegreya-sans-500.woff2", "assets/fonts/alegreya-sans-700.woff2", "assets/fonts/cormorant-garamond-500-600-italic.woff2", "assets/fonts/cormorant-garamond-500-700.woff2", "assets/fonts/fonts.css", "assets/fonts/ibm-plex-mono-400.woff2", "assets/fonts/ibm-plex-mono-500.woff2"];
const HORS_LIGNE = 'hors-ligne.html';
const DELAI_RESEAU = 3000;                 // navigations : au-delà, la copie enregistrée est servie
const PORTEE = new URL('./', self.location.href).href;
const abs = (p) => new URL(p, PORTEE).href;
const EMPREINTES = abs('__atlas__/empreintes.json');   // entrées internes du cache
const COMPLET = abs('__atlas__/complet');
const LISTE = Object.keys(FICHIERS);
const TOTAL = LISTE.reduce((s, p) => s + FICHIERS[p][0], 0);
let enCours = null;

// adresse normalisée : sans requête ni ancre ; « dossier/ » devient « dossier/index.html »
function cle(u) {
  const x = new URL(u);
  x.hash = '';
  x.search = '';
  if (x.pathname.endsWith('/')) x.pathname += 'index.html';
  return x.href;
}
async function recuperer(p) {              // revalidé auprès du serveur : jamais une copie périmée du cache HTTP
  const r = await fetch(abs(p), { cache: 'no-cache' });
  if (!r.ok) throw new Error(p + ' : ' + r.status);
  return r;
}
async function present(cache, p) { return !!(await cache.match(abs(p))); }

self.addEventListener('install', (e) => {
  self.skipWaiting();
  e.waitUntil((async () => {
    const cache = await caches.open(CACHE);
    await Promise.all(NOYAU.map(async (p) => { await cache.put(abs(p), await recuperer(p)); }));
    // version précédente : ce qui y était enregistré est repris, copié s’il n’a pas changé, téléchargé de nouveau sinon
    for (const nom of (await caches.keys()).filter((k) => k.startsWith(PREFIXE) && k !== CACHE)) {
      const ancien = await caches.open(nom);
      let emp = {};
      try { const r = await ancien.match(EMPREINTES); if (r) emp = await r.json(); } catch (err) { /* tout est retéléchargé */ }
      for (const p of LISTE) {
        if (await present(cache, p)) continue;
        const r = await ancien.match(abs(p));
        if (!r) continue;
        try { await cache.put(abs(p), emp[p] === FICHIERS[p][1] ? r : await recuperer(p)); } catch (err) { /* repris au prochain téléchargement */ }
      }
    }
    await cache.put(EMPREINTES, new Response(JSON.stringify(Object.fromEntries(LISTE.map((p) => [p, FICHIERS[p][1]])))));
    let complet = true;
    for (const p of LISTE) if (!(await present(cache, p))) { complet = false; break; }
    if (complet) await cache.put(COMPLET, new Response(VERSION));
  })());
});

self.addEventListener('activate', (e) => {
  e.waitUntil((async () => {
    const vieux = (await caches.keys()).filter((k) => k.startsWith(PREFIXE) && k !== CACHE);
    await Promise.all(vieux.map((k) => caches.delete(k)));
    await self.clients.claim();
  })());
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;
  if (req.cache === 'only-if-cached' && req.mode !== 'same-origin') return;
  const u = new URL(req.url);
  if (u.origin !== self.location.origin || !req.url.startsWith(PORTEE)) return;   // autres sites (urantia.org…) : jamais en cache
  e.respondWith(req.mode === 'navigate' ? navigation(e) : ressource(e));
});

// navigations : le réseau d’abord (3 s au plus), puis la copie enregistrée, puis la page hors ligne
function navigation(e) {
  const k = cle(e.request.url);
  const reseau = fetch(e.request).then((r) => {
    if (r.ok && r.type === 'basic') {
      const copie = r.clone();
      e.waitUntil(caches.open(CACHE).then((c) => c.put(k, copie)).catch(() => {}));
    }
    return r;
  });
  e.waitUntil(reseau.then(() => {}, () => {}));
  return (async () => {
    try {
      return await Promise.race([reseau, new Promise((_, non) => setTimeout(() => non(new Error('délai')), DELAI_RESEAU))]);
    } catch (err) {
      const copie = await caches.match(k, { cacheName: CACHE });
      if (copie) return copie;
      try { return await reseau; } catch (err2) { return horsLigne(); }
    }
  })();
}

// autres ressources du site : la copie enregistrée, sinon le réseau (et la réponse est enregistrée)
async function ressource(e) {
  const k = cle(e.request.url);
  const cache = await caches.open(CACHE);
  const copie = await cache.match(k);
  if (copie) return copie;
  const r = await fetch(e.request);
  if (r.ok && r.type === 'basic') e.waitUntil(cache.put(k, r.clone()).catch(() => {}));
  return r;
}

async function horsLigne() {
  const r = await caches.match(abs(HORS_LIGNE), { cacheName: CACHE });
  const t = r ? await r.text() : '<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>Hors ligne</title></head>'
    + '<body><p>Cette page n’est pas encore enregistrée pour la lecture hors ligne.</p></body></html>';
  return new Response(t.replace('<head>', '<head><base href="' + PORTEE + '">'), { headers: { 'Content-Type': 'text/html; charset=utf-8' } });
}

// messages de la page : état de l’enregistrement, téléchargement complet (avec progression)
self.addEventListener('message', (e) => {
  const d = e.data || {};
  if (d.type === 'etat') {
    e.waitUntil(etat().then((s) => { if (e.source) e.source.postMessage(s); }));
  } else if (d.type === 'telecharger') {
    if (!enCours) enCours = telecharger().finally(() => { enCours = null; });
    e.waitUntil(enCours);
  }
});
async function diffuser(m) {
  for (const c of await self.clients.matchAll({ type: 'window', includeUncontrolled: true })) c.postMessage(m);
}
async function etat() {
  const cache = await caches.open(CACHE);
  let n = 0, octets = 0;
  for (const p of LISTE) if (await present(cache, p)) { n++; octets += FICHIERS[p][0]; }
  return { type: 'etat', version: VERSION, enregistres: n, total: LISTE.length, octets, totalOctets: TOTAL,
    complet: n === LISTE.length, enCours: !!enCours };
}
async function telecharger() {
  const cache = await caches.open(CACHE);
  const manquants = [];
  let fait = 0, octets = 0, erreurs = 0;
  for (const p of LISTE) {
    if (await present(cache, p)) { fait++; octets += FICHIERS[p][0]; } else manquants.push(p);
  }
  const point = (type) => diffuser({ type, fait, total: LISTE.length, octets, totalOctets: TOTAL, erreurs, version: VERSION });
  await point('progression');
  let i = 0;
  const ouvrier = async () => {
    while (i < manquants.length) {
      const p = manquants[i++];
      try { await cache.put(abs(p), await recuperer(p)); } catch (err) { erreurs++; }
      fait++;
      octets += FICHIERS[p][0];
      await point('progression');
    }
  };
  await Promise.all([ouvrier(), ouvrier(), ouvrier()]);
  if (!erreurs) await cache.put(COMPLET, new Response(VERSION));
  await point(erreurs ? 'erreur' : 'termine');
}
