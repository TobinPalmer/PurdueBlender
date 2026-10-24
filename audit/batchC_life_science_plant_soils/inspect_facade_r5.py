import bpy
from mathutils import Vector
f=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\life_science_plant_and_soils_laboratory.blend'
bpy.ops.wm.open_mainfile(filepath=f)
for o in bpy.data.objects:
 if o.type=='MESH' and ('facade bay' in o.name or 'glazing' in o.name) and (o.name.startswith('LSPS | facade') or o.name.startswith('LSPS R')):
  if 'glazing' not in o.name and 'mullion' not in o.name and 'sill' not in o.name: continue
  if o.name.endswith('glazing') or 'facade bay' in o.name:
   cs=[o.matrix_world@Vector(v) for v in o.bound_box]; lo=[min(v[i] for v in cs) for i in range(3)]; hi=[max(v[i] for v in cs) for i in range(3)]
   print(o.name, [round(hi[i]-lo[i],2) for i in range(3)], [m.name for m in o.data.materials])
