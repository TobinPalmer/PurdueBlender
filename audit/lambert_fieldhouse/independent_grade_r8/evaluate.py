import json, os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / 'audit' / 'lambert_fieldhouse'
GRADE = AUDIT / 'independent_grade_r8'
CANDIDATE = AUDIT / 'lambert_fieldhouse_r8_candidate.blend'
EXPECTED_SHA256 = 'b0e931109230641be77e8d3fc64cadf7d77c4e7d5f318e7fcf3103de7836124f'

def evaluate():
    probe = json.loads((GRADE / 'fresh_probe.json').read_text(encoding='utf-8'))
    sha = __import__('hashlib').sha256(CANDIDATE.read_bytes()).hexdigest()
    assert sha == EXPECTED_SHA256, f'Candidate changed: {sha}'
    criteria = [
      {'criterion':'Correct identity and source-backed footprint','score':1.8,'max_score':2.0,
       'evidence':'The candidate clearly depicts Ward L. Lambert Fieldhouse and Gymnasium. The exported ground footprint is named as Purdue ArcGIS feature 261 and the saved evidence records the 20-edge source polygon. Purdue Athletics confirms the current six-lane, 200 m track; the retained centerline perimeter in the previous validation was 199.989 m. The archives record supports the hall dimensions and gym story count. The archived source does not georegister the separate volumes, and the model documentation properly acknowledges that uncertainty.'},
      {'criterion':'Position, orientation, and scale/dimensions','score':1.4,'max_score':2.0,
       'evidence':'The fieldhouse roof is documented at the archival 303 x 172 ft dimensions and the gym is documented at 210 x 110 ft. The GIS polygon is reproduced with aligned perimeter segments. But historic hall/gym allocations are not georegistered by the available source and are explicitly an illustrative placement hypothesis. In the exterior render, perimeter bands/lines continue conspicuously beyond the apparent building volume, and the fresh-open world bounds extend to y=-99.82 m. The source evidence itself says parts of the projected hall rectangle cross open/notched GIS areas.'},
      {'criterion':'Evidence-backed height, floors, and roof form','score':1.5,'max_score':2.0,
       'evidence':'The archival source supports a one-story fieldhouse and four-story gym, and the candidate renders a long arched fieldhouse roof plus a flat gym roof. The relative forms are plausible, but eaves/ridge heights, floor-to-floor heights, truss spacing, current roof profiles, and gym localization remain schematic or unmeasured. The close exterior view is dominated by a large, nearly flat gray roof surface; it does not show useful roof finish scale.'},
      {'criterion':'Facade, entrances, and distinctive architecture','score':1.5,'max_score':2.0,
       'evidence':'R8 improves on R7 with brick image-texture/material detail, glass-block glazing, concrete bands and pilasters, a glazed entrance, signage, and an event/interior view showing seating, track and hurdles. These are supported at a broad level by archival/contemporary visual cues. The facade cadence and entry treatment remain partly generic; the conspicuous pale GIS-outline bands/lines look detached from the modeled facade in the review view. The interior event framing is tightly cropped, hides much of the fieldhouse, and clips the floor text; the other interior render mostly shows the roof and exterior rather than the track interior.'},
      {'criterion':'Modular export, portability, and complete evidence','score':1.6,'max_score':2.0,
       'evidence':'Blender 5.2.3 freshly opened the exact R8 candidate. The expected Asset_lambert_fieldhouse collection exists, with 972 objects (967 meshes), no linked libraries, and a brick image texture packed in the file. There are 39 materials used. However, 24 hurdle component meshes have no material slots, contradicting the earlier round-6 validation’s all-mesh-material claim; R8 also lacks a revision-specific structured evidence/validation record in the audit folder. The asset is a candidate and is not the production path modular/buildings/lambert_fieldhouse.blend.'},
    ]
    score = round(sum(c['score'] for c in criteria), 1)
    evidence = [
      {'type':'independent fresh-open inspection','path':str((GRADE/'fresh_probe.json').relative_to(ROOT)),'summary':f"Loaded with Blender 5.2.3. Export collection found; {probe['objects']} objects, {probe['mesh_count']} mesh objects, {probe['materials_used']} materials used; {len(probe['unassigned_meshes'])} meshes have no assigned material; image texture packed; no linked libraries."},
      {'type':'render review','path':'audit/lambert_fieldhouse/exterior_round8.png','summary':'Three-quarter exterior shows the major volumes, but long pale perimeter bands/lines visibly float beyond the apparent walls; roof finish and facade remain schematic at this view.'},
      {'type':'render review','path':'audit/lambert_fieldhouse/interior_round8.png','summary':'Composition largely shows the broad roof and outside wall, so it is not an effective inspection view of the track interior.'},
      {'type':'render review','path':'audit/lambert_fieldhouse/interior_event_round8.png','summary':'Shows seating, hurdles and parts of the track but is cropped tightly; part of the floor lettering is clipped and large empty gray areas dominate.'},
      {'type':'source evidence','path':'audit/lambert_fieldhouse/evidence_round6.json','summary':'Documents the GIS feature 261, historical plan dimensions/story counts, Purdue Athletics 6-lane 200 m track, visual references, and material uncertainties. This predates R8 and should be refreshed for a final revision.'},
      {'type':'primary-source verification','url':'https://purduesports.com/facilities/lambert-fieldhouse','summary':'Purdue Athletics identifies the facility and describes a six-lane, 200-meter track.'},
      {'type':'primary-source verification','url':'https://archives.lib.purdue.edu/agents/corporate_entities/559?filter_fields%5B%5D=subjects&filter_values%5B%5D=Inventory+control','summary':'Purdue Archives listing describes the historical 172 by 303 foot fieldhouse.'},
      {'type':'prior independent grade','path':'audit/lambert_fieldhouse/independent_grade_r7.md','summary':'R7 scored 7.8/10 and called out flat exterior materials, generic facade/entrance, sparse interior/event details, and detached perimeter lines. R8 improves materials and some interior details, but the lines and presentation/registration problems remain.'}
    ]
    findings = [
      'R8 has materially improved brick surface appearance and event/interior props relative to R7, but it does not pass the 8/10 gate: 7.8/10.',
      'The GIS perimeter-derived bands still read as detached thin linework in the exterior render. Resolve their relationship to the built facade or exclude them from the building render and clearly identify them as site/context geometry.',
      'Improve the entry and gym facade with evidence-backed distinctive detail, and produce a true interior view with the roof not obstructing the track, seating, infield and lighting.',
      'Assign materials to all 24 hurdle component meshes, refresh R8 evidence and validation records, and rerun the fresh-open integrity check before requesting the next grade.',
      'The model’s volume registration and roof heights remain hypotheses, since available archival dimensions are not georeferenced and do not measure elevations.'
    ]
    return {'score':score,'max_score':10,'pass_threshold':8,'passed':score>=8,'candidate':str(CANDIDATE.relative_to(ROOT)),'candidate_sha256':sha,'criteria':criteria,'evidence':evidence,'findings':findings,'review_date':'2026-10-26','blender_version':'5.2.3'}

if __name__ == '__main__':
    result=evaluate()
    (GRADE/'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))
