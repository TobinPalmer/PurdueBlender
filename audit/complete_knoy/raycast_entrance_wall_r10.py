import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\knoy_hall.blend')
o=bpy.data.objects['KNOY_Exterior_Masonry_Walls'];dg=bpy.context.evaluated_depsgraph_get();ev=o.evaluated_get(dg)
for x in [-5,0,5]:
 for z in [3.5,3.9,4.2]:
  origin=Vector((x,-55,z)); direction=Vector((0,1,0)); hit,loc,norm,fi=ev.ray_cast(origin,direction, distance=20)
  if hit: print(x,z,'loc',tuple(round(c,3) for c in loc),'matindex',ev.data.polygons[fi].material_index, 'mat',o.data.materials[ev.data.polygons[fi].material_index].name)
  else: print(x,z,'miss')
