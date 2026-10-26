from __future__ import annotations
import hashlib, json
from pathlib import Path
import bpy
ROOT=Path(__file__).resolve().parents[1]
MASTER=ROOT/'purdue_campus_master.blend'
if Path(bpy.data.filepath).resolve()!=MASTER.resolve(): raise RuntimeError(f'Wrong master file: {bpy.data.filepath}')
manifest=json.loads((ROOT/'modular/manifest.json').read_text(encoding='utf-8'))
verification=json.loads((ROOT/'modular/verification.json').read_text(encoding='utf-8'))
scene=bpy.context.scene

def j(rel): return json.loads((ROOT/rel).read_text(encoding='utf-8'))
def asset_record(asset_id): return next(x for x in manifest['assets'] if x['id']==asset_id)
def check_detail(asset_id, relpath, sha, count, grade_rel, reopen_rel, grade_hash_field='sha256', passed_field='passed'):
    record=asset_record(asset_id); grade=j(grade_rel); reopen=j(reopen_rel); path=(ROOT/relpath).resolve()
    actual=hashlib.sha256(path.read_bytes()).hexdigest()
    if record.get('kind')!='detailed' or record.get('asset_sha256')!=sha: raise RuntimeError(f'{asset_id}: manifest kind/hash mismatch')
    if actual!=sha or grade.get(grade_hash_field)!=sha or reopen.get('sha256')!=sha: raise RuntimeError(f'{asset_id}: exact asset/grade/reopen hash mismatch')
    if not grade.get(passed_field) or float(grade['score'])<8.0: raise RuntimeError(f'{asset_id}: independent score below threshold')
    col=bpy.data.collections.get(record['collection']); marker=bpy.data.objects.get('Placement_'+asset_id)
    if col is None or col.library is None or marker is None: raise RuntimeError(f'{asset_id}: collection or marker missing')
    if len(col.all_objects)!=count or record.get('object_count')!=count: raise RuntimeError(f'{asset_id}: object count mismatch')
    if Path(bpy.path.abspath(col.library.filepath)).resolve()!=path: raise RuntimeError(f'{asset_id}: library path mismatch')
    if marker.instance_collection!=col: raise RuntimeError(f'{asset_id}: marker instances the wrong collection')
    if any(c.name==record['collection'] for c in scene.collection.children): raise RuntimeError(f'{asset_id}: detailed collection is also linked directly')
    origin=record.get('placement_origin_xy_m')
    if not origin: raise RuntimeError(f'{asset_id}: placement origin missing')
    error=((marker.location.x-origin[0])**2+(marker.location.y-origin[1])**2)**0.5
    if error>0.001 or abs(marker.location.z)>0.001: raise RuntimeError(f'{asset_id}: marker offset {error:.6f} m')
    if any(abs(v)>1e-6 for v in marker.rotation_euler) or any(abs(v-1)>1e-6 for v in marker.scale): raise RuntimeError(f'{asset_id}: marker rotation/scale is not identity')
    return {'id':asset_id,'sha256':actual,'score':float(grade['score']),'objects':count,'mesh_count':sum(o.type=='MESH' for o in col.all_objects),'library_path':col.library.filepath,'marker':marker.name,'marker_xy_m':[float(marker.location.x),float(marker.location.y)],'marker_error_m':error}

# Accepted Yue-Kong Pao is a campus-coordinate legacy massing library and stays directly linked.
yid='massing_yue_kong_pao_hall_a3cb766'; yr=asset_record(yid); yg=j('audit/yue_kong_pao_hall/independent_grade_r1.json'); yre=j('audit/yue_kong_pao_hall/independent_grade_r1_reopen.json'); yp=(ROOT/'modular'/yr['file']).resolve(); yc=bpy.data.collections.get(yr['collection'])
ysha=hashlib.sha256(yp.read_bytes()).hexdigest()
if yr.get('kind')!='massing' or ysha!=yg['asset_sha256'] or ysha!=yre['sha256'] or not yg['passes'] or float(yg['score'])<8: raise RuntimeError('Yue-Kong Pao grade/hash mismatch')
if yc is None or yc.library is None or len(yc.all_objects)!=363: raise RuntimeError('Yue-Kong Pao linked collection missing/wrong count')
if Path(bpy.path.abspath(yc.library.filepath)).resolve()!=yp: raise RuntimeError('Yue-Kong Pao link path mismatch')
if not any(c.name==yr['collection'] for c in scene.collection.children): raise RuntimeError('Yue-Kong Pao direct massing link is missing')
if bpy.data.objects.get('Placement_'+yid) is not None: raise RuntimeError('Unexpected Yue-Kong Pao placement marker')
if not all(o.type!='MESH' or o.data and len(o.data.materials)>0 for o in yc.all_objects): raise RuntimeError('Yue-Kong Pao has materialless meshes')
yue={'id':yid,'sha256':ysha,'score':float(yg['score']),'objects':len(yc.all_objects),'mesh_count':sum(o.type=='MESH' for o in yc.all_objects),'library_path':yc.library.filepath,'direct_scene_link':True,'bounds_world_m':yre['bounds_world_xyz']}

tark=check_detail('tarkington_hall','modular/buildings/tarkington_hall.blend','b844a77e35ad44bf722ea0432ed40dc47a6b01fff24c095cbabf68e760f87065',1361,'audit/tarkington_hall/independent_grade_r4.json','audit/tarkington_hall/independent_grade_r4_reopen.json')
zta=check_detail('massing_zeta_tau_alpha_af8a443','modular/buildings/zeta_tau_alpha.blend','1e9b54a032ac508e3e473e1757b6edce6ee8724b581c884d54e984572ed8a7af',563,'audit/zeta_tau_alpha/independent_grade_r2.json','audit/zeta_tau_alpha/independent_grade_r2_extract.json',grade_hash_field='reviewed_sha256',passed_field='passes')
markers=sum(o.name.startswith('Placement_') for o in bpy.data.objects)
if markers!=71: raise RuntimeError(f'Expected 71 placement markers, found {markers}')
if len(scene.objects)!=3930: raise RuntimeError(f'Expected 3930 scene objects, found {len(scene.objects)}')
if manifest['detailed_asset_count']!=71 or verification['detailed_asset_count']!=71: raise RuntimeError('Detailed asset totals mismatch')
if verification['master_placement_markers']!=markers or verification['master_scene_object_count']!=len(scene.objects): raise RuntimeError('Verification index counts mismatch')
if verification['source_asset_object_count']!=sum(int(a.get('object_count',0)) for a in manifest['assets']): raise RuntimeError('Source asset object total mismatch')
report={'status':'PASS','master':str(MASTER),'master_sha256':hashlib.sha256(MASTER.read_bytes()).hexdigest(),'master_scene_objects':len(scene.objects),'master_placement_markers':markers,'detailed_asset_count':manifest['detailed_asset_count'],'source_asset_object_count':verification['source_asset_object_count'],'verified_assets':[yue,tark,zta],'fresh_process_reopen':True}
(ROOT/'audit/master_sync_r29.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2,ensure_ascii=False))

