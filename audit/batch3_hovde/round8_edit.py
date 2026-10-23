import bpy

p = r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/hovde_hall.blend'
bpy.ops.wm.open_mainfile(filepath=p)

# Preserve the four outer supports, remove the two inner ones that sat in the door bays.
for i, y in {1: -5.6, 2: -4.35, 5: 4.05, 6: 5.35}.items():
    for prefix in ('HOVD_Classical_Column_', 'HOVD_Column_Base_', 'HOVD_Column_Capital_',
                   'HOVD_Column_FluteCollar_Base_', 'HOVD_Column_FluteCollar_Capital_'):
        obj = bpy.data.objects.get(prefix + str(i))
        if obj:
            obj.location.y = y
for i in (3, 4):
    for prefix in ('HOVD_Classical_Column_', 'HOVD_Column_Base_', 'HOVD_Column_Capital_',
                   'HOVD_Column_FluteCollar_Base_', 'HOVD_Column_FluteCollar_Capital_'):
        obj = bpy.data.objects.get(prefix + str(i))
        if obj:
            bpy.data.objects.remove(obj, do_unlink=True)

# Reduce the stone framing around the doors and shallow pediment span while retaining a supportable span.
for name, factor in [('HOVD_Portico_Entablature', .88), ('HOVD_Portico_Cornice', .88),
                     ('HOVD_Portico_Pediment_Base', .86), ('HOVD_Portico_Pediment_Crown', .86)]:
    bpy.data.objects[name].scale.x *= factor
# Add a little rise to the triangular face so it reads as a pediment, not a broad horizontal cap.
bpy.data.objects['HOVD_Portico_Pediment_Base'].scale.z *= 1.28
bpy.data.objects['HOVD_Portico_Pediment_Crown'].scale.z *= 1.12

bpy.ops.wm.save_as_mainfile(filepath=p)
print('Round 8: four outer columns remain, inner door-bay supports removed, pediment narrowed and slightly raised.')
print('Root retained:', tuple(bpy.data.objects['HOVD_Root'].location),
      tuple(bpy.data.objects['HOVD_Root'].rotation_euler))
