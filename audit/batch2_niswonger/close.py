import bpy
for o in bpy.data.objects:
 if o.name.startswith('NISW_ClerestoryClosure'):
  for v in o.data.vertices:
   if abs(v.co.z-7.35)<.01:v.co.z=4.6
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
