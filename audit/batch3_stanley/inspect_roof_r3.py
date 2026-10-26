import bpy
from mathutils import Vector
p=r'modular/buildings/stanley_coulter_hall.blend';bpy.ops.wm.open_mainfile(filepath=p)
for o in bpy.data.collections['SC_Roof_and_Dormers'].objects:
 if o.type=='MESH' and not o.name.startswith('SC_Dormer') and not o.name.startswith('SC_Chimney'):
  pts=[o.matrix_world@Vector(c) for c in o.bound_box];lo=[min(v[i] for v in pts) for i in range(3)];hi=[max(v[i] for v in pts) for i in range(3)];print(o.name,[round(x,2) for x in lo],[round(x,2) for x in hi])
for o in bpy.data.collections['SC_Exterior_Structure'].objects:
 if 'Cornice' in o.name or 'Parapet' in o.name or 'Roofline' in o.name or 'Band' in o.name:
  pts=[o.matrix_world@Vector(c) for c in o.bound_box];print('EXTERIOR',o.name,[round(min(v[i] for v in pts),2) for i in range(3)],[round(max(v[i] for v in pts),2) for i in range(3)])
