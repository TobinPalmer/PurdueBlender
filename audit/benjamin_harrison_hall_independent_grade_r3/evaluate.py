import json, hashlib
from pathlib import Path
BASE=Path(__file__).resolve().parent

def evaluate():
    p=json.loads((BASE/'probe_actual.json').read_text(encoding='utf-8'))
    rebuilt=json.loads((BASE/'probe_rebuilt.json').read_text(encoding='utf-8'))
    facade=json.loads((BASE/'source_snapshots'/'facade_photo_comparison.json').read_text(encoding='utf-8'))
    source=json.loads((BASE/'source_review.json').read_text(encoding='utf-8'))
    reopened=json.loads((BASE/'collection_export_actual_reopened.json').read_text(encoding='utf-8'))
    foot=p['footprint']; man=p['manifest']; names=set(p['object_names'])
    anchors=sorted(set(a for cue in facade['observed_cues_and_model_objects'] for a in cue['model_objects']))
    anchor_check={a:a in names for a in anchors}
    gis_ok=(foot['gis_feature_id']==85 and foot['gis_name']=='Benjamin Harrison Residence Hall'
      and foot['gis_distinct_vertices']==28 and foot['model_base_distinct_vertices']==28
      and foot['symmetric_nearest_vertex_error_m']<0.02)
    placement_ok=(man['id']=='benjamin_harrison_hall' and man['file']=='buildings/benjamin_harrison_hall.blend'
      and man['collection']=='Asset_benjamin_harrison_hall' and man['scene']=='Building_benjamin_harrison_hall'
      and man['names_exact'] and gis_ok)
    export_ok=(man['object_count']==220 and man['actual_object_count']==220 and man['names_exact']
      and not p['export_cameras_or_lights'] and not p['unpacked_external_images'] and not p['linked_libraries']
      and reopened['object_count']==220 and not reopened['camera_or_light']
      and not reopened['unpacked_external_images'] and not reopened['linked_libraries'])
    cue_ok=all(anchor_check.values()) and facade['source_image_sha256']==source['photo']['sha256']
    criteria=[
      {'name':'Correct identity and source-backed footprint','max_points':2,'points':2 if gis_ok else 0,
       'status':'verified' if gis_ok else 'failed',
       'evidence':f"Official Purdue GIS FID 85 identifies {foot['gis_name']} at {foot['gis_address']}; independently projected 28-vertex polygon matches the evaluated base perimeter (28 vertices; symmetric nearest-vertex error {foot['symmetric_nearest_vertex_error_m']:.6f} m).",
       'limitation':'Official campus-map polygon is not a certified survey.'},
      {'name':'Position, orientation, and scale/dimensions','max_points':2,'points':2 if placement_ok else 0,
       'status':'verified' if placement_ok else 'failed',
       'evidence':f"Manifest placement origin {man['origin_xy_m']} m plus the local frame maps the full GIS vertex pattern to the model; source ring comparison independently confirms plan shape, scale and orientation. Evaluated local XYZ bounds: {p['evaluated_model_bounds_local_m']} m.",
       'limitation':'Position, orientation and dimensions are awarded from GIS/manifest geometry only. No dimensions or heading were inferred from the unregistered perspective photograph; the local meters-per-degree transform is approximate.'},
      {'name':'Evidence-backed height, floors, and roof form','max_points':2,'points':1,
       'status':'partially verified',
       'evidence':'Purdue OEP source states three major wings, 8 stories in each north/south wing and 2 in the central section; those relative masses and story bands are represented in the reopened model and fresh views.',
       'limitation':'No authoritative total elevation, floor datums, floor-to-floor dimensions or roof-form evidence. The photo is perspective and is not used to infer vertical dimensions.'},
      {'name':'Facade, entrances, and distinctive architecture','max_points':2,'points':1.5 if cue_ok else 0,
       'status':'photo-backed cues; dimensions and orientation unverified' if cue_ok else 'failed anchor validation',
       'evidence':'Direct visual comparison of the archived Purdue hero photo with the fresh Cam_West_Entrance render supports four broad cues: red-brown brick on wings/connector; repeated vertically stacked narrow windows; a light perforated screen across the lower connector; and glazed entrance adjoining a broad light canopy. The listed Blender object anchors all exist in the reopened export: '+', '.join(anchors)+'.',
       'limitation':'Photograph compass direction and camera registration are unknown. It cannot establish wing-to-compass assignment, exact window width/spacing, screen dimensions/pattern, canopy dimensions, lettering, unseen elevations, or precise facade geometry.'},
      {'name':'Modular export, portability, and complete evidence','max_points':2,'points':2 if export_ok else 0,
       'status':'verified' if export_ok else 'failed',
       'evidence':f"Canonical builder reran in an isolated replica and emitted three fresh views. Actual asset reopened in Blender {p['blender_version']}; named collection has 220 objects and exact manifest membership. Collection-only export reopened with 220 objects, no camera/light objects, no unpacked external images and no linked libraries. Source snapshots and image are recorded with SHA256 hashes.",
       'limitation':'Opening asset emits an unavailable legacy BLENDER_EEVEE identifier warning in Blender 4.5; builder switches to EEVEE Next in-memory for successful renders.'}
    ]
    score=round(sum(c['points'] for c in criteria),2)
    result={'score':score,'max_score':10,'passing_threshold':8,'pass':score>=8,'criteria':criteria,
      'evidence':{'actual_probe':str(BASE/'probe_actual.json'),'rebuilt_probe':str(BASE/'probe_rebuilt.json'),
        'facade_comparison':str(BASE/'source_snapshots'/'facade_photo_comparison.json'),
        'reopened_collection_export':str(BASE/'collection_export_actual_reopened.json'),
        'source_review':str(BASE/'source_review.json'),'rebuild_log':str(BASE/'canonical_builder_rebuild.log'),
        'views':[str(BASE/'views'/f) for f in ('purdue_harrison_hall_exterior_hero.jpg','cam_hero_perspective.png','cam_topdown_footprint.png','cam_west_entrance.png')],
        'original_asset_sha256':p['asset_sha256'],'isolated_rebuild_sha256':rebuilt['asset_sha256'],'photo_anchor_validation':anchor_check},
      'findings':[
        'The new official exterior photograph supports broad color/material and composition cues but remains unregistered; it did not change or validate placement, orientation, dimensions, exact facade geometry, or roof.',
        'GIS identity and plan geometry are independently verified; local placement/scale/orientation derive from that polygon and the manifest origin.',
        'Height, floor datums, total height and roof remain partly/unverified; the OEP source supports story arrangement only.',
        'No building/model/builder/shared-index files were changed for this independent grade; the canonical builder ran against an isolated copy.'
      ]}
    return result

if __name__=='__main__':
    result=evaluate()
    (BASE/'result.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2,ensure_ascii=False))
