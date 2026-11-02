"""Generate design/research/*.csv. Run: python3 design/research/tools/gen_research.py
Plan = master plan doc (wins every conflict). SC = Shardfall choice (invented, playtests tune it).
Month 0 = Oct 2026 (production/README.md)."""
import csv, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GP = os.path.dirname(os.path.dirname(R))

def cal(m):
    y, mo = divmod(9 + int(m), 12)
    return f"{2026 + y}-{mo + 1:02d}"

def w(name, head, rows):
    with open(os.path.join(R, name), "w", newline="") as f:
        c = csv.writer(f); c.writerow(head); c.writerows(rows)
    print(name, len(rows))

PH = {0: (0, 3), 1: (3, 6), 2: (6, 14), 3: (14, 20), 4: (20, 38), 5: (20, 42), 6: (42, 46), 7: (46, 52), 8: (52, 54), 9: (54, 66)}

# ---------- research team (maps audit GEN-184..189) ----------
team = [
 ("RT_LEAD", "Insights manager / research lead", "GEN-188", [0,1,1,1,1,1,1,1,1], "Owns the research log, gate readouts, priorities"),
 ("RT_UXR", "User researcher", "GEN-184", [0,0,2,3,5,5,5,5,3], "Lab and remote studies, surveys, interviews"),
 ("RT_COORD", "Playtest coordinator", "GEN-185", [0,0,1,2,3,4,4,3,2], "Recruiting, NDAs and consent, scheduling, lab ops"),
 ("RT_DS", "Data scientist", "GEN-186", [0,0,0,1,2,3,3,3,3], "Models, simulations, experiments"),
 ("RT_ANA", "Game analyst / statistician", "GEN-187", [0,0,1,1,3,4,4,4,4], "KPIs, dashboards, test analysis"),
 ("RT_DE", "Analytics engineer", "GEN-159 (tech)", [0,0,0,1,2,2,2,2,2], "Warehouse models, event QA; pairs with tech telemetry engineer"),
 ("RT_PRO", "Pro team (expert playtesters, staff)", "GEN-189", [0,0,2,4,8,10,10,6,6], "See pro_team.csv"),
]
phs = ["P0", "P1", "P2", "P3", "P4+P5", "P6", "P7", "P8", "P9 (per year)"]
rows = []
tot = [0]*9
for i, n, g, hc, note in team:
    rows.append([i, n, g] + hc + [11000 if i == "RT_PRO" else 13500, note, "SC"])
    tot = [a + b for a, b in zip(tot, hc)]
rows.append(["RT_TOTAL", "Total research and analytics", "", *tot, "", "Production's team_by_phase.csv carries UX/UI and Live ops/Analytics only; see conflicts.csv RC_01", "SC"])
w("research_team.csv", ["role_id", "role", "audit_row", *phs, "loaded_cost_per_person_month_usd", "notes", "source"], rows)

# ---------- methods ----------
methods = [
 ("METH_LAB", "Moderated lab session", "Why players struggle; first-time understanding", "8 to 40 per round", "2 to 4 h", "Lab stations, 3 cameras, eye tracker on 2 stations, telemetry overlay", "Issue list ranked by severity x frequency"),
 ("METH_THINK", "Think-aloud", "What players expect versus what happens", "5 to 8 per build", "60 to 90 min", "Lab, mic, facecam", "Confusion points with timestamps"),
 ("METH_BLIND", "Blind first-play test", "Shortcut discovery, landmark pull, path finding", "5 to 20", "1 to 3 h", "Lab or remote, path heatmap", "Discovery rates, path traces"),
 ("METH_RITE", "RITE (rapid iterative testing)", "Fix tutorial and UI issues inside one week", "1 to 2 a day for 5 days", "45 min", "Lab, designer on call, hot data patch", "Fixed issue log per day"),
 ("METH_SURVEY", "Survey (in-build and exit)", "Fun, would buy, clarity, NPS", "All testers", "2 to 10 min", "In-build popups, web form", "survey_items.csv scores"),
 ("METH_DIARY", "Diary study (remote, multi-week)", "Long-play motivation, churn reasons, co-op habits", "30 for 4 weeks", "Daily 5 min", "Remote build, diary app", "Weekly motivation curve, quit reasons"),
 ("METH_INTERVIEW", "Semi-structured interview", "Motivation, build identity, story understanding", "6 to 12", "45 min", "Video call or lab", "Coded themes"),
 ("METH_CARD", "Card sort and tree test", "Menu and inventory structure", "15 to 30", "20 min", "Online tool", "Menu tree fixes"),
 ("METH_SUS", "Usability scale (10-item SUS-style)", "Menu and HUD usability score", "Per UI test", "3 min", "Survey", "Score out of 100"),
 ("METH_EYE", "Eye tracking", "HUD read, telegraph read, popup notice", "12 per test", "30 min", "Tobii-class screen tracker", "Gaze heatmaps, time to first fixation"),
 ("METH_BIO", "Galvanic skin response (optional)", "Tension in boss fights and Citadel set pieces", "12", "60 min", "Wrist sensor", "Arousal curve by event"),
 ("METH_TELEM", "Telemetry analysis", "Where players die, quit, stall; build choices", "All", "Continuous", "Warehouse, dashboards.csv", "KPI readouts"),
 ("METH_HEAT", "Spatial heatmaps", "Death, quit, stall and path density per km²", "All", "Continuous", "Level overlay in editor", "Heatmap per level"),
 ("METH_FUNNEL", "Funnel analysis", "Quest, tutorial and store drop-off", "All", "Continuous", "Warehouse", "Drop-off per step"),
 ("METH_AB", "A/B experiment", "Choose between two tunings with real players", "Power-calculated", "1 to 4 weeks", "Live config (tech/02)", "Effect size with 95% CI"),
 ("METH_SIM", "Balance simulation", "Level against band, Ember, drops (plan 5.5)", "10,000 runs a night", "Overnight", "Simulation scripts (design/simulation)", "Charts against targets"),
 ("METH_EXPERT", "Expert review (pro team)", "Exploits, frame data, PvP balance, speed paths", "Pro team", "Per build", "Debug build, frame counter", "Exploit and balance tickets"),
 ("METH_ACCESS", "Accessibility session with disabled players", "Can players finish tasks with each preset", "8 to 12 per round", "90 min", "Lab with adaptive controllers", "Task success per preset"),
 ("METH_CULT", "Cultural and language review session", "Clarity of text and lore in each locale", "3 per language", "2 h", "Localized build", "Locale issue list"),
 ("METH_SOCIAL", "Social listening", "Sentiment and top complaints after launch", "Public posts", "Weekly", "Social listening tool", "Weekly top 10 topics"),
 ("METH_BENCH", "Competitive benchmark sessions", "Same tasks in Shardfall and a reference game", "12", "2 h", "Lab, bought copies (plan 0.1)", "Relative clarity and fun"),
]
w("methods.csv", ["method_id", "method", "answers", "sample", "session_length", "tools", "output"], [list(m) + ["SC"] for m in methods])

# ---------- playtests ----------
pts = []
def pt(phase, m0, m1, name, kind, players, seg, content, meth, measure, target, kpis, gate, step, src):
    pid = f"PT_{len(pts)+1:03d}"
    pts.append([pid, phase, m0, m1, cal(m0), name, kind, players, seg, content, meth, measure, target, kpis, gate, step, src])

pt(0, 0, 3, "Source-game sessions, one expert and one newcomer per game", "internal", "2 designers x 6 games", "Staff", "First 10 h and a late segment of each source game", "METH_THINK", "Confusion points with timestamps", "All six logged", "", "Gate 0", "0.2", "plan")
pt(0, 2, 3, "Benchmark baseline: deaths understood in source games", "lab", 12, "SEG_SOULS; SEG_FPS", "Dark Souls, Elden Ring, Halo first hour", "METH_BENCH; METH_SURVEY", "Death clarity in reference games", "Baseline recorded for KPI_R01", "KPI_R01", "Gate 0", "0.2", "SC")
pt(1, 4, 5, "Pitch reviews with outside designers", "expert", "3 reviews", "Outside designers", "Pitch, concept doc, 90 s video", "METH_INTERVIEW", "Recorded objections", "All objections answered", "", "Gate 1", "1.1", "plan")
pt(1, 5, 6, "Concept video and pillar survey", "remote", 200, "SEG_ALL", "90 s concept video", "METH_SURVEY", "Appeal and would-buy on concept", "60% top-two-box appeal", "KPI_R42", "Gate 1", "1.1", "SC")
pt(2, 7, 14, "Combat prototype, twice a week", "internal", 8, "Staff", "Gray-box arena, sword, rifle, spell, 3 enemies", "METH_SURVEY; METH_TELEM", "Deaths per minute, TTK, I knew why I died", "80% yes", "KPI_R01; KPI_R02; KPI_R03", "Gate 2", "2.1", "plan")
pt(2, 9, 11, "Melee and gun parity", "lab", 12, "SEG_SOULS; SEG_FPS", "Melee-only and gun-only loadouts, 3 arenas", "METH_LAB; METH_TELEM", "Clear time gap", "Under 15%", "KPI_R04", "Gate 2", "2.2", "plan")
pt(2, 8, 10, "First- and third-person switch feel", "lab", 16, "SEG_FPS; SEG_RPG", "Arena, aim switch on and fallback over-shoulder", "METH_LAB; METH_SURVEY", "Switch comfort 1 to 5; nausea report", "4 of 5; under 5% discomfort", "KPI_R44", "Gate 2", "risk 5.4", "SC")
pt(2, 9, 11, "Traversal: Strider and skimmer", "internal", 8, "Staff", "2 km² gray-box terrain", "METH_TELEM", "Time between new things seen on mount", "40 to 60 s", "KPI_R09", "Gate 2", "2.3", "plan")
pt(2, 10, 12, "Progression prototype review", "expert", "Pro team", "Pro team", "4 skills, 2 trees, 3 h sim log", "METH_SIM; METH_EXPERT", "Farmable actions found", "Zero untargeted XP farms", "KPI_R17", "Gate 2", "2.4", "plan")
pt(2, 11, 13, "Site and Citadel quarter, blind", "lab", 10, "SEG_ALL", "Cave with shortcut, 30 min Citadel quarter", "METH_BLIND; METH_THINK", "Each shortcut found; feeling on opening", "60% find each shortcut (SC, from 5.2)", "KPI_R10", "Gate 2", "2.5", "plan")
pt(2, 12, 13, "Co-op latency test", "internal", 8, "Staff", "2-player arena at 50, 100, 150 ms", "METH_TELEM; METH_SURVEY", "Hit disagreement, feel 1 to 5", "Works at 150 ms; feel 4 of 5 at 100 ms", "KPI_R28", "Gate 2", "2.7", "plan")
pt(2, 13, 14, "Gate 2 gray-box playthrough (30 min)", "lab", 10, "SEG_ALL", "30 min gray-box path", "METH_LAB; METH_SURVEY", "Fun", "7 of 10 outside testers", "KPI_R40", "Gate 2", "Gate 2", "plan")
pt(3, 15, 19, "Onboarding RITE: cryo wreck to first town", "lab", "2 a day x 5 days, 3 rounds", "SEG_NEW; SEG_RPG", "Slice opening", "METH_RITE", "Tutorial task success", "90% finish without help", "KPI_R33", "Gate 3", "3.2", "SC")
pt(3, 16, 18, "HUD and menu usability", "lab", 15, "SEG_ALL", "HUD, inventory, skills, perks, map, journal", "METH_CARD; METH_SUS; METH_EYE", "Usability score; HUD read time", "SUS 75+; telegraph noticed in under 300 ms", "KPI_R45; KPI_R46", "Gate 3", "3.2", "SC")
pt(3, 18, 19, "Vertical slice lab test, recorded, exit survey", "lab", 40, "SEG_ALL", "Full slice path", "METH_LAB; METH_SURVEY; METH_TELEM", "Would buy; fun; confusion hit rate", "75% would buy; fun 4/5+; no confusion point over 20%", "KPI_R40; KPI_R41; KPI_R43", "Gate 3", "3.3", "plan")
pt(3, 19, 20, "Vertical slice re-test after top 10 fixes", "lab", 20, "SEG_ALL", "Full slice path", "METH_LAB; METH_SURVEY", "Same three targets", "Same as above with new players", "KPI_R40; KPI_R41; KPI_R43", "Gate 3", "3.3", "plan")
pt(3, 18, 19, "Accessibility round 1", "lab", 10, "SEG_ACCESS", "Slice with each accessibility preset", "METH_ACCESS", "Task success per preset", "80% task success per preset", "KPI_R47", "Gate 3", "production plan", "production")
pt(3, 17, 19, "Ostra and story comprehension", "lab", 12, "SEG_RPG; SEG_NEW", "Slice dialogue and lore items", "METH_INTERVIEW; METH_SURVEY", "Can retell the premise; knows the goal", "80% retell crash and Shard premise", "KPI_R48", "Gate 3", "3.2", "SC")
# Phase 4 systems
for m0, nm, seg, meas, tgt, k in [
 (22, "Weapon class feel, 12 melee classes (4 per round)", "SEG_SOULS", "Feel 1 to 5 per class; TTK spread", "Every class 3.8+", "KPI_R03; KPI_R44"),
 (24, "Firearm class feel, 8 classes", "SEG_FPS", "Feel and recoil readability", "Every class 3.8+", "KPI_R03; KPI_R44"),
 (26, "Weave elements and subclass kits (18)", "SEG_RPG; SEG_FPS", "Kit clarity; combo discovery", "70% use a combo unprompted", "KPI_R15"),
 (28, "Perk trees and build planning", "SEG_RPG", "Build identity; respec intent", "Players can name their build in 2 h", "KPI_R15; KPI_R16"),
 (30, "Crafting and Rites usability", "SEG_RPG", "Task success; SUS", "SUS 70+", "KPI_R45"),
 (32, "Loot and perk roll readability", "SEG_LOOT", "Compare-and-equip time", "Under 10 s per decision", "KPI_R25"),
 (34, "Drop-in co-op flow, 4 players", "SEG_COOP", "Join success; quest sync confusion", "95% join success; no lost quest state", "KPI_R27; KPI_R28"),
 (35, "Arena PvP 3v3 with power weapons", "SEG_PVP", "Win rate spread by weapon; fun", "No weapon class over 55% win rate", "KPI_R29"),
 (36, "Strike (3 players) and raid prototype (6)", "SEG_COOP", "Completion and wipe causes", "Strike 85% completion; raid mechanics learned in 5 wipes", "KPI_R31; KPI_R32"),
 (37, "Forgeframe creator usability", "SEG_CREATOR", "Build a challenge room in 60 min", "70% succeed", "KPI_R49"),
]:
    pt(4, m0, m0 + 1, nm, "lab", 12, seg, "Debug build, system feature", "METH_LAB; METH_SURVEY; METH_EXPERT", meas, tgt, k, "Gate 4", "4.x", "SC")
pt(4, 20, 38, "Pro team weekly sweeps", "expert", "Pro team", "Pro team", "Latest debug build", "METH_EXPERT", "Exploits, frame data deltas, speed paths", "Every sweep filed in 48 h", "KPI_R17", "Gate 4", "4.x", "SC")
pt(4, 28, 29, "Accessibility round 2", "lab", 12, "SEG_ACCESS", "Systems complete build", "METH_ACCESS", "Task success per preset", "85% task success per preset", "KPI_R47", "Gate 4", "production plan", "production")
# Phase 5 per region / citadel / boss
regions = [("REG_01", "Cinderreach", 20), ("REG_02", "Saltmere", 27), ("REG_03", "Thornwood", 27), ("REG_04", "Glasswaste", 34), ("REG_05", "Rimefall", 34), ("REG_06", "Hollowdeep", 34)]
for rid, rn, s in regions:
    pt(5, s + 2, s + 3, f"Blind traversal, {rn}", "lab", 5, "SEG_ALL", f"{rid} gray-box", "METH_BLIND; METH_HEAT", "Landmark spacing on mount", "New thing seen every 40 to 60 s", "KPI_R09", "Gate 5", "5.1", "plan")
    pt(5, s + 4, s + 5, f"Citadel blind test, {rn}", "lab", 10, "SEG_ALL", f"LOC_CIT_{rid} gray-box", "METH_BLIND; METH_THINK", "Shortcut discovery; path length", "Every shortcut found by 60%; 2 to 3 h first play", "KPI_R10; KPI_R13", "Gate 5", "5.2", "plan")
    pt(5, s + 6, s + 7, f"Region re-test after polish, {rn}", "lab", 10, "SEG_ALL", f"{rid} art and polish pass", "METH_LAB; METH_SURVEY; METH_HEAT", "Fun; stalls; deaths per area", "Fun 4/5 (SC)", "KPI_R40; KPI_R02", "Gate 5", "5.1", "plan")
pt(5, 38, 40, "Orbital act low-gravity movement", "lab", 12, "SEG_ALL", "REG_Q movement test room", "METH_LAB; METH_SURVEY", "Comfort and control", "4 of 5; under 5% discomfort", "KPI_R44", "Gate 5", "5.3", "plan")
pt(5, 40, 42, "Ending comprehension and choice", "lab", 15, "SEG_RPG", "Act 3 and three endings", "METH_INTERVIEW; METH_SURVEY", "Choice understood; ending satisfaction", "80% can state what their choice did", "KPI_R21; KPI_R48", "Gate 5", "5.3", "SC")
# bosses
bosses = list(csv.DictReader(open(os.path.join(GP, "data/actors/bosses.csv"))))
ci = {"Shard-bearer": "3 to 12 attempts median first kill (plan 5.4)", "Raid": "Week-1 clear by 5% of raid teams (SC)"}
for i, b in enumerate(bosses):
    m0 = 24 + (i * 16) // len(bosses)
    tgt = ci.get(b["Class"], "2 to 8 attempts median first kill (SC)")
    pt(5, m0, m0 + 2, f"Boss test, {b['Boss']}", "lab" if b["Class"] != "Raid" else "expert", 20 if b["Class"] != "Raid" else "Pro team, 2 raid teams of 6", "SEG_SOULS; SEG_ALL" if b["Class"] != "Raid" else "Pro team", b["ACT_ID"], "METH_LAB; METH_TELEM; METH_SURVEY", "Attempts to first kill; I knew why I died; fairness 1 to 5", tgt + "; 80% death clarity", "KPI_R05; KPI_R01; KPI_R06", "Gate 5", "5.4", "plan" if b["Class"] == "Shard-bearer" else "SC")
pt(5, 36, 42, "Long-play diary study, Acts 1 and 2", "remote", 30, "SEG_ALL", "Regions 1 to 4", "METH_DIARY; METH_TELEM", "Motivation curve; quit reasons", "No week with over 20% wanting to stop", "KPI_R50", "Gate 5", "5.x", "SC")
pt(5, 38, 40, "Localization and culture review", "remote", "3 per language x 12", "SEG_LOC", "Localized build", "METH_CULT", "Clarity of UI and lore", "No blocker per locale", "KPI_R51", "Gate 5", "7.4", "SC")
# Phase 6
pt(6, 43, 45, "Outside playtest, first 15 hours, NDA", "remote", 200, "SEG_ALL", "Alpha build, first 15 h", "METH_TELEM; METH_HEAT; METH_SURVEY", "Deaths per area, quit points, time per region, build choices", "Fix top 25 problems; fun 4/5+", "KPI_R02; KPI_R14; KPI_R15; KPI_R40", "Gate 6", "6.4", "plan")
pt(6, 42, 46, "Melee and gun parity, full game", "expert", "Pro team + 24", "SEG_SOULS; SEG_FPS", "All regions, two loadouts", "METH_TELEM; METH_EXPERT", "Clear time gap", "Under 15%", "KPI_R04", "Gate 6", "6.3", "plan")
pt(6, 44, 45, "Accessibility round 3", "lab", 12, "SEG_ACCESS", "Alpha build", "METH_ACCESS", "Task success per preset", "90% task success per preset", "KPI_R47", "Gate 6", "production plan", "production")
pt(6, 44, 46, "Completionist route timing", "expert", "Pro team", "Pro team", "Full game", "METH_TELEM", "Main path and completion hours", "Campaign 60 to 90 h (plan 3.3)", "KPI_R14", "Gate 6", "3.3", "plan")
# Phase 7
pt(7, 49, 51, "Closed online beta", "beta", 50000, "SEG_ALL", "Co-op and PvP stress build", "METH_TELEM; METH_SURVEY", "Matchmaking, desync, server cost", "KPI_06 targets; disconnect under 1% of sessions", "KPI_06; KPI_R28; KPI_R30", "Gate 7", "7.2", "plan")
pt(7, 48, 50, "Final tutorial and first hour check", "lab", 20, "SEG_NEW", "Beta build", "METH_LAB", "Onboarding completion; first-session length", "90% reach first town; 60 min median first session", "KPI_R33; KPI_R35", "Gate 7", "7.x", "SC")
pt(7, 50, 51, "Accessibility round 4 (cert evidence)", "lab", 12, "SEG_ACCESS", "Cert candidate", "METH_ACCESS", "XAG and CVAA task checks", "All pass", "KPI_R47", "Gate 7", "7.3", "production")
# Phase 8-9
pt(8, 52, 54, "Launch room readouts", "live", "All players", "Live", "Launch build", "METH_TELEM; METH_SOCIAL", "Crash, server load, matchmaking, progress", "KPI_01; KPI_06", "KPI_01; KPI_06; KPI_03", "Gate 8", "8.2", "plan")
pt(8, 53, 54, "Patch 1.1 balance input", "live", "All players", "Live", "Launch telemetry", "METH_TELEM", "Top balance problems", "Shipped inside 6 weeks", "KPI_R05; KPI_R29", "Gate 8", "8.3", "plan")
pt(9, 54, 66, "Telemetry review every 2 weeks", "live", "All players", "Live", "Live game", "METH_TELEM; METH_AB", "All KPIs", "kpis.csv", "all", "", "9.4", "plan")
for s in range(4):
    m = 54 + 3 * s
    pt(9, m - 2, m - 1, f"Season {s+1} pre-release test", "expert", "Pro team + 40", "SEG_COOP; SEG_PVP", "New strike, Hollowed Citadel, Shardborn, PvP map", "METH_EXPERT; METH_SURVEY", "Strike completion; map win split", "Strike 80% completion; map side win split 45 to 55%", "KPI_R31; KPI_R29", "", "9.1", "SC")
pt(9, 54, 66, "Player council (rotating, 50 players)", "remote", 50, "SEG_ALL", "Live game", "METH_INTERVIEW; METH_SURVEY", "Season sentiment", "KPI_12", "KPI_12", "", "9.4", "SC")
pt(9, 62, 65, "Expansion 1 lab and blind tests", "lab", 40, "SEG_ALL", "New region, raid, faction line", "METH_LAB; METH_BLIND", "Same as Gates 3 and 5", "Fun 4/5; shortcuts 60%", "KPI_R40; KPI_R10", "", "9.2", "SC")
w("playtests.csv", ["pt_id", "phase", "month_start", "month_end", "calendar_start", "test", "kind", "players", "segments", "content", "methods", "measure", "target", "kpis", "gate", "plan_step", "source"], pts)

# ---------- pro team ----------
pro = [
 ("PRO_SOULS", "Souls-like specialist", 2, "Boss fairness, frame data, parry windows, no-hit runs", "KPI_R05; KPI_R01"),
 ("PRO_FPS", "Competitive FPS player", 2, "TTK, recoil, aim assist parity, PvP spawns", "KPI_R03; KPI_R29"),
 ("PRO_SPEED", "Speedrunner and exploit hunter", 1, "Sequence breaks, clips, XP and Ember farms", "KPI_R17; KPI_R23"),
 ("PRO_RAID", "Raid leader", 2, "Raid and strike mechanics, wipe causes, week-1 difficulty", "KPI_R32"),
 ("PRO_BUILD", "Theorycrafter", 1, "Build power budget, perk and Shardborn outliers", "KPI_R15; KPI_R16"),
 ("PRO_ACCESS", "Accessibility tester (disabled gamer)", 1, "Presets, remapping, subtitles, Assist", "KPI_R47"),
 ("PRO_COMP", "Completionist and lore reader", 1, "Quest bugs, lore consistency, journal clarity", "KPI_R19; KPI_R48"),
]
w("pro_team.csv", ["pro_id", "specialty", "count_at_peak", "focus", "kpis", "phases", "source"], [list(p[:5]) + ["P2 onward; 10 at P6 and P7 (research_team.csv RT_PRO)", "SC"] for p in pro])

# ---------- segments ----------
seg = [
 ("SEG_ALL", "Target mix", "All rows below at quota", "Default mix for gate tests"),
 ("SEG_SOULS", "Souls-like players", "20+ h in two Souls-likes in 2 years", "25%"),
 ("SEG_FPS", "Shooter and looter players", "20+ h in a looter shooter or Halo in 2 years", "25%"),
 ("SEG_RPG", "Open-world RPG players", "40+ h in Skyrim-style RPG", "25%"),
 ("SEG_NEW", "Genre newcomers", "Plays action games, no Souls-like finished", "15%"),
 ("SEG_ACCESS", "Players with disabilities", "Recruited through accessibility partners", "10%; plus dedicated rounds"),
 ("SEG_COOP", "Co-op groups", "Recruited as pre-made groups of 3 or 4", "Per test"),
 ("SEG_PVP", "PvP players", "Ranked arena play in 1 year", "Per test"),
 ("SEG_LOOT", "Loot-focused players", "100+ h in a looter", "Per test"),
 ("SEG_CREATOR", "Creators and modders", "Published a mod or Forge map", "Per test"),
 ("SEG_LOC", "Native speakers per locale", "One of the 12 text languages", "3 per language"),
]
w("segments.csv", ["seg_id", "segment", "screener", "quota_or_use", "rules"], [list(s) + ["Age 18+ (M rating); platform split PC 40 / PS5 35 / Xbox 25 (SC); no staff, press or competitor staff; NDA and consent (production legal_eula_privacy.md); paid at local rate"] for s in seg])

# ---------- lab ----------
lab = [
 ("LAB_ROOMS", "Test rooms", "2 rooms of 12 stations, 1 room of 4 co-op pods, 2 interview rooms", "Phase 3"),
 ("LAB_STATION", "Station kit", "PC at min and recommended spec, PS5, Xbox Series S and X, headset, facecam", "Phase 3"),
 ("LAB_OBS", "Observation room", "One-way glass and live stream of every station with telemetry overlay", "Phase 3"),
 ("LAB_EYE", "Eye trackers", "2 screen-mounted trackers", "Phase 3"),
 ("LAB_ACCESS", "Adaptive kit", "Adaptive controllers, one-hand and foot switches, large monitor", "Phase 3"),
 ("LAB_CAPTURE", "Capture", "60 fps capture of game, face and controller input (plan 0.1 tool set)", "Phase 2"),
 ("LAB_REMOTE", "Remote test platform", "Secure streaming or watermarked build delivery, session recording, kill switch", "Phase 5"),
 ("LAB_BUILDFLAG", "Playtest build flag", "Enables survey popups, bug hotkey, tester ID, session markers; never in retail", "Phase 2"),
 ("LAB_LOG", "Research log", "One log of every finding with severity, status and owner; producers review each sprint", "Phase 2"),
]
w("lab_spec.csv", ["lab_id", "item", "spec", "needed_by", "source"], [list(l) + ["SC"] for l in lab])

# ---------- survey items ----------
sv = [
 ("SRV_DEATH_CLARITY", "Post-death prompt", "Did you know why you died?", "Yes / No", "After every death (playtest builds; 1 in 5 deaths after Phase 5)"),
 ("SRV_DEATH_FAIR", "Post-death prompt", "Was that death fair?", "1 to 5", "After a No on clarity"),
 ("SRV_BOSS_FUN", "Post-boss", "How much did you enjoy this fight?", "1 to 5", "After a boss kill or quit"),
 ("SRV_BOSS_FAIR", "Post-boss", "How fair did this fight feel?", "1 to 5", "After a boss kill or quit"),
 ("SRV_SESSION_FUN", "Post-session", "How fun was this session?", "1 to 5", "Session end"),
 ("SRV_SESSION_LOST", "Post-session", "Were you ever unsure what to do next?", "Yes / No + where", "Session end"),
 ("SRV_SESSION_CONTINUE", "Post-session", "How much do you want to keep playing?", "1 to 5", "Session end"),
 ("SRV_EXIT_BUY", "Exit survey", "Would you buy this game at full price?", "Definitely / Probably / Not sure / Probably not / Definitely not", "End of lab test"),
 ("SRV_EXIT_RECOMMEND", "Exit survey", "How likely are you to recommend it to a friend?", "0 to 10", "End of lab test"),
 ("SRV_EXIT_CONFUSION", "Exit survey", "Pick every moment that confused you", "Checklist of test beats", "End of lab test"),
 ("SRV_EXIT_PILLARS", "Exit survey", "Rate: fights were readable; horizon pulled me; my build felt like mine; sword and gun felt equal; story came from the world", "1 to 5 each", "End of lab test"),
 ("SRV_UI_USABILITY", "UI usability", "Ten-item usability scale for the screen tested", "1 to 5 each, scored to 100", "After UI tasks"),
 ("SRV_ACCESS_TASK", "Accessibility", "Could you do this task with your settings?", "Yes / With help / No", "Per task"),
 ("SRV_SHORTCUT", "Blind test", "How did opening that shortcut feel?", "1 to 5 + one word", "On shortcut open"),
 ("SRV_LIVE_PULSE", "Live pulse (opt-in, retail)", "How are you enjoying this season?", "1 to 5", "Once per season, after 3 h played that season"),
 ("SRV_CHURN", "Lapsed-player email (opt-in)", "What made you stop playing?", "Choice list + text", "28 days inactive"),
]
w("survey_items.csv", ["srv_id", "instrument", "question_en", "scale", "when", "kpi", "ships_in_retail"],
  [list(s) + [{"SRV_DEATH_CLARITY": "KPI_R01", "SRV_SESSION_FUN": "KPI_R40", "SRV_EXIT_BUY": "KPI_R41", "SRV_EXIT_CONFUSION": "KPI_R43", "SRV_UI_USABILITY": "KPI_R45", "SRV_ACCESS_TASK": "KPI_R47", "SRV_LIVE_PULSE": "KPI_R52", "SRV_CHURN": "KPI_R50"}.get(s[0], ""), "Yes" if s[0] in ("SRV_LIVE_PULSE", "SRV_CHURN") else "No"] for s in sv])

# ---------- KPIs ----------
live = {r["kpi_id"]: r for r in csv.DictReader(open(os.path.join(GP, "design/liveops/liveops_kpis.csv")))}
kp = []
def k(i, area, name, formula, events, grain, target, alert, phase, owner, dsh, src):
    kp.append([i, area, name, formula, events, grain, target, alert, phase, owner, dsh, src])
LF = {
 "KPI_01": ("Quality", "crashed sessions / sessions", "session_start; session_end; crash report", "Build x platform x day", "Over 1% of sessions", "DSH_LAUNCH; DSH_QUALITY"),
 "KPI_02": ("Business", "Metacritic-style aggregate", "External", "Launch", "Under 80", "DSH_EXEC"),
 "KPI_03": ("Engagement", "players active on day N after first session / players with a first session that day", "session_start", "Install cohort x platform", "D1 under 50%", "DSH_RETENTION; DSH_EXEC"),
 "KPI_04": ("Live", "players at season rank 50 by week 13 / season active players", "season_rank (TR_01)", "Season", "Under 40% at week 11", "DSH_SEASON"),
 "KPI_05": ("Live", "lapsed 28+ days players back in season week 1 / lapsed players", "session_start", "Season", "Under 20%", "DSH_SEASON; DSH_RETENTION"),
 "KPI_06": ("Multiplayer", "p90 seconds from queue to match", "mm_queue; mm_match (TR_02)", "Mode x region x hour", "p90 over target for 30 min", "DSH_LAUNCH; DSH_MP"),
 "KPI_07": ("Business", "buyers in 12 months / monthly active players", "purchase", "Month", "Under 8%", "DSH_STORE"),
 "KPI_08": ("Business", "refunds / purchases", "purchase; refund (TR_03)", "Month x SKU", "Over 3%", "DSH_STORE"),
 "KPI_09": ("Business", "expansion owners / base owners", "entitlement", "Expansion", "Under 25% at 3 months", "DSH_STORE; DSH_EXEC"),
 "KPI_10": ("Creation", "published maps and rooms", "ugc_publish (TR_04)", "Month x platform", "Under 1,000 in month 1", "DSH_FORGE"),
 "KPI_11": ("Support", "ticket first-reply and close times", "Support desk", "Week", "Any week over target", "DSH_EXEC"),
 "KPI_12": ("Sentiment", "Steam recent review band", "External; METH_SOCIAL", "Week", "Mixed or worse", "DSH_EXEC; DSH_SEASON"),
}
for kid, r in live.items():
    a, f, e, g, al, d = LF[kid]
    k(kid, a, r["metric"], f, e, g, r["target"], al, "P8 onward", "Live ops", d, "liveops_kpis.csv (target not redefined here)")
R_ = [
 ("KPI_R01", "Combat", "Death clarity", "Yes answers / SRV_DEATH_CLARITY answers", "death; survey_response (TR_05)", "Build x area x killer", "80% (plan Gate 2)", "Any area or attack under 70%", "P2 onward", "Combat design", "DSH_PLAYTEST; DSH_COMBAT", "plan"),
 ("KPI_R02", "Combat", "Deaths per minute", "deaths / minutes in combat", "death; combat_state (TR_06)", "Area x level band", "0.15 to 0.35 open world; up to 1.0 in boss arenas (SC)", "Area 2x its region median", "P2 onward", "Combat design", "DSH_COMBAT; DSH_WORLD", "plan measure, SC target"),
 ("KPI_R03", "Combat", "Time to kill by weapon class", "median seconds from first hit to kill per class vs enemy role", "damage_dealt (TR_07); kill", "Class x enemy role x level band", "Within 15% of class target in data/items (SC)", "Class over 20% off", "P2 onward", "Systems design", "DSH_COMBAT", "plan measure"),
 ("KPI_R04", "Combat", "Melee and gun parity", "abs(median clear time melee - gun) / mean", "encounter_end (TR_08)", "Encounter x region", "Under 15% (plan 2.2)", "Over 15%", "P2, P6, live", "Combat design", "DSH_COMBAT; DSH_EXEC", "plan"),
 ("KPI_R05", "Combat", "Boss attempts to first kill", "median boss_attempt count before first win", "boss_attempt", "Boss x party size", "Shard-bearers 3 to 12 (plan 5.4); others 2 to 8 (SC)", "Outside the band for 2 review cycles", "P5 onward", "Boss team", "DSH_BOSS", "plan"),
 ("KPI_R06", "Combat", "Boss phase deaths", "deaths by phase and by move / attempts", "boss_attempt; death", "Boss x phase x MOV_ ID", "No single move over 35% of deaths (SC)", "Any move over 35%", "P5 onward", "Boss team", "DSH_BOSS", "SC"),
 ("KPI_R07", "Combat", "Attack lethality outliers", "deaths by ATK_ ID / exposures to that attack", "death; enemy_attack_start (TR_09)", "ATK_ ID", "No attack 3x its role median (SC)", "Over 3x", "P4 onward", "Combat design", "DSH_COMBAT", "SC"),
 ("KPI_R08", "Combat", "Assist and Echo use", "players with Assist on / players; Echo summons per boss", "settings_changed (TR_10); summon_used (TR_11)", "Boss x region", "Tracked, no target; flag a boss where Echo use over 60% (SC)", "Over 60%", "P6 onward", "Combat design", "DSH_BOSS; DSH_ACCESS", "SC"),
 ("KPI_R09", "World", "New thing seen interval", "median seconds between landmark_seen events while mounted", "landmark_seen (TR_12)", "Region x route", "40 to 60 s (plan 2.3)", "Over 75 s on a route", "P2, P5", "Level design", "DSH_WORLD", "plan"),
 ("KPI_R10", "World", "Shortcut discovery", "players who opened shortcut / players who reached it", "shortcut_opened (TR_13); area_enter", "Shortcut x Citadel", "60% each (plan 5.2)", "Under 50%", "P2, P5, live", "Level design", "DSH_WORLD", "plan"),
 ("KPI_R11", "World", "Anchor and tower discovery", "Anchors lit / Anchors passed within 50 m", "anchor_lit; position samples", "Region", "85% (SC)", "Under 70%", "P5 onward", "Level design", "DSH_WORLD", "SC"),
 ("KPI_R12", "World", "Explorer mode use", "players with Explorer mode on / players", "settings_changed", "Platform", "Tracked; mode must stay finishable (no stall area over 2x)", "Stall rate 2x marker mode", "P6 onward", "Narrative design", "DSH_QUEST", "SC"),
 ("KPI_R13", "World", "Site and Citadel completion", "completions / entries; first-play hours", "area_enter; site_complete (TR_14)", "Site x region", "Citadel first play 2 to 3 h (plan 5.2); site completion 80% of entries (SC)", "Under 60%", "P5 onward", "Level design", "DSH_WORLD", "plan + SC"),
 ("KPI_R14", "Progression", "Level against region band", "player level at region entry - band minimum", "level_up; area_enter", "Region x route", "Main path within band; completionist under 8 over max (SC)", "Main path under band minimum", "P4 onward", "Systems design", "DSH_PROGRESSION", "plan 4.2"),
 ("KPI_R15", "Progression", "Build diversity", "Shannon entropy of primary skill share at level 40, normalized 0 to 1", "skill_rank; item_equipped", "Platform x month", "0.75 or higher (SC)", "Under 0.6", "P6 onward", "Systems design", "DSH_PROGRESSION", "SC"),
 ("KPI_R16", "Progression", "Sword and rifle share", "players whose damage is 70%+ melee vs 70%+ firearm", "damage_dealt", "Level band", "Each side 30 to 50% of committed builds (SC)", "Either under 20%", "P6 onward", "Systems design", "DSH_PROGRESSION; DSH_EXEC", "SC, pillar 4"),
 ("KPI_R17", "Progression", "XP and Ember farm anomalies", "players over 4 SD XP per hour by action", "skill_xp (TR_15); economy_txn", "XPA_ ID", "Zero untargeted farms (plan 2.4)", "Any flagged action", "P2 onward", "Data science", "DSH_PROGRESSION; DSH_ECONOMY", "plan"),
 ("KPI_R18", "Progression", "Ember lost on death", "Ember lost / Ember earned", "economy_txn (sink = death)", "Region", "10 to 20% (SC)", "Over 30%", "P5 onward", "Systems design", "DSH_ECONOMY", "SC"),
 ("KPI_R19", "Narrative", "Main quest funnel", "players reaching step / players starting the quest", "quest_step", "QST_ ID step", "Act 1 done by 70% of owners, campaign by 35% (SC)", "Any step losing 10% of players", "P6 onward", "Narrative design", "DSH_QUEST; DSH_EXEC", "SC"),
 ("KPI_R20", "Narrative", "Quest stall and abandon", "players idle on a step 3+ sessions / players on step", "quest_step; quest_abandon (TR_16)", "QST_ ID", "Under 10% per step (SC)", "Over 15%", "P6 onward", "Narrative design", "DSH_QUEST", "SC"),
 ("KPI_R21", "Narrative", "Ending and faction split", "share per ending and per joined faction", "ending_reached (TR_17); faction_join", "Ending", "No ending under 15% (SC)", "Under 10%", "P6 onward", "Narrative design", "DSH_QUEST", "SC"),
 ("KPI_R22", "Narrative", "Companion completion", "companion lines finished / recruited", "quest_step", "CMP_ ID", "50% (SC)", "Under 30%", "P6 onward", "Narrative design", "DSH_QUEST", "SC"),
 ("KPI_R23", "Economy", "Ember inflation", "median banked Ember by level vs simulation curve", "economy_txn", "Level x week", "Within 20% of design/simulation curve (SC)", "Over 30%", "P6 onward", "Economy design", "DSH_ECONOMY", "SC"),
 ("KPI_R24", "Economy", "Source to sink ratio", "Ember earned / Ember spent and lost", "economy_txn", "Week", "1.0 to 1.2 (SC)", "Over 1.4", "P6 onward", "Economy design", "DSH_ECONOMY", "SC"),
 ("KPI_R25", "Economy", "Dead gear", "items acquired never equipped by any player / items in loot tables", "item_acquired; item_equipped", "ITM_ ID", "Under 15% of weapons (SC)", "Over 25%", "P6 onward", "Systems design", "DSH_ECONOMY", "SC"),
 ("KPI_R26", "Multiplayer", "Co-op share", "play minutes in parties of 2+ / play minutes", "coop_join; coop_leave", "Week", "Tracked; 25% (SC)", "", "P7 onward", "Online design", "DSH_MP", "SC"),
 ("KPI_R27", "Multiplayer", "Join success", "successful joins / join attempts", "coop_join (result field TR_18)", "Platform pair x region", "97% (SC)", "Under 93%", "P4 onward", "Online engineering", "DSH_MP; DSH_LAUNCH", "SC"),
 ("KPI_R28", "Multiplayer", "Disconnect and desync", "sessions ending in disconnect / MP sessions", "coop_leave reason; match_end", "Mode x region", "Under 1% (SC)", "Over 2%", "P2 onward", "Online engineering", "DSH_MP; DSH_LAUNCH", "SC"),
 ("KPI_R29", "Multiplayer", "PvP weapon and map balance", "win rate by weapon class, power weapon and map side", "match_end", "Weapon x map x rating band", "45 to 55% each (SC)", "Outside 42 to 58%", "P4 onward", "PvP design", "DSH_PVP", "SC"),
 ("KPI_R30", "Multiplayer", "Match quality", "share of 3v3 matches with team rating gap under 100", "match_end", "Playlist x hour", "85% (SC)", "Under 75%", "P7 onward", "Online design", "DSH_PVP", "SC"),
 ("KPI_R31", "Endgame", "Strike completion", "strike completions / starts", "activity_end (TR_19)", "Strike x modifier", "85% normal, 50% top modifier (SC)", "Under 70% normal", "P4 onward", "Endgame design", "DSH_ENDGAME", "SC"),
 ("KPI_R32", "Endgame", "Raid clear", "teams clearing / teams attempting", "activity_end", "Raid x week", "5% week 1, 25% week 4 (SC)", "Over 15% in week 1", "P4 onward", "Endgame design", "DSH_ENDGAME", "SC"),
 ("KPI_R33", "Onboarding", "Onboarding completion", "players reaching first town / players starting a new game", "tutorial_step (TR_20); quest_step", "Platform x day", "90% (SC)", "Under 85%", "P3 onward", "UX", "DSH_ONBOARD", "SC"),
 ("KPI_R34", "Onboarding", "Time to first Shard-bearer", "median play hours to ACT_BOSS_VAEL kill", "boss_attempt", "Cohort", "6 to 10 h (SC, Region 1 band)", "Over 14 h", "P6 onward", "UX", "DSH_ONBOARD", "SC"),
 ("KPI_R35", "Onboarding", "First session length", "median minutes of first session", "session_end", "Cohort", "60 min or more (SC)", "Under 40 min", "P7 onward", "UX", "DSH_ONBOARD; DSH_RETENTION", "SC"),
 ("KPI_R36", "Engagement", "Active players", "DAU, WAU, MAU and DAU/MAU", "session_start", "Day x platform", "DAU/MAU 0.25+ in live (SC)", "Drop 20% week on week outside season gaps", "P8 onward", "Analytics", "DSH_RETENTION; DSH_EXEC", "SC"),
 ("KPI_R37", "Engagement", "Hours per active player", "play hours per WAU", "session_end", "Week", "8 h a week first month (SC)", "", "P8 onward", "Analytics", "DSH_RETENTION", "SC"),
 ("KPI_R38", "Quality", "Frame rate compliance", "frames at 60 fps in performance mode / frames sampled", "perf_sample", "Platform x region", "95% (plan 7.1)", "Under 90% in any region", "P4 onward", "Engineering", "DSH_QUALITY", "plan"),
 ("KPI_R39", "Quality", "Load time menu to world", "median seconds", "load_time (TR_21)", "Platform", "Under 15 s consoles (plan 7.1)", "Over 15 s", "P6 onward", "Engineering", "DSH_QUALITY", "plan"),
 ("KPI_R40", "Research", "Fun rating", "mean SRV_SESSION_FUN", "survey_response", "Test x segment", "4 of 5 (plan Gates 3, 6); 7 of 10 at Gate 2", "Under 3.6", "P2 to P7", "Research", "DSH_PLAYTEST; DSH_EXEC", "plan"),
 ("KPI_R41", "Research", "Would buy", "Definitely + Probably / answers", "survey_response", "Test x segment", "75% (plan Gate 3)", "Under 65%", "P3 to P7", "Research", "DSH_PLAYTEST; DSH_EXEC", "plan"),
 ("KPI_R42", "Research", "Concept appeal", "top-two-box appeal", "Web survey", "Segment", "60% (SC)", "Under 50%", "P1", "Research", "DSH_PLAYTEST", "SC"),
 ("KPI_R43", "Research", "Confusion hit rate", "testers hitting a confusion point / testers", "survey_response; researcher log", "Beat", "No point over 20% (plan Gate 3)", "Over 20%", "P3 to P7", "Research", "DSH_PLAYTEST", "plan"),
 ("KPI_R44", "Research", "Feel and comfort", "mean feel score; discomfort reports", "survey_response", "Feature", "3.8+ feel; under 5% discomfort (SC)", "Under 3.5 or over 5%", "P2 to P5", "Research", "DSH_PLAYTEST", "SC"),
 ("KPI_R45", "Research", "UI usability score", "SUS-style 0 to 100", "survey_response", "Screen", "75 (SC)", "Under 68", "P3 onward", "UX", "DSH_PLAYTEST", "SC"),
 ("KPI_R46", "Research", "Telegraph read time", "median ms to first gaze on a telegraph", "Eye tracker", "Attack", "Under 300 ms (SC)", "Over 400 ms", "P3 to P5", "Research", "DSH_PLAYTEST", "SC"),
 ("KPI_R47", "Accessibility", "Accessibility task success", "tasks done unaided / tasks", "Researcher log", "Preset", "80%, 85%, 90%, 100% by rounds 1 to 4 (SC)", "Under round target", "P3 to P7", "Accessibility", "DSH_ACCESS", "SC"),
 ("KPI_R48", "Research", "Story comprehension", "testers who retell premise or choice correctly / testers", "Interview coding", "Test", "80% (SC)", "Under 65%", "P3 to P5", "Narrative", "DSH_PLAYTEST", "SC"),
 ("KPI_R49", "Creation", "Forgeframe task success", "creators finishing a room in 60 min / creators", "Researcher log; ugc_publish", "Build", "70% (SC)", "Under 50%", "P4 onward", "Tools", "DSH_FORGE", "SC"),
 ("KPI_R50", "Engagement", "Churn risk", "predicted 14-day churn share among active (DS_CHURN)", "Model output", "Day", "Tracked; drivers reviewed every 2 weeks", "Up 5 points week on week", "P8 onward", "Data science", "DSH_RETENTION", "SC"),
 ("KPI_R51", "Localization", "Locale blockers", "open blocker issues per language", "Loc QA and METH_CULT", "Language", "Zero at Gate 7", "Any", "P5 to P7", "Localization", "DSH_QUALITY", "SC"),
 ("KPI_R52", "Sentiment", "Season pulse", "mean SRV_LIVE_PULSE", "survey_response", "Season", "4.0 (SC)", "Under 3.5", "P9", "Research", "DSH_SEASON", "SC"),
 ("KPI_R53", "Social", "Player reports", "reports per 1,000 MP sessions", "player_report (TR_22)", "Mode x region", "Under 5 (SC)", "Over 10", "P7 onward", "Community", "DSH_MP; DSH_PVP", "SC"),
]
for r in R_:
    k(*r)
w("kpis.csv", ["kpi_id", "area", "metric", "formula", "events", "grain", "target", "alert", "phase", "owner", "dashboards", "source"], kp)

# ---------- dashboards ----------
D = [
 ("DSH_PLAYTEST", "Playtest live room", "Research, design leads", "Live during tests; daily report", "Lab", "KPI_R01; KPI_R40; KPI_R41; KPI_R43; KPI_R44; KPI_R45; KPI_R46; KPI_R48", ["Test progress by station|table", "Death clarity by area|bar", "Fun and would-buy by segment|bar", "Confusion points by beat|ranked bar", "Live death map|map heatmap", "Research log open issues|table"]),
 ("DSH_COMBAT", "Combat health", "Combat and systems design", "Hourly", "Warehouse", "KPI_R01; KPI_R02; KPI_R03; KPI_R04; KPI_R07", ["Deaths per minute by area|bar", "TTK by class vs target|dot plot", "Parity gap by encounter|bar", "Lethal attack outliers|ranked table", "Death cause mix by enemy faction|stacked bar"]),
 ("DSH_BOSS", "Boss tuning", "Boss team", "Hourly", "Warehouse", "KPI_R05; KPI_R06; KPI_R08", ["Attempts to first kill per boss vs band|range bar", "Phase reached funnel|funnel", "Deaths by MOV_ ID|ranked bar", "Party size and Echo use|stacked bar", "Fairness score|bar"]),
 ("DSH_WORLD", "World and levels", "Level design", "Daily", "Warehouse + editor overlay", "KPI_R02; KPI_R09; KPI_R10; KPI_R11; KPI_R13", ["Death, quit and stall heatmaps per level|map heatmap", "New thing seen interval by route|line", "Shortcut discovery per Citadel|bar", "Site completion|bar", "Path traces sample|map"]),
 ("DSH_PROGRESSION", "Progression", "Systems design", "Daily", "Warehouse + simulation", "KPI_R14; KPI_R15; KPI_R16; KPI_R17", ["Level vs region band, sim vs real|line with band", "Skill share at level 40|stacked bar", "Melee vs firearm build share|bar", "Perk pick rates|ranked bar", "XP anomaly flags|table"]),
 ("DSH_ECONOMY", "Economy", "Economy design", "Daily", "Warehouse", "KPI_R18; KPI_R23; KPI_R24; KPI_R25", ["Banked Ember by level vs sim|line", "Sources and sinks|stacked area", "Ember lost on death by region|bar", "Dead gear list|table", "Material flow|stacked bar"]),
 ("DSH_QUEST", "Quests and story", "Narrative design", "Daily", "Warehouse", "KPI_R12; KPI_R19; KPI_R20; KPI_R21; KPI_R22", ["Main path funnel by act|funnel", "Stall steps|ranked table", "Faction and ending split|bar", "Companion completion|bar", "Explorer vs marker stall|bar"]),
 ("DSH_ONBOARD", "First hours", "UX", "Daily", "Warehouse", "KPI_R33; KPI_R34; KPI_R35", ["Tutorial step funnel|funnel", "First session length|histogram", "Hours to first Shard-bearer|histogram", "Early quit points|map heatmap"]),
 ("DSH_MP", "Co-op and network", "Online team", "5 min", "Realtime stream", "KPI_06; KPI_R26; KPI_R27; KPI_R28; KPI_R53", ["Join success by platform pair|bar", "Disconnects by reason|stacked bar", "Latency by region|line", "Party size mix|bar", "Reports per 1,000 sessions|line"]),
 ("DSH_PVP", "Arena PvP", "PvP design", "Hourly", "Warehouse", "KPI_R29; KPI_R30; KPI_R53", ["Win rate by weapon class|dot plot with band", "Power weapon pickup and win|bar", "Map side win split|bar", "Rating gap distribution|histogram"]),
 ("DSH_ENDGAME", "Strikes and raids", "Endgame design", "Hourly", "Warehouse", "KPI_R31; KPI_R32", ["Strike completion by modifier|bar", "Raid clears by week|line", "Wipe causes by encounter|ranked bar"]),
 ("DSH_LAUNCH", "Launch room (plan 8.2)", "Live ops room", "1 min", "Realtime stream", "KPI_01; KPI_06; KPI_R27; KPI_R28", ["Crash rate by platform and build|line", "Server load and concurrency|line", "Matchmaking time p50 and p90|line", "Player progress: region reached|stacked area", "Top crash groups|table"]),
 ("DSH_RETENTION", "Retention and engagement", "Leadership, live ops", "Daily", "Warehouse", "KPI_03; KPI_05; KPI_R35; KPI_R36; KPI_R37; KPI_R50", ["Retention curves by cohort|line", "DAU, WAU, MAU|line", "Churn risk and top drivers|bar", "Lapsed and returning|stacked bar"]),
 ("DSH_SEASON", "Season health", "Season team", "Daily", "Warehouse", "KPI_04; KPI_05; KPI_12; KPI_R52", ["Season rank progress vs pace|line", "New activity participation|bar", "Pulse survey|bar", "Sentiment band|stat tile"]),
 ("DSH_STORE", "Store and editions", "Business", "Daily", "Warehouse + platform reports", "KPI_07; KPI_08; KPI_09", ["Buyers and conversion|line", "Revenue by SKU|bar", "Refund rate|line", "Expansion attach|stat tile"]),
 ("DSH_QUALITY", "Performance and stability", "Engineering, QA", "Hourly", "Warehouse + crash tracker", "KPI_01; KPI_R38; KPI_R39; KPI_R51", ["FPS compliance by region and platform|heat table", "Hitches per hour|line", "Load times|histogram", "Crash groups trend|line"]),
 ("DSH_ACCESS", "Accessibility use", "Accessibility", "Weekly", "Warehouse + lab log", "KPI_R08; KPI_R47", ["Settings and preset adoption|bar", "Task success by preset per round|bar", "Assist use by boss|bar"]),
 ("DSH_FORGE", "Forgeframe", "Tools, community", "Daily", "Warehouse + mod hub", "KPI_10; KPI_R49", ["Published maps and rooms|line", "Plays per creation|histogram", "Review queue age|line"]),
 ("DSH_EXEC", "Executive summary", "Leadership, publisher", "Weekly", "Warehouse", "KPI_02; KPI_03; KPI_09; KPI_11; KPI_12; KPI_R04; KPI_R16; KPI_R19; KPI_R36; KPI_R40; KPI_R41", ["Gate readiness tiles|stat tiles", "Retention|line", "Parity and build share|bar", "Fun and would-buy trend|line", "Sentiment|stat tile"]),
]
w("dashboards.csv", ["dsh_id", "name", "audience", "refresh", "source", "kpis", "panel_count", "source_note"], [[d[0], d[1], d[2], d[3], d[4], d[5], len(d[6]), "SC; launch room panels from plan 8.2" if d[0] == "DSH_LAUNCH" else "SC"] for d in D])
pan = []
for d in D:
    for j, p in enumerate(d[6], 1):
        t, c = p.split("|")
        pan.append([f"{d[0]}_P{j:02d}", d[0], j, t, c, "Platform; build; region; segment (where the KPI grain allows)", "Uses the KPI alert from kpis.csv" if "KPI" in d[5] else ""])
w("dashboard_panels.csv", ["panel_id", "dsh_id", "order", "panel", "chart", "filters", "alert_rule"], pan)

# ---------- telemetry requests to tech (tech owns events) ----------
tr = [
 ("TR_01", "season_rank", "season_id, rank, xp_source", "KPI_04"),
 ("TR_02", "mm_queue / mm_match", "mode, playlist, party size, region, wait_s, rating band", "KPI_06; KPI_R30"),
 ("TR_03", "refund", "product ID, platform, days since purchase", "KPI_08"),
 ("TR_04", "ugc_publish / ugc_play", "creation ID, type, platform, plays", "KPI_10; KPI_R49"),
 ("TR_05", "survey_response", "srv_id, answer, context ID (death, boss, session), tester ID in playtest builds", "KPI_R01; KPI_R40 to R52"),
 ("TR_06", "combat_state", "enter and exit, encounter ID, enemy count", "KPI_R02"),
 ("TR_07", "damage_dealt (sampled, aggregated per encounter)", "weapon class, damage type, target role, total, hits, crits", "KPI_R03; KPI_R16"),
 ("TR_08", "encounter_end", "ENC_ ID, duration, loadout class, result, party size", "KPI_R04"),
 ("TR_09", "enemy_attack_start (sampled 10%)", "ATK_ ID, target in range", "KPI_R07"),
 ("TR_10", "settings_changed", "OPT_ ID, old, new, preset", "KPI_R08; KPI_R12"),
 ("TR_11", "summon_used", "Echo or co-op, boss or area ID", "KPI_R08"),
 ("TR_12", "landmark_seen", "landmark ID, distance, mounted flag", "KPI_R09"),
 ("TR_13", "shortcut_opened", "shortcut ID, LOC_ ID, time since area entry", "KPI_R10"),
 ("TR_14", "site_complete / area_enter / anchor_lit", "LOC_ ID, time spent", "KPI_R11; KPI_R13"),
 ("TR_15", "skill_xp (aggregated per minute)", "XPA_ ID, xp, had target", "KPI_R17"),
 ("TR_16", "quest_abandon / quest_track", "QST_ ID, step, tracked flag", "KPI_R20"),
 ("TR_17", "ending_reached / faction_join", "ending ID, FAC_ ID", "KPI_R21"),
 ("TR_18", "coop_join result field", "success or failure code", "KPI_R27"),
 ("TR_19", "activity_end", "strike or raid ID, modifiers, result, wipes, duration", "KPI_R31; KPI_R32"),
 ("TR_20", "tutorial_step", "step ID, skipped, duration", "KPI_R33"),
 ("TR_21", "load_time", "from, to, seconds, storage tier", "KPI_R39"),
 ("TR_22", "player_report", "category, mode (no free text in telemetry)", "KPI_R53"),
 ("TR_23", "ab_assignment", "experiment ID, variant", "All experiments"),
 ("TR_24", "playtest_marker (playtest builds only)", "tester ID, station, researcher note tag", "DSH_PLAYTEST"),
 ("TR_25", "position_sample (1 per 10 s, playtest and 1% retail sample)", "level ID, x, y, z", "Heatmaps"),
]
w("telemetry_requests.csv", ["tr_id", "event", "fields", "kpis", "owner", "status"], [list(t) + ["design/tech (06-telemetry)", "requested"] for t in tr])

# ---------- data science models ----------
ds = [
 ("DS_SIM", "Progression and loot simulation (plan 5.5)", "Do level, Ember and drops track the bands", "Agent sim, 10,000 runs a night; calibrated to telemetry at P6 (plan 6.3)", "data/ tables; real XP rates", "Charts vs bands; tuning deltas", "P2 onward", "Sim vs real gap under 10% after calibration"),
 ("DS_DIFF", "Difficulty spike detector", "Which areas and attacks are unfair", "Bayesian hierarchical model of death rate by area, attack and level", "death; combat_state; survey", "Ranked spike list", "P5 onward", "Back-tested against lab clarity answers"),
 ("DS_BOSS", "Boss attempt model", "Will a boss land in its attempts band", "Survival model on attempts to kill", "boss_attempt", "Predicted median and band check", "P5 onward", "Predict from first 500 players within 1 attempt"),
 ("DS_CHURN", "Churn prediction", "Who stops in the next 14 days and why", "Gradient boosted trees on session and progress features; SHAP drivers", "session, quest, death, social events", "Risk score and drivers (KPI_R50)", "P8 onward", "AUC 0.75+; used only for aggregate insight and content fixes, never for pricing"),
 ("DS_SEG", "Player segmentation", "What play styles exist", "Clustering on time share by activity and build", "All gameplay events", "6 to 10 segments for design", "P7 onward", "Stable across two months"),
 ("DS_MM", "Matchmaking skill rating", "Fair 3v3 matches", "Team rating model (TrueSkill-style, own implementation)", "match_end", "Rating per player", "P4 onward", "Predict match winner 60%+; KPI_R30"),
 ("DS_BAL", "PvP and build balance monitor", "Is anything over-tuned", "Win-rate regression controlling for skill", "match_end; damage_dealt", "Outlier list for patches", "P7 onward", "Outliers confirmed by pro team"),
 ("DS_ECON", "Economy health model", "Inflation and farms", "Source-sink stock and flow model, anomaly detection (4 SD)", "economy_txn; skill_xp", "Alerts KPI_R17, KPI_R23", "P6 onward", "False alert rate under 1 a week"),
 ("DS_ANOM", "Live anomaly detection", "Broken builds, exploits, outages", "Seasonal baseline with alert on 3 SD", "All KPI streams", "Alerts to on-call", "P7 onward", "Catches seeded test anomalies"),
 ("DS_FORECAST", "Concurrency and server forecast", "How many servers on launch and season days", "Time series forecast with wishlist and beta inputs", "Beta, wishlists, live CCU", "Server plan (load test to 2x, tech/06)", "P7 onward", "Error under 20% at launch"),
 ("DS_AB", "Experiment platform", "Choose tunings with evidence", "Randomized by player ID; CUPED variance reduction; sequential tests", "ab_assignment; KPI events", "Readouts with 95% CI", "P8 onward", "A/A tests pass"),
 ("DS_TEXT", "Survey and review text coding", "Top themes in open answers and reviews", "Topic clustering, human-checked", "Survey text, public reviews", "Weekly themes", "P3 onward", "Researcher checks 10% sample"),
]
w("models.csv", ["ds_id", "model", "question", "method", "inputs", "output", "phase", "acceptance", "source"], [list(d) + ["plan 5.5" if d[0] == "DS_SIM" else "SC"] for d in ds])

# ---------- experiments ----------
ex = [
 ("EXP_01", "Death-recovery prompt wording", "Shard-ghost hint text A vs B", "Recovery rate of dropped Ember", "KPI_R35", "Text only"),
 ("EXP_02", "Tutorial order", "Ward before Breath vs Breath before Ward", "Onboarding completion", "KPI_R35", "Live config"),
 ("EXP_03", "Echo summon cost", "Current vs 25% cheaper", "Boss quit rate", "KPI_R08", "Solo only"),
 ("EXP_04", "Strike matchmaking wait cap", "90 s vs 60 s before widening", "Match quality vs wait", "KPI_06", "Playlist"),
 ("EXP_05", "Season track XP pace", "Current vs +10% early weeks", "Week-4 activity", "KPI_04", "No paid effect"),
 ("EXP_06", "Store tab placement", "Hub tab order", "Store views without lower retention", "KPI_03", "Retention is a guardrail"),
]
w("experiments.csv", ["exp_id", "name", "variants", "primary_metric", "guardrail", "notes", "rules"], [list(e) + ["SC. Never test combat numbers in PvP or difficulty in boss fights for some players only; never test prices; guardrails KPI_01 and KPI_03 must not drop"] for e in ex])
print("done")

# ---------- data requests (data/ owned by the data thread) ----------
pop = [
 ("POP_PT_DEATH_CLARITY", "prompt", "Death screen", "After respawn fade, playtest builds only (LAB_BUILDFLAG)", "STR_POP_PT_DEATH_CLARITY_T", "", "STR_CMN_YES; STR_CMN_NO", "Did you know why you died?"),
 ("POP_PT_DEATH_FAIR", "prompt", "Death screen", "After a No on POP_PT_DEATH_CLARITY", "STR_POP_PT_DEATH_FAIR_T", "", "1 to 5 scale", "Was that death fair?"),
 ("POP_PT_BOSS", "prompt", "HUD", "Boss kill or leaving the arena, playtest builds only", "STR_POP_PT_BOSS_T", "STR_POP_PT_BOSS_B", "1 to 5 scale x2", "Rate this fight|How much did you enjoy it, and how fair did it feel?"),
 ("POP_PT_SESSION", "modal", "Pause menu", "Quit to menu, playtest builds only", "STR_POP_PT_SESSION_T", "STR_POP_PT_SESSION_B", "1 to 5 scale x2; Yes/No", "Before you go|How fun was this session? Do you want to keep playing? Were you ever unsure what to do next?"),
 ("POP_PT_BUG", "toast", "HUD", "Bug hotkey pressed, playtest builds only", "STR_POP_PT_BUG_T", "", "", "Bug marked. Thanks."),
 ("POP_LIVE_PULSE", "modal", "Hub", "Once a season after 3 h that season, only with OPT_TELEMETRY on; skippable", "STR_POP_LIVE_PULSE_T", "STR_POP_LIVE_PULSE_B", "1 to 5 scale; STR_CMN_SKIP", "Quick question|How are you enjoying this season?"),
]
w("popups_requests.csv", ["popup_id", "kind", "screen", "trigger", "title_str", "body_str", "buttons", "text_en"], pop)
st = []
for p in pop:
    parts = p[7].split("|")
    st.append([p[4], p[2], parts[0], int(len(parts[0]) * 1.4) + 1, "", "Research survey popup"])
    if p[5]:
        st.append([p[5], p[2], parts[1], int(len(parts[1]) * 1.4) + 1, "", "Research survey popup"])
w("strings_requests.csv", ["str_id", "screen", "text_en", "max_chars", "tokens", "notes"], st)
w("data-requests.csv", ["dr_id", "owner_table", "current_value", "requested_value", "reason", "doc"], [
 ["RES-DR-001", "ui/popups.csv (via ui/gen)", "No survey prompts", "Add the 6 rows in design/research/popups_requests.csv; 5 are playtest-build only", "In-build surveys for KPI_R01, KPI_R40, KPI_R52", "survey_items.csv"],
 ["RES-DR-002", "ui/strings.csv (via ui/gen)", "No survey strings", "Add the rows in design/research/strings_requests.csv (max_chars = English x 1.4)", "Text for RES-DR-001", "strings_requests.csv"],
 ["RES-DR-003", "items, actors and world tables", "No analytics tag", "No new column needed: telemetry keys on existing IDs (ATK_, MOV_, ACT_BOSS_, LOC_, QST_, XPA_, ITM_); keep IDs stable after Gate 4 or publish a rename map", "KPI history breaks if IDs change", "kpis.csv"],
])
