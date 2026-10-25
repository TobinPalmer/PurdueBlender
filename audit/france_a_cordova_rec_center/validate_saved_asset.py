"""Reopen-time validation for the dedicated CREC source asset."""
import bpy, json, hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[2]
asset_id='massing_france_a_c_rdova_recreational_sports_center_ae69df0'
blend=root/'modular'/'buildings'/(asset_id+'.blend')
coll=bpy.data.collections.get('Asset_'+asset_id)
assert coll is not None, 'Stable exported collection missing'
assert coll.get('stable_asset_id')==asset_id
objs=list(coll.objects)
meshes=[o for o in objs if o.type=='MESH']
assert len(meshes)>=10, f'Unexpected mesh count: {len(meshes)}'
allverts=[];face_count=0;invalid=[];matnames=set()
for o in meshes:
    allverts.extend([o.matrix_world@v.co for v in o.data.vertices]);face_count+=len(o.data.polygons)
    for p in o.data.polygons:
        if any(i>=len(o.data.vertices) for i in p.vertices):invalid.append(o.name)
    matnames.update(m.name for m in o.data.materials if m)
assert not invalid, f'Invalid mesh indices: {invalid}'
assert face_count>1000, f'Unexpectedly low face count: {face_count}'
assert len(matnames)>=8, f'Insufficient material variety: {sorted(matnames)}'
mins=[min(v[i] for v in allverts) for i in range(3)];maxs=[max(v[i] for v in allverts) for i in range(3)]
ref=next((o for o in objs if o.name.startswith('CREC | source footprint reference')),None)
assert ref is not None and ref.hide_render
roof=next((o for o in meshes if o.name=='CREC | GIS-footprint roof outline'),None)
assert roof is not None
roof_material_face_counts={}
for p in roof.data.polygons:
    mat=roof.data.materials[p.material_index]
    roof_material_face_counts[mat.name]=roof_material_face_counts.get(mat.name,0)+1
for p in ['crec_east_entry.png','crec_roof_overview.png','crec_interior_cutaway.png']:
    assert (root/'audit'/'france_a_cordova_rec_center'/p).is_file(), f'Missing render {p}'
result={
 'asset_id':asset_id,'blend_path':str(blend),'reopened_in_blender':bpy.app.version_string,
 'collection_object_count':len(objs),'mesh_object_count':len(meshes),'face_count':face_count,
 'material_count':len(matnames),'campus_world_bounds':{'min':mins,'max':maxs},
 'gis_feature_id':coll.get('source_feature_id'),'coordinate_frame':coll.get('coordinate_frame'),
 'roof_cap_material_face_counts':roof_material_face_counts,
 'source_reference_hidden_in_render':ref.hide_render,'evidence_renders':['crec_east_entry.png','crec_roof_overview.png','crec_interior_cutaway.png'],
 'blend_sha256':hashlib.sha256(blend.read_bytes()).hexdigest(),
 'checks':'PASS'
}
(root/'audit'/'france_a_cordova_rec_center'/'validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
