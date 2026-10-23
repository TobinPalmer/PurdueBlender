import bpy,json,pathlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=pathlib.Path(r'C:/Users/Tobin/Documents/Blender/PurdueMap'); f=P/'modular/buildings/elliott_hall_of_music.blend'; bpy.ops.wm.open_mainfile(filepath=str(f))
w=bpy.data.objects['ELLT_Official_Footprint_Exterior_Walls']; data=json.loads((P/'audit/batch3_elliott/result_round3_accessibility.json').read_text());
bvh=BVHTree.FromObject(w,bpy.context.evaluated_depsgraph_get(),epsilon=0)
# recover tangent from the nearest boundary edge at recorded door location
rings=[(float(v.co.x),float(v.co.y)) for v in w.data.vertices if abs(v.co.z)<1e-6]
# only the wall is no longer original ring; recover GIS source ring from preserved backup
bpy.ops.wm.open_mainfile(filepath=str(P/'audit/batch3_elliott/before_resume.blend')); bw=bpy.data.objects['ELLT_Official_Footprint_Exterior_Walls']; N=len(bw.data.vertices)//2; ring=[(float(v.co.x),float(v.co.y)) for v in bw.data.vertices[:N]]
# area sign
A=.5*sum(ring[i][0]*ring[(i+1)%N][1]-ring[(i+1)%N][0]*ring[i][1] for i in range(N)); out=[]
# reload source again to get BVH
bpy.ops.wm.open_mainfile(filepath=str(f)); w=bpy.data.objects['ELLT_Official_Footprint_Exterior_Walls']; bvh=BVHTree.FromObject(w,bpy.context.evaluated_depsgraph_get(),epsilon=0)
for d in data['doors']:
 p=Vector(d['xy']); i=min(range(N),key=lambda i:(ring[i][0]-p.x)**2+(ring[i][1]-p.y)**2); j=(i+1)%N; dx=ring[j][0]-ring[i][0];dy=ring[j][1]-ring[i][1];ll=(dx*dx+dy*dy)**.5;tx,ty=dx/ll,dy/ll;nx,ny=(ty,-tx) if A>0 else (-ty,tx); origin=Vector((p.x+nx*.6,p.y+ny*.6,1.5)); hit=bvh.ray_cast(origin,Vector((-nx,-ny,0)),1.2)
 origin2=Vector((p.x+nx*.6,p.y+ny*.6,4.0));hit2=bvh.ray_cast(origin2,Vector((-nx,-ny,0)),1.2)
 out.append({'name':d['name'],'z1_5m_wall_hit':hit[0] is not None,'z4m_wall_hit':hit2[0] is not None,'distance':hit[3]})
(P/'audit/batch3_elliott/opening_ray_check.json').write_text(json.dumps(out,indent=2));print(out)
