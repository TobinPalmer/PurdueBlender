import bpy
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\krach_leadership_center.blend'
bpy.ops.wm.open_mainfile(filepath=p)
a=bpy.data.collections['Asset_krach_leadership_center']
print('PLACEMENT',repr(a.get('placement_origin_xy_m')),type(a.get('placement_origin_xy_m')))
print('CAMPUS',repr(a.get('campus_origin_m')),type(a.get('campus_origin_m')))
print('PROPS',list(a.keys()))
