#!/usr/bin/env python3
"""Turn a persisted browser_batch output (JSON list of {type,text}) into a compact,
scored candidate list.

Usage: parse_x_pages.py <tool-result.json> [--known id,id,...] [--known-file f ...]
                        [--labels NOTIFICATIONS,HOME,S1,...,PEER:handle,LIST:name]

Each read_page block is one page; label them in order with --labels. A label starting
with PEER: is a profile page: posts are scored against that page's own median views and
anything at 3x or more is flagged OUTLIER. --known-file accepts files with one status id
per line, optionally followed by a tab and a reason (the skip log)."""
import json, re, sys, argparse, statistics
ap = argparse.ArgumentParser()
ap.add_argument('path'); ap.add_argument('--known', default='')
ap.add_argument('--known-file', action='append', default=[])
ap.add_argument('--labels', default='NOTIFICATIONS,HOME,S1,S2,S3')
a = ap.parse_args()
known = set(x.strip() for x in a.known.replace('\n', ',').split(',') if x.strip())
for f in a.known_file:
    try:
        for line in open(f):
            sid = line.split('\t')[0].strip()
            if sid: known.add(sid)
    except FileNotFoundError:
        pass
items = json.load(open(a.path))
texts = [b['text'] for b in items if b.get('type') == 'text']
print('closed tab:', any(t.startswith('[tabs_close_mcp]') for t in texts))
blocks = [t for t in texts if t.startswith('[read_page]')]
labels = a.labels.split(',')

def num(s):
    s = s.replace(',', '')
    m = re.match(r'^(\d+(?:\.\d+)?)([KM]?)$', s)
    if not m: return 0
    v = float(m.group(1)); return int(v * {'': 1, 'K': 1e3, 'M': 1e6}[m.group(2)])

def counts_of(grp):
    c = dict(replies=0, reposts=0, likes=0, bookmarks=0, views=0)
    for n, k in re.findall(r'(\d[\d,]*) (repl|repost|like|bookmark|view)', grp):
        c[{'repl': 'replies', 'repost': 'reposts', 'like': 'likes', 'bookmark': 'bookmarks', 'view': 'views'}[k]] = int(n.replace(',', ''))
    return c

def age_min(age):
    m = re.match(r'(\d+) (minute|hour|second)', age)
    if not m: return 10**6
    return int(m.group(1)) * {'second': 0, 'minute': 1, 'hour': 60}[m.group(2)]

def parse(art):
    h = re.search(r'link \[ref_\d+\] href="/([A-Za-z0-9_]+)"', art); handle = h.group(1) if h else '?'
    t = re.search(r'link "([^"]+)" \[ref_\d+\] href="(/[^"/]+/status/(\d+))"', art)
    age, url, sid = (t.group(1), t.group(2), t.group(3)) if t else ('?', '', '')
    after = art[t.end():] if t else art
    gens = [m.group(1) for m in re.finditer(r'generic "([^"]+)"', after)]
    gens = [g for g in gens if not g.startswith(('Replying to', 'Quote', 'Embedded', 'Verified', '@'))]
    out = []
    for g in gens:
        if re.match(r'^\d+[hms]$', g) and not out: continue   # the short age badge under the time link
        if re.match(r'^\d+(\.\d+)?[KM]?$', g) or g == 'Show more' or re.match(r'^\d+[hm]$', g): break
        out.append(g)
    grp = re.search(r'group "([^"]+)"', art)
    c = counts_of(grp.group(1) if grp else '')
    return dict(handle=handle, age=age, url=url, sid=sid, text=' / '.join(out),
                counts=grp.group(1) if grp else '', trunc='Show more' in art, c=c, mins=age_min(age))

def score(d):
    c, mins = d['c'], d['mins']
    tags = []
    if mins <= 30: tags.append('FRESH')
    if mins <= 120 and c['replies'] < 10: tags.append('EARLY')
    elif c['replies'] >= 20: tags.append('HOT')
    if 500 <= c['views'] <= 60000: tags.append('PEER-BAND')
    elif c['views'] > 60000: tags.append('BIG')
    if c['likes'] and c['replies'] / c['likes'] >= 0.15: tags.append('CONVO')
    if c['bookmarks'] >= 10: tags.append('SAVED')
    if mins > 360: tags.append('OLD')
    return ' '.join(tags)

for label, tree in zip(labels, blocks):
    print(f'\n========== {label} ==========')
    arts = re.split(r'\n\s*article \[ref_\d+\]', tree)[1:]
    if not arts: print('!! no articles'); continue
    if label.startswith('PEER:'):
        ds = [parse(x) for x in arts]
        ds = [d for d in ds if d['sid'] and d['c']['views']]
        pinned = [d for d in ds if d['mins'] >= 10**6]          # dated posts at the top are pinned
        ds = [d for d in ds if d['mins'] < 10**6]
        for d in pinned: print(f"  pinned (ignored): @{d['handle']} {d['age']} {d['counts']} :: {d['text'][:120]}")
        views = [d['c']['views'] for d in ds]
        med = statistics.median(views) if views else 0
        print(f'median views on page: {med:.0f} over {len(ds)} posts')
        for d in ds:
            mult = d['c']['views'] / med if med else 0
            flag = 'OUTLIER' if mult >= 3 else ('above' if mult >= 1.5 else '')
            kn = 'KNOWN' if d['sid'] in known else 'NEW'
            print(f"- {kn} {flag:7s} {mult:4.1f}x @{d['handle']} | {d['age']} | {d['counts']} {'[TRUNC]' if d['trunc'] else ''} | {score(d)}\n   https://x.com{d['url']}\n   {d['text'][:200]}")
        continue
    for art in arts:
        if label == 'NOTIFICATIONS' and 'Replying to' not in art:
            kind = re.search(r'generic "((?:and \d+ others? )?(?:liked|followed|reposted|quoted)[^"]*)"', art)
            who = sorted(set(re.findall(r'link \[ref_\d+\] href="/([A-Za-z0-9_]+)"', art)))
            age = re.search(r'generic "(\d+ (?:minutes?|hours?) ago|Sep \d+)"', art)
            snip = [s for s in re.findall(r'generic "([^"]{30,})"', art) if not s.startswith(('New post', 'and '))]
            print(f'  {(kind.group(1) if kind else "?"):28s} {who[:4]} {age.group(1) if age else ""} :: {snip[-1][:70] if snip else ""}')
            continue
        d = parse(art)
        flag = 'KNOWN' if d['sid'] in known else 'NEW'
        rep = d['c']['replies']
        tag = f"REPLY-TO-YOU {flag} replies={rep}" if label == 'NOTIFICATIONS' else f"- {flag}"
        print(f"{tag} @{d['handle']} | {d['age']} | {d['counts']} {'[TRUNC]' if d['trunc'] else ''} | {score(d)}\n   https://x.com{d['url']}\n   {d['text'][:230]}")
