import bpy,json
from pathlib import Path
from mathutils import Vector
D=Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap/audit/complete_cl50'); c=bpy.data.collections['Asset_class_of_1950'];o=[]
for x in c.all_objects:
 if x.type=='MESH':
  b=[x.matrix_world@Vector(p) for p in x.bound_box];o.append(dict(name=x.name,min=[min(p[i] for p in b) for i in range(3)],max=[max(p[i] for p in b) for i in range(3)]))
(D/'inspection.json').write_text(json.dumps(o,indent=2))
print([(x['name'],x['min'],x['max']) for x in o if any(y in x['name'] for y in ['Floor','Stage','Riser_1','Seat_1_0','GIS','Entrance'])])
