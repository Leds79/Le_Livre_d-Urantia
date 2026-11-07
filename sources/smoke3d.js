// Test d'exécution de la vue 3D hors navigateur : faux DOM, vrai Three.js r128, rendu WebGL simulé.
// Usage : node smoke3d.js page.html three.min.js OrbitControls.js
const fs = require('fs');
const vm = require('vm');
const [page, threePath, orbitPath] = process.argv.slice(2);
const html = fs.readFileSync(page, 'utf8');
const inline = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map((m) => m[1]);
const refs = (html.match(/<script id="refs-urantia">([\s\S]*?)<\/script>/) || [])[1];   // références cliquables (urantia.org)
const errors = [];

const grad = { addColorStop() {} };
const ctx2d = new Proxy({}, {
  get(t, k) {
    if (k in t) return t[k];
    if (k === 'createLinearGradient' || k === 'createRadialGradient') return () => grad;
    if (k === 'getImageData') return () => ({ data: new Uint8ClampedArray(4) });
    return () => {};
  },
  set(t, k, v) { t[k] = v; return true; }
});
const ids = {};
function mk(tag) {
  const e = {
    tagName: tag, style: {}, dataset: {}, hidden: false, children: [], textContent: '', value: '0', max: '0', title: '', checked: true,
    clientWidth: 1200, clientHeight: 800, width: 300, height: 150, parent: null,
    classList: { add() {}, remove() {}, toggle() {}, contains() { return false; } },
    _l: {},
    addEventListener(t, f) { (this._l[t] = this._l[t] || []).push(f); },
    removeEventListener() {}, setAttribute(k, v) { this['_a_' + k] = v; }, getAttribute(k) { return this['_a_' + k]; }, removeAttribute() {},
    appendChild(c) { this.children.push(c); return c; }, querySelectorAll() { return []; }, querySelector() { return mk('div'); },
    getBoundingClientRect() { return { left: 0, top: 0, width: 1200, height: 800 }; },
    getContext() { return ctx2d; }, setPointerCapture() {}, releasePointerCapture() {}, focus() {},
    click() { (this._l.click || []).forEach((f) => f({ preventDefault() {}, stopPropagation() {}, target: this })); }
  };
  let ih = '';
  Object.defineProperty(e, 'innerHTML', { get() { return ih; }, set(v) { ih = String(v); } });
  return e;
}
const document = {
  getElementById(id) { return ids[id] || (ids[id] = Object.assign(mk('div'), { id })); },
  createElement(tag) { return mk(tag); },
  querySelector(s) { return ids['q:' + s] || (ids['q:' + s] = mk('div')); },
  querySelectorAll() { return []; },
  addEventListener(t, f) { (document._l[t] = document._l[t] || []).push(f); }, _l: {},
  removeEventListener() {},
  head: mk('head'), body: mk('body'), readyState: 'complete',
  createDocumentFragment() { return mk('fragment'); }, createTextNode(t) { return { nodeType: 3, textContent: t }; }
};
Object.values(ids).forEach(() => {});
const rafs = [];
const ctx = {
  console, document, Math, Date, JSON, Proxy, Uint8ClampedArray, Float32Array, Uint16Array, Uint32Array, Int32Array, Uint8Array, Int8Array, Int16Array, Float64Array, ArrayBuffer, DataView, Map, Set, WeakMap, Symbol, Promise, Number, String, Boolean, Object, Array, Error, TypeError, RangeError, parseFloat, parseInt, isNaN, isFinite,
  performance: { now: () => Date.now() },
  setTimeout, clearTimeout, setInterval, clearInterval,
  requestAnimationFrame: (f) => { rafs.push(f); return rafs.length; },
  cancelAnimationFrame() {},
  innerWidth: 1200, innerHeight: 800, devicePixelRatio: 1,
  matchMedia: () => ({ matches: false, addEventListener() {} }),
  addEventListener() {}, removeEventListener() {},
  ResizeObserver: class { observe() {} },
  navigator: { userAgent: 'node' }, self: null, location: { hash: process.env.HASH || '' }
};
ctx.window = ctx; ctx.self = ctx; ctx.globalThis = ctx;
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(threePath, 'utf8'), ctx, { filename: 'three.min.js' });
const T = ctx.THREE;
T.WebGLRenderer = function () { return { setPixelRatio() {}, setClearColor() {}, setSize() {}, render() {}, getPixelRatio() { return 1; }, capabilities: { getMaxAnisotropy() { return 8; } }, localClippingEnabled: false }; };
vm.runInContext(fs.readFileSync(orbitPath, 'utf8'), ctx, { filename: 'OrbitControls.js' });
const canvas = document.getElementById('c');
canvas.ownerDocument = document;
try { vm.runInContext(inline[inline.length - 1], ctx, { filename: 'page.js' }); } catch (e) { errors.push('init: ' + (e.stack || e)); }
if (refs) { try { vm.runInContext(refs, ctx, { filename: 'refs-urantia.js' }); } catch (e) { errors.push('refs: ' + (e.stack || e)); } }
console.log('bloc refs-urantia :', refs ? 'exécuté' : 'absent');

let t = Date.now();
function frames(n) { for (let i = 0; i < n; i++) { const f = rafs.shift(); if (!f) return; t += 16; try { f(t); } catch (e) { errors.push('frame: ' + (e.stack || e)); return; } } }
const fire = (el, type, ev) => (el._l[type] || []).forEach((f) => { try { f(Object.assign({ preventDefault() {}, stopPropagation() {}, target: el }, ev || {})); } catch (e) { errors.push(type + ' ' + (el.id || '') + ': ' + (e.stack || e)); } });
frames(5);
// frise : ouvrir, parcourir tous les évènements, lecture, fermer
const tl = document.getElementById('t-time'), tlR = document.getElementById('tl-r');
fire(tl, 'click');
frames(3);
const n = Number(tlR.max) + 1;
for (let i = 0; i < n; i++) { tlR.value = String(i); fire(tlR, 'input'); fire(tlR, 'change'); frames(4); }
console.log('évènements parcourus :', n, '· carte :', document.getElementById('tl-t').textContent, '·', document.getElementById('tl-d').innerHTML);
fire(document.getElementById('tl-prev'), 'click'); frames(2);
fire(document.getElementById('tl-strip'), 'click', { clientX: 300, clientY: 10 }); frames(2);
fire(document.getElementById('tl-play'), 'click'); frames(2); fire(document.getElementById('tl-play'), 'click');
fire(document.getElementById('t-gov'), 'click'); frames(2);
fire(document.getElementById('t-deite'), 'click'); frames(2);
// niveaux : parcourir l'échelle avec la frise ouverte puis fermée
for (const u of [0, 1, 2, 3, 4, 7, 8, 9, 11]) { fire(document.getElementById('zoom'), 'input'); document.getElementById('zoom').value = String(u); fire(document.getElementById('zoom'), 'input'); frames(40); }
fire(tl, 'click'); frames(3);
// carrière ascendante : ouvrir, parcourir les étapes, lecture, fermer
const ta = document.getElementById('t-asc');
fire(ta, 'click'); frames(3);
for (let i = 0; i < 15; i++) { fire(document.getElementById('asc-next'), 'click'); frames(40); }
console.log('carrière :', document.getElementById('asc-meta').textContent, '·', document.getElementById('asc-t').textContent);
fire(document.getElementById('asc-prev'), 'click'); frames(5);
fire(document.getElementById('asc-play'), 'click'); frames(2); fire(document.getElementById('asc-play'), 'click');
fire(tl, 'click'); frames(3); fire(tl, 'click'); frames(3);
fire(ta, 'click'); frames(3);
// clic simple sur un point : déclenché après 240 ms
fire(canvas, 'pointerdown', { clientX: 600, clientY: 400, button: 0, pointerType: 'mouse', pointerId: 1 });
fire(canvas, 'pointerup', { clientX: 600, clientY: 400, button: 0, pointerType: 'mouse', pointerId: 1 });
fire(document.getElementById('t-coupe'), 'click'); frames(30); fire(document.getElementById('t-coupe'), 'click');
setTimeout(() => {
  frames(30);
  const lbl = document.getElementById('labels').children.filter((c) => c._l.click);
  console.log('étiquettes cliquables :', lbl.length, 'sur', document.getElementById('labels').children.length);
  if (lbl[0]) { fire(lbl[0], 'click'); frames(10); }
  console.log(errors.length ? 'ERREURS :\n' + errors.join('\n') : 'AUCUNE ERREUR D’EXÉCUTION');
  process.exit(errors.length ? 1 : 0);
}, 400);
