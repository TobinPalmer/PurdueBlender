import bpy,json,os
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='modular/buildings/rawls_hall.blend');s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();glass=bpy.data.objects['RAWL_North_Windows_Glass'];mulls=bpy.data.objects['RAWL_North_Windows_BronzeMullions'];wall=bpy.data.objects['RAWL_Masonry_Exterior_Walls'];rows=[]
# At pane interior points away from bars, trace through the glass assembly and record next surfaces.
for x,z in [(20.43,2.4),(20.43,7.89),(20.43,13.38),(23.0,2.4),(23.0,7.89),(23.0,13.38),(27.3,2.4),(27.3,7.89),(27.3,13.38)]:
 origin=Vector((x,30,z));d=Vector((0,-1,0));hits=[]
 for _ in range(4):
  hit,loc,n,fi,obj,mat=s.ray_cast(dg,origin,d,distance=50)
  if not hit:break
  hits.append({'object':obj.name,'point':[round(v,3) for v in loc]});origin=loc+d*.025
 rows.append({'x':x,'z':z,'hits':hits})
print(json.dumps(rows,indent=2));open('audit/batch4_rawls/round4_aperture_ray_checks.json','w').write(json.dumps(rows,indent=2))
