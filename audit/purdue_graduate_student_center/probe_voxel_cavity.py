import bpy,json,bmesh
from pathlib import Path
p=Path('audit/purdue_graduate_student_center/garage_voxel_repaired_1m.blend').resolve();bpy.ops.wm.open_mainfile(filepath=str(p));o=bpy.data.objects['PGSC_InterfaceTest_Garage_Cutout_1m']
points=[[150,260,0],[160,260,0],[145,252,0],[180,260,0],[150,280,0]];res=[]
from mathutils import Vector
for x,y,z in points:
 hit,loc,norm,fi=o.ray_cast(Vector((x,y,-1)),Vector((0,0,1)),distance=30)
 res.append({'xy':[x,y],'hit':hit,'z':round(float(loc.z),4) if hit else None})
bm=bmesh.new();bm.from_mesh(o.data);bm.normal_update();vol=bm.calc_volume(signed=False)
print(json.dumps({'rays':res,'volume':vol,'bounds':[[min(v.co[i] for v in o.data.vertices),max(v.co[i] for v in o.data.vertices)] for i in range(3)]},indent=2))
