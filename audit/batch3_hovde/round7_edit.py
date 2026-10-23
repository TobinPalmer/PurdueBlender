import bpy

p = r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/hovde_hall.blend'
bpy.ops.wm.open_mainfile(filepath=p)
# Shift the six supports clear of the three modeled door openings; retain the count and root.
centers = [-5.6, -4.1, -1.7, 1.2, 3.8, 5.6]
for i, y in enumerate(centers, 1):
    for prefix in (
        'HOVD_Classical_Column_', 'HOVD_Column_Base_', 'HOVD_Column_Capital_',
        'HOVD_Column_FluteCollar_Base_', 'HOVD_Column_FluteCollar_Capital_'
    ):
        obj = bpy.data.objects.get(prefix + str(i))
        if obj:
            obj.location.y = y
bpy.ops.wm.save_as_mainfile(filepath=p)
print('Round 7 support centers:', centers)
print('Root transform retained:', tuple(bpy.data.objects['HOVD_Root'].location),
      tuple(bpy.data.objects['HOVD_Root'].rotation_euler))
