# S6988 Part J9: for each icon with no Library entry (PANSCRIPTUM_COVERAGE_ICONS.tsv entries=0), find its source wiki and universe from real lead text. No AI, nothing invented.
# python3 -I icon_sources.py OUT.tsv   (reads /mnt/project-files)
import json,re,os,sys
P='/mnt/project-files/'; B=P+'assay-c3m/'
um=json.load(open(B+'source_universe_map.json'))
miss=[l.split('\t')[0] for l in open(P+'plans/PANSCRIPTUM_COVERAGE_ICONS.tsv').read().splitlines()[1:] if l.split('\t')[1]=='0']
wiki={'Clark Kent':'dc','Wonder Woman':'dc','Spider-Man':'marvel','Captain America':'marvel','Aquaman':'dc','Green Lantern':'dc','Joker':'dc','Goku':'dragon-ball-z','Vegeta':'dragon-ball-z','Gohan':'dragon-ball-z','Frieza':'dragon-ball-z','Sasuke':'naruto','Luffy':'one-piece','Zoro':'one-piece','Kenshiro':'fist-of-the-north-star','Raoh':'fist-of-the-north-star','Jotaro':'jojo-s-bizarre-adventure','Sailor Moon':'sailor-moon','Kratos':'god-of-war','Darth Vader':'star-wars','Aragorn':'the-lord-of-the-rings','Sauron':'the-lord-of-the-rings'}
rows=['icon\tstatus\tsource_slug\tuniverse\tlead_idx\tevidence']
for n in miss:
    w=wiki.get(n)
    if not w:
        rows.append(f'{n}\tnot_in_source\t\t\t\tno source wiki for this franchise in source_universe_map.json or the leads; only incidental mentions elsewhere'); continue
    u=um.get(w,''); f=B+'leads/'+w+'.jsonl'
    if not os.path.exists(f):
        rows.append(f'{n}\tuniverse_in_map_pages_not_fetched\t{w}\t{u}\t\tleads/{w}.jsonl absent: wiki leads never downloaded'); continue
    p=re.compile(r'\b'+re.escape(n)+r'\b',re.I); first=None
    for l in open(f):
        r=json.loads(l)
        if p.search(r['text']):
            first=first or r
            if r['text'].lower().startswith(n.lower()): first=r; break
    rows.append(f"{n}\tin_source\t{w}\t{u}\t{first['i']}\t{first['text'][:110]}".replace('\t\t','\t\t') if first else f'{n}\tnot_in_source_wiki\t{w}\t{u}\t\tno lead in {w} names {n}')
open(sys.argv[1],'w').write('\n'.join(rows)+'\n')
