import bpy
bpy.ops.wm.open_mainfile(filepath=r'modular/site/engineering_mall_groundwork_patch.blend')
for o in bpy.data.objects:
 if o.name.startswith('Plant_'):
  print(o.name, round(o.get('reference_frame_x',-1),2), round(o.get('reference_frame_y',-1),2), round(o.get('reference_crown_x',-1),2), round(o.get('reference_crown_y',-1),2), round(o.get('visual_crown_scale_xy',0),2), round(o.get('canopy_diameter_m',0),1), round(o.get('height_m',0),1))
