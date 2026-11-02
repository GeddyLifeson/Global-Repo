"""B07: turns data/input/*.csv into Content/Python/sf_input_spec.json for sf_build_input.py.

Gamepad keys come from the xbox column (PS5 is the same physical layout). Presets come from
input_preset_bindings.csv as per-column overrides of the default rows.
"""
import csv
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT.parent / "data/input"
OUT = ROOT / "Content/Python/sf_input_spec.json"

PAD = {"A": "Gamepad_FaceButton_Bottom", "B": "Gamepad_FaceButton_Right", "X": "Gamepad_FaceButton_Left",
       "Y": "Gamepad_FaceButton_Top", "LB": "Gamepad_LeftShoulder", "RB": "Gamepad_RightShoulder",
       "LT": "Gamepad_LeftTriggerAxis", "RT": "Gamepad_RightTriggerAxis", "LS click": "Gamepad_LeftThumbstick",
       "RS click": "Gamepad_RightThumbstick", "Menu": "Gamepad_Special_Right", "View": "Gamepad_Special_Left",
       "D-pad up": "Gamepad_DPad_Up", "D-pad down": "Gamepad_DPad_Down", "D-pad left": "Gamepad_DPad_Left",
       "D-pad right": "Gamepad_DPad_Right", "RS flick": "Gamepad_Right2D", "LS flick": "Gamepad_Left2D"}
KBM = {"Esc": "Escape", "Enter": "Enter", "Space": "SpaceBar", "Tab": "Tab", "Delete": "Delete", "F5": "F5",
       "Caps Lock": "CapsLock", "Left Shift": "LeftShift", "Left Ctrl": "LeftControl", "Ctrl": "LeftControl",
       "Left Alt": "LeftAlt", "Page Up": "PageUp", "Page Down": "PageDown", "LMB": "LeftMouseButton",
       "LMB on panel": "LeftMouseButton", "RMB": "RightMouseButton", "MMB": "MiddleMouseButton",
       "Mouse4": "ThumbMouseButton", "Mouse5": "ThumbMouseButton2", "Mouse wheel": "MouseWheelAxis",
       "Mouse wheel up": "MouseScrollUp", "Mouse wheel down": "MouseScrollDown", "Mouse": "Mouse2D",
       "Mouse flick": "Mouse2D", "Semicolon": "Semicolon", "Slash": "Slash", "Apostrophe": "Apostrophe",
       "Home": "Home", "End": "End", "Right Ctrl": "RightControl", "Right Shift": "RightShift", "Right Alt": "RightAlt", "LMB drag": "Mouse2D", "Mouse (RMB held)": "Mouse2D"}
KBM.update({c: c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"})
KBM.update({f"Num{i}": f"NumPad{n}" for i, n in enumerate(["Zero", "One", "Two", "Three", "Four", "Five"])})
KBM.update(zip("123456789", ["One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine"]))
DIRECTIONS = {"WASD": ("W", "S", "A", "D"), "Arrow keys": ("Up", "Down", "Left", "Right"),
              "IJKL": ("I", "K", "J", "L"),
              "Face buttons": ("Gamepad_FaceButton_Top", "Gamepad_FaceButton_Bottom", "Gamepad_FaceButton_Left",
                               "Gamepad_FaceButton_Right"),
              "D-pad": ("Gamepad_DPad_Up", "Gamepad_DPad_Down", "Gamepad_DPad_Left", "Gamepad_DPad_Right")}
# up, down, left, right as modifiers that turn a 1D key into a 2D direction
SWIZZLE = ["SwizzleAxis", {"order": ["enum", "InputAxisSwizzle", "YXZ"]}]
NEGATE = ["Negate", {}]
DIRECTION_MODS = ([SWIZZLE], [SWIZZLE, NEGATE], [NEGATE], [])
STICKS = {"LS": "Gamepad_Left", "RS": "Gamepad_Right"}
COLUMNS = (("xbox", PAD), ("kbm", KBM), ("kbm_alt", KBM))
UP_KEYS = {"W", "Gamepad_DPad_Up", "PageUp"}
TRIGGER_KEYS = {"Gamepad_LeftTriggerAxis", "Gamepad_RightTriggerAxis"}
BUTTON_TRIGGERS = {"press": "Pressed", "release": "Released", "chord": "Pressed"}
UNBOUND = {"-", "unbound", "platform keyboard", "stick tilt", "via pause hub"}
MOUSE_CHORDS = {"Mouse (RMB held)": "RMB", "LMB drag": "LMB"}

def rows(name):
    with open(DATA / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


TIMING = {r["id"]: float(r["value"]) for r in rows("input_timing.csv")}
ACTIONS = rows("input_actions.csv")
skipped = []


def split_note(binding):
    """'Esc (hold 0.4 s)' -> ('Esc', 'hold 0.4 s'); gameplay conditions like 'after a block' are dropped."""
    binding = binding.replace(" after a block", "")
    if binding in MOUSE_CHORDS:
        return binding, ""
    m = re.fullmatch(r"(.*?) \((.*)\)", binding)
    return (m[1], m[2]) if m else (binding, "")


def value_type(r):
    if r["trigger"] in ("axis", "flick"):
        return "Axis1D" if r["xbox"] in ("LT", "RT") or r["kbm"] in ("W / S", "A / D", "W", "S") else "Axis2D"
    return "Axis1D" if " / " in r["xbox"] else "Boolean"


def triggers(r, note, hold_keys, key):
    hold = re.search(r"hold ([\d.]+)", note)
    if r["trigger"] == "hold" and not r["hold_s"]:
        return []
    if r["trigger"] == "hold" or hold or note == "hold":
        seconds = float(r["hold_s"] or (hold[1] if hold else TIMING["TIM_TAP_HOLD"]))
        return [["Hold", {"hold_time_threshold": seconds, "is_one_shot": True}]]
    if note == "tap" or (r["trigger"] in ("press", "release") and key in hold_keys):
        return [["Tap", {"tap_release_time_threshold": hold_keys.get(key, TIMING["TIM_TAP_HOLD"])}]]
    return [[BUTTON_TRIGGERS[r["trigger"]], {}]] if r["trigger"] in BUTTON_TRIGGERS else []


def stick_mods(prefix, axial, look):
    lo, hi = (TIMING["DZ_LS_INNER"], TIMING["DZ_LS_OUTER"]) if prefix == "Gamepad_Left" else (TIMING["DZ_RS_INNER"], TIMING["DZ_RS_OUTER"])
    mods = [["DeadZone", {"lower_threshold": lo, "upper_threshold": hi,
                          "type": ["enum", "DeadZoneType", "AXIAL" if axial else "RADIAL"]}]]
    if look:
        exp = TIMING["LOOK_CURVE"]
        mods.append(["ResponseCurveExponential", {"curve_exponent": ["vec", exp, exp, 1.0]}])
    return mods


def keys(r, token, table, vtype):
    """(key, name suffix, modifiers) for one binding alternative."""
    if token in STICKS:
        if vtype == "Axis2D":
            return [(STICKS[token] + "2D", "", stick_mods(STICKS[token], False, re.search(r"(LOOK|AIM|ORBIT)$", r["action_id"])))]
        axis = "X" if r["kbm"] == "A / D" else "Y"
        return [(STICKS[token] + axis, "", stick_mods(STICKS[token], True, False))]
    if token in DIRECTIONS:
        if vtype == "Axis2D":
            return [(k, "_" + d, m) for k, d, m in zip(DIRECTIONS[token], ("UP", "DOWN", "LEFT", "RIGHT"), DIRECTION_MODS)]
        signs = ([], [NEGATE], [NEGATE], []) if vtype == "Axis1D" else ([],) * 4
        return [(k, "", m) for k, m in zip(DIRECTIONS[token], signs)]
    if token in table:
        return [(table[token], "", [])]
    parts = re.sub(r"^D-pad (\w+) / (\w+)$", r"D-pad \1 / D-pad \2", token).split(" / ")
    if len(parts) > 1:
        found = [k for p in parts for k in keys(r, p, table, vtype)]
        if vtype == "Axis1D" and len(found) == 2:
            neg = 1 if found[0][0] in UP_KEYS else 0
            return [(k, ("_NEG", "_POS")[i != neg], m + ([NEGATE] if i == neg else []))
                    for i, (k, _, m) in enumerate(found)]
        return found
    skipped.append(f"{r['action_id']}: {token}")
    return []


def chord_action(entries, ctx, mod, helpers):
    for r, col, _ in entries:
        if r["trigger"] == "hold" and not r["hold_s"] and r[col] == mod:
            return r["action_id"]
    helper = f"IA_{ctx[4:]}_MOD_{mod.upper().replace(' ', '_')}"
    helpers[helper] = ((PAD if mod in PAD else KBM)[mod], [])
    return helper


def build_context(ctx, entries, vtypes, helpers):
    """Mappings for one context; entries are (row, column, key table) with any preset override applied."""
    hold_keys = {}
    for r, col, table in entries:
        base, _ = split_note(r[col])
        if r["trigger"] == "hold" and r["hold_s"] and base in table:
            hold_keys[table[base]] = float(r["hold_s"])
    maps = []
    for r, col, table in entries:
        base, note = split_note(r[col])
        if not base or base in UNBOUND:
            continue
        vtype, chord = vtypes[r["action_id"]], None
        if "+" in base:
            mod, base = base.split("+")
            chord = chord_action(entries, ctx, mod, helpers)
        elif base in MOUSE_CHORDS:
            chord = chord_action(entries, ctx, MOUSE_CHORDS[base], helpers)
        for key, suffix, mods in keys(r, base, table, vtype):
            if r["trigger"] == "double_tap":
                tap = f"IA_{ctx[4:]}_TAP_{key.upper()}"
                helpers[tap] = (key, [["Tap", {"tap_release_time_threshold": TIMING["TIM_TAP_HOLD"]}]])
                trig = [["Combo", {"combo_actions": ["combo", tap, TIMING["TIM_DOUBLE_TAP"], 2]}]]
            else:
                trig = [] if vtype == "Axis2D" else triggers(r, note, hold_keys, key)
            if chord:
                trig = [["ChordAction", {"chord_action": ["action", chord]}]] + trig
            if key in TRIGGER_KEYS:
                if vtype == "Boolean":
                    trig = trig or [["Down", {}]]
                    for t in trig:
                        t[1]["actuation_threshold"] = TIMING["DZ_TRIGGER"]
                else:
                    mods = [["DeadZone", {"lower_threshold": TIMING["DZ_TRIGGER"], "upper_threshold": 1.0,
                                          "type": ["enum", "DeadZoneType", "AXIAL"]}]] + mods
            maps.append({"action": r["action_id"], "key": key, "triggers": trig, "modifiers": mods,
                         "name": r["action_id"] + suffix if r["remappable"] == "Y" else ""})
    return maps


def build():
    """IMC_<ctx> for the default map, plus IMC_<ctx>_<preset> for each preset that changes that context."""
    vtypes = {r["action_id"]: value_type(r) for r in ACTIONS}
    overrides = defaultdict(dict)
    for o in rows("input_preset_bindings.csv"):
        col = "xbox" if o["column"] == "pad" else o["column"]
        change = {col: o["binding"]}
        if o["trigger"]:
            change.update(trigger=o["trigger"], hold_s=o["hold_s"])
        overrides[o["preset_id"]][(o["action_id"], col)] = change
    by_ctx = defaultdict(list)
    for r in ACTIONS:
        by_ctx[r["ctx_id"]].append(r)
    contexts, helpers = {}, {}
    for preset, changes in [("", {})] + sorted(overrides.items()):
        for ctx, ctx_rows in by_ctx.items():
            if preset and not any((r["action_id"], c) in changes for r in ctx_rows for c, _ in COLUMNS):
                continue
            entries = [({**r, **changes.get((r["action_id"], col), {})}, col, table) for r in ctx_rows for col, table in COLUMNS]
            ctx_helpers = {}
            maps = build_context(ctx, entries, vtypes, ctx_helpers)
            maps += [{"action": h, "key": k, "triggers": t, "modifiers": [], "name": ""} for h, (k, t) in ctx_helpers.items()]
            contexts["IMC" + ctx[3:] + ("_" + preset[4:] if preset else "")] = maps
            helpers.update(ctx_helpers)
    actions = [{"id": a, "type": t} for a, t in vtypes.items()] + [{"id": h, "type": "Boolean"} for h in helpers]
    return {"actions": actions, "contexts": contexts, "skipped": sorted(set(skipped))}


spec = build()
OUT.write_text(json.dumps(spec, indent=1) + "\n", newline="\n")
print(f"{len(spec['actions'])} actions, {len(spec['contexts'])} contexts, "
      f"{sum(map(len, spec['contexts'].values()))} mappings; skipped: {', '.join(spec['skipped'])}")
