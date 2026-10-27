import bpy, json
from pathlib import Path

root = Path(bpy.data.filepath).resolve().parent
manifest_path = root / 'modular' / 'manifest.json'
manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
detailed = [a for a in manifest['assets'] if a.get('kind') == 'detailed']
expected = {f"Placement_{a['id']}": a for a in detailed}
actual = {o.name: o for o in bpy.context.scene.objects if o.name.startswith('Placement_')}
errors = []
if set(actual) != set(expected):
    errors.append({'kind':'marker_set','missing':sorted(set(expected)-set(actual)),'extra':sorted(set(actual)-set(expected))})
checks=[]
for name, asset in expected.items():
    marker=actual.get(name)
    if marker is None or marker.instance_collection is None:
        errors.append({'kind':'missing_instance','marker':name}); continue
    col=marker.instance_collection
    lib=col.library
    actual_path=Path(bpy.path.abspath(lib.filepath)).resolve() if lib else None
    expected_path=(root/'modular'/asset['file']).resolve()
    xy=asset['placement_origin_xy_m']
    position_ok=all(abs(float(marker.location[i])-float(xy[i]))<=0.001 for i in range(2))
    path_ok=actual_path==expected_path
    object_count=len(col.all_objects)
    object_count_ok=object_count==asset.get('object_count')
    if not path_ok: errors.append({'kind':'wrong_library','marker':name,'actual':str(actual_path),'expected':str(expected_path)})
    if not position_ok: errors.append({'kind':'wrong_position','marker':name,'actual':list(marker.location[:2]),'expected':xy})
    if not object_count_ok: errors.append({'kind':'object_count_mismatch','marker':name,'actual':object_count,'expected':asset.get('object_count')})
    checks.append({'id':asset['id'],'marker':name,'library':str(actual_path),'position_xy_m':list(marker.location[:2]),'object_count':object_count,'path_ok':path_ok,'position_ok':position_ok,'object_count_ok':object_count_ok})
missing_libraries=[]
for lib in bpy.data.libraries:
    p=Path(bpy.path.abspath(lib.filepath)).resolve()
    if not p.exists(): missing_libraries.append(str(p))
if missing_libraries: errors.append({'kind':'missing_library_files','paths':missing_libraries})
result={'status':'PASS' if not errors else 'FAIL','master_file':str(Path(bpy.data.filepath).resolve()),'blender_version':bpy.app.version_string,'manifest_asset_count':len(manifest['assets']),'detailed_asset_count':len(detailed),'master_placement_marker_count':len(actual),'verified_detailed_markers':len(checks),'linked_library_count':len(bpy.data.libraries),'master_scene_object_count':len(bpy.context.scene.objects),'missing_library_files':missing_libraries,'errors':errors,'checks':checks}
out=root/'audit'/'master_sync_2026-10-27.json'
out.write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='checks'}))
if errors: raise RuntimeError(f'Fresh-open master verification failed with {len(errors)} errors')
