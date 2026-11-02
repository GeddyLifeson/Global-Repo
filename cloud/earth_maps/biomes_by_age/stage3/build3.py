import numpy as np, json, io, base64, os, glob
from PIL import Image
B2 = '/tmp/claude-0/bm2/'; B3 = '/tmp/claude-0/bm3/'
W, H = 1440, 720
kas = [k for k in list(range(16)) + ['f245', 'f585'] if os.path.exists(B3 + f'names_{k}.npz')]
print('slices', kas)
vocab = {}; domc = {}
def agg(idx):                     # 2x2 -> mode-ish
    a, b, c, d = idx[0::2, 0::2], idx[0::2, 1::2], idx[1::2, 0::2], idx[1::2, 1::2]
    out = np.where((a == b) | (a == c) | (a == d), a, np.where((b == c) | (b == d), b, np.where(c == d, c, a)))
    return out
grids = {}
for k in kas:
    z = np.load(B3 + f'names_{k}.npz', allow_pickle=True)
    names = z['vocab']; idx = z['idx']
    g = np.zeros((H, W), np.uint16)
    loc = agg(idx)                                  # 580 x 1440, local ids, -1 none
    lut = np.zeros(len(names) + 1, np.uint16)
    for i, n in enumerate(names):
        lut[i + 1] = vocab.setdefault(str(n), len(vocab) + 1)
    g[20:600] = lut[loc + 1]
    R = np.array(Image.open(B2 + f's{k}.png'))
    ok = (R >= 1) & (R <= 27) & (g > 0)
    for gid, cl in zip(g[ok], R[ok]):
        domc.setdefault(int(gid), np.zeros(30, int))[int(cl)] += 1
    grids[k] = g
inv = [None] * len(vocab)
for n, i in vocab.items(): inv[i - 1] = n
dom = [int(domc[i].argmax()) if i in domc else 4 for i in range(1, len(vocab) + 1)]
tot = 0; pk = {}
for k, g in grids.items():
    assert g.max() < 256
    buf = io.BytesIO(); Image.fromarray(g.astype(np.uint8), 'L').save(buf, 'PNG', optimize=True); pk[k] = buf.getvalue(); tot += len(pk[k])
    print(k, len(pk[k]))
print('total', tot, 'biomes', len(inv))
json.dump({'vocab': inv, 'dom': dom, 'pk': {str(k): base64.b64encode(v).decode() for k, v in pk.items()}}, open(B3 + 'pk.json', 'w'))
