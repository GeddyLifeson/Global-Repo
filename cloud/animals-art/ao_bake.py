"""Bake ambient occlusion onto an Untamed Wilds model's own UV layout (headless Blender, bpy 5.2).

    python ao_bake.py MODELS_JSON PLAN VARIANT SCALE OUT.png
Builds every visible box of the model for that species variant, posed as in the model code, and bakes AO to an
image of texWidth*SCALE x texHeight*SCALE. Mirrored parts share UVs, as in game.
"""
import json, math, sys
import bpy, bmesh
from mathutils import Matrix, Vector

models, plan, variant, scale, out = sys.argv[-5:]
m = json.load(open(models))[plan]; variant, scale = int(variant), int(scale)
tw, th = m['tw'], m['th']
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = 'CYCLES'; sc.cycles.samples = 64; sc.cycles.device = 'CPU'

bm = bmesh.new()
uvl = bm.loops.layers.uv.new('UV')


def pose(p):
    rx, ry, rz = p['rot']
    return Matrix.Translation(Vector(p['pivot'])) @ Matrix.Rotation(rz, 4, 'Z') @ Matrix.Rotation(ry, 4, 'Y') @ Matrix.Rotation(rx, 4, 'X')


def add_box(mat, b, uv, mirror):
    x, y, z, w, h, d, g = b
    u, v = uv
    x0, y0, z0, x1, y1, z1 = x - g, y - g, z - g, x + w + g, y + h + g, z + d + g
    if mirror:
        x0, x1 = x1, x0
    P = {7: (x0, y0, z0), 0: (x1, y0, z0), 1: (x1, y1, z0), 2: (x0, y1, z0), 3: (x0, y0, z1), 4: (x1, y0, z1), 5: (x1, y1, z1), 6: (x0, y1, z1)}
    w, h, d = (int(round(t)) for t in (w, h, d))
    quads = [([4, 0, 1, 5], u + d + w, v + d, u + d + w + d, v + d + h), ([7, 3, 6, 2], u, v + d, u + d, v + d + h),
             ([4, 3, 7, 0], u + d, v, u + d + w, v + d), ([1, 2, 6, 5], u + d + w, v + d, u + d + w + w, v),
             ([0, 7, 2, 1], u + d, v + d, u + d + w, v + d + h), ([3, 4, 5, 6], u + d + w + d, v + d, u + d + w + d + w, v + d + h)]
    centre = mat @ Vector(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    for ids, u1, v1, u2, v2 in quads:
        if u1 == u2 or v1 == v2:
            continue
        verts = [bm.verts.new(mat @ Vector(P[i])) for i in ids]
        f = bm.faces.new(verts)
        for loop, (s, t) in zip(f.loops, [(u2, v1), (u1, v1), (u1, v2), (u2, v2)]):
            loop[uvl].uv = (s / tw, 1 - t / th)
        f.normal_update()
        if w and h and d and f.normal.dot(f.calc_center_median() - centre) < 0:
            f.normal_flip()


def walk(name, parent):
    p = m['parts'][name]
    if p['sets'] and variant not in p['sets']:
        return
    mat = parent @ pose(p)
    for b in p['boxes']:
        add_box(mat, b, p['uv'], p['mirror'])
    for c in p['children']:
        walk(c, mat)


for r in m['roots']:
    walk(r, Matrix.Scale(1 / 16, 4))
me = bpy.data.meshes.new('animal'); bm.to_mesh(me)
ob = bpy.data.objects.new('animal', me); sc.collection.objects.link(ob)
img = bpy.data.images.new('ao', tw * scale, th * scale, alpha=True); img.generated_color = (1, 1, 1, 0)
mat = bpy.data.materials.new('m'); mat.use_nodes = True
node = mat.node_tree.nodes.new('ShaderNodeTexImage'); node.image = img; mat.node_tree.nodes.active = node
me.materials.append(mat)
w = bpy.data.worlds.new('w'); sc.world = w
bpy.context.view_layer.objects.active = ob; ob.select_set(True)
sc.render.bake.margin = 2
bpy.ops.object.bake(type='AO')
img.filepath_raw = out; img.file_format = 'PNG'; img.save()
