import bpy,bmesh,json,hashlib
from mathutils import Vector
path=r'C:\Users\Tobin\Documents\Blender\PurdueMap\modular\buildings\massing_house_301837281_58ead22.blend'
bpy.ops.wm.open_mainfile(filepath=path)
col=bpy.data.collections['Asset_massing_house_301837281_58ead22']
meshobs=[o for o in col.all_objects if o.type=='MESH']
rows=[]; totals={'vertices':0,'edges':0,'faces':0,'nonmanifold_edges':0,'boundary_edges':0,'wire_edges':0}
for o in meshobs:
    bm=bmesh.new(); bm.from_mesh(o.data); bm.normal_update()
    row={'object':o.name,'edges':len(bm.edges),'faces':len(bm.faces),
         'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),
         'boundary_edges':sum(e.is_boundary for e in bm.edges),
         'wire_edges':sum(not e.link_faces for e in bm.edges)}
    bm.free(); rows.append(row)
    totals['vertices']+=len(o.data.vertices); totals['edges']+=row['edges']; totals['faces']+=row['faces']
    for key in ('nonmanifold_edges','boundary_edges','wire_edges'): totals[key]+=row[key]
with open(path,'rb') as f: sha=hashlib.sha256(f.read()).hexdigest().upper()
report={'sha256':sha,'mesh_object_count':len(meshobs),'topology_totals':totals,
        'objects_with_nonmanifold_edges':[r for r in rows if r['nonmanifold_edges']]}
out=r'C:\Users\Tobin\Documents\Blender\PurdueMap\audit\phi_gamma_delta\topology_probe.json'
with open(out,'w',encoding='utf-8') as f: json.dump(report,f,indent=2)
print(json.dumps(report,indent=2))
