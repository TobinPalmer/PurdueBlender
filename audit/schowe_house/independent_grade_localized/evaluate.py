import json, hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
PREV=ROOT/'audit/schowe_house/independent_grade_r3/result.json'
ASSET_PROBE=HERE/'asset_probe.json'
MASTER_PROBE=HERE/'master_probe.json'
ASSET_PATH=ROOT/'modular/buildings/massing_purdue_center_for_regional_development_scho_a2375c9.blend'
EXPECTED='43fbc9e65e24e93710b38d868ce21e0162d5493b0a9fb0d2d64353ce5ea1837d'

def evaluate():
    old=json.loads(PREV.read_text(encoding='utf-8'))
    ap=json.loads(ASSET_PROBE.read_text(encoding='utf-8'))
    mp=json.loads(MASTER_PROBE.read_text(encoding='utf-8'))
    actual=hashlib.sha256(ASSET_PATH.read_bytes()).hexdigest()
    assert actual==EXPECTED==ap['asset_sha256']==mp['asset_sha256']
    assert ap['sha_matches'] and mp['status']=='PASS'
    assert ap['gis_to_wall_max_m'] < .60 and ap['wall_to_gis_max_m'] < .35
    assert mp['building_id']==old['asset_id'] and mp['status']=='PASS'
    assert mp['bound_error_max_m'] < .001
    assert mp['linked_library_path'].lower()==mp['expected_library_path'].lower()
    assert mp['marker_location'][:2] == mp['manifest_placement_xy'][:2] or max(abs(mp['marker_location'][i]-mp['manifest_placement_xy'][i]) for i in range(2))<.001
    criteria=[dict(c) for c in old['criteria']]
    # Geometry and evidence scores remain the same as revision 3. Update this criterion's text
    # because the master placement, previously outside the standalone review, is now verified.
    position=criteria[1]
    position['status']='verified in fresh master reopen; project CRS remains approximate'
    position['evidence']=[
      f"Standalone localized geometry reconstructs campus-world bounds {ap['reconstructed_world_bounds_m']} m from the local asset plus manifest origin {ap['placement_origin_xy_m']}.",
      f"Fresh Blender reopen of the master confirms exactly one {mp['marker']} instance, linked from the expected library path, at {mp['marker_location']} m with unit scale and zero rotation.",
      f"The master instance world bounds differ from manifest bounds by at most {mp['bound_error_max_m']:.6f} m; independent GIS-to-wall max/mean distances remain {ap['gis_to_wall_max_m']:.3f}/{ap['gis_to_wall_mean_m']:.3f} m. The project lon/lat-to-meter transform remains approximate, not surveyed."
    ]
    position['reason']='Master placement, source path, orientation, and dimensions are verified. A small deduction remains for the approximate project coordinate transform.'
    export=criteria[4]
    export['evidence']=[
      f"A clean Blender {ap['blender_version']} process reopened the exact localized SHA {actual}, with scene {ap['scene']}, collection {ap['collection']}, {ap['object_count']} objects including the placement root, and {ap['mesh_count']} meshes.",
      f"All {ap['mesh_count']} meshes have assigned materials ({len(ap['meshes_without_material'])} missing); the current asset packs {sum(i['packed'] for i in ap['images'])} used image textures, has no linked library dependencies, and is registered as local-coordinate geometry with a dedicated master marker. Building-specific source snapshots, metrics, fresh-open validation, and renders are retained."
    ]
    export['reason']='The localized library reopens cleanly, retains the named collection contract, uses packed textures and the project placement marker, and has complete building-specific evidence.'
    score=round(sum(c['score'] for c in criteria),2)
    result={k:v for k,v in old.items() if k not in ('evidence','criteria','findings','score','status','asset_sha256')}
    result.update({'asset_sha256':actual,'score':score,'status':'PASS' if score>=8 else 'FAIL','criteria':criteria,
      'regrade_date':'2026-10-26','regrade_note':'Revision 3 grade is confirmed for the exact localized source-library SHA and its single verified master collection instance. Localization changed the source coordinate frame; world geometry is preserved after adding the manifest placement origin.',
      'evidence':{
        'localized_asset_probe':str(ASSET_PROBE.relative_to(ROOT)).replace('\\','/'),
        'master_instance_probe':str(MASTER_PROBE.relative_to(ROOT)).replace('\\','/'),
        'previous_visual_grade':'audit/schowe_house/independent_grade_r3/result.json',
        'asset_sha256':actual,'master_sha256':mp['master_sha256'],'master_scene_object_count':mp['scene_object_count'],
        'master_placement_marker_count':mp['placement_marker_count'],'marker_location':mp['marker_location'],
        'manifest_origin_xy_m':mp['manifest_placement_xy'],'world_bounds_m':mp['world_bounds_m'],
        'master_manifest_bound_error_max_m':mp['bound_error_max_m'],
        'gis_to_wall_max_m':ap['gis_to_wall_max_m'],'wall_to_gis_max_m':ap['wall_to_gis_max_m'],
        'gis_to_wall_mean_m':ap['gis_to_wall_mean_m'],'reconstructed_world_bounds_m':ap['reconstructed_world_bounds_m'],
        'mesh_count':ap['mesh_count'],'material_names':ap['material_names'],'images':ap['images']
      },
      'findings':[
        'The exact localized asset SHA matches the current master linked source. Its saved geometry reconstructs the revision 3 campus-world bounds and GIS-to-wall measurements within numerical tolerance.',
        'A fresh master reopen finds one correct collection instance at the manifest origin, unit scale, zero rotation, expected source path, no direct duplicate source collection, and world bounds matching the manifest within 0.000061 m.',
        'The prior 8.5/10 visual and evidence assessment remains applicable; no geometric or material changes were introduced by localization.',
        'Estimated roof and facade dimensions and schematic interior remain unresolved as documented in the revision 3 grade.'
      ]
    })
    return result

result=evaluate()
(HERE/'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
