from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
AUDIT = ROOT / 'audit/massing_hockmeyer_hall_of_structural_biology_hock_4d524ab'
ASSET = ROOT / 'modular/buildings/massing_hockmeyer_hall_of_structural_biology_hock_4d524ab.blend'

def evaluate() -> dict:
    build = json.loads((AUDIT / 'build_evidence.json').read_text(encoding='utf-8'))
    reopen = json.loads((AUDIT / 'reopen_validation.json').read_text(encoding='utf-8'))
    gis = json.loads((AUDIT / 'sources/purdue_building_shapes_hock.json').read_text(encoding='utf-8-sig'))
    attrs = gis['features'][0]['attributes']
    renders = [AUDIT / 'renders' / n for n in ('hockmeyer_exterior_oblique.png','hockmeyer_courtyard_entry.png','hockmeyer_roof_plan.png')]
    photo = AUDIT / 'sources/purdue_hockmeyer_exterior_2009.jpg'
    shell_error = float(reopen['max_source_to_shell_xy_vertex_error_m'])
    exact_ring = (attrs.get('FID') == build.get('source_feature_id') == 669 and
                  'Hockmeyer' in attrs.get('BUILDING_N','') and
                  reopen.get('ring_vertices_source') == reopen.get('ring_vertices_shell_lower') == reopen.get('ring_vertices_shell_upper') == 58 and shell_error < 0.001)
    all_renders = all(p.is_file() and p.stat().st_size > 100_000 for p in renders)
    collection_ok = reopen.get('collection_found') and reopen.get('expected_collection') == build.get('collection')
    dependencies = reopen.get('external_unpacked_file_dependencies')
    scene_ok = bool(reopen.get('scene_name_matches'))

    criteria = [
      {'name':'Correct identity and source-backed footprint','score':1.75,'max_score':2,
       'evidence':[f"Purdue BuildingShapes feature FID {attrs.get('FID')} is named {attrs.get('BUILDING_N')!r}; code HOCK and address are also recorded.",f"The reopened shell matches all {reopen.get('ring_vertices_source')} exterior-ring vertices from the official Purdue feature; maximum XY vertex error is {shell_error:.6f} m.","The previous Shape__Area conflict is credibly resolved: feature area is in native EPSG:3857, and the observed ratio to locally projected area matches expected Web Mercator inflation within about 0.2%.","OSM way 283274991 is independent identity/outline corroboration, but a localized outline difference remains (reported maximum Hausdorff distance about 16.27 m); no survey plan distinguishes the edge."],
       'deduction':'Small deduction for a localized difference between the official GIS perimeter and independent OSM outline, despite a transparent, defensible source choice.'},
      {'name':'Position, orientation, and scale/dimensions','score':1.75,'max_score':2,
       'evidence':[f"Asset keeps all 58 source vertices in the repo campus coordinate frame; direct reopen comparison reports {shell_error:.6f} m maximum XY error.","The builder applies the repository's documented lon/lat-to-local-meter approximation to the official GIS geometry; OSM broadly overlaps as an independent check.","No survey control points or independent measured dimensions are available; localized GIS/OSM outline disagreement remains."],
       'deduction':'Chosen-source placement and shape are strongly verified, but independent surveyed dimensions/registration are unavailable.'},
      {'name':'Evidence-backed height, floors, and roof form','score':1.25,'max_score':2,
       'evidence':["Purdue Biological Sciences' 2010 article and current emergency plan support three occupied stories; the emergency plan also states penthouse and basement.","The shell is three stories and 11.4 m high, but the 3.8 m floor-to-floor scaffold is explicitly an estimate, not measured height.","A flat roof cap is a massing placeholder; a separate penthouse block was removed because the available official photos do not locate or dimension it, despite the plan confirming its presence.","Undocumented GIS NUM_LEVELS=6 and Extrution=60 are preserved as raw fields and not treated as height evidence."],
       'deduction':'Story count is supported. Quantitative height, penthouse form/location, and detailed roof form remain unverified or estimated.'},
      {'name':'Facade, entrances, and distinctive architecture','score':1.5,'max_score':2,
       'evidence':["Official Purdue 2009 exterior photo directly shows red brick, large pale opaque upper cladding, extensive blue-green multi-story courtyard glazing, and glazed arrival frontage.","Revised renders show red brick, a broad pale-clad upper volume, and enlarged curtainwall strips on the shell's re-entrant/courtyard edges; this addresses the prior review's major omitted facade cues.","The images are not registered to the GIS polygon, so facade-to-edge alignment and bay placement remain schematic. No doorway/canopy is modeled because its precise location is not georeferenced."],
       'deduction':'Major materials and courtyard glazing are now represented, but facade registration/detail and exact entrance placement are still uncertain.'},
      {'name':'Modular export, portability, and complete evidence','score':1.5,'max_score':2,
       'evidence':[f"Saved asset exists: {ASSET.is_file()}; expected exported collection {build.get('collection')!r} is present with {reopen.get('collection_object_count')} objects.",f"Reopen validation reports no external unpacked file dependencies: {dependencies!r}.",f"All three review renders exist and exceed 100 KB: {all_renders}; raw Purdue GIS, official photo/page snapshots, emergency plan, OSM, layer metadata, build evidence, and reopen evidence are present.",f"Expected scene ID does not match reopened scene: expected {reopen.get('expected_scene_name')!r}, actual {reopen.get('actual_scene_name')!r}. Blender 4.5.15 truncation is explicitly recorded; collection contract passes={bool(collection_ok)}."],
       'deduction':'Strong collection/export evidence and portable asset, but the expected scene-name contract remains a recorded compatibility failure.'}
    ]
    score = round(sum(c['score'] for c in criteria),2)
    findings = [
      f"{'PASS' if score >= 8 else 'FAIL'} ({score}/10; minimum passing standard 8/10).",
      "The r1 area criticism is resolved: the apparent 73% area mismatch comes from native Web Mercator area distortion, not an incorrect target area; the chosen shell follows official Purdue FID 669.",
      "Do not claim the 11.4 m height or penthouse/roof geometry as measured; obtain elevation/roof-plan evidence if vertical accuracy is required.",
      "Resolve the full expected scene-name contract in the compatible Blender version/export workflow; reopen currently confirms collection success but not the expected scene ID.",
      "Retain the localized Purdue/OSM perimeter difference and unregistered facade/entrance placement as stated limitations."
    ]
    return {'building_id':build['building_id'],'asset':str(ASSET.relative_to(ROOT)).replace('\\','/'),'evaluator':'independent Hockmeyer Hall review r2','score':score,'max_score':10,'pass_threshold':8,'passed':score>=8,'criteria':criteria,'evidence':{'build_evidence':'audit/massing_hockmeyer_hall_of_structural_biology_hock_4d524ab/build_evidence.json','reopen_validation':'audit/massing_hockmeyer_hall_of_structural_biology_hock_4d524ab/reopen_validation.json','visual_review':[str(p.relative_to(ROOT)).replace('\\','/') for p in renders]+[str(photo.relative_to(ROOT)).replace('\\','/')],'gis_feature_id':attrs.get('FID'),'source_to_shell_xy_vertex_error_m':shell_error,'expected_collection_found':bool(collection_ok),'expected_scene_name_matches':scene_ok,'external_unpacked_file_dependencies':dependencies,'all_review_renders_present':all_renders},'findings':findings}

if __name__ == '__main__':
    result=evaluate()
    out=Path(__file__).with_name('result.json')
    out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2,ensure_ascii=False))
