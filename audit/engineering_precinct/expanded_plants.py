import bpy
bpy.ops.wm.open_mainfile(filepath=r'modular/site/engineering_mall_groundwork_patch.blend')
for o in bpy.data.objects:
 if o.name.startswith('Plant_') and o.get('visual_crown_scale_xy',0)>1:
  print(o.name,'XY',round(o.location.x,1),round(o.location.y,1),'frame',o.get('reference_crown_x'),o.get('reference_crown_y'),'scale',round(o.get('visual_crown_scale_xy'),2),'spread',o.get('canopy_diameter_m'),'h',o.get('height_m'),'dist',o.get('preview_view_distance_m'))
