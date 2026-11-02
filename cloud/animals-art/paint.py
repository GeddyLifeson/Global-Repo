"""Paint an Untamed Wilds animal skin fresh, Factorio style, at SCALE x its texture size.

The old 16x skin is only a colour reference (blurred, so markings survive as soft patches). Every face is drawn
as its own picture: fur strands, hide wrinkles, shell scutes, horn rings or hoof keratin as a height field, lit
from the face's upper left, with bevelled edges, baked AO from Blender (ao_bake.py), dust and mud low on the legs.

    python3 paint.py MODELS_JSON PLAN SPECIES SRC16.png AO.png OUT.png [SCALE]
"""
import json, re, sys, zlib
import numpy as np
from PIL import Image
from eyes import paint_eyes

LIGHT = np.array([-0.5, -0.6, 0.9]) / np.linalg.norm([-0.5, -0.6, 0.9])  # texture space: x right, y down, z out
MUTE, WARM = 0.72, np.array([1.04, 0.98, 0.88])
MUD = np.array([86, 68, 48], np.float32)
HIDE_SPECIES = {'african', 'asian', 'pygmy', 'notiomastodon'}
SHAGGY_SPECIES = {'woolly', 'columbian', 'muskox', 'megatherium', 'mylodon', 'paramylodon', 'nothrotheriops', 'megalonyx'}


def material(plan, species, name):
    if re.search(r'^eye_', name):
        return 'eye'
    if re.search(r'tusk|claw|spike|^(as|al|ar|pm|pg)_|^(hl|hlf|md|ib|ibf|bh|bhf|mg|mgf)_|^sg_(left|right)$|^boss$', name):
        return 'horn'
    if re.search(r'(arm|leg)_(left|right)_3', name):
        return 'hoof' if plan in ('Equid', 'Bovid', 'Cervid') else 'pad'
    if plan == 'Glyptodont':
        return 'shell' if re.search(r'carapace|ridge|cap|club', name) else 'hide'
    if plan == 'Elephantid' and species in HIDE_SPECIES and not re.search(r'hair|skirt', name):
        return 'hide'
    if re.search(r'skirt|mane|hair|ruff|beard|tuft|forelock|hump', name) or species in SHAGGY_SPECIES:
        return 'shaggy'
    return 'fur'


def blur(a, r, axis):
    """Box blur of radius r along one axis (edge clamped)."""
    if r < 1:
        return a
    pad = [(0, 0)] * a.ndim; pad[axis] = (r + 1, r)
    c = np.cumsum(np.pad(a, pad, mode='edge'), axis=axis)
    hi = np.take(c, np.arange(2 * r + 1, c.shape[axis]), axis=axis)
    lo = np.take(c, np.arange(0, c.shape[axis] - 2 * r - 1), axis=axis)
    return (hi - lo) / (2 * r + 1)


def soft(a, r):
    return blur(blur(a, r, 0), r, 1)


def height(kind, h, w, rng, s):
    n = rng.random((h, w))
    if kind in ('fur', 'shaggy', 'pad'):
        along = 1 if kind != 'shaggy' and w > h * 1.3 else 0  # strands follow the face's long axis; shaggy hair hangs down
        length = int((1.5 if kind != 'shaggy' else 4) * s)
        strands = blur(n, length, along)
        strands = (strands - strands.mean()) * (2 * length + 1) ** 0.5
        clumps = soft(rng.random((h, w)), 3 * s)
        return 0.3 * strands + 1.6 * (clumps - clumps.mean()) / (clumps.std() + 1e-6) * 0.12 + 0.2 * soft(n, 1)
    if kind == 'hide':
        wr = blur(n, 3 * s, 1) * (6 * s + 1) ** 0.5       # horizontal wrinkles
        return 0.7 * (wr - wr.mean()) + 0.3 * soft(n, max(1, s // 2))
    if kind == 'shell':
        cell = 3 * s
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        d = np.full((h, w), 1e9, np.float32)
        for cy in np.arange(-cell, h + cell, cell):
            for cx in np.arange(-cell, w + cell, cell * 1.0):
                ox = cx + (cell / 2 if int(cy // cell) % 2 else 0) + rng.uniform(-cell * .2, cell * .2)
                d = np.minimum(d, np.hypot(xx - ox, yy - cy - rng.uniform(-cell * .2, cell * .2)))
        return 1 - np.clip(d / (cell * 0.62), 0, 1) ** 1.5 + 0.15 * soft(n, 1)
    if kind == 'horn':
        yy = np.mgrid[0:h, 0:w][0].astype(np.float32)
        return 0.5 * np.sin(yy / (1.5 * s) * np.pi) + 0.3 * blur(n, 2 * s, 0)
    if kind == 'pelt':                                     # short tufted fur in overlapping layers (vanilla-size boxes)
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        warp = (soft(rng.random((h, w)), s) - 0.5) * 6 * s
        tufts = ((yy + warp) % (2.5 * s)) / (2.5 * s)
        strands = blur(n, max(1, int(0.8 * s)), 0)
        strands = (strands - strands.mean()) * (1.6 * s + 1) ** 0.5
        clumps = soft(rng.random((h, w)), 2 * s)
        return 0.2 * (1 - tufts) + 0.4 * strands + 0.6 * (clumps - clumps.mean()) / (clumps.std() + 1e-6) * 0.25 + 0.1 * n
    if kind == 'skin':                                     # bare skin: soft mottling, fine pores, a few bristles
        pores = n - soft(n, 1)
        bristle = np.clip(blur(rng.random((h, w)) ** 30, s, 0) * 4, 0, 1)
        return 0.5 * (soft(n, 2 * s) - 0.5) * 4 + 0.25 * pores + 0.4 * bristle
    if kind == 'cloth':                                    # woven cloth with soft folds
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        weave = np.sin(xx * np.pi / max(1, s // 2)) * np.sin(yy * np.pi / max(1, s // 2))
        folds = blur(rng.random((h, w)), 3 * s, 0)
        return 0.15 * weave + 1.5 * (folds - folds.mean()) * (6 * s + 1) ** 0.5 * 0.2 + 0.1 * n
    if kind == 'bone':                                     # smooth bone with pits and hairline cracks
        cracks = np.clip(1 - np.abs(soft(n, s) - 0.5) * 40, 0, 1)
        return 0.3 * (soft(n, 2 * s) - 0.5) * 3 - 0.5 * cracks - 0.2 * (n > 0.97)
    if kind == 'chitin':                                   # hard glossy plates
        yy = np.mgrid[0:h, 0:w][0].astype(np.float32)
        return 0.6 * ((yy % (3 * s)) / (3 * s)) + 0.1 * soft(n, 1)
    if kind == 'gel':                                      # wobbly jelly
        return 0.8 * (soft(n, 3 * s) - 0.5) * 4
    if kind == 'stone':                                    # chipped rock
        return 0.6 * (soft(n, s) - 0.5) * 4 + 0.3 * (soft(n, 3 * s) - 0.5) * 6 + 0.15 * n
    if kind == 'metal':                                    # worn plate, brushed, a few dents
        return 0.15 * blur(n, 3 * s, 1) * (6 * s + 1) ** 0.5 - 0.6 * (soft(n, 2 * s) > 0.56)
    if kind == 'wood':                                     # grain along the long axis
        along = 1 if w > h else 0
        g = blur(n, 4 * s, along) * (8 * s + 1) ** 0.5
        return 0.5 * (g - g.mean()) + 0.1 * n
    if kind == 'feather':                                  # overlapping rows of scalloped feather tips
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        row = 2 * s
        off = (yy // row) % 2 * 0.75 * s
        t = (yy + 0.5 * s * np.abs(np.sin((xx + off) * np.pi / (1.5 * s)))) % row / row
        return 0.8 * (1 - t) + 0.15 * blur(n, s, 0)
    if kind == 'wool':                                     # tight curls
        curls = soft(n, s) - soft(n, 3 * s)
        return 2.5 * curls / (curls.std() + 1e-6) * 0.3 + 0.1 * n
    if kind == 'wing':                                     # thin membrane with veins
        xx = np.mgrid[0:h, 0:w][1].astype(np.float32)
        return 0.25 * np.cos(xx / (2 * s) * np.pi) ** 8 + 0.05 * soft(n, 1)
    return 0.3 * blur(n, 2 * s, 0)                        # hoof, eye: smooth keratin


def light(H, strength):
    gy, gx = np.gradient(H)
    nrm = np.dstack([-gx * strength, -gy * strength, np.ones_like(H)])
    nrm /= np.linalg.norm(nrm, axis=2, keepdims=True)
    return nrm @ LIGHT


def paint_face(base, alpha, kind, ao, rng, s, low, depth=1.0):
    h, w = alpha.shape
    H = height(kind, h, w, rng, s)
    lit = light(H, {'shell': 3.0, 'horn': 1.5, 'hide': 2.0, 'skin': 1.5, 'pelt': 1.8, 'cloth': 1.5, 'bone': 1.8, 'chitin': 2.0, 'gel': 1.0, 'stone': 2.5, 'metal': 2.0, 'wood': 2.0, 'feather': 2.5, 'wool': 2.0}.get(kind, 1.2))
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    form = 1.1 - 0.22 * yy / max(h - 1, 1) - 0.08 * xx / max(w - 1, 1)  # face lit from its upper left
    edge = np.ones((h, w), np.float32)
    k = max(1, s // 2)
    edge[:k, :] *= 1.12; edge[:, :k] *= 1.06; edge[-k:, :] *= 0.72; edge[:, -k:] *= 0.8  # bevel
    col = base * ((1.15 - 0.6 * depth) + 0.6 * depth * lit)[..., None] * (form * edge)[..., None]
    if depth != 1.0:   # tone follows the relief too: dark gaps between strands, scales and folds
        col *= (1 + 0.16 * (depth - 1) / 0.35 * np.clip((H - H.mean()) / (H.std() + 1e-6), -2, 2))[..., None]
    if kind == 'shell':
        col *= (0.75 + 0.35 * np.clip(H, 0, 1))[..., None]
    if kind in ('horn', 'chitin', 'gel', 'metal'):
        col += 40 * np.clip(lit - 0.9, 0, 1)[..., None] * 4  # waxy shine
    col *= (0.38 + 0.62 * ao)[..., None]
    dust = soft(rng.random((h, w)), 2 * s)
    col *= (0.9 + 0.2 * (dust - dust.mean()) / (dust.std() + 1e-6) * 0.25)[..., None]
    if low:  # mud creeping up the lower legs
        m = np.clip((yy / max(h - 1, 1) - 0.6) * 1.6 + (dust - 0.5) * 0.8, 0, 0.6)
        col = col * (1 - m[..., None]) + MUD * (0.6 + 0.4 * lit[..., None]) * m[..., None]
    return np.clip(col, 0, 255)


def grade(rgb):
    grey = rgb.mean(-1, keepdims=True)
    return np.clip((grey + (rgb - grey) * MUTE) * WARM, 0, 255)


def faces(u, v, w, h, d):
    return [(u, v + d, d, h), (u + d, v + d, w, h), (u + d + w, v + d, d, h), (u + 2 * d + w, v + d, w, h), (u + d, v, w, d), (u + d + w, v, w, d)]


def paint(model, plan, species, variant, src, ao, s=4):
    src = np.asarray(src.convert('RGBA'), np.float32)
    big = src.repeat(s, 0).repeat(s, 1)
    ao = np.asarray(ao.convert('L'), np.float32) / 255
    out = np.zeros_like(big)
    rng = np.random.default_rng(zlib.crc32(f'{plan}/{species}'.encode()))
    for name, p in model['parts'].items():
        if p['sets'] and variant not in p['sets']:
            continue
        kind = material(plan, species, name)
        if kind == 'eye':
            continue
        low = bool(re.search(r'(arm|leg)_(left|right)_[23]', name))
        for b in p['boxes']:
            w, h, d = (int(round(t)) for t in b[3:6])
            for qi, (x, y, fw, fh) in enumerate(faces(*p['uv'], w, h, d)):
                if fw <= 0 or fh <= 0:
                    continue
                sl = (slice(y * s, (y + fh) * s), slice(x * s, (x + fw) * s))
                a = big[sl][..., 3]
                if not (a > 0).any():
                    continue
                base = soft(big[sl][..., :3], s)  # old skin as a soft colour reference only
                if kind in ('horn', 'hoof', 'pad'):
                    base = np.broadcast_to(big[sl][..., :3][a > 0].mean(0), base.shape)
                occl = ao[sl] if w and h and d else np.maximum(ao[sl], 0.75)  # flat fringes sit against the body
                face = paint_face(base, a, kind, occl, rng, s, low)
                if name.endswith('snout') or name.endswith('nose'):
                    if qi == 1:  # front of the muzzle: dark wet nose leather with nostrils
                        face = nose(face, s)
                out[sl] = np.dstack([grade(face), a])
    return paint_eyes(Image.fromarray(out.astype(np.uint8)), model, scale=s, look='real')


def nose(face, s):
    h, w = face.shape[:2]
    face = face * 0.55
    yy, xx = np.mgrid[0:h, 0:w]
    for cx in (w * 0.3, w * 0.7):
        r = max(1.0, min(w, h) * 0.13)
        hole = ((xx - cx) / r) ** 2 + ((yy - h * 0.38) / (r * 1.3)) ** 2 < 1
        face[hole] = face[hole] * 0.25
    return face


if __name__ == '__main__':
    models, plan, species, src, ao, out = sys.argv[1:7]
    s = int(sys.argv[7]) if len(sys.argv) > 7 else 4
    m = json.load(open(models))[plan]
    variant = int(sys.argv[8]) if len(sys.argv) > 8 else 0
    paint(m, plan, species, variant, Image.open(src), Image.open(ao), s).save(out)
