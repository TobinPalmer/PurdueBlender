import bpy
from mathutils import Vector
from pathlib import Path
ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap')
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'modular/buildings/knoy_hall.blend'))
scene=bpy.context.scene
keep={'KNOY_L2_TypicalPlan_InteriorPartitions','KNOY_Stair_L2_L3_Core_A','KNOY_Stair_L2_L3_Core_B','KNOY_Stair_L2_L3_Core_C'}
for o in bpy.data.collections['Asset_knoy_hall'].all_objects:
 if o.name.startswith('KNOY_L2_TypicalPlan_Door_'):keep.add(o.name)
for o in bpy.data.objects:o.hide_render=o.name not in keep
# Add neutral temporary floor datum beneath the illustrative partition/door geometry.
mesh=bpy.data.meshes.new('RenderOnly_L2_Floor_Mesh'); mesh.from_pydata([(-45,-50,4.45),(45,-50,4.45),(45,50,4.45),(-45,50,4.45)],[],[(0,1,2,3)]); mesh.update()
floor=bpy.data.objects.new('RenderOnly_L2_Floor',mesh);scene.collection.objects.link(floor)
floor.hide_render=False; floor.data.materials.append(bpy.data.materials.get('KNOY_Interior_Door_Neutral_Estimate'))
camd=bpy.data.cameras.new('KNOY_R11_Interior_Cutaway_Camera');cam=bpy.data.objects.new('KNOY_R11_Interior_Cutaway_Camera',camd);scene.collection.objects.link(cam)
target=Vector((0,0,6.0));cam.location=(42,-68,48);cam.rotation_euler=(target-Vector(cam.location)).to_track_quat('-Z','Y').to_euler();camd.type='ORTHO';camd.ortho_scale=90;scene.camera=cam
scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.display.shading.curvature_ridge_factor=1.2;scene.display.shading.curvature_valley_factor=1.0
scene.display.shading.background_type='WORLD';scene.display.shading.show_specular_highlight=True
scene.render.resolution_x=1600;scene.render.resolution_y=1150;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.filepath=str(ROOT/'audit/complete_knoy/knoy_l2_doors_stairs_spatial_r11.png')
bpy.ops.render.render(write_still=True)
print('Rendered L2 illustrative partitions, source-traced doors, and L2-L3 stair cores')
