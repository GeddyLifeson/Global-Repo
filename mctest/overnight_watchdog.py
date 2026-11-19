# S6990 Stage-based overnight test watchdog for the MCTestServer w28 server and Prism client (review G2-G15). Stdlib only, Windows.
# Usage: python overnight_watchdog.py [--config cfg.json] run | preflight | dry-run <server_log> [client_log]
# Dry-run only reads logs. `run` launches Java and so is for the PC overnight window only (2 AM-4 PM Chicago, Marlon asleep). UNTESTED live.
import sys, os, re, json, time, glob, socket, struct, subprocess, zipfile, ctypes, datetime, pathlib

CFG = dict(
    root=r"C:\MCTestServer", world="w28", report_dir=r"C:\MCTestServer\test_reports\w28\overnight",
    server_cmd=[r"java", "@user_jvm_args.txt", "-Xlog:gc*:file=logs/gc.log:time,uptime:filecount=2,filesize=20m",
                r"@libraries/net/neoforged/neoforge/26.1.2.116/win_args.txt", "nogui"],
    client_cmd=[],            # Prism launch line, e.g. [r"E:\Prism\prismlauncher.exe","-d",r"E:\Prism","-l","Diaithir_w28"]
    client_dir=r"E:\Prism\instances\Diaithir_w28\.minecraft",
    client_gc_log="logs/gc.log",  # relative to client_dir; add the -Xlog flag in the instance JVM args
    player="Uber_Byte", rcon_port=25576, game_port=25566,
    min_free_ram_gb=20, min_free_commit_gb=24, min_free_disk_gb=20, client_start_free_ram_gb=10,
    dt_jar="dungeons-and-taverns-5.2.0.jar", dt_jar_size=39393055,
    library_jars=["ScalableCatsForce-NeoForge-6.1.1-mc26.1.2-3.9.0-all.jar"],
    hard_stop="05:30", max_failures=2, poll_s=60)

# (name, regex, budget_s [from previous stage passing], must_match_also)
SERVER_STAGES = [
    ("FML start", r"Starting FancyModLoader version", 60, None),
    ("NeoForge load", r"NeoForge mod loading, version 26\.1\.2\.116", 120, None),
    ("KubeJS startup", r"Loaded 19/19 KubeJS startup scripts.*with 0 errors", 120, None),
    ("KubeJS server", r"Loaded 28/28 KubeJS server scripts.*with 0 errors", 240, None),
    ("MC start", r"Starting minecraft server version 26\.1\.2", 240, None),
    ("Done", r"Done \(", 300, None),
    ("RCON up", r"RCON running on 127\.0\.0\.1:", 60, None)]
SERVER_FAIL = [r"Missing or unsupported mandatory dependencies", r"Skipping jar\. File mods/", r"java\.lang\.OutOfMemoryError",
    r"Encountered an unexpected exception", r"This crash report has been saved to", r"Failed to start the minecraft server"]
CLIENT_STAGES = [
    ("FML start", r"Starting FancyModLoader version .*CLIENT in PROD", 120, None),
    ("NeoForge load", r"NeoForge mod loading, version", 300, None),
    ("KubeJS", r"Loaded 19/19 KubeJS startup scripts", 300, None),
    ("User+LWJGL", r"Setting user: Uber_Byte", 600, None),
    ("Resource reload", r"Reloading ResourceManager:", 300, None),
    # stage 6 (silent) is judged from gc.log, see gc_verdict; the next pattern has a 25 min budget
    ("Sound/atlas", r"OpenAL initialized|Sound engine started|Created: 16384x16384x2 minecraft:textures/atlas/blocks\.png-atlas", 1500, None),
    ("Connecting", r"Connecting to 127\.0\.0\.1, 25566", 300, None)]
CLIENT_FAIL = [r"java\.lang\.OutOfMemoryError", r"Skipping jar\. File mods/", r"WritingException", r"MixinTransformerError"]
JOIN_RE = r"Uber_Byte\[/127\.0\.0\.1:\d+\] logged in with entity id"
JOINED_RE = r"Uber_Byte joined the game"
WIN_FAIL_TITLES = ("Crash Assistant",)

def scan(lines, stages, fail_res):
    """Pure function. Returns (hits, fail): hits = [(stage, line_no, quote)] for stages passed in order; fail = (line_no, quote) or None."""
    hits, i = [], 0
    for n, ln in enumerate(lines, 1):
        for fr in fail_res:
            if re.search(fr, ln): return hits, (n, ln.strip())
        if i < len(stages) and re.search(stages[i][1], ln):
            hits.append((stages[i][0], n, ln.strip())); i += 1
    return hits, None

def gc_verdict(text):
    """Heap after-GC ratios from G1 lines like 'Pause Young ... 7000M->6900M(7168M)'. FAIL if 3 consecutive samples >= 95% of heap."""
    r = [int(m.group(2)) / int(m.group(3)) for m in re.finditer(r"(\d+)M->(\d+)M\((\d+)M\)", text)]
    if len(r) >= 3 and all(x >= 0.95 for x in r[-3:]): return "FAIL", "client heap too small: old gen >= 95% for 3 samples"
    return "OK", f"{len(r)} GC samples, last {r[-1]:.0%}" if r else "no GC samples yet"

# ---- machine probes ----
class MS(ctypes.Structure):
    _fields_ = [("l", ctypes.c_ulong), ("load", ctypes.c_ulong)] + [(k, ctypes.c_ulonglong) for k in ("tp", "ap", "tpf", "apf", "tv", "av", "x")]
def mem():
    m = MS(); m.l = ctypes.sizeof(m); ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)); return m.ap / 2**30, m.apf / 2**30
def java_procs():
    o = subprocess.run(["tasklist", "/FO", "CSV", "/NH"], capture_output=True, text=True).stdout
    return [(r[0], int(r[1]), int(r[4].replace(",", "").replace(" K", "") or 0) / 1024) for r in (l.strip('"').split('","') for l in o.splitlines() if l) if r[0].lower() in ("java.exe", "javaw.exe")]
def free_disk(p): import shutil; return shutil.disk_usage(p).free / 2**30
def port_free(p):
    s = socket.socket()
    try: s.bind(("127.0.0.1", p)); return True
    except OSError: return False
    finally: s.close()
def rcon(port, pw, cmd, t=30):
    def pkt(i, ty, b): b = b.encode() + b"\0\0"; return struct.pack("<iii", len(b) + 8, i, ty) + b
    s = socket.create_connection(("127.0.0.1", port), t); s.settimeout(t)
    def rd():
        n = struct.unpack("<i", s.recv(4))[0]; d = b""
        while len(d) < n: d += s.recv(n - len(d))
        return struct.unpack("<ii", d[:8]), d[8:-2].decode(errors="replace")
    s.sendall(pkt(1, 3, pw)); rd()
    s.sendall(pkt(2, 2, cmd)); r = rd()[1]; s.close(); return r
def rcon_pw(c):  # read at runtime, never printed or stored
    for l in open(os.path.join(c["root"], c["world"], "server.properties"), encoding="utf8"):
        if l.startswith("rcon.password="): return l.split("=", 1)[1].strip()

# ---- preflight ----
def preflight(c):
    bad, ok = [], []
    def chk(name, cond, detail=""): (ok if cond else bad).append(f"{name}: {detail}")
    if os.name != "nt": return ["not Windows: preflight is for the PC"], []
    ram, com = mem()
    chk("no java running", not java_procs(), str(java_procs()))
    chk(f"free RAM >= {c['min_free_ram_gb']} GB", ram >= c["min_free_ram_gb"], f"{ram:.1f}")
    chk(f"free commit >= {c['min_free_commit_gb']} GB", com >= c["min_free_commit_gb"], f"{com:.1f}")
    for d in (c["root"], os.path.splitdrive(c["client_dir"])[0] + "\\"):
        chk(f"disk {d} >= {c['min_free_disk_gb']} GB", free_disk(d) >= c["min_free_disk_gb"], f"{free_disk(d):.1f}")
    chk(f"port {c['game_port']} free", port_free(c["game_port"]))
    w = os.path.join(c["root"], c["world"])
    dt = os.path.join(w, "mods", c["dt_jar"])
    chk("D&T jar size", os.path.exists(dt) and os.path.getsize(dt) == c["dt_jar_size"], dt)
    for label, mods in (("server", os.path.join(w, "mods")), ("client", os.path.join(c["client_dir"], "mods"))):
        nontoml = []
        for j in glob.glob(os.path.join(mods, "*.jar")):
            if os.path.basename(j) in c["library_jars"]: continue
            try:
                with zipfile.ZipFile(j) as z:
                    if "META-INF/neoforge.mods.toml" not in z.namelist(): nontoml.append(os.path.basename(j))
            except zipfile.BadZipFile: nontoml.append(os.path.basename(j) + " (bad zip)")
        chk(f"{label} jars all NeoForge", not nontoml, ", ".join(nontoml[:8]))
    chk("server args file is .116", os.path.exists(os.path.join(w, "libraries/net/neoforged/neoforge/26.1.2.116/win_args.txt")))
    return bad, ok

# ---- run ----
def snap(c, outdir, stage, reason, server_log, client_log, procs):
    d = os.path.join(outdir, f"{datetime.datetime.now():%H%M}_{stage.replace(' ', '_').replace('/', '_')}"); os.makedirs(d, exist_ok=True)
    for name, p in (("server_tail.txt", server_log), ("client_tail.txt", client_log)):
        if p and os.path.exists(p): open(os.path.join(d, name), "w", encoding="utf8").write("".join(open(p, encoding="utf8", errors="replace").readlines()[-60:]))
    ram = os.path.join(outdir, "ram.csv")
    if os.path.exists(ram): open(os.path.join(d, "ram_tail.csv"), "w").write("".join(open(ram).readlines()[-5:]))
    for pid in procs:
        r = subprocess.run(["jcmd", str(pid), "Thread.print"], capture_output=True, text=True)
        open(os.path.join(d, f"threads_{pid}.txt"), "w").write(r.stdout[-200000:])
    open(os.path.join(d, "reason.txt"), "w").write(reason)  # window-only screenshot: not implemented, see NOT RUN list in result file
    return d

def run(c):
    out = c["report_dir"]; os.makedirs(out, exist_ok=True)
    bad, ok = preflight(c)
    res = [f"# Overnight result {datetime.datetime.now():%Y-%m-%d %H:%M}", "", "| item | verdict | evidence |", "|---|---|---|"]
    def row(i, v, e): res.append(f"| {i} | {v} | {e} |")
    for b in bad: row("preflight", "FAIL", b)
    if bad:
        open(os.path.join(out, "overnight_result.md"), "w").write("\n".join(res)); return 1
    w = os.path.join(c["root"], c["world"]); slog = os.path.join(w, "logs", "latest.log"); clog = os.path.join(c["client_dir"], "logs", "latest.log")
    csv = os.path.join(out, "ram.csv"); open(csv, "w").write("time,freeGB,commitFreeGB,javaProcsWS_MB\n")
    hard = datetime.datetime.combine(datetime.date.today(), datetime.time(*map(int, c["hard_stop"].split(":"))))
    if hard < datetime.datetime.now(): hard += datetime.timedelta(days=1)
    NOWIN = 0x08000000
    srv = subprocess.Popen(c["server_cmd"], cwd=w, creationflags=NOWIN, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    mine = {srv.pid}; client = None; t0 = time.time(); state = "server"; stage_t = time.time(); si = ci = 0
    sh, ch, failed = [], [], None
    def stop_all():
        try: rcon(c["rcon_port"], rcon_pw(c), "stop", 20)
        except Exception: pass
        end = time.time() + 120
        while time.time() < end and srv.poll() is None: time.sleep(3)
        for p in list(mine): subprocess.run(["taskkill", "/PID", str(p), "/F"], capture_output=True)
    try:
        while not failed and datetime.datetime.now() < hard:
            time.sleep(c["poll_s"])
            ram, com = mem(); open(csv, "a").write(f"{datetime.datetime.now():%H:%M:%S},{ram:.1f},{com:.1f},{sum(p[2] for p in java_procs()):.0f}\n")
            if srv.poll() is not None: failed = ("server", "server process exited unexpectedly " + str(srv.returncode)); break
            if client and client.poll() is not None and state == "client": pass  # Prism launcher exits after spawning javaw; the javaw check below is the real one
            sl = open(slog, encoding="utf8", errors="replace").read().splitlines() if os.path.exists(slog) else []
            sh, f = scan(sl, SERVER_STAGES, SERVER_FAIL)
            if f: failed = ("server fail string", f"line {f[0]}: {f[1]}"); break
            if glob.glob(os.path.join(w, "crash-reports", "*")) and any(os.path.getmtime(p) > t0 for p in glob.glob(os.path.join(w, "crash-reports", "*"))): failed = ("server crash report", "new file in crash-reports"); break
            if len(sh) > si: si = len(sh); stage_t = time.time()
            elif si < len(SERVER_STAGES) and state == "server" and time.time() - stage_t > SERVER_STAGES[si][2]: failed = (SERVER_STAGES[si][0], f"stall: no '{SERVER_STAGES[si][1]}' within {SERVER_STAGES[si][2]} s"); break
            if state == "server" and si == len(SERVER_STAGES):
                if ram < c["client_start_free_ram_gb"]: failed = ("client start", f"free RAM {ram:.1f} GB < {c['client_start_free_ram_gb']}"); break
                if any(p[0].lower() == "javaw.exe" for p in java_procs()): failed = ("client start", "a javaw already runs"); break
                if not c["client_cmd"]: failed = ("client start", "client_cmd not configured"); break
                before = {p[1] for p in java_procs()}
                client = subprocess.Popen(c["client_cmd"], creationflags=NOWIN); state = "client"; stage_t = time.time(); time.sleep(20)
                mine |= {p[1] for p in java_procs()} - before; mine.add(client.pid)
            if state == "client":
                cl = open(clog, encoding="utf8", errors="replace").read().splitlines() if os.path.exists(clog) else []
                ch, f = scan(cl, CLIENT_STAGES, CLIENT_FAIL)
                if f: failed = ("client fail string", f"line {f[0]}: {f[1]}"); break
                gcp = os.path.join(c["client_dir"], c["client_gc_log"])
                if len(ch) == 5 and os.path.exists(gcp):  # silent stage: GC log is the heartbeat
                    v, msg = gc_verdict(open(gcp, errors="replace").read())
                    if v == "FAIL": failed = ("silent stage", msg); break
                if len(ch) > ci: ci = len(ch); stage_t = time.time()
                elif ci < len(CLIENT_STAGES) and time.time() - stage_t > CLIENT_STAGES[ci][2]: failed = (CLIENT_STAGES[ci][0], f"stall: no '{CLIENT_STAGES[ci][1]}' within {CLIENT_STAGES[ci][2]} s"); break
                if ci == len(CLIENT_STAGES):
                    sl = open(slog, encoding="utf8", errors="replace").read().splitlines()
                    j = [(n, l.strip()) for n, l in enumerate(sl, 1) if re.search(JOINED_RE, l)]
                    if j:
                        pw = rcon_pw(c)
                        rcon(c["rcon_port"], pw, f"gamemode creative {c['player']}")
                        time.sleep(60); lst = rcon(c["rcon_port"], pw, "list")
                        row("join", "PASS" if c["player"] in lst else "FAIL", f"{slog} line {j[0][0]}: {j[0][1]} | RCON list at +60 s: {lst}")
                        break
                    if time.time() - stage_t > 120: failed = ("join", "no 'joined the game' within 120 s of Connecting"); break
        else:
            if not failed and not any(r.startswith("| join") for r in res): failed = ("hard stop", c["hard_stop"])
    finally:
        if failed:
            d = snap(c, out, failed[0], failed[1], slog, clog, mine)
            row(failed[0], "FAIL", failed[1] + f" (bundle {d})")
        for s_, n, q in sh: row("server: " + s_, "PASS", f"{slog} line {n}: {q}")
        for s_, n, q in ch: row("client: " + s_, "PASS", f"{clog} line {n}: {q}")
        row("input-driven items (Offgrid, Space-fire, Tool Belt, Codex, title screen)", "NOT RUN", "no dry-run input helper")
        stop_all()
        open(os.path.join(out, "overnight_result.md"), "w").write("\n".join(res) + "\n")
    return 1 if failed else 0

def dry_run(server_log, client_log=None):
    for label, path, st, fl in (("server", server_log, SERVER_STAGES, SERVER_FAIL), ("client", client_log, CLIENT_STAGES, CLIENT_FAIL)):
        if not path: continue
        lines = open(path, encoding="utf8", errors="replace").read().splitlines()
        hits, f = scan(lines, st, fl)
        print(f"== {label}: {len(hits)}/{len(st)} stages")
        for s_, n, q in hits: print(f"  PASS {s_} line {n}: {q[:110]}")
        if len(hits) < len(st): print(f"  STALL at stage '{st[len(hits)][0]}' (budget {st[len(hits)][2]} s)")
        if f: print(f"  FAIL string line {f[0]}: {f[1][:110]}")
        if label == "server":
            j = [(n, l.strip()) for n, l in enumerate(lines, 1) if re.search(JOINED_RE, l)]
            print("  join evidence:", f"line {j[0][0]}: {j[0][1][:100]}" if j else "none")

if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["--config"]: CFG.update(json.load(open(a[1], encoding="utf8"))); a = a[2:]
    if a[:1] == ["dry-run"]: dry_run(*a[1:3])
    elif a[:1] == ["preflight"]:
        b, o = preflight(CFG); print("\n".join(["OK   " + x for x in o] + ["FAIL " + x for x in b])); sys.exit(1 if b else 0)
    elif a[:1] == ["run"]: sys.exit(run(CFG))
    else: sys.exit(__doc__)
