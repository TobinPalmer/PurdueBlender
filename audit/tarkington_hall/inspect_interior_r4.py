import bpy
from mathutils import Vector
for o in sorted(bpy.data.objects,key=lambda o:o.name):
 if o.type!='MESH': continue
 if o.name.startswith(('Tark_Lobby','Tark_PetesZa','Tark_SharkTank','Tark_Commons_Central','Tark_East_Courtyard','Tark_West_Courtyard','Tark_North_Entrance','Tark_South_Entrance')):
  c=o.matrix_world.translation
  if -25<c.x<20 and -25<c.y<38:
   print(o.name,'p',tuple(round(x,1) for x in c),'dim',tuple(round(x,1) for x in o.dimensions),'mat',[m.name if m else None for m in o.data.materials])
