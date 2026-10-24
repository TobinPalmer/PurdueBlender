import bpy,json
from mathutils import Vector
from pathlib import Path
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\morgan_j_burke_boilermaker_aquatic_center.blend')
D=[]
for o in bpy.data.objects:
 if any(t in o.name.lower() for t in ['roof','seating','spectator','mezzanine','pool','grandstand','stair']):
  if o.type in {'MESH','CURVE','CAMERA'}:
   D.append({'name':o.name,'type':o.type,'loc':list(o.location),'dims':list(o.dimensions),'mat':[m.name for m in o.data.materials] if hasattr(o.data,'materials') else []})
Path(r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\batchC_boilermaker_aquatic_r1\objects_r3_aquatic.json').write_text(json.dumps(D,indent=2))
