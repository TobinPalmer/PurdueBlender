import bpy, json
from mathutils import Vector
for obj in bpy.data.objects:
    n=obj.name.lower()
    if not any(k in n for k in ['atrium','roof','1086','ceiling','oculus','penthouse']):
        continue
    if obj.type=='MESH':
        pts=[obj.matrix_world@Vector(c) for c in obj.bound_box]
        bounds=[[round(min(p[i] for p in pts),3),round(max(p[i] for p in pts),3)] for i in range(3)]
    else: bounds=None
    print(obj.name, obj.type, bounds, [s.material.name if s.material else None for s in obj.material_slots[:2]])
