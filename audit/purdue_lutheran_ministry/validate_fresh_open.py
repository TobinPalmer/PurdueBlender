"""Fresh-open check for the PLM asset; run with Blender opening the asset first."""
import bpy
import hashlib
import json
from datetime import date
from pathlib import Path

ASSET_ID = "massing_purdue_lutheran_ministry_5425b3c"
ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = Path(__file__).resolve().parent
EXPECTED_ANCHOR = (345.768593, 45.942800)
COLLECTION = bpy.data.collections.get("Asset_" + ASSET_ID)
SCENE = bpy.data.scenes.get("Building_" + ASSET_ID)
ROOT_OBJECT = bpy.data.objects.get("AssetRoot_" + ASSET_ID)
assert COLLECTION is not None, "Expected asset collection missing"
assert SCENE is not None, "Expected building scene missing"
assert ROOT_OBJECT is not None, "Placement root missing"

OBJECTS = list(COLLECTION.all_objects)
MESHES = [obj for obj in OBJECTS if obj.type == "MESH"]
assert ROOT_OBJECT in OBJECTS
assert all(obj.parent == ROOT_OBJECT for obj in OBJECTS if obj is not ROOT_OBJECT), "Asset objects are not rooted at local origin"
assert tuple(round(float(v), 6) for v in ROOT_OBJECT.location) == (0.0, 0.0, 0.0)
anchor = tuple(round(float(v), 6) for v in ROOT_OBJECT.get("campus_anchor_xy_m", ()))
assert anchor == EXPECTED_ANCHOR, f"Unexpected campus anchor {anchor}"

points = [ROOT_OBJECT.matrix_world.inverted() @ obj.matrix_world @ vertex.co
          for obj in MESHES for vertex in obj.data.vertices]
bounds = [[round(min(point[i] for point in points), 4), round(max(point[i] for point in points), 4)]
          for i in range(3)]
asset_camera_lights = [obj.name for obj in OBJECTS if obj.type in {"CAMERA", "LIGHT"}]
assert not asset_camera_lights, f"Review camera/light leaked into exported collection: {asset_camera_lights}"
external_images = [image.filepath for image in bpy.data.images if image.source == "FILE"]
assert not external_images, f"External image dependencies: {external_images}"
assert bpy.data.collections.get("PLM | removable roof panels, hide to inspect interior") is not None
assert bpy.data.collections["PLM | removable roof panels, hide to inspect interior"].hide_render is False
assert not any(mod.type == "BOOLEAN" for obj in COLLECTION.all_objects for mod in obj.modifiers), "Unapplied Boolean cutter modifiers remain"
assert len(MESHES) >= 100, f"Detailed asset mesh count unexpectedly low: {len(MESHES)}"
assert "PLM | exterior ministry sign" in bpy.data.objects
assert "PLM | front porch shingle canopy" in bpy.data.objects

report = {
    "asset_id": ASSET_ID,
    "validated_date": date.today().isoformat(),
    "opened_file": bpy.data.filepath,
    "asset_sha256": hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),
    "scene": SCENE.name,
    "collection": COLLECTION.name,
    "scene_and_collection_found": True,
    "asset_objects": len(OBJECTS),
    "mesh_objects": len(MESHES),
    "all_asset_objects_parented_to_local_root": True,
    "root_local_xyz": [round(float(v), 6) for v in ROOT_OBJECT.location],
    "placement_anchor_xy_m": list(anchor),
    "evaluated_asset_bounds_local_m": {"x": bounds[0], "y": bounds[1], "z": bounds[2]},
    "review_camera_lights_inside_export_collection": asset_camera_lights,
    "external_image_dependencies": external_images,
    "boolean_apertures_applied": True,
    "render_roof_visible_by_default": True,
    "render_previews": ["review_preview.png", "review_preview_roof.png", "review_preview_interior.png"],
}
(EVIDENCE / "fresh_open_validation_2026-10-26.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print("FRESH_OPEN_VALIDATION=" + json.dumps(report))
