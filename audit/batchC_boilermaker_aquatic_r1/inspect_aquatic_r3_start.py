import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\morgan_j_burke_boilermaker_aquatic_center.blend')
a=bpy.data.collections['Asset_morgan_j_burke_boilermaker_aquatic_center']
for n in ['AQUA R2 | north entrance dark sign plaque','AQUA R2 | north brick pilaster 1','AQUA R2 | north entry glazed door leaf 1','AQUA | clear-span natatorium | pitched roof planes','AQUA | clear-span natatorium | standing seam roof ribs','AQUA R2 | North Three Quarter Camera','AQUA R2 | Interior Seating Camera','AQUA R2 | schematic east mezzanine gallery']:
 o=bpy.data.objects.get(n)
 if o:
  b=[o.matrix_world@Vector(c) for c in o.bound_box] if o.type=='MESH' else []
  print(n,o.type, 'loc',tuple(round(v,2) for v in o.location),'dim',tuple(round(v,2) for v in o.dimensions),'bound',[[round(min(v[i] for v in b),2),round(max(v[i] for v in b),2)] for i in range(3)] if b else '')
