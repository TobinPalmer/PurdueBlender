import bpy
bpy.ops.wm.open_mainfile(filepath=r'modular/site/engineering_mall_groundwork_patch.blend')
items=sorted([o for o in bpy.data.objects if o.name.startswith('Plant_')],key=lambda o:o.get('preview_view_distance_m',999))
for o in items[:50]:
 print(o.name, round(o.get('reference_crown_x',9),2), round(o.get('reference_crown_y',9),2), round(o.get('preview_view_distance_m',999),1), o.get('common_name'))
