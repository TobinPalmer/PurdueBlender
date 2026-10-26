"""Independent rubric evaluator for the committed CQE building candidate."""
from pathlib import Path
import hashlib, json
ROOT = Path(__file__).resolve().parents[2]
GRADE = ROOT / 'audit' / 'massing_cary_quadrangle_east_cqe_independent_grade'
CANDIDATE_COMMIT = '5d99c49085f6755c474145e95bc20a582523901b'

def sha256(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''): h.update(block)
    return h.hexdigest()

def evaluate():
    probe=json.loads((GRADE/'blender_probe.json').read_text(encoding='utf-8'))
    build=json.loads((ROOT/'audit/massing_cary_quadrangle_east_cqe_230c813/build_evidence.json').read_text(encoding='utf-8'))
    source=json.loads((ROOT/'audit/massing_cary_quadrangle_east_cqe_230c813/source_record.json').read_text(encoding='utf-8'))
    asset=ROOT/'modular/buildings/massing_cary_quadrangle_east_cqe_230c813.blend'
    source_snapshot=ROOT/'audit/massing_cary_quadrangle_east_cqe_230c813/sources/purdue_building_shapes_fid639_cqe_2026-10-25.geojson'
    image_paths=[
      'audit/massing_cary_quadrangle_east_cqe_230c813/cqe_detailed_preview.png',
      'audit/massing_cary_quadrangle_east_cqe_230c813/cqe_top_preview.png',
      'audit/massing_cary_quadrangle_east_cqe_230c813/cqe_orthophoto_footprint_overlay.png',
      'audit/massing_cary_quadrangle_east_cqe_230c813/sources/purdue_archives_cary_quadrangle_image_159.jpg',
      'audit/massing_cary_quadrangle_east_cqe_230c813/sources/indiana_2023_orthophoto_cqe.jpg']
    p=probe['source_feature']; a=probe['asset']
    bdev=a['wall_vs_source_boundary_distance_m']
    area_delta=abs(a['wall_footprint_area_m2']-p['projected_area_m2'])
    criteria=[
      {'criterion':'Correct identity and source-backed footprint','score':2.0,'max_score':2.0,'status':'verified','evidence':f"Reopened saved asset and raw GIS GeoJSON agree on FID 639, BLDG_ABBR=CQE, and Franklin Levering Cary Quadrangle (East). The wall-shell plan is derived from the GIS ring; independent projected polygon area is {p['projected_area_m2']:.3f} m² versus {a['wall_footprint_area_m2']:.3f} m² for the shell (absolute difference {area_delta:.3f} m²). Maximum source-to-shell boundary deviation is {bdev['source_to_wall_max']:.3f} m, consistent with the documented 0.12 m simplification tolerance. The source polygon overlays the 2023 roof in the saved orthophoto image.",'limitations':[]},
      {'criterion':'Position, orientation, and scale/dimensions','score':1.9,'max_score':2.0,'status':'verified_with_limitations','evidence':f"Source and model share the documented campus coordinate frame; independently measured asset extent is {a['bounds_world_m_xyz']} m. Orthophoto overlay supports north-south orientation and site placement. Plan area and perimeter agree closely with projected FID 639 geometry (source {p['projected_perimeter_m']:.3f} m; shell {a['wall_footprint_perimeter_m']:.3f} m).",'limitations':['Coordinates use the project’s local lon/lat-to-meter approximation rather than a surveyed campus control or independent geodetic registration; the small deduction reflects that placement/scale limitation.']},
      {'criterion':'Evidence-backed height, floors, and roof form','score':0.8,'max_score':2.0,'status':'partially_verified','evidence':'Historic archive search-index description supports three stories plus basement; the saved 2023 orthophoto supports a long, complex roof mass with interruptions. The asset has three visible window levels, a gable roof, and dormer-like protrusions.','limitations':[f"GIS NUM_LEVELS={p['NUM_LEVELS']} and CountOfFLO={p['CountOfFLO']} conflict with the historic three-stories-plus-basement description. GIS Extrution={p['Extrution']} has no documented units; treating it as feet to obtain 14.63 m is only a tentative assumption. Neither roof ridge/eaves heights nor exact dormer count/profile are established by the cited material."]},
      {'criterion':'Facade, entrances, and distinctive architecture','score':0.6,'max_score':2.0,'status':'weakly_supported','evidence':'The historic description supports broad Tudor-Gothic character and brick/stone/concrete materials. A preserved Purdue Archives Cary Quadrangle image shows general Cary architecture, including Gothic arches and prominent vertical entrance elements.','limitations':['The archival photograph is not labeled as CQE and cannot verify this building’s elevation; visually, its prominent entrance towers are not represented in the model. No CQE-specific facade elevation or entrance image is supplied. Window bay rhythm/count, pilasters, specific pointed entrance, entry side and central placement are schematic or inferred from site layout; do not treat those as verified details.']},
      {'criterion':'Modular export, portability, and complete evidence','score':1.8,'max_score':2.0,'status':'verified_with_limitations','evidence':f"Reopened {probe['scene']} and its expected {probe['collection']} collection. It contains {a['mesh_objects']} mesh objects, all with identity transforms, no external object libraries, and measured bounds {a['bounds_world_m_xyz']}. Dedicated build/evidence/source records and previews exist; source snapshots include the GIS feature, 2023 orthophoto, and general Cary archival photograph.",'limitations':['The archival record facts are taken from a search-index result because the direct page was blocked; the underlying CQE-specific elevation source is unavailable.']}
    ]
    total=round(sum(x['score'] for x in criteria),2)
    result={'score':total,'max_score':10,'status':'pass' if total>=8 else 'fail','candidate_commit':CANDIDATE_COMMIT,'evaluated_utc_date':'2026-10-25','asset_path':'modular/buildings/massing_cary_quadrangle_east_cqe_230c813.blend','criteria':criteria,'evidence':{'direct_reopen_probe':'audit/massing_cary_quadrangle_east_cqe_independent_grade/blender_probe.json','candidate_build_evidence':'audit/massing_cary_quadrangle_east_cqe_230c813/build_evidence.json','candidate_source_record':'audit/massing_cary_quadrangle_east_cqe_230c813/source_record.json','independent_source_comparison':{'source_feature':p,'wall_shell':a,'boundary_deviation_m':bdev,'area_difference_m2':area_delta},'reviewed_visual_evidence':image_paths,'sha256':{str(x.relative_to(ROOT)).replace('\\','/'):sha256(x) for x in [asset,source_snapshot]+[ROOT/x for x in image_paths] if x.exists()},'method':'Independently reopened the committed .blend in Blender 4.5.15, inspected the named collection and model previews, read raw source snapshots, projected the source polygon with the documented campus conversion, and compared it directly to the wall-shell boundary. Evaluator authored and run by a reviewer who did not build the asset.'},'findings':['The building identity and GIS-derived plan footprint are strongly supported and pass.','Do not treat 14.63 m as measured: Extrution=48 has undocumented units, and the record’s two floor-count fields conflict with the historic three-stories-plus-basement account.','The model’s exact facade, entrance placement, dormer form/count, and Tudor-Gothic detailing remain unverified because available architectural photos are Cary-complex context, not CQE-specific elevations.','Current result is below the required 8/10 threshold. Obtain CQE-specific elevations or labeled close photography, and resolve vertical/source-unit uncertainty before requesting a fresh independent grade.']}
    return result

if __name__=='__main__':
    result=evaluate()
    (GRADE/'result.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2,ensure_ascii=False))

