import bpy
from pathlib import Path
ROOT=Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap');bpy.ops.wm.open_mainfile(filepath=str(ROOT/'modular/buildings/knoy_hall.blend'))
scene=bpy.context.scene;keep={'KNOY_L2_TypicalPlan_InteriorPartitions'}
for c in (bpy.data.collections['KNOY_TypicalPlan_Doors_L2-L4'],bpy.data.collections['KNOY_TypicalPlan_WashroomFixtures_L2-L4']):
 for o in c.objects:
  if o.name.startswith('KNOY_L2_'):keep.add(o.name)
for o in bpy.data.objects:o.hide_render=o.name not in keep
wall=bpy.data.objects['KNOY_L2_TypicalPlan_InteriorPartitions'];wall.color=(.92,.92,.92,1)
for o in bpy.data.collections['KNOY_TypicalPlan_Doors_L2-L4'].objects:
 if o.name.startswith('KNOY_L2_'):o.color=(.12,.15,.17,1)
for o in bpy.data.collections['KNOY_TypicalPlan_WashroomFixtures_L2-L4'].objects:
 if o.name.startswith('KNOY_L2_'):o.color=(1,.98,.91,1)
floor_mat=bpy.data.materials.new('RenderOnly_L2_Floor_Dark');floor_mat.diffuse_color=(.17,.18,.19,1)
mesh=bpy.data.meshes.new('RenderOnly_L2_Floor_Mesh');mesh.from_pydata([(-45,-55,4.45),(45,-55,4.45),(45,55,4.45),(-45,55,4.45)],[],[(0,1,2,3)]);mesh.materials.append(floor_mat);plane=bpy.data.objects.new('RenderOnly_L2_Floor',mesh);scene.collection.objects.link(plane);plane.color=(.15,.16,.18,1)
camd=bpy.data.cameras.new('KNOY_R12_TopPlan_Camera');cam=bpy.data.objects.new('KNOY_R12_TopPlan_Camera',camd);scene.collection.objects.link(cam);cam.location=(0,0,70);cam.rotation_euler=(0,0,0);camd.type='ORTHO';camd.ortho_scale=75;scene.camera=cam
scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.color_type='OBJECT';scene.display.shading.show_shadows=False;scene.display.shading.show_cavity=False;scene.display.shading.background_type='WORLD';scene.display.shading.background_color=(.93,.94,.95)
scene.render.resolution_x=1100;scene.render.resolution_y=1500;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.filepath=str(ROOT/'audit/complete_knoy/knoy_l2_typical_plan_rooms_r12.png')
bpy.ops.render.render(write_still=True);print('Rendered high-contrast top-down typical plan review')
