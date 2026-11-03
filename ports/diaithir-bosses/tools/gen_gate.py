"""S6873 Adds the Shardfall Gate to diaithir-bosses: lang lines, the Codex quests (quests/gate.json) and the handbook chapter.
Re-runnable; touches only those three files. Run from the module root: python3 -I tools/gen_gate.py"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AS, DA = os.path.join(ROOT, "src/main/resources/assets/diaithirbosses"), os.path.join(ROOT, "src/main/resources/data/diaithirbosses")
gate = json.load(open(os.path.join(DA, "gate.json"), encoding="utf8"))
n, secs = len(gate["keystones"]), gate["defend"]["seconds"]

TEXT = {
    "block.diaithirbosses.shardfall_gate": "Shardfall Gate",
    "gate.diaithirbosses.age": "The Gate does not answer yet. Its Age has not come.",
    "gate.diaithirbosses.locked": "The Gate is shut. Beat The Last Wheel and clear the rush first.",
    "gate.diaithirbosses.missing": "%s of %s keystones are in. Still missing: %s.",
    "gate.diaithirbosses.keystone": "A keystone is taken. %s of %s are in.",
    "gate.diaithirbosses.wrong_hour": "The Gate does not answer at this hour. Use it at midnight.",
    "gate.diaithirbosses.hour_done": "The Gate answers. Use it again and hold it for %s seconds.",
    "gate.diaithirbosses.defend_start": "The waves come. Hold the Gate for %s seconds.",
    "gate.diaithirbosses.defend_failed": "The Gate was left alone. Use it again to restart the hold.",
    "gate.diaithirbosses.progress": "%s of %s seconds.",
    "gate.diaithirbosses.opened": "The Shardfall Gate is open.",
    "gate.diaithirbosses.open": "The Shardfall Gate is open.",
}
QUESTS = [
    ("gate/price", "The Gate's price", "Beat The Last Wheel and clear the boss rush. The Gate stays shut until both are done.", ["ascendant/tier3", "ascendant/rush"], "event", "boss_rush_cleared"),
    ("gate/keystones", "The keystones", f"The Gate takes {n} keystones, one for each system of the world. Sneak-use the Gate with an item to give it; some are known to it already. Use the Gate bare-handed to see what is missing.", ["gate/price"], "event", "gate_keystones_complete"),
    ("gate/hour", "The hour", "Use the Gate at midnight.", ["gate/keystones"], "event", "gate_hour_done"),
    ("gate/hold", "The hold", f"Hold the Gate for {secs} seconds against the waves. Do not leave it.", ["gate/hour"], "event", "gate_hold_done"),
    ("gate/open", "The Shardfall Gate", "The Gate is open.", ["gate/hold"], "event", "shardfall_gate_open"),
]

def rw(path, fn):
    d = json.load(open(path, encoding="utf8")) if os.path.exists(path) else None
    d = fn(d)
    json.dump(d, open(path, "w", encoding="utf8"), indent=1, ensure_ascii=False)

rw(os.path.join(AS, "lang/en_us.json"), lambda d: {**d, **TEXT})
rw(os.path.join(DA, "quests/gate.json"), lambda d: {"tab": "Bosses", "quests": [
    {"id": i, "title": t, "text": x, "after": a, "kind": k, "event": e, "age": "RODOS"} for i, t, x, a, k, e in QUESTS]})
def codex(d):
    d["chapters"] = [c for c in d["chapters"] if c.get("tier") != "gate"]
    d["chapters"].append({"tier": "gate", "name": "The Shardfall Gate", "age": "RODOS", "text": " ".join(q[2] for q in QUESTS[:4]), "items": [
        {"id": "diaithirbosses:shardfall_gate", "name": "Shardfall Gate", "age": "RODOS", "text": ""}]})
    return d
rw(os.path.join(ROOT, "codex/bosses_handbook.json"), codex)
