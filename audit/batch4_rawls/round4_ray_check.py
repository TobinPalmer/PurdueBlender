import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='modular/buildings/rawls_hall.blend');s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get()
for x,z in [(25,2.4),(25,5.2),(25,8),(5,2.4),(5,5.2),(5,8)]:
 origin=Vector((x,30,z));direction=Vector((0,-1,0));hit,loc,n,fi,obj,mat=s.ray_cast(dg,origin,direction,distance=30)
 print('ray',x,z,'hit',hit,'obj',obj.name if obj else None,'loc',tuple(round(v,3) for v in loc),'face',fi,'matrix',tuple(mat.translation) if mat else None)
print('glass world y sample')
o=bpy.data.objects['RAWL_North_Windows_Glass'];
for poly in o.data.polygons:
 pts=[o.matrix_world@o.data.vertices[i].co for i in poly.vertices];cx=sum(v.x for v in pts)/4;cz=sum(v.z for v in pts)/4
 if 20<cx<30 and 1<cz<10:
  print('glass quad',round(cx,2),round(cz,2),'y',round(sum(v.y for v in pts)/4,3));
