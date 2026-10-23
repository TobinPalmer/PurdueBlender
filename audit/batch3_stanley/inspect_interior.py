import bpy
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\stanley_coulter_hall.blend'; bpy.ops.wm.open_mainfile(filepath=p)
for c in bpy.data.collections:
 print('COL',c.name,len(c.objects),len(c.all_objects))
for n in ['Cam_SC_06_Interior_Schematic','SC_Interior_Shell']:
 o=bpy.data.objects.get(n)
 if o and o.type=='CAMERA': print('CAM',o.location,tuple(o.rotation_euler),o.data.ortho_scale,o.data.lens)
if bpy.data.collections.get('SC_Interior_Shell'):
 c=bpy.data.collections['SC_Interior_Shell'];
 for o in list(c.objects)[:45]: print('INT',o.name,o.type)
