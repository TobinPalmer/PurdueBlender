"""Render the saved south entrance detail using its actual procedural materials."""
import bpy
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap');BLEND=ROOT/'modular/buildings/knoy_hall.blend'
bpy.ops.wm.open_mainfile(filepath=str(BLEND));scene=bpy.context.scene
camd=bpy.data.cameras.new('R13_Entry_Material_Camera');cam=bpy.data.objects.new('R13_Entry_Material_Camera',camd);scene.collection.objects.link(cam)
cam.location=(8.0,-55.4,7.0);target=Vector((.76,-46.34,4.25));cam.rotation_euler=(target-Vector(cam.location)).to_track_quat('-Z','Y').to_euler();camd.lens=52;scene.camera=cam
lightd=bpy.data.lights.new('R13_Entry_Material_Key','AREA');light=bpy.data.objects.new('R13_Entry_Material_Key',lightd);scene.collection.objects.link(light);light.location=(-1.5,-52,9.5);lightd.energy=2800;lightd.shape='DISK';lightd.size=7;light.rotation_euler=(target-Vector(light.location)).to_track_quat('-Z','Y').to_euler()
filld=bpy.data.lights.new('R13_Entry_Material_Fill','AREA');fill=bpy.data.objects.new('R13_Entry_Material_Fill',filld);scene.collection.objects.link(fill);fill.location=(6,-50,3.5);filld.energy=800;filld.shape='DISK';filld.size=5;fill.rotation_euler=(target-Vector(fill.location)).to_track_quat('-Z','Y').to_euler()
if scene.world:
    scene.world.use_nodes=True;bg=scene.world.node_tree.nodes.get('Background');bg.inputs['Color'].default_value=(.36,.42,.52,1);bg.inputs['Strength'].default_value=.28
scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True
scene.render.resolution_x=1700;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.view_settings.view_transform='AgX'
out=ROOT/'audit/complete_knoy/knoy_entrance_detail_material_r13.png';scene.render.filepath=str(out);bpy.ops.render.render(write_still=True)
print('Rendered saved entrance geometry/materials only; blend was opened, not saved.')
