import bpy
bpy.ops.wm.open_mainfile(filepath=r'modular/site/engineering_mall_groundwork_patch.blend')
for o in bpy.data.objects:
 if o.name.startswith('Plant_'):
  x=o.get('reference_crown_x',9);y=o.get('reference_crown_y',9)
  if .42<=x<=.75 and .22<=y<=.58:
   print(o.name,round(x,2),round(y,2),round(o.get('preview_view_distance_m',0),1),round(o.get('canopy_diameter_m',0),1),round(o.get('height_m',0),1),o.get('common_name'))
