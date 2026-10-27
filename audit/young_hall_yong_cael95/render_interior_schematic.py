"""Render the representative (explicitly schematic) interior grouping."""
import bpy
from pathlib import Path
from mathutils import Vector

out=Path(__file__).with_name("preview_interior_schematic.png")
scene=bpy.context.scene
keep=("first modules","corridor modules","vestibule modules","elevator modules",
      "study modules","table modules","lobby modules")
for obj in bpy.data.collections["Asset_massing_young_hall_yong_cae1b95"].objects:
    if obj.type in {"MESH","FONT"}:
        obj.hide_render=not any(s in obj.name for s in keep)
cx,cy,cz=266,-504,1.5
cam_data=bpy.data.cameras.new("YONG interior evidence camera")
cam=bpy.data.objects.new("YONG interior evidence camera",cam_data)
scene.collection.objects.link(cam)
cam.location=(cx+33,cy-17,10)
target=Vector((cx,cy,cz))
cam.rotation_euler=(target-cam.location).to_track_quat("-Z","Y").to_euler()
cam_data.type="ORTHO"; cam_data.ortho_scale=32
old=scene.camera; scene.camera=cam
scene.render.resolution_x=1200; scene.render.resolution_y=800; scene.render.resolution_percentage=100
scene.render.filepath=str(out)
bpy.ops.render.render(write_still=True)
print("INTERIOR_PREVIEW",str(out))
