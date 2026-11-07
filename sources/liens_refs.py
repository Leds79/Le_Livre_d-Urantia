"""Références cliquables : chaque « fascicule:section.paragraphe » affiché dans un élément .ref ouvre le passage
exact sur urantia.org (lecteur en ligne de la Fondation Urantia), dans un nouvel onglet.

Adresses : https://www.urantia.org/fr/le-livre-d-urantia/<page du fascicule>#U<fascicule>_<section>_<paragraphe>
(ancres vérifiées le 2026-11-07 : U57_8_1 = page 660, comme notre 57:8.1 ; l'Introduction est le fascicule 0).

Usage :
  python -I liens_refs.py table <table-des-matieres.html> <refs-urantia.js>
      fabrique le script à partir de la table des matières de https://www.urantia.org/fr/le-livre-durantia/lire
  python -I liens_refs.py injecte <refs-urantia.js> page.html [page.html ...]
      insère (ou remplace) le script, en fin de page, dans un bloc <script id="refs-urantia">
"""
import json
import re
import sys

SCRIPT = r'''(function () {
  'use strict';
  // Références cliquables : chaque « fascicule:section.paragraphe » d’un élément .ref ouvre le passage sur urantia.org
  var BASE = 'https://www.urantia.org/fr/le-livre-d-urantia/';
  var S = __TABLE__;   // page de chaque fascicule, de l’Introduction (0) au fascicule 196
  var RX = /(\d{1,3}):(\d{1,2})(?:\.(\d{1,3}))?(?:\s*[–-]\s*\d{1,3})?/g;
  function link(el) {
    var t = el.textContent;
    if (el.getAttribute('data-lk') === t) return;                       // déjà fait, texte inchangé
    if (el.closest('a, button, [role="button"]') || el.querySelector('a')) return;
    var frag = document.createDocumentFragment(), last = 0, n = 0, m;
    RX.lastIndex = 0;
    while ((m = RX.exec(t))) {
      var p = +m[1];
      if (!S[p]) continue;
      if (m.index > last) frag.appendChild(document.createTextNode(t.slice(last, m.index)));
      var a = document.createElement('a');
      a.className = 'ref-lien';
      a.href = BASE + S[p] + '#U' + p + '_' + (+m[2]) + '_' + (m[3] ? +m[3] : 0);
      a.target = '_blank';
      a.rel = 'noopener';
      a.title = 'Lire ' + m[0] + ' sur urantia.org';
      a.textContent = m[0];
      frag.appendChild(a);
      last = m.index + m[0].length;
      n++;
    }
    if (!n) return;
    if (last < t.length) frag.appendChild(document.createTextNode(t.slice(last)));
    el.textContent = '';
    el.appendChild(frag);
    el.setAttribute('data-lk', el.textContent);
  }
  function scan(node) {
    if (!node || node.nodeType !== 1) return;
    if (node.classList.contains('ref')) link(node);
    var l = node.querySelectorAll('.ref');
    for (var i = 0; i < l.length; i++) link(l[i]);
  }
  function refOf(node) { var e = node && (node.nodeType === 1 ? node : node.parentNode); return e && e.closest ? e.closest('.ref') : null; }
  function start() {
    try {
      var st = document.createElement('style');
      st.textContent = 'a.ref-lien{color:inherit;text-decoration:underline dotted;text-decoration-thickness:1px;text-underline-offset:2px;pointer-events:auto}' +
        'a.ref-lien:hover,a.ref-lien:focus-visible{color:var(--gold-ink,inherit);text-decoration-style:solid}';
      document.head.appendChild(st);
      scan(document.body);
      if (!window.MutationObserver) return;
      new MutationObserver(function (list) {
        for (var i = 0; i < list.length; i++) {
          var mu = list[i];
          if (mu.type === 'characterData') { var r = refOf(mu.target); if (r) link(r); continue; }
          for (var j = 0; j < mu.addedNodes.length; j++) {
            var nd = mu.addedNodes[j];
            if (nd.nodeType === 1) scan(nd); else { var r2 = refOf(nd); if (r2) link(r2); }
          }
        }
      }).observe(document.body, { childList: true, subtree: true, characterData: true });
    } catch (e) { /* les références restent en texte simple */ }
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
})();
'''

BLOCK = re.compile(r'\n?<script id="refs-urantia">.*?</script>\n?', re.S)


def table(toc, out):
    t = open(toc, encoding='utf-8').read()
    m = {int(n): 'fascicule-' + n + '-' + s for n, s in re.findall(r'href="/fr/le-livre-d-urantia/fascicule-(\d+)-([a-z0-9-]+)"', t)}
    m[0] = 'introduction'
    missing = [i for i in range(197) if i not in m]
    if missing:
        sys.exit('fascicules introuvables dans la table des matières : %s' % missing)
    js = SCRIPT.replace('__TABLE__', json.dumps([m[i] for i in range(197)], ensure_ascii=True, separators=(',', ':')))
    open(out, 'w', encoding='utf-8', newline='\n').write(js)
    print('script écrit : %s (%d octets)' % (out, len(js.encode('utf-8'))))


def injecte(js_path, pages):
    js = open(js_path, encoding='utf-8').read().strip()
    block = '\n<script id="refs-urantia">\n' + js + '\n</script>\n'
    for p in pages:
        h = open(p, encoding='utf-8').read()
        h = BLOCK.sub('\n', h).rstrip('\n') + '\n' + block
        open(p, 'w', encoding='utf-8', newline='\n').write(h)
        print('références cliquables :', p)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    if len(sys.argv) >= 4 and sys.argv[1] == 'table':
        table(sys.argv[2], sys.argv[3])
    elif len(sys.argv) >= 4 and sys.argv[1] == 'injecte':
        injecte(sys.argv[2], sys.argv[3:])
    else:
        sys.exit(__doc__)
