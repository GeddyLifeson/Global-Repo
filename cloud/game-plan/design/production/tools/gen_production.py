"""Generates the Shardfall production tables. Run: python3 tools/gen_production.py (from design/production).
Every number not cited in sources.md is a Shardfall planning choice (3 Oct 2026). Change the inputs here, not the CSVs."""
import csv, os, re
OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GP = os.path.abspath(os.path.join(OUT, '..', '..'))
def w(name, header, rows):
    with open(os.path.join(OUT, name), 'w', newline='') as f:
        c = csv.writer(f); c.writerow(header); c.writerows(rows)

# ---------- Phases and schedule (master plan Part 4 and 5.6) ----------
# Plan counts months from project start. Shardfall choice: month 0 = Oct 2026 (research started then).
START = '2026-10'
def add(ym, m):
    y, mo = map(int, ym.split('-')); t = y*12 + mo-1 + m; return f"{t//12}-{t%12+1:02d}"
# (id, name, start month, end month, gate) -- straight from the plan
PH = [
 ('P0','Research lab',0,3,'Gate 0: research complete'),
 ('P1','Concept',3,6,'Gate 1: pitch approved, engine chosen, pre-production funded, lore bible and style guide signed off'),
 ('P2','Pre-production',6,14,'Gate 2: prototypes pass (combat, first/third-person switch, Strider, co-op)'),
 ('P3','Vertical slice',14,20,'Gate 3: slice hits its three test targets, cost estimate within 10% of budget, full production funded (Cinderreach slice)'),
 ('P4','Production, systems',20,38,'Gate 4: systems complete'),
 ('P5','Production, content',20,42,'Gate 5: content complete (runs in parallel with P4)'),
 ('P6','Alpha',42,46,'Gate 6: content complete, no blockers, fewer than 200 major bugs, playtest fun 4/5 or higher'),
 ('P7','Beta and certification',46,52,'Gate 7: certification passed on all platforms, fewer than 50 major bugs, none on the main path'),
 ('P8','Launch',52,54,'Gate 8: crash rate under 0.5% of sessions, review score 85 or higher'),
 ('P9','Live service',54,None,'Ongoing: season every 3 months, one paid expansion a year'),
]
w('schedule_phases.csv', ['phase','name','start_month','end_month','start','end','gate'],
  [(p,n,s0,e if e is not None else 'ongoing',add(START,s0),add(START,e) if e is not None else 'ongoing',g) for p,n,s0,e,g in PH])
MILESTONES = [  # plan 5.6, plus plan Part 4/8.1 beats
 ('M00',0,'Project start'),('M01',3,'Gate 0: research complete'),('M02',6,'Gate 1: pitch and engine approved'),
 ('M03',14,'Gate 2: prototypes pass'),('M04',20,'Gate 3: vertical slice approved; full production funded'),
 ('M05',36,'Public reveal trailer (about 18 months before launch, plan 8.1)'),
 ('M06',38,'Gate 4: systems complete'),('M07',42,'Gate 5: content complete'),
 ('M08',44,'Outside playtest: 200 testers under NDA, first 15 hours (plan 6.4)'),
 ('M09',45,'Gameplay deep-dive (9 months before launch)'),('M10',46,'Gate 6: alpha'),
 ('M11',48,'Age rating submissions (ESRB, PEGI, IARC and others)'),
 ('M12',49,'Closed online beta, 50,000 players (plan 7.2)'),('M13',51,'Preview events (3 months before launch)'),
 ('M14',52,'Gate 7: certification passed; day-one patch ready'),('M15',54,'Launch (creator early access 2 weeks before)'),
 ('M16',54,'Patch 1.01 within 2 weeks; patch 1.1 within 6 weeks'),
 ('M17',57,'First season; Forgeframe on PC'),('M18',60,'Forgeframe on consoles'),('M19',66,'First expansion'),
]
w('milestones.csv', ['milestone_id','month','calendar','milestone'], [(i,m,add(START,m),t) for i,m,t in MILESTONES])

# ---------- Team (plan 5.1 totals: 8, 20, 60, 110, 280 peak, 260, 120) ----------
# Department splits are Shardfall choices; totals per phase are the plan's.
DEPT_COST = {'Leadership':22000,'Production':14000,'Design':13500,'Engineering':16000,'Online/Backend':17000,
 'Art':12500,'Animation':13000,'Audio':12500,'Narrative':12500,'UX/UI':13000,'QA':8000,
 'Live ops/Analytics':14000,'User research and analytics':13000,'Marketing/Community':12000,'IT/HR/Finance':11000}
COLS = ['P0','P1','P2','P3','P4+P5','P6','P7','P8','P9 (per year)']
COL_MONTHS = [3,3,8,6,22,4,6,2,12]
PLAN_TOT = [8,20,60,110,280,260,260,260,120]
TEAM = {  # P0 P1 P2 P3 P45 P6 P7 P8 P9
 'Leadership':       [3,4,5,6,6,6,6,6,4],
 'Production':       [1,2,5,8,16,16,16,14,8],
 'Design':           [3,4,8,13,36,24,24,22,10],
 'Engineering':      [1,4,14,19,40,36,40,48,15],
 'Online/Backend':   [0,0,4,6,15,15,16,16,10],
 'Art':              [0,4,8,18,68,28,26,24,14],
 'Animation':        [0,0,4,7,21,12,10,10,8],
 'Audio':            [0,0,2,6,12,10,8,8,6],
 'Narrative':        [0,1,2,4,10,8,6,6,4],
 'UX/UI':            [0,0,1,5,6,6,7,6,4],
 'QA':               [0,0,0,2,18,60,60,60,6],
 'Live ops/Analytics':[0,0,0,0,0,0,0,2,2],
 'User research and analytics':[0,1,7,13,24,29,29,24,21],  # design/research/research_team.csv; heads moved from Design, Engineering, Art, UX/UI, QA and Live ops so plan totals hold; QA stays 60 in alpha and beta (plan 5.1)
 'Marketing/Community':[0,0,0,1,4,6,8,10,6],
 'IT/HR/Finance':    [0,0,0,2,4,4,4,4,2],
}
tot = [sum(v[i] for v in TEAM.values()) for i in range(9)]
assert tot == PLAN_TOT, tot
w('team_by_phase.csv', ['department']+COLS+['loaded_cost_per_person_month_usd'],
  [[d]+v+[DEPT_COST[d]] for d,v in TEAM.items()]+[['TOTAL (plan 5.1)']+tot+['']])
# Production-phase structure from plan 5.1: six region teams, systems team of 40, boss team of 15, cinematics
w('org_chart_production.csv', ['unit','count','headcount','reports_to','makeup'], [
 ('Directors (game, creative, art, tech, audio, executive producer)',1,6,'Studio head','Plan 5.1 leadership'),
 ('Region teams',6,150,'Game director','25 each: region lead, 4 level designers, 3 quest designers, 1 writer, 7 environment artists, 1 prop artist, 1 lighting artist, 1 tech artist, 1 VFX artist, 1 sound designer, 1 animator, 3 embedded QA'),
 ('Systems team',1,40,'Tech director + design director','Combat, AI, progression, loot, economy, co-op, save, UI engineering; 12 designers, 28 engineers'),
 ('Boss team',1,15,'Game director','44 bosses plus Hush (data/actors/bosses.csv); 8 weeks per major boss, 4 per site boss (plan 5.4): 4 designers, 4 animators, 3 character artists, 2 VFX, 1 AI engineer, 1 sound designer'),
 ('Cinematics',1,12,'Creative director','About 45 minutes in-engine: opening, act transitions, three endings (plan 5.7)'),
 ('Online and backend',1,15,'Tech director','Dedicated servers, matchmaking, loot validation, mod hub'),
 ('UX/UI',1,8,'Creative director','UX research, UI design, accessibility'),
 ('Central audio and music',1,4,'Audio director','Music, VO direction, mix'),
 ('Central QA and automation',1,4,'Executive producer','Test bots, crash triage, cert pre-checks'),
 ('Production (producers, outsourcing, localization)',1,16,'Executive producer','Includes outsourcing partner managers'),
 ('Central art (character lead, art outsourcing direction)',1,2,'Art director',''),
 ('Live ops and analytics',1,2,'Executive producer','Telemetry, balance simulation'),
 ('Marketing and community',1,2,'Executive producer','Grows from P6'),
 ('Studio services (IT, HR, finance)',1,4,'Studio head',''),
 ('TOTAL',None,280,'',''),
])
MONTHS = dict(zip(COLS, COL_MONTHS))
# Plan 5.1: Region 1 first as the template, then 2 and 3 in parallel, then 4 to 6; about 7 months each
REG = [('Region 1 (Cinderreach, template)',20,27),('Region 2',27,34),('Region 3',27,34),('Region 4',34,41),('Region 5',34,41),('Region 6',34,41),
       ('Orbital act (the Quiet)',34,42),('Citadels (one per region, built inside each region slot)',20,41)]
w('region_schedule.csv',['work','start_month','end_month','start','end','source'],[(n,a,b,add(START,a),add(START,b),'Plan 5.1, 5.2, 5.3') for n,a,b in REG])
# ---------- Asset throughput / outsourcing ----------
# (category, count, unit, per artist-month, outsource share, source of count)
TP = [
 ('Environment meshes',1825,'meshes',6,0.60,'xlsx Assets'),
 ('Environment materials',400,'materials',10,0.40,'xlsx Assets'),
 ('Environment setpieces',216,'setpieces',1,0.30,'xlsx Assets'),
 ('Levels / interiors (build + dress)',132,'levels',0.25,0.20,'xlsx Assets'),
 ('Hero/NPC characters',88,'characters',0.5,0.50,'xlsx Assets'),
 ('Character parts (modular)',550,'parts',4,0.70,'xlsx Assets'),
 ('Armor sets',91,'sets',0.5,0.60,'xlsx Assets'),
 ('Enemy types (20 archetypes + variants)',60,'types',0.4,0.50,'Plan 4.4 (xlsx lists 72; plan wins)'),
 ('Creatures',24,'creatures',0.3,0.40,'xlsx Assets'),
 ('Bosses',40,'bosses',0.2,0.20,'xlsx Assets'),
 ('Weapon models',289,'models',2,0.70,'xlsx Assets'),
 ('Item models (non-weapon)',620,'items',6,0.80,'xlsx Assets (500+120)'),
 ('Vehicles + variants',18,'vehicles',0.25,0.50,'xlsx Assets'),
 ('Animation clips (gameplay)',858,'clips',8,0.50,'xlsx Assets'),
 ('Cinematics',45,'minutes',1.5,0.50,'Plan 5.7 (about 45 minutes; xlsx lists 60 scenes)'),
 ('VFX effects',1281,'effects',4,0.35,'xlsx VFX tab'),
 ('SFX files incl. variations',4810,'files',60,0.30,'xlsx SFX tab'),
 ('Ambience beds',120,'beds',4,0.20,'xlsx Assets'),
 ('UI visual assets',1294,'assets',15,0.40,'xlsx Assets UI rows'),
 ('Concept art (Art direction rows)',164,'sheets',3,0.30,'xlsx Assets'),
]
rows = []; tot_am = tot_out = 0
for c,n,u,t,o,src in TP:
    am = n/t; out = am*o; tot_am += am; tot_out += out
    rows.append([c,n,u,t,round(am),f"{int(o*100)}%",round(out),round(am-out),src])
rows.append(['TOTAL','','','',round(tot_am),'',round(tot_out),round(tot_am-tot_out),''])
w('asset_throughput.csv', ['category','count','unit','per_artist_month','artist_months','outsourced_share','outsourced_artist_months','internal_artist_months','count_source'], rows)

# ---------- Localization ----------
# Each str_id counts once; strings_data.csv already holds the narrative, quest and dialogue text, so no planned buckets are added on top
STR_W = {}
for f in ('data/ui/strings.csv', 'data/ui/strings_data.csv'):
    for r in csv.DictReader(open(os.path.join(GP, f))):
        STR_W.setdefault(r['str_id'], (f, len(re.findall(r"[\w']+", r['text_en']))))
ui_w = sum(n for f, n in STR_W.values() if f.endswith('/strings.csv')); data_w = sum(n for _, n in STR_W.values()) - ui_w
VO_LINES = 60000
SRC = ui_w + data_w
# Plan 7.4: text in 12 languages, voice in 5 (both counts include English; Shardfall choice of which ones)
LANG = [('en-US','EN','Source','VO'),('fr-FR','FR','Tier 1','VO'),('de-DE','DE','Tier 1','VO'),('es-ES','ES','Tier 1','VO'),
 ('ja-JP','JA','Tier 1','VO'),('pt-BR','PT-BR','Tier 2','Text'),('it-IT','IT','Tier 2','Text'),('pl-PL','PL','Tier 2','Text'),
 ('ru-RU','RU','Tier 2','Text'),('ko-KR','KO','Tier 2','Text'),('zh-Hans','ZH-S','Tier 2','Text'),('zh-Hant','ZH-T','Tier 2','Text')]
assert len(LANG)==12 and sum(1 for l in LANG if l[3]=='VO')==5
TR_RATE = 0.14; LQA_RATE = 0.03; VO_LINE = 14
rows = []; loc_total = 0
for code,short,tier,kind in LANG:
    if tier=='Source':
        cost = vo_cost = 0
    else:
        cost = SRC*(TR_RATE+LQA_RATE); vo_cost = VO_LINES*VO_LINE if kind=='VO' else 0
    loc_total += cost+vo_cost
    rows.append([code,short,tier,kind,SRC,round(cost),round(vo_cost),round(cost+vo_cost)])
rows.append(['TOTAL','','','','',round(sum(r[5] for r in rows)),round(sum(r[6] for r in rows)),round(loc_total)])
w('localization.csv', ['locale','short','tier','scope','source_words','text_cost_usd','vo_cost_usd','total_usd'], rows)
w('localization_wordcount.csv', ['bucket','words','source'],
  [('UI strings',ui_w,'data/ui/strings.csv (measured)'),('Data strings (names, descs, lore, quests, dialogue)',data_w,'data/ui/strings_data.csv (measured)'),('TOTAL',SRC,'')])

# ---------- Budget (plan 5.2 shares; staff cost computed from team_by_phase) ----------
DEV = COLS[:8]
staff = {c: sum(TEAM[d][i]*DEPT_COST[d] for d in TEAM)*COL_MONTHS[i] for i,c in enumerate(COLS)}
staff_dev = sum(staff[c] for c in DEV)
DEV_TOTAL = staff_dev/0.55          # plan: staff is 55% of the development budget
SHARE = [('Outsourced art and animation',.15,[0,0,.02,.06,.72,.15,.05,0]),
 ('Voice, music and motion capture',.08,[0,0,.03,.10,.70,.12,.05,0]),
 ('Engine, tools and licenses',.05,[.02,.05,.15,.12,.45,.08,.10,.03]),
 ('Servers and backend through year one',.05,[0,0,0,.03,.12,.05,.20,.60]),
 ('QA, certification and localization',.07,[0,0,.01,.04,.30,.25,.38,.02]),
 ('Contingency',.05,[0,0,.05,.10,.50,.15,.15,.05])]
def k(v):   # thousands; the total is the sum of the rounded cells so rows and columns add up
    r=[round(x/1e3) for x in v]; return r+[sum(r)]
def colsum(rs): return [sum(r[i] for r in rs) for i in range(2,11)]
rows=[['Staff: '+d,'']+k([TEAM[d][i]*DEPT_COST[d]*COL_MONTHS[i] for i in range(8)]) for d in TEAM]
rows.append(['Staff subtotal','55%']+colsum(rows))
lines={}
for name,sh,spr in SHARE:
    v=[DEV_TOTAL*sh*x for x in spr]; lines[name]=sum(v)
    rows.append([name,f"{int(sh*100)}%"]+k(v))
rows.append(['DEVELOPMENT TOTAL','100%']+colsum(rows[:len(TEAM)]+rows[len(TEAM)+1:]))
MKT = DEV_TOTAL*0.60   # plan: marketing is separate, 50-100% of dev; Shardfall choice 60%
mspr=[0,0,0,0,.20,.20,.30,.30]
rows.append(['Marketing (separate, 60% of dev)','']+k([MKT*x for x in mspr]))
w('budget_by_phase.csv', ['line (USD thousands)','plan_share']+DEV+['total'], rows)
# Consumer products and transmedia (design/licensing/team.csv). Publishing staff, outside the plan 5.1 dev headcount.
CP = [('Head of Consumer Products',1,30,18000),('Licensing manager',1,36,13000),('Transmedia producer',1,36,14000),
      ('Product development and approvals coordinator',2,40,10000),('Supply chain manager',1,40,13000),('Brand artist',1,32,12000)]
WIN = [(0,3),(3,6),(6,14),(14,20),(20,42),(42,46),(46,52),(52,54)]
cpv=[sum(h*c*max(0,b-max(a,st)) for _,h,st,c in CP) for a,b in WIN]
rows.append(['Consumer products and transmedia team (7 staff, licensing/team.csv; outside plan 5.1)','publishing']+k(cpv))
CE_UNITS, CE_COST = 60000, 91.60
cev=[0]*6+[CE_UNITS*CE_COST,0]  # production starts month 48 (licensing/manufacturing_schedule.csv)
rows.append(["Collector's Edition run: 60,000 units at $91.60 (licensing/ce_bill_of_materials.csv); working capital recouped from sales",'publishing']+k(cev))
w('team_by_phase.csv', ['department']+COLS+['loaded_cost_per_person_month_usd'],
  [[d]+v+[DEPT_COST[d]] for d,v in TEAM.items()]+[['TOTAL (plan 5.1)']+tot+['']]+
  [['Consumer products (publishing, outside plan total; licensing/team.csv)']+[sum(h for _,h,st,_ in CP if st<b) for a,b in WIN]+[7]+['10000-18000']])
w('budget_by_phase.csv', ['line (USD thousands)','plan_share']+DEV+['total'], rows)
cp_live = sum(h*c*12 for _,h,_,c in CP)
live_staff = staff['P9 (per year)']; live_host = 6e6
w('budget_live_per_year.csv', ['line','usd_thousands','basis'], [
 ('Live team staff (120 people, plan 5.1)',round(live_staff/1e3),'team_by_phase.csv P9 column x 12 months'),
 ('Servers and backend after year one',round(live_host/1e3),'Shardfall choice'),
 ('Outsourced art for seasons and expansion',round(4e6/1e3),'Shardfall choice'),
 ('Marketing for seasons and expansion',round(8e6/1e3),'Shardfall choice'),
 ('Consumer products and transmedia team (7)',round(cp_live/1e3),'licensing/team.csv'),
 ('TOTAL',round((live_staff+live_host+12e6+cp_live)/1e3),'')])
VENDOR = 8000
summary = {'dev_total_M':round(DEV_TOTAL/1e6,1),'staff_M':round(staff_dev/1e6,1),'contingency_M':round(lines['Contingency']/1e6,1),
 'marketing_M':round(MKT/1e6,1),'live_per_year_M':round((live_staff+live_host+12e6+cp_live)/1e6,1),'consumer_products_team_to_launch_M':round(sum(cpv)/1e6,2),'ce_run_M':round(CE_UNITS*CE_COST/1e6,2),
 'peak_internal':max(tot),'asset_artist_months':round(tot_am),'outsourced_asset_am':round(tot_out),
 'outsourcing_budget_M':round(lines['Outsourced art and animation']/1e6,1),
 'vendor_months_affordable':round(lines['Outsourced art and animation']/VENDOR),
 'src_words':SRC,'ui_w':ui_w,'data_w':data_w,'loc_M':round(loc_total/1e6,1)}
with open(os.path.join(OUT,'summary.txt'),'w') as f:
    for k,v in summary.items(): f.write(f"{k}={v}\n")
print(summary)
