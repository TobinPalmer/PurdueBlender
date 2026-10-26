from pathlib import Path
import json, hashlib
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'audit'/'purdue_fire_department'
GRADE=BASE/'independent_grade_localized'
EXPECTED_ASSET='6a20209ae3db99c028a16d7df11e42a87577b8bee29afc5e0ead98a779b03817'
EXPECTED_MASTER='fd42c154b5812f16bcf8cf21560600d3e46d4358fd82c07c7395fdbb1208aaa2'

def evaluate():
    probe=json.loads((GRADE/'fresh_master_probe.json').read_text(encoding='utf-8'))
    asset=json.loads((BASE/'asset_validation.json').read_text(encoding='utf-8'))
    footprint=json.loads((GRADE/'localized_footprint_probe.json').read_text(encoding='utf-8'))
    master_record=json.loads((ROOT/'audit'/'master_sync_fire_drug_schowe_2026-10-26.json').read_text(encoding='utf-8'))
    master_fire=next(x for x in master_record['checks'] if x['id']=='massing_purdue_fire_department_520430b')
    evidence=json.loads((BASE/'evidence.json').read_text(encoding='utf-8'))
    assert probe['status']=='PASS'
    assert probe['asset_sha256']==EXPECTED_ASSET==asset['asset_sha256']==footprint['asset_sha256']==master_fire['asset_sha256']
    assert asset['verified_after_fresh_open'] is True and asset['object_count_all_types']==100
    assert asset['mesh_object_count']==99 and asset['assigned_material_meshes']==99 and not asset['external_image_paths']
    master_hash=hashlib.sha256((ROOT/'purdue_campus_master.blend').read_bytes()).hexdigest()
    assert master_hash==EXPECTED_MASTER==master_record['master_sha256']
    assert probe['marker_name']=='Placement_massing_purdue_fire_department_520430b'
    assert probe['linked_library']==probe['expected_library']
    assert probe['marker_rotation']==[0.0,0.0,0.0] and probe['marker_scale']==[1.0,1.0,1.0]
    assert max(abs(probe['marker_location'][i]-probe['manifest_origin_xy_m'][i]) for i in range(2))<0.001
    assert probe['status']=='PASS' and master_fire['status']=='PASS' and master_fire['errors']==[]
    assert master_fire['bound_error_max_m']<0.001
    assert footprint['feature_id']==211 and footprint['abbr']=='DMNT'
    assert max(footprint['source_to_model_max_vertex_error_m'],footprint['model_to_source_max_vertex_error_m'])<0.005
    criteria=[
      {'criterion':'Correct identity and source-backed footprint','score':2.0,'max_score':2.0,'status':'verified','evidence':[
        'Purdue Archives identifies the Clayton W. Dement Fire Station (DMNT) as a three-bay brick fire station: https://collections.lib.purdue.edu/campus/buildings/53',
        'Purdue Facilities Operations confirms PUFD is located at 1250 W Third Street: https://www.purdue.edu/operations/operations-maintenance/wp-content/uploads/sites/7/2025/12/bd-manual.pdf',
        'Official GIS FID 211 identifies DMNT at 1250 3rd Street. After localization, the model shell matches its 14 source vertices in local coordinates within %.6f m.'%max(footprint['source_to_model_max_vertex_error_m'],footprint['model_to_source_max_vertex_error_m'])],
       'reason':'The building identity is confirmed by primary sources; this is the Purdue Fire Department home station.'},
      {'criterion':'Position, orientation, and scale/dimensions','score':2.0,'max_score':2.0,'status':'verified in the project coordinate transform','evidence':[
        'Fresh Blender 5.2.3 reopen confirmed marker location %s matches manifest XY %s within 0.001 m.'%(probe['marker_location'],probe['manifest_origin_xy_m']),
        'Marker rotation is zero and scale is unit. The marker links the exact intended relative library path.',
        'Reconstructed world bounds from fresh local asset geometry and marker position differ from manifest world bounds by at most %.8f m.'%max(abs(probe['reconstructed_world_bounds_m'][i][j]-probe['manifest_world_bounds_m'][i][j]) for i in range(3) for j in range(2))],
       'reason':'Localization preserved the previously verified source footprint and the master instance places it at the manifest position. Absolute position remains in the project’s documented approximate local conversion, not a survey CRS.'},
      {'criterion':'Evidence-backed height, floors, and roof form','score':1.0,'max_score':2.0,'status':'partially verified; total height estimated','evidence':[
        'Official GIS lists two levels and an extrusion value of 15 without documenting the unit/meaning.',
        'Model bounds remain 0–14.6 m. The roof-height split and raised apparatus hall are image-based estimates; no surveyed elevation source was found.'],
       'reason':'Floor count and broad silhouette have support, but numeric heights are unverified and remain estimates.'},
      {'criterion':'Facade, entrances, and distinctive architecture','score':1.4,'max_score':2.0,'status':'mostly supported, some interpretation','evidence':[
        'Purdue archival record identifies brick construction and a three-bay station; current Street View shows two clear vehicle doors, a red canopy, personnel entry, brick office wing, and taller ribbed-metal hall.',
        'Rendered preview and source panoramas were directly compared; façade materials/details are assigned and packaged in the asset. Source snapshots and URLs remain in audit/purdue_fire_department/evidence.json.'],
       'reason':'Principal materials and massing are represented. The exact third-bay position/configuration is interpreted from the historic three-bay description because only two doors are clear in the current frontal panorama.'},
      {'criterion':'Modular export, portability, and complete evidence','score':2.0,'max_score':2.0,'status':'verified','evidence':[
        'Fresh Blender 5.2.3 open confirms 99 mesh objects, all 99 assigned materials, no external file images, expected scene/collection, and 100 total collection objects including AssetRoot.',
        'Current asset SHA-256: %s.'%EXPECTED_ASSET,
        'Fresh master audit and independent master open both pass; no superseded massing collection is directly linked alongside the detail instance.'],
       'reason':'Stable collection/path contract and self-contained materials are preserved after localization.'}
    ]
    score=round(sum(c['score'] for c in criteria),2)
    return {'building':'Clayton W. Dement Fire Station (Purdue University Fire Department)','asset_id':'massing_purdue_fire_department_520430b','asset_path':'modular/buildings/massing_purdue_fire_department_520430b.blend','asset_sha256':EXPECTED_ASSET,'master_path':'purdue_campus_master.blend','master_sha256':master_hash,'grader':'independent_grader_subagent','grade_date':'2026-10-26','score':score,'max_score':10,'passing_threshold':8,'status':'PASS' if score>=8 else 'FAIL','criteria':criteria,'fresh_reopen_checks':{'asset':asset,'master':probe,'integration_audit':master_fire,'localized_footprint':footprint},'findings':['The localized asset preserves the prior geometry and footprint fit; the world placement is recreated by the master marker.','Master marker uses the exact modular library path, correct XY, zero rotation, and unit scale; reconstructed world bounds agree with the manifest within tolerance.','Roof height is estimated; the current front view visibly supports two bay doors while the historic Purdue record calls the station three-bay. Exact third-bay configuration remains uncertain.','Interior layout is not modeled because available evidence does not support one.']}

if __name__=='__main__':
    result=evaluate()
    (Path(__file__).with_name('result.json')).write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({'status':result['status'],'score':result['score'],'asset_sha256':result['asset_sha256'],'master_sha256':result['master_sha256']},indent=2))


