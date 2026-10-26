import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
for p,name in [('modular/buildings/massing_northwestern_parking_garage_979f1a2.blend','Northwestern Parking Garage'),('audit/purdue_graduate_student_center/garage_boolean_test_corrected.blend','PGSC_InterfaceTest_Garage_Cutout_Corrected')]:
 bpy.ops.wm.open_mainfile(filepath=str(Path(p).resolve()));o=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(o.data);bm.normal_update();rays=[]
 for x,y in ((150,260),(160,260),(145,252),(180,260),(150,280)):
  hit,loc,norm,fi=o.ray_cast(Vector((x,y,-1)),Vector((0,0,1)),distance=30);rays.append({'xy':[x,y],'hit':hit,'z':round(float(loc.z),3) if hit else None})
 print(json.dumps({'file':p,'faces':len(o.data.polygons),'volume':bm.calc_volume(signed=False),'nonman':sum(not e.is_manifold for e in bm.edges),'rays':rays}))
