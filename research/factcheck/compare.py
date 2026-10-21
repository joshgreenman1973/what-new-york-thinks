#!/usr/bin/env python3
"""Compare the blind checkers' readings with the page's data. Usage: compare.py [group ...]"""
import json, glob, os, re, sys
from datetime import datetime


def as_date(t):
    t = re.sub(r'\s+', ' ', str(t).replace('Sept.', 'Sep').replace('.', '')).strip()
    for f in ('%Y-%m-%d', '%B %d, %Y', '%b %d, %Y', '%B %d %Y', '%b %d %Y', '%m/%d/%Y', '%m/%d/%y'):
        try:
            return datetime.strptime(t, f).date().isoformat()
        except ValueError:
            pass
    return t

HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, '..', '..', 'data', 'polls.json')))
rows = {r['id']: r for r in D['questions']}
polls = {p['poll_id']: p for p in D['polls']}


def val(v):
    if v is None:
        return None
    s = str(v).strip().replace('%', '').replace('\u2212', '-')
    if s in ('<1', '<0.5', '*', '<1.0'):
        return '<1'
    if s in ('-', '--', '—'):
        return 0.0
    try:
        return float(s)
    except ValueError:
        return s


def ours(x):
    return '<1' if x.get('shown') == '<1' else float(x['pct'])


def norm_label(s):
    return re.sub(r'[^a-z0-9]+', ' ', (s or '').lower()).strip()


groups = sys.argv[1:] or [os.path.basename(p)[9:-5] for p in glob.glob(f'{HERE}/readings-*.json')]
tot = {'match': 0, 'mismatch': 0, 'missing': 0, 'unreadable': 0}
issues = []
seen_detail = set()
for g in groups:
    f = f'{HERE}/readings-{g}.json'
    if not os.path.exists(f):
        print(f'[{g}] no results yet')
        continue
    res = json.load(open(f))['results']
    for c in res:
        r = rows.get(c['check_id'])
        if not r:
            issues.append((g, c['check_id'], 'unknown check id', ''))
            continue
        if c.get('status') in ('unreachable', 'not found'):
            tot['unreadable'] += 1
            issues.append((g, c['check_id'], c['status'], (c.get('note') or '')[:160]))
            continue
        figs = {norm_label(k): val(v) for k, v in (c.get('figures') or {}).items()}
        for x in (r['results'] if g == 'supplement' else (r.get('breakdown') or r['results'])):
            theirs = figs.get(norm_label(x['label']))
            if theirs is None:
                tot['missing'] += 1
                issues.append((g, c['check_id'], 'no reading', f"{r['subject']} | {x['label']} ours={ours(x)}"))
            elif theirs == ours(x) or (isinstance(theirs, float) and isinstance(ours(x), float) and abs(theirs - ours(x)) < 1e-9):
                tot['match'] += 1
            else:
                tot['mismatch'] += 1
                issues.append((g, c['check_id'], 'MISMATCH', f"{r['poll_id']} {'NYC col' if r['city_column'] else 'total'} | {r['subject']} | {r.get('item') or ''} | {x['label']}: ours={ours(x)} theirs={theirs} | {(c.get('where') or '')[:80]} | {(c.get('note') or '')[:120]}"))
        pdx = c.get('poll_details') or {}
        p = polls.get(r['poll_id'], {})
        for k in ('field_start', 'field_end', 'n', 'moe'):
            if pdx.get(k) not in (None, '') and p.get(k) not in (None, ''):
                a, b = str(pdx[k]).strip(), str(p[k]).strip()
                if k in ('n', 'moe'):
                    try:
                        if float(re.sub(r'[^0-9.]', '', a)) == float(b):
                            continue
                    except ValueError:
                        pass
                if k.startswith('field'):
                    a = as_date(a)
                if a != b and (r['poll_id'], k) not in seen_detail:
                    seen_detail.add((r['poll_id'], k))
                    issues.append((g, c['check_id'], 'POLL DETAIL', f"{r['poll_id']} {k}: ours={b} theirs={a}"))
print(tot)
for i in issues:
    print(' | '.join(i))
