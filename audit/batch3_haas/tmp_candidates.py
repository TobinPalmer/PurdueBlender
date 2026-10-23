import bpy
from mathutils import Vector
for n in ['HAAS_Cheek_Wall_South','HAAS_Cheek_Wall_North','HAAS_West_Portico_Canopy','HAAS_Beltcourse2_North']:
 o=bpy.data.objects.get(n)
 if not o:continue
 p=[o.matrix_world@Vector(v) for v in o.bound_box];mi=[min(q[i] for q in p) for i in range(3)];ma=[max(q[i] for q in p) for i in range(3)]
 print(n,[c.name for c in o.users_collection],tuple(round(x,2) for x in mi),tuple(round(x,2) for x in ma),tuple(round(x,2) for x in o.location))
