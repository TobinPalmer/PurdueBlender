import bpy
from pathlib import Path
from mathutils import Vector

root = Path(__file__).resolve().parents[3]
asset = root / "modular" / "buildings" / "alpha_epsilon_pi.blend"
out = Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(asset))
scene = bpy.data.scenes["Building_alpha_epsilon_pi"]
collection = bpy.data.collections["Asset_alpha_epsilon_pi"]
objects = list(collection.all_objects)
mins = [min((o.matrix_world @ Vector(c))[i] for o in objects if o.type == "MESH" for c in o.bound_box) for i in range(3)]
maxs = [max((o.matrix_world @ Vector(c))[i] for o in objects if o.type == "MESH" for c in o.bound_box) for i in range(3)]
target = Vector([(mins[i] + maxs[i]) / 2 for i in range(3)])
camera = scene.camera
if camera is None:
    camera_data = bpy.data.cameras.new("IndependentReviewCamera")
    camera = bpy.data.objects.new("IndependentReviewCamera", camera_data)
    scene.collection.objects.link(camera)
    scene.camera = camera
camera.data.lens = 50
camera.data.clip_end = 500
scene.render.resolution_x = 1000
scene.render.resolution_y = 750
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
for label, offset in [
    ("front", Vector((0, -65, 25))),
    ("east", Vector((65, -3, 24))),
    ("west", Vector((-65, -3, 24))),
    ("rear", Vector((0, 65, 25))),
]:
    camera.location = target + offset
    direction = target - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = str(out / f"{label}_review.png")
    bpy.ops.render.render(write_still=True)
print({"renders": [str(out / f"{v}_review.png") for v in ("front", "east", "west", "rear")], "target": list(target)})
