import sys, time
from rcon import rcon
from sites import box
for name in sys.argv[1:]:
    x0, z0, x1, z1 = box(name); zm = (z0 + z1) // 2
    t = time.time()
    r = rcon([f"forceload add {x0*16} {z0*16} {x1*16} {zm*16}", f"forceload add {x0*16} {(zm+1)*16} {x1*16} {z1*16}"])
    print(name, r, round(time.time() - t), "s", flush=True)
