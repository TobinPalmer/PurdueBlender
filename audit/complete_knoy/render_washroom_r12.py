import bpy
from mathutils import Vector
from pathlib import Path
ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap');bpy.ops.wm.open_mainfile(filepath=str(ROOT/'modular/buildings/knoy_hall.blend'))
scene=bpy.context.scene;keep={'KNOY_L2_TypicalPlan_InteriorPartitions'}
for c in (bpy.data.collections['KNOY_TypicalPlan_Doors_L2-L4'],bpy.data.collections['KNOY_TypicalPlan_WashroomFixtures_L2-L4']):
 for o in c.objects:
  if o.name.startswith('KNOY_L2_'):keep.add(o.name)
for o in bpy.data.objects:o.hide_render=o.name not in keep
mat=bpy.data.materials.new('RenderOnly_Washroom_Floor');mat.diffuse_color=(.72,.73,.74,1)
mesh=bpy.data.meshes.new('RenderOnly_Washroom_Floor_Mesh');mesh.from_pydata([(-22,-12,4.46),(-8,-12,4.46),(-8,2,4.46),(-22,2,4.46)],[],[(0,1,2,3)]);mesh.materials.append(mat);plane=bpy.data.objects.new('RenderOnly_Washroom_Floor',mesh);scene.collection.objects.link(plane)
camd=bpy.data.cameras.new('KNOY_R12_Washroom_Cutaway_Camera');cam=bpy.data.objects.new('KNOY_R12_Washroom_Cutaway_Camera',camd);scene.collection.objects.link(cam);target=Vector((-14.4,-8.2,5.2));cam.location=(-7,-15,11.0);cam.rotation_euler=(target-Vector(cam.location)).to_track_quat('-Z','Y').to_euler();camd.type='ORTHO';camd.ortho_scale=10.5;scene.camera=cam
scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=False;scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.display.shading.curvature_ridge_factor=1.2;scene.display.shading.curvature_valley_factor=1.0;scene.display.shading.background_type='WORLD';scene.display.shading.background_color=(.82,.84,.86)
scene.render.resolution_x=1300;scene.render.resolution_y=950;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.filepath=str(ROOT/'audit/complete_knoy/knoy_washroom_cutaway_r12.png')
bpy.ops.render.render(write_still=True);print('Rendered plan-supported washroom cutaway')
