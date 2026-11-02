"""Rescue players who fell out of the world: build a stone platform at the Creag Ruadh spawn, move everyone online onto it, set world spawn,
and install a one-shot login rule (KubeJS) that does the same for anyone offline. Needs the server running; changes no world data but those blocks."""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rcon

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.environ.get('DIAITHIR_ROOT', r'C:\DiaithirServer')
props = dict(l.strip().split('=', 1) for l in open(os.path.join(ROOT, 'server', 'server.properties'), encoding='utf-8') if '=' in l and not l.startswith('#'))
X, Z = -251201, -1541408
IN = 'execute in minecraft:overworld run '


def cmd(c, tries=8):
    for i in range(tries):
        try:
            r = rcon.Rcon('127.0.0.1', int(props['rcon.port']), props['rcon.password'], timeout=90)
            try: return r.command(c)
            finally: r.close()
        except Exception as e:
            print('  retry', i + 1, e); time.sleep(8)
    raise SystemExit('RCON does not answer: is the server running?')


js = os.path.join(ROOT, 'server', 'kubejs', 'server_scripts', 'diaithir')
os.makedirs(js, exist_ok=True)
open(os.path.join(js, 'rescue_once.js'), 'w').write('''// One-shot: a stone platform at Creag Ruadh and a teleport onto it for anyone who logs in after the rescue.
PlayerEvents.loggedIn(event => {
  let p = event.player
  if (p.persistentData.getBooleanOr('rescue_v1', false)) return
  p.persistentData.putBoolean('rescue_v1', true)
  let name = p.username, s = event.server
  s.scheduleInTicks(40, () => {
    s.runCommandSilent('execute in minecraft:overworld run forceload add %d %d')
    s.runCommandSilent('execute in minecraft:overworld run fill %d 205 %d %d 205 %d minecraft:stone')
    s.runCommandSilent('execute in minecraft:overworld run fill %d 206 %d %d 211 %d minecraft:air')
    s.runCommandSilent(`execute in minecraft:overworld run tp ${name} %d 207 %d`)
    s.runCommandSilent(`execute in minecraft:overworld run spawnpoint ${name} %d 207 %d`)
  })
})
''' % (X, Z, X - 3, Z - 3, X + 3, Z + 3, X - 3, Z - 3, X + 3, Z + 3, X, Z, X, Z))
print(cmd('kubejs reload server_scripts'))
print(cmd(IN + 'forceload add %d %d' % (X, Z)))
time.sleep(5)
print(cmd(IN + 'fill %d 205 %d %d 205 %d minecraft:stone' % (X - 3, Z - 3, X + 3, Z + 3)))
print(cmd(IN + 'fill %d 206 %d %d 211 %d minecraft:air' % (X - 3, Z - 3, X + 3, Z + 3)))
print(cmd(IN + 'setworldspawn %d 207 %d' % (X, Z)))
print(cmd('list'))
for n in ('Uber_Byte',):
    print(cmd(IN + 'tp %s %d 207 %d' % (n, X, Z)))
    print(cmd(IN + 'effect give %s minecraft:slow_falling 30 0 true' % n))
    print(cmd(IN + 'spawnpoint %s %d 207 %d' % (n, X, Z)))
print('Rescue done. Anyone who joins later is moved to the platform once.')
