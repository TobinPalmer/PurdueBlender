import bpy,json,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
p=HERE/'builder_smoke_project/modular/buildings/black_cultural_center.blend'
manifest=json.loads((HERE/'sources/manifest_snapshot.json').read_text(encoding='utf-8-sig'))
e=next(a for a in manifest['assets'] if a.get('id')=='black_cultural_center')
bpy.ops.wm.open_mainfile(filepath=str(p)); c=bpy.data.collections.get(e['collection']); assert c
objs=list(c.all_objects); types={}
for o in objs: types[o.type]=types.get(o.type,0)+1
names=sorted(o.name for o in objs); curr=json.loads((HERE/'blender_asset_probe.json').read_text())
r={'rebuilt_asset_path':'builder_smoke_project/modular/buildings/black_cultural_center.blend','rebuilt_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'opened_in':bpy.app.version_string,'scene':bpy.context.scene.name,'collection':c.name,'object_count':len(objs),'type_counts':types,'manifest_object_count':e['object_count'],'manifest_names_match':names==sorted(e['objects']),'current_asset_sha256':curr['asset_sha256'],'rebuild_byte_identical_to_current':hashlib.sha256(p.read_bytes()).hexdigest()==curr['asset_sha256'],'camera_light_count':sum(o.type in {'CAMERA','LIGHT'} for o in objs)}
(HERE/'builder_smoke_reopen.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8'); print(json.dumps(r,indent=2)); assert len(objs)==621 and r['manifest_names_match']
