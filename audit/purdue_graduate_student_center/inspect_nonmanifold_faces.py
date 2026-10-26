import bpy,bmesh,json
from pathlib import Path
p=Path('audit/purdue_graduate_student_center/garage_boolean_test.blend').resolve(); bpy.ops.wm.open_mainfile(filepath=str(p))
o=bpy.data.objects['PGSC_InterfaceTest_Garage_Cutout']; bm=bmesh.new(); bm.from_mesh(o.data); bm.normal_update()
out=[]
for e in bm.edges:
 if not e.is_manifold:
  faces=[]
  for f in e.link_faces:
   faces.append({'area':round(float(f.calc_area()),6),'normal':[round(float(x),5) for x in f.normal],'verts':[[round(float(x),4) for x in (o.matrix_world@v.co)] for v in f.verts]})
  out.append({'edge':[[round(float(x),4) for x in o.matrix_world@v.co] for v in e.verts],'faces':faces})
print(json.dumps(out,indent=2))
