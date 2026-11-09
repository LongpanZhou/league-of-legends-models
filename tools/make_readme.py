"""Writes README.md from models.json: a picture table for every category of model.

    python tools/make_readme.py

Run it from the root of the repository after the pack has been rebuilt (see scripts/build-model-pack.mjs in
the website's repository).
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COLUMNS = 6
PICTURE = 104          # pixels wide in the README
FOLD_ABOVE = 40        # categories with more models than this start folded

models = json.load(open(os.path.join(ROOT, 'models.json'), encoding='utf-8'))['models']

EPIC = re.compile(r'^(atakhan|baron_nashor|dragon.*|rift_herald|scuttle_crab|voidgrubs|voidmite)$')
JUNGLE = re.compile(r'^(blue_sentinel|red_brambleback|gromp.*|krug.*|murk_wolf.*|raptor.*)$')
WARDS = re.compile(r'(ward|trinket|gravestone)')

# (anchor, emoji, title, blurb, test)
CATEGORIES = [
    ('champions', '🧙', 'Champions', 'Every champion, in the models folder `models/champions/`.', lambda p, n: p.startswith('champions/')),
    ('epic', '🐉', 'Epic monsters', 'Baron, the elemental drakes, Herald, Atakhan, the void creatures and the scuttle crab.', lambda p, n: '/' not in p and bool(EPIC.match(n))),
    ('jungle', '🌲', 'Jungle monsters', 'The camps: buffs, gromp, krugs, wolves and raptors, with their small versions.', lambda p, n: '/' not in p and bool(JUNGLE.match(n))),
    ('minions', '⚔️', 'Minions', 'Melee, ranged, siege and super minions, for both sides.', lambda p, n: n.startswith('minion')),
    ('nexuses', '💎', 'Nexuses', 'Nexuses and inhibitors, in the different looks the game has had.', lambda p, n: n.startswith('nexus')),
    ('turrets', '🗼', 'Turrets', 'Turrets and towers, in the different looks the game has had.', lambda p, n: n.startswith('turret')),
    ('wards', '👁️', 'Wards and trinkets', 'Wards, trinkets and the ward crabs.', lambda p, n: bool(WARDS.search(n)) and '/' not in p),
]


def name_of(path):
    return re.sub(r'\.glb$', '', path.split('/')[-1])


def natural(s):
    return [int(t) if t.isdigit() else t for t in re.split(r'(\d+)', s)]


groups = {key: [] for key, *_ in CATEGORIES}
unplaced = []
for m in models:
    n = name_of(m['path'])
    for key, _e, _t, _b, test in CATEGORIES:
        if test(m['path'], n):
            groups[key].append(m)
            break
    else:
        unplaced.append(m['path'])
for items in groups.values():
    items.sort(key=lambda m: natural(name_of(m['path'])))

total_mb = sum(m['size'] for m in models) / 1e6
map_mb = os.path.getsize(os.path.join(ROOT, 'map', 'summoners-rift.glb')) / 1e6


def table(items):
    rows = []
    for i in range(0, len(items), COLUMNS):
        cells = []
        for m in items[i:i + COLUMNS]:
            n = name_of(m['path'])
            img = f'<img src="{m["thumb"]}" width="{PICTURE}" alt="{n}">' if m.get('thumb') else n
            cells.append(f'<td align="center" valign="top" width="{100 // COLUMNS}%"><a href="models/{m["path"]}">{img}<br><sub><b>{n}</b></sub></a></td>')
        cells += ['<td></td>'] * (COLUMNS - len(cells))
        rows.append('<tr>' + ''.join(cells) + '</tr>')
    return '<table>\n' + '\n'.join(rows) + '\n</table>'


out = []
out.append(f'''<div align="center">

# League of Legends models

**{len(models) + 1} 3D models** of the Summoner's Rift map, its structures, monsters and minions, and every champion,
in glTF binary (`.glb`) with a picture of each.

![models](https://img.shields.io/badge/models-{len(models) + 1}-C8AA6E?style=for-the-badge&labelColor=010A13)
![champions](https://img.shields.io/badge/champions-{len(groups['champions'])}-0AC8FF?style=for-the-badge&labelColor=010A13)
![size](https://img.shields.io/badge/size-{total_mb / 1000 + map_mb / 1000:.1f}%20GB-C8AA6E?style=for-the-badge&labelColor=010A13)
![format](https://img.shields.io/badge/format-glTF%20(.glb)-0AC8FF?style=for-the-badge&labelColor=010A13)

Click a picture to open its model, then **Download raw file**.

Used by [longpanzhou.github.io](https://longpanzhou.github.io), whose layout editor downloads a model from here when it is dropped on the map.

</div>

---
''')

out.append('## Contents\n')
out.append('| | Category | Models |\n|---|---|---:|')
out.append(f'| 🗺️ | [Map](#map) | 1 |')
for key, emoji, title, _b, _t in CATEGORIES:
    out.append(f'| {emoji} | [{title}](#{key}) | {len(groups[key])} |')
out.append('')

out.append(f'''<a id="map"></a>
## 🗺️ Map

<p align="center"><a href="map/summoners-rift.glb"><img src="thumbs/map.png" width="640" alt="Summoner's Rift"></a></p>

<p align="center"><a href="map/summoners-rift.glb"><b>summoners-rift.glb</b></a> · {map_mb:.0f} MB · the optimised map the website uses</p>
''')

for key, emoji, title, blurb, _t in CATEGORIES:
    items = groups[key]
    if not items:
        continue
    out.append(f'<a id="{key}"></a>\n## {emoji} {title}\n')
    out.append(f'{blurb}\n')
    if len(items) > FOLD_ABOVE:
        out.append(f'<details>\n<summary><b>Show the {len(items)} {title.lower()}</b></summary>\n\n{table(items)}\n\n</details>\n')
    else:
        out.append(table(items) + '\n')

out.append('''---

<sub>League of Legends, its champions, monsters and the models in this repository belong to Riot Games. They are collected here for a fan project.</sub>
''')

open(os.path.join(ROOT, 'README.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(out))
print('README.md written;', len(models), 'models,', 'not placed in a category:', unplaced)
for key, *_ in CATEGORIES:
    print(f'  {key}: {len(groups[key])}')
