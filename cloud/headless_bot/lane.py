# S6854 lane.py: headless NeoForge 26.1.2 test lane in the cloud. Real server + real client (portablemc) under Xvfb, so the real
# NeoForge handshake, registries and rendering run (mc_fake_player_bot.py S6843 is refused by modded NeoForge servers).
# Usage as a library from a check script:
#     from lane import Lane
#     with Lane('qol', jars=[...]) as L:
#         L.server_cmd('setblock 0 -60 0 stone'); L.shot('x.png'); L.expect_log('server', r'Done')
# CLI: python3 -I lane.py smoke NAME JAR...   (boot, join, one screenshot, stop)
# Light packs only: server 2.5G + client 3G fit the 15 GB container; the full pack does not (client OOM).
# Env: LANE_ROOT (/tmp/claude-0/lane), LANE_JAVA (/tmp/claude-0/jdk25), NF (26.1.2.116), DISPLAY_NUM (96), MCDIR, OUT (outputs).
import os, re, shutil, subprocess, sys, time, signal, pathlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
ROOT = pathlib.Path(os.environ.get('LANE_ROOT', '/tmp/claude-0/lane'))
JAVA = os.environ.get('LANE_JAVA', '/tmp/claude-0/jdk25')  # JDK 25 (tools/get_jdk25.sh); not JAVA_HOME, which may point at 21
NF = os.environ.get('NF', '26.1.2.116')
DNUM = os.environ.get('DISPLAY_NUM', '96')
MCDIR = os.environ.get('MCDIR', '/tmp/claude-0/mc')
BASE = ROOT / 'srv-base'   # one-time installer output (libraries, unix_args): java -jar neoforge-installer --install-server

class Lane:
    def __init__(self, name, jars, server_jars=None, client_jars=None, props=None, client_files=None, srv_xmx='2500M', cl_xmx='3G', user='Tester', out=None):
        self.name, self.user = name, user
        self.dir = ROOT / name; self.srv = self.dir / 'server'; self.cl = self.dir / 'client'
        self.out = pathlib.Path(out or os.environ.get('OUT', self.dir / 'out')); self.out.mkdir(parents=True, exist_ok=True)
        self.jars = [pathlib.Path(j) for j in jars]
        self.sj = [pathlib.Path(j) for j in (server_jars if server_jars is not None else jars)]
        self.cj = [pathlib.Path(j) for j in (client_jars if client_jars is not None else jars)]
        self.props = props or {}; self.client_files = client_files or {}; self.srv_xmx, self.cl_xmx = srv_xmx, cl_xmx
        self.sproc = self.cproc = None; self.xvfb = None
    # ---------- setup ----------
    def _prep(self):
        if self.dir.exists(): shutil.rmtree(self.dir)
        self.srv.mkdir(parents=True); self.cl.mkdir(parents=True); self.out.mkdir(parents=True, exist_ok=True)
        for item in ('libraries', 'run.sh'):
            os.symlink(BASE / item, self.srv / item)
        (self.srv / 'eula.txt').write_text('eula=true\n')
        p = {'online-mode': 'false', 'level-type': 'minecraft\\:flat', 'spawn-protection': '0', 'pause-when-empty-seconds': '-1',
             'enable-command-block': 'true', 'gamemode': 'creative', 'difficulty': 'peaceful', 'spawn-monsters': 'false',
             'view-distance': '4', 'simulation-distance': '4', 'max-tick-time': '-1', 'enable-rcon': 'false', 'sync-chunk-writes': 'false'}
        p.update(self.props)
        (self.srv / 'server.properties').write_text(''.join(f'{k}={v}\n' for k, v in p.items()))
        (self.srv / 'ops.json').write_text('[{"uuid":"00000000-0000-0000-0000-000000000000","name":"%s","level":4}]' % self.user)
        for tgt, js in ((self.srv / 'mods', self.sj), (self.cl / 'mods', self.cj)):
            tgt.mkdir()
            for j in js: shutil.copy(j, tgt / j.name)
        for rel, txt in self.client_files.items():  # e.g. {'config/diaithirctm-client.toml': 'enabled = true\n'}
            fp = self.cl / rel; fp.parent.mkdir(parents=True, exist_ok=True); fp.write_text(txt)
        (self.cl / 'options.txt').write_text('\n'.join([
            'version:4790', 'onboardAccessibility:false', 'tutorialStep:none', 'renderDistance:4', 'simulationDistance:5', 'graphicsMode:0', 'particles:2',
            'maxFps:30', 'guiScale:2', 'pauseOnLostFocus:false', 'skipMultiplayerWarning:true', 'narrator:0', 'joinedFirstServer:true',
            'key_key.use:key.keyboard.r', 'key_key.chat:key.keyboard.t', 'key_key.command:key.keyboard.slash']) + '\n')
    def _xvfb(self):
        r = subprocess.run(['pgrep', '-f', f'Xvfb :{DNUM}'], capture_output=True)
        if r.returncode:
            self.xvfb = subprocess.Popen(['Xvfb', f':{DNUM}', '-screen', '0', '1280x720x24'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(2)
        os.environ['DISPLAY'] = f':{DNUM}'
        import drive; drive.DISPLAY = f':{DNUM}'; drive._d = None; self.drive = drive
    # ---------- server ----------
    def start_server(self, wait=600):
        log = self.srv / 'server.log'; fifo = self.srv / 'cmd.in'
        os.mkfifo(fifo)
        nf = sorted(os.listdir(BASE / 'libraries/net/neoforged/neoforge'))[-1]
        env = {**os.environ, 'PATH': f'{JAVA}/bin:' + os.environ['PATH']}
        self.sproc = subprocess.Popen(
            f'tail -f cmd.in | java -Xms1G -Xmx{self.srv_xmx} -Djava.net.preferIPv4Stack=true @libraries/net/neoforged/neoforge/{nf}/unix_args.txt nogui > server.log 2>&1',
            shell=True, cwd=self.srv, env=env, start_new_session=True)
        r = self.expect_log('server', r'Done \([0-9.]+s\)!|Mod loading has failed|Exception in server tick', wait)
        if not r or 'Done' not in r.group(0): raise RuntimeError(f'server did not start: {r and r.group(0)} (see {log})')
        return r.group(0)
    def server_cmd(self, c, wait=0.6):
        """Send a console command; returns the server log lines it produced (command feedback, errors)."""
        p = self.srv / 'server.log'; n0 = len(p.read_text(errors='replace').splitlines())
        with open(self.srv / 'cmd.in', 'w') as f: f.write(c + '\n')
        time.sleep(wait)
        return p.read_text(errors='replace').splitlines()[n0:]
    # ---------- client ----------
    def start_client(self, wait=420, host='127.0.0.1', port=25565):
        self._xvfb()
        env = {**os.environ, 'LIBGL_ALWAYS_SOFTWARE': '1', 'GALLIUM_DRIVER': 'llvmpipe', 'DISPLAY': f':{DNUM}'}
        cmd = ['portablemc', '--main-dir', MCDIR, 'start', '--mc-dir', str(self.cl), f'neoforge::{NF}', '-u', self.user, '--jvm', f'{JAVA}/bin/java',
               f'--jvm-arg=-Xmx{self.cl_xmx}', '--jvm-arg=-Xms1G', '--jvm-arg=-Djava.net.preferIPv4Stack=true', '--jvm-arg=-XX:+UseCompactObjectHeaders',
               '--resolution', '1280x720', '--join-server', host, '--join-server-port', str(port)]
        self.cproc = subprocess.Popen(cmd, env=env, stdout=open(self.out / 'portablemc.out', 'w'), stderr=subprocess.STDOUT, start_new_session=True)
        r = self.expect_log('server', rf'{self.user} joined the game|{self.user}\[.*logged in', wait)
        if not r:
            try: self.shot('join_failed.png')
            except Exception: pass
            raise RuntimeError('client did not join; see ' + str(self.out / 'portablemc.out') + ' and ' + str(self.cl / 'logs/latest.log'))
        self.server_cmd(f'op {self.user}')  # ops.json uuid is wrong for offline-mode players
        self.wait_render()
        return r.group(0)
    def wait_render(self, wait=120):
        """Block until the client frame is not black (llvmpipe needs ~20-40 s to draw the first world frame)."""
        from PIL import Image, ImageStat
        t0 = time.time(); p = str(self.out / '_probe.png')
        while time.time() - t0 < wait:
            self.drive.shot(p)
            if ImageStat.Stat(Image.open(p).convert('L')).mean[0] > 12: break
            time.sleep(4)
        time.sleep(3)
    # ---------- helpers ----------
    def logpath(self, which):
        return self.srv / 'server.log' if which == 'server' else self.cl / 'logs/latest.log'
    def expect_log(self, which, pat, wait=60):
        t0 = time.time(); rx = re.compile(pat); p = self.logpath(which)
        while time.time() - t0 < wait:
            if p.exists():
                m = rx.search(p.read_text(errors='replace'))
                if m: return m
            if which == 'server' and self.sproc and self.sproc.poll() is not None and not p.exists(): break
            time.sleep(1.5)
        return None
    def log_lines(self, which, pat):
        rx = re.compile(pat); p = self.logpath(which)
        return [l for l in p.read_text(errors='replace').splitlines() if rx.search(l)] if p.exists() else []
    def shot(self, name):
        return self.drive.shot(str(self.out / name))
    def look(self, x, y, z, yaw, pitch):
        self.server_cmd(f'tp {self.user} {x} {y} {z} {yaw} {pitch}', 1.5)
    def stop(self):
        for p in (self.cproc, self.sproc):
            if p and p.poll() is None:
                try: os.killpg(p.pid, signal.SIGKILL)
                except ProcessLookupError: pass
        subprocess.run(['pkill', '-9', '-f', 'unix_args.txt'], capture_output=True)  # server java only (args file is unique to it)
    def __enter__(self):
        self._prep(); self.start_server(); return self
    def __exit__(self, *a): self.stop()

if __name__ == '__main__':
    if len(sys.argv) >= 4 and sys.argv[1] == 'smoke':
        with Lane(sys.argv[2], sys.argv[3:]) as L:
            print('server', L.start_server.__name__, 'up'); print(L.start_client()); L.shot('smoke.png'); print('shot', L.out / 'smoke.png')
    else: print(__doc__)
