#!/usr/bin/env python3
"""Turn a persisted browser_batch output (JSON list of {type,text}) into a compact
candidate list. Usage: parse_x_pages.py <tool-result.json> [--known id,id,...]
Each read_page block is treated as one page; label them in order with --labels."""
import json, re, sys, argparse
ap = argparse.ArgumentParser()
ap.add_argument('path'); ap.add_argument('--known', default='')
ap.add_argument('--labels', default='NOTIFICATIONS,HOME,S1,S2,S3')
a = ap.parse_args()
known = set(x.strip() for x in a.known.replace('\n', ',').split(',') if x.strip())
items = json.load(open(a.path))
texts = [b['text'] for b in items if b.get('type') == 'text']
print('closed tab:', any(t.startswith('[tabs_close_mcp]') for t in texts))
blocks = [t for t in texts if t.startswith('[read_page]')]
labels = a.labels.split(',')

def parse(art):
    h = re.search(r'link \[ref_\d+\] href="/([A-Za-z0-9_]+)"', art); handle = h.group(1) if h else '?'
    t = re.search(r'link "([^"]+)" \[ref_\d+\] href="(/[^"/]+/status/(\d+))"', art)
    age, url, sid = (t.group(1), t.group(2), t.group(3)) if t else ('?', '', '')
    after = art[t.end():] if t else art
    gens = [m.group(1) for m in re.finditer(r'generic "([^"]+)"', after)]
    gens = [g for g in gens if not g.startswith(('Replying to', 'Quote', 'Embedded', 'Verified', '@'))]
    out = []
    for g in gens:
        if re.match(r'^\d+(\.\d+)?[KM]?$', g) or g == 'Show more' or re.match(r'^\d+[hm]$', g): break
        out.append(g)
    grp = re.search(r'group "([^"]+)"', art)
    return dict(handle=handle, age=age, url=url, sid=sid, text=' / '.join(out),
                counts=grp.group(1) if grp else '', trunc='Show more' in art)

for label, tree in zip(labels, blocks):
    print(f'\n========== {label} ==========')
    arts = re.split(r'\n\s*article \[ref_\d+\]', tree)[1:]
    if not arts: print('!! no articles'); continue
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
        rep = re.search(r'(\d+) Repl', d['counts'])
        tag = f"REPLY-TO-YOU {flag} replies={rep.group(1) if rep else '0'}" if label == 'NOTIFICATIONS' else f"- {flag}"
        print(f"{tag} @{d['handle']} | {d['age']} | {d['counts']} {'[TRUNC]' if d['trunc'] else ''}\n   https://x.com{d['url']}\n   {d['text'][:230]}")
