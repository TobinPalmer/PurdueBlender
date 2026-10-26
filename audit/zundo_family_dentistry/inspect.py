import bpy, json
p=r'modular/buildings/massing_zundo_family_dentistry_f840e2b.blend'
bpy.ops.wm.open_mainfile(filepath=p)
for s in bpy.data.scenes:
 print('SCENE',s.name)
 for o in s.objects:
  print('OBJ',o.name,o.type, 'loc',tuple(o.location),'dims',tuple(o.dimensions))
  if o.type=='MESH':
   print('verts', [tuple(o.matrix_world @ v.co) for v in o.data.vertices])
