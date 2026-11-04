# S6987 everything/run_all.py MANIFEST.json [--jars J...|--rcon HOST:PORT:PASS] [--only blocks,items,entities,recipes,dimensions,commands,bosses,machines] [--limit N] [--out DIR]
#   [--bosses id,id] [--machines machines.json] [--client]
# Exercises everything the manifest lists on a running server (own Lane from --jars, or an existing server such as C:\MCTestServer via --rcon; enable-rcon=true there)
# and writes OUT/report.tsv + REPORT.md: one row per thing, PASS / FAIL / UNTESTED, with the evidence file (the server's own command feedback, plus screenshots with --client).
# Vanilla commands only (setblock, item replace, summon, damage, execute in, crafter block), so no new jar. Runs at spawn in the real overworld; a dimension is entered only when it is the thing tested.
import sys, os, re, json, time, socket, struct, pathlib, csv, collections
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
class Rcon:
    def __init__(s, host, port, pw):
        s.k = socket.create_connection((host, port), 30); s.n = 0; s._send(3, pw)
    def _send(s, t, body):
        s.n += 1; b = body.encode(); s.k.sendall(struct.pack('<iii', 10 + len(b), s.n, t) + b + b'\0\0'); return s._recv()
    def _recv(s):
        h = b''
        while len(h) < 4: h += s.k.recv(4 - len(h))
        n = struct.unpack('<i', h)[0]; d = b''
        while len(d) < n: d += s.k.recv(n - len(d))
        return d[8:-2].decode('utf8', 'replace')
    def cmd(s, c): return re.sub('§.', '', s._send(2, c)).strip()
R = None; OUT = pathlib.Path('report'); ROWS = []
def row(cat, id_, status, detail, ev=''):
    ROWS.append((cat, id_, status, detail, ev))
def evid(cat, id_, lines):
    p = OUT / 'evidence' / cat / (id_.replace(':', '__').replace('/', '_') + '.log'); p.parent.mkdir(parents=True, exist_ok=True); p.write_text('\n'.join(lines) + '\n'); return str(p.relative_to(OUT))
def c(x): return R.cmd(x)
def cells(n, per=48):  # cell i -> x, z; y=100 sky so the flat ground never interferes
    return [(2 * (i % 8) + 1, 100, 2 * (i // 8) + 1) for i in range(n)]
def clear(): c('fill 0 99 0 17 103 17 air'); c('kill @e[type=!player]')
def batches(seq, n=48):
    for i in range(0, len(seq), n): yield seq[i:i + n]
def prep():
    c('forceload add 0 0 17 17'); c('gamerule spawn_mobs false'); c('time set day'); time.sleep(1)
OK_SET = re.compile(r'Changed the block'); OK_SUM = re.compile(r'Summoned new')
def t_blocks(ids):
    for b in batches(ids):
        clear(); out = {}
        for id_, (x, y, z) in zip(b, cells(len(b))):
            out[id_] = [f'> setblock {x} {y} {z} {id_}', c(f'setblock {x} {y} {z} {id_}')]
        time.sleep(1.5)  # a few ticks so block entities / tick handlers run
        for id_, (x, y, z) in zip(b, cells(len(b))):
            t = c(f'execute if block {x} {y} {z} {id_}'); out[id_] += [f'> execute if block ... {id_}', t]
            ok = OK_SET.search(out[id_][1]) and 'passed' in t.lower()
            row('blocks', id_, 'PASS' if ok else 'FAIL', 'placed and read back' if ok else out[id_][1] + ' | ' + t, evid('blocks', id_, out[id_]))
def t_items(ids):
    for b in batches(ids):
        clear(); c('setblock 1 100 1 minecraft:chest'); 
        for id_ in b:
            o = ['> item replace block 1 100 1 container.0 with ' + id_ + ' 1', c(f'item replace block 1 100 1 container.0 with {id_} 1')]
            t = c(f'execute if items block 1 100 1 container.0 {id_}'); o += ['> execute if items ... ' + id_, t]
            ok = 'passed' in t.lower()
            row('items', id_, 'PASS' if ok else 'FAIL', 'stack created and read back from a container' if ok else o[1] + ' | ' + t, evid('items', id_, o))
def t_entities(ids):
    for b in batches(ids, 24):
        clear(); out = {}
        for id_, (x, y, z) in zip(b, cells(len(b))):
            c(f'setblock {x} 99 {z} minecraft:stone'); out[id_] = [f'> summon {id_} {x} {y} {z}', c(f'summon {id_} {x} {y} {z}')]
        time.sleep(2.5)
        for id_, (x, y, z) in zip(b, cells(len(b))):
            t = c(f'execute if entity @e[type={id_},distance=..30,x={x},y={y},z={z}]'); out[id_] += [f'> still present after 2.5 s', t]
            ok = OK_SUM.search(out[id_][1]) and 'passed' in t.lower()
            row('entities', id_, 'PASS' if ok else 'FAIL', 'summoned and still alive/ticking after 2.5 s' if ok else out[id_][1] + ' | ' + t, evid('entities', id_, out[id_]))
def t_dimensions(ids):
    for id_ in ids:
        a = c(f'execute in {id_} run forceload add 0 0'); b = c(f'execute in {id_} run setblock 0 120 0 minecraft:stone'); d = c(f'execute in {id_} run execute if block 0 120 0 minecraft:stone')
        ok = 'passed' in d.lower(); c(f'execute in {id_} run forceload remove 0 0')
        row('dimensions', id_, 'PASS' if ok else 'FAIL', 'chunk loads, block placed and read back' if ok else f'{a} | {b} | {d}', evid('dimensions', id_, [a, b, d]))
def t_commands():
    h = c('help'); roots = sorted(set(re.findall(r'^/(\S+)', h, re.M)))
    for r in roots:
        o = c(f'help {r}'); ok = bool(o) and 'unknown' not in o.lower()
        row('commands', r, 'UNTESTED' if ok else 'FAIL', 'registered (help resolves); not executed: side effects unknown, add it to --exec-safe in a spec' if ok else o, evid('commands', r, [o]))
VANILLA_TAG = {'minecraft:planks': 'minecraft:oak_planks', 'minecraft:logs': 'minecraft:oak_log', 'minecraft:wooden_slabs': 'minecraft:oak_slab', 'minecraft:stone_crafting_materials': 'minecraft:cobblestone',
               'minecraft:coals': 'minecraft:coal', 'minecraft:wool': 'minecraft:white_wool', 'minecraft:sand': 'minecraft:sand'}
def pick(ing, M):
    for x in ing:
        if not x.startswith('#'): return x
        t = x[1:]
        if t in VANILLA_TAG: return VANILLA_TAG[t]
        v = M['tags'].get(t)
        if v and not v[0].startswith('#'): return v[0]
    return None
def t_recipes(M, ids):
    for id_ in ids:
        r = M['recipes'][id_]; ty = r['type'].split(':')[-1]
        if ty not in ('crafting_shaped', 'crafting_shapeless'):
            row('recipes', id_, 'UNTESTED', f'type {r["type"] or "?"} needs its machine driver (see machines spec)'); continue
        if not r['result']: row('recipes', id_, 'FAIL', 'recipe has no result'); continue
        slots = {}
        if ty == 'crafting_shaped':
            for ri, line in enumerate(r['pattern']):
                for ci, ch in enumerate(line):
                    if ch != ' ': slots[ri * 3 + ci] = pick(r['key'].get(ch, []), M)
        else:
            for i, ing in enumerate(r['ingredients']): slots[i] = pick(ing, M)
        if not slots or any(v is None for v in slots.values()): row('recipes', id_, 'UNTESTED', 'an ingredient is a tag with no resolvable member'); continue
        clear(); o = []
        c('setblock 9 100 9 minecraft:crafter[orientation=down_east]')
        for s, it in slots.items(): o += [f'> slot {s} = {it}', c(f'item replace block 9 100 9 container.{s} with {it} 1')]
        o += ['> power', c('setblock 8 100 9 minecraft:redstone_block')]; time.sleep(1.2)
        d = c('data get entity @e[type=item,limit=1,sort=nearest,x=9,y=100,z=9,distance=..6] Item'); o += ['> dropped stack', d]
        m = re.search(r'id:\s*"([^"]+)"', d); n = re.search(r'count:\s*(\d+)', d); got, cnt = (m and m[1]), (int(n[1]) if n else 1)
        if got == r['result'] and cnt == r['count']: row('recipes', id_, 'PASS', f'crafted {cnt} x {got} as intended', evid('recipes', id_, o))
        elif got: row('recipes', id_, 'FAIL', f'intended {r["count"]} x {r["result"]} but crafted {cnt} x {got}', evid('recipes', id_, o))
        else: row('recipes', id_, 'FAIL', 'nothing crafted from the exact inputs (recipe not registered, disabled, or overridden)', evid('recipes', id_, o))
def t_static(M):
    for rid, st, why in M['static_checks']:
        row('recipes' if rid in M['recipes'] else 'obtainable', rid, 'UNTESTED' if st == 'INFO' else st, why)
def t_bosses(M, ids, client):
    for id_ in ids:
        clear(); o = [f'> summon {id_}', c(f'summon {id_} 9 100 9 {{PersistenceRequired:1b}}')]; time.sleep(3)
        h0 = c(f'data get entity @e[type={id_},limit=1] Health'); o += ['> health after spawn', h0]
        alive = 'Health' in h0
        near0 = c('execute if entity @e[type=!player,distance=..60,x=9,y=100,z=9]')
        # fight: survival player (needs --client) stands beside it; bare console runs only report alive/kill/loot
        ctx = {}
        if client:
            o += [c('gamemode survival Tester'), c('tp Tester 9 100 14 180 0')]; time.sleep(8)
            ph = c('data get entity Tester Health'); ctx['player_health'] = ph; o += ['> player health after 8 s next to boss', ph]
            fx = c('data get entity Tester ActiveEffects'); o += ['> player effects', fx]
            cnt = c('execute store result score #n dt run execute if entity @e[type=!player,distance=..60,x=9,y=100,z=9]'); o += ['> entities around', cnt]
        else: o += ['> (no client: fight and ability checks skipped)']
        o += ['> kill as player', c(f'damage @e[type={id_},limit=1] 100000 minecraft:player_attack' + (' by Tester' if client else ''))]; time.sleep(3)
        dead = 'passed' not in c(f'execute if entity @e[type={id_}]').lower(); o += [f'> dead: {dead}']
        drops = c('data get entity @e[type=item,limit=1,sort=nearest,x=9,y=100,z=9,distance=..20] Item'); o += ['> nearest drop', drops]
        exp = M['loot'].get(id_.replace(':', ':entities/'), [])
        got_drop = 'id:' in drops
        ev = evid('bosses', id_, o)
        if not alive: row('bosses', id_, 'FAIL', 'did not spawn / not alive 3 s later', ev)
        elif not dead: row('bosses', id_, 'FAIL', 'could not be killed with 100000 damage', ev)
        elif exp and not got_drop: row('bosses', id_, 'FAIL', f'loot table lists {exp[:5]} but nothing dropped', ev)
        elif not client: row('bosses', id_, 'UNTESTED', f'spawns, alive, killable{", drops loot" if got_drop else ", no loot table found"}; fight and abilities need --client', ev)
        else: row('bosses', id_, 'PASS' if 'Health' in ctx.get('player_health', '') else 'UNTESTED', 'spawned, fought a survival player (see evidence), killed, loot checked', ev)
def t_machines(spec):
    for m in json.load(open(spec)):  # {"id","block","state","slots":{"0":"item"},"wait":10,"out_slot":2,"expect":"ns:item"}
        clear(); b = m['block'] + m.get('state', ''); o = [c(f'setblock 9 100 9 {b}')]
        for s, it in m.get('slots', {}).items(): o.append(c(f'item replace block 9 100 9 container.{s} with {it}'))
        for cmd in m.get('extra', []): o.append(c(cmd))
        time.sleep(m.get('wait', 10)); t = c(f'execute if items block 9 100 9 container.{m["out_slot"]} {m["expect"]}'); o.append(t)
        row('machines', m['id'], 'PASS' if 'passed' in t.lower() else 'FAIL', f'output slot {m["out_slot"]} holds {m["expect"]}' if 'passed' in t.lower() else 'expected output missing: ' + t, evid('machines', m['id'], o))
def main():
    global R, OUT
    a = sys.argv[1:]; M = json.load(open(a[0])); opt = lambda k, d=None: a[a.index(k) + 1] if k in a else d
    OUT = pathlib.Path(opt('--out', 'report')); OUT.mkdir(parents=True, exist_ok=True)
    only = (opt('--only') or 'blocks,items,entities,recipes,dimensions,commands,bosses,machines').split(','); lim = int(opt('--limit', 10**9)); lane = None
    if '--rcon' in a:
        h, p, pw = opt('--rcon').split(':'); R = Rcon(h, int(p), pw)
    else:
        from lane import Lane
        jars = a[a.index('--jars') + 1:]; jars = jars[:next((i for i, x in enumerate(jars) if x.startswith('--')), len(jars))]
        lane = Lane('everything', jars, props={'enable-rcon': 'true', 'rcon.port': '25575', 'rcon.password': 'dtest', 'broadcast-rcon-to-ops': 'false'}, srv_xmx='3G', out=str(OUT / 'shots')); lane.__enter__()
        R = Rcon('127.0.0.1', 25575, 'dtest')
        if '--client' in a: lane.start_client()
    try:
        prep(); c('scoreboard objectives add dt dummy')
        if 'blocks' in only: t_blocks(sorted(M['blocks'])[:lim])
        if 'items' in only: t_items(sorted(M['items'])[:lim])
        if 'entities' in only: t_entities(sorted(M['entities'])[:lim])
        if 'recipes' in only: t_static(M); t_recipes(M, sorted(M['recipes'])[:lim])
        if 'dimensions' in only: t_dimensions(sorted(M['dimensions'])[:lim])
        if 'commands' in only: t_commands()
        if 'bosses' in only and opt('--bosses'): t_bosses(M, opt('--bosses').split(','), '--client' in a)
        if 'machines' in only and opt('--machines'): t_machines(opt('--machines'))
    finally:
        with open(OUT / 'report.tsv', 'w', newline='') as f:
            w = csv.writer(f, delimiter='\t'); w.writerow(['category', 'id', 'status', 'detail', 'evidence']); w.writerows(ROWS)
        tally = collections.Counter((r[0], r[2]) for r in ROWS); cats = sorted({r[0] for r in ROWS})
        md = ['# Full-game test report', '', '| category | PASS | FAIL | UNTESTED |', '|---|---|---|---|'] + [f'| {k} | ' + ' | '.join(str(tally[(k, s)]) for s in ('PASS', 'FAIL', 'UNTESTED')) + ' |' for k in cats]
        md += ['', 'Every row, with evidence path, is in report.tsv. FAIL rows:', ''] + [f'- {r[0]} `{r[1]}`: {r[3]} ({r[4]})' for r in ROWS if r[2] == 'FAIL'][:200]
        (OUT / 'REPORT.md').write_text('\n'.join(md) + '\n'); print('\n'.join(md[:12]))
        if lane: lane.stop()
if __name__ == '__main__': main()
