import bpy
from mathutils import Vector
for obj in bpy.data.objects:
    if obj.type!='MESH': continue
    pts=[obj.matrix_world@Vector(c) for c in obj.bound_box]
    b=[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]
    if b[0][1]>=18 and b[0][0]<=45 and b[1][1]>=-11 and b[1][0]<=8 and b[2][1]>=2.5 and b[2][0]<=5.5:
        print(obj.name, 'bounds', [[round(v,2) for v in a] for a in b], 'dims', [round(d,2) for d in obj.dimensions], 'material', [s.material.name if s.material else None for s in obj.material_slots])
