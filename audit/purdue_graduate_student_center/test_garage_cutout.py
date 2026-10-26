import bpy,json,bmesh
from pathlib import Path
from mathutils import Vector
ROOT=Path.cwd()
GARAGE=ROOT/'modular/buildings/massing_northwestern_parking_garage_979f1a2.blend'
CUT=ROOT/'audit/purdue_graduate_student_center/pgsc_garage_cutout_polygon.json'
OUT=ROOT/'audit/purdue_graduate_student_center/garage_boolean_test.blend'
bpy.ops.wm.open_mainfile(filepath=str(GARAGE))
source=bpy.data.objects.get('Northwestern Parking Garage')
if source is None: raise RuntimeError('Garage source mesh missing')
collection=source.users_collection[0]
obj=source.copy(); obj.data=source.data.copy(); obj.name='PGSC_InterfaceTest_Garage_Cutout'; collection.objects.link(obj)
source.hide_render=True; source.hide_viewport=True
cut_data=json.loads(CUT.read_text(encoding='utf-8'))
ring=cut_data['cutout_ring_xy_m']; n=len(ring)-1; z0=0.01; z1=3.85
verts=[(x,y,z) for z in (z0,z1) for x,y in ring[:-1]]
faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
for i in range(n):
 j=(i+1)%n; faces.append((i,j,n+j,n+i))
mesh=bpy.data.meshes.new('PGSC_GIS_Cutout_Test_Mesh'); mesh.from_pydata(verts,[],faces); mesh.update()
cutter=bpy.data.objects.new('PGSC_GIS_Cutout_Test',mesh); collection.objects.link(cutter)
mod=obj.modifiers.new('Boolean_PGSC_Interface_Test','BOOLEAN'); mod.operation='DIFFERENCE'; mod.solver='EXACT'; mod.object=cutter
bpy.context.view_layer.objects.active=obj; obj.select_set(True); source.select_set(False); cutter.select_set(False)
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.data.objects.remove(cutter,do_unlink=True)
# topology and volume metrics
bm=bmesh.new(); bm.from_mesh(obj.data); bm.normal_update()
nonman=sum(not e.is_manifold for e in bm.edges); boundary=sum(e.is_boundary for e in bm.edges); volume=bm.calc_volume(signed=False)
pts=[obj.matrix_world @ v.co for v in obj.data.vertices]
bounds=[[min(v[i] for v in pts),max(v[i] for v in pts)] for i in range(3)]
result={'source_object':source.name,'output_object':obj.name,'vertices':len(obj.data.vertices),'faces':len(obj.data.polygons),'nonmanifold_edges':nonman,'boundary_edges':boundary,'volume_after_m3':volume,'bounds_world_m':bounds,'cutout_xy_buffer_m':cut_data['buffer_m'],'cutout_height_m':z1-z0,'cutout_polygon_area_m2':cut_data['cutout_area_m2'],'status':'PASS' if nonman==0 else 'FAIL'}
(ROOT/'audit/purdue_graduate_student_center/garage_boolean_test.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
if nonman: raise RuntimeError('Boolean result is nonmanifold')

