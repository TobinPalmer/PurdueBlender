import bpy,json,bmesh
from pathlib import Path
p=Path('modular/buildings/massing_northwestern_parking_garage_979f1a2.blend').resolve(); bpy.ops.wm.open_mainfile(filepath=str(p))
o=bpy.data.objects.get('Northwestern Parking Garage'); bm=bmesh.new(); bm.from_mesh(o.data); bm.normal_update()
print(json.dumps({'verts':len(bm.verts),'edges':len(bm.edges),'faces':len(bm.faces),'nonmanifold':sum(not e.is_manifold for e in bm.edges),'boundary':sum(e.is_boundary for e in bm.edges),'wire':sum(e.is_wire for e in bm.edges),'face_components':len(bmesh.ops.find_doubles(bm,verts=bm.verts,dist=0.00001)['targetmap']) if False else 'n/a','bounds':[[min((o.matrix_world@v.co)[i] for v in o.data.vertices),max((o.matrix_world@v.co)[i] for v in o.data.vertices)] for i in range(3)]},indent=2))
