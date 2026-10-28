import bpy, os
from mathutils import Vector
p=r'modular/buildings/massing_house_301841248_fe939c7.blend'; bpy.ops.wm.open_mainfile(filepath=p)
scene=bpy.context.scene; root=bpy.data.collections['Asset_massing_house_301841248_fe939c7']
# Fresh-open assertions before preview-state changes.
assert bpy.data.objects.get('House_301841248') is not None
assert len(bpy.data.objects['House_301841248'].data.vertices)==32
keep={'AXiD_FloorSlab_0_12','Interior_Partition_Lower','Interior_Partition_Lower.001','Interior_CrossWall_Lower','Interior_CrossWall_Lower.001','Interior_GroundDiningTable','Interior_GroundLoungeTable','Interior_GroundLoungeSeat','Interior_Lobby_Rug'}
keep |= {o.name for o in bpy.data.objects if o.name.startswith('Interior_GroundDiningChair')}
for o in bpy.data.objects:
    o.hide_render = o.name not in keep
# Build camera outside asset collection
cx=(-297.6089-274.1079)/2; cy=(241.6119+269.2498)/2
camdata=bpy.data.cameras.new('AXiD_InteriorPlan_Camera'); cam=bpy.data.objects.new('AXiD_InteriorPlan_Camera',camdata); scene.collection.objects.link(cam)
cam.location=(cx-32,cy-24,40); cam.rotation_euler=(Vector((cx,cy,.5))-cam.location).to_track_quat('-Z','Y').to_euler(); camdata.type='ORTHO'; camdata.ortho_scale=43; scene.camera=cam
scene.render.engine='BLENDER_WORKBENCH'; scene.display.shading.light='STUDIO'; scene.display.shading.studio_light='paint.sl'; scene.display.shading.color_type='MATERIAL'; scene.display.shading.show_shadows=True; scene.display.shading.show_cavity=True; scene.display.shading.cavity_type='WORLD'; scene.display.shading.curvature_ridge_factor=1.2; scene.display.shading.curvature_valley_factor=1.1; scene.display.shading.background_type='WORLD'; scene.display.shading.show_specular_highlight=False
scene.render.resolution_x=1500; scene.render.resolution_y=1125; scene.render.resolution_percentage=100; scene.render.image_settings.file_format='PNG'; scene.render.filepath=os.path.abspath(r'audit/alpha_xi_delta_fid788/interior_cutaway_preview.png')
bpy.ops.render.render(write_still=True)
print('FRESH_OPEN_OK',len(scene.objects),'asset_objects',len(root.objects),'visible',sorted(o.name for o in scene.objects if not o.hide_render))
