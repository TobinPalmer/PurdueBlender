"""Read-only inspect/render pass for the inherited CQE massing library."""
import bpy
import json
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / "modular" / "buildings" / "massing_cary_quadrangle_east_cqe_230c813.blend"
OUT = ROOT / "audit" / "massing_cary_quadrangle_east_cqe_230c813"
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
scene = bpy.context.scene
collection = bpy.data.collections.get("Asset_massing_cary_quadrangle_east_cqe_230c813")
records = []
coords = []
for obj in collection.objects:
    world = [obj.matrix_world @ Vector(v) for v in obj.bound_box]
    coords += world
    records.append({
        "name": obj.name,
        "type": obj.type,
        "dimensions": list(obj.dimensions),
        "location": list(obj.location),
        "vertices": len(obj.data.vertices) if obj.type == "MESH" else 0,
        "faces": len(obj.data.polygons) if obj.type == "MESH" else 0,
        "materials": [m.name for m in obj.data.materials] if obj.type == "MESH" else [],
    })
bounds = [[min(p[i] for p in coords), max(p[i] for p in coords)] for i in range(3)]
(OUT / "original_inspection.json").write_text(json.dumps({
    "asset": str(ASSET.relative_to(ROOT)).replace("\\", "/"),
    "scene": scene.name,
    "collection": collection.name,
    "bounds_world_m": bounds,
    "objects": records,
}, indent=2) + "\n", encoding="utf-8")

# Temporary, unsaved preview setup.
center = Vector(((bounds[0][0]+bounds[0][1])/2, (bounds[1][0]+bounds[1][1])/2, (bounds[2][0]+bounds[2][1])/2))
cam_data = bpy.data.cameras.new("CQE_Before_Camera")
camera = bpy.data.objects.new("CQE_Before_Camera", cam_data)
scene.collection.objects.link(camera)
camera.location = center + Vector((75, -105, 54))
camera.rotation_euler = (center - camera.location).to_track_quat("-Z", "Y").to_euler()
cam_data.lens = 50
scene.camera = camera
light_data = bpy.data.lights.new("CQE_Before_Key", "AREA")
light_data.energy = 13000
light_data.shape = "DISK"
light_data.size = 75
light = bpy.data.objects.new("CQE_Before_Key", light_data)
scene.collection.objects.link(light)
light.location = center + Vector((-35, -55, 105))
scene.render.engine = "BLENDER_EEVEE_NEXT"
scene.render.resolution_x = 1000
scene.render.resolution_y = 800
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = str(OUT / "original_preview.png")
bpy.ops.render.render(write_still=True)
print(json.dumps({"scene": scene.name, "collection": collection.name, "bounds": bounds, "objects": records}, indent=2))
