#!/usr/bin/env python3
"""Parse the Longevity Master Workbook into static JSON for the Astro site.

Reads data/Longevity_Master_Workbook_v2.xlsx, writes JSON files into src/data/.
Run via `npm run data`. The JSON is committed so the site builds without Python.
"""

import json
import os
import re

from openpyxl import load_workbook

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'data', 'Longevity_Master_Workbook_v2.xlsx')
OUT = os.path.join(ROOT, 'src', 'data')

BLOCK = re.compile(r'^[█▓▒░ ]*$')


def sheet_rows(path, name):
    wb = load_workbook(path, data_only=True)
    ws = wb[name]
    rows = []
    for row in ws.iter_rows(values_only=True):
        vals = ['' if v is None else str(v).strip() for v in row]
        rows.append(vals)
    # left-shift every row to its first non-empty cell
    norm = []
    for vals in rows:
        while vals and not vals[0]:
            vals.pop(0)
        while vals and not vals[-1]:
            vals.pop()
        norm.append(vals)
    while norm and not norm[-1]:
        norm.pop()
    return norm


def is_heading(cells):
    if len(cells) != 1 or not cells[0]:
        return False
    t = cells[0]
    if len(t) > 90 or len(t) < 3:
        return False
    if t.upper().startswith('TRAINING LIVES'):
        return True
    letters = [c for c in t if c.isalpha()]
    if not letters:
        return False
    upper = sum(1 for c in letters if c.isupper()) / len(letters)
    return upper > 0.8


HEADER_HINTS = {
    'item', 'metric', 'the mistake', 'baseline item', 'tag', 'sheet', 'field',
    'derived', 'date', 'lever', '#', 'study', 'add or verify this week', 'flag',
    'log', 'log item', 'day', 'substance', 'condition',
}


def is_header(cells):
    if len(cells) < 3:
        return False
    joined = [c.lower() for c in cells]
    if any(c in ('grade', 'ref', 'source', 'unit', 'journal · year', 'cited for') for c in joined):
        return True
    return joined[0] in HEADER_HINTS


def parse_sheet(rows):
    """Generic section parser: yields sections with title, intro lines, header, rows."""
    sections = []
    cur = None
    for cells in rows:
        if not cells:
            continue
        if is_heading(cells):
            cur = {'title': cells[0], 'intro': [], 'header': None, 'rows': []}
            sections.append(cur)
            continue
        if cur is None:
            continue
        if is_header(cells) and not cur['rows']:
            cur['header'] = cells
            continue
        if cur['header'] is None:
            cur['intro'].append(cells)
        else:
            width = len(cur['header'])
            row = (cells + [''] * width)[:width]
            cur['rows'].append(row)
    # drop fully-empty columns and pure block-bar columns
    for sec in sections:
        if not sec['header']:
            continue
        if not sec['rows']:
            # blank log template: keep the header as written
            sec['header'] = [c for c in sec['header'] if c]
            continue
        n = len(sec['header'])
        keep = []
        for i in range(n):
            col = [r[i] for r in sec['rows']]
            header_empty = not sec['header'][i]
            all_empty = all(not v for v in col)
            all_blocks = all(BLOCK.match(v) for v in col)
            if header_empty and (all_empty or all_blocks):
                continue
            if not header_empty and all_empty:
                continue
            keep.append(i)
        sec['header'] = [sec['header'][i] for i in keep]
        sec['rows'] = [[r[i] for i in keep] for r in sec['rows']]
    return [s for s in sections if s['intro'] or s['header'] or s['rows']]


def parse_prose_sheet(rows):
    """Sheets without tables: intro paragraph plus key/value pairs per section."""
    sections = []
    cur = None
    for cells in rows:
        if not cells:
            continue
        if is_heading(cells):
            cur = {'title': cells[0], 'intro': [], 'pairs': []}
            sections.append(cur)
            continue
        if cur is None:
            continue
        if len(cells) == 1:
            cur['intro'].append(cells[0])
        elif len(cells) == 2:
            cur['pairs'].append({'k': cells[0], 'v': cells[1]})
        else:
            cur['intro'].append(' — '.join(c for c in cells if c))
    return sections


def clean_rows(sec):
    return [
        {'cells': r} for r in sec['rows']
        if any(c for c in r)
    ]


SMALL_WORDS = {'a', 'an', 'and', 'as', 'at', 'by', 'for', 'in', 'of', 'on', 'or', 'per', 'the', 'to', 'with'}


def nice_title(t):
    words = t.title().split(' ')
    out = []
    for i, w in enumerate(words):
        if i and w.lower() in SMALL_WORDS:
            out.append(w.lower())
        else:
            out.append(w)
    s = ' '.join(out)
    for bad, good in (('Apob', 'ApoB'), ('Ldl-C', 'LDL-C'), ('Hdl-C', 'HDL-C'), ('Hdl', 'HDL'),
                      ('Vo2Max', 'VO2max'), ('Lp(A)', 'Lp(a)'), ('Bmi', 'BMI'), ('Upf', 'UPF'),
                      ('Spf', 'SPF'), ('Rct', 'RCT'), ('Hba1C', 'HbA1c'), ('Aga', 'AGA'),
                      ('Rx', 'Rx'), ('Nad+', 'NAD+'), ('Uva', 'UVA'), ('Uvb', 'UVB')):
        s = s.replace(bad, good)
    return s


def knowledge_sheet(path, name, slug, blurb):
    secs = parse_sheet(sheet_rows(path, name))
    description = blurb
    # the first section is the sheet's own title line; use its intro as the page description
    if secs and not secs[0]['header'] and not secs[0]['rows'] and secs[0]['intro']:
        description = ' '.join(' '.join(c for c in line if c) for line in secs[0]['intro']) or blurb
        secs = secs[1:]
    return {
        'slug': slug,
        'sheet': name,
        'blurb': description,
        'sections': [
            {
                'title': nice_title(s['title']),
                'intro': [' '.join(c for c in line if c) for line in s['intro']],
                'header': s['header'],
                'rows': [r for r in s['rows'] if any(c for c in r)],
            }
            for s in secs
        ],
    }


def main():
    os.makedirs(OUT, exist_ok=True)

    systems = [
        knowledge_sheet(SRC, 'APPEARANCE', 'appearance',
                        'Hair, scalp, face, skin, eyes, teeth and grooming — the visible layer, filtered by your Walker type, Fitzpatrick type and scalp condition.'),
        knowledge_sheet(SRC, 'BODY_NUTRITION', 'body-nutrition',
                        'Energy balance, protein architecture, caffeine, alcohol, hydration — and the supplements that are not worth the money.'),
        knowledge_sheet(SRC, 'SLEEP_RECOVERY', 'sleep-recovery',
                        'The one intervention that improves everything else. Wake time first; everything downstream keys off it.'),
        knowledge_sheet(SRC, 'LONGEVITY_HEALTH', 'longevity-health',
                        'Blood markers, grip, VO2max and screening — the added-years layer, read against your condition flags.'),
        knowledge_sheet(SRC, 'PRESENCE_STYLE', 'presence-style',
                        'Posture, voice, speech, fragrance and fit — presence as practice, not purchase.'),
    ]
    json.dump(systems, open(os.path.join(OUT, 'systems.json'), 'w'), indent=1)

    mistakes = knowledge_sheet(SRC, 'MISTAKES', 'mistakes',
                               'The habits that quietly undo everything else — with the mechanism, the fix and a verdict.')
    json.dump(mistakes, open(os.path.join(OUT, 'mistakes.json'), 'w'), indent=1)

    # Dashboard metrics. Empty "Your value"/"Status" columns are dropped during
    # parsing, so the surviving row reads: metric, target band, why, grade.
    dash = parse_sheet(sheet_rows(SRC, 'MASTER_DASHBOARD'))
    metrics = []
    for sec in dash:
        if sec['header'] and sec['header'][0].lower() == 'metric':
            for r in sec['rows']:
                if not any(r):
                    continue
                metrics.append({
                    'metric': r[0],
                    'target': r[1] if len(r) > 1 else '',
                    'why': r[2] if len(r) > 2 else '',
                    'grade': r[3] if len(r) > 3 else '',
                })
    json.dump(metrics, open(os.path.join(OUT, 'metrics.json'), 'w'), indent=1)

    # Profile field catalogue (structure only — no personal values)
    profile_rows = sheet_rows(SRC, 'PROFILE')
    groups, cur = [], None
    for cells in profile_rows:
        if not cells:
            continue
        if len(cells) == 1 and cells[0].isupper() or (len(cells) == 1 and is_heading(cells)):
            cur = {'title': cells[0].title(), 'fields': []}
            groups.append(cur)
            continue
        if cur and len(cells) >= 4 and cells[0].lower() not in ('field', 'derived') and cells[1].lower() != 'your value':
            cur['fields'].append({'field': cells[0], 'unit': cells[2], 'why': cells[3]})
    profile = {'groups': groups}
    json.dump(profile, open(os.path.join(OUT, 'profile.json'), 'w'), indent=1)

    # Weekly plan
    plan_secs = parse_sheet(sheet_rows(SRC, 'WEEKLY_PLAN'))
    plan = {'handoff': {'title': '', 'intro': [], 'pairs': []}, 'anchors': [], 'baseline': [], 'weeks': []}

    def kv_rows(sec, skip_first=False):
        """Rows from the table if any, else key/value lines from the intro."""
        if sec['rows']:
            pairs = [{'k': r[0], 'v': r[1]} for r in sec['rows'] if len(r) > 1 and r[0] and r[1]]
        else:
            pairs = [{'k': line[0], 'v': line[1]} for line in sec['intro'] if len(line) > 1 and line[0] and line[1]]
        return pairs[1:] if skip_first else pairs

    for sec in plan_secs:
        t = sec['title']
        intro = [' '.join(c for c in line if c) for line in sec['intro']]
        if 'TRAINING LIVES' in t:
            plan['handoff'] = {'title': 'Where training lives', 'intro': intro, 'pairs': kv_rows(sec)}
        elif 'DAILY ANCHORS' in t:
            plan['anchors'] = kv_rows(sec)
        elif 'BASELINE' in t:
            plan['baseline'] = kv_rows(sec, skip_first=True)
        elif re.match(r'^WEEK \d+', t):
            num = int(re.match(r'^WEEK (\d+)', t).group(1))
            tasks = [{'task': r[0], 'detail': r[1], 'trackIn': r[2] if len(r) > 2 else ''}
                     for r in sec['rows'] if r and r[0]]
            plan['weeks'].append({'num': num, 'title': intro[0] if intro else t, 'tasks': tasks})
    json.dump(plan, open(os.path.join(OUT, 'plan.json'), 'w'), indent=1)

    # Tracking log templates
    track_secs = parse_sheet(sheet_rows(SRC, 'TRACKING'))
    logs = [{'name': s['title'],
             'note': ' '.join(c for line in s['intro'] for c in line),
             'columns': s['header']}
            for s in track_secs if s['header']]
    json.dump(logs, open(os.path.join(OUT, 'tracking.json'), 'w'), indent=1)

    # Read-me → about content
    rm_secs = parse_sheet(sheet_rows(SRC, 'READ_ME'))
    about = {'sections': [], 'references': [], 'medical': []}
    for s in rm_secs:
        t = s['title']
        intro = [' '.join(c for line in s['intro'] for c in line)]
        if t.upper().startswith('PRIMARY REFERENCES'):
            about['references'] = [{'n': r[0], 'study': r[1], 'journal': r[2], 'citedFor': r[3]}
                                   for r in s['rows'] if len(r) > 3 and r[1]]
        elif t.upper().startswith('THE MEDICAL LINE'):
            about['medical'] = [{'k': r[0], 'v': r[1]} for r in s['rows'] if len(r) > 1 and r[0]]
        else:
            about['sections'].append({
                'title': t,
                'intro': intro,
                'rows': [{'k': r[0], 'v': r[1]} for r in s['rows'] if len(r) > 1 and r[0] and r[1]]
                        or [{'k': '', 'v': ' '.join(r)} for r in s['rows'] if any(r)],
            })
    json.dump(about, open(os.path.join(OUT, 'about.json'), 'w'), indent=1)

    counts = {
        'systems': sum(len(s['sections']) for s in systems),
        'systemRows': sum(len(sec['rows']) for s in systems for sec in s['sections']),
        'mistakeSections': len(mistakes['sections']),
        'metrics': len(metrics),
        'profileFields': sum(len(g['fields']) for g in groups),
        'weeks': len(plan['weeks']),
        'logs': len(logs),
        'references': len(about['references']),
    }
    print(json.dumps(counts, indent=1))


if __name__ == '__main__':
    main()
