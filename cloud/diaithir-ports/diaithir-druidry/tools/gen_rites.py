# S6828
# Generates data/diaithir_druidry/rites/<universe>.json: one rite per Library SPELL entry (magic.rite).
# Text is the entry's own summary (real text only). Steps are derived from hash(id) and Age tier; the
# step vocabulary is the Ascendant rite chain (feast, offer, hunt, stones, hour, coop, defend).
# Usage: python3 -I tools/gen_rites.py <content.sqlite> <library.sqlite> [out_dir]
import sqlite3, sys, json, hashlib, os, re, collections
CONTENT, LIB = sys.argv[1], sys.argv[2]
OUT = sys.argv[3] if len(sys.argv) > 3 else os.path.join(os.path.dirname(__file__), '..', 'src/main/resources/data/diaithir_druidry/rites')
SCHOOL = {'Martial':'fitech','Ki':'filid','Arcane':'fiusaichi','Stellar':'bardu','Mythic':'draeid','Grounded':'gouba','Outer':'sitichi'}
AGE = ['I','II','III','IV','V','VI','VII']
OFFER = [['minecraft:bone',16],['minecraft:iron_ingot',16],['minecraft:amethyst_shard',12],['minecraft:glow_berries',24],['minecraft:gold_ingot',12],['minecraft:lapis_lazuli',32],['minecraft:diamond',4],['minecraft:ender_eye',4],['minecraft:echo_shard',2],['minecraft:netherite_scrap',2]]
HUNT = [['minecraft:zombie',8],['minecraft:skeleton',8],['minecraft:spider',10],['minecraft:witch',3],['minecraft:blaze',5],['minecraft:enderman',4],['minecraft:wither_skeleton',4],['minecraft:warden',1]]
OGHAM = ['birch','rowan','alder','willow','ash','hawthorn','oak','holly','hazel']
HOURS = ['midnight','dawn','noon','dusk']
def h(s): return int.from_bytes(hashlib.sha256(s.encode()).digest()[:8], 'big')
def pick(pool, tier, k):  # tier raises the floor of the pool index
    lo = min(len(pool)-3, (tier-1)*(len(pool)-3)//6); return pool[lo + k % 3 if lo + k % 3 < len(pool) else lo]
def steps(i, t):
    k = h(i); n = min(6, 2 + (t+1)//2); out = []
    kinds = ['offer','hunt','hour','stones','feast','offer'][:n-1] if t < 4 else ['offer','hunt','stones','hour','feast'][:n-1]
    for j, kd in enumerate(kinds):
        s = {'step': kd}; kk = k >> (j*5)
        if kd == 'offer': it, c = pick(OFFER, t, kk); s.update(item=it, count=max(1, c*t//4 or 1))
        elif kd == 'hunt': m, c = pick(HUNT, t, kk); s.update(entity=m, count=c, radius=48)
        elif kd == 'stones': s.update(runes=[OGHAM[(kk+x) % 9] for x in range(min(9, 2+t))], order_hidden=True)
        elif kd == 'hour': s.update(window=HOURS[kk % 4])
        elif kd == 'feast': s.update(tag='diaithirbosses:offering_feast')
        out.append(s)
    if t >= 6: out.append({'step': 'coop', 'fighters': 2 + t % 2, 'solo': 'champion_token_per_absent'})
    if t >= 4: out.append({'step': 'defend', 'seconds': 60 + 15*(t-4)})
    return out
con = sqlite3.connect(f'file:{CONTENT}?mode=ro', uri=True); lib = sqlite3.connect(f'file:{LIB}?mode=ro', uri=True)
rows = con.execute("select id,tier,universe,realm,era,name,spine from content where form='SPELL' order by id").fetchall()
by = collections.defaultdict(list); miss = 0
for i, t, u, r, e, n, sp in rows:
    x = lib.execute('select summary from entry where id=?', (i,)).fetchone()
    if not x or not x[0]: miss += 1; continue
    by[u].append({'id': i, 'name': n, 'tier': t, 'age': AGE[t-1], 'school': SCHOOL.get(r, 'draeid'), 'era': e, 'spine': sp, 'text': x[0], 'steps': steps(i, t)})
os.makedirs(OUT, exist_ok=True); idx = {}
for u, rs in by.items():
    f = re.sub(r'[^a-z0-9_]', '_', u.lower()); json.dump({'universe': u, 'format': 'rite.v1', 'rites': rs}, open(f'{OUT}/{f}.json', 'w'), ensure_ascii=False, separators=(',', ':')); idx[f] = len(rs)
json.dump({'format': 'rite.v1', 'total': sum(idx.values()), 'files': idx, 'skipped_no_text': miss}, open(f'{OUT}/_index.json', 'w'), indent=1)
print(sum(idx.values()), 'rites,', len(idx), 'files,', miss, 'without text')
