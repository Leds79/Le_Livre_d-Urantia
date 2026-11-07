"""Convertit les contours Natural Earth (domaine public) en tableaux compacts
pour la texture d'Urantia : terres (1:50 m), lacs et fleuves (1:110 m).
Usage : python -I geo.py <dossier ne> <sortie.json>
Format : anneaux en dixièmes de degré, codés en différences (lon, lat, dlon, dlat, ...)."""
import json
import sys
from pathlib import Path

NE, OUT = Path(sys.argv[1]), Path(sys.argv[2])


def dp(pts, tol):
    """Douglas-Peucker itératif."""
    if len(pts) < 4:
        return pts
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        a, b = stack.pop()
        ax, ay = pts[a]
        bx, by = pts[b]
        dx, dy = bx - ax, by - ay
        l2 = dx * dx + dy * dy
        best, bi = -1.0, -1
        for i in range(a + 1, b):
            px, py = pts[i]
            if l2 == 0:
                d = (px - ax) ** 2 + (py - ay) ** 2
            else:
                t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / l2))
                d = (px - ax - t * dx) ** 2 + (py - ay - t * dy) ** 2
            if d > best:
                best, bi = d, i
        if bi > 0 and best > tol * tol:
            keep[bi] = True
            stack.append((a, bi))
            stack.append((bi, b))
    return [p for p, k in zip(pts, keep) if k]


def area(r):
    s = 0.0
    for i in range(len(r)):
        x1, y1 = r[i]
        x2, y2 = r[(i + 1) % len(r)]
        s += x1 * y2 - x2 * y1
    return abs(s) / 2


def enc(r):
    out, px, py = [], 0, 0
    for x, y in r:
        ix, iy = round(x * 10), round(y * 10)
        if out and ix == px and iy == py:
            continue
        out += [ix - px, iy - py]
        px, py = ix, iy
    return out


def polys(path, tol, min_area):
    res = []
    for f in json.loads(path.read_text(encoding='utf-8'))['features']:
        g = f['geometry']
        plist = [g['coordinates']] if g['type'] == 'Polygon' else g['coordinates']
        for p in plist:
            rings = []
            for k, ring in enumerate(p):
                s = dp([tuple(c[:2]) for c in ring], tol)
                if len(s) >= 4 and area(s) >= (min_area if k == 0 else min_area * 2):
                    rings.append(enc(s))
                elif k == 0:
                    break
            if rings:
                res.append(rings)
    return res


def lines(path, tol, only=None):
    res, names = [], []
    for f in json.loads(path.read_text(encoding='utf-8'))['features']:
        if only and (f['properties'].get('name') or '') not in only:
            continue
        g = f['geometry']
        llist = [g['coordinates']] if g['type'] == 'LineString' else g['coordinates']
        for ln in llist:
            s = dp([tuple(c[:2]) for c in ln], tol)
            if len(s) >= 2:
                res.append(enc(s))
        names.append(f['properties'].get('name') or f['properties'].get('NAME'))
    return res, names


land = polys(NE / 'ne_50m_land.geojson', 0.06, 0.25)
lakes = polys(NE / 'ne_110m_lakes.geojson', 0.06, 0.15)
rivers, rnames = lines(NE / 'ne_110m_rivers_lake_centerlines.geojson', 0.08)
r50, n50 = lines(NE / 'ne_50m_rivers_lake_centerlines.geojson', 0.04,
                 {'Tigris', 'Euphrates', 'Jordan', 'Indus', 'Ganges', 'Volga', 'Danube', 'Niger', 'Huang', 'Amur', 'Yenisey'})
rivers += r50
rnames += n50
data = {'src': 'Natural Earth (domaine public)', 'land': land, 'lakes': lakes, 'rivers': rivers}
txt = json.dumps(data, separators=(',', ':'))
OUT.write_text(txt, encoding='utf-8')
print('terres', len(land), 'lacs', len(lakes), 'fleuves', len(rivers), '·', round(len(txt) / 1024), 'Ko')
print('fleuves :', ', '.join(sorted({n for n in rnames if n})))
