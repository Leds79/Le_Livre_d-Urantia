/* Service worker de « Le Livre d’Urantia en images » : lecture hors ligne et installation.
   Écrit par construire_site.py à chaque construction : ne pas le modifier à la main.
   VERSION est l’empreinte du contenu des fichiers listés ; elle change dès que l’un d’eux change. */
'use strict';
const VERSION = '0aa2d1c27d2e';
const PREFIXE = 'atlas-urantia-';
const CACHE = PREFIXE + VERSION;
// tout l’atlas, pour le téléchargement complet : chemin → [octets, empreinte]
const FICHIERS = {
  "index.html": [151389, "04382f4165a5f279"],
  "nebadon-dans-orvonton.html": [73763, "7644473b7cd4e66e"],
  "atlas-3d.html": [2553868, "6087a4f15f4f2d6e"],
  "familles-de-personnalites.html": [123410, "62441591423176f9"],
  "concepts-en-schemas.html": [110540, "a9f987a1d81e4734"],
  "dieu-et-deite.html": [96576, "5c04e67a98561679"],
  "destinee-humaine.html": [147465, "255c8ee81998d2c5"],
  "histoire-d-urantia.html": [199770, "abd025ba8a163b49"],
  "rebellion-de-lucifer.html": [154337, "702f2799d2c58e69"],
  "vie-de-jesus.html": [135858, "174bd03b42b8c982"],
  "bible-et-livre.html": [450751, "b8e871adc308b9df"],
  "pere-fils-esprit.html": [151731, "0deb9523fa16d1ce"],
  "paradis-et-havona.html": [181568, "a8ae198224970cac"],
  "etre-supreme.html": [177682, "b2d71ae9245573c5"],
  "effusions-de-micael.html": [148933, "4a2f4e07f6c708b1"],
  "jerusem-et-edentia.html": [272330, "c9395276f44c7e41"],
  "les-anges.html": [163594, "c9b573f2f00ef13e"],
  "avenir-d-une-planete.html": [171623, "e84d3f1db153c66b"],
  "institutions-humaines.html": [200817, "0580ebfe43b98fd9"],
  "evolution-religion.html": [121381, "81a3f425204631bc"],
  "religion-vecue.html": [162548, "d294af37ee25e98d"],
  "melchizedek-et-religions.html": [199695, "347a7bf1e0c5a3ed"],
  "annees-cachees-de-jesus.html": [209709, "dfa126e94eecc9a3"],
  "douze-apotres.html": [146510, "0c564ba1011171b3"],
  "enseignements-de-jesus.html": [209963, "9b70720babb15c6c"],
  "apres-la-pentecote.html": [156188, "6793e51aa1533bea"],
  "histoire-du-livre.html": [137495, "826775cc7c66a7ea"],
  "auteurs-et-chiffres.html": [269282, "c9720d7f71a2c0fc"],
  "science-et-histoire.html": [514087, "193d497fc9b5a016"],
  "fascicules.html": [397636, "0131db6d42430077"],
  "parcours-de-lecture.html": [166273, "98336f6aae4f9032"],
  "glossaire.html": [198497, "02718f8f87bfc986"],
  "hors-ligne.html": [8034, "0b63c01870a12a34"],
  "manifest.webmanifest": [840, "3d1ea890c7f7d469"],
  "assets/refs-urantia.js": [12035, "5d4e6af5f83a9141"],
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
  "assets/recherche.js": [1398625, "1f17e12a9edad7d5"],
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
