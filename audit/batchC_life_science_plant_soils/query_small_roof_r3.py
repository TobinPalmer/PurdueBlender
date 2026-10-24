import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'modular/buildings/life_science_plant_and_soils_laboratory.blend')
for o in bpy.data.collections['Asset_life_science_plant_and_soils_laboratory'].all_objects:
 if o.type!='MESH': continue
 pts=[o.matrix_world @ Vector(v) for v in o.bound_box]; z0=min(p.z for p in pts);z1=max(p.z for p in pts)
 if z1>12 and o.dimensions.x<2 and o.dimensions.y<2: print(o.name,tuple(round(v,2) for v in o.location),tuple(round(v,2) for v in o.dimensions),round(z0,2),round(z1,2))
