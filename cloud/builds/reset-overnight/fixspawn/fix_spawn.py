"""Set the world spawn and border centre at Creag Ruadh on the running server (reads rcon settings from server.properties)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rcon
root = sys.argv[1] if len(sys.argv) > 1 else r'E:\DiaithirServer'
props = dict(l.strip().split('=', 1) for l in open(os.path.join(root, 'server', 'server.properties'), encoding='utf-8') if '=' in l and not l.startswith('#'))
r = rcon.Rcon('127.0.0.1', int(props['rcon.port']), props['rcon.password'], timeout=60)
for c in ('execute in minecraft:overworld run setworldspawn -251201 207 -1541408', 'worldborder center -251201 -1541408', 'worldborder set 40000'):
    print(r.command(c))
print('Spawn set at Creag Ruadh. New players spawn there; players already in the world: /tp them or relog after /spawnpoint.')
