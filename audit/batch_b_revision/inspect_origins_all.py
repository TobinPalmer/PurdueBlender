import bpy
for p in ['horticulture_building','ford_dining_court','flex_lab','heine_pharmacy','ray_w_herrick_laboratories','brees_student_athletic_academic_center']:
 f=rf'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\{p}.blend'; bpy.ops.wm.open_mainfile(filepath=f)
 a=bpy.data.collections['Asset_'+p]
 print(p,'placement',[float(x) for x in a.get('placement_origin_xy_m')],'campus',repr(a.get('campus_origin_m')),'loc',repr(a.get('origin_xy_m')))
