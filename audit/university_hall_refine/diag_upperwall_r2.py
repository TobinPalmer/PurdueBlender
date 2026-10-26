import bpy
for o in bpy.data.objects:
 if o.type!='MESH': continue
 p=o.matrix_world.translation
 if p.z>=10 and p.z<13 and o.dimensions.x>1 and o.dimensions.y>1:
  print(o.name,tuple(round(v,1) for v in p),tuple(round(v,1) for v in o.dimensions),[m.name for m in o.data.materials])
