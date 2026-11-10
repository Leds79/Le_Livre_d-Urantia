/* Service worker de « Le Livre d’Urantia en images » : lecture hors ligne et installation.
   Écrit par construire_site.py à chaque construction : ne pas le modifier à la main.
   VERSION est l’empreinte du contenu des fichiers listés ; elle change dès que l’un d’eux change. */
'use strict';
const VERSION = 'dc087848e66f';
const PREFIXE = 'atlas-urantia-';
const CACHE = PREFIXE + VERSION;
// tout l’atlas, pour le téléchargement complet : chemin → [octets, empreinte]
const FICHIERS = {
  "index.html": [153738, "2034306adc8c5e44"],
  "nebadon-dans-orvonton.html": [74742, "a55b3fc1e77b85e7"],
  "atlas-3d.html": [2557762, "8d3cf30ec58472ce"],
  "familles-de-personnalites.html": [123980, "5601594ee2dccba3"],
  "concepts-en-schemas.html": [111038, "c4c43cee392299c0"],
  "dieu-et-deite.html": [97005, "9d09cea30c94ddaf"],
  "destinee-humaine.html": [147577, "5f01cc734e74cbf7"],
  "histoire-d-urantia.html": [200100, "8264c336c301cfdb"],
  "rebellion-de-lucifer.html": [154562, "b976bb4b8600c0a9"],
  "vie-de-jesus.html": [138351, "a4cee0da9f9bc673"],
  "bible-et-livre.html": [451284, "656c378886a8d2cb"],
  "pere-fils-esprit.html": [152103, "d4ed7daf3df99b42"],
  "paradis-et-havona.html": [181867, "15fe2ba18fe49475"],
  "etre-supreme.html": [178005, "90f754eb88baf923"],
  "effusions-de-micael.html": [149264, "8bd95bc5d407a16c"],
  "jerusem-et-edentia.html": [272649, "f5e23e1f373d50fc"],
  "les-anges.html": [163721, "d455ecc74fa80dca"],
  "avenir-d-une-planete.html": [171981, "b17dfda4b870a365"],
  "institutions-humaines.html": [201188, "29370cb6d734be39"],
  "evolution-religion.html": [121754, "dcd7784e16357eeb"],
  "religion-vecue.html": [162989, "c2e148efaadba8cb"],
  "melchizedek-et-religions.html": [200284, "717bb2f3e165e7ba"],
  "annees-cachees-de-jesus.html": [210163, "bbba4f0be8df832e"],
  "douze-apotres.html": [146925, "d73169f0ebcb06f5"],
  "enseignements-de-jesus.html": [210351, "d10afcfc64e4410a"],
  "apres-la-pentecote.html": [156610, "b66bfe88ef1da0e8"],
  "histoire-du-livre.html": [137719, "d0a66b1776d6636e"],
  "auteurs-et-chiffres.html": [269863, "1785d98582665e90"],
  "science-et-histoire.html": [514785, "4b5856f4aee957e1"],
  "fascicules.html": [398039, "599134903db27139"],
  "parcours-de-lecture.html": [166804, "cc1fe422ae386397"],
  "glossaire.html": [196144, "2c8ae67da2431785"],
  "index-des-noms.html": [791347, "b02e638ef73a4027"],
  "hors-ligne.html": [8133, "6bc92026df1da2a1"],
  "manifest.webmanifest": [840, "3d1ea890c7f7d469"],
  "assets/refs-urantia.js": [12035, "5d4e6af5f83a9141"],
  "assets/hors-ligne.js": [5241, "d9b44df9a17c61f0"],
  "assets/musique.js": [8725, "036b5f1d0e719ff8"],
  "assets/navigation.js": [45568, "a6983cbd126c1138"],
  "assets/ecouter.js": [19790, "e89bc5bf97adbae3"],
  "assets/glossaire.js": [100934, "ee77095a01f19d87"],
  "assets/quiz.js": [58554, "29f9334aa619a00f"],
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
  "assets/recherche.js": [1593806, "75d3c91cbddf17d9"],
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
