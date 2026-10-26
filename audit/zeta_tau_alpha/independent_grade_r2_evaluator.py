from __future__ import annotations
import hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
FOLDER=Path(__file__).resolve().parent
ASSET=ROOT/'modular/buildings/zeta_tau_alpha.blend'
EXPECTED='1e9b54a032ac508e3e473e1757b6edce6ee8724b581c884d54e984572ed8a7af'
SCORECARD=[('Identity and source-backed footprint',2.0,2.0),('Campus position, orientation, and scale',1.5,2.0),('Evidence-backed height, floors, and roof',1.4,2.0),('Facade, entrances, and distinctive details',1.5,2.0),('Technical integrity, materials, interior, and evidence',1.8,2.0)]
def evaluate():
    sha=hashlib.sha256(ASSET.read_bytes()).hexdigest()
    if sha!=EXPECTED: raise RuntimeError(f'Frozen R2 candidate changed: {sha}')
    e=json.loads((FOLDER/'independent_grade_r2_extract.json').read_text(encoding='utf-8'))
    m=json.loads((FOLDER/'independent_grade_r2_metrics.json').read_text(encoding='utf-8'))
    b=json.loads((FOLDER/'build_report_r2.json').read_text(encoding='utf-8'))
    v=json.loads((FOLDER/'reopen_validation_r2.json').read_text(encoding='utf-8'))
    assert e['fresh_process_reopen'] and e['sha256']==sha and e['object_count']==563 and e['mesh_count']==562
    assert e['material_count']==13 and e['materialless_meshes']==[] and e['material_images_all_packed']
    assert v['sha256']==sha and v['pediment_text_outward_side_check']=='PASS'
    assert round(m['iou'],6)==1.0 and m['centroid_error_m']<0.001
    assert abs(b['measured_asset_bbox_max_z_m']-e['world_bounds_xyz'][2][1])<0.001
    total=round(sum(x[1] for x in SCORECARD),2)
    return {'reviewed_sha256':sha,'score':total,'passing_threshold':8.0,'passes':total>=8.0,'criteria':[{'criterion':n,'score':s,'max_score':mx} for n,s,mx in SCORECARD],
      'verified':{'fresh_blender_reopen':True,'collection_count':e['object_count'],'mesh_count':e['mesh_count'],'material_count':e['material_count'],'all_images_packed':True,'gis_shell_iou':m['iou'],'centroid_error_m':m['centroid_error_m'],'text_outward_side_check':v['pediment_text_outward_side_check'],'height_consistent_with_report':True},
      'unverified':['final master placement and orientation','survey-grade wall line','measured height/story count','architectural interior layout']}
if __name__=='__main__': print(json.dumps(evaluate(),indent=2))
