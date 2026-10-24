import bpy
bpy.ops.wm.open_mainfile(filepath=r'modular/site/engineering_mall_groundwork_patch.blend')
for o in bpy.data.objects:
 if o.name.startswith('Plant_'):
  x=o.get('reference_crown_x',9); y=o.get('reference_crown_y',9)
  if .05<=x<=.48 and .22<=y<=.65:
   print(o.name,'xy',round(o.location.x,1),round(o.location.y,1),'scr',round(x,2),round(y,2),'dist',round(o.get('preview_view_distance_m',0),1),'scale',round(o.get('visual_crown_scale_xy',0),2),'spread',round(o.get('canopy_diameter_m',0),1),'h',round(o.get('height_m',0),1),o.get('common_name'))
