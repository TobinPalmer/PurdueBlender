"""Render the saved asset after reopening it in Blender."""
import bpy
import os

root=os.path.abspath(os.path.join(os.path.dirname(__file__),"..",".."))
if bpy.data.collections.get("Asset_massing_windsor_halls_80aeb51") is None:
    raise RuntimeError("Windsor collection failed fresh open")
scene=bpy.context.scene
if scene.camera is None:
    raise RuntimeError("Saved Windsor scene has no camera")
scene.render.resolution_x=1500
scene.render.resolution_y=1200
scene.render.resolution_percentage=100
scene.render.filepath=os.path.join(os.path.dirname(__file__),"previews","fresh_open_saved_asset.png")
bpy.ops.render.render(write_still=True)
print("FRESH_OPEN_RENDER",scene.render.filepath)
