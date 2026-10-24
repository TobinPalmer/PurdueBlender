import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\life_science_plant_and_soils_laboratory.blend')
for o in bpy.data.objects:
 if o.type!='MESH': continue
 cs=[o.matrix_world@Vector(v) for v in o.bound_box]; ds=[max(v[i] for v in cs)-min(v[i] for v in cs) for i in range(3)]; ds.sort()
 if 1.2<ds[1]<1.8 and 1.5<ds[2]<2.1 and ds[0]<.2:
  print(o.name,tuple(round(x,2) for x in ds),[m.name if m else None for m in o.data.materials])
