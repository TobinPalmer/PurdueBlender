import bpy,bmesh,json
from pathlib import Path
p=Path('audit/purdue_graduate_student_center/garage_boolean_test_1m.blend').resolve();bpy.ops.wm.open_mainfile(filepath=str(p))
o=bpy.data.objects['PGSC_InterfaceTest_Garage_Cutout_1m']
for x in bpy.context.selected_objects:x.select_set(False)
o.select_set(True);bpy.context.view_layer.objects.active=o
o.data.remesh_mode='VOXEL';o.data.remesh_voxel_size=0.1
bpy.ops.object.voxel_remesh()
bm=bmesh.new();bm.from_mesh(o.data);bm.normal_update();nonman=sum(not e.is_manifold for e in bm.edges);boundary=sum(e.is_boundary for e in bm.edges);vol=bm.calc_volume(signed=False)
res={'voxel_size_m':0.1,'vertices':len(o.data.vertices),'faces':len(o.data.polygons),'nonmanifold_edges':nonman,'boundary_edges':boundary,'volume_m3':vol,'status':'PASS' if nonman==0 and boundary==0 else 'FAIL'}
Path('audit/purdue_graduate_student_center/garage_voxel_repair_1m.json').write_text(json.dumps(res,indent=2));print(json.dumps(res));bpy.ops.wm.save_as_mainfile(filepath=str(Path('audit/purdue_graduate_student_center/garage_voxel_repaired_1m.blend').resolve()))
