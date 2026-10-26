"""Render the conceptual program diagram in a fresh Blender process."""
import bpy
from pathlib import Path
from mathutils import Vector

out=Path(__file__).resolve().parent/"preview_schematic_interior.png"
scene=bpy.data.scenes.get("Building_massing_honors_college_and_residences_north_3de3b7c_SchematicInterior_NOT_AS_BUILT")
assert scene is not None
scene.render.engine="BLENDER_EEVEE"
scene.render.resolution_x=1000
scene.render.resolution_y=1000
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.view_settings.view_transform="AgX"
world=bpy.data.worlds.new("Schematic Interior neutral world")
world.use_nodes=True
world.node_tree.nodes["Background"].inputs["Color"].default_value=(.52,.58,.68,1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value=.6
scene.world=world
camdata=bpy.data.cameras.new("SchematicInteriorCamera")
cam=bpy.data.objects.new("SchematicInteriorCamera",camdata)
scene.collection.objects.link(cam)
cam.location=(0,-58,82)
target=Vector((0,0,0))
cam.rotation_euler=(target-cam.location).to_track_quat("-Z","Y").to_euler()
camdata.type="ORTHO"
camdata.ortho_scale=78
scene.camera=cam
lightdata=bpy.data.lights.new("SchematicInteriorArea","AREA")
lightdata.energy=18000
lightdata.shape="DISK"
lightdata.size=38
light=bpy.data.objects.new("SchematicInteriorArea",lightdata)
scene.collection.objects.link(light)
light.location=(-20,-22,45)
light.rotation_euler=(Vector((0,0,0))-light.location).to_track_quat("-Z","Y").to_euler()
scene.render.filepath=str(out)
bpy.context.window.scene=scene
bpy.ops.render.render(write_still=True)
print("SCHEMATIC_RENDER",out)
