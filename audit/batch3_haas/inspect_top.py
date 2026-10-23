import bpy,bmesh
from mathutils import Vector
for n in ['HAAS_Corrected_GIS_Wall_Envelope','HAAS_Photo_Main_Hipped_Roof','HAAS_Photo_Entrance_Hipped_Roof']:
 o=bpy.data.objects.get(n)
 print('\n',n,'mesh',len(o.data.vertices),len(o.data.polygons))
 for p in o.data.polygons:
  co=[o.matrix_world@o.data.vertices[i].co for i in p.vertices]
  if p.normal.z>.8 or all(v.z>11.3 for v in co):
   print('face',p.index,'normal',tuple(round(x,3) for x in (o.matrix_world.to_3x3()@p.normal)),'z',[round(v.z,3) for v in co],'area',round(p.area,2),'mat',p.material_index)
