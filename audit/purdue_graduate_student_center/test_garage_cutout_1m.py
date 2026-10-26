import bpy,json,bmesh
from pathlib import Path
from mathutils import Vector
ROOT=Path.cwd(); GARAGE=ROOT/'modular/buildings/massing_northwestern_parking_garage_979f1a2.blend'; CUT=ROOT/'audit/purdue_graduate_student_center/pgsc_garage_cutout_polygon_1m.json'; OUT=ROOT/'audit/purdue_graduate_student_center/garage_boolean_test_1m.blend'
bpy.ops.wm.open_mainfile(filepath=str(GARAGE)); source=bpy.data.objects['Northwestern Parking Garage']; collection=source.users_collection[0]
obj=source.copy();obj.data=source.data.copy();obj.name='PGSC_InterfaceTest_Garage_Cutout_1m';collection.objects.link(obj)
data=json.loads(CUT.read_text()); ring=data['cutout_ring_xy_m'];n=len(ring)-1;z0=-0.5;z1=4.5
verts=[(x,y,z) for z in(z0,z1) for x,y in ring[:-1]];faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
for i in range(n):j=(i+1)%n;faces.append((i,j,n+j,n+i))
mesh=bpy.data.meshes.new('PGSC_Cutter_1m');mesh.from_pydata(verts,[],faces);mesh.update();cutter=bpy.data.objects.new('PGSC_Cutter_1m',mesh);collection.objects.link(cutter)
mod=obj.modifiers.new('PGSC_Cutout_1m','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.context.view_layer.objects.active=obj;obj.select_set(True);bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
bm=bmesh.new();bm.from_mesh(obj.data);bm.normal_update();nonman=[e for e in bm.edges if not e.is_manifold];boundary=sum(e.is_boundary for e in bm.edges)
res={'vertices':len(obj.data.vertices),'faces':len(obj.data.polygons),'nonmanifold_edges':len(nonman),'boundary_edges':boundary,'cutout_height_m':z1-z0,'cutout_xy_buffer_m':1.0,'status':'PASS' if len(nonman)==0 else 'FAIL'}
(ROOT/'audit/purdue_graduate_student_center/garage_boolean_test_1m.json').write_text(json.dumps(res,indent=2));print(json.dumps(res));bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
if nonman:raise RuntimeError('nonmanifold result')
