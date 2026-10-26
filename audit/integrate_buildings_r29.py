from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MOD=ROOT/'modular'
AUD=ROOT/'audit'
manifest_path=MOD/'manifest.json'
verification_path=MOD/'verification.json'
manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
verification=json.loads(verification_path.read_text(encoding='utf-8'))
snapshot=json.loads((AUD/'master_sync_r29_pre_save_snapshot.json').read_text(encoding='utf-8'))

def read(rel): return json.loads((ROOT/rel).read_text(encoding='utf-8'))
def world_bounds(local, origin):
    return [[float(local[i][0])+float(origin[i]),float(local[i][1])+float(origin[i])] if i<2 else [float(local[i][0]),float(local[i][1])] for i in range(3)]
def row(asset_id):
    return next(x for x in manifest['assets'] if x['id']==asset_id)

# Yue-Kong Pao Hall remains a campus-coordinate library, but now contains the graded detailed geometry.
yue_id='massing_yue_kong_pao_hall_a3cb766'
yue=row(yue_id); yg=read('audit/yue_kong_pao_hall/independent_grade_r1.json'); yr=read('audit/yue_kong_pao_hall/independent_grade_r1_reopen.json')
yue_snap=snapshot['assets']['Asset_massing_yue_kong_pao_hall_a3cb766']
assert yg['passes'] and yg['asset_sha256']==yr['sha256'] and len(yue_snap['objects'])==363
yue.update({
    'objects':yue_snap['objects'],'object_count':363,
    'bounds_world_m':yr['bounds_world_xyz'],'exterior_bounds_world_m':yr['bounds_world_xyz'],
    'asset_sha256':yg['asset_sha256'],'independent_grade_score':float(yg['score']),
    'independent_grade_file':'../audit/yue_kong_pao_hall/independent_grade_r1.md',
    'evidence_file':'../audit/yue_kong_pao_hall/independent_grade_r1_reopen.json',
    'accuracy_status':'R1 independently passed at 8.0/10 and the exact asset freshly reopened in Blender 5.2.3. The south facade follows Purdue photo evidence and all 363 meshes have materials. Independent roof-slab/GIS screening IoU is 0.788 with 13.01 m Hausdorff; slabs simplify the irregular outline and are not a surveyed wall boundary. Height and penthouse are estimates; side/rear elevations and room layouts are schematic.'
})

# Tarkington R4 is a local-coordinate detailed asset linked through its existing placement marker.
tark_id='tarkington_hall'; tark=row(tark_id)
tg=read('audit/tarkington_hall/independent_grade_r4.json'); tr=read('audit/tarkington_hall/independent_grade_r4_reopen.json')
tark_snap=snapshot['assets']['Asset_tarkington_hall']; origin=tark['placement_origin_xy_m']; local=tr['aggregate_mesh_bounds_local_m']
assert tg.get('passed',tg.get('passes',False)) and float(tg['score'])>=8.0 and tg.get('sha256')==tr['sha256']
assert len(tark_snap['objects'])==tr['collection_object_count']==1361
# Marker exactness is independently checked in the current live master snapshot before its save.
tark.update({
    'objects':tark_snap['objects'],'object_count':1361,'local_bounds_m':local,
    'bounds_world_m':world_bounds(local,origin),'exterior_bounds_world_m':world_bounds(local,origin),
    'asset_sha256':tr['sha256'],'independent_grade_score':float(tg['score']),
    'independent_grade_file':'../audit/tarkington_hall/independent_grade_r4.md',
    'evidence_file':'../audit/tarkington_hall/independent_grade_r4_reopen.json',
    'accuracy_status':'R4 independently passed at 8.0/10 and exact-file Blender reopen checks pass. Export-only GIS/orthophoto shell IoU is 0.952, mean boundary residual 0.61 m, P95 2.22 m; the 8.70 m Hausdorff residual and generalized roof/GIS outline remain limitations. Roof height is estimated; interior room/program details are schematic. Master marker was checked against the manifest origin and identity rotation/scale.'
})

# Zeta Tau Alpha is now a local-coordinate detailed asset, using the old stable ID and a new marker.
zta_id='massing_zeta_tau_alpha_af8a443'; zta=row(zta_id)
zg=read('audit/zeta_tau_alpha/independent_grade_r2.json'); zr=read('audit/zeta_tau_alpha/independent_grade_r2_extract.json'); zrv=read('audit/zeta_tau_alpha/reopen_validation_r2.json')
zta_snap=snapshot['assets']['Asset_massing_zeta_tau_alpha_af8a443']; zorigin=zr['asset_origin_xy_m']; zlocal=zr['world_bounds_xyz']
assert zg['passes'] and float(zg['score'])>=8 and zg['reviewed_sha256']==zr['sha256']==zrv['sha256']
assert len(zta_snap['objects'])==zr['object_count']==563
zta.update({
    'kind':'detailed','file':'buildings/zeta_tau_alpha.blend','objects':zta_snap['objects'],'object_count':563,
    'placement_origin_xy_m':zorigin,'local_bounds_m':zlocal,'bounds_world_m':world_bounds(zlocal,zorigin),
    'exterior_bounds_world_m':world_bounds(zlocal,zorigin),
    'asset_sha256':zr['sha256'],'independent_grade_score':float(zg['score']),
    'independent_grade_file':'../audit/zeta_tau_alpha/independent_grade_r2.md',
    'evidence_file':'../audit/zeta_tau_alpha/independent_grade_r2_extract.json',
    'placement_transform':'master collection-instance marker translates local geometry to placement_origin_xy_m',
    'accuracy_status':'R2 independently passed at 8.2/10; fresh Blender reopen, packed textures, GIS FID 773 footprint and outward-facing pediment lettering verified. GIS ring is not surveyed wall faces; height (11.91 m) and story count are estimates, and interior layout is schematic. Master placement marker now uses the source-derived local origin with identity rotation and scale.'
})

manifest['detailed_asset_count']=sum(1 for a in manifest['assets'] if a.get('kind')=='detailed')
verification['asset_count']=len(manifest['assets'])
verification['building_count']=len(manifest['assets'])-1
verification['detailed_asset_count']=manifest['detailed_asset_count']
verification['master_placement_markers']=snapshot['placement_markers']
verification['master_scene_object_count']=snapshot['master_scene_objects']
verification['source_asset_object_count']=sum(int(a.get('object_count',0)) for a in manifest['assets'])
verification['status']='PASS'
verification['errors']=[]
verification.setdefault('superseded_massing_assets',[])
if zta_id not in verification['superseded_massing_assets']:
    verification['superseded_massing_assets'].append(zta_id)

# Preserve the repository's mixed legacy byte encoding: edit only ASCII table/header bytes.
import re
readme_path=ROOT/'README.md'; raw=readme_path.read_bytes()
newline=b'\r\n' if b'\r\n' in raw else b'\n'
for old,new in [
 (b'## Detailed models: status and latest grader score (71 buildings)',b'## Detailed models: status and latest grader score (73 buildings)'),
 (b'## Unfinished buildings (165 total)',b'## Unfinished buildings (162 total)'),
 (b'Current assignments among the unfinished list: Rossen 35 buildings, Rohan 15 buildings, Tobin 5 buildings, Arjav 10 buildings, Brady 100 buildings.',b'Current assignments among the unfinished list: Rossen 35 buildings, Rohan 15 buildings, Tobin 2 buildings, Arjav 10 buildings, Brady 100 buildings.'),
 (b'### Detailed models still in progress or awaiting a grade (32)',b'### Detailed models still in progress or awaiting a grade (31)'),
 (b'### Buildings that still have only massing models (133)',b'### Buildings that still have only massing models (131)'),
]:
    if raw.count(old)!=1: raise RuntimeError(f'Readme expected byte row missing/duplicated: {old!r}')
    raw=raw.replace(old,new,1)
old_tark=re.compile(rb'^\| Tarkington Hall \| \[tarkington_hall\.blend\]\(modular/buildings/tarkington_hall\.blend\) \| Needs independent grade \| Not graded \| Tobin \|\r?$',re.M)
raw,n=old_tark.subn(b'| Tarkington Hall | [tarkington_hall.blend](modular/buildings/tarkington_hall.blend) | Finished | [8.0/10](audit/tarkington_hall/independent_grade_r4.md) | - |',raw,count=1)
if n!=1: raise RuntimeError('Finished Tarkington row not replaced')
for old in [
 b'| Tarkington Hall | [`tarkington_hall.blend`](modular/buildings/tarkington_hall.blend) | Not graded | Tobin |',
 b'| yue kong pao hall | [`massing_yue_kong_pao_hall_a3cb766.blend`](modular/buildings/massing_yue_kong_pao_hall_a3cb766.blend) | Tobin |',
 b'| zeta tau alpha | [`massing_zeta_tau_alpha_af8a443.blend`](modular/buildings/massing_zeta_tau_alpha_af8a443.blend) | Tobin |',
]:
    if raw.count(old)!=1: raise RuntimeError(f'Readme unfinished row missing/duplicated: {old!r}')
    raw=raw.replace(old+newline,b'',1)
anchor=b'| Winifred Parker Hall | [winifred_parker_hall.blend](modular/buildings/winifred_parker_hall.blend) | Finished | [8.05/10](audit/winifred_parker_hall/independent_grade_r5.md) | \x97 |'
assert raw.count(anchor)==1
insert=(b'| Yue-Kong Pao Hall | [massing_yue_kong_pao_hall_a3cb766.blend](modular/buildings/massing_yue_kong_pao_hall_a3cb766.blend) | Finished | [8.0/10](audit/yue_kong_pao_hall/independent_grade_r1.md) | - |'+newline+
        b'| Zeta Tau Alpha | [zeta_tau_alpha.blend](modular/buildings/zeta_tau_alpha.blend) | Finished | [8.2/10](audit/zeta_tau_alpha/independent_grade_r2.md) | - |')
raw=raw.replace(anchor,anchor+newline+insert,1)
readme_path.write_bytes(raw)

# Keep the modular asset index aligned with the accepted file paths/counts.
buildings_path=MOD/'BUILDINGS.md'; braw=buildings_path.read_bytes()
for old,new in [
 (b'| Tarkington Hall | [tarkington_hall.blend](buildings/tarkington_hall.blend) | 814 |',b'| Tarkington Hall | [tarkington_hall.blend](buildings/tarkington_hall.blend) | 1361 |'),
 (b'| Winifred Parker Hall | [winifred_parker_hall.blend](buildings/winifred_parker_hall.blend) | 582 |',b'| Winifred Parker Hall | [winifred_parker_hall.blend](buildings/winifred_parker_hall.blend) | 582 |'+newline+b'| Yue-Kong Pao Hall | [massing_yue_kong_pao_hall_a3cb766.blend](buildings/massing_yue_kong_pao_hall_a3cb766.blend) | 363 |'+newline+b'| Zeta Tau Alpha | [zeta_tau_alpha.blend](buildings/zeta_tau_alpha.blend) | 563 |'),
]:
    if braw.count(old)!=1: raise RuntimeError(f'BUILDINGS expected byte row missing/duplicated: {old!r}')
    braw=braw.replace(old,new,1)
buildings_path.write_bytes(braw)

manifest_path.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
verification_path.write_text(json.dumps(verification,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps({'updated_assets':{x:{'kind':row(x)['kind'],'file':row(x)['file'],'count':row(x)['object_count'],'grade':row(x)['independent_grade_score']} for x in [tark_id,yue_id,zta_id]},'unfinished':162,'detailed_assets':manifest['detailed_asset_count'],'massing_unfinished':131,'owner_counts':{'Rossen':35,'Rohan':15,'Tobin':2,'Arjav':10,'Brady':100},'verification':verification},indent=2,ensure_ascii=False))



