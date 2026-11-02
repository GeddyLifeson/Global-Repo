"""Bake ambient occlusion onto a vanilla model layer's own UV layout (headless Blender, bpy 5.2).

    python poly_ao.py LAYERS_JSON KEY SCALE HIDE OUT.png
LAYERS_JSON comes from ExportLayers.java (posed polygons with pixel UVs). HIDE is a regex of part paths left out
(parts the game hides by default, such as chests, saddles or a rolled-up shell), or '-' for none.
"""
import json, re, sys
import bpy, bmesh
from mathutils import Vector

layers, key, scale, hide, out = sys.argv[-5:]
m = json.load(open(layers))[key]; scale = int(scale)
tw, th = m['tw'], m['th']
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = 'CYCLES'; sc.cycles.samples = 64; sc.cycles.device = 'CPU'
bm = bmesh.new(); uvl = bm.loops.layers.uv.new('UV')
for f in m['faces']:
    if hide != '-' and re.search(hide, f['part']):
        continue
    us = [v[3] for v in f['v']]; vs = [v[4] for v in f['v']]
    if max(us) - min(us) < 1e-4 or max(vs) - min(vs) < 1e-4:
        continue
    face = bm.faces.new([bm.verts.new(Vector((v[0], -v[1], -v[2]))) for v in f['v']])  # game y down, z forward -> Blender up
    for loop, v in zip(face.loops, f['v']):
        loop[uvl].uv = (v[3] / tw, 1 - v[4] / th)
me = bpy.data.meshes.new('mob'); bm.to_mesh(me)
ob = bpy.data.objects.new('mob', me); sc.collection.objects.link(ob)
img = bpy.data.images.new('ao', tw * scale, th * scale, alpha=True); img.generated_color = (1, 1, 1, 0)
mat = bpy.data.materials.new('m'); mat.use_nodes = True
node = mat.node_tree.nodes.new('ShaderNodeTexImage'); node.image = img; mat.node_tree.nodes.active = node
me.materials.append(mat)
sc.world = bpy.data.worlds.new('w')
bpy.context.view_layer.objects.active = ob; ob.select_set(True)
sc.render.bake.margin = 2
bpy.ops.object.bake(type='AO')
img.filepath_raw = out; img.file_format = 'PNG'; img.save()
