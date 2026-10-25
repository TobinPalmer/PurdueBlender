import bpy
from mathutils import Vector
from pathlib import Path
ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap');A=ROOT/'modular/buildings/neil_armstrong_hall.blend';OUT=ROOT/'audit/neil_armstrong_hall_refine/top_without_cantilever.png'
bpy.ops.wm.open_mainfile(filepath=str(A));scene=bpy.context.scene
obj=bpy.data.objects['ARMS_Cantilever_Canopy_Deck'];obj.hide_render=True
scene.render.engine='BLENDER_EEVEE';scene.render.resolution_x=1300;scene.render.resolution_y=850;scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new('topdiag');scene.world.use_nodes=True;next(n for n in scene.world.node_tree.nodes if n.type=='BACKGROUND').inputs['Strength'].default_value=.7
bpy.ops.object.camera_add(location=(0,-5,155));cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=185;cam.rotation_euler=(Vector((0,-5,0))-cam.location).to_track_quat('-Z','Y').to_euler();scene.camera=cam
bpy.ops.object.light_add(type='AREA',location=(0,-40,110));l=bpy.context.object;l.data.energy=80000;l.data.shape='DISK';l.data.size=100;l.rotation_euler=(Vector((0,-5,10))-l.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(OUT);bpy.ops.render.render(write_still=True)
