import bpy,json
from mathutils import Vector
for o in bpy.data.objects:
 if o.type!='MESH': continue
 c=o.matrix_world.translation
 if (-49<c.x<-20 and 16<c.y<65) or (14<c.x<42 and 16<c.y<65) or (-49<c.x<-20 and -55<c.y<-6) or (14<c.x<42 and -55<c.y<-6):
  if not (o.name.startswith('Tark_Win_') or o.name.startswith('Tark_Sill_')):
   print(o.name, tuple(round(v,1) for v in c), tuple(round(v,1) for v in o.dimensions))
