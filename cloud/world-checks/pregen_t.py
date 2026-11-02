import sys, time
from rcon import rcon
from sites import transect_chunks
for name in sys.argv[1:]:
    t = time.time(); ch = transect_chunks(name)
    for i in range(0, len(ch), 50):
        rcon([f"forceload add {cx*16} {cz*16}" for cx, cz in ch[i:i + 50]] + ["save-all flush", "forceload remove all"])
    print(name, len(ch), "chunks", round(time.time() - t), "s", flush=True)
