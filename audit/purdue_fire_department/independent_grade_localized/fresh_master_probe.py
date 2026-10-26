import bpy, json, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
MOD=ROOT/'modular'; ID='massing_purdue_fire_department_520430b'
MASTER=ROOT/'purdue_campus_master.blend'; ASSET=MOD/'buildings'/f'{ID}.blend'
OUT=Path(__file__).with_name('fresh_master_probe.json')
OUT.write_text(json.dumps({'status':'OPENING','master':str(MASTER)}),encoding='utf-8')
bpy.ops.wm.open_mainfile(filepath=str(MASTER))
manifest=json.loads((MOD/'manifest.json').read_text(encoding='utf-8'))
rec=next(a for a in manifest['assets'] if a['id']==ID)
marker=bpy.data.objects.get('Placement_'+ID)
assert marker is not None
assert marker.instance_type=='COLLECTION' and marker.instance_collection is not None
assert marker.instance_collection.name==rec['collection']
lib=Path(bpy.path.abspath(marker.instance_collection.library.filepath)).resolve()
assert lib==ASSET.resolve(),str(lib)
assert max(abs(float(marker.location[i])-float(rec['placement_origin_xy_m'][i])) for i in range(2))<0.001
assert max(abs(float(v)) for v in marker.rotation_euler)<1e-7
assert max(abs(float(v)-1) for v in marker.scale)<1e-7
old=bpy.data.collections.get('Asset_'+ID)
assert not (old is not None and old in list(bpy.context.scene.collection.children))
result={'status':'PASS','master_path':str(MASTER),'asset_id':ID,'marker_name':marker.name,'marker_location':list(marker.location),'manifest_origin_xy_m':rec['placement_origin_xy_m'],'marker_rotation':list(marker.rotation_euler),'marker_scale':list(marker.scale),'linked_library':str(lib),'expected_library':str(ASSET.resolve()),'linked_collection':marker.instance_collection.name,'manifest_local_bounds_m':rec['local_bounds_m'],'reconstructed_world_bounds_m':[[rec['local_bounds_m'][i][j]+(float(marker.location[i]) if i<2 else 0) for j in range(2)] for i in range(3)],'manifest_world_bounds_m':rec['bounds_world_m'],'asset_sha256':hashlib.sha256(ASSET.read_bytes()).hexdigest()}
OUT.write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
