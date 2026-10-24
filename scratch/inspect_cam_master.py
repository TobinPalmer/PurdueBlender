import bpy
f=r'C:\Users\Tobin\Documents\Blender\PurdueMap\purdue_campus_master.blend'
bpy.ops.wm.open_mainfile(filepath=f)
print('cams',[(o.name,tuple(round(v,2) for v in o.location),tuple(round(v,3) for v in o.rotation_euler)) for o in bpy.data.objects if o.type=='CAMERA'][:20])
for o in bpy.data.objects:
 if any(x in o.name.lower() for x in ['mechanical','msee','fountain','engineering_mall','hampt','forney','armstrong']):
  print(o.name,o.type,tuple(round(v,2) for v in o.location),o.dimensions[:])
