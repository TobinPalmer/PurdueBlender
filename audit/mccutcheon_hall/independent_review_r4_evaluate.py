"""Independent full-building evaluator for John T. McCutcheon Hall R4."""
import json
from pathlib import Path

AUDIT=Path(__file__).resolve().parent
ROOT=Path(__file__).resolve().parents[2]
criteria=[
 {'name':'Correct identity and source-backed footprint','score':1.90,'max_score':2.0,
  'evidence':'Purdue identification and GIS FID 57; transformed plinth AABB matches under 0.0001 m.',
  'findings':'GIS/local projection is approximate, not survey control; AABB agreement does not verify every wall segment.'},
 {'name':'Position, orientation, and scale/dimensions','score':1.60,'max_score':2.0,
  'evidence':'Expected local frame and identity asset-root transform persist in the reopened source asset.',
  'findings':'No master-marker placement check; no survey control or verified complete facade heading/dimensions.'},
 {'name':'Evidence-backed height, floors, and roof form','score':1.30,'max_score':2.0,
  'evidence':'R4 removes 16 unsupported penthouse components, lowers roof edge to 27.72 m, retains roof/parapet/HVAC, documents eight floors per tower, and analyzes 2017–2018 USGS 3DEP returns.',
  'findings':'LiDAR uses class-1 unclassified candidates because no class-6 building returns exist; metadata vertical accuracy is N/A. p95 is 25.93 m and maximum 26.16 m, still below the 27.72 m roof edge; HVAC reaches 28.50 m. Floor count does not resolve floor spacing or exact roof height.'},
 {'name':'Facade, entrances, and distinctive architecture','score':1.45,'max_score':2.0,
  'evidence':'Purdue official exterior photo supports broad brick, blue-gray glazing, perforated screen, glazed entry, light base, sign, and some rooftop equipment categories.',
  'findings':'Reference is cropped, oblique, undated, unscaled, and direction-unidentified; exact facade positioning, blank elevations, and opening schedule remain unverified.'},
 {'name':'Modular export, portability, and complete evidence','score':1.80,'max_score':2.0,
  'evidence':'Blender 5.2.3 reopened the expected asset; one direct root/219 children; identity root transform; 10 foliage images packed; relative foliage library resolves; no unresolved unpacked image dependencies; R4 renders and validation present.',
  'findings':'Master integration/placement and as-built interior/circulation are not reviewed or verified.'}
]

def evaluate(criteria):
    score=round(sum(c['score'] for c in criteria),2)
    maximum=sum(c['max_score'] for c in criteria)
    return {
      'building':'John T. McCutcheon Residence Hall',
      'building_id':'mccutcheon_hall',
      'revision_reviewed':4,
      'review_date':'2026-10-24',
      'review_type':'independent_full_building_read_only',
      'reviewer':'independent evaluator; did not build or edit R4',
      'asset':'modular/buildings/mccutcheon_hall.blend',
      'report':'audit/mccutcheon_hall/independent_review_r4.md',
      'score':score,'score_display':round(score,1),'max_score':maximum,
      'acceptance_threshold':8.0,'meets_threshold':score>=8.0,
      'criteria':criteria,
      'penthouse_removal_assessment':{
        'credit':'Removing 16 unsupported rooftop penthouse objects and lowering the tower roof edge from 30.35 m to 27.72 m is a reasonable correction supported by the 2017–2018 surface-return distribution and reduces a previously conspicuous unsupported mass.',
        'caveats':'No class-6 building returns were present; roof candidates are class 1 unclassified; the product vertical accuracy is N/A; candidate p95 is 25.93 m and maximum 26.16 m, still below the modeled 27.72 m roof edge; HVAC reaches 28.50 m. These are not surveyed roof/equipment heights.'},
      'technical_reopen':{'blender_version':'5.2.3 LTS','direct_asset_objects':1,'child_inclusive_objects':219,'asset_mesh_objects':210,'asset_root_location':[0.0,0.0,0.0],'asset_root_scale':[1.0,1.0,1.0],'overall_mesh_top_including_HVAC_m':28.5,'unresolved_unpacked_images':[],'master_edited':False},
      'limitations':['No master placement check.','No as-built interior/circulation plan.','Roof/LiDAR evidence is qualitative/approximate because of classification and accuracy limits.'],
      'read_only_review':True,'asset_edited':False,'master_edited':False,'shared_index_edited':False}

result=evaluate(criteria)
(AUDIT/'independent_review_r4_scorecard.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:result[k] for k in ['score','score_display','meets_threshold','penthouse_removal_assessment','criteria']},indent=2))
