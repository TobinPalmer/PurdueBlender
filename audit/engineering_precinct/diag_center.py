import bpy
bpy.ops.wm.open_mainfile(filepath=r'modular/site/engineering_mall_groundwork_patch.blend')
for o in bpy.data.objects:
 if o.name.startswith('Plant_'):
  x=o.get('reference_crown_x',9);y=o.get('reference_crown_y',9)
  if .54<=x<=.78 and .32<=y<=.56:
   print(o.name,round(x,3),round(y,3),'base',round(o.get('reference_frame_x',0),3),round(o.get('reference_frame_y',0),3),'dist',o.get('preview_view_distance_m'),'diam',o.get('canopy_diameter_m'),'vis',round(o.get('visual_crown_scale_xy',0),2),'h',o.get('height_m'),'dbh',o.get('inventory_dbh_in'),'spread',o.get('inventory_spread_ft'))
