import bpy, bmesh, json, hashlib
from pathlib import Path
p=Path('modular/buildings/massing_house_1089876362_14ecd2c.blend').resolve()
bpy.ops.wm.open_mainfile(filepath=str(p))
c=bpy.data.collections['Asset_massing_house_1089876362_14ecd2c']
r=[]
for o in c.objects:
 if o.type=='MESH':
  bm=bmesh.new(); bm.from_mesh(o.data)
  boundary=sum(e.is_boundary for e in bm.edges); nonmanifold=sum(not e.is_manifold for e in bm.edges)
  r.append({'object':o.name,'verts':len(bm.verts),'faces':len(bm.faces),'boundary_edges':boundary,'nonmanifold_edges':nonmanifold})
  bm.free()
report={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'mesh_topology':r,
        'total_boundary_edges':sum(x['boundary_edges'] for x in r),
        'total_nonmanifold_edges':sum(x['nonmanifold_edges'] for x in r)}
Path('audit/kappa_delta_rho/topology_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
