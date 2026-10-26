import bpy,json
from mathutils import Vector
for name in ['Beering_Purdue_Red_Brick','Beering_Roof_Membrane','Indiana_Bedford_Limestone','Beering_Solar_Ribbon_Glass']:
 m=bpy.data.materials.get(name)
 print('\nMAT',name,'users',m.users,'diffuse',list(m.diffuse_color))
 if m and m.use_nodes:
  for n in m.node_tree.nodes:
   if n.type=='BSDF_PRINCIPLED':
    print('PRINC',[(x.name,tuple(x.default_value) if hasattr(x.default_value,'__len__') else x.default_value) for x in n.inputs if x.name in ['Base Color','Metallic','Roughness','Alpha','IOR']])
for prefix in ['Tark_Roof_HVAC','Tark_Roof_Penthouse','Tark_NW_Wing_Roof','Tark_Dorm_Room','Tark_Dorm_Bed','Tark_Dorm_Desk','Tark_PetesZa','Tark_SharkTank','Tark_Lobby']:
 arr=[o for o in bpy.data.objects if o.name.startswith(prefix)]
 if arr:
  b=[]
  for o in arr:
   if o.type=='MESH':
    vs=[o.matrix_world@Vector(v) for v in o.bound_box]
    b.append([min(v.x for v in vs),max(v.x for v in vs),min(v.y for v in vs),max(v.y for v in vs),min(v.z for v in vs),max(v.z for v in vs)])
  print('GROUP',prefix,'n',len(arr),'bounds',[[min(v[i] for v in b),max(v[i] for v in b)] for i in range(6)] if b else None,'names',[o.name for o in arr[:8]])
