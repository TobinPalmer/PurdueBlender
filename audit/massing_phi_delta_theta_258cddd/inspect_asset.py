import bpy, json
from mathutils import Vector
p=r'modular/buildings/massing_phi_delta_theta_258cddd.blend'
bpy.ops.wm.open_mainfile(filepath=p)
print('SCENE', [(s.name, len(s.objects)) for s in bpy.data.scenes])
print('COLLECTIONS', [(c.name, len(c.objects), len(c.children)) for c in bpy.data.collections])
for o in bpy.data.objects:
    print('OBJECT', o.name, o.type, tuple(round(x,4) for x in o.location), tuple(round(x,4) for x in o.dimensions), 'rot', tuple(round(x,5) for x in o.rotation_euler))
    if o.type == 'MESH':
        w=[o.matrix_world @ v.co for v in o.data.vertices]
        print('MESH_VERTS',len(w),'FACES',len(o.data.polygons),'BOUNDS',[[min(v[i] for v in w),max(v[i] for v in w)] for i in range(3)])
        print('SAMPLE', [tuple(round(x,4) for x in v) for v in w[:30]])
