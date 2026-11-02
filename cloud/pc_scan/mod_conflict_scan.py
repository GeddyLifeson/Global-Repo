"""Find mods that conflict with the Tellus fork's chunk generator, by boot test.
Usage: python -I mod_conflict_scan.py            (long: one server boot per candidate; run in the background, log to a file)
"""
import json, re, shutil, subprocess, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import boot_headroom, rcon, serverctl

SRC = Path(r"E:\MCTest\server\mods")
DST = serverctl.SERVER_DIR / "mods"
OFF = serverctl.SERVER_DIR / "mods_disabled"
OUR = ["Tellus-neoforge-26.1.2-0.8.3-diaithir.1.jar", "diaithir-ages-neoforge-26.1.2-0.1.0.jar"]
SUSPECT_PREFIXES = ("terrablender", "terralith", "tectonic", "biomesoplenty", "regions-unexplored", "lithostitched",
                    "nullscape", "nomorecraters", "[neoforge]ctov", "distanthorizons")
PROBES = {
    "spawn": "diaithir_probe 56.982 -10.0145",
    "dogger": "diaithir_probe 55.0 2.5",
    "deep": "diaithir_probe 45.0 -20.0",
}


def suspects(files):
    return [f for f in files if f.lower().startswith(SUSPECT_PREFIXES)]


def verdict(p):
    bad = []
    s, d, o = p.get("spawn"), p.get("dogger"), p.get("deep")
    if not s or s.get("ocean") or s.get("overlay", 0) < 0.99 or s.get("relM", -1) < 2:
        bad.append(f"spawn not island land: {s}")
    if not d or d.get("ocean") or d.get("relM", -1) < 40:
        bad.append(f"dogger bank not dry: {d}")
    if not o or not o.get("ocean"):
        bad.append(f"deep atlantic not ocean: {o}")
    return bad


DROPPED = ("tellus", "walled-city-structure", "biomesoplenty-neoforge-26.1.2-26.1.2.0.22")
PINNED = {  # release decisions in docs/release/OVERRIDE_JARS.md; the replacement must be a local file
    "BiomesOPlenty-neoforge-26.1.2-26.1.2.0.21.jar": Path(r"E:\DiaithirRPG_release\0.1.0\prism_test\Diaithir\minecraft\mods"),
    "Terralith_26.1_v2.6.4_Neoforge.jar": Path(r"E:\DiaithirRPG_release\pinned"),
}
DEEP_WORLDS = Path(r"C:\Users\imarl\curseforge\minecraft\Instances\ATM11 - Deep Worlds")


def base_mod(name):
    """True for a Deep Worlds server jar that goes into the Diaithir set unchanged."""
    low = name.lower()
    return not low.startswith(DROPPED) and not low.startswith("terralith")


def sync_base():
    DST.mkdir(exist_ok=True)
    OFF.mkdir(exist_ok=True)
    for f in DST.glob("*.jar"):
        f.unlink()
    for f in OFF.glob("*.jar"):
        f.unlink()
    for f in SRC.glob("*.jar"):
        if base_mod(f.name):
            shutil.copy2(f, DST / f.name)
    for name, folder in PINNED.items():
        if (folder / name).exists():
            shutil.copy2(folder / name, DST / name)
        else:
            print(f"PINNED JAR MISSING: {name} (looked in {folder})", flush=True)
    shutil.copy2(Path(r"E:\MCTest\tellus_port\src\mc261-neoforge\build\libs") / OUR[0], DST / OUR[0])
    shutil.copy2(Path(r"E:\DiaithirRPG\engine\build\libs") / OUR[1], DST / OUR[1])


def sync_content():
    """Deep Worlds KubeJS and config (minus its zz_test_ scripts), then the Age I content and economy, then the guarded burning.js."""
    srv = serverctl.SERVER_DIR
    skip = shutil.ignore_patterns("zz_test_*")
    shutil.copytree(Path(r"E:\MCTest\server\kubejs"), srv / "kubejs", dirs_exist_ok=True, ignore=skip)
    shutil.copytree(Path(r"E:\MCTest\server\config"), srv / "config", dirs_exist_ok=True)
    subprocess.run([sys.executable, "-I", r"E:\DiaithirRPG\tools\age1\install.py", "--kubejs", str(srv / "kubejs")], check=True)
    shutil.copy2(DEEP_WORLDS / "kubejs" / "server_scripts" / "diaithir" / "burning.js", srv / "kubejs" / "server_scripts" / "diaithir" / "burning.js")


def boot_and_probe():
    """Returns (status, failures, tail). status in done|crash|timeout. Exits (BLOCKED) if the PC never has 10 GB commit headroom."""
    if not boot_headroom.wait(10.0):
        raise SystemExit("BLOCKED: commit headroom below 10 GB for 60 min")
    pid = serverctl.start()
    status = serverctl.wait_done(900)
    failures, tail = [], ""
    if status == "done":
        pr = serverctl.read_props()
        r = rcon.Rcon("127.0.0.1", int(pr["rcon.port"]), pr["rcon.password"])
        try:
            res = {k: rcon.parse_kv_line(r.command(c)) for k, c in PROBES.items()}
            failures = verdict(res)
        finally:
            serverctl.stop(r, pid)
    else:
        text = serverctl.LOG.read_text(encoding="utf8", errors="replace") if serverctl.LOG.exists() else ""
        tail = "\n".join(l for l in text.splitlines() if re.search(r"ERROR|Exception|Missing|Caused by", l))[-1500:]
        subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True)   # only the PID we started
    wipe_world()
    return status, failures, tail


def wipe_world():
    w = serverctl.SERVER_DIR / "world"
    if w.exists():
        shutil.rmtree(w)


def disable(name):
    shutil.move(str(DST / name), str(OFF / name))


def enable(name):
    shutil.move(str(OFF / name), str(DST / name))


def main():
    sync_base()
    sync_content()
    log = []
    status, fails, tail = boot_and_probe()
    log.append(("FULL SET", status, fails, tail))
    if status == "done" and not fails:
        print("full set passes; nothing to disable")
    else:
        names = suspects([f.name for f in DST.glob("*.jar")])
        for n in names:
            disable(n)
        status, fails, tail = boot_and_probe()
        log.append(("SUSPECTS OFF", status, fails, tail))
        if status != "done" or fails:
            print("still failing with suspects off; see log, stopping for a human"); dump(log); return 2
        for n in names:
            enable(n)
            status, fails, tail = boot_and_probe()
            log.append((f"+{n}", status, fails, tail))
            if status != "done" or fails:
                disable(n)
    dump(log)
    return 0


def dump(log):
    lines = ["# Mod conflicts with the Tellus fork (auto-generated by tools/world/mod_conflict_scan.py)", "",
             f"Run: {time.strftime('%Y-%m-%d %H:%M')}", "", "| step | boot | probe failures | evidence |", "|---|---|---|---|"]
    for step, status, fails, tail in log:
        lines.append(f"| {step} | {status} | {'; '.join(fails) or '-'} | {tail.replace(chr(10), ' / ')[:300] or '-'} |")
    lines += ["", "Disabled mods (final): " + ", ".join(sorted(p.name for p in OFF.glob('*.jar'))) if OFF.exists() else ""]
    Path(r"E:\DiaithirRPG\docs\world\conflicts.md").write_text("\n".join(lines), encoding="utf8")


if __name__ == "__main__":
    sys.exit(main())
