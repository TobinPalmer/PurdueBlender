import bpy
from mathutils import Vector
for n in ['HAAS_Brick_Wall_East','HAAS_Photo_Entrance_Limestone_Facade','HAAS_R6_EastFacade_Inlaid_Brick_Rings']:
 o=bpy.data.objects[n];pts=[o.matrix_world@Vector(v.co) for v in o.data.vertices];print(n,'loc',tuple(o.location),'rot',tuple(o.rotation_euler),'scale',tuple(o.scale),'worldx',min(p.x for p in pts),max(p.x for p in pts),'localx',min(v.co.x for v in o.data.vertices),max(v.co.x for v in o.data.vertices))
