import bpy
for o in bpy.data.objects:
 c=o.matrix_world.translation
 if o.type=='MESH' and (o.name.startswith(('Tark_Dorm','Tark_Room119','Tark_Room118','Tark_Typical','Tark_Corridor')) or (-47<c.x<-30 and -38<c.y<-22 and c.z<4)):
  print(o.name,tuple(round(v,2) for v in c),tuple(round(v,2) for v in o.dimensions))
