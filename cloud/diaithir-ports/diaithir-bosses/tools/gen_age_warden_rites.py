#!/usr/bin/env python3 -I
# S6832 Rite chains for the Age Wardens (one per Age I-VI and VIII; AGE_BALANCE.md). Same step format as gen_ascendant.py (ritual/<id>.json),
# clues in lang ritual.diaithirbosses.<id>.<n>, Codex hints in codex/ritual_hints_wardens.json, quests in quests/age_wardens.json.
# Own files, so gen_ascendant.py reruns do not touch them. Warden profiles (boss/<id>.json, summon.rite = ascendant_altar) belong to the mobs thread.
import json, os, random
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NS = "diaithirbosses"
AS, DA = f"{ROOT}/src/main/resources/assets/{NS}", f"{ROOT}/src/main/resources/data/{NS}"
TREE_RIDDLE = ["the pale one that wears the first white", "red berries set against the witch", "the one that bleeds when it is cut", "the weeper by the water",
               "kin of the tree that holds up the world", "the gate the Fair Folk keep", "the door-wood, the strong one", "the winter king, green when all is grey", "the nut of the one who knows"]
HOURS = {"midnight": (17000, 19000, "when the moon stands highest over the stone"), "dawn": (23000, 1000, "in the breath between night and the first light"),
         "dusk": (12000, 13500, "as the sun drowns and the first stars wake"), "noon": (5500, 6500, "when no shadow falls beside the stone")}
ROM = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI", 8: "Rodos"}
# age -> (offer item, count, offer clue, hunt mob, count, hunt clue, stones, hour, defend s, coop, wave mobs, feast)
RITE = {
    1: ("minecraft:flint", 16, "The first hearth was ringed with flint. Sixteen chips, laid at the foot of the stone.", "minecraft:zombie", 6,
        "The walking dead guard the old fire-ring. Let six fall in sight of the altar.", 2, "dawn", 30, 0, ["minecraft:zombie"], False),
    2: ("minecraft:copper_ingot", 16, "The green metal came before the bright one. Sixteen ingots, warm from the pot.", "minecraft:skeleton", 10,
        "Bone-archers keep the ore roads. Ten must be unstrung.", 2, "dusk", 40, 0, ["minecraft:skeleton", "minecraft:zombie"], False),
    3: ("#c:ingots/bronze", 8, "Two soft metals made one hard. Eight bronze bars upon the stone.", "minecraft:spider", 12,
        "The weavers of the dark hollows resent the smiths. Twelve of them fewer.", 3, "noon", 45, 0, ["minecraft:spider", "minecraft:cave_spider"], True),
    4: ("minecraft:iron_ingot", 24, "The grey metal rings truer than the bronze. Twenty-four ingots, cold and plain.", "minecraft:witch", 5,
        "The brewers who sold the smiths their ruin. Five must answer.", 3, "midnight", 60, 0, ["minecraft:zombie", "minecraft:skeleton", "minecraft:witch"], True),
    5: ("#c:ingots/steel", 8, "Iron taught to bend and not break. Eight steel bars for the warden's gate.", "minecraft:creeper", 15,
        "The hissing ones undo what smiths make. Fifteen must be put out.", 4, "dawn", 75, 2, ["minecraft:creeper", "minecraft:zombie", "minecraft:skeleton"], True),
    6: ("minecraft:redstone_block", 8, "The late age runs on red dust and wire. Eight blocks, packed and dull.", "minecraft:enderman", 8,
        "Tall walkers step between the wires. Eight must lose their footing.", 4, "noon", 90, 2, ["minecraft:enderman", "minecraft:skeleton", "minecraft:zombie"], True),
    8: ("minecraft:echo_shard", 6, "The last Age answers in echoes. Six shards, still ringing.", "minecraft:phantom", 12,
        "Sleepless watchers circle the end of days. Twelve must fall.", 5, "midnight", 105, 3, ["minecraft:phantom", "minecraft:skeleton", "minecraft:enderman"], True),
}
lang = json.load(open(f"{AS}/lang/en_us.json", encoding="utf8"))
hints, quests = [], [dict(id="age_wardens/rite", title="Wake an Age Warden", text="Each Age keeps a Warden. Raise an Ascendant altar and follow the clues of its rite.", after=[], kind="build")]
for age, (oi, oc, oclue, hm, hc, hclue, ns, hour, dsec, coop, wave, feast) in RITE.items():
    bid = f"age_warden_{age}"
    rnd = random.Random("warden:" + bid)
    seq = [rnd.randrange(9) for _ in range(ns)]
    for i in range(1, ns):
        while seq[i] == seq[i - 1]: seq[i] = rnd.randrange(9)
    a, b, hclue_t = HOURS[hour]
    steps, clues = [], []
    if feast:
        steps.append(dict(type="offer", item="#diaithirbosses:offering_feast", count=1)); clues.append("The altar eats before it fights. Set one feast upon the stone, a dish worth a guest-gift.")
    steps += [dict(type="offer", item=oi, count=oc), dict(type="hunt", mob=hm, count=hc), dict(type="stones", sequence=seq), dict(type="hour", **{"from": a, "to": b})]
    clues += [oclue, hclue, "Trees stand in the stone's mind. Seal them in this order, no other: " + "; then ".join(TREE_RIDDLE[r] for r in seq) + ".", f"The stone will answer only {hclue_t}. Use the altar then."]
    if coop:
        steps.append(dict(type="coop", players=coop)); clues.append(f"It will not wake for one hand. {coop} must stand at the altar together, or the stone will take a token for every spirit that stands in for a friend.")
    steps.append(dict(type="defend", seconds=dsec, mobs=wave)); clues.append(f"Whatever you woke will come to see who woke it. Hold the altar for {dsec} breaths of the sun-count and do not leave it.")
    os.makedirs(f"{DA}/ritual", exist_ok=True)
    json.dump({"boss": bid, "steps": steps}, open(f"{DA}/ritual/{bid}.json", "w", encoding="utf8"), indent=1)
    for i, c in enumerate(clues):
        lang[f"ritual.{NS}.{bid}.{i}"] = c
        qid = f"age_wardens/rite_{bid}_{i}"
        hints.append({"boss": bid, "step": i, "quest": qid, "text": c})
        quests.append(dict(id=qid, title=f"Warden of Age {ROM[age]}: step {i + 1}", text=c, after=[f"age_wardens/rite_{bid}_{i - 1}"] if i else ["age_wardens/rite"], kind="ritual_step", boss=bid, step=i))
json.dump(lang, open(f"{AS}/lang/en_us.json", "w", encoding="utf8"), indent=1, ensure_ascii=False)
os.makedirs(f"{ROOT}/codex", exist_ok=True)
json.dump({"_doc": "Codex Rites page, Age Wardens. Same shape as ritual_hints.json; text equals the in-game clue.", "hints": hints}, open(f"{ROOT}/codex/ritual_hints_wardens.json", "w", encoding="utf8"), indent=1, ensure_ascii=False)
os.makedirs(f"{DA}/quests", exist_ok=True)
json.dump({"tab": "Bosses", "quests": quests}, open(f"{DA}/quests/age_wardens.json", "w", encoding="utf8"), indent=1, ensure_ascii=False)
print(len(RITE), "wardens,", len(hints), "clues")
