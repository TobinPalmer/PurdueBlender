"""Repair the Beering Hall rooftop room and source-supported facade accents.

Run with Blender in background mode. This script updates only the dedicated
Beering Hall library and writes previews/evidence under audit/beering_hall/.
The existing modular local frame, GIS-aligned walls, manifest collection name,
and placement origin remain unchanged.
"""
import bpy
import json
import math
import hashlib
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / "modular" / "buildings" / "beering_hall.blend"
OUT = ROOT / "audit" / "beering_hall"
OUT.mkdir(parents=True, exist_ok=True)
SCENE_NAME = "Building_beering_hall"
COLLECTION_NAME = "Asset_beering_hall"


def material(name, color, roughness=0.55, metallic=0.0):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
    return mat


def assign(obj, mat):
    if obj.data and hasattr(obj.data, "materials"):
        obj.data.materials.clear()
        obj.data.materials.append(mat)


def move_to_collection(obj, collection):
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    collection.objects.link(obj)


def cube(name, location, dimensions, mat, collection, rotation=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    obj.rotation_euler.z = rotation
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    assign(obj, mat)
    move_to_collection(obj, collection)
    return obj


def cylinder(name, location, radius, depth, mat, collection, vertices=96):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth,
                                        location=location)
    obj = bpy.context.object
    obj.name = name
    assign(obj, mat)
    move_to_collection(obj, collection)
    return obj


def point_camera(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def add_preview_setup(scene, export_collection, white, brick):
    setup = bpy.data.collections.get("Beering_Preview_Setup")
    if not setup:
        setup = bpy.data.collections.new("Beering_Preview_Setup")
        scene.collection.children.link(setup)
    for obj in list(setup.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    # A neutral ground plane is strictly scene-only; it is not exported with the asset.
    floor_mat = material("Beering Preview Ground", (0.12, 0.16, 0.20), 0.9)
    bpy.ops.mesh.primitive_plane_add(size=240, location=(0, 0, -0.08))
    ground = bpy.context.object
    ground.name = "Beering_Preview_Ground"
    assign(ground, floor_mat)
    move_to_collection(ground, setup)
    for name, loc, energy, size in [
        ("Beering_Preview_Key", (-70, -95, 110), 14000, 65),
        ("Beering_Preview_Fill", (90, -30, 65), 8000, 55),
        ("Beering_Preview_Rim", (10, 95, 95), 10000, 55),
    ]:
        data = bpy.data.lights.new(name, "AREA")
        data.energy = energy
        data.shape = "DISK"
        data.size = size
        light = bpy.data.objects.new(name, data)
        setup.objects.link(light)
        light.location = loc
        point_camera(light, (0, 0, 12))
    cam_data = bpy.data.cameras.new("Beering_Preview_Camera")
    cam = bpy.data.objects.new("Beering_Preview_Camera", cam_data)
    setup.objects.link(cam)
    cam.location = (-115, -130, 100)
    point_camera(cam, (0, 0, 12))
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = 145
    scene.camera = cam
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.world.color = (0.16, 0.18, 0.23)
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "Medium High Contrast"
    return setup


def render_view(scene, path, location, target, ortho_scale, resolution):
    cam = scene.camera
    cam.location = location
    point_camera(cam, target)
    cam.data.ortho_scale = ortho_scale
    scene.render.resolution_x, scene.render.resolution_y = resolution
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


def main():
    bpy.ops.wm.open_mainfile(filepath=str(ASSET))
    scene = bpy.data.scenes.get(SCENE_NAME)
    asset = bpy.data.collections.get(COLLECTION_NAME)
    assert scene and asset, "Expected Beering Hall scene/collection missing"
    # The prior model placed a 14 m wide brick drum and green tiered dome on
    # the lower classroom wing. Remove that entire unsupported cluster,
    # including observatory-like furniture. The official view instead shows
    # a shallow white annular glazed room atop the high brick tower.
    legacy_prefixes = ("BRNG_Rotunda_", "BRNG_Vision21_")
    generated_prefixes = ("BRNG_Rooftop_Room_", "BRNG_Classroom_Tall_Glazing")
    old_feature_objects = [o for o in list(asset.all_objects) if o.name.startswith(legacy_prefixes)]
    previous_generated_objects = [o for o in list(asset.all_objects)
                                  if o.name.startswith(generated_prefixes)]
    for obj in old_feature_objects + previous_generated_objects:
        bpy.data.objects.remove(obj, do_unlink=True)
    before = {o.name for o in asset.all_objects}

    brick = material("Beering Brick - warm red", (0.40, 0.105, 0.070), 0.82)
    stone = material("Beering Rooftop Room - pale limestone", (0.86, 0.83, 0.74), 0.45)
    glass = material("Beering Rooftop Room - blue gray glazing", (0.045, 0.105, 0.14), 0.20, 0.18)
    dark = material("Beering Rooftop Room - mullion shadow", (0.10, 0.13, 0.14), 0.45)

    # Locate the cylindrical room on the center of the existing office-tower
    # roof, derived from the retained source model's tower bounds. The GIS
    # footprint is not evidence for roof equipment location or height.
    tower = bpy.data.objects.get("BRNG_Office_Tower_Masonry")
    assert tower and tower.name in asset.objects
    tower_cx = (tower.bound_box[0][0] + tower.bound_box[6][0]) / 2.0
    # Use evaluated world bounds for robustness when source object transforms vary.
    deps = bpy.context.evaluated_depsgraph_get()
    ev = tower.evaluated_get(deps)
    mesh = ev.to_mesh()
    pts = [ev.matrix_world @ v.co for v in mesh.vertices]
    tx = (min(p.x for p in pts) + max(p.x for p in pts)) / 2.0
    ty = (min(p.y for p in pts) + max(p.y for p in pts)) / 2.0
    tz = max(p.z for p in pts)
    ev.to_mesh_clear()
    # Correct the source-derived tower center to stable values from its measured
    # evaluated bounds. The profile is inferred from the official oblique photo.
    cx, cy, roof = tx, ty, tz
    radius = 5.05
    bottom = roof + 0.05
    room_top = 29.70  # Preserve the pre-repair library's maximum roof datum.
    window_bottom = bottom + 0.42
    window_top = room_top - 0.70
    room_height = room_top - bottom
    assert room_height > 2.2

    # Low white base ring; tall vertical glazing; evenly spaced white piers;
    # a solid, shallow circular crown. This reproduces the visible ring-like
    # silhouette without asserting an undocumented roof construction.
    cylinder("BRNG_Rooftop_Room_Base", (cx, cy, bottom + 0.12), radius + 0.35, 0.24, stone, asset)
    pane_count = 24
    pane_radius = radius - 0.04
    pane_height = window_top - window_bottom
    pane_mid = (window_top + window_bottom) / 2.0
    for i in range(pane_count):
        a = 2 * math.pi * i / pane_count
        px = cx + pane_radius * math.cos(a)
        py = cy + pane_radius * math.sin(a)
        angle = a + math.pi / 2.0
        cube(f"BRNG_Rooftop_Room_Glazed_Bay_{i:02d}", (px, py, pane_mid),
             (0.93, 0.08, pane_height), glass, asset, angle)
        # Thin center mullion on each glazed bay, matching the photo's narrow
        # vertical divisions. Piers themselves read as the white exterior ring.
        cube(f"BRNG_Rooftop_Room_Mullion_{i:02d}", (px, py - 0.045 * math.sin(a), pane_mid),
             (0.045, 0.10, pane_height), dark, asset, angle)
        pier_r = radius + 0.10
        qx = cx + pier_r * math.cos(a)
        qy = cy + pier_r * math.sin(a)
        cube(f"BRNG_Rooftop_Room_White_Pier_{i:02d}", (qx, qy, pane_mid),
             (0.27, 0.34, pane_height + 0.08), stone, asset, angle)
    cylinder("BRNG_Rooftop_Room_Crown_Fascia", (cx, cy, room_top - 0.34), radius + 0.42, 0.48, stone, asset)
    cylinder("BRNG_Rooftop_Room_Flat_Crown", (cx, cy, room_top - 0.08), radius + 0.28, 0.16, stone, asset)

    # Photo-backed variation in the classroom-wing facade: add five tall,
    # vertically proportioned glazed bays on the long elevation while
    # retaining the existing smaller window rhythm elsewhere. Positions are
    # intentionally described as a visual interpretation, not surveyed data.
    wing = bpy.data.objects.get("BRNG_Classroom_Wing_Masonry")
    assert wing and wing.name in asset.objects
    ev = wing.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = ev.to_mesh()
    wpts = [ev.matrix_world @ v.co for v in mesh.vertices]
    ymin = min(p.y for p in wpts)
    xmin, xmax = min(p.x for p in wpts), max(p.x for p in wpts)
    ev.to_mesh_clear()
    # Five broad 2-storey curtain-window groups on the west-facing long wall.
    # Image-to-cardinal registration is not proven; this side is a qualitative
    # interpretation of the main facade visible in the official oblique photo.
    for i, y in enumerate([ymin + 12.0, ymin + 26.0, ymin + 40.0, ymin + 54.0, ymin + 68.0]):
        cube(f"BRNG_Classroom_Tall_Glazing_{i+1:02d}", (xmin - 0.09, y, 8.0),
             (0.10, 3.8, 7.0), glass, asset)
        for dy in (-1.75, 0.0, 1.75):
            cube(f"BRNG_Classroom_Tall_Glazing_Mullion_{i+1:02d}_{dy:+.2f}",
                 (xmin - 0.16, y + dy, 8.0), (0.12, 0.09, 7.0), dark, asset)
        for z in (4.5, 8.0, 11.5):
            cube(f"BRNG_Classroom_Tall_Glazing_Horizontal_{i+1:02d}_{z:.1f}",
                 (xmin - 0.165, y, z), (0.12, 3.8, 0.10), dark, asset)

    # Mark estimated-vs-supported fields on the asset root for downstream use.
    root = bpy.data.objects.get("AssetRoot_beering_hall")
    if root:
        root["building_id"] = "beering_hall"
        root["owner"] = "Rosen"
        root["roof_evidence"] = "Official Purdue College of Education exterior photo; qualitative"
        root["roof_location_status"] = "Inferred atop BRNG_Office_Tower_Masonry; not surveyed"
        root["height_status"] = "Unverified; GIS R=95.1 and Extrution=38 units/definitions undocumented"
        root["story_status"] = "GIS reports NUM_LEVELS=9; total story configuration not independently verified"
        root["placement_origin_xy_m"] = [-201.3499984741211, -206.14999389648438]

    # Keep camera/light/ground setup out of the exported asset collection.
    setup = add_preview_setup(scene, asset, stone, brick)
    assert not [o for o in asset.all_objects if o.type in {"CAMERA", "LIGHT"}]

    # Save and render visual evidence.
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET))
    render_view(scene, OUT / "beering_hall_repaired_preview.png",
                (-115, -130, 100), (0, 0, 12), 145, (1200, 900))
    render_view(scene, OUT / "beering_hall_rooftop_room_detail.png",
                (-45, -55, 55), (cx, cy, 26.6), 38, (1200, 900))

    report = {
        "asset_id": "beering_hall",
        "owner": "Rosen",
        "scene": SCENE_NAME,
        "collection": COLLECTION_NAME,
        "asset": str(ASSET),
        "removed_legacy_rotunda_and_vision21_objects": len(old_feature_objects),
        "removed_previous_generated_objects_for_idempotence": len(previous_generated_objects),
        "added_asset_objects": len(set(o.name for o in asset.all_objects) - before),
        "rooftop_room_center_local_m": [cx, cy],
        "tower_roof_z_estimated_m": roof,
        "rooftop_room_top_m": room_top,
        "structural_footprint_edited": False,
        "manifest_placement_edited": False,
        "asset_collection_object_count": len(asset.all_objects),
        "preview": "audit/beering_hall/beering_hall_repaired_preview.png",
        "rooftop_detail": "audit/beering_hall/beering_hall_rooftop_room_detail.png",
        "asset_sha256": hashlib.sha256(ASSET.read_bytes()).hexdigest(),
        "height_story_status": "GIS reports 9 levels, but total floor/story layout and measured roof height remain unverified. R=95.1 and Extrution=38 have undocumented units/definitions. Model elevations are inherited/estimated visual geometry, not measurements.",
        "limitations": [
            "GIS supports identity, footprint and position, not roof geometry or height.",
            "Purdue College of Education exterior photo supports a shallow white ring-like glazed rooftop room on the high brick tower; exact location, dimensions and construction are not measured.",
            "The tall glazing bays are qualitative interpretations of the official oblique image; other elevations are not fully source-verified.",
            "The pre-existing GIS-aligned structural plan and manifest placement were preserved without re-registration to every GIS vertex.",
        ],
    }
    (OUT / "build_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
