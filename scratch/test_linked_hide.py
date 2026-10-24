import bpy
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\purdue_campus_master.blend')
for name in ['Engineering_Mall_Central_Concourse','Engineering_Mall_Fountain_Plaza','EngFountain_Aerated_Base_Foam_Pool']:
 o=bpy.data.objects.get(name); print(name, bool(o), (o.library.filepath if o and o.library else None), o.hide_render if o else None)
 if o:
  try: o.hide_render=True; print('hidden ok')
  except Exception as e: print('hide error',repr(e))
