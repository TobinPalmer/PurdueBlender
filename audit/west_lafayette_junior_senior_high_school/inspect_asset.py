import bpy, json
for s in bpy.data.scenes:
 print('SCENE',s.name)
 for c in s.collection.children:
  print('COLLECTION',c.name)
  for o in c.objects:
   print('OBJECT',o.name,o.type,'loc',tuple(o.location),'rot',tuple(o.rotation_euler),'scale',tuple(o.scale),'verts',len(o.data.vertices) if o.type=='MESH' else '')
   if o.type=='MESH':
    pts=[o.matrix_world @ v.co for v in o.data.vertices]
    print('BOUNDS',[(min(p[i] for p in pts),max(p[i] for p in pts)) for i in range(3)])
    print('VERTS',[(round(v.co.x,3),round(v.co.y,3),round(v.co.z,3)) for v in o.data.vertices[:100]])
