import bpy,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get(); g=bpy.data.objects['RAWL_SE_Diagonal_CurtainWall_Glass']
def tree(n):
 o=bpy.data.objects[n].evaluated_get(dg); m=o.to_mesh()
 try:return BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons],all_triangles=False)
 finally:o.to_mesh_clear()
trees=[tree(n) for n in ['RAWL_Masonry_Exterior_Walls','RAWL_2026_Plan1086_01_00','RAWL_2026_Plan1086_02_00']]
p=g.data.polygons[1]; c=sum((g.matrix_world@g.data.vertices[i].co for i in p.vertices),Vector())/len(p.vertices); n=(g.matrix_world.to_3x3()@p.normal).normalized(); s=c+n*.02
base=bpy.data.objects['RAWL_1086_R10_Schematic_Projection_Surface_01'].matrix_world.translation.copy(); tangent=Vector((math.cos(-1.27),math.sin(-1.27),0))
for off in [-2.2,-1.8,-1.6,-1.4,-1.2,-1,-.8,-.6,-.4,-.2,0,.2,.4,.6]:
 t=base+tangent*(off+.8); d=t-s; clear=all(tr.ray_cast(s,d.normalized(),d.length)[0] is None for tr in trees); print(round(off,2),clear,round(d.normalized().dot(n),2))
