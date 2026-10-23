import bpy,json
from pathlib import Path
from mathutils import Vector
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/potter_engineering.blend');bpy.ops.wm.open_mainfile(filepath=str(P));c=bpy.data.collections['Asset_potter_engineering']
out=[]
for name in ['POTR_Historic2016_Plan51_MergedPartitions','POTR_Historic2016_Plan53_MergedPartitions','POTR_Historic2016_Plan54_MergedPartitions','POTR_Historic2016_Plan55_MergedPartitions','POTR_Interior_Slab_Level_1_EstimatedElevation','POTR_Interior_Slab_Level_2_EstimatedElevation','POTR_Interior_Slab_Level_3_EstimatedElevation']:
 o=bpy.data.objects.get(name)
 if o:
  bb=[o.matrix_world@Vector(v) for v in o.bound_box]
  out.append({'name':name,'bounds':[[min(v[i] for v in bb) for i in range(3)],[max(v[i] for v in bb) for i in range(3)]],'props':{k:o[k] for k in o.keys() if k!='_RNA_UI'}})
print(json.dumps(out,indent=2))
