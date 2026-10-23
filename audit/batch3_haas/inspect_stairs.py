import bpy
from mathutils import Vector
for n in ['HAAS_Step_Upper_4','HAAS_Step_Upper_5','HAAS_Step_Upper_6']:
 o=bpy.data.objects[n];pts=[o.matrix_world@Vector(v) for v in o.bound_box];print(n,'loc',tuple(o.location),'bounds',[[round(min(p[i] for p in pts),2) for i in range(3)],[round(max(p[i] for p in pts),2) for i in range(3)]])
