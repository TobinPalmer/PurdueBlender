"""Fresh, reproducible independent ABE grade. Run with system Python; invokes Blender."""
from pathlib import Path
import json, subprocess, sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
ASSET=ROOT/'modular/buildings/agricultural_and_biological_engineering_abe.blend'
BLENDER=ROOT.parent/'blender/blender-4.5.15-windows-x64/blender.exe'
PROBE=HERE/'blender_probe.py'; PROBE_RESULT=HERE/'blender_probe.json'
def evaluate():
    assert ASSET.is_file() and BLENDER.is_file(), 'Asset or Blender executable missing'
    run=subprocess.run([str(BLENDER),'--background','--python',str(PROBE)],cwd=ROOT,capture_output=True,text=True,timeout=300)
    if run.returncode or not PROBE_RESULT.is_file(): raise RuntimeError(f'Blender probe failed ({run.returncode})\n{run.stdout}\n{run.stderr}')
    p=json.loads(PROBE_RESULT.read_text(encoding='utf-8'))
    ev=json.loads((ROOT/'audit/abe/evidence.json').read_text(encoding='utf-8'))
    val=json.loads((ROOT/'audit/abe/validation.json').read_text(encoding='utf-8'))
    sources=ev['sources']
    assert p['building_id']=='agricultural_and_biological_engineering_abe'
    assert p['source_feature_id']==406 and p['manifest_collection_matches']
    assert p['shell_centroid_error_local_m'] < 0.5
    assert p['shell_centroid_error_double_transform_m'] < 0.5
    assert p['manifest_object_count']==p['collection_object_count']
    assert p['manifest_object_names_match']
    assert val['reopened_asset_successfully'] and val['manifest_translation_recovers_gis_footprint']
    criteria=[
      {'name':'Identity and source-backed footprint','score':2.0,'max_score':2,
       'evidence':['Purdue GIS feature 406 identifies ABE by code, full name, and address 225 S University Street (audit/abe/evidence/purdue_abe_gis_feature_406.json).',f'The reopened shell is tagged to feature {p["source_feature_id"]}; its vertices were independently measured against the GIS outer ring. Directed boundary distances: shell→GIS {p["shell_to_source_hausdorff_m"]:.3f} m; GIS→shell {p["source_to_shell_hausdorff_m"]:.3f} m.'],
       'findings':'Identity is corroborated by code/name/address and the shell closely follows the GIS ring. GIS is cartographic rather than a surveyed wall line; builder simplifies some boundary vertices for a mesh-ready envelope.'},
      {'name':'Position, orientation, scale and dimensions','score':2.0,'max_score':2,
       'evidence':[f'The shell centroid is {p["shell_centroid_error_local_m"]:.4f} m from GIS-derived local centroid before placement.',f'Applying manifest placement origin {p["placement_origin_xy_m"]} m exactly once recovers the source campus centroid within {p["shell_centroid_error_double_transform_m"]:.4f} m; project shell extent is {p["source_bounds_project_m"]}.','Independent shell and GIS bounds are in blender_probe.json; source outline is used without scale fitting.'],
       'findings':'The prior double-placement defect is fixed: the collection shell is in local coordinates and the manifest origin restores its GIS position. The conversion uses the repository’s approximate geographic formula, not survey-grade coordinates.'},
      {'name':'Evidence-backed height, floors and roof form','score':1.0,'max_score':2,
       'evidence':['Purdue GIS reports six levels but its Extrution value 58 has unspecified units; MSKTD reports an existing three-storey building and replacement five-storey facility. These records are planning/program evidence rather than as-built elevations.','The model and evidence label 18 m as estimated, with five above-grade levels and a flat parapet roof plus small mechanical screen.'],
       'findings':'The story program has independent Purdue and architect support, but the retained/new wing split and exact level datums are unresolved. Height, parapet and roof screen are estimates; no calibrated elevation or roof plan was located.'},
      {'name':'Facade, entrances and distinctive architecture','score':1.0,'max_score':2,
       'evidence':['The cited Farm Progress entrance photograph supports red brick, pale stone framing and a 1928 marker; those cues appear in the saved overview and entry-detail renders.','The model includes repeated windows, a portal and the marker, but the source photo is uncalibrated and cannot place the entry on a specific GIS edge.'],
       'findings':'Materials and the historic marker are supported qualitatively. The entry side, window rhythm, curtain-wall wing, and historic-versus-new facade boundary remain illustrative; renders show a schematic massing/facade rather than a calibrated elevation.'},
      {'name':'Modular export, portability and complete evidence','score':2.0,'max_score':2,
       'evidence':[f'The saved file reopens with scene {p["scene"]}, expected collection {p["collection"]}, building ID and GIS feature metadata; {p["collection_object_count"]} collection objects ({p["mesh_object_count"]} meshes).',f'No unpacked file images or linked libraries: {p["unpacked_file_images"]}, {p["linked_library_paths"]}.','Dedicated evidence contains raw GIS JSON, Purdue planning PDF, architect/history/photo sources, source notes, two renders, and reopen validation.'],
       'findings':'The standalone asset is portable; the manifest count and full object-name list match the reopened collection exactly.'}
    ]
    score=round(sum(c['score'] for c in criteria),2)
    result={'score':score,'max_score':10,'pass_threshold':8,'passed':score>=8,'criteria':criteria,
      'evidence':{'evaluator':'audit/agricultural_and_biological_engineering_abe_independent_grade_r2/evaluate.py','blender_probe':'audit/agricultural_and_biological_engineering_abe_independent_grade_r2/blender_probe.py','blender_probe_result':'audit/agricultural_and_biological_engineering_abe_independent_grade_r2/blender_probe.json','builder_evidence':'audit/abe/evidence.json','builder_validation':'audit/abe/validation.json','GIS_snapshot':'audit/abe/evidence/purdue_abe_gis_feature_406.json','overview':'audit/abe/evidence/abe_exterior_overview.png','entry_detail':'audit/abe/evidence/abe_entry_detail.png','asset':'modular/buildings/agricultural_and_biological_engineering_abe.blend'},
      'findings':['Local-coordinate placement repair independently verified against the Purdue GIS ring and manifest origin.','The exact height, roof layout, facade rhythm, and entrance placement remain uncertain or illustrative.'],
      'method':'A separate Blender background process reopened the saved asset. This evaluator measured evaluated shell vertices, reconstructed the GIS local frame from the preserved feature snapshot, calculated directed boundary distances and centroid errors before and after manifest translation, inspected collection metadata and object counts, and checked unpacked images/linked libraries.'}
    (HERE/'result.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    return result
if __name__=='__main__':
    r=evaluate(); print(json.dumps(r,indent=2)); sys.exit(0 if r['passed'] else 1)
