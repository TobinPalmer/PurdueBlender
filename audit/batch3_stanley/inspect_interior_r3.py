import bpy
from mathutils import Vector
p=r'modular/buildings/stanley_coulter_hall.blend';bpy.ops.wm.open_mainfile(filepath=p)
for cn in ['SC_Interior_Shell','SC_Interior_Stairs','SC_Interior_Furniture']:
 c=bpy.data.collections.get(cn)
 if c: print('\n',cn, len(c.objects), [o.name for o in c.objects[:80]])
