#!/usr/bin/env python3
# S6875 diaithir-animation body layer generator: player body and item-use clips (PAL JSON), item tags and body_clips.json from the coverage csv.
"""Generates the vanilla-body pose layer for diaithir-animation (clean-room replacement for Not Enough Animations / firstperson poses).

Usage: gen_body.py [coverage.csv]   (default /mnt/project-files/plans/ANIMATIONS_COVERAGE.csv)
Writes assets/diaithiranimation/player_animations/body.json, data/diaithiranimation/tags/item/anim/body/<kind>.json, body_clips.json.
Angles are degrees, vanilla ModelPart convention (arm xRot -90 = straight forward). Bones: right_arm left_arm torso head right_leg left_leg.
Clip names: use.<kind>.<phase> for held-item actions, act.<name> for body states and one-shots.
"""
import csv, json, os, re, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "main")
ASSET = os.path.join(ROOT, "resources", "assets", "diaithiranimation", "player_animations")
TAGS = os.path.join(ROOT, "resources", "data", "diaithiranimation", "tags", "item", "anim", "body")
CSV = sys.argv[1] if len(sys.argv) > 1 else "/mnt/project-files/plans/ANIMATIONS_COVERAGE.csv"
R = [0, 0, 0]

def A(x=0, y=0, z=0):
    return [x, y, z]

def clip(length, bones, loop=False):
    out = {"animation_length": length, "bones": {}}
    if loop:
        out["loop"] = True
    for b, frames in bones.items():
        out["bones"][b] = {"rotation": {f"{t:.2f}": {"vector": v, "easing": "easeInOutSine"} for t, v in frames}}
    return out

def hold(length, **pose):
    """A pose held for `length`, as a loop (a pose per bone)."""
    return clip(length, {b: [(0, v), (length, v)] for b, v in pose.items()}, loop=True)

def sway(length, bone, a, b, others=None):
    """Loop that moves one bone between two poses; others are held."""
    bones = {bone: [(0, a), (length / 2, b), (length, a)]}
    for o, v in (others or {}).items():
        bones[o] = [(0, v), (length, v)]
    return clip(length, bones, loop=True)

def alt(length, r_a, r_b, l_a, l_b, extra=None):
    """Two-arm alternating loop (climb, swim, crawl)."""
    bones = {"right_arm": [(0, r_a), (length / 2, r_b), (length, r_a)], "left_arm": [(0, l_a), (length / 2, l_b), (length, l_a)]}
    bones.update(extra or {})
    return clip(length, bones, loop=True)

C = {}   # name -> clip
KINDS = {}   # kind -> clip names (body_clips.json)

# ----------------------------------------------------------------------------- held-item actions (use.<kind>.<phase>)
# throwable: wind up over the shoulder, throw through
C["use.throwable.windup"] = clip(0.3, {"right_arm": [(0, R), (0.2, A(-150, 0, 25)), (0.3, A(-160, 0, 25))], "torso": [(0, R), (0.3, A(0, 14, 0))], "left_arm": [(0, R), (0.3, A(-30, 10, 0))]})
C["use.throwable.throw"] = clip(0.35, {"right_arm": [(0, A(-160, 0, 25)), (0.12, A(-60, -10, 0)), (0.2, A(-50, -10, 0)), (0.35, R)], "torso": [(0, A(0, 14, 0)), (0.12, A(0, -16, 0)), (0.35, R)], "head": [(0, R), (0.12, A(8, -6, 0)), (0.35, R)]})
# food: hand to mouth, head tilts, chewing bob
C["use.food.eat"] = clip(0.5, {"right_arm": [(0, A(-100, -25, 10)), (0.25, A(-112, -28, 10)), (0.5, A(-100, -25, 10))], "head": [(0, A(8, 0, 0)), (0.12, A(14, 0, 0)), (0.25, A(8, 0, 0)), (0.37, A(14, 0, 0)), (0.5, A(8, 0, 0))], "left_arm": [(0, A(-10, 10, 0)), (0.5, A(-10, 10, 0))]}, loop=True)
C["use.drink.tilt"] = clip(0.3, {"right_arm": [(0, R), (0.3, A(-115, -30, 12))], "head": [(0, R), (0.3, A(-12, 0, 0))]})
C["use.drink.sip"] = clip(0.8, {"right_arm": [(0, A(-115, -30, 12)), (0.8, A(-122, -30, 12))], "head": [(0, A(-12, 0, 0)), (0.4, A(-22, 0, 0)), (0.8, A(-12, 0, 0))]}, loop=True)
# horn / instrument: both hands to mouth, head back
C["use.horn.play"] = clip(1.0, {"right_arm": [(0, A(-120, -35, 5)), (1.0, A(-120, -35, 5))], "left_arm": [(0, A(-110, 30, -5)), (1.0, A(-110, 30, -5))], "head": [(0, A(-10, 0, 0)), (0.5, A(-18, 0, 0)), (1.0, A(-10, 0, 0))], "torso": [(0, A(-4, 0, 0)), (1.0, A(-4, 0, 0))]}, loop=True)
# spyglass / map: hand to eye, other steadies; map held in both hands
C["use.spyglass.raise"] = clip(0.25, {"right_arm": [(0, R), (0.25, A(-125, -32, 8))], "left_arm": [(0, R), (0.25, A(-70, 40, 0))], "head": [(0, R), (0.25, A(3, 0, 0))]})
C["use.spyglass.read"] = hold(1.0, right_arm=A(-125, -32, 8), left_arm=A(-70, 40, 0), head=A(3, 0, 0))
C["use.map.raise"] = clip(0.3, {"right_arm": [(0, R), (0.3, A(-55, -20, 0))], "left_arm": [(0, R), (0.3, A(-55, 20, 0))], "head": [(0, R), (0.3, A(18, 0, 0))]})
C["use.map.read"] = sway(2.0, "head", A(18, -6, 0), A(18, 6, 0), {"right_arm": A(-55, -20, 0), "left_arm": A(-55, 20, 0)})
# wrench / tool: forward apply, a small twist
C["use.tool.use"] = clip(0.5, {"right_arm": [(0, R), (0.15, A(-70, -15, 0)), (0.3, A(-76, -15, 10)), (0.4, A(-70, -15, -10)), (0.5, R)], "torso": [(0, R), (0.15, A(0, -6, 0)), (0.5, R)], "head": [(0, R), (0.15, A(10, 0, 0)), (0.5, R)]})
# mount gear: saddle/horse armour onto a mount, then swing up
C["use.mount.equip"] = clip(0.6, {"right_arm": [(0, R), (0.2, A(-50, -20, 0)), (0.4, A(-40, -20, 0)), (0.6, R)], "left_arm": [(0, R), (0.2, A(-50, 20, 0)), (0.4, A(-40, 20, 0)), (0.6, R)], "torso": [(0, R), (0.25, A(18, 0, 0)), (0.6, R)]})
C["use.mount.mount"] = clip(0.5, {"right_leg": [(0, R), (0.2, A(-70, 0, 20)), (0.5, A(-30, 0, 10))], "left_leg": [(0, R), (0.5, A(-30, 0, -10))], "torso": [(0, R), (0.2, A(-10, 0, 0)), (0.5, R)], "right_arm": [(0, R), (0.2, A(-60, -10, 0)), (0.5, A(-40, -10, 0))]})
# wings: deploy out, glide (held spread), flap, fold
C["use.wings.deploy"] = clip(0.5, {"right_arm": [(0, R), (0.5, A(0, 0, 80))], "left_arm": [(0, R), (0.5, A(0, 0, -80))], "head": [(0, R), (0.25, A(-8, 0, 0)), (0.5, R)]})
C["use.wings.glide"] = hold(1.0, right_arm=A(-20, 0, 70), left_arm=A(-20, 0, -70), torso=A(70, 0, 0), head=A(-60, 0, 0))
C["use.wings.flap"] = clip(0.6, {"right_arm": [(0, A(-20, 0, 70)), (0.3, A(-20, 0, 45)), (0.6, A(-20, 0, 70))], "left_arm": [(0, A(-20, 0, -70)), (0.3, A(-20, 0, -45)), (0.6, A(-20, 0, -70))]})
C["use.wings.fold"] = clip(0.5, {"right_arm": [(0, A(0, 0, 80)), (0.5, R)], "left_arm": [(0, A(0, 0, -80)), (0.5, R)]})
# spell / scroll: open the scroll, read, cast with a push
C["use.scroll.open"] = clip(0.5, {"right_arm": [(0, R), (0.25, A(-60, -15, 0)), (0.5, A(-55, -15, 0))], "left_arm": [(0, R), (0.25, A(-60, 15, 0)), (0.5, A(-55, 15, 0))], "head": [(0, R), (0.5, A(20, 0, 0))]})
C["use.scroll.read"] = sway(2.0, "head", A(22, -4, 0), A(22, 4, 0), {"right_arm": A(-55, -15, 0), "left_arm": A(-55, 15, 0)})
C["use.scroll.cast"] = clip(0.7, {"right_arm": [(0, A(-55, -15, 0)), (0.3, A(-130, 0, 20)), (0.45, A(-80, 0, 0)), (0.7, R)], "left_arm": [(0, A(-55, 15, 0)), (0.3, A(-100, 0, -20)), (0.7, R)], "torso": [(0, R), (0.3, A(-6, 0, 0)), (0.45, A(8, 0, 0)), (0.7, R)]})
# fishing rod: cast over the shoulder, wait, reel
C["use.rod.cast"] = clip(0.6, {"right_arm": [(0, R), (0.2, A(-140, -5, 10)), (0.35, A(-60, -5, 0)), (0.6, A(-55, -5, 0))], "torso": [(0, R), (0.2, A(0, 10, 0)), (0.35, A(0, -8, 0)), (0.6, R)]})
C["use.rod.wait"] = hold(1.0, right_arm=A(-55, -5, 0), left_arm=A(-20, 10, 0), head=A(8, 0, 0))
C["use.rod.reel"] = clip(0.5, {"right_arm": [(0, A(-65, -5, 0)), (0.25, A(-80, -5, 0)), (0.5, A(-65, -5, 0))], "left_arm": [(0, A(-40, 20, 0)), (0.25, A(-60, 20, 0)), (0.5, A(-40, 20, 0))], "torso": [(0, R), (0.25, A(4, 0, 0)), (0.5, R)]}, loop=True)

# ----------------------------------------------------------------------------- body states (loops) and one-shots (act.<name>)
# movement states: vanilla already moves the limbs for walk/run/sneak; these loops layer a pose on top of it
C["act.crawl"] = alt(0.8, A(-170, 0, 10), A(-130, 0, 20), A(-130, 0, -20), A(-170, 0, -10), {"torso": [(0, A(-8, 0, 0)), (0.8, A(-8, 0, 0))]})
C["act.swim"] = alt(1.0, A(-170, 0, 15), A(20, 0, 30), A(20, 0, -30), A(-170, 0, -15))
C["act.swim_sprint"] = alt(0.6, A(-175, 0, 10), A(30, 0, 25), A(30, 0, -25), A(-175, 0, -10), {"head": [(0, A(-10, 0, 0)), (0.6, A(-10, 0, 0))]})
C["act.tread"] = alt(1.2, A(-20, 0, 55), A(-20, 0, 35), A(-20, 0, -35), A(-20, 0, -55), {"right_leg": [(0, A(-25, 0, 0)), (0.6, A(20, 0, 0)), (1.2, A(-25, 0, 0))], "left_leg": [(0, A(20, 0, 0)), (0.6, A(-25, 0, 0)), (1.2, A(20, 0, 0))]})
C["act.dive"] = clip(0.8, {"right_arm": [(0, R), (0.4, A(-180, 0, 0))], "left_arm": [(0, R), (0.4, A(-180, 0, 0))], "torso": [(0, R), (0.4, A(30, 0, 0))], "head": [(0, R), (0.4, A(-20, 0, 0))]})
C["act.wade"] = alt(0.9, A(-15, 0, 10), A(15, 0, 10), A(15, 0, -10), A(-15, 0, -10), {"torso": [(0, A(4, 0, 0)), (0.9, A(4, 0, 0))]})
for nm, (r_a, r_b) in {"climb": (A(-170, 0, 12), A(-120, 0, 12)), "ladder": (A(-165, 0, 8), A(-115, 0, 8)), "vine": (A(-160, 0, 20), A(-110, 0, 20)), "scaffold": (A(-150, 0, 6), A(-100, 0, 6))}.items():
    C[f"act.{nm}"] = alt(0.7, r_a, r_b, r_b, r_a, {"right_leg": [(0, A(-15, 0, 0)), (0.35, A(-60, 0, 0)), (0.7, A(-15, 0, 0))], "left_leg": [(0, A(-60, 0, 0)), (0.35, A(-15, 0, 0)), (0.7, A(-60, 0, 0))]})
C["act.glide"] = C["use.wings.glide"]
C["act.fall"] = clip(0.6, {"right_arm": [(0, A(-10, 0, 70)), (0.3, A(-10, 0, 85)), (0.6, A(-10, 0, 70))], "left_arm": [(0, A(-10, 0, -70)), (0.3, A(-10, 0, -85)), (0.6, A(-10, 0, -70))], "right_leg": [(0, A(-8, 0, 6)), (0.6, A(-8, 0, 6))], "left_leg": [(0, A(8, 0, -6)), (0.6, A(8, 0, -6))]}, loop=True)
C["act.jump"] = clip(0.4, {"right_arm": [(0, R), (0.2, A(-110, 0, 40)), (0.4, A(-60, 0, 30))], "left_arm": [(0, R), (0.2, A(-110, 0, -40)), (0.4, A(-60, 0, -30))], "right_leg": [(0, R), (0.25, A(-45, 0, 0)), (0.4, A(-20, 0, 0))], "left_leg": [(0, R), (0.25, A(15, 0, 0)), (0.4, A(10, 0, 0))]})
C["act.land_soft"] = clip(0.3, {"right_leg": [(0, R), (0.1, A(-35, 0, 0)), (0.3, R)], "left_leg": [(0, R), (0.1, A(-35, 0, 0)), (0.3, R)], "torso": [(0, R), (0.1, A(14, 0, 0)), (0.3, R)], "right_arm": [(0, R), (0.1, A(-20, 0, 35)), (0.3, R)], "left_arm": [(0, R), (0.1, A(-20, 0, -35)), (0.3, R)]})
C["act.land_hard"] = clip(0.9, {"right_leg": [(0, R), (0.12, A(-70, 0, 0)), (0.5, A(-60, 0, 0)), (0.9, R)], "left_leg": [(0, R), (0.12, A(-70, 0, 0)), (0.5, A(-60, 0, 0)), (0.9, R)], "torso": [(0, R), (0.12, A(35, 0, 0)), (0.5, A(30, 0, 0)), (0.9, R)], "head": [(0, R), (0.12, A(15, 0, 0)), (0.9, R)], "right_arm": [(0, R), (0.12, A(-50, 0, 30)), (0.5, A(-40, 0, 30)), (0.9, R)], "left_arm": [(0, R), (0.12, A(-50, 0, -30)), (0.5, A(-40, 0, -30)), (0.9, R)]})
# riding: legs astride, hands to reins/wheel
C["act.ride_horse"] = hold(1.0, right_leg=A(-80, 0, 18), left_leg=A(-80, 0, -18), right_arm=A(-45, -10, 0), left_arm=A(-45, 10, 0), torso=A(2, 0, 0))
C["act.ride_boat"] = hold(1.0, right_leg=A(-80, 10, 0), left_leg=A(-80, -10, 0), right_arm=A(-40, -10, 0), left_arm=A(-40, 10, 0))
C["act.ride_cart"] = hold(1.0, right_leg=A(-80, 0, 0), left_leg=A(-80, 0, 0), right_arm=A(-30, -10, 0), left_arm=A(-30, 10, 0), head=A(4, 0, 0))
C["act.ride_mount"] = hold(1.0, right_leg=A(-75, 0, 22), left_leg=A(-75, 0, -22), right_arm=A(-50, -12, 0), left_arm=A(-50, 12, 0), torso=A(4, 0, 0))
C["act.sit"] = hold(1.0, right_leg=A(-85, 8, 0), left_leg=A(-85, -8, 0), right_arm=A(-20, -10, 0), left_arm=A(-20, 10, 0))
C["act.sit_seat"] = hold(1.0, right_leg=A(-88, 5, 0), left_leg=A(-88, -5, 0), right_arm=A(-35, -12, 0), left_arm=A(-35, 12, 0), head=A(4, 0, 0))
C["act.sleep"] = sway(4.0, "torso", A(0, 0, 0), A(1.5, 0, 0), {"head": A(0, 0, 0)})
C["act.stand_up"] = clip(0.6, {"torso": [(0, A(40, 0, 0)), (0.4, A(10, 0, 0)), (0.6, R)], "right_arm": [(0, A(-70, 0, 20)), (0.6, R)], "left_arm": [(0, A(-70, 0, -20)), (0.6, R)], "right_leg": [(0, A(-60, 0, 0)), (0.6, R)], "left_leg": [(0, A(-60, 0, 0)), (0.6, R)]})
C["act.hurt"] = clip(0.4, {"torso": [(0, R), (0.08, A(-14, 0, 0)), (0.4, R)], "head": [(0, R), (0.08, A(-18, 0, 6)), (0.4, R)], "right_arm": [(0, R), (0.08, A(-20, 0, 25)), (0.4, R)], "left_arm": [(0, R), (0.08, A(-20, 0, -25)), (0.4, R)]})
C["act.die"] = clip(1.2, {"torso": [(0, R), (0.5, A(-30, 0, 0)), (1.2, A(-85, 0, 0))], "head": [(0, R), (0.6, A(-25, 0, 10))], "right_arm": [(0, R), (0.5, A(-30, 0, 50)), (1.2, A(-10, 0, 70))], "left_arm": [(0, R), (0.5, A(-30, 0, -50)), (1.2, A(-10, 0, -70))], "right_leg": [(0, R), (1.2, A(-10, 0, 10))], "left_leg": [(0, R), (1.2, A(-10, 0, -10))]})
C["act.respawn"] = clip(0.9, {"torso": [(0, A(40, 0, 0)), (0.6, A(10, 0, 0)), (0.9, R)], "head": [(0, A(30, 0, 0)), (0.9, R)], "right_arm": [(0, A(-50, 0, 30)), (0.9, R)], "left_arm": [(0, A(-50, 0, -30)), (0.9, R)]})
# interaction one-shots
C["act.interact"] = clip(0.4, {"right_arm": [(0, R), (0.15, A(-80, -15, 0)), (0.25, A(-90, -15, 0)), (0.4, R)], "torso": [(0, R), (0.15, A(0, -6, 0)), (0.4, R)]})
C["act.crouch_interact"] = clip(0.5, {"right_arm": [(0, R), (0.2, A(-70, -10, 0)), (0.5, R)], "torso": [(0, A(20, 0, 0)), (0.5, A(20, 0, 0))], "head": [(0, A(10, 0, 0)), (0.5, A(10, 0, 0))]})
C["act.open_container"] = clip(0.6, {"right_arm": [(0, R), (0.2, A(-85, -15, 0)), (0.3, A(-55, -15, 0)), (0.6, A(-30, -10, 0))], "left_arm": [(0, R), (0.25, A(-60, 15, 0)), (0.6, A(-30, 10, 0))], "head": [(0, R), (0.3, A(14, 0, 0)), (0.6, A(14, 0, 0))]})
C["act.close_container"] = clip(0.4, {"right_arm": [(0, A(-30, -10, 0)), (0.15, A(-80, -10, 0)), (0.4, R)], "left_arm": [(0, A(-30, 10, 0)), (0.4, R)], "head": [(0, A(14, 0, 0)), (0.4, R)]})
C["act.brew"] = clip(1.2, {"right_arm": [(0, R), (0.25, A(-80, -20, 0)), (0.5, A(-100, -25, 5)), (0.9, A(-80, -20, 0)), (1.2, R)], "left_arm": [(0, R), (0.25, A(-60, 20, 0)), (1.2, R)], "head": [(0, R), (0.3, A(18, 0, 0)), (1.2, R)]})
C["act.craft"] = clip(0.8, {"right_arm": [(0, R), (0.2, A(-65, -15, 0)), (0.4, A(-55, -15, 0)), (0.6, A(-65, -15, 0)), (0.8, R)], "left_arm": [(0, R), (0.2, A(-65, 15, 0)), (0.8, R)], "head": [(0, R), (0.2, A(16, 0, 0)), (0.8, R)]})
C["act.enchant"] = clip(1.5, {"right_arm": [(0, R), (0.4, A(-120, -10, 20)), (1.2, A(-120, -10, 20)), (1.5, R)], "left_arm": [(0, R), (0.4, A(-120, 10, -20)), (1.2, A(-120, 10, -20)), (1.5, R)], "head": [(0, R), (0.4, A(-14, 0, 0)), (1.5, R)]})
C["act.trade"] = clip(1.0, {"right_arm": [(0, R), (0.25, A(-70, -20, 0)), (0.5, A(-50, -20, 0)), (0.75, A(-70, -20, 0)), (1.0, R)], "head": [(0, R), (0.25, A(0, 6, 0)), (0.75, A(8, 0, 0)), (1.0, R)]})
C["act.mine"] = clip(0.5, {"right_arm": [(0, R), (0.18, A(-140, -10, 5)), (0.32, A(-30, -10, 0)), (0.5, R)], "torso": [(0, R), (0.18, A(-4, 0, 0)), (0.32, A(8, 0, 0)), (0.5, R)]})
C["act.place"] = clip(0.35, {"right_arm": [(0, R), (0.12, A(-75, -15, 0)), (0.2, A(-90, -15, 0)), (0.35, R)], "head": [(0, R), (0.12, A(8, 0, 0)), (0.35, R)]})
C["act.block"] = clip(0.3, {"right_arm": [(0, R), (0.15, A(-80, -40, 10)), (0.3, A(-80, -40, 10))], "left_arm": [(0, R), (0.15, A(-30, 20, 0)), (0.3, A(-30, 20, 0))]})
C["act.equip_armor"] = clip(0.9, {"right_arm": [(0, R), (0.3, A(-150, -20, 30)), (0.6, A(-110, -20, 20)), (0.9, R)], "left_arm": [(0, R), (0.3, A(-60, 20, 0)), (0.9, R)], "head": [(0, R), (0.3, A(10, 0, 0)), (0.9, R)]})
C["act.swap_hotbar"] = clip(0.3, {"right_arm": [(0, R), (0.12, A(-35, -10, 5)), (0.3, R)], "head": [(0, R), (0.12, A(6, 0, 0)), (0.3, R)]})
C["act.drop_item"] = clip(0.4, {"right_arm": [(0, R), (0.12, A(-30, -10, 0)), (0.22, A(-70, -10, 0)), (0.4, R)], "torso": [(0, R), (0.12, A(6, 0, 0)), (0.4, R)]})
C["act.pick_up"] = clip(0.5, {"torso": [(0, R), (0.2, A(30, 0, 0)), (0.5, R)], "right_arm": [(0, R), (0.2, A(-40, -10, 0)), (0.5, R)], "head": [(0, R), (0.2, A(14, 0, 0)), (0.5, R)]})
C["act.throw"] = C["use.throwable.throw"]
C["act.push"] = hold(1.0, right_arm=A(-85, -10, 0), left_arm=A(-85, 10, 0), torso=A(16, 0, 0))
C["act.pull"] = hold(1.0, right_arm=A(-75, -10, 0), left_arm=A(-75, 10, 0), torso=A(-12, 0, 0))
C["act.carry"] = hold(1.0, right_arm=A(-70, -25, 0), left_arm=A(-70, 25, 0), torso=A(-3, 0, 0))
C["act.punch"] = clip(0.3, {"right_arm": [(0, R), (0.1, A(-100, -5, 0)), (0.18, A(-95, -5, 0)), (0.3, R)], "torso": [(0, R), (0.1, A(0, -14, 0)), (0.3, R)], "left_arm": [(0, R), (0.1, A(-30, 15, 0)), (0.3, R)]})
C["act.hold_torch"] = hold(1.0, right_arm=A(-45, -12, 0))
C["act.hold_map"] = hold(1.0, right_arm=A(-55, -20, 0), left_arm=A(-55, 20, 0), head=A(14, 0, 0))
C["act.hold_spyglass"] = hold(1.0, right_arm=A(-125, -32, 8), left_arm=A(-70, 40, 0))
# emote wheel basics (Emotecraft clips are merged separately)
C["act.wave"] = clip(1.2, {"right_arm": [(0, R), (0.25, A(0, 0, 150)), (0.45, A(0, 0, 135)), (0.65, A(0, 0, 155)), (0.85, A(0, 0, 135)), (1.2, R)], "head": [(0, R), (0.25, A(0, -10, 0)), (1.2, R)]})
C["act.point"] = clip(1.0, {"right_arm": [(0, R), (0.25, A(-90, -8, 0)), (0.8, A(-90, -8, 0)), (1.0, R)], "head": [(0, R), (0.25, A(0, -8, 0)), (1.0, R)]})
C["act.nod"] = clip(0.8, {"head": [(0, R), (0.15, A(20, 0, 0)), (0.3, R), (0.45, A(20, 0, 0)), (0.6, R)]})
C["act.shake_head"] = clip(0.8, {"head": [(0, R), (0.15, A(0, 35, 0)), (0.35, A(0, -35, 0)), (0.55, A(0, 35, 0)), (0.8, R)]})
C["act.dance"] = clip(1.6, {"right_arm": [(0, A(0, 0, 150)), (0.4, A(-120, 0, 60)), (0.8, A(0, 0, 150)), (1.2, A(-120, 0, 60)), (1.6, A(0, 0, 150))], "left_arm": [(0, A(-120, 0, -60)), (0.4, A(0, 0, -150)), (0.8, A(-120, 0, -60)), (1.2, A(0, 0, -150)), (1.6, A(-120, 0, -60))], "torso": [(0, A(0, 0, 8)), (0.8, A(0, 0, -8)), (1.6, A(0, 0, 8))], "right_leg": [(0, A(-30, 0, 0)), (0.4, R), (0.8, A(-30, 0, 0)), (1.2, R), (1.6, A(-30, 0, 0))], "left_leg": [(0, R), (0.4, A(-30, 0, 0)), (0.8, R), (1.2, A(-30, 0, 0)), (1.6, R)]}, loop=True)
C["act.cheer"] = clip(1.2, {"right_arm": [(0, R), (0.2, A(-175, 0, 20)), (0.5, A(-165, 0, 25)), (0.8, A(-175, 0, 20)), (1.2, R)], "left_arm": [(0, R), (0.2, A(-175, 0, -20)), (0.5, A(-165, 0, -25)), (0.8, A(-175, 0, -20)), (1.2, R)], "head": [(0, R), (0.2, A(-12, 0, 0)), (1.2, R)]})
C["act.bow"] = clip(1.4, {"torso": [(0, R), (0.5, A(45, 0, 0)), (0.9, A(45, 0, 0)), (1.4, R)], "head": [(0, R), (0.5, A(20, 0, 0)), (1.4, R)], "right_arm": [(0, R), (0.5, A(-30, -10, 0)), (1.4, R)], "left_arm": [(0, R), (0.5, A(-30, 10, 0)), (1.4, R)]})
C["act.salute"] = clip(1.2, {"right_arm": [(0, R), (0.25, A(-130, -50, 30)), (0.9, A(-130, -50, 30)), (1.2, R)], "head": [(0, R), (0.25, A(-4, 0, 0)), (1.2, R)]})
C["act.pray"] = clip(2.0, {"right_arm": [(0, R), (0.4, A(-70, -30, 0)), (1.6, A(-70, -30, 0)), (2.0, R)], "left_arm": [(0, R), (0.4, A(-70, 30, 0)), (1.6, A(-70, 30, 0)), (2.0, R)], "head": [(0, R), (0.4, A(24, 0, 0)), (1.6, A(24, 0, 0)), (2.0, R)]})
C["act.laugh"] = clip(1.2, {"torso": [(0, R), (0.1, A(-8, 0, 0)), (0.2, A(2, 0, 0)), (0.3, A(-8, 0, 0)), (0.4, A(2, 0, 0)), (0.5, A(-8, 0, 0)), (1.2, R)], "head": [(0, R), (0.1, A(-18, 0, 0)), (0.5, A(-18, 0, 0)), (1.2, R)], "left_arm": [(0, R), (0.2, A(-50, 20, 0)), (1.0, A(-50, 20, 0)), (1.2, R)]})

# ----------------------------------------------------------------------------- how the client picks the clip for each held-item kind
# coverage csv "kind" -> body kind; phases are the clip suffixes the mod plays in order while the use state runs
ITEM_KINDS = {
    "throwable": ["windup", "throw"], "food": ["eat"], "drink": ["tilt", "sip"], "horn": ["play"], "spyglass": ["raise", "read"], "map": ["raise", "read"],
    "tool": ["use"], "mount": ["equip", "mount"], "wings": ["deploy", "glide", "flap", "fold"], "scroll": ["open", "read", "cast"], "rod": ["cast", "wait", "reel"],
}
CSV_KIND = {"throwable": "throwable", "food": "food", "horn/instrument": "horn", "spyglass/map": "spyglass", "wrench/tool": "tool", "mount gear": "mount",
            "elytra/wings": "wings", "spell/scroll": "scroll", "fishing rod": "rod", "drink/potion": "drink"}
# coverage "action" rows (player category) -> clip
ACTION_CLIP = {"walk": None, "run": None, "sprint": None, "sneak": None, "sneak-walk": None, "crawl": "crawl", "swim": "swim", "swim-sprint": "swim_sprint", "tread water": "tread",
               "climb": "climb", "ladder": "ladder", "vine": "vine", "scaffold": "scaffold", "glide (elytra)": "glide", "fall": "fall", "land (soft/hard)": "land_soft",
               "jump": "jump", "ride horse": "ride_horse", "ride boat": "ride_boat", "ride cart": "ride_cart", "ride mount": "ride_mount", "sit": "sit", "sleep": "sleep",
               "stand up": "stand_up", "use item": "interact", "eat": None, "drink": None, "block": "block", "mine": "mine", "place block": "place", "interact": "interact",
               "open container": "open_container", "close container": "close_container", "fish": None, "brew": "brew", "craft": "craft", "enchant": "enchant", "trade": "trade",
               "sit at seat": "sit_seat", "get hurt": "hurt", "die": "die", "respawn": "respawn", "emote wheel": "wave", "equip armor": "equip_armor", "swap hotbar": "swap_hotbar",
               "drop item": "drop_item", "pick up item": "pick_up", "throw": "throw", "push/pull": "push", "carry": "carry", "dive": "dive", "wade": "wade",
               "punch (empty hand)": "punch", "hold torch": "hold_torch", "hold map": "hold_map", "hold spyglass": "hold_spyglass", "wave": "wave", "point": "point", "nod": "nod",
               "shake head": "shake_head", "dance": "dance", "cheer": "cheer", "bow": "bow", "salute": "salute", "pray": "pray", "laugh": "laugh", "crouch interact": "crouch_interact"}
# rows whose clip is a held-item kind rather than an act.* one
ACTION_ITEMKIND = {"eat": "food", "drink": "drink", "fish": "rod"}
# walk/run/sprint/sneak rows: vanilla limb swing plus the body layer's lean (act.lean_*) -- covered by the leans below
for nm, (tx, hx) in {"walk": (2, 0), "run": (6, -2), "sprint": (12, -4), "sneak": (28, 12), "sneak_walk": (26, 10)}.items():
    C[f"act.lean_{nm}"] = hold(1.0, torso=A(tx, 0, 0), head=A(hx, 0, 0))
for a, c in {"walk": "lean_walk", "run": "lean_run", "sprint": "lean_sprint", "sneak": "lean_sneak", "sneak-walk": "lean_sneak_walk"}.items():
    ACTION_CLIP[a] = c


def main():
    os.makedirs(ASSET, exist_ok=True); os.makedirs(TAGS, exist_ok=True)
    json.dump({"format_version": "1.8.0", "animations": C}, open(os.path.join(ASSET, "body.json"), "w"), indent=1)
    meta = {"clips": sorted(C), "item_kinds": ITEM_KINDS, "actions": {k: v for k, v in ACTION_CLIP.items() if v}, "action_itemkind": ACTION_ITEMKIND}
    json.dump(meta, open(os.path.join(ROOT, "resources", "body_clips.json"), "w"), indent=1)
    tags = {k: set() for k in ITEM_KINDS}
    for r in csv.DictReader(open(CSV)):
        if not r["owner"].startswith("1") or r["category"] != "item-use":
            continue
        m = re.match(r"item \((.+)\)", r["kind"])
        k = CSV_KIND.get(m.group(1)) if m else None
        if k == "spyglass" and re.search(r"map|atlas|chart", r["thing"]):
            k = "map"   # the csv kind spyglass/map holds both; maps are held in two hands, spyglasses at the eye
        if k:
            tags[k].add(r["thing"])
    tags["spyglass"].add("minecraft:spyglass"); tags["map"] |= {"minecraft:filled_map", "minecraft:map"}
    tags["spyglass"] -= tags["map"]
    tags["horn"].add("minecraft:goat_horn"); tags["wings"].add("minecraft:elytra"); tags["rod"].add("minecraft:fishing_rod")
    tags["throwable"] |= {"minecraft:snowball", "minecraft:egg", "minecraft:ender_pearl", "minecraft:splash_potion", "minecraft:lingering_potion", "minecraft:experience_bottle"}
    tags["drink"] |= {"minecraft:potion", "minecraft:milk_bucket", "minecraft:honey_bottle"}
    for k, v in tags.items():
        json.dump({"replace": False, "values": [{"id": x, "required": False} for x in sorted(v)]}, open(os.path.join(TAGS, k + ".json"), "w"), indent=0)
    print(len(C), "clips;", {k: len(v) for k, v in tags.items()})


main()
