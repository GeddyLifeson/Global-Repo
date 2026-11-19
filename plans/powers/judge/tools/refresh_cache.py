#!/usr/bin/env python3
"""Refetch packed-cache page texts that look broken (under 60 chars: interwiki stubs like 'nl:Zatanna', disambig lists, empty) and store a longer live text in the same cache/*.pages.json.gz.
  refresh_cache.py [--dry]"""
import sys, os, gzip, glob, json, urllib.parse
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import pages
dry = '--dry' in sys.argv; n = 0
for g in sorted(glob.glob(os.path.join(HERE, '..', 'cache', '*.pages.json.gz'))):
    d = json.load(gzip.open(g, 'rt', encoding='utf-8')); ch = 0
    for u, t in d.items():
        if len(t) >= 60 or not u.startswith('http') or '/wiki/' not in u: continue
        h, ti = u.split('/')[2], urllib.parse.unquote(u.split('/wiki/', 1)[1]).replace('_', ' ')
        try: x = pages.full_extract(h, ti)
        except Exception: continue
        if len(x) > len(t) + 20 and not x.startswith(t[:10] + 'zzz'):
            print(os.path.basename(g), u[-60:], len(t), '->', len(x)); ch += 1
            if not dry: d[u] = x
    if ch and not dry: json.dump(d, gzip.open(g, 'wt', encoding='utf-8'), ensure_ascii=False); n += ch
print('refreshed', n)
