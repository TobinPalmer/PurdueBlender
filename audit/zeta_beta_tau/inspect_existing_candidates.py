import bpy, json
from mathutils import Vector
for p in [r'modular/buildings/massing_house_301841332_9b3bd1f.blend',r'modular/buildings/massing_house_301841334_fa7e5a2.blend']:
  bpy.ops.wm.open_mainfile(filepath=p)
  print('FILE',p)
  for s in bpy.data.scenes:
    print('SCENE',s.name)
    for c in s.collection.children:
      print('COLLECTION',c.name)
      for o in c.objects:
        if o.type=='MESH':
          pts=[o.matrix_world@v.co for v in o.data.vertices]
          print('OBJECT',o.name,'verts',len(pts),'faces',len(o.data.polygons),'bounds',[[min(v[i] for v in pts),max(v[i] for v in pts)] for i in range(3)])
          # print z=0 profile
          base=[tuple(round(v[i],3) for i in range(2)) for v in pts if abs(v.z)<.001]
          print('BASE',base[:100])
