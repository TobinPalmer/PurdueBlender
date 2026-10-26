"""Reopen BIDC library, validate its contract, and render final previews."""
import bpy
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUILDING_ID = "bechtel_innovation_design_center_bidc"
ASSET = ROOT / "modular" / "buildings" / f"{BUILDING_ID}.blend"
OUT = ROOT / "audit" / BUILDING_ID
COLLECTION = f"Asset_{BUILDING_ID}"

bpy.ops.wm.open_mainfile(filepath=str(ASSET))
scene = bpy.context.scene
asset = bpy.data.collections.get(COLLECTION)
assert asset is not None, f"Missing required collection {COLLECTION}"
meshes = [obj for obj in asset.all_objects if obj.type == "MESH"]
assert len(meshes) >= 200, f"Unexpectedly low mesh count: {len(meshes)}"
shell = bpy.data.objects.get("BIDC_GIS_primary_shell")
assert shell is not None and shell.type == "MESH", "Missing footprint-driven shell"
assert len(shell.data.vertices) == 48, "Prism shell no longer follows 24-point GIS ring"
coords = [shell.matrix_world @ vertex.co for vertex in shell.data.vertices]
bounds = [
    [min(v[axis] for v in coords), max(v[axis] for v in coords)]
    for axis in range(3)
]
expected = [[-18.612, 17.639], [-17.729, 15.810], [0.0, 10.35]]
for axis in range(3):
    assert all(abs(bounds[axis][i] - expected[axis][i]) < 0.01 for i in range(2)), (bounds, expected)
assert bpy.data.collections.get("Preview_Rig_not_for_export") is not None
assert not [image.filepath for image in bpy.data.images if image.source == "FILE"]

scene.render.resolution_x = 1280
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
for camera_name, filename in (("BIDC_overview_camera", "overview.png"),
                              ("BIDC_plan_camera", "plan.png")):
    camera = bpy.data.objects.get(camera_name)
    assert camera is not None and camera.type == "CAMERA"
    scene.camera = camera
    scene.render.filepath = str(OUT / filename)
    bpy.ops.render.render(write_still=True)

report = {
    "asset_file": ASSET.relative_to(ROOT).as_posix(),
    "reopened": True,
    "collection": COLLECTION,
    "mesh_object_count": len(meshes),
    "gis_shell": shell.name,
    "gis_shell_vertex_count": len(shell.data.vertices),
    "gis_shell_bounds_local_m": [[round(v, 6) for v in axis] for axis in bounds],
    "external_image_dependencies": [],
    "previews_rendered_after_reopen": [
        f"audit/{BUILDING_ID}/overview.png", f"audit/{BUILDING_ID}/plan.png"
    ],
}
(OUT / "validation.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, indent=2))
