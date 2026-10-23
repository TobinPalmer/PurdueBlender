import bpy
from mathutils import Vector
c=bpy.data.collections['Asset_felix_haas_hall']
for o in c.objects:
    pts=[o.matrix_world@Vector(v) for v in o.bound_box]
    if not pts: continue
    mn=[min(p[i] for p in pts) for i in range(3)];mx=[max(p[i] for p in pts) for i in range(3)]
    if mn[0]>12.4 and mx[0]<13.6 and min(abs((mn[1]+mx[1])/2-y) for y in [-7.65,7.65])<2.1 and mx[2]<6:
        print(o.name,'bounds',[[round(x,2) for x in mn],[round(x,2) for x in mx]],'mat',[m.name if m else None for m in getattr(o.data,'materials',[])])
