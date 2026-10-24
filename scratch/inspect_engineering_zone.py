import bpy, math
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\purdue_campus_master.blend'
bpy.ops.wm.open_mainfile(filepath=p)
for o in bpy.data.objects:
 x,y,z=o.location
 if abs(x)<100 and 115<y<230:
  print(o.name, o.type, tuple(round(v,1) for v in o.location), o.get('source_id',''), o.users_collection[0].name if o.users_collection else '')
