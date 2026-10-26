import bpy, hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
ASSET=ROOT/'modular/buildings/massing_st_thomas_aquinas_5535390.blend'
EXPECTED='a06977c0783442a0eb7561d23e294bfc65d11546b3aa4a0c13d9c9b62f68a330'
ID='massing_st_thomas_aquinas_5535390'
marker=bpy.data.objects.get('Placement_'+ID)
collection=bpy.data.collections.get('Asset_'+ID)
if marker is None or collection is None: raise RuntimeError('Missing St Thomas marker or linked collection')
actual=hashlib.sha256(ASSET.read_bytes()).hexdigest()
lib=Path(bpy.path.abspath(collection.library.filepath)).resolve()
origin=(21.32823749544109,-412.2141452954931)
err=((float(marker.location.x)-origin[0])**2+(float(marker.location.y)-origin[1])**2)**0.5
result={'fresh_process_read_only_master_reopen':True,'master':bpy.data.filepath,'asset_sha256':actual,'expected_asset_sha256':EXPECTED,'hash_matches':actual==EXPECTED,'marker':marker.name,'marker_instance_collection':marker.instance_collection.name if marker.instance_collection else None,'source_library':str(lib),'source_library_matches_asset':lib==ASSET.resolve(),'marker_xyz':[float(v) for v in marker.location],'rotation_euler':[float(v) for v in marker.rotation_euler],'scale':[float(v) for v in marker.scale],'placement_origin_xy_m':list(origin),'marker_position_error_m':err,'linked_object_count':len(collection.all_objects)}
if not result['hash_matches'] or not result['source_library_matches_asset'] or err>0.001 or result['marker_instance_collection']!=collection.name: raise RuntimeError(json.dumps(result))
Path(__file__).resolve().parent.joinpath('independent_grade_r4_master_marker.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
