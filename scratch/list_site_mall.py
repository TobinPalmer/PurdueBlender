import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\site\campus_site.blend')
for o in bpy.data.objects:
 if any(s in o.name.lower() for s in ['engineering_mall','engfountain','fountain_plaza','engineering_fountain']):
  if o.type=='EMPTY' or o.type=='MESH': print(o.name,o.type,tuple(round(x,2) for x in o.location),tuple(round(x,1) for x in o.dimensions),o.library.filepath if o.library else '')
