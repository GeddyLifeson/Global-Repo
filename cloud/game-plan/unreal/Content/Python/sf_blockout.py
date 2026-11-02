"""B24: whiteboxes the Cinderreach vertical slice from sf_blockout_spec.json (tools/gen_blockout.py).

Editor only (it opens a level): Output Log, Python: py sf_blockout.py
Creates /GF_Cinderreach/Maps/L_Cinderreach_Slice as a World Partition level on the first run, then updates it in
place: actors are matched by their SfKey tag, moved and resized to the spec, and blockout actors the spec no longer
lists are deleted. Anything without the SfBlockout tag is left alone, so hand-placed art survives a rerun.
"""
import json
import os

import unreal

HERE = os.path.dirname(os.path.abspath(__file__))
TAG = "SfBlockout"
KEY = "SfKey:"
LIB = unreal.EditorAssetLibrary
ACTORS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
LEVELS = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
MESHES = {"cube": "/Engine/BasicShapes/Cube.Cube", "cylinder": "/Engine/BasicShapes/Cylinder.Cylinder"}


def open_map(path):
    if LIB.does_asset_exist(path):
        if not LEVELS.load_level(path):
            raise RuntimeError(f"SfBlockout: could not open {path}")
        return
    LIB.make_directory(path.rsplit("/", 1)[0])
    if not LEVELS.new_level(path, is_partitioned_world=True):
        raise RuntimeError(f"SfBlockout: could not create {path}; is the GF_Cinderreach plugin enabled?")


def keyed_actors():
    out = {}
    for actor in ACTORS.get_all_level_actors():
        tags = [str(t) for t in actor.tags]
        if TAG in tags:
            key = next((t[len(KEY):] for t in tags if t.startswith(KEY)), None)
            if key is None or key in out:
                ACTORS.destroy_actor(actor)
            else:
                out[key] = actor
    return out


def configure(actor, a, meshes):
    if a["cls"] == "StaticMeshActor":
        comp = actor.static_mesh_component
        comp.set_static_mesh(meshes[a["mesh"]])
        comp.set_collision_profile_name("BlockAll" if a.get("collision", True) else "NoCollision")
    elif a["cls"] == "TextRenderActor":
        text = actor.get_editor_property("text_render")
        text.set_editor_property("text", unreal.Text(a["text"]))
        text.set_editor_property("world_size", 150.0)
        text.set_editor_property("horizontal_alignment", unreal.HorizTextAligment.EHTA_CENTER)
    elif a["cls"] == "SkyLight":
        actor.get_editor_property("light_component").set_editor_property("real_time_capture", True)


def apply(a, existing, meshes):
    cls = getattr(unreal, a["cls"])
    loc = unreal.Vector(*a["loc"])
    pitch, yaw, roll = a["rot"]
    rot = unreal.Rotator(roll=roll, pitch=pitch, yaw=yaw)
    actor = existing.pop(a["key"], None)
    if actor is not None and actor.get_class() != cls.static_class():
        ACTORS.destroy_actor(actor)
        actor = None
    created = actor is None
    if created:
        actor = ACTORS.spawn_actor_from_class(cls, loc, rot)
    actor.set_actor_location_and_rotation(loc, rot, False, True)
    actor.set_actor_scale3d(unreal.Vector(*a["scale"]))
    actor.set_actor_label(a["label"])
    actor.set_folder_path(a["folder"])
    actor.set_editor_property("tags", [TAG, KEY + a["key"]] + a.get("tags", []))
    actor.set_editor_property("is_spatially_loaded", False)  # always loaded, so a rerun finds every blockout actor
    configure(actor, a, meshes)
    return created


def main():
    with open(os.path.join(HERE, "sf_blockout_spec.json")) as f:
        spec = json.load(f)
    open_map(spec["map"])
    meshes = {k: unreal.load_asset(v) for k, v in MESHES.items()}
    existing = keyed_actors()
    created = sum(apply(a, existing, meshes) for a in spec["actors"])
    for actor in existing.values():
        ACTORS.destroy_actor(actor)
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    unreal.log(f"SfBlockout: {spec['map']} {len(spec['levels'])} levels, {len(spec['actors'])} actors "
               f"({created} new, {len(spec['actors']) - created} updated, {len(existing)} removed)")


main()
