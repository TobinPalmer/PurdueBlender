import bpy,math
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get(); g=bpy.data.objects['RAWL_SE_Diagonal_CurtainWall_Glass']
screens=[bpy.data.objects[n].matrix_world.translation.copy() for n in ['RAWL_1086_R10_Schematic_Projection_Surface_01','RAWL_1086_R10_Schematic_Projection_Surface_02']]
# wall01 normal facing estimated table-centre side
wall=bpy.data.objects['RAWL_2026_Plan1086_01_00']; wn=Vector((-math.sin(wall.rotation_euler.z),math.cos(wall.rotation_euler.z),0)); ds=[o for o in bpy.data.objects if o.name.startswith('RAWL_2026_1086_Desk')]; deskctr=sum((o.matrix_world.translation for o in ds),Vector())/len(ds); todesks=(deskctr-sum(screens,Vector())/2).normalized(); print('deskctr',tuple(deskctr),'wallnormal',tuple(wn),'towards desks',tuple(todesks),'alignment',wn.dot(todesks))
for i,t in enumerate(screens):
 vals=[]
 for p in g.data.polygons:
  c=sum((g.matrix_world@g.data.vertices[j].co for j in p.vertices),Vector())/len(p.vertices); n=(g.matrix_world.to_3x3()@p.normal).normalized(); s=c+n*.02; d=t-s; hit,loc,no,face,obj,mat=sc.ray_cast(dg,s,d.normalized(),distance=d.length-.06)
  if obj is None: vals.append((round(d.normalized().dot(wn),2),round(d.length,1),p.index))
 print('screen',i,'best camera panes',sorted(vals,reverse=True)[:10])
