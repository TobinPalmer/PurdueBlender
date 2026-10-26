"""Reproducible independent ABE evaluator. Run with Python; it invokes Blender."""
from pathlib import Path
import json, subprocess, sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
ASSET=ROOT/'modular/buildings/agricultural_and_biological_engineering_abe.blend'
EVIDENCE=ROOT/'audit/abe/evidence.json'
VALIDATION=ROOT/'audit/abe/validation.json'
MANIFEST=ROOT/'modular/manifest.json'
PROBE=HERE/'blender_probe.py'
PROBE_RESULT=HERE/'blender_probe.json'
BLENDER=ROOT.parent/'blender/blender-4.5.15-windows-x64/blender.exe'

def evaluate():
    assert BLENDER.is_file() and ASSET.is_file()
    run=subprocess.run([str(BLENDER),'--background','--python',str(PROBE)],cwd=ROOT,capture_output=True,text=True,timeout=300)
    if not PROBE_RESULT.is_file():
        raise RuntimeError(f'Blender probe did not produce output; exit={run.returncode}\nstdout={run.stdout}\nstderr={run.stderr}')
    probe=json.loads(PROBE_RESULT.read_text(encoding='utf-8'))
    ev=json.loads(EVIDENCE.read_text(encoding='utf-8'))
    val=json.loads(VALIDATION.read_text(encoding='utf-8'))
    manifest=json.loads(MANIFEST.read_text(encoding='utf-8'))
    entry=next(x for x in manifest['assets'] if x['id']=='agricultural_and_biological_engineering_abe')
    sources=ev['sources']
    criteria=[
      {"name":"Identity and source-backed footprint","score":2.0,"max_score":2,
       "evidence":["Purdue GIS FeatureServer feature 406 matches BLDG_ABBR=ABE, full building name and address 225 S University Street (audit/abe/evidence/purdue_abe_gis_feature_406.json).","Saved asset's shell is tagged with source feature 406; independent symmetric boundary distances are recorded in blender_probe.json."],
       "findings":"Identity is well matched and the shell is generated from the GIS ring. The source is a cartographic footprint rather than a measured wall survey; the builder simplified vertices by up to roughly 0.75 m."},
      {"name":"Position, orientation, scale and dimensions","score":0.5,"max_score":2,
       "evidence":[f"Manifest placement origin is {probe['manifest_placement_origin_xy_m']} m, while the exported shell remains at campus-coordinate centroid {probe['shell_centroid_asset_xy_m']} m.",f"Offset from the expected local footprint centroid is {probe['shell_centroid_error_if_local_m']:.2f} m; distance to GIS coordinates in the project's campus frame is {probe['shell_centroid_error_if_project_coordinates_m']:.3f} m.","The standalone shell dimensions and orientation can be compared to the GIS outline in blender_probe.json."],
       "findings":"The saved .blend stores the shell in campus/project coordinates rather than around a local origin. Since this detailed asset is also assigned the manifest Placement origin, the modular instance would apply placement twice and be displaced by hundreds of meters. Footprint shape and dimensions agree, but local-coordinate placement contract fails."},
      {"name":"Evidence-backed height, floors and roof","score":1.0,"max_score":2,
       "evidence":["GIS attributes record NUM_LEVELS/CountOfFLO=6 and Extrution=58 with no documented units; MSKTD describes a three-storey existing building and five-storey replacement facility (audit/abe/evidence.json).","The shell height is explicitly estimated at 18 m; the overview render shows flat roof/parapet and a schematic mechanical screen."],
       "findings":"Floor program has useful independent support, but the exact six-level composition and 18 m height are not established by as-built elevations. The evidence set offers no calibrated roof plan or elevation; roof equipment and silhouette remain estimated."},
      {"name":"Facade, entrances and distinctive architecture","score":0.8,"max_score":2,
       "evidence":["The Farm Progress photo is cited for brick, pale stone framing and the 1928 marker; preview images are audit/abe/evidence/abe_exterior_overview.png and abe_entry_detail.png."],
       "findings":"The model represents the photo cues, but the entrance was assigned to a long GIS edge because the image cannot locate it; bay spacing, curtain-wall wing, facade cadence and the historic/new addition division are illustrative. Renders show repeated generic windows and a simple portal, with no georeferenced facade plan."},
      {"name":"Modular export, portability and complete evidence","score":1.3,"max_score":2,
       "evidence":[f"Blender reopened {probe['asset_path']} and found the expected {probe['collection']} collection, building ID and source feature metadata; {probe['collection_object_count']} collection objects, {probe['mesh_object_count']} meshes.",f"Unpacked image dependencies: {probe['unpacked_file_images']}; linked libraries: {probe['linked_library_paths']}.","Evidence includes raw GIS JSON, a planning PDF, architect/history/photo source records, two renders, and a reopen validator/report."],
       "findings":"The collection is portable in external dependencies and evidence is thorough. The local-coordinate contract mismatch prevents correct collection instancing, and the shared manifest object_count is stale (1482 vs actual 956), which the coordinator should correct."}
    ]
    score=sum(c['score'] for c in criteria)
    result={"score":round(score,2),"max_score":10,"pass_threshold":8,"passed":score>=8,
      "criteria":criteria,"evidence":{"evaluator":"audit/agricultural_and_biological_engineering_abe_independent_grade/evaluate.py","blender_probe":"audit/agricultural_and_biological_engineering_abe_independent_grade/blender_probe.py","blender_probe_result":"audit/agricultural_and_biological_engineering_abe_independent_grade/blender_probe.json","builder_evidence":"audit/abe/evidence.json","builder_validation":"audit/abe/validation.json","overview":"audit/abe/evidence/abe_exterior_overview.png","entry_detail":"audit/abe/evidence/abe_entry_detail.png","asset":"modular/buildings/agricultural_and_biological_engineering_abe.blend","manifest":"modular/manifest.json"},
      "findings":["FAIL: convert geometry to the documented local frame by subtracting placement_origin_xy_m before export, then rerun independent position/footprint comparisons.","Fix the manifest object_count to the reopened asset's true collection object count after final acceptance.","Floor count and overall height are supported only approximately; façade and entrance placement remain illustrative."],
      "method":"The evaluator reopened the saved asset in Blender, read its exported collection, mesh and metadata, measured the GIS shell, compared the shell to raw GIS coordinates both in campus and expected local frames, checked unpacked images and linked libraries, and read source/validation evidence."}
    (HERE/'result.json').write_text(json.dumps(result,indent=2)+"\n",encoding='utf-8')
    return result
if __name__=='__main__':
    result=evaluate(); print(json.dumps(result,indent=2)); sys.exit(0 if result['passed'] else 1)
