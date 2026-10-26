import bpy, json
from mathutils import Vector
p=r'modular/buildings/massing_hi_vine_dbdf0c5.blend'
bpy.ops.wm.open_mainfile(filepath=p)
for s in bpy.data.scenes:
 print('SCENE',s.name)
 for c in s.collection.children:
  print('COLLECTION',c.name)
 for o in s.objects:
  if o.type=='MESH':
   pts=[o.matrix_world @ Vector(v) for v in o.bound_box]
   print('OBJECT',o.name,'type',o.type,'verts',len(o.data.vertices),'faces',len(o.data.polygons),'dims',list(o.dimensions),'bounds',[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)],'mods',len(o.modifiers))
