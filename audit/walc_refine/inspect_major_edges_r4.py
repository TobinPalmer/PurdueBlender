import bpy,json
from mathutils import Vector
asset=bpy.data.collections['Asset_walc']
names=['WALC_Source906_Edge_75_Band2','WALC_Source906_Edge_75_Band4','WALC_Source906_Edge_75_Band6','WALC_Source906_Edge_47_Band2','WALC_Source906_Edge_47_Band4','WALC_Source906_Edge_47_Band6','WALC_Source906_Edge_2_Band2','WALC_Source906_Edge_33_Band2','WALC_Source906_Edge_50_Band2','WALC_Source906_Edge_58_Band2']
for name in names:
 o=bpy.data.objects.get(name)
 if not o:
  print(name,'MISSING'); continue
 me=o.data
 ps=[o.matrix_world@v.co for v in me.vertices]
 bounds=[[round(min(p[i] for p in ps),4),round(max(p[i] for p in ps),4)] for i in range(3)]
 mat=[m.name if m else None for m in o.data.materials]
 print(name,'type',o.type,'nverts',len(me.vertices),'nfaces',len(me.polygons),'bounds',bounds,'materials',mat,'hidden',o.hide_viewport,o.hide_render,'collections',[c.name for c in o.users_collection])
 print('  verts',[[round((o.matrix_world@v.co)[i],4) for i in range(3)] for v in me.vertices[:8]])
 print('  normals',[tuple(round(x,3) for x in (o.matrix_world.to_3x3()@p.normal).normalized()) for p in list(me.polygons)[:3]])
