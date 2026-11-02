"""Photoreal-ish dish renderer for the Diaithir kit. A dish is a JSON scene (vessel, base mounds, sauce pools, pieces, garnish) built
from parametric components with PBR food materials (subsurface, coat, mottle, grill stripes), lit by the kit's sun plus a softbox and rim.
    python dish_run.py -- SPECS.json OUT_DIR [kit options]
spec: {"name": ..., "views": ["icon"], "tilt": 8, "zoom": 0.68, "materials": {"d": {"type": "flat"}}, "parts": [{"part": "scene", "mat": "d", "scene": {"vessel": {...}, "layers": [component, ...]}}]} (see dish_wrap in make_dish_scenes.py)
component kinds: mound pool chunk slice fillet ball cyl wedge egg shrimp leaf ring noodles scatter grains
 common fields: mat (preset name) | color [r,g,b]; at [x,z] (px from centre, plate radius ~6.5); r (spread radius); n (count); s (size px);
 h (height px); stripes (grill marks); lvl 'floor'|'base'; seed."""
import sys, math, random, colorsys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import bpy, bmesh
from mathutils import Vector, Matrix, Euler
import kit, parts_extra, parts_magic

# name: (rgb, rough, sss, sss_radius_scale, coat, mottle, bump)
P = {
 'meat_cooked': ((132, 74, 42), .55, .35, 1, 0, .25, .5), 'meat_seared': ((92, 52, 30), .5, .2, 1, 0, .35, .6), 'meat_rare': ((176, 72, 62), .4, .5, 1, .1, .15, .3),
 'chicken_roast': ((206, 144, 70), .5, .3, 1, 0, .3, .5), 'chicken_white': ((238, 214, 176), .5, .5, 1, 0, .1, .3), 'pork_roast': ((190, 120, 70), .5, .35, 1, 0, .3, .4),
 'fish_fillet': ((240, 150, 120), .45, .5, 1, .1, .15, .3), 'fish_white': ((246, 238, 222), .45, .5, 1, .1, .1, .3), 'fish_fried': ((214, 150, 60), .6, .2, 1, 0, .35, .8),
 'shrimp': ((238, 112, 72), .35, .4, 1, .15, .2, .3), 'shell': ((214, 200, 184), .35, .1, 1, .1, .2, .3), 'squid': ((236, 224, 206), .4, .3, 1, .1, .1, .2),
 'bread_crust': ((196, 130, 60), .65, .15, 1, 0, .35, .7), 'bread_crumb': ((240, 220, 170), .8, .3, 1, 0, .15, .8), 'pastry': ((222, 164, 80), .6, .2, 1, 0, .3, .6),
 'batter_fried': ((210, 148, 60), .65, .15, 1, 0, .4, 1.0), 'tortilla': ((226, 196, 140), .75, .2, 1, 0, .25, .5), 'dough': ((236, 214, 164), .7, .3, 1, 0, .15, .4),
 'cheese_yellow': ((250, 202, 72), .35, .4, 1, .05, .15, .2), 'cheese_white': ((246, 240, 224), .4, .4, 1, 0, .1, .2), 'cheese_melted': ((252, 196, 60), .25, .4, 1, .2, .25, .3),
 'sauce_red': ((178, 38, 22), .18, .2, 1, .6, .15, .15), 'sauce_brown': ((108, 56, 28), .2, .2, 1, .6, .2, .15), 'sauce_cream': ((240, 224, 190), .25, .4, 1, .4, .1, .1),
 'sauce_green': ((90, 140, 46), .25, .25, 1, .4, .2, .2), 'sauce_yellow': ((232, 160, 28), .2, .3, 1, .5, .2, .15), 'sauce_orange': ((226, 112, 28), .2, .3, 1, .5, .2, .15),
 'sauce_purple': ((110, 30, 70), .15, .2, 1, .6, .15, .1), 'broth_clear': ((206, 148, 60), .1, .2, 1, .7, .1, .05), 'broth_dark': ((92, 52, 30), .12, .2, 1, .7, .1, .05),
 'broth_white': ((232, 224, 204), .15, .3, 1, .6, .1, .05), 'honey': ((230, 150, 20), .08, .3, 1, .8, .1, .05), 'chocolate': ((74, 42, 28), .2, .1, 1, .5, .1, .1),
 'rice_white': ((246, 242, 228), .6, .45, 1, 0, .1, .6), 'rice_yellow': ((236, 196, 74), .6, .35, 1, 0, .2, .6), 'rice_brown': ((196, 160, 110), .6, .3, 1, 0, .2, .6),
 'noodle': ((238, 208, 132), .4, .35, 1, .15, .1, .2), 'pasta': ((240, 208, 120), .45, .3, 1, .1, .1, .2), 'grain': ((226, 190, 110), .7, .2, 1, 0, .25, .6),
 'veg_green': ((72, 142, 48), .45, .35, 1, .1, .25, .3), 'veg_dark': ((40, 96, 38), .5, .3, 1, 0, .3, .3), 'herb': ((62, 130, 44), .55, .3, 1, 0, .35, .4),
 'tomato': ((204, 42, 30), .25, .35, 1, .3, .15, .2), 'carrot': ((236, 124, 30), .4, .3, 1, .1, .15, .2), 'potato': ((226, 190, 106), .55, .3, 1, 0, .2, .4),
 'potato_fried': ((222, 168, 70), .6, .15, 1, 0, .4, .6), 'onion': ((238, 228, 204), .35, .35, 1, .1, .1, .2), 'onion_red': ((150, 50, 100), .35, .35, 1, .1, .2, .2),
 'pepper_red': ((200, 36, 28), .25, .3, 1, .3, .1, .15), 'pepper_green': ((60, 138, 46), .25, .3, 1, .3, .1, .15), 'chili': ((190, 30, 20), .25, .2, 1, .3, .1, .1),
 'mushroom': ((166, 124, 90), .5, .3, 1, 0, .3, .4), 'beans': ((140, 86, 52), .35, .2, 1, .1, .25, .3), 'lentil': ((160, 110, 56), .5, .2, 1, 0, .3, .5),
 'corn': ((244, 198, 54), .3, .3, 1, .2, .15, .3), 'egg_white': ((250, 248, 240), .2, .4, 1, .4, .05, .1), 'yolk': ((246, 170, 24), .15, .5, 1, .5, .05, .05),
 'cream': ((252, 246, 232), .3, .4, 1, .3, .05, .1), 'butter': ((250, 220, 110), .3, .4, 1, .2, .05, .1), 'sugar': ((252, 250, 244), .5, .3, 1, 0, .1, .8),
 'berry_red': ((176, 24, 50), .2, .25, 1, .4, .15, .2), 'berry_blue': ((52, 50, 120), .2, .2, 1, .4, .15, .2), 'fruit_yellow': ((242, 206, 70), .3, .3, 1, .2, .15, .2),
 'fruit_orange': ((240, 140, 30), .3, .3, 1, .2, .15, .2), 'fruit_green': ((140, 180, 60), .3, .3, 1, .2, .15, .2), 'nut': ((190, 140, 84), .5, .2, 1, 0, .3, .5),
 'sesame': ((236, 220, 180), .5, .1, 1, 0, .1, .6), 'spice_red': ((176, 52, 24), .8, 0, 1, 0, .3, .5), 'spice_yellow': ((220, 160, 40), .8, 0, 1, 0, .3, .5),
 'seaweed': ((28, 54, 40), .35, .1, 1, .2, .2, .3), 'tofu': ((244, 234, 206), .5, .4, 1, 0, .1, .3), 'sausage': ((156, 80, 52), .35, .25, 1, .2, .3, .3),
 'bacon': ((176, 70, 54), .4, .3, 1, .1, .4, .3), 'ham': ((226, 140, 130), .4, .4, 1, .1, .1, .2), 'jam': ((150, 24, 44), .1, .2, 1, .8, .1, .05),
 # vessels
 'white_ceramic': ((150, 150, 148), .15, .0, 1, .3, 0, .0), 'blue_ceramic': ((88, 120, 170), .15, .0, 1, .3, 0, .0), 'clay': ((176, 98, 58), .6, 0, 1, 0, .3, .5),
 'clay_dark': ((86, 56, 42), .55, 0, 1, 0, .3, .5), 'wood': ((150, 104, 64), .55, 0, 1, 0, .4, .4), 'wood_dark': ((92, 60, 40), .55, 0, 1, 0, .4, .4),
 'iron': ((52, 54, 58), .45, 0, 1, 0, .3, .5), 'copper': ((196, 108, 62), .3, 0, 1, 0, .2, .2), 'steel': ((170, 174, 180), .3, 0, 1, 0, .2, .2),
 'bamboo': ((200, 176, 100), .45, 0, 1, 0, .3, .3), 'banana_leaf': ((70, 140, 56), .45, .2, 1, 0, .3, .3), 'slate': ((54, 58, 64), .5, 0, 1, 0, .3, .5),
 'paper': ((232, 214, 176), .85, .1, 1, 0, .2, .3), 'glass': ((196, 224, 230), .05, 0, 1, 0, 0, 0), 'cloth': ((226, 210, 190), .9, .1, 1, 0, .3, .5),
 'gold': ((224, 178, 60), .25, 0, 1, 0, .1, .1)}
METAL = {'iron', 'copper', 'steel', 'gold'}
STRIPE_MATS = {'meat_cooked', 'meat_seared', 'chicken_roast', 'pork_roast', 'fish_fillet', 'fish_white', 'sausage', 'bacon', 'bread_crust', 'tortilla', 'tofu', 'ham', 'potato'}

def hexrgb(c): return tuple(c)
def mk_material(name, rgb=None, stripes=False, ring=None):
    key = '%s|%s|%d|%s' % (name, rgb, stripes, ring)
    if key in bpy.data.materials: return bpy.data.materials[key]
    base, rough, sss, srad, coat, mottle, bump = P[name]
    if rgb is not None: base = tuple(rgb)
    m = bpy.data.materials.new(key); m.use_nodes = True; g = kit.G(m)
    b = g.n['Principled BSDF']
    tc = g.new('ShaderNodeTexCoord')
    nz = g.new('ShaderNodeTexNoise', Scale=14.0, Detail=5.0, Roughness=0.55); g.L(tc.outputs['Object'], nz.inputs['Vector'])
    nz2 = g.new('ShaderNodeTexNoise', Scale=60.0, Detail=3.0, Roughness=0.6); g.L(tc.outputs['Object'], nz2.inputs['Vector'])
    A, B = kit.lin(base, 1.0 - mottle * 0.45), kit.lin(base, 1.0 + mottle * 0.35)
    col = g.mix(A, B, nz.outputs['Fac'])
    if stripes:
        # grill marks: dark diagonal bars across the top
        mp = g.new('ShaderNodeMapping'); g.L(tc.outputs['Object'], mp.inputs['Vector']); mp.inputs['Rotation'].default_value = (0, 0, 0.7)
        w = g.new('ShaderNodeTexWave', Scale=7.0, Distortion=1.2, Detail=2.0); w.wave_type = 'BANDS'; w.bands_direction = 'X'; g.L(mp.outputs['Vector'], w.inputs['Vector'])
        cr = g.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].position = 0.72; cr.color_ramp.elements[1].position = 0.78; g.L(w.outputs['Fac'], cr.inputs['Fac'])
        sep = g.new('ShaderNodeSeparateXYZ'); nrm = g.new('ShaderNodeNewGeometry'); g.L(nrm.outputs['Normal'], sep.inputs[0])
        top = g.op('GREATER_THAN', sep.outputs['Z'], 0.45)
        k = g.op('MULTIPLY', cr.outputs['Color'] if False else g.op('SUBTRACT', 1.0, cr.outputs['Color']), top)
        col = g.mix(col, kit.lin((40, 24, 16), 1.0), g.op('MULTIPLY', k, 0.75))
    g.L(col, b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = rough
    b.inputs['Specular IOR Level'].default_value = 0.5
    if name in METAL: b.inputs['Metallic'].default_value = 0.9
    if sss:
        b.inputs['Subsurface Weight'].default_value = sss
        b.inputs['Subsurface Radius'].default_value = (0.6 * srad, 0.3 * srad, 0.15 * srad)
        b.inputs['Subsurface Scale'].default_value = 0.02
    if coat: b.inputs['Coat Weight'].default_value = coat; b.inputs['Coat Roughness'].default_value = 0.05
    if name == 'glass':
        b.inputs['Transmission Weight'].default_value = 0.9; b.inputs['Roughness'].default_value = 0.03
    bm = g.new('ShaderNodeBump', Strength=bump, Distance=0.01); g.L(nz2.outputs['Fac'], bm.inputs['Height']); g.L(bm.outputs['Normal'], b.inputs['Normal'])
    return m

def lo(x, y, z): return kit.to_bl(x, y, z)
def new_obj(name, bm, mat, smooth=True, disp=0.0, dscale=0.3, subd=0):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(o)
    bpy.context.view_layer.objects.active = o
    for p in me.polygons: p.use_smooth = smooth
    me.materials.append(mat)
    if subd:
        s = o.modifiers.new('s', 'SUBSURF'); s.levels = s.render_levels = subd
    if disp:
        t = bpy.data.textures.new('d', 'CLOUDS'); t.noise_scale = dscale; t.noise_depth = 2
        d = o.modifiers.new('d', 'DISPLACE'); d.texture = t; d.strength = disp / 16; d.mid_level = 0.5
    return o

def blob(bm, c, r, rot=(0, 0, 0), seg=(20, 10), lat=None):
    """ellipsoid centred c (px) with radii r=(rx,ry,rz) px, game axes (y up)"""
    res = bmesh.ops.create_uvsphere(bm, u_segments=seg[0], v_segments=seg[1], radius=1.0)
    vs = res['verts']
    M = Matrix.Translation(lo(*c)) @ Euler((math.radians(rot[0]), math.radians(-rot[2]), math.radians(rot[1])), 'XYZ').to_matrix().to_4x4() @ Matrix.Diagonal((r[0] / 16, r[2] / 16, r[1] / 16, 1))
    for v in vs: v.co = M @ v.co
    return vs
def tube(bm, pts, rad, seg=8):
    """polyline tube through px points"""
    prev = None
    for i, p in enumerate(pts):
        r = rad[i] if isinstance(rad, (list, tuple)) else rad
        if i + 1 < len(pts): d = Vector(lo(*pts[i + 1])) - Vector(lo(*p))
        else: d = Vector(lo(*p)) - Vector(lo(*pts[i - 1]))
        d.normalize(); a = d.cross(Vector((0, 0, 1)))
        if a.length < 1e-3: a = d.cross(Vector((1, 0, 0)))
        a.normalize(); b2 = d.cross(a)
        ring = [bm.verts.new(Vector(lo(*p)) + (a * math.cos(t * 2 * math.pi / seg) + b2 * math.sin(t * 2 * math.pi / seg)) * r / 16) for t in range(seg)]
        if prev:
            for t in range(seg): bm.faces.new((prev[t], prev[(t + 1) % seg], ring[(t + 1) % seg], ring[t]))
        prev = ring
    return

def lathe(profile, mat, name='vessel', seg=48):
    bm = bmesh.new(); vs = [bm.verts.new(lo(r, y, 0)) for r, y in profile]
    es = [bm.edges.new((vs[i], vs[i + 1])) for i in range(len(vs) - 1)]
    bmesh.ops.spin(bm, geom=vs + es, cent=lo(0, 0, 0) + Vector((0, 0, 0)), axis=(0, 0, 1), angle=2 * math.pi, steps=seg)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.verts.ensure_lookup_table()
    return new_obj(name, bm, mat, True, subd=1)

# vessel profiles: (radius px, height px) from the centre bottom outward and up; all centred on x=0,z=0 then moved to (8,*,8)
def vessel_profile(t, d):
    s = d / 13.0
    if t == 'plate': return [(0, 5.9), (3.2 * s, 5.9), (5.2 * s, 6.0), (6.2 * s, 6.5), (6.6 * s, 6.55), (6.6 * s, 6.3), (5.0 * s, 5.85), (0, 5.8)][::-1] if False else [(0, 6.4), (3.4 * s, 6.4), (5.2 * s, 6.55), (6.4 * s, 7.1), (6.6 * s, 7.1), (6.6 * s, 6.9), (6.2 * s, 6.6), (4.4 * s, 5.95), (0, 5.9)]
    if t == 'bowl': return [(0, 6.4), (3.2 * s, 6.7), (4.8 * s, 7.8), (5.9 * s, 9.6), (6.1 * s, 9.9), (5.8 * s, 9.9), (4.6 * s, 7.2), (3.0 * s, 5.7), (2.6 * s, 5.2), (0, 5.2)]
    if t == 'deep_bowl': return [(0, 6.6), (3.0 * s, 7.2), (4.6 * s, 9.2), (5.3 * s, 11.4), (5.5 * s, 11.7), (5.2 * s, 11.7), (4.2 * s, 8.6), (2.8 * s, 5.8), (2.4 * s, 5.2), (0, 5.2)]
    if t == 'cup': return [(0, 6.0), (2.6 * s, 6.0), (3.4 * s, 8.5), (3.8 * s, 11.6), (3.4 * s, 11.7), (3.0 * s, 8.8), (2.4 * s, 5.4), (0, 5.3)]
    if t == 'mug': return [(0, 6.0), (3.3 * s, 6.0), (3.6 * s, 11.4), (3.3 * s, 11.5), (3.1 * s, 6.6), (0, 6.5)][::-1] if False else [(0, 5.4), (3.6 * s, 5.4), (3.8 * s, 6.0), (3.8 * s, 12.0), (3.5 * s, 12.1), (3.5 * s, 6.5), (0, 6.5)]
    if t == 'pan': return [(0, 6.2), (5.6 * s, 6.2), (6.4 * s, 7.0), (6.8 * s, 7.6), (6.5 * s, 7.6), (5.8 * s, 6.9), (0, 6.6)]
    if t == 'pot': return [(0, 5.4), (4.8 * s, 5.4), (5.2 * s, 6.0), (5.2 * s, 12.0), (5.0 * s, 12.2), (4.8 * s, 6.4), (0, 6.2)]
    if t == 'tray': return [(0, 6.0), (6.8 * s, 6.0), (7.0 * s, 6.8), (6.7 * s, 6.8), (6.5 * s, 6.3), (0, 6.3)]
    if t == 'jar': return [(0, 5.2), (3.6 * s, 5.2), (3.9 * s, 5.6), (3.9 * s, 11.0), (3.4 * s, 11.4), (3.4 * s, 12.0), (3.0 * s, 12.0), (3.0 * s, 11.2), (3.6 * s, 10.8), (3.6 * s, 5.9), (0, 5.8)]
    if t == 'glass': return [(0, 5.4), (3.0 * s, 5.4), (3.2 * s, 6.0), (3.6 * s, 12.0), (3.4 * s, 12.0), (3.0 * s, 6.5), (0, 6.5)]
    return [(0, 6.2), (6.0 * s, 6.2), (6.2 * s, 6.6), (5.9 * s, 6.6), (0, 6.4)]
VESSEL_FLOOR = {'plate': 6.0, 'bowl': 5.9, 'deep_bowl': 5.9, 'cup': 5.9, 'mug': 6.5, 'pan': 6.6, 'pot': 6.2, 'tray': 6.3, 'jar': 5.8, 'glass': 6.5, 'board': 6.7, 'leaf': 6.1, 'basket': 6.3, 'paper': 6.2}
VESSEL_R = {'plate': 5.2, 'bowl': 4.6, 'deep_bowl': 4.2, 'cup': 2.8, 'mug': 3.0, 'pan': 5.6, 'pot': 4.6, 'tray': 6.0, 'jar': 3.0, 'glass': 2.8, 'board': 6.0, 'leaf': 6.0, 'basket': 5.2, 'paper': 5.0}

def build_vessel(v, R):
    t = v.get('type', 'plate'); d = v.get('diam', 13) * 0.84
    mn = v.get('mat', 'white_ceramic'); ring = (0.62, (60, 96, 160)) if mn == 'blue_ceramic' else None
    mat = mk_material(mn if mn in P else 'white_ceramic', v.get('color'), ring=None)
    if t == 'board':
        bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
        sx, sz = v.get('w', 13), v.get('d', 9)
        M = Matrix.Translation(lo(8, 6.35, 8)) @ Matrix.Diagonal((sx / 16, sz / 16, 0.7 / 16, 1))
        for x in bm.verts: x.co = M @ x.co
        bmesh.ops.bevel(bm, geom=bm.edges[:], offset=0.02, segments=2)
        return new_obj('board', bm, mat, True)
    if t == 'leaf':
        bm = bmesh.new(); blob(bm, (8, 6.25, 8), (7.2, 0.35, 5.2), (0, 0, 0), (28, 8))
        return new_obj('leaf', bm, mat, True, disp=0.5, dscale=0.5)
    if t == 'basket':
        o = lathe([(0, 6.0), (5.2, 6.0), (5.8, 7.6), (5.6, 7.6), (5.0, 6.4), (0, 6.3)], mat, seg=40)
    else:
        o = lathe(vessel_profile(t, d), mat, seg=56)
    o.location = Vector(lo(8, 0, 8)) - Vector(lo(0, 0, 0))
    if t == 'mug':
        bm = bmesh.new(); tube(bm, [(11.3, 10.6, 8), (13.2, 10.0, 8), (13.4, 8.4, 8), (11.4, 7.4, 8)], 0.55)
        h = new_obj('handle', bm, mat, True)
    if t == 'pan':
        bm = bmesh.new(); tube(bm, [(14.4, 7.0, 8), (19, 7.4, 8)], 0.6); new_obj('handle', bm, mk_material('wood'), True)
    if t == 'cup':
        bm = bmesh.new(); tube(bm, [(11.2, 10.6, 8), (13, 10.0, 8), (13.1, 8.4, 8), (11.3, 7.6, 8)], 0.5); new_obj('handle', bm, mat, True)
    return o

def surf(base_list, x, z):
    """height of food surface under (x,z) from placed mounds (px)"""
    h = 0
    for (cx, cz, r, top, floor) in base_list:
        d = math.hypot(x - cx, z - cz)
        if d < r: h = max(h, floor + (top - floor) * (1 - (d / r) ** 2) ** 0.5)
    return h

def build_scene(sc, R):
    v = sc.get('vessel', {}); t = v.get('type', 'plate'); build_vessel(v, R)
    floor = VESSEL_FLOOR.get(t, 6.2); vr = VESSEL_R.get(t, 5.0) * v.get('diam', 13) / 13.0 * 0.84
    bases = []
    for L in sc.get('layers', []):
        k = L.get('k', 'chunk'); mn = L.get('mat', 'meat_cooked'); mn = mn if mn in P else 'meat_cooked'
        stripes = L.get('stripes', mn in STRIPE_MATS and L.get('grill', False))
        mat = mk_material(mn, L.get('color'), stripes=stripes)
        rr = random.Random(L.get('seed', 1) * 977 + hash(k) % 97); at = L.get('at', [0, 0]); cx, cz = 8 + at[0], 8 + at[1]
        GS = 1.3; n = L.get('n', 1); s = L.get('s', 1.5) * GS; r = L.get('r', 0) * (1.15 if L.get('k') not in ('mound', 'pool') else 1.0); h = L.get('h', L.get('s', 1.5)) * (GS if L.get('k') not in ('pool',) else 1.0)
        bm = bmesh.new(); disp = L.get('disp', 0.0); ds = 0.4
        def base_y(x, z): return (floor + surf(bases, x, z)) if False else (surf(bases, x, z) if L.get('lvl') != 'floor' and surf(bases, x, z) else floor)
        def spot(i):
            if n == 1 and not r: return cx, cz
            a = rr.random() * 6.2832; d = (rr.random() ** 0.5) * r
            return cx + d * math.cos(a), cz + d * math.sin(a)
        if k == 'mound':
            top = floor + h; rx = L.get('r', 4); blob(bm, (cx, floor + h * 0.15, cz), (rx, h * 0.9, rx * L.get('asp', 1.0)), (0, 0, 0), (28, 14)); disp = disp or 0.5
            bases.append((cx, cz, rx, top, floor))
        elif k == 'pool':
            rx = L.get('r', 4); y = (L.get('y') or floor)
            blob(bm, (cx, y + 0.1, cz), (rx, L.get('h', 0.35), rx * L.get('asp', 1.0)), (0, rr.random() * 90, 0), (32, 8)); disp = disp or 0.2
            bases.append((cx, cz, rx, y + 0.5, y))
        elif k in ('chunk', 'cyl', 'slice', 'fillet', 'ball', 'wedge'):
            for i in range(n):
                x, z = spot(i); y0 = base_y(x, z); yaw = rr.random() * 180
                if k == 'chunk': blob(bm, (x, y0 + s * 0.45, z), (s * 0.55, s * 0.45, s * 0.5), (rr.random() * 12, yaw, rr.random() * 12), (12, 8))
                elif k == 'ball': blob(bm, (x, y0 + s * 0.5, z), (s * 0.5, s * 0.5, s * 0.5), (0, 0, 0), (16, 10))
                elif k == 'slice': blob(bm, (x, y0 + h * 0.35 + i * 0.0, z), (s * 0.55, h * 0.3, s * 0.55 * L.get('asp', 1.0)), (rr.random() * 8, yaw, rr.random() * 8), (20, 8))
                elif k == 'fillet': blob(bm, (x, y0 + h * 0.5, z), (s * 0.9, h * 0.5, s * 0.45), (0, yaw if n > 1 else L.get('yaw', 20), 0), (22, 10))
                elif k == 'wedge': blob(bm, (x, y0 + h * 0.4, z), (s * 0.7, h * 0.4, s * 0.45), (0, yaw, 0), (3, 3))
                elif k == 'cyl': tube(bm, [(x - s * 0.8, y0 + h * 0.5, z), (x, y0 + h * 0.55, z), (x + s * 0.8, y0 + h * 0.5, z)], [h * 0.35, h * 0.5, h * 0.35], 12) if False else blob(bm, (x, y0 + h * 0.5, z), (s * 1.0, h * 0.5, h * 0.5), (0, L.get('yaw', yaw), 0), (20, 10))
            disp = disp or 0.15
        elif k in ('egg',):
            x, z = spot(0); y0 = base_y(x, z)
            blob(bm, (x, y0 + 0.2, z), (s * 1.3, 0.3, s * 1.15), (0, 0, 0), (28, 6)); eg = new_obj('egg', bm, mat, True, disp=0.1); bm = bmesh.new()
            blob(bm, (x, y0 + 0.5, z), (s * 0.55, s * 0.4, s * 0.55), (0, 0, 0), (16, 10)); new_obj('yolk', bm, mk_material('yolk'), True); bm = bmesh.new(); disp = 0
        elif k == 'shrimp':
            for i in range(n):
                x, z = spot(i); y0 = base_y(x, z); a = rr.random() * 6.28
                pts = [(x + math.cos(a + q * 0.55) * s * 0.9 - math.cos(a) * 0, y0 + 0.5 + math.sin(q * 0.5) * s * 0.35, z + math.sin(a + q * 0.55) * s * 0.9) for q in range(6)]
                tube(bm, pts, [s * 0.28, s * 0.36, s * 0.38, s * 0.34, s * 0.26, s * 0.12], 8)
            disp = 0.05
        elif k == 'leaf':
            for i in range(n):
                x, z = spot(i); y0 = base_y(x, z)
                blob(bm, (x, y0 + 0.4 + rr.random() * 0.4, z), (s * 0.9, 0.18, s * 0.55), (rr.random() * 20, rr.random() * 180, rr.random() * 20), (12, 6))
            disp = disp or 0.3
        elif k == 'ring':
            for i in range(n):
                x, z = spot(i); y0 = base_y(x, z)
                res = bmesh.ops.create_circle(bm, segments=1)  # placeholder to keep API symmetric
                for vv in res['verts']: bm.verts.remove(vv)
                pts = [(x + math.cos(q * 0.5236) * s, y0 + s * 0.3, z + math.sin(q * 0.5236) * s) for q in range(13)]
                tube(bm, pts, s * 0.28, 8)
        elif k == 'noodles':
            for i in range(n):
                x, z = spot(i); y0 = base_y(x, z); a = rr.random() * 6.28; pts = []
                for q in range(9):
                    pts.append((x + math.cos(a + q * 0.1) * (r or 3) * (q - 4) / 4.0 + rr.uniform(-0.5, 0.5), y0 + 0.3 + abs(math.sin(q * 0.9 + i)) * s, z + math.sin(a) * (r or 3) * (q - 4) / 4.0 + rr.uniform(-0.5, 0.5)))
                tube(bm, pts, s * 0.14, 5)
        elif k in ('scatter', 'grains'):
            for i in range(n):
                x, z = spot(i); y0 = base_y(x, z)
                if k == 'grains': blob(bm, (x, y0 + s * 0.2, z), (s * 0.55, s * 0.22, s * 0.25), (rr.random() * 30, rr.random() * 180, rr.random() * 30), (6, 4))
                else: blob(bm, (x, y0 + s * 0.3, z), (s * 0.4, s * 0.3, s * 0.4), (rr.random() * 30, rr.random() * 180, 0), (6, 4))
            disp = 0
        if len(bm.verts): new_obj(k, bm, mat, True, disp=disp, dscale=ds)
        else: bm.free()

def p_scene(part, mat, R):
    build_scene(part['scene'], R)
    if 'dishkey' not in bpy.data.objects:  # softbox overhead + rim
        bpy.ops.object.light_add(type='AREA'); k = bpy.context.object; k.name = 'dishkey'; k.data.energy = 70; k.data.size = 1.6
        k.location = (0.5, -0.3, 2.2); k.rotation_euler = (0, 0, 0); k.data.color = (1.0, 0.96, 0.9)
        bpy.ops.object.light_add(type='AREA'); r = bpy.context.object; r.name = 'dishrim'; r.data.energy = 60; r.data.size = 1.0
        r.location = (-1.2, 1.2, 1.2); r.rotation_euler = (math.radians(-60), 0, math.radians(135)); r.data.color = (1.0, 0.98, 0.95)
    return None

kit.MATERIALS['dishdummy'] = kit.MATERIALS['flat']
kit.PARTS.update(parts_magic.PARTS)
kit.PARTS['scene'] = p_scene
kit.main()
