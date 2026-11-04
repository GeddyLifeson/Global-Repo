# S6911 checks/repl_lane.py OUTDIR JAR...: boot a lane, join, then exec() each /tmp/claude-0/cmd_N.py (globals L, d, out) so a GUI can be explored without rebooting. Write /tmp/claude-0/cmd_stop to end.
import sys, pathlib, time, os, glob
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from lane import Lane
out, *jars = sys.argv[1:]
with Lane('repl', jars, props={'spawn-monsters': 'false'}, srv_xmx='2500M', out=out) as L:
    (L.cl / 'options.txt').open('a').write('key_key.toolbelt.open:key.keyboard.g\nkey_key.toolbelt.slot:key.keyboard.v\n')
    print('joined', L.start_client(), flush=True); d = L.drive
    for c in ('gamemode survival Tester', 'time set day', 'weather clear'): L.server_cmd(c)
    n = 0
    while not os.path.exists('/tmp/claude-0/cmd_stop'):
        f = f'/tmp/claude-0/cmd_{n}.py'
        if os.path.exists(f):
            try: exec(open(f).read())
            except Exception as e: print('ERR', repr(e), flush=True)
            print('DONE', n, flush=True); n += 1
        time.sleep(1)
