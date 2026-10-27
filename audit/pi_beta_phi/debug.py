import bpy,json
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\massing_house_301838781_891384f.blend')
for n in ['PiPhi_interior_floor_1','PiPhi_dining_table_0','PiPhi_room_partition_0_-1_0','PiPhi_lounge_rug']:
 o=bpy.data.objects.get(n); print(n, o.location[:] if o else None, o.dimensions[:] if o else None, o.hide_render if o else None, list(o.users_collection[0].name for _ in [0]) if o else None)
print('count',len(bpy.data.objects), 'asset',len(bpy.data.collections['Asset_massing_house_301838781_891384f'].objects))
