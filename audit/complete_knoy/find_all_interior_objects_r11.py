import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\knoy_hall.blend')
print('OBJECTS',len(bpy.data.objects))
for o in sorted(bpy.data.objects,key=lambda x:x.name):
 if 'partition' in o.name.lower() or 'stair' in o.name.lower() or 'elev' in o.name.lower() or 'door' in o.name.lower():print(o.name,o.type,o.users_collection[0].name if o.users_collection else 'none')
