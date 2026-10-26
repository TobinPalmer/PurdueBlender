import bpy,json,bmesh
from pathlib import Path
from mathutils import Vector
ROOT=Path.cwd();GARAGE=ROOT/'modular/buildings/massing_northwestern_parking_garage_979f1a2.blend';CUT=ROOT/'audit/purdue_graduate_student_center/pgsc_garage_cutout_polygon.json';OUT=ROOT/'audit/purdue_graduate_student_center/garage_boolean_test_corrected.blend'
bpy.ops.wm.open_mainfile(filepath=str(GARAGE));source=bpy.data.objects['Northwestern Parking Garage'];collection=source.users_collection[0];obj=source.copy();obj.data=source.data.copy();obj.name='PGSC_InterfaceTest_Garage_Cutout_Corrected';collection.objects.link(obj)
data=json.loads(CUT.read_text());ring=data['cutout_ring_xy_m'];n=len(ring)-1;z0=-0.5;z1=4.5
verts=[(x,y,z) for z in(z0,z1) for x,y in ring[:-1]];faces=[tuple(range(n)),tuple(reversed(range(n,2*n)))]
for i in range(n):j=(i+1)%n;faces.append((i,j,n+j,n+i))
mesh=bpy.data.meshes.new('PGSC_Cutter_Corrected');mesh.from_pydata(verts,[],faces);mesh.update();cutter=bpy.data.objects.new('PGSC_Cutter_Corrected',mesh);collection.objects.link(cutter)
bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(mesh);bm.free();mesh.update()
mod=obj.modifiers.new('PGSC_Cutout_Corrected','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.context.view_layer.objects.active=obj;obj.select_set(True);bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
bm=bmesh.new();bm.from_mesh(obj.data);bm.normal_update();nonman=sum(not e.is_manifold for e in bm.edges);boundary=sum(e.is_boundary for e in bm.edges);vol=bm.calc_volume(signed=False)
rays=[]
for x,y in ((150,260),(160,260),(145,252),(180,260),(150,280)):
 hit,loc,norm,fi=obj.ray_cast(Vector((x,y,-1)),Vector((0,0,1)),distance=30);rays.append({'xy':[x,y],'hit':hit,'z':round(float(loc.z),4) if hit else None})
res={'vertices':len(obj.data.vertices),'faces':len(obj.data.polygons),'nonmanifold_edges':nonman,'boundary_edges':boundary,'volume_m3':vol,'rays':rays,'status':'PASS' if nonman==0 and boundary==0 else 'FAIL'}
(ROOT/'audit/purdue_graduate_student_center/garage_boolean_test_corrected.json').write_text(json.dumps(res,indent=2));print(json.dumps(res));bpy.ops.wm.save_as_mainfile(filepath=str(OUT));
