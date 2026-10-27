import bpy, json
from mathutils import Vector
p=bpy.data.filepath
print('FILE',p,'scene',bpy.context.scene.name)
for c in bpy.data.collections:
 if 'massing_house_860826641_2c90f97' in c.name or 'House_860826641' in c.name:
  print('COLLECTION',c.name)
for o in bpy.data.objects:
 if o.name=='House_860826641':
  dg=bpy.context.evaluated_depsgraph_get(); e=o.evaluated_get(dg); mesh=e.to_mesh()
  verts=[o.matrix_world @ v.co for v in mesh.vertices]
  print('OBJECT',o.name,o.type,'verts',len(mesh.vertices),'faces',len(mesh.polygons),'loc',list(o.location),'dim',list(o.dimensions),'materials',[m.name for m in o.data.materials])
  print('BOUNDS',[[min(v[i] for v in verts),max(v[i] for v in verts)] for i in range(3)])
  e.to_mesh_clear()
print('all mats',[(m.name,m.diffuse_color[:]) for m in bpy.data.materials])
