import bpy, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get(); g=bpy.data.objects['RAWL_SE_Diagonal_CurtainWall_Glass']
def tree(name):
 o=bpy.data.objects[name].evaluated_get(dg); m=o.to_mesh()
 try:return BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons],all_triangles=False)
 finally:o.to_mesh_clear()
trees=[tree(n) for n in ['RAWL_Masonry_Exterior_Walls','RAWL_2026_Plan1086_01_00','RAWL_2026_Plan1086_02_00']]
base=bpy.data.objects['RAWL_1086_R10_Schematic_Projection_Surface_01'].matrix_world.translation.copy(); tangent=Vector((math.cos(-1.27),math.sin(-1.27),0))
def visible(off):
 t=base+tangent*off; good=[]
 for p in g.data.polygons:
  c=sum((g.matrix_world@g.data.vertices[i].co for i in p.vertices),Vector())/4; n=(g.matrix_world.to_3x3()@p.normal).normalized(); s=c+n*.02; d=t-s
  if all(tree.ray_cast(s,d.normalized(),d.length)[0] is None for tree in trees):good.append(p.index)
 return set(good)
for a,b in [(-.8,.15),(-.9,.1),(-1,.0),(-.75,.25),(-1.2,-.2)]:
 s=visible(a)&visible(b); print(a,b,len(s),sorted(s)[:20])
