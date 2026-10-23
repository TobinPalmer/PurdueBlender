import bpy,json
from mathutils import Vector
for name in ['HAAS_Photo_Main_Hipped_Roof','HAAS_Photo_Entrance_Hipped_Roof']:
 o=bpy.data.objects[name];r=[]
 for p in o.data.polygons:
  n=o.matrix_world.to_3x3()@p.normal;c=o.matrix_world@p.center
  r.append({'face':p.index,'normal':[round(x,3) for x in n],'center':[round(x,2) for x in c],'material':p.material_index,'smooth':p.use_smooth})
 print(name, 'materials',[m.name for m in o.data.materials],'faces',json.dumps(r))
