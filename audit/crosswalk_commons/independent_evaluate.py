import json
from pathlib import Path

def evaluate():
  root = Path(__file__).resolve().parents[2]
  folder = root / 'audit/crosswalk_commons'
  probe = json.loads((folder / 'independent_grade_probe.json').read_text(encoding='utf-8'))
  sources = json.loads((folder / 'sources_and_assumptions.json').read_text(encoding='utf-8'))
  evidence = json.loads((folder / 'build_evidence.json').read_text(encoding='utf-8'))
  criteria = [
  {
    'name': 'Correct identity and source-backed footprint', 'score': 2.0, 'max_score': 2,
    'evidence': 'OSM way 231217849 identifies Crosswalk Commons at 925 Hilltop Drive; its 14-vertex WGS84 ring is retained by the mesh with independently measured maximum vertex-to-ground-vertex error %.6f m.' % probe['max_source_vertex_nearest_error_m'],
    'finding': 'Strong identity/plan evidence, with the limitation that OSM is crowd-sourced rather than survey control.'
  },
  {
    'name': 'Position, orientation, and scale/dimensions', 'score': 2.0, 'max_score': 2,
    'evidence': 'The source ring is transformed with the repository local conversion and matches the saved mesh vertices. Reopened Blender bounds are %s m, consistent with the source-derived outline.' % json.dumps(probe['dimensions_m']),
    'finding': 'Horizontal placement and outline are source-backed; the project conversion and mapped footprint carry stated uncertainty.'
  },
  {
    'name': 'Evidence-backed height, floors, and roof form', 'score': 1.3, 'max_score': 2,
    'evidence': 'Official 2023 operator gallery photos visibly support three levels and a low, nearly flat parapet. The reopened asset is 9.5 m tall. No dimensioned elevation or measured roof-height source is provided; the model evidence labels 9.5 m as an estimate.',
    'finding': 'Floor count and general roof silhouette are plausible from photographs, but vertical scale remains estimated and rooftop form is not documented.'
  },
  {
    'name': 'Facade, entrances, and distinctive architecture', 'score': 0.8, 'max_score': 2,
    'evidence': 'Official operator photos show pale horizontal siding above a ground-level dark fascia, red-brick piers, large common-area glazing, and a substantial stone entry wall/canopy. The candidate has pale upper wall zones and repeated windows, but the ground facade reads mostly as repeated blue windows with sparse narrow brick accents; the distinctive stone wall, broad dark glazing/fascia composition and actual entrance position are not reproduced or geolocated.',
    'finding': 'Facade material vocabulary is partly present, but characteristic ground-floor composition and entrance mass need evidence-led revision; no source supports the chosen entrance side.'
  },
  {
    'name': 'Modular export, portability, and complete evidence', 'score': 2.0, 'max_score': 2,
    'evidence': 'Independently reopened in Blender 4.5.15: expected scene/collection, one mesh named Crosswalk Commons, seven material slots, no modifiers or external image dependencies. Four operator exterior stills, raw OSM response, source notes, and explicit uncertainty records are saved.',
    'finding': 'Portable single-mesh export and source evidence are complete for the claims made.'
  }
]
  score = round(sum(c['score'] for c in criteria), 2)
  return {
  'building_id': 'massing_crosswalk_commons_7c01ecd',
  'building_name': 'Crosswalk Commons',
  'score': score,
  'max_score': 10,
  'passing_threshold': 8,
  'passes': score >= 8,
  'criteria': criteria,
  'evidence': {
    'asset': probe,
    'identity_and_footprint_source': sources['sources'][0],
    'visual_source': sources['sources'][2],
    'assumptions': sources['model_assumptions'],
    'independent_inspection': 'Reopened the current saved .blend in Blender 4.5.15 and inspected the two saved rendered views against the retained official operator photographs.'
  },
  'findings': [
    'Revise the ground-floor long facade from repeated generic storefront windows to match the operator photograph: broad glazed common-area bays separated by brick piers, continuous dark fascia, and the larger stone entry wall/canopy.',
    'Locate the entrance on a georeferenced or clearly identifiable photograph/map view before treating its side and position as verified; current longest-edge placement is expressly approximate.',
    'Keep 9.5 m roof height labeled estimated unless dimensioned elevation or reliable height data is obtained.'
  ]
}

if __name__ == '__main__':
  result = evaluate()
  root = Path(__file__).resolve().parents[2]
  (root / 'audit/crosswalk_commons/independent_grade_result.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
  print(json.dumps(result, indent=2))
