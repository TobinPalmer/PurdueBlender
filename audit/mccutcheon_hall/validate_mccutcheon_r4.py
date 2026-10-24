import bpy
import json
import os
from mathutils import Vector
from pathlib import Path

ROOT = Path(r"C:\Users\Tobin\Documents\Blender\PurdueMap")
ASSET = ROOT / "modular/buildings/mccutcheon_hall.blend"
AUDIT = ROOT / "audit/mccutcheon_hall"
bpy.ops.wm.open_mainfile(filepath=str(ASSET))

asset = bpy.data.collections["Asset_mccutcheon_hall"]
scene = bpy.data.scenes["Building_mccutcheon_hall"]
root = bpy.data.objects["AssetRoot_mccutcheon_hall"]
overlay = bpy.data.objects["MCUT_Official_Footprint_Overlay"]
assert len(asset.all_objects) == 219, len(asset.all_objects)
assert len(asset.objects) == 1
assert root.location.length < 1e-6 and all(abs(v - 1) < 1e-6 for v in root.scale)
assert scene.camera and scene.camera.name == "Cam_Hero_Perspective"
assert abs(scene.camera.data.lens - 30.0) < 1e-4
assert scene.world and scene.world.name == "McCutcheon_Clear_Day_Sky"
assert any(n.type == "TEX_SKY" and n.sky_type == "HOSEK_WILKIE" for n in scene.world.node_tree.nodes)
assert overlay.hide_render and not overlay.hide_viewport and overlay.get("source_fid") == 57
assert root.get("r4_documented_north_tower_occupied_floors") == 8
assert root.get("r4_documented_south_tower_occupied_floors") == 8
assert all(bpy.data.objects.get(f"MCUT_{tower}_{suffix}") is None
           for tower in ("North", "South")
           for suffix in ("Penthouse_Brick", "Penthouse_Coping", "Penthouse_Roof_Slab",
                          "PH_Louver_N", "PH_Louver_S", "PH_Louver_W", "PH_Louver_E", "PH_Door"))
assert all(bpy.data.objects.get(name) for name in (
    "MCUT_North_Tower_Roof_Deck", "MCUT_South_Tower_Roof_Deck",
    "MCUT_North_Tower_Parapet_N", "MCUT_South_Tower_Parapet_N",
    "MCUT_North_Tower_Coping_N", "MCUT_South_Tower_Coping_N"))

expected = {
    "Site_Lawn_Base": "MCUT_Grass_Lawn_Qualitative",
    "Site_McCutcheon_Drive": "MCUT_Asphalt_Drive_Qualitative",
    "Site_MacArthur_Drive": "MCUT_Asphalt_Drive_Qualitative",
}
materials = {}
for name, material_name in expected.items():
    obj = bpy.data.objects[name]
    materials[name] = [m.name for m in obj.data.materials]
    assert obj.data.materials and obj.data.materials[0].name == material_name

images, missing = [], []
for image in bpy.data.images:
    if image.source == "FILE" and image.filepath:
        resolved = bpy.path.abspath(image.filepath)
        item = {"name": image.name, "filepath": image.filepath,
                "resolved_exists": os.path.exists(resolved), "packed": bool(image.packed_file)}
        images.append(item)
        if not item["resolved_exists"] and not item["packed"]:
            missing.append(item)
assert not missing, missing

z_values = []
for obj in asset.all_objects:
    if obj.type == "MESH":
        z_values.extend((obj.matrix_world @ Vector(corner)).z for corner in obj.bound_box)
model_top = max(z_values)
tower_roof_top = max((obj.matrix_world @ Vector(corner)).z
                      for obj in asset.all_objects
                      if obj.type == "MESH" and "Tower_" in obj.name
                      and "HVAC" not in obj.name
                      for corner in obj.bound_box)
assert 27.5 < tower_roof_top < 28.0, tower_roof_top

scene.render.resolution_x = 1440
scene.render.resolution_y = 810
scene.render.resolution_percentage = 75
scene.render.image_settings.file_format = "PNG"
renders = []
for camera_name, output_name in (
    ("Cam_Hero_Perspective", "mccutcheon_r4_hero.png"),
    ("Cam_East_Entrance", "mccutcheon_r4_entrance.png"),
):
    scene.camera = bpy.data.objects[camera_name]
    path = AUDIT / output_name
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True, scene=scene.name)
    renders.append(str(path.relative_to(ROOT)).replace("\\", "/"))

result = {
    "revision": 4,
    "passed": True,
    "saved_asset_reopened": True,
    "blender_version": bpy.app.version_string,
    "collection": asset.name,
    "direct_objects": len(asset.objects),
    "child_inclusive_objects": len(asset.all_objects),
    "root_location": list(root.location),
    "root_scale": list(root.scale),
    "all_asset_mesh_top_m_including_hvac": round(float(model_top), 4),
    "tower_roof_top_m_excluding_roof_hvac": round(float(tower_roof_top), 4),
    "north_tower_documented_occupied_floors": root["r4_documented_north_tower_occupied_floors"],
    "south_tower_documented_occupied_floors": root["r4_documented_south_tower_occupied_floors"],
    "removed_rooftop_penthouse_object_count": 16,
    "tower_roof_decks_parapets_copings_retained": True,
    "gis_overlay": {"hide_render": overlay.hide_render, "hide_viewport": overlay.hide_viewport,
                    "source_fid": overlay.get("source_fid")},
    "site_materials": materials,
    "packed_foliage_image_count": sum(item["packed"] for item in images),
    "unresolved_unpacked_images": missing,
    "lidar_height_estimate": {
        "p95_above_nearby_ground_m": root["r4_lidar_roof_p95_height_above_ground_m"],
        "p99_9_above_nearby_ground_m": root["r4_lidar_roof_p999_height_above_ground_m"],
        "max_candidate_above_nearby_ground_m": root["r4_lidar_max_candidate_height_above_ground_m"],
        "classification_and_accuracy_limitations_recorded": True,
    },
    "renders": renders,
    "master_edited": False,
}
(AUDIT / "mccutcheon_r4_validation.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print("MCUT_R4_VALIDATION=" + json.dumps(result, indent=2))

