import bpy,os,json
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('modular/buildings/rawls_hall.blend'));s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get()
for gn in ['RAWL_SE_Diagonal_CurtainWall_Glass','RAWL_South_Windows_South_Glass','RAWL_East_Windows_Glass','RAWL_North_Windows_Glass']:
 o=bpy.data.objects[gn];print('\n',gn,len(o.data.polygons))
 for p in list(o.data.polygons)[::max(1,len(o.data.polygons)//5)]:
  pts=[o.matrix_world@o.data.vertices[i].co for i in p.vertices];c=sum(pts,Vector())/len(pts);normal=(o.matrix_world.to_3x3()@p.normal).normalized()
  desk=min([x for x in bpy.data.objects if x.type=='MESH' and '1086_Desk' in x.name],key=lambda x:(x.location-c).length)
  target=desk.location+Vector((0,0,.32));d=(target-c).normalized();origin=c-d*3
  hit,loc,n,fi,obj,ma=s.ray_cast(dg,origin,d,distance=(target-origin).length+1)
  print('pane',p.index,'c',tuple(round(v,2) for v in c),'n',tuple(round(v,2) for v in normal),'desk',desk.name,'target',tuple(round(v,2) for v in target),'first',obj.name if obj else None)
