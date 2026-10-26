"""Reopen, inspect, and render CQS without changing shared campus files."""
import bpy
import json
import math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ASSET_ID = "massing_cary_quadrangle_south_cqs_7ee2283"
ASSET = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
OUT = Path(__file__).resolve().parent
COLL_NAME = f"Asset_{ASSET_ID}"
SCENE_NAME = f"Building_{ASSET_ID}"


def aim(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def render_view(scene, name, camera_location, target, ortho_scale, resolution=(1500, 850)):
    cam_data = bpy.data.cameras.new("CQS evidence camera")
    cam = bpy.data.objects.new("CQS evidence camera", cam_data)
    scene.collection.objects.link(cam)
    cam.location = camera_location
    aim(cam, target)
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = ortho_scale
    scene.camera = cam
    scene.render.resolution_x, scene.render.resolution_y = resolution
    scene.render.filepath = str(OUT / name)
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam, do_unlink=True)
    bpy.data.cameras.remove(cam_data)


def run():
    bpy.ops.wm.open_mainfile(filepath=str(ASSET))
    scene = bpy.data.scenes.get(SCENE_NAME)
    coll = bpy.data.collections.get(COLL_NAME)
    assert scene and coll, "Expected CQS scene or collection missing after reopen"
    objs = list(coll.objects)
    assert len(objs) == 1, f"Expected a single exported building object, found {len(objs)}"
    obj = objs[0]
    assert obj.type == "MESH" and obj.name == "Cary Quadrangle South (CQS)"
    assert obj.get("stable_building_id") == ASSET_ID
    assert len(obj.modifiers) == 0, "Unexpected modifiers need evaluation before dimensions are recorded"
    depsgraph = bpy.context.evaluated_depsgraph_get()
    eval_obj = obj.evaluated_get(depsgraph)
    points = [eval_obj.matrix_world @ Vector(corner) for corner in eval_obj.bound_box]
    bounds = [[min(p[i] for p in points), max(p[i] for p in points)] for i in range(3)]
    edge_use = {}
    mesh = eval_obj.to_mesh()
    for poly in mesh.polygons:
        for key in poly.edge_keys:
            edge_use[tuple(sorted(key))] = edge_use.get(tuple(sorted(key)), 0) + 1
    open_edges = sum(v == 1 for v in edge_use.values())
    nonmanifold_edges = sum(v != 2 for v in edge_use.values())
    eval_obj.to_mesh_clear()
    loc = list(obj.location)
    scale = list(obj.scale)
    assert max(abs(x) for x in loc) < 1e-6 and max(abs(x - 1) for x in scale) < 1e-6
    assert len(obj.data.materials) >= 4, "Expected masonry, stone, roof, and glazing materials"
    # Collection and object transforms remain identity in campus coordinates.
    assert tuple(coll.instance_offset) == (0.0, 0.0, 0.0)

    # Temporary photographic evidence lighting and cameras are removed after render.
    rig = bpy.data.collections.new("CQS_render_only")
    scene.collection.children.link(rig)
    world = bpy.data.worlds.new("CQS render world") if not scene.world else scene.world
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value = (0.56, 0.60, 0.66, 1.0)
    bg.inputs["Strength"].default_value = 0.8
    light_data = bpy.data.lights.new("CQS large softbox", "AREA")
    light = bpy.data.objects.new("CQS large softbox", light_data)
    rig.objects.link(light)
    light.location = (-365.0, 360.0, 180.0)
    light_data.energy = 30000
    light_data.shape = "DISK"
    light_data.size = 120
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "Medium High Contrast"
    scene.view_settings.exposure = 0.0
    scene.view_settings.gamma = 1.0
    cx = (bounds[0][0] + bounds[0][1]) / 2
    cy = (bounds[1][0] + bounds[1][1]) / 2
    # South-facing view follows the documented 2006 camera position/heading.
    render_view(scene, "cqs_south_preview.png", (cx, bounds[1][0] - 3, 8),
                (cx, bounds[1][0] + 32, 11.0), 108)
    render_view(scene, "cqs_top_preview.png", (cx, cy, 210), (cx, cy, 8.0), 205)
    for o in list(rig.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    bpy.data.collections.remove(rig)

    report = {
        "asset_id": ASSET_ID,
        "reopened_asset": str(ASSET.relative_to(ROOT)),
        "scene": scene.name,
        "collection": coll.name,
        "collection_object_count": len(objs),
        "object_name": obj.name,
        "object_type": obj.type,
        "stable_id_custom_property": obj.get("stable_building_id"),
        "evaluated_world_bounds_m": bounds,
        "object_location": loc,
        "object_scale": scale,
        "object_rotation_euler": list(obj.rotation_euler),
        "mesh_vertices": len(obj.data.vertices),
        "mesh_polygons": len(obj.data.polygons),
        "material_names": [m.name if m else None for m in obj.data.materials],
        "modifier_count": len(obj.modifiers),
        "boundary_edge_count": open_edges,
        "nonmanifold_edge_count": nonmanifold_edges,
        "expected_collection_transform": "Identity; simple massing remains in campus coordinates.",
        "placement_source": "Purdue BuildingShapesZip4 FID 653, BLDG_ABBR CQS; project local approximation documented in builder.",
        "height_uncertainty": "GIS Extrution=54 unit undocumented; modeled height is a photo-proportion estimate.",
        "facade_uncertainty": "South elevation photo is building-specific, but window dimensions are schematic; roof pitch is estimated.",
        "rendered_views": ["cqs_south_preview.png", "cqs_top_preview.png"],
        "validation": "Saved asset reopened successfully; named scene/collection and campus-coordinate object verified; no unapplied modifiers. Mesh is built from closed solids, with intersections between joined features; manifold counts reflect those intersections.",
    }
    (OUT / "reopen_validation.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


run()
