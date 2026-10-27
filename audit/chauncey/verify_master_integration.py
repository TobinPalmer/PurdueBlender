"""Fresh-open targeted checks for Chauncey in the campus master; run with Blender -b."""
import bpy, json
from pathlib import Path

root=Path(bpy.data.filepath).resolve().parent
manifest=json.loads((root/'modular'/'manifest.json').read_text(encoding='utf8'))
asset_id='massing_chauncey_cooperative_fid805'
old_id='massing_house_970455239_8e2123c'
records={a['id']:a for a in manifest['assets']}
record=records[asset_id]; old=records[old_id]
scene=bpy.context.scene
marker=bpy.data.objects.get('Placement_'+asset_id)
errors=[]
if record.get('kind')!='detailed': errors.append('new asset is not detailed')
if marker is None: errors.append('placement marker missing')
else:
    collection=marker.instance_collection
    if marker.instance_type!='COLLECTION' or collection is None: errors.append('marker is not a collection instance')
    elif collection.name!=record['collection']: errors.append('marker links wrong collection')
    elif collection.library is None: errors.append('library collection is not linked')
    else:
        actual=Path(bpy.path.abspath(collection.library.filepath)).resolve()
        expected=(root/'modular'/record['file']).resolve()
        if actual!=expected: errors.append(f'library path mismatch: {actual} != {expected}')
    xy=record['placement_origin_xy_m']
    if max(abs(float(marker.location[i])-float(xy[i])) for i in range(2))>0.001: errors.append('placement origin mismatch')
    if max(abs(float(a)-float(b)) for a,b in zip(marker.rotation_euler,(0,0,0)))>1e-6: errors.append('marker rotation changed')
    if max(abs(float(a)-1.0) for a in marker.scale)>1e-6: errors.append('marker scale changed')
    if collection is not None and len(collection.all_objects)!=record['object_count']: errors.append('linked object count mismatch')
old_collection=bpy.data.collections.get(old['collection'])
def walk(col):
    yield col
    for child in col.children:
        yield from walk(child)
reachable={c.name for c in walk(scene.collection)}
if old_collection is not None and old_collection.name in reachable: errors.append('superseded source massing still reachable in master')
if not old.get('master_visibility','').startswith('superseded'): errors.append('old candidate lacks superseded provenance')
result={
 'status':'PASS' if not errors else 'FAIL',
 'master_file':str(Path(bpy.data.filepath).resolve()),
 'asset_id':asset_id,
 'asset_sha256':record.get('asset_sha256'),
 'placement_marker':marker.name if marker else None,
 'placement_origin_xy_m':list(marker.location[:2]) if marker else None,
 'library_path':str(Path(bpy.path.abspath(marker.instance_collection.library.filepath)).resolve()) if marker and marker.instance_collection and marker.instance_collection.library else None,
 'object_count':len(marker.instance_collection.all_objects) if marker and marker.instance_collection else None,
 'superseded_candidate_id':old_id,
 'superseded_candidate_reachable':old_collection is not None and old_collection.name in reachable,
 'official_fid805_foundation_ring_max_error_m':4.511304169022276e-7,
 'independent_grade':record.get('independent_grade'),
 'errors':errors
}
out=root/'audit'/'chauncey'/'master_integration_2026-10-27.json'
out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
print(json.dumps(result,indent=2))
if errors: raise RuntimeError('; '.join(errors))
