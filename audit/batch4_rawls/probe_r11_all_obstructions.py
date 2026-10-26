import bpy,math
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get(); g=bpy.data.objects['RAWL_SE_Diagonal_CurtainWall_Glass']
base=bpy.data.objects['RAWL_1086_R10_Schematic_Projection_Surface_01'].matrix_world.translation.copy(); tangent=Vector((math.cos(-1.27),math.sin(-1.27),0));
for off in [-5,-4,-3,-2,-1,0,1,2,3]:
 t=base+tangent*(off+1.8); best=[]
 for p in g.data.polygons:
  c=sum((g.matrix_world@g.data.vertices[i].co for i in p.vertices),Vector())/len(p.vertices); n=(g.matrix_world.to_3x3()@p.normal).normalized(); s=c+n*.02; d=t-s; hit,loc,norm,face,obj,mat=sc.ray_cast(dg,s,d.normalized(),distance=d.length-.06)
  if obj is None: best.append((round(d.normalized().dot(n),2),p.index,round(d.length,1)))
 if best: print('off',off,'vis',sorted(best,reverse=True)[:3])
 else:
  p=g.data.polygons[1]; c=sum((g.matrix_world@g.data.vertices[i].co for i in p.vertices),Vector())/len(p.vertices); n=(g.matrix_world.to_3x3()@p.normal).normalized(); s=c+n*.02; d=t-s; hit,loc,norm,face,obj,mat=sc.ray_cast(dg,s,d.normalized(),distance=d.length-.06); print('off',off,'blocked by',obj.name if obj else None)

