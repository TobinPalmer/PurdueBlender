"""Inspect a fresh-open saved Haas library without modifying or saving it."""
import bpy,bmesh,json,hashlib
from pathlib import Path
from mathutils import Vector
D=Path(__file__).resolve().parent
asset=Path(bpy.data.filepath);sha=hashlib.sha256(asset.read_bytes()).hexdigest()
C=bpy.data.collections['Asset_felix_haas_hall'];rows=[]
for o in C.all_objects:
    if o.type!='MESH':continue
    bm=bmesh.new();bm.from_mesh(o.data)
    rows.append(dict(name=o.name,nonmanifold_edges=sum(not e.is_manifold for e in bm.edges),zero_area_faces=sum(f.calc_area()<1e-10 for f in bm.faces)))
    bm.free()
walls=[]
for o in C.objects:
    if o.name.startswith('HAAS_Rebuild_Wall_'):
        pts=[o.matrix_world@v.co for v in o.data.vertices]
        walls.append(dict(object=o.name,bounds=[[min(v[i] for v in pts),max(v[i] for v in pts)] for i in range(3)]))
report=dict(asset_sha256=sha,revision=C.get('revision'),collection=C.name,objects=len(C.all_objects),bad_meshes=[r for r in rows if r['nonmanifold_edges'] or r['zero_area_faces']],external_libraries=[x.filepath for x in bpy.data.libraries],unpacked_external_images=[x.filepath for x in bpy.data.images if x.filepath and not x.packed_file],live_modifiers=[dict(object=o.name,modifier=m.name,type=m.type) for o in C.all_objects for m in o.modifiers],wall_extents=walls,archive_objects=[dict(name=c.name,objects=len(c.all_objects),hidden_render=c.hide_render,hidden_viewport=c.hide_viewport) for c in bpy.data.collections if 'Archive' in c.name],source_saved=False,accepted=False)
assert not report['bad_meshes'],report['bad_meshes']
assert not report['external_libraries'] and not report['unpacked_external_images']
assert C.get('revision')==D.name
assert hashlib.sha256(asset.read_bytes()).hexdigest()==sha
(D/'reopen_validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='wall_extents'},indent=2))
