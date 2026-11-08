/* Service worker de « Le Livre d’Urantia en images » : lecture hors ligne et installation.
   Écrit par construire_site.py à chaque construction : ne pas le modifier à la main.
   VERSION est l’empreinte du contenu des fichiers listés ; elle change dès que l’un d’eux change. */
'use strict';
const VERSION = 'bb870d50b275';
const PREFIXE = 'atlas-urantia-';
const CACHE = PREFIXE + VERSION;
// tout l’atlas, pour le téléchargement complet : chemin → [octets, empreinte]
const FICHIERS = {
  "index.html": [133042, "f961cc5ea59476dd"],
  "nebadon-dans-orvonton.html": [72922, "dafcdc6b58fd037e"],
  "atlas-3d.html": [2516689, "4dab2a2d4b0081f1"],
  "familles-de-personnalites.html": [122569, "265c67fdba5d4fac"],
  "concepts-en-schemas.html": [109699, "6eda1a17a6eb1f69"],
  "dieu-et-deite.html": [95735, "6f9cf03352446f51"],
  "destinee-humaine.html": [137359, "1b5139dd24ea190f"],
  "histoire-d-urantia.html": [184997, "83472edc882a6e0c"],
  "rebellion-de-lucifer.html": [153496, "5a1920223d33296d"],
  "vie-de-jesus.html": [121017, "8b9f9c4699758d8e"],
  "bible-et-livre.html": [449884, "2bb9f4a42afe62b8"],
  "paradis-et-havona.html": [169226, "e76bfc01eca779d3"],
  "etre-supreme.html": [176818, "0041d6eae392a156"],
  "effusions-de-micael.html": [147911, "f7ffaa569eb3c270"],
  "jerusem-et-edentia.html": [271429, "c19e4d97887f0416"],
  "les-anges.html": [162735, "336fd77914e269fb"],
  "avenir-d-une-planete.html": [170766, "880de8a85fd179f5"],
  "institutions-humaines.html": [199955, "ccc0868e20dc870d"],
  "evolution-religion.html": [120540, "056358fc048210e8"],
  "melchizedek-et-religions.html": [198813, "6eefb76cda503b21"],
  "douze-apotres.html": [144658, "4ac25b57543ddfce"],
  "enseignements-de-jesus.html": [172806, "742fa2cef5c91d72"],
  "histoire-du-livre.html": [136445, "a8c488ff06614088"],
  "auteurs-et-chiffres.html": [268365, "c0d88027839ab607"],
  "fascicules.html": [380181, "1c6e1e49bf9d436c"],
  "parcours-de-lecture.html": [164705, "074134e3b0c742e6"],
  "glossaire.html": [197656, "35d043eea1d19b48"],
  "hors-ligne.html": [7475, "2196788085a5aa46"],
  "manifest.webmanifest": [840, "3d1ea890c7f7d469"],
  "assets/refs-urantia.js": [11858, "1e90f999f912766f"],
  "assets/hors-ligne.js": [5241, "d9b44df9a17c61f0"],
  "assets/musique.js": [8725, "036b5f1d0e719ff8"],
  "assets/navigation.js": [44949, "df3429012e63a6f3"],
  "assets/ecouter.js": [19700, "f6926356d7817b21"],
  "assets/glossaire.js": [101975, "6010fd2a8185216c"],
  "assets/quiz.js": [58585, "ecc6029cadf6aed1"],
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
  "assets/recherche.js": [979105, "7626e9c6b50ea4c4"],
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
