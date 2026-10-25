import bpy,collections
from mathutils import Vector
o=bpy.data.objects['LWSN_Foundation_Base']; mw=o.matrix_world
print('mworld', [list(r) for r in mw])
print('vertex z count',collections.Counter(round((mw@v.co).z,3) for v in o.data.vertices))
for p in list(o.data.polygons)[:6]: print([round((mw@o.data.vertices[i].co).z,4) for i in p.vertices])
