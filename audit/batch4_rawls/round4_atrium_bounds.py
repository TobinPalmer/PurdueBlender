import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='modular/buildings/rawls_hall.blend')
for n in ['RAWL_Atrium_Mezzanine_Balustrades','RAWL_Atrium_Structural_Columns','RAWL_R2_Atrium_Railwork_EvidenceInformed']:
 o=bpy.data.objects[n];vs=[o.matrix_world@Vector(v) for v in o.bound_box];print(n,[[round(min(v[i] for v in vs),2),round(max(v[i] for v in vs),2)] for i in range(3)])
