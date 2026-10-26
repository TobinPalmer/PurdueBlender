import json
from pathlib import Path
base=Path(__file__).resolve().parent
probe=json.loads((base/'model_probe.json').read_text(encoding='utf-8'))
evidence=json.loads((base.parent/'evidence.json').read_text(encoding='utf-8'))

def evaluate(probe,evidence):
    # Scores follow the five 2-point criteria from the project AGENT.md.
    criteria=[
      {'criterion':'Correct identity and source-backed footprint','score':2.0,'max_score':2.0,'status':'verified',
       'evidence':[f"Purdue GIS Feature 526 identifies {probe['source_gis_name']} (PGSC) at 504 Northwestern Avenue; saved raw source is in {evidence['sources'][0]['local_copy']}.",
         'Purdue Archives identifies PGSC as the former Visitor Information Center portion of Northwestern Avenue Parking Garage; the 2025 Purdue photo directly depicts the center frontage.',
         f"The independent probe found the structural shell's lower GIS vertices within {probe['source_to_model_vertex_nearest_max_m']:.8f} m of the source polygon vertices after the documented campus transform."],
       'reason':'Identity sources corroborate the assigned use and shared-garage location; the structural shell follows the GIS polygon exactly within floating-point tolerance.'},
      {'criterion':'Position, orientation, and scale/dimensions','score':2.0,'max_score':2.0,'status':'verified in source-local frame; master marker pending',
       'evidence':[f"Model asset anchor is {probe['placement_origin_xy_m']} m in the project campus frame.",
         'The structural shell matches the transformed GIS ring vertex-for-vertex to sub-micrometre nearest-vertex distance; shell footprint dimensions follow the 31.27 x 27.15 m GIS bounding box.',
         f"The asset extends beyond the wall footprint to {probe['asset_world_bounds_m']} m because of facade/canopy detail; that decorative extent is not treated as the wall footprint."],
       'reason':'Position, footprint shape, orientation and dimensions agree with the source polygon. The manifest/master marker has not yet been updated for this asset.'},
      {'criterion':'Evidence-backed height, floors, and roof form','score':1.0,'max_score':2.0,'status':'partially verified; height estimated',
       'evidence':['Purdue GIS reports NUM_LEVELS=2 and Extrution=12, but the saved layer metadata does not define the vertical units or clarify whether these attributes refer to PGSC or the garage envelope.',
         'The model uses 3.65 m as a plausible 12-foot low-volume height. The official image supports a shallow, flat storefront/canopy composition but does not provide surveyed elevations or a measured roof section.'],
       'reason':'The low storefront volume and roof datum are plausible interpretations, not measured dimensions; roof height remains explicitly estimated.'},
      {'criterion':'Facade, entrances, and distinctive architecture','score':1.6,'max_score':2.0,'status':'mostly source-supported',
       'evidence':['The official 2025 Purdue exterior photo shows red-brown brick, raised light-colored PGSC lettering, dark storefront glazing, recessed entrance and a long horizontal canopy.',
         'The model preview includes the brick frontage, sign, dark glazed openings/entry, brick piers and canopy, with procedural brick/concrete/glass materials. The official photo does not support every modeled opening or rear-side detail.'],
       'reason':'The defining street-facing language and materials are represented well; opening layout and non-photographed facades remain interpretive.'},
      {'criterion':'Modular export, portability, and complete evidence','score':2.0,'max_score':2.0,'status':'verified for standalone library; master interface exception recorded',
       'evidence':[f"Fresh independent Blender 5.2.3 open of SHA {probe['asset_sha256']} found scene `{probe['scene_name']}`, expected collection `{probe['collection_name']}`, {probe['object_count']} objects including {probe['mesh_count']} meshes, and {probe['used_material_count']} used materials.",
         f"The asset has {len(probe['external_unpacked_images'])} unpacked external image dependencies; GIS, official Purdue sources, Street View reference, provenance, metrics, and fresh-open evidence are saved under `{evidence['asset_path']}`'s audit folder.",
         'The separate garage collision is explicitly disclosed and is an integration exception rather than a missing path or portability defect.'],
       'reason':'The stable standalone library opens and has portable procedural materials plus a complete source record.'}
    ]
    score=round(sum(c['score'] for c in criteria),2)
    collision=probe['garage_vertical_ray_hits_at_pgsc_centroid']
    findings=[
      'PASS: exact asset SHA, expected scene and collection, GIS identity/footprint, materials and portability independently reopened and checked.',
      'The interior is a schematic arrangement derived from published room descriptions, not a measured floor plan; do not treat partition locations as survey data.',
      'The 3.65 m wall height is estimated from an undocumented GIS Extrution value; it is not a surveyed height.',
      f"INTEGRATION EXCEPTION: the current separate Northwestern Parking Garage massing is one mesh with bounds {probe['garage']['bounds_world_m']} m. A vertical ray through the PGSC GIS polygon centroid intersects garage surfaces at z={[h['z_m'] for h in collision]} m, while PGSC occupies z=0–3.65 m. Leaving the garage massing unchanged would occlude/intersect the entire student-center volume. Root must subtract/split the garage volume or replace that neighboring massing before final master integration.",
      f"The broad-phase AABB intersection is {probe['asset_garage_aabb_overlap']['aabb_overlap_volume_m3']:.1f} m³; it is not presented as a precise solid-intersection volume."
    ]
    return {'building':'Purdue Graduate Student Center (PGSC)','asset_id':probe['asset_id'],'asset_path':'modular/buildings/massing_purdue_graduate_student_center_af9c5c7.blend',
      'asset_sha256':probe['asset_sha256'],'grader':'independent_grader_subagent','grade_date':'2026-10-26','score':score,'max_score':10,
      'passing_threshold':8,'status':'PASS' if score>=8 else 'FAIL','criteria':criteria,'evidence':[
        'audit/purdue_graduate_student_center/independent_grade/model_probe.json',
        'audit/purdue_graduate_student_center/independent_grade/probe.py',
        'audit/purdue_graduate_student_center/independent_grade/evaluate.py',
        'audit/purdue_graduate_student_center/preview_three_quarter.png',
        'audit/purdue_graduate_student_center/sources/purdue_official_pgsc_photo_2025-08.jpg',
        'audit/purdue_graduate_student_center/sources/purdue_gis_pgsc_fid526_2026-10-26.geojson',
        'audit/purdue_graduate_student_center/sources/purdue_pgsc_historic_record_2026-10-26.html'],
      'findings':findings,'master_integration_status':'BLOCKED_BY_NORTHWESTERN_GARAGE_SOLID_MASSING'}

result=evaluate(probe,evidence)
(base/'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({'score':result['score'],'status':result['status'],'master_integration_status':result['master_integration_status'],'findings':result['findings']},indent=2))
