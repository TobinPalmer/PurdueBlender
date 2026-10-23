import bpy,json
from pathlib import Path
from mathutils import Vector
P=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/modular/buildings/potter_engineering.blend');bpy.ops.wm.open_mainfile(filepath=str(P));o=bpy.data.objects['POTR_2016_StairCore3_Level3_Flight'];rows=[]
for p in o.data.polygons:
 if p.normal.z>.99 and p.area>.08:
  vs=[o.data.vertices[k].co for k in p.vertices];rows.append({'z':round(sum(v.z for v in vs)/len(vs),4),'x':round(sum(v.x for v in vs)/len(vs),3),'y':round(sum(v.y for v in vs)/len(vs),3),'area':round(p.area,3)})
print(json.dumps(sorted(rows,key=lambda r:r['z']),indent=2))
