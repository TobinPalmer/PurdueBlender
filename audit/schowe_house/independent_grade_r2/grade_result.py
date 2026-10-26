import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
PROBE=HERE/'fresh_asset_probe.json'

def evaluate():
    p=json.loads(PROBE.read_text(encoding='utf-8'))
    assert p['gis_feature_id']==295 and p['gis_name']=='Schowe House'
    assert p['asset_sha256']=='05b7286ddab789bef1c7023a2d20bc2ada2daffc418991ec612bfe2ed340c4ef'
    criteria=[
      {'criterion':'Correct identity and source-backed footprint','score':2.0,'max_score':2.0,'status':'verified',
       'evidence':[f"Purdue GIS FID {p['gis_feature_id']} identifies {p['gis_name']} at {p['gis_address']} with {p['gis_area_m2']:.3f} m² plan area; Purdue campus map/PCRD page and the 2025 NIRPC panel independently support the Schowe House / PCRD identity.",
                   f"Against the converted GIS boundary, sampled perimeter wall-to-source max distance is {p['wall_to_gis_max_sampled_distance_m']:.3f} m, GIS-to-wall max is {p['gis_to_wall_max_sampled_distance_m']:.3f} m, mean GIS-to-wall distance is {p['gis_to_wall_mean_sampled_distance_m']:.3f} m. The local boundary deviations are consistent with the documented 0.14 m wall thickness plus door/garage interruptions."],
       'reason':'Identity and mapped source footprint are now well supported; the former multi-meter segment shift is repaired.'},
      {'criterion':'Position, orientation, and scale/dimensions','score':1.8,'max_score':2.0,'status':'mostly verified in campus coordinates',
       'evidence':[f"Structural wall bounds {p['wall_ground_bounds_m']} m align with the official GIS bounds {p['gis_bounds_m']} m to approximately 0.14 m at the extents.",
                   'The source uses the documented project-local lon/lat conversion, not a surveyed CRS. This standalone review did not independently verify the full-master placement or neighboring context.'],
       'reason':'Plan position and dimensions track the GIS outline closely, with a small deduction for the approximate transform and unreviewed master context.'},
      {'criterion':'Evidence-backed height, floors, and roof form','score':0.7,'max_score':2.0,'status':'height estimated; roof silhouette incomplete',
       'evidence':['The modeled ridge is about 5.85 m and overall roof height about 6.0 m, inferred from a single oblique photo; no measured elevation or confirmed floor count was found.',
                   'The retained image shows multiple cross-gabled roof volumes and tall chimney(s). The model uses one continuous two-slope roof sheet clipped to the footprint, with two small dormers; it does not reproduce the visible cross-gable junctions or chimneys.',
                   'The reference photo does not establish exact ridge/eave heights or hidden-side roof geometry.'],
       'reason':'Photo-supported roof material and a pitched main roof are present, but the source silhouette is materially more complex than the model and vertical dimensions remain estimates.'},
      {'criterion':'Facade, entrances, and distinctive architecture','score':1.3,'max_score':2.0,'status':'partially supported',
       'evidence':['The model has red-brown brick, gray slate, windows, a porch entry, garage doors, and a schematic interior; these features are generally supported by the 2025 source photo.',
                   'The source photo shows dark wood/shingle cladding on upper gable faces and strong cross-gable/chimney details. The model uses brick for the gable wall areas and omits the visible chimney(s).',
                   'Several roof undersides/intersections read as exposed light surfaces in the saved roof preview; hidden and rear elevations are not independently documented.'],
       'reason':'The base material palette and some facade openings match the reference, but upper cladding and distinctive roof/chimney details are missing, and the preview retains visible roof/wall artifacts.'},
      {'criterion':'Modular export, portability, and complete evidence','score':2.0,'max_score':2.0,'status':'verified in fresh Blender reopen',
       'evidence':[f"A clean Blender {p['blender_version']} process reopened the exact SHA {p['asset_sha256']} and found scene {p['scene']}, collection {p['collection']}, {p['object_count']} objects, and {p['mesh_count']} meshes.",
                   'Three generated textures are packed, no linked libraries are present, and the building-specific evidence folder has raw GIS, official identification, the address-associated 2025 image, source register, metrics, and previews.'],
       'reason':'The library and evidence package are self-contained and reopen successfully.'}
    ]
    score=round(sum(c['score'] for c in criteria),2)
    return {'building':'Purdue Center for Regional Development / Schowe House','asset_id':p['asset_path'].split('/')[-1].removesuffix('.blend'),
       'asset_path':p['asset_path'],'asset_sha256':p['asset_sha256'],'grader':'independent_grader_subagent','grade_date':'2026-10-26',
       'score':score,'max_score':10,'passing_threshold':8,'status':'PASS' if score>=8 else 'FAIL','criteria':criteria,
       'evidence':{'fresh_asset_probe':str(PROBE.relative_to(ROOT)).replace('\\','/'),'gis_feature_id':p['gis_feature_id'],
          'gis_bounds_m':p['gis_bounds_m'],'evaluated_asset_bounds_m':p['evaluated_bounds_m'],
          'wall_ground_vertex_count':p['wall_ground_vertex_count'],'wall_ground_edge_segment_count':p['wall_ground_edge_segment_count'],
          'gis_to_wall_max_sampled_distance_m':p['gis_to_wall_max_sampled_distance_m'],
          'wall_to_gis_max_sampled_distance_m':p['wall_to_gis_max_sampled_distance_m'],
          'gis_to_wall_mean_sampled_distance_m':p['gis_to_wall_mean_sampled_distance_m'],
          'packed_images':[i['name'] for i in p['images'] if i['packed']],
          'visual_references':['audit/schowe_house/preview_three_quarter.png','audit/schowe_house/preview_roof.png','audit/schowe_house/sources/schowe_house_pcrd_photo_2025_crop.png']},
       'findings':['The GIS-to-wall multi-meter shift is corrected; sampled wall perimeter now agrees within 0.55 m maximum and about 0.003 m mean, with deviations concentrated around interrupted ground-level openings and wall thickness.',
          'Reconstruct the visible cross-gabled roof junctions and upper dark wood/shingle gable cladding from the saved 2025 photo; the current continuous two-slope roof is materially simplified.',
          'Add the prominent brick chimney(s) visible in the source photo and repair the pale exposed roof/wall intersection surfaces seen in the roof preview.',
          'Keep ridge/eave heights and hidden elevations labeled as estimates unless stronger source evidence appears.']}

result=evaluate()
(HERE/'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
