import json, hashlib
from pathlib import Path

BASE = Path(__file__).resolve().parent

def evaluate(probe_path=None, evidence_path=None, sources_path=None):
    """Grade the reopened asset against AGENT.md's 5 criteria using saved probe/source evidence."""
    probe_path = Path(probe_path or BASE/'probe_actual.json')
    evidence_path = Path(evidence_path or BASE/'source_review.json')
    p = json.loads(probe_path.read_text(encoding='utf-8'))
    src = json.loads(evidence_path.read_text(encoding='utf-8'))
    reopened = json.loads((BASE/'collection_export_reopened.json').read_text(encoding='utf-8'))
    foot = p['footprint']; man = p['manifest']
    footprint_ok = (foot['gis_feature_id']==85 and foot['gis_name']=='Benjamin Harrison Residence Hall'
                    and foot['gis_distinct_vertices']==28 and foot['model_base_distinct_vertices']==28
                    and foot['symmetric_nearest_vertex_error_m'] < 0.02)
    placement_ok = (man['id']=='benjamin_harrison_hall' and man['file']=='buildings/benjamin_harrison_hall.blend'
                    and man['collection']=='Asset_benjamin_harrison_hall' and man['scene']=='Building_benjamin_harrison_hall'
                    and p['evaluated_model_bounds_local_m'][2][0] > -0.1)
    export_ok = (man['names_exact'] and man['object_count']==man['actual_object_count']
                 and not p['export_cameras_or_lights'] and not p['unpacked_external_images']
                 and not p['linked_libraries'] and p['collection_export_probe']['exists']
                 and reopened['object_count']==man['actual_object_count'] and not reopened['camera_or_light']
                 and not reopened['unpacked_external_images'] and not reopened['linked_libraries'])
    criteria = [
      {'name':'Correct identity and source-backed footprint','max_points':2,'points':2 if footprint_ok else 0,
       'status':'verified' if footprint_ok else 'failed',
       'evidence':f"Official Purdue GIS feature 85 identifies {foot['gis_name']} at {foot['gis_address']}; independent projection yields {foot['gis_distinct_vertices']} vertices against {foot['model_base_distinct_vertices']} model base vertices with symmetric nearest-vertex error {foot['symmetric_nearest_vertex_error_m']:.6f} m.",
       'limitation':'The Purdue campus-map polygon is not a certified survey.'},
      {'name':'Position, orientation, and scale/dimensions','max_points':2,'points':2 if placement_ok and footprint_ok else 0,
       'status':'verified' if placement_ok and footprint_ok else 'failed',
       'evidence':f"Manifest origin {man['origin_xy_m']} m was applied to the local GIS frame; the model base ring matches the full source vertex set and orientation. Evaluated asset bounds are {p['evaluated_model_bounds_local_m']} m in local XYZ.",
       'limitation':'Project local meters-per-degree conversion is approximate; the footprint does not establish surveyed wall thickness or exact interior dimensions.'},
      {'name':'Evidence-backed height, floors, and roof form','max_points':2,'points':1,
       'status':'partially verified',
       'evidence':'Purdue OEP page documents three major wings, with north and south wings at 8 stories and center section at 2 stories; these relative masses are represented in the reopened scene and fresh preview.',
       'limitation':'No authoritative total elevation, floor-to-floor heights, floor datum, or roof-form source was found. Story count does not verify modeled 30.35 m total bounds or roof geometry.'},
      {'name':'Facade, entrances, and distinctive architecture','max_points':2,'points':0,
       'status':'unverified',
       'evidence':'Fresh renders show brick wall surfaces, repetitive window bands, an entrance canopy, signage, and a west solar screen. The official housing page only states two wings linked by common areas; its official hall-photo gallery feed confirms photo assets exist but supplied no facade descriptions or measured elevation. The award page cited by the builder lists a Harrison Hall employee and does not itself support an exterior entrance photograph.',
       'limitation':'Appearance alone is not evidence. No reviewed source image or dimensioned elevation verifies facade material/colors, window rhythm, screen geometry, sign, or entrance details.'},
      {'name':'Modular export, portability, and complete evidence','max_points':2,'points':2 if export_ok else 0,
       'status':'verified' if export_ok else 'failed',
       'evidence':f"Canonical builder ran on an isolated copy and generated fresh views; actual asset reopened in Blender {p['blender_version']}. Export collection has {man['actual_object_count']} objects with exact manifest names, no cameras/lights in export, no unpacked external images or linked libraries; collection-only export probe was written ({p['collection_export_probe']['bytes']} bytes) and reopened independently with the same 220 objects, no cameras/lights, and no external references. GIS, OEP, housing HTML, and gallery-feed JSON source snapshots are archived beside this report.",
       'limitation':'Opening the legacy scene emits Blender 4.5 warning that engine identifier BLENDER_EEVEE is unavailable; builder switches to BLENDER_EEVEE_NEXT for renders. Scene still opens and previews render.'}
    ]
    score=round(sum(c['points'] for c in criteria),2)
    findings=[
      'Footprint/identity/manifest placement are independently verified against official Purdue GIS feature 85.',
      'The canonical builder reruns successfully against the supplied seed in an isolated replica; its output hashes differ from the original because it saves refreshed metadata/render state, while the original asset, builder, and building evidence hashes were recorded unchanged.',
      'Height and roof remain unverified. Facade/entrance details need a direct source-image comparison or dimensioned elevation before those points can be awarded.',
      'The builder evidence record overstates the award page as supporting an entrance photograph; the saved award page is a winner-list and does not establish a facade image.'
    ]
    return {'score':score,'max_score':10,'passing_threshold':8,'pass':score>=8,'criteria':criteria,'evidence':{'probe':str(probe_path),'source_review':str(evidence_path),'asset_sha256':p['asset_sha256'],'fresh_builder_rebuild_probe':str(BASE/'probe_rebuilt.json')},'findings':findings}

if __name__=='__main__':
    result=evaluate()
    (BASE/'result.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2,ensure_ascii=False))
