import bpy,math
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get(); g=bpy.data.objects['RAWL_SE_Diagonal_CurtainWall_Glass']
base=bpy.data.objects['RAWL_1086_R10_Schematic_Projection_Surface_01'].matrix_world.translation.copy(); tangent=Vector((math.cos(-1.27),math.sin(-1.27),0))
def visible(off):
 t=base+tangent*(off+1.8); rows=[]
 for p in g.data.polygons:
  c=sum((g.matrix_world@g.data.vertices[i].co for i in p.vertices),Vector())/len(p.vertices); n=(g.matrix_world.to_3x3()@p.normal).normalized(); s=c+n*.02; d=t-s; hit,loc,no,face,obj,mat=sc.ray_cast(dg,s,d.normalized(),distance=d.length-.06)
  if obj is None: rows.append((p.index,d.normalized().dot(n),d.length))
 return rows
allv={round(x*.25,2):visible(round(x*.25,2)) for x in range(-32,13)}
best=[]
for a,va in allv.items():
 for b,vb in allv.items():
  if b-a<0.9:continue
  mb={i:(dot,dist) for i,dot,dist in vb}; common=[(min(dot,mb[i][0]),i,dist,mb[i][1]) for i,dot,dist in va if i in mb]
  if common:
   score=max(common)[0]; best.append((score,a,b,sorted(common,reverse=True)[:1]))
print(sorted(best,reverse=True)[:15])
