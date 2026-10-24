import bpy,json
from mathutils import Vector
rows=[]
for o in bpy.data.objects:
 if o.name.startswith('KRCH | schematic level slab'):
  level=o.get('level_top_m'); origin=Vector((-19.45,-9.3,level+0.5)); hit=o.ray_cast(o.matrix_world.inverted()@origin,o.matrix_world.inverted().to_3x3()@Vector((0,0,-1)))
  origin2=Vector((0,0,level+0.5)); hit2=o.ray_cast(o.matrix_world.inverted()@origin2,o.matrix_world.inverted().to_3x3()@Vector((0,0,-1)))
  rows.append({'name':o.name,'level':level,'hole_hit':hit[0],'hole_location':list(hit[1]),'solid_hit':hit2[0]})
print(json.dumps(rows,indent=2))
