"""Turns the Age I underground on in the live world: caves, aquifers, lava, geodes and stone patches (all off in world_gen_settings.dat).
Needs Tellus 0.8.3-diaithir.16 in the server's mods (older jars ignore the keys' new depth ratio and flood the deep with lava), so it checks
the jar first and changes nothing if it is older. Then: stop the server, back up and patch world_gen_settings.dat, refresh the preset, move the
already generated overworld chunks aside (they are solid rock; Tellus rebuilds them with the same surface), start the server.
Files placed next to this script are installed after the server stops: a Tellus-*.jar (replaces the server's, the old one goes to mods_hold),
a YungsBetterCaves-*.jar (the giant caves mod) and better_cave.json (its scaled carver). Pass --keep-chunks to leave existing chunks alone (only new chunks get caves). Usage: python -I underground_fix.py [ROOT] [--keep-chunks]"""
import glob, gzip, os, re, shutil, socket, struct, subprocess, sys, time

KEYS = ('cave_generation', 'caves_reach_surface', 'lava_pools', 'geodes', 'geological_stone_patches', 'deep_dark')
MIN_TELLUS = 16
MIN_HEAP_MB = 6144   # Better Caves, the water prefetch and 4,000-block columns ran a 3 GB heap out of memory; 4.5 GB worked, 6 GB leaves headroom


def patch_settings(raw):
    """Sets the KEYS byte tags to 1 wherever the Tellus generator stores them. Returns (new bytes, {key: tags set})."""
    counts = {}
    for k in KEYS:
        tag = b'\x01' + struct.pack('>H', len(k)) + k.encode()
        counts[k] = raw.count(tag + b'\x00') + raw.count(tag + b'\x01')
        raw = raw.replace(tag + b'\x00', tag + b'\x01')
    return raw, counts


def staged_files(here):
    """Files the operator left next to the script: (Tellus jar, Better Caves jar, scaled carver json), each a path or ''."""
    def one(pattern):
        found = sorted(glob.glob(os.path.join(here, pattern)))
        return found[-1] if found else ''
    return one('Tellus-*.jar'), one('YungsBetterCaves-*.jar'), one('better_cave.json')


def install_staged(srv, files, stamp):
    tellus, caves, carver = files
    mods = os.path.join(srv, 'mods')
    if tellus:
        hold = os.path.join(srv, 'mods_hold', 'tellus_' + stamp)
        os.makedirs(hold, exist_ok=True)
        for old in glob.glob(os.path.join(mods, 'Tellus-*.jar')):
            if os.path.basename(old) != os.path.basename(tellus):
                shutil.move(old, os.path.join(hold, os.path.basename(old)))
        shutil.copy2(tellus, mods); print('installed', os.path.basename(tellus))
    if caves:
        for old in glob.glob(os.path.join(mods, 'YungsBetterCaves-*.jar')):
            if os.path.basename(old) != os.path.basename(caves):
                os.remove(old)
        shutil.copy2(caves, mods); print('installed', os.path.basename(caves))
    if carver:
        dst = os.path.join(srv, 'kubejs', 'data', 'bettercaves', 'worldgen', 'configured_carver')
        os.makedirs(dst, exist_ok=True); shutil.copy2(carver, os.path.join(dst, 'better_cave.json')); print('installed the scaled Better Caves carver')


def raise_heap(srv, minimum_mb=MIN_HEAP_MB):
    """Raises -Xmx in user_jvm_args.txt to at least minimum_mb (a .bak copy is kept). Returns (old, new) as text, or None if there is no -Xmx line."""
    path = os.path.join(srv, 'user_jvm_args.txt')
    if not os.path.exists(path):
        return None
    text = open(path, encoding='utf-8').read()
    m = re.search(r'^(?!#)\s*-Xmx(\d+)([GgMm])\s*$', text, re.M)
    if not m:
        return None
    mb = int(m.group(1)) * (1024 if m.group(2) in 'Gg' else 1)
    if mb >= minimum_mb:
        return m.group(0).strip(), m.group(0).strip()
    shutil.copy2(path, path + '.bak')
    new = '-Xmx%dM' % minimum_mb
    open(path, 'w', encoding='utf-8').write(text[:m.start()] + new + text[m.end():])
    return m.group(0).strip(), new


def tellus_build(mods):
    for f in glob.glob(os.path.join(mods, 'Tellus-*.jar')):
        m = re.search(r'diaithir\.(\d+)', os.path.basename(f))
        if m:
            return int(m.group(1)), os.path.basename(f)
    return 0, None


def main(argv):
    args = [a for a in argv if not a.startswith('--')]
    keep = '--keep-chunks' in argv
    root = args[0] if args else os.environ.get('DIAITHIR_ROOT', r'C:\DiaithirServer')
    here = os.path.dirname(os.path.abspath(__file__))
    srv = os.path.join(root, 'server')
    props = dict(l.strip().split('=', 1) for l in open(os.path.join(srv, 'server.properties'), encoding='utf-8') if '=' in l and not l.startswith('#'))
    rport, rpw, port = int(props['rcon.port']), props['rcon.password'], int(props.get('server-port', 25565))
    level = props.get('level-name', 'world')

    files = staged_files(here)
    build, jar = tellus_build(os.path.join(srv, 'mods'))
    if files[0]:
        build, jar = max((build, jar), (tellus_build(here)[0], os.path.basename(files[0])), key=lambda t: t[0])
    if build < MIN_TELLUS:
        print('NOTHING CHANGED: the server has Tellus %s; it needs diaithir.%d or newer (publish the pack that carries it first).' % (jar, MIN_TELLUS))
        return 5
    print('Tellus jar is', jar)

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
                s = socket.create_connection(('127.0.0.1', rport), timeout=timeout); s.settimeout(timeout)

                def send(t, body):
                    b = body.encode() + b'\0\0'
                    s.sendall(struct.pack('<iii', len(b) + 8, 2, t) + b)
                    n = struct.unpack('<i', s.recv(4))[0]
                    d = b''
                    while len(d) < n:
                        d += s.recv(n - len(d))
                    return d[8:-2].decode(errors='replace')
                try:
                    send(3, rpw)
                    return send(2, cmd)
                finally:
                    s.close()
            except Exception as e:
                last = e
                print('  rcon retry %d (%s)' % (i + 1, e)); time.sleep(10)
        raise last

    pids = server_pids()
    if pids or up(port) or up(rport):
        print('server is running (pids %s); stopping...' % pids)
        for c in ('save-all flush', 'stop'):
            try:
                rcon_cmd(c, tries=1, timeout=60)
            except Exception as e:
                print('  %s got no reply: %s' % (c, e))
        end = time.time() + 150
        while time.time() < end and (any(alive(p) for p in pids) or up(port)):
            time.sleep(3)
        for p in server_pids() or [p for p in pids if alive(p)]:
            print('server did not exit; killing java pid', p)
            subprocess.run(['taskkill', '/PID', str(p), '/F'], capture_output=True)
        for _ in range(30):
            if not up(port) and not up(rport):
                break
            time.sleep(2)
        if up(port):
            print('STOP FAILED: something still holds port %d. Close the Minecraft server window, then run this again.' % port); return 2
        time.sleep(5)
    print('server is stopped')

    stamp = time.strftime('%Y%m%d_%H%M%S')
    install_staged(srv, files, stamp)
    heap = raise_heap(srv)
    print('heap:', 'no -Xmx line in user_jvm_args.txt, check the start script' if heap is None else '%s -> %s' % heap)
    dat = os.path.join(srv, level, 'data', 'minecraft', 'world_gen_settings.dat')
    shutil.copy2(dat, dat + '.bak_' + stamp)
    raw, counts = patch_settings(gzip.decompress(open(dat, 'rb').read()))
    with open(dat, 'wb') as f:
        f.write(gzip.compress(raw))
    again = patch_settings(gzip.decompress(open(dat, 'rb').read()))[1]
    print('world_gen_settings.dat patched (backup .bak_%s): %s' % (stamp, ', '.join('%s x%d' % kv for kv in counts.items())))
    if any(v < 2 for v in counts.values()):
        print('WARNING: a key was not found twice (generator + biome_source); restore the .bak and tell the thread'); return 3

    preset_src = next((c for c in (os.path.join(here, 'diaithir_age_1.json'),
                                   os.path.join(here, '..', '..', 'content', 'server', 'kubejs', 'data', 'tellus', 'worldgen', 'world_preset', 'diaithir_age_1.json'))
                       if os.path.exists(c)), '')
    preset_dst = os.path.join(srv, 'kubejs', 'data', 'tellus', 'worldgen', 'world_preset', 'diaithir_age_1.json')
    if preset_src:
        os.makedirs(os.path.dirname(preset_dst), exist_ok=True); shutil.copy(preset_src, preset_dst); print('refreshed the preset overlay')

    if keep:
        print('--keep-chunks: existing chunks stay solid; only new chunks get caves')
    else:
        aside = os.path.join(srv, 'chunks_aside_' + stamp)
        moved = 0
        for sub in ('region', 'entities', 'poi'):
            d = os.path.join(srv, level, 'dimensions', 'minecraft', 'overworld', sub)
            if os.path.isdir(d):
                dst = os.path.join(aside, sub)
                os.makedirs(aside, exist_ok=True); shutil.move(d, dst)
                moved += len(os.listdir(dst))
        print('moved %d chunk files aside to %s (move them back to undo); Tellus rebuilds the surface identically with caves' % (moved, aside))

    ss = os.path.join(root, 'start_server.ps1')
    print('starting server...')
    r = subprocess.run(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', ss], timeout=900)
    if r.returncode:
        print('start script reported', r.returncode, '- waiting for the server instead')
    end = time.time() + 1500
    while time.time() < end and not (up(port) and up(rport)):
        time.sleep(5)
    if not up(rport):
        print('SERVER DID NOT COME UP in 25 minutes; look at', os.path.join(srv, 'logs', 'latest.log')); return 4
    time.sleep(10)
    for c in ('execute in minecraft:overworld run setworldspawn -251201 207 -1541408',):
        print(rcon_cmd(c))
    print('Server is up with caves, aquifers and lava below Creag Ruadh. First chunk loads are slow while the rock regenerates.')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
