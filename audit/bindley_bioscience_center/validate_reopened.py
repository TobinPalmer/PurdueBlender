"""Reopen and contract-check Bindley, then render previews from that file."""
import bpy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUILDING_ID = "bindley_bioscience_center"
ASSET = ROOT / "modular" / "buildings" / f"{BUILDING_ID}.blend"
OUT = ROOT / "audit" / BUILDING_ID
COLLECTION = f"Asset_{BUILDING_ID}"
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
scene = bpy.context.scene
asset = bpy.data.collections.get(COLLECTION)
assert asset is not None, f"Missing required collection: {COLLECTION}"
meshes = [obj for obj in asset.all_objects if obj.type == "MESH"]
assert len(meshes) > 400, f"Unexpected mesh count {len(meshes)}"
shell = bpy.data.objects.get("BIND_GIS_primary_shell")
assert shell is not None and shell.type == "MESH"
shell_name = shell.name
shell_vertex_count = len(shell.data.vertices)
assert shell_vertex_count == 382, f"Expected two shell vertices per GIS ring point; got {shell_vertex_count}"
coords = [shell.matrix_world @ vertex.co for vertex in shell.data.vertices]
bounds = [[min(v[axis] for v in coords), max(v[axis] for v in coords)] for axis in range(3)]
expected = [[-16.4493147, 20.2156676], [-50.6889256, 47.9088218], [0.0, 13.3]]
for axis in range(3):
    assert all(abs(bounds[axis][i] - expected[axis][i]) < 0.02 for i in range(2)), (bounds, expected)
assert bpy.data.collections.get("Preview_Rig_not_for_export") is not None
assert not [img.filepath for img in bpy.data.images if img.source == "FILE"]
sign = bpy.data.objects.get("BIND_entry_name_wall")
assert sign is not None and sign.type == "MESH" and sign.dimensions.z >= 3.4
assert sign.data.materials and sign.data.materials[0].diffuse_color[0] < 0.04
sign_text = bpy.data.objects.get("BIND_entry_sign_text")
assert sign_text is not None and sign_text.type == "FONT"
roof_equipment = [obj for obj in asset.all_objects if obj.name.startswith(("BIND_roof_plant_screen_", "BIND_roof_vent_"))]
assert len(roof_equipment) == 8
roof_tops = {obj.name: max((obj.matrix_world @ v.co).z for v in obj.data.vertices)
             for obj in roof_equipment if obj.type == "MESH"}
assert max(roof_tops.values()) <= 14.51, roof_tops

scene.render.resolution_x = 1440
scene.render.resolution_y = 1000
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
for camera_name, filename in (("BIND_overview_camera", "overview.png"),
                              ("BIND_entry_camera", "entry_detail.png"),
                              ("BIND_plan_camera", "plan.png")):
    camera = bpy.data.objects.get(camera_name)
    assert camera and camera.type == "CAMERA"
    scene.camera = camera
    scene.render.filepath = str(OUT / filename)
    bpy.ops.render.render(write_still=True)

# Recreate and reopen the collection-only handoff artifact. The export is
# deliberately saved inside Bindley's own audit folder for review.
export_file = OUT / "bindley_collection_export_probe.blend"
bpy.data.libraries.write(str(export_file), {asset}, path_remap="RELATIVE_ALL", fake_user=True)
bpy.ops.wm.open_mainfile(filepath=str(export_file))
exported = bpy.data.collections.get(COLLECTION)
assert exported is not None
export_objects = list(exported.all_objects)
assert len(export_objects) == 528, f"Unexpected exported object count {len(export_objects)}"
assert not [obj.name for obj in export_objects if obj.type in {"CAMERA", "LIGHT"}]
assert not [lib.filepath for lib in bpy.data.libraries]

report = {
    "asset_file": ASSET.relative_to(ROOT).as_posix(),
    "reopened": True,
    "collection": COLLECTION,
    "mesh_object_count": len(meshes),
    "gis_shell": shell_name,
    "gis_shell_vertex_count": shell_vertex_count,
    "gis_shell_bounds_local_m": [[round(v, 6) for v in axis] for axis in bounds],
    "external_image_dependencies": [],
    "dark_name_wall_present": True,
    "roof_screen_and_vent_tops_local_m": {name: round(float(z), 4) for name, z in roof_tops.items()},
    "roof_equipment_max_top_local_m": round(float(max(roof_tops.values())), 4),
    "roof_equipment_height_status": "Conservative schematic tops at or below 14.5 m; no verified roof plan or section found.",
    "collection_export_file": f"audit/{BUILDING_ID}/bindley_collection_export_probe.blend",
    "collection_export_reopened": True,
    "collection_export_object_count": len(export_objects),
    "collection_export_camera_or_light_objects": [],
    "collection_export_linked_libraries": [],
    "previews_rendered_after_reopen": [
        f"audit/{BUILDING_ID}/overview.png",
        f"audit/{BUILDING_ID}/entry_detail.png",
        f"audit/{BUILDING_ID}/plan.png"
    ]
}
(OUT / "validation.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, indent=2))
