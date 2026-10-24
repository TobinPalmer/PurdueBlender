import bpy, json, os
path=r'C:/Users/Tobin/Documents/Blender/PurdueMap/purdue_campus_master.blend'
print('opened_master',bpy.data.filepath)
for o in bpy.data.objects:
 if o and ('lawson' in o.name.lower() or 'lwsn' in o.name.lower()) and ('placement' in o.name.lower() or 'assetroot' in o.name.lower()):
  print('object',o.name,'location',list(o.location),'rotation',list(o.rotation_euler),'scale',list(o.scale),'matrix_world',[list(row) for row in o.matrix_world])
for lib in bpy.data.libraries:
 if 'lawson' in (lib.filepath or '').lower():print('library',lib.filepath,'absolute',bpy.path.abspath(lib.filepath))
