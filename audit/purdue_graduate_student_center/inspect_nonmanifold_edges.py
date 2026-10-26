import bpy,bmesh,json
from pathlib import Path
p=Path('audit/purdue_graduate_student_center/garage_boolean_test.blend').resolve(); bpy.ops.wm.open_mainfile(filepath=str(p))
o=bpy.data.objects.get('PGSC_InterfaceTest_Garage_Cutout'); bm=bmesh.new(); bm.from_mesh(o.data); bm.normal_update()
rows=[]
for e in bm.edges:
 if not e.is_manifold:
  rows.append({'co':[[round(float(x),6) for x in (o.matrix_world@v.co)] for v in e.verts],'length':round(e.calc_length(),8),'faces':len(e.link_faces),'boundary':e.is_boundary,'face_normals':[[round(float(c),5) for c in f.normal] for f in e.link_faces]})
print(json.dumps({'count':len(rows),'edges':rows},indent=2))
