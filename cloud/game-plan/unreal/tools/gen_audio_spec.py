"""B27: turns design/audio/*.csv and the sample manifests into Content/Python/sf_audio_spec.json for sf_import_audio.py.

events: one SoundCue per event that has sample files (all its variations, random pick at runtime).
sounds: DT_SfSounds rows. Every event plus every SFX_ hook from sfx_hook_map.csv, and the MetaSounds in metasound_specs.md.
music: DT_SfMusicCues rows parsed from music_cues.csv, plus the region renders of each stinger (MR14).
rules: DA_SfMusicRules values parsed from music_system_rules.csv; a rule whose wording no longer parses stops the run.
"""
import csv
import json
import re
from collections import defaultdict
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
AUDIO = ROOT.parent / "design/audio"
FULL = AUDIO / "samples/full"
OUT = ROOT / "Content/Python/sf_audio_spec.json"
GAME = "/Game/Audio"

# mix_priority.csv tiers by event name; first match wins, anything else is tier 4 (player weapons and abilities)
TIERS = [(r"Tell|Unblockable", 1), (r"_Player_.*(WardBreak|LowHealth|BreathEmpty)", 2), (r"^Play_VO_", 3),
         (r"_Impacts_|Parry|Crit|StanceBreak", 5), (r"_(Enemies|Bosses|Creatures|UV)_", 6), (r"Bark", 7),
         (r"_(PlayerFootsteps|Traversal)_|Foley", 8), (r"^Play_MUS_", 9), (r"^Play_AMB_|_(Ambience|Weather)_", 10),
         (r"_(Ui|UI)_", 11)]


def rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def tier(event):
    return next((t for pattern, t in TIERS if re.search(pattern, event)), 4)


def folder(root, event):
    kind, group = event.split("_")[1:3]
    return f"{GAME}/{root}/{kind}/{group}"


def number(rule, pattern):
    m = re.search(pattern, rule)
    if not m:
        raise SystemExit(f"music_system_rules.csv no longer matches {pattern!r}: {rule}")
    return [float(g) for g in m.groups()] if len(m.groups()) > 1 else float(m[1])


def main():
    cues = {r["cue_id"]: r for r in rows(AUDIO / "music_cues.csv")}
    amb_loop = {"Play_" + r["amb_id"]: "one-shot" not in r["driver"] for r in rows(AUDIO / "ambience_layers.csv")}
    rules = {r["rule_id"]: r for r in rows(AUDIO / "music_system_rules.csv")}
    regions = rules["MR01"]["values"].split()

    files, lengths, sfx_loops = defaultdict(list), defaultdict(float), set()
    for manifest in sorted(FULL.glob("*/manifest.csv")):
        for r in rows(manifest):
            if not r.get("file"):
                continue
            files[r["event_id"]].append(str(PurePosixPath(manifest.parent.name, r["file"])))
            lengths[r["event_id"]] = max(lengths[r["event_id"]], float(r["duration_s"]))
            if r.get("type") == "loop":
                sfx_loops.add(r["event_id"])

    def base_cue(event):
        cue = event[len("Play_"):]
        for suffix in ["_L1", "_L2", "_L3"] + [f"_{g}" for g in regions]:
            if cue.endswith(suffix) and cue[: -len(suffix)] in cues:
                return cue[: -len(suffix)]
        return cue

    def loops(event):
        if event.startswith("Play_MUS_"):
            return cues.get(base_cue(event), {}).get("loop") == "Yes"
        if event.startswith("Play_AMB_"):
            return amb_loop.get(event, True)
        return event in sfx_loops or ("_Ambience_" in event and "OneShots" not in event)

    events = {}
    for event, paths in sorted(files.items()):
        events[event] = {"wave_folder": folder("Waves", event), "cue": f"{folder('Cues', event)}/{event}.{event}", "files": sorted(paths), "loop": loops(event),
                         "priority": 100 - 9 * (tier(event) - 1), "play_when_silent": event.endswith("_L3")}

    sounds = {e: v["cue"] for e, v in events.items()}
    for h in rows(AUDIO / "sfx_hook_map.csv"):
        if h["wwise_event"] in events:
            sounds[h["hook"]] = events[h["wwise_event"]]["cue"]
    metasounds = re.findall(r"^## (MS_\w+)", (AUDIO / "metasound_specs.md").read_text(encoding="utf-8"), re.M)
    sounds.update({m: f"{GAME}/MetaSounds/{m}.{m}" for m in metasounds})

    music = []

    def add_cue(cue, region="", mode="", variant="", level=0, boss="", phase=0, role="Loop", bpm=0.0):
        event = "Play_" + cue
        enrage = events.get(event + "_L3", {}).get("cue", "")
        music.append({"Name": cue, "Region": region, "Mode": mode, "Variant": variant, "Level": level, "Boss": boss,
                      "Phase": phase, "Role": role, "Bpm": bpm, "LengthSeconds": lengths.get(event, 0.0),
                      "Sound": events.get(event, {}).get("cue", ""), "Enrage": enrage})

    for cue, r in cues.items():
        state = dict(kv.split("=") for kv in r["wwise_state"].split("; ") if kv)
        parts = cue.split("_")
        region = parts[1] if parts[1] in regions else ""
        boss = re.match(r"MUS_BOSS_(\w+?)_(INTRO|P\d|T\d|WIN)$", cue)
        mode = state.get("Music_Mode", "Boss" if boss else r["category"].split()[-1].capitalize())
        variant = state.get("Music_Sub", parts[-1] if parts[-1] in ("DAY", "NIGHT") else "")
        if state.get("World_State") == "Hollowed":
            mode, variant = "Explore", "HOLLOWED"
        if region == "HUB" and variant in ("DAY", "NIGHT"):
            mode = "Explore"
        tail = boss[2] if boss else parts[-1]
        role = {"INTRO": "Intro", "WIN": "Win", "END": "End"}.get(tail, "Transition" if re.fullmatch(r"T\d", tail) else
                                                                 "Loop" if r["loop"] == "Yes" else "OneShot")
        if r["category"] == "Stinger" and role != "End":
            role = "Stinger"
        add_cue(cue, region, mode, variant, int(state.get("Combat_Level", 0)), boss[1] if boss else "",
                int(tail[1:]) if boss and tail[0] in "PT" else 0, role, float(r["tempo_bpm"] or 0))
    for event in events:
        cue = event[len("Play_"):]
        if cue not in cues and base_cue(event) != cue and cues[base_cue(event)]["category"] == "Stinger":
            add_cue(cue, region=cue.rsplit("_", 1)[1], mode="Stinger", role="Stinger")

    mr = {k: v["behaviour"] for k, v in rules.items()}
    spec_rules = {
        "mode_priority": re.search(r"Priority ([\w >]+)", mr["MR02"])[1].split(" > "),
        "region_crossfade_seconds": number(mr["MR01"], r"(\d+) s crossfade"),
        "tension_fade_bars": number(mr["MR05"], r"over (\d+) bars"),
        "combat_level_thresholds": number(mr["MR04"], r"0-(\d+) = 1, \d+-(\d+) = 2")[:2],
        "combat_level_down_delay": number(mr["MR04"], r"after (\d+) s below"),
        "combat_end_delay": number(mr["MR07"], r"for (\d+) s"),
        "combat_end_silence": number(mr["MR07"], r"then (\d+) s silence"),
        "enrage_health_percent": number(mr["MR10"], r"below (\d+)% HP"),
        "win_silence_before": number(mr["MR11"], r"([\d.]+) s silence, WIN"),
        "win_silence_after": number(mr["MR11"], r"then (\d+) s silence"),
        "death_fade_seconds": number(mr["MR12"], r"in ([\d.]+) s"),
        "death_stinger": "MUS_STG_" + re.search(r"(\w+) stinger", mr["MR12"])[1],
        "explore_gap_seconds": number(mr["MR13"], r"(\d+)-(\d+) s random silence"),
        "stinger_max_age": number(mr["MR14"], r"older than (\d+) s"),
        "pvp_music_cap_db": number(mr["MR16"], r"capped at (-?\d+) dB"),
        "menu_low_pass_hz": number(mr["MR21"], r"at (\d+) Hz"),
        "menu_duck_db": -number(mr["MR21"], r"duck -(\d+) dB"),
    }
    if spec_rules["death_stinger"] not in cues:
        raise SystemExit(f"MR12 names {spec_rules['death_stinger']}, which is not in music_cues.csv")

    OUT.write_text(json.dumps({"events": events, "sounds": sounds, "music": music, "rules": spec_rules},
                              indent=1), encoding="utf-8")
    print(f"{OUT.name}: {len(events)} events, {sum(len(e['files']) for e in events.values())} files, "
          f"{len(sounds)} sound rows, {len(music)} music cues")


if __name__ == "__main__":
    main()
