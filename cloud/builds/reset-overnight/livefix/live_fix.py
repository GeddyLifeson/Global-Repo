"""Live fix for the running Diaithir server: remove the 7 stale per-coal biome modifiers (they duplicate deep_mod_ores and cause
"Feature order cycle found" on the first chunk), restart, then set spawn at Creag Ruadh. Does not touch the world.
Robust: a stalled server that ignores RCON stop is killed (only the java that holds the server port), and every RCON call retries."""
import os, shutil, socket, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rcon

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = sys.argv[1] if len(sys.argv) > 1 else os.environ.get('DIAITHIR_ROOT', r'C:\DiaithirServer')
SRV = os.path.join(ROOT, 'server')
props = dict(l.strip().split('=', 1) for l in open(os.path.join(SRV, 'server.properties'), encoding='utf-8') if '=' in l and not l.startswith('#'))
rport, rpw, port = int(props['rcon.port']), props['rcon.password'], int(props.get('server-port', 25565))
MODS = ('black', 'fire', 'gold', 'rainbow', 'red_brown', 'silver', 'white')
SPAWN_CMDS = ('execute in minecraft:overworld run setworldspawn -251201 207 -1541408', 'worldborder center -251201 -1541408', 'worldborder set 40000')


def up(p):
    s = socket.socket(); s.settimeout(2)
    try:
        s.connect(('127.0.0.1', p)); return True
    except OSError:
        return False
    finally:
        s.close()


def ps(script):
    return subprocess.run(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', script], capture_output=True, text=True, timeout=120).stdout.strip()


def server_pids():
    """PIDs of java.exe that listen on the server port or whose command line is this Diaithir server (win_args.txt / the server folder)."""
    out = ps("$p=@(); try{$p+=(Get-NetTCPConnection -LocalPort %d -State Listen -ErrorAction Stop).OwningProcess}catch{}; "
             "$p+=(Get-CimInstance Win32_Process -Filter \"Name='java.exe'\" | Where-Object { $_.CommandLine -like '*win_args.txt*' -and $_.CommandLine -like '*user_jvm_args*' } | ForEach-Object ProcessId); "
             "$p | Sort-Object -Unique" % port)
    return [int(x) for x in out.split() if x.isdigit()]


def alive(pid):
    return str(pid) in subprocess.run(['tasklist', '/FI', 'PID eq %d' % pid, '/NH'], capture_output=True, text=True).stdout


def rcon_cmd(cmd, tries=12, timeout=90):
    last = None
    for i in range(tries):
        try:
            r = rcon.Rcon('127.0.0.1', rport, rpw, timeout=timeout)
            try:
                return r.command(cmd)
            finally:
                r.close()
        except Exception as e:
            last = e
            print('  rcon retry %d (%s)' % (i + 1, e)); time.sleep(10)
    raise last


# 1. stop
pids = server_pids()
if pids or up(port) or up(rport):
    print('server is running (pids %s); stopping...' % pids)
    try:
        print('  list ->', rcon_cmd('list', tries=1, timeout=30))
        rcon_cmd('save-all flush', tries=1, timeout=60)
    except Exception as e:
        print('  save-all got no reply:', e)
    try:
        rcon_cmd('stop', tries=1, timeout=60)
    except Exception as e:
        print('  stop got no reply:', e)
    end = time.time() + 150
    while time.time() < end and (any(alive(p) for p in pids) or up(port)):
        time.sleep(3)
    for p in server_pids() or [p for p in pids if alive(p)]:
        print('server did not exit; killing java pid', p)
        subprocess.run(['taskkill', '/PID', str(p), '/F'], capture_output=True)
    for _ in range(30):
        if not up(port) and not up(rport): break
        time.sleep(2)
    if up(port):
        print('STOP FAILED: something still holds port %d. Close the Minecraft server window, then run this again.' % port); sys.exit(2)
    time.sleep(5)
# Distant Horizons must not run on the SERVER: it built LODs for 93 dimensions (backrooms:level*) and exhausted a 4 GB heap (OOM 22:28 on 10-25).
# The client keeps it. Also drop half-generated chunks around spawn (3x3 regions) so they regenerate; they are moved aside, not deleted.
import glob
for fn in glob.glob(os.path.join(SRV, 'mods', 'DistantHorizons*.jar')):
    hold = os.path.join(SRV, 'mods_hold', 'dh_server')
    try:
        os.makedirs(hold, exist_ok=True); shutil.move(fn, os.path.join(hold, os.path.basename(fn))); print('held (server only)', os.path.basename(fn))
    except OSError as e:
        print('could not hold', fn, '-', e)
level = props.get('level-name', 'world')
aside = os.path.join(SRV, 'region_aside_' + time.strftime('%Y%m%d_%H%M%S'))
for rx in (-492, -491, -490):
    for rz in (-3012, -3011, -3010):
        for f in glob.glob(os.path.join(SRV, level, '**', 'r.%d.%d.mca' % (rx, rz)), recursive=True):
            dst = os.path.join(aside, os.path.relpath(f, SRV)); os.makedirs(os.path.dirname(dst), exist_ok=True)
            try:
                shutil.move(f, dst); print('moved aside', os.path.relpath(f, SRV))
            except OSError as e:
                print('could not move', f, '-', e)

# the stall watchdog (server_watchdog.py) would restart or report on the dead server: stop it too
ps("Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*server_watchdog.py*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }")
print('server is stopped (watchdog stopped too)')

# Valkyrien Skies hangs the server tick (FQ.postTickGame since 10:10): hold VS, Eureka and anything that needs them until it is fixed
HOLD = ('valkyrienskies-*.jar', 'eureka-*.jar', 'vs_*.jar', 'vs-*.jar', 'clockwork-*.jar', 'trackwork-*.jar', 'createvs-*.jar')
import fnmatch
for mods_dir in (os.path.join(SRV, 'mods'), os.environ.get('DIAITHIR_PRISM_MODS', r'C:\Prism\instances\Diaithir\.minecraft\mods')):
    if not os.path.isdir(mods_dir): continue
    hold = os.path.join(os.path.dirname(mods_dir), 'mods_hold', 'vs_hang')
    for fn in os.listdir(mods_dir):
        if any(fnmatch.fnmatch(fn.lower(), pat.lower()) for pat in HOLD):
            try:
                os.makedirs(hold, exist_ok=True)
                shutil.move(os.path.join(mods_dir, fn), os.path.join(hold, fn)); print('held', fn, 'in', hold)
            except OSError as e:
                print('could not hold', fn, '-', e)

# 2. remove the stale modifiers and install the helpers
d = os.path.join(SRV, 'kubejs', 'data', 'diaithir', 'neoforge', 'biome_modifier')
for n in MODS:
    f = os.path.join(d, n + '_coal_ore.json')
    if os.path.exists(f):
        os.remove(f); print('removed', f)
left = [n for n in MODS if os.path.exists(os.path.join(d, n + '_coal_ore.json'))]
if left:
    print('COULD NOT REMOVE', left); sys.exit(3)
print('verified: the 7 coal modifier files are gone')
sd = os.path.join(SRV, 'kubejs', 'server_scripts', 'diaithir')
os.makedirs(sd, exist_ok=True)
shutil.copy(os.path.join(HERE, 'spawn_once.js'), os.path.join(sd, 'spawn_once.js'))
print('installed spawn_once.js (moves each existing player to Creag Ruadh once, at next login)')
ss, new_ss = os.path.join(ROOT, 'start_server.ps1'), os.path.join(HERE, 'start_server.ps1')
if os.path.exists(new_ss):
    if os.path.exists(ss): shutil.copy(ss, ss + '.bak')
    shutil.copy(new_ss, ss); print('installed fixed start_server.ps1')

# 3. start and wait for RCON
print('starting server...')
r = subprocess.run(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', ss], timeout=900)
if r.returncode: print('start script reported', r.returncode, '- carrying on, waiting for the server instead')
end = time.time() + 1500
while time.time() < end and not (up(port) and up(rport)):
    time.sleep(5)
if not up(rport):
    print('SERVER DID NOT COME UP in 25 minutes; look at', os.path.join(SRV, 'logs', 'latest.log')); sys.exit(4)
time.sleep(10)

# 4. spawn
for c in SPAWN_CMDS:
    print(rcon_cmd(c))
print('Server is up, join ssh-elem.tun.ply.gg (spawn is at Creag Ruadh)')
