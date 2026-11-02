import runpy, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
for s in ['gen_player.py','gen_perks.py','gen_enemies.py','gen_bosses.py','gen_world.py']: runpy.run_path(s)
