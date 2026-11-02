"""B08 loot and economy simulator (stdlib only).
Rolls data/items/loot_tables.csv inside the 30-minute session loop from design/loops and kindles levels
from level 1 until Hush falls at level 80, RUNS times. Reads data/ and design/loops/ read-only.
Run: python3 sim.py [runs]   (default 10000; writes the CSVs and report.html next to this file)
Model choices (SIM_ in findings.csv) are listed in README.md."""
import csv, os, random, re, sys
from bisect import bisect
from collections import Counter, defaultdict
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
GP = os.path.join(HERE, '..', '..', '..')
sys.path.insert(0, os.path.join(GP, 'data', 'actors', 'tools'))
from common import ember_drop  # FRM_EMBER_DROP
def rd(p): return list(csv.DictReader(open(os.path.join(GP, p), encoding='utf-8')))

ORDER = ['REG_01', 'REG_02', 'REG_03', 'REG_04', 'REG_05', 'REG_06', 'REG_Q']
BAND = {r['Region ID']: (int(r['Min level']), int(r['Max level'])) for r in rd('data/actors/region_bands.csv')}
KINDLE = {int(r['Level']): int(r['Ember to kindle next']) for r in rd('data/actors/level_curve.csv')}
FLOW = {r['band']: r for r in rd('design/loops/economy_flow.csv')}
RAR = ['Common', 'Forged', 'Rare', 'Relic', 'Shardborn']
DROP_RAR = {r['region_id']: [float(r['pct_' + k.lower()]) for k in RAR] for r in rd('data/items/drop_rarity_by_region.csv')}
POUCH = {r['item_id']: int(r['magnitude']) for r in rd('data/items/consumables.csv') if r['effect'] == 'Grants Ember'}
ENC = {r['enc_id'][:-7]: [(k, int(n)) for n, k in (p.split(' ', 1) for p in r['composition'].split('; '))]
       for r in rd('design/loops/encounter_templates.csv') if r['region'] == 'REG_01'}
ROLE = {'Fodder': 'FODDER', 'Skirmisher': 'SKIRMISHER', 'Artillery': 'ARTILLERY', 'Shield-bearer': 'SHIELDBEARER', 'Heavy': 'HEAVY', 'Leader': 'LEADER'}
FACTIONS = ['HOLLOWED', 'REMNANT', 'THORN', 'CHOIRBORN']
SESSION = ['ENC_PATROL', 'ENC_CAMP', 'ENC_PICKET', 'ENC_SITE', 'ENC_AMBUSH', 'ENC_ELITE']  # gen_loops.py SEG order
BREAKS, NODES, VAULTS, HOURS_CAP = 4, 3, 3, 200  # SIM choices per session / per region
COMPLETE_SESSIONS = 18  # SIM: completionist stays 9 h per region (plan 2.x: a region is 6 to 12 hours)
QUEST_SESSIONS = {'main_path': 8, 'completionist': COMPLETE_SESSIONS}  # SIM: a region's quest Ember is paid over its first sessions
SELL_SHARE = 0.5  # SIM: half of gear drops are sold (F_PRICE_SELL), the rest dismantled or kept
DEATH_P, LOST_P = 0.3, 0.3  # SIM: deaths per session; share of deaths whose Shard-ghost is not recovered (loses 50%, ECOF_DEATH)

BOSSES = {}
for r in rd('data/actors/bosses.csv'):
    lt = next((t.split()[0] for t in r['Drops (item refs)'].split('; ') if t.startswith('ITM_LT_BOSS')), None)
    BOSSES[r['ACT_ID']] = dict(cls=r['Class'], reg=r['Region'], lvl=int(r['Level']), ember=int(r['Ember reward']), lt=lt)
SITE = {g: [b for b, v in BOSSES.items() if v['cls'] == 'Site' and v['reg'] == g] for g in ORDER}
SB = {v['reg']: b for b, v in BOSSES.items() if v['cls'] == 'Shard-bearer'}
ONCE = [b for b, v in BOSSES.items() if v['cls'] in ('Field', 'Citadel', 'Shard-bearer', 'Undervault')]

# Compile loot rows: (kind, payload, qmin, qmax, chance, gate, gearmod)
EMB, SUB, GEAR, SHB, SEAL, POU, ITEM, SKIP = range(8)
def cat(e):
    p = e.split('_')
    return {'MAT': 'mat_' + p[2].lower(), 'SET': 'set_piece', 'ART': 'weapon_art', 'CON': 'consumable', 'SHB': 'shardborn'}.get(p[1], p[1].lower())
def quest_ember(route):
    # Main path takes Main quests only; completionist takes all. Lantern Hold quests split over the 6 regions plus the hub, Undervault over REG_04-06.
    out = Counter()
    for q in rd('data/world/quests.csv'):
        if not q['ember'].strip() or (route == 'main_path' and q['kind'] != 'Main quest'): continue
        regs = ORDER if q['region'] == 'REG_HUB' else ORDER[3:6] if q['region'] == 'REG_U' else [q['region']]
        for g in regs: out[g] += float(q['ember']) / len(regs)
    return out
QUESTS = {k: quest_ember(k) for k in QUEST_SESSIONS}
PRICE = [float(r['price_mult']) for r in rd('data/items/rarities.csv')]
def sell_values():
    # F_PRICE_SELL = floor(buy x 0.25), buy = base_value x price_mult x (1 + 0.05 u); pool = gear first found at or before the region
    rank = {g: i for i, g in enumerate(ORDER + ['REG_END'])}
    items = [(rank.get(r['first_region'], 7), float(r['base_value'] or 0)) for f in ('weapons_melee', 'weapons_firearm', 'armor_pieces')
             for r in rd(f'data/items/{f}.csv')]
    out = {}
    for g, (_, lo, hi, *_) in ((r['region_id'], list(map(int, (0, r['drop_upg_min'], r['drop_upg_max'])))) for r in rd('data/items/drop_rarity_by_region.csv')):
        pool = [b for k, b in items if k <= rank[g]]
        out[g] = [sum(pool) / len(pool) * m * (1 + 0.05 * (lo + hi) / 2) * 0.25 for m in PRICE]
    return out
SELL = sell_values()

def compile_tables():
    T = defaultdict(list)
    for r in rd('data/items/loot_tables.csv'):
        T[r['table_id']].append(r)
    out = {}
    for tid, rows in T.items():
        weighted = any(r['condition'] == 'weighted pick' for r in rows)
        rr = []
        for r in rows:
            e, c, ch = r['entry'], r['condition'], float(r['chance_pct'])
            gate = 2 if c.startswith('first kill;') else 1 if c.startswith('first kill per character') else 0
            mod = 'boss' if 'boss: rarity' in c else 'vault' if 'VAULT:' in c else 'elite' if 'elite weight' in c else ''
            if e == 'ITM_CUR_EMBER':
                m = re.search(r'qty_max: x([\d.]+)', r.get('notes', ''))  # m_numeric moves text quantities to notes
                rr.append((EMB, float(m.group(1)) if m else 0, 0, 0, ch, gate, mod))
            elif e == 'nothing' or e.startswith('ITM_AMO') or e.startswith('POOL'):
                rr.append((SKIP, 0, 0, 0, ch, gate, mod))
            else:
                kind = (GEAR if e.startswith('ITM_LT_GEAR') else SUB if e.startswith('ITM_LT_') else SHB if e.startswith('ITM_SHB')
                        else SEAL if e == 'ITM_CUR_SEALS' else POU if e in POUCH else ITEM)
                payload = e if kind in (SUB, GEAR) else POUCH.get(e) if kind == POU else cat(e)
                rr.append((kind, payload, int(r['qty_min']), int(r['qty_max']), ch, gate, mod))
        cum, t = [], 0
        for x in rr: t += x[4]; cum.append(t)
        out[tid] = (weighted, rr, cum)
    return out
TABLES = compile_tables()

def rarity_cum(reg, mod, elite):
    w = DROP_RAR[reg][:]
    w[4] = 0  # ITM_F_DROP_RARITY: Shardborn only from tables with allow_shardborn=1; no table sets it
    k = 4 if mod == 'boss' else 2 if (mod == 'elite' and elite) else 1
    w[2:] = [x * k for x in w[2:]]
    if mod == 'vault': w[0] = w[1] = 0
    c, s = [], 0
    for x in w: s += x; c.append(s)
    return c
CUM = {}
PLAIN = dict(first=True, elite=False)  # context for chests, crates, breakables and nodes

class Run:
    def __init__(self, seed, route):
        self.route, self.ri = route, 0
        self.r = random.Random(seed); self.pace = self.r.triangular(0.8, 1.25, 1.0); self.L = 1; self.bank = 0.0; self.hours = 0.0
        self.st = Counter(); self.emb = Counter(); self.killed = set(); self.line = []; self.entry = {}; self.exit = {}; self.bosskill = {}

    def earn(self, reg, src, e):
        self.st[reg, 'ember_' + src] += e; self.emb[reg] += e

    def roll(self, tid, reg, ctx, sreg=None):
        sreg = sreg or reg
        weighted, rows, cum = TABLES[tid.replace('<region>', sreg)]
        r, st = self.r, self.st
        picks = [rows[bisect(cum, r.random() * cum[-1])]] if weighted else [x for x in rows if x[4] >= 100 or r.random() * 100 < x[4]]
        for kind, p, a, b, _, gate, mod in picks:
            if gate and not ctx['first'] and (gate == 2 or r.random() >= 0.1): continue
            if kind == EMB:
                if p:
                    self.earn(reg, 'kills', ember_drop(ctx['el'], p) * (0.25 if self.L - ctx['el'] >= 10 else 1))
                else: self.earn(reg, 'bosses', ctx['boss_ember'])
                continue
            if kind == SKIP: continue
            q = r.randint(a, b)
            if kind == SUB:
                for _ in range(q): self.roll(p, reg, ctx, sreg)
            elif kind == GEAR:
                greg = p.rsplit('_', 2)[-2] + '_' + p.rsplit('_', 1)[-1] if '<region>' not in p else sreg
                key = (greg, mod, ctx['elite'])
                c = CUM.get(key) or CUM.setdefault(key, rarity_cum(greg, mod, ctx['elite']))
                for _ in range(q):
                    k = bisect(c, r.random() * c[-1]); st[reg, 'gear_' + RAR[k]] += 1
                    if r.random() < SELL_SHARE: self.earn(reg, 'selling', SELL[greg][k])
            elif kind == POU: self.earn(reg, 'chests', p * q)
            elif kind == SEAL: st[reg, 'seals'] += q
            else: st[reg, p] += q

    def fight(self, comp, reg):
        lo, hi = BAND[reg]
        for role, n in comp:
            for _ in range(n):
                el = min(hi, max(lo, self.L + self.r.randint(-1, 1)))
                self.roll(f'ITM_LT_{self.r.choice(FACTIONS)}_{ROLE[role]}', reg, dict(el=el, first=True, elite=role in ('Heavy', 'Leader')))
                self.st[reg, 'kills'] += 1

    def boss(self, b, reg):
        v = BOSSES[b]; first = b not in self.killed; self.killed.add(b)
        if first: self.bosskill[b] = self.L
        if v['lt']: self.roll(v['lt'], reg, dict(el=v['lvl'], first=first, elite=True, boss_ember=v['ember']), v['reg'] if v['reg'] in DROP_RAR else reg)
        else: self.earn(reg, 'bosses', v['ember'])

    def region(self):
        if self.route == 'completionist':
            g = ORDER[self.ri]
            if g != 'REG_Q' and SB[g] in self.killed and self.st[g, 'sessions'] >= COMPLETE_SESSIONS: self.ri += 1
            return ORDER[self.ri]
        i = max(j for j, g in enumerate(ORDER) if BAND[g][0] <= self.L)
        return ORDER[i] if ORDER[i] != 'REG_Q' or 'ACT_BOSS_HOLLOWTWINS' in self.killed else 'REG_06'

    def session(self):
        reg = self.region(); r = self.r
        if reg not in self.entry: self.entry[reg] = self.L
        before = self.emb[reg]
        pending = sorted((BOSSES[b]['lvl'], b) for b in ONCE if b not in self.killed and BOSSES[b]['lvl'] <= self.L + 1
                         and (BOSSES[b]['reg'] == 'REG_U' or ORDER.index(BOSSES[b]['reg']) <= ORDER.index(reg)))
        for enc in SESSION:
            if enc == 'ENC_ELITE' and pending: self.boss(pending[0][1], reg); continue
            self.fight(ENC[enc], reg)
            if enc == 'ENC_CAMP': self.roll(f'ITM_LT_SMALLCHEST_{reg}', reg, PLAIN)
            if enc == 'ENC_SITE':
                self.roll(f'ITM_LT_SHARDCRATE_{reg}', reg, PLAIN)
                if SITE[reg]: self.boss(SITE[reg][self.st[reg, 'sessions'] % len(SITE[reg])], reg)
        if self.st[reg, 'vaults'] < VAULTS:
            self.st[reg, 'vaults'] += 1; self.fight(ENC['ENC_CHOIRVAULT'], reg)
            self.roll(f'ITM_LT_VAULT_{reg}', reg, PLAIN)
        for _ in range(BREAKS): self.roll(f'ITM_LT_BREAKABLE_{reg}', reg, PLAIN)
        for t in r.sample(NODE_TABLES, NODES): self.roll(t, reg, PLAIN)
        f = FLOW[reg]; inflow = float(f['ember_in_per_hour'])
        if self.st[reg, 'sessions'] < QUEST_SESSIONS[self.route]: self.earn(reg, 'quests', QUESTS[self.route][reg] / QUEST_SESSIONS[self.route])
        earned = self.emb[reg] - before
        self.bank += earned * (float(f['sink_kindle_levels']) + float(f['sink_death_loss'])) / inflow  # kindle share per economy_flow.csv
        if r.random() < DEATH_P and r.random() < LOST_P: self.st[reg, 'death_loss'] += self.bank / 2; self.bank /= 2
        while self.L < 100 and self.bank >= KINDLE[self.L]: self.bank -= KINDLE[self.L]; self.L += 1
        self.st[reg, 'sessions'] += 1; self.st[reg, 'hours'] += 0.5 / self.pace; self.hours += 0.5 / self.pace
        self.exit[reg] = self.L; self.line.append((self.hours, self.L))

    def play(self):
        while self.L < 80 and self.hours < HOURS_CAP: self.session()
        return self
NODE_TABLES = sorted(t for t in TABLES if t.startswith('ITM_LT_NODE'))

DROP_UPG = {r['region_id']: int(r['drop_upg_max']) for r in rd('data/items/drop_rarity_by_region.csv')}
UPG = rd('data/items/upgrade_costs.csv')
def kit_cost(u):
    need = Counter()
    for kind, n, top in (('weapon', 2, u), ('armor', 5, u // 2)):  # ITM_F_DROP_UPG: armor u = floor(weapon u / 2)
        for r in UPG:
            if r['item_kind'] == kind and int(r['to_level']) <= top:
                need[r['material'].split('_')[2].lower()] += n * int(r['qty']); need['ember'] += n * int(r['ember'])
                need['spc'] += n * ('ASCENDANT' in r['shardborn_extra'])
                need['ecof'] += n * round(150 * int(r['to_level']) ** 1.6 * 1.7)  # ECOF_UPGRADE, Rare
    return need

def new_acc(): return Counter(), [], [], defaultdict(list), defaultdict(list), defaultdict(list), defaultdict(list)
def merge(acc, part):
    acc[0].update(part[0]); acc[1].extend(part[1]); acc[2].extend(part[2])
    for d, src in zip(acc[3:], part[3:]):
        for k, v in src.items(): d[k] += v

def chunk(job):
    route, seeds = job
    agg, hrs, lv, ent, ex, bk, rh = acc = new_acc()
    for s in seeds:
        g = Run(s, route).play(); agg.update(g.st); hrs.append(round(g.hours, 1))
        levels, i, L = [], 0, 1  # level at each whole hour, one pass over the sorted session log
        for t in range(HOURS_CAP + 1):
            while i < len(g.line) and g.line[i][0] <= t: L = g.line[i][1]; i += 1
            levels.append(L)
        lv.append((g.L, levels))
        for k, v in g.entry.items(): ent[k].append(v); rh[k].append(g.st[k, 'hours'])
        for k, v in g.exit.items(): ex[k].append(v)
        for k, v in g.bosskill.items(): bk[k].append(v)
    return route, acc

def pct(xs, p):
    xs = sorted(xs); return xs[min(len(xs) - 1, int(p / 100 * len(xs)))] if xs else ''
def wr(name, rows):
    with open(os.path.join(HERE, name), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

def report(route, acc, N):
    agg, hrs, lv, ent, ex, bk, rh = acc
    out = defaultdict(list)
    for g in ORDER:
        h = agg[g, 'hours']
        if not h: continue  # region never reached on this route
        gear = sum(agg[g, 'gear_' + k] for k in RAR)
        out['drop_rates'].append({'route': route, 'region': g, 'kills_per_hour': round(agg[g, 'kills'] / h),
            'gear_per_hour': round(gear / h, 2), **{f'pct_{k.lower()}': round(100 * agg[g, 'gear_' + k] / gear, 2) for k in RAR},
            'table_pct_rare_plus': round(sum(DROP_RAR[g][2:4]), 1),
            **{f'{k}_per_hour': round(agg[g, k] / h, 2) for k in ('set_piece', 'weapon_art', 'consumable', 'mat_hull', 'mat_dust', 'mat_glass', 'mat_star', 'mat_spc', 'mat_mon')},
            'shardborn_per_run': round(agg[g, 'shardborn'] / N, 2)})
        src = {k: agg[g, 'ember_' + k] / h for k in ('kills', 'bosses', 'chests', 'quests', 'selling')}
        tot, target = sum(src.values()), float(FLOW[g]['ember_in_per_hour'])
        out['ember_by_band'].append({'route': route, 'region': g, **{f'ember_{k}_per_hour': round(v) for k, v in src.items()},
            'ember_per_hour': round(tot), 'ecof_inflow_target': round(target), 'pct_of_target': round(100 * tot / target),
            'kills_bosses_share_pct': round(100 * (src['kills'] + src['bosses']) / tot), 'target_share_pct': 65,
            'death_loss_per_hour': round(agg[g, 'death_loss'] / h)})
        out['level_vs_band'].append({'route': route, 'region': g, 'band_min': BAND[g][0], 'band_max': BAND[g][1],
            **{f'entry_level_p{p}': pct(ent[g], p) for p in (10, 50, 90)}, **{f'exit_level_p{p}': pct(ex[g], p) for p in (10, 50, 90)},
            **{f'hours_p{p}': round(pct(rh[g], p), 1) for p in (10, 50, 90)}})
        u = DROP_UPG[g]; need = kit_cost(u)  # SIM kit: 2 weapons + 5 armor pieces taken to this band's top drop level
        out['sinks'].append({'route': route, 'region': g, 'kit_upgrade_level': u, 'kit_ember_upgrade_costs_csv': need['ember'],
            'kit_ember_ecof_upgrade_rare': need['ecof'], 'smithing_budget_per_region': round(tot * h / N * float(FLOW[g]['sink_smithing']) / target),  # smithing share of simulated income
            **{f'{m}_need': need[m] for m in ('hull', 'dust', 'glass', 'star', 'spc')},
            **{f'{m}_supply_per_region': round(agg[g, 'mat_' + m] / N) for m in ('hull', 'dust', 'glass', 'star', 'spc')}})
    out['progression'] = [{'route': route, 'hour': t, **{f'level_p{p}': pct([l[t] for _, l in lv], p) for p in (10, 50, 90)}}
                          for t in range(0, int(max(hrs)) + 2)]
    out['boss_levels'] = [{'route': route, 'boss': b, 'class': v['cls'], 'region': v['reg'], 'boss_level': v['lvl'],
                           **{f'player_level_p{p}': pct(bk[b], p) for p in (10, 50, 90)}, 'median_gap': pct(bk[b], 50) - v['lvl']}
                          for b, v in BOSSES.items() if bk[b]]
    out['summary'] = [{'route': route, 'runs': N, **{f'hours_to_80_p{p}': pct(hrs, p) for p in (10, 50, 90)},
                       'runs_capped': sum(L < 80 for L, _ in lv), 'shardborn_per_run': round(sum(v for (_, k), v in agg.items() if k == 'shardborn') / N, 2),
                       'gear_per_run': round(sum(v for (_, k), v in agg.items() if k.startswith('gear_')) / N)}]
    return out

if __name__ == '__main__':
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 10000
    tables = defaultdict(list)
    accs = {route: new_acc() for route in ('main_path', 'completionist')}
    with Pool() as pool:
        for route, part in pool.imap_unordered(chunk, [(route, range(i, N, 64)) for route in accs for i in range(64)]):
            merge(accs[route], part)
    for route, acc in accs.items():
        for name, rows in report(route, acc, N).items(): tables[name] += rows
    for name, rows in tables.items(): wr(name + '.csv', rows)
    print(tables['summary'])
