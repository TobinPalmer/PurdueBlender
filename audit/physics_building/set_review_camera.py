"""Aim the Physics Building asset preview from Northwestern Avenue."""
import bpy
from mathutils import Vector
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSET_PATH = ROOT / "modular/buildings/physics_building_phys_3bf42f3.blend"
bpy.ops.wm.open_mainfile(filepath=str(ASSET_PATH))
camera = next((o for o in bpy.data.objects if o.type == "CAMERA"), None)
if camera is None:
    raise RuntimeError("Physics asset presentation camera is missing")
camera.location = (-155.0, 155.0, 50.0)
target = Vector((0.0, 0.0, 7.0))
camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
camera.data.lens = 52
camera["viewpoint_note"] = "Review angle from the northwest/Northwestern Avenue frontage; presentation only."
bpy.ops.wm.save_as_mainfile(filepath=str(ASSET_PATH), compress=True)
print({"asset": str(ASSET_PATH), "camera": camera.name, "location": list(camera.location)})
