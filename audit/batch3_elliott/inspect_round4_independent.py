import bpy, json
from mathutils import Vector
p=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\elliott_hall_of_music.blend'
bpy.ops.wm.open_mainfile(filepath=p)
sc=bpy.context.scene
col=bpy.data.collections.get('ELLIOTT_HALL_OF_MUSIC_EXPORT') or next((c for c in bpy.data.collections if 'ELLIOTT' in c.name.upper()),None)
objs=list(col.all_objects) if col else list(sc.objects)
print('REOPEN', bpy.data.filepath, 'collection', col.name if col else None, 'objects',len(objs))
for o in objs:
 if any(k in o.name.lower() for k in ['access','bridge','walkway','door','opening','seat','roof','flytower','shell','wall']):
  print('OBJ',o.name, o.type, list(o.dimensions), list(o.location), [m.name for m in o.data.materials] if o.type=='MESH' else '')
print('COLLECTIONS',[c.name for c in bpy.data.collections])
print('SCENE OBJECTS',len(sc.objects))
