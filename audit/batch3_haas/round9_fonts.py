import bpy
from mathutils import Vector
C=bpy.data.collections['Asset_felix_haas_hall']
for o in C.objects:
 if o.type=='FONT': print(o.name,repr(o.data.body),tuple(round(x,2) for x in o.location),tuple(round(x,2) for x in o.dimensions))
