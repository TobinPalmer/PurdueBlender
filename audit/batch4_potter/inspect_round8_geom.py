import bpy,json
from pathlib import Path
from mathutils import Vector
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/potter_engineering.blend');bpy.ops.wm.open_mainfile(filepath=str(P));c=bpy.data.collections['Asset_potter_engineering'];names=[o.name for o in c.all_objects if any(q in o.name for q in ('StairCore3','Slab_Level','Handrail','4S04','Room401'))];print('\n'.join(names))
for o in c.all_objects:
 if o.name.startswith('POTR_2016_StairCore3_Level0_Flight') or o.name.startswith('POTR_2016_StairCore3_Level0_Handrails') or o.name=='POTR_Interior_Slab_Level_1_EstimatedElevation':
  bb=[o.matrix_world@Vector(co) for co in o.bound_box];print(o.name,[tuple(round(v,3) for v in (min(p[i] for p in bb),max(p[i] for p in bb))) for i in range(3)],len(o.data.vertices) if o.type=='MESH' else 'curve')
