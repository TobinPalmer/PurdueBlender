import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get(); g=bpy.data.objects['RAWL_SE_Diagonal_CurtainWall_Glass']
def tree(name):
 o=bpy.data.objects[name].evaluated_get(dg); m=o.to_mesh()
 try:return BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons],all_triangles=False)
 finally:o.to_mesh_clear()
trees=[tree(n) for n in ['RAWL_Masonry_Exterior_Walls','RAWL_2026_Plan1086_01_00','RAWL_2026_Plan1086_02_00']]
for name in ['RAWL_1086_R10_Schematic_Projection_Surface_01','RAWL_1086_R10_Schematic_Projection_Surface_02','RAWL_1086_R10_Schematic_Lectern_Top']:
 t=bpy.data.objects[name].matrix_world.translation; print('\n',name,tuple(round(x,2) for x in t)); good=[]
 for p in g.data.polygons:
  c=sum((g.matrix_world@g.data.vertices[i].co for i in p.vertices),Vector())/4; n=(g.matrix_world.to_3x3()@p.normal).normalized(); s=c+n*.02; d=t-s
  if all(tree.ray_cast(s,d.normalized(),d.length)[0] is None for tree in trees):good.append(p.index)
 print('clear panes',good)

