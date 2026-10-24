import bpy, math
bpy.ops.wm.open_mainfile(filepath=r'modular/site/engineering_mall_groundwork_patch.blend')
for o in bpy.data.objects:
 if o.name.startswith('Plant_'):
  x=o.get('reference_crown_x',9); y=o.get('reference_crown_y',9); d=o.get('preview_view_distance_m',999)
  if .34<=x<=.60 and .30<=y<=.62:
   print(o.name, round(x,2), round(y,2), round(d,1), round(o.get('visual_crown_scale_xy',0),2), round(o.get('canopy_diameter_m',0),1), round(o.get('height_m',0),1))
