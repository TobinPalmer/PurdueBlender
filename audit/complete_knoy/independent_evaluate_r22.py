"""Independent Knoy R22 rubric evaluator; grading only, no model edits."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
AUDIT=ROOT/'audit'/'complete_knoy'
REPORT='audit/complete_knoy/independent_review_round22.md'

def evaluate(criteria, acceptance_target=8.0):
    raw=sum(item['score'] for item in criteria)
    raw_max=sum(item['max_score'] for item in criteria)
    normalized=round(raw/raw_max*10,1)
    findings=[f for item in criteria for f in item['findings']]
    return {
      'building':'Maurice G. Knoy Hall of Technology',
      'building_id':'knoy_hall',
      'revision_reviewed':22,
      'review_date':'2026-10-24',
      'reviewer':'independent full-building reviewer; did not build or edit Knoy R22',
      'asset':'modular/buildings/knoy_hall.blend',
      'report':REPORT,
      'review_type':'independent_full_building_read_only',
      'score':normalized,'max_score':10.0,
      'raw_score':round(raw,2),'raw_max_score':raw_max,
      'normalization':'round((raw_score / raw_max_score) * 10, 1)',
      'previous_independent_score':7.8,
      'acceptance_target':acceptance_target,
      'passed':normalized>=acceptance_target,
      'criteria':criteria,
      'evidence':[
        'audit/complete_knoy/source_research_r22.md',
        'audit/complete_knoy/purdue_archives_item_1125_r22.json',
        'audit/complete_knoy/purdue_archives_item_1126_r22.json',
        'audit/complete_knoy/purdue_archives_knoy_exterior_1125_r22.jpg',
        'audit/complete_knoy/purdue_archives_knoy_exterior_winter_1126_r22.jpg',
        'audit/complete_knoy/source_knoy_r22_cerias_report.pdf',
        'audit/complete_knoy/source_knoy_r22_cerias_knoy_plan_crop.png',
        'audit/complete_knoy/validation_round21.json',
        'audit/complete_knoy/knoy_exterior_full_r17.png',
        'audit/complete_knoy/knoy_entrance_facade_r17.png'
      ],
      'findings':findings,
      'r22_source_decision':'New sources add qualitative facade support but do not resolve roof/L5 height, face-specific glazing, or interior circulation; R22 geometry is unchanged.',
      'read_only_review':True,
      'asset_edited':False,
      'master_edited':False,
      'shared_index_edited':False
    }

criteria=[
 {'name':'Identity and footprint','score':1.7,'max_score':2.0,'findings':[
  'Purdue GIS and stepped plan evidence support building identity and plan form.',
  'CERIAS plan-on-aerial figure is low-resolution and lacks tie points/residual; the approximate campus transform is not survey control.']},
 {'name':'Placement, orientation, and scale','score':1.6,'max_score':2.0,'findings':[
  'Prior manifest/GIS placement evidence remains applicable and the saved root is identity.',
  'R22 supplies no surveyed placement or master-marker audit.']},
 {'name':'Height, floors, and roof','score':1.2,'max_score':2.0,'findings':[
  'L1-L4 intervals match Purdue’s planning-study value within approximately 0.011 m per interval.',
  'R22 does not resolve L5, penthouse, roof profile, or the conflicting 48-ft GIS height attribute.']},
 {'name':'Exterior and entrances','score':1.4,'max_score':2.0,'findings':[
  'New Purdue Archives photos corroborate stepped brick forms, pale coping, lower glazing, and interrupted slit windows on pictured faces.',
  'The model’s repeated continuous glazing ribbons do not capture interruptions consistently; no new photo is georeferenced or face-identified.']},
 {'name':'Interior and circulation','score':1.7,'max_score':2.0,'findings':[
  'Existing plans/stairs/fixtures have broad support from the available planning material.',
  'The CERIAS overlay figure has no level label, reliable scale, coordinates, map heading, or control residual and cannot verify model walls or circulation.']},
 {'name':'Technical and evidence quality','score':1.0,'max_score':1.0,'findings':[
  'Blender 5.2.3 reopened the current asset with 191 objects and 169 meshes, identity root, and no file-backed image dependencies.',
  'Independent geometry/world-matrix hash matches the saved R21 hash exactly; R22 makes no geometry change.']}
]

result=evaluate(criteria)
(AUDIT/'independent_review_round22_scorecard.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:result[k] for k in ['score','raw_score','raw_max_score','passed','criteria']},indent=2))
