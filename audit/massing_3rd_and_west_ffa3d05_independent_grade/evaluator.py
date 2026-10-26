"""Independent rubric grader for the 3rd and West Blender building asset."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2]
GRADE=Path(__file__).resolve().parent
PROBE=json.loads((GRADE/'independent_probe.json').read_text(encoding='utf-8'))
EVID=json.loads((ROOT/'audit'/'massing_3rd_and_west_ffa3d05'/'build_evidence.json').read_text(encoding='utf-8'))


def evaluate():
    p=PROBE; sources=EVID['sources']
    # Score source support separately from claims of model/source agreement.
    criteria=[
      {'name':'Correct identity and source-backed footprint','points':1.8,'max_points':2,
       'status':'verified_with_limitations',
       'evidence':['OSM way 1324500897 is explicitly tagged building=dormitory and name=3rd and West; the official Purdue housing article and project source identify the Third Street/McCormick Road 3rd and West community.','The 14-node outline is faithfully implemented; independent probe found a maximum node-to-structural-shell error of %.8f m.' % p['max_source_node_to_shell_vertex_error_m'], 'No independent surveyed or official footprint was found, so this does not validate the OSM polygon itself.'],
       'deduction':'Footprint identity is plausible and source-backed but relies on OSM as the sole geometric outline.'},
      {'name':'Position, orientation, and scale/dimensions','points':1.6,'max_points':2,
       'status':'verified_with_limitations',
       'evidence':['The OSM ring was independently transformed using the project’s stated compatibility formula; model vertex comparison and bounds agree.','The footprint area is %.1f m² with extents approximately 108.6 by 91.5 m. Official project material reports 325,000 sq ft gross floor area; five times the footprint is approximately %.0f sq ft, about 8%% lower, a plausible but not conclusive scale cross-check.' % (p['source_ring_area_m2'],p['source_gross_floor_area_check']['projected_area_at_five_stories_sqft']), 'Official sources confirm the building is at Third Street and McCormick Road.'],
       'deduction':'No independent current map/survey registration or orientation measurement; the OSM coordinates are both the placement input and the comparison source.'},
      {'name':'Evidence-backed height, floors, and roof form','points':1.4,'max_points':2,
       'status':'partially_verified',
       'evidence':['Purdue University Residences and Purdue Research Foundation project pages state five stories; the saved Purdue photo visibly supports a flat parapeted roof silhouette.','The modeled 18.0 m eave, 0.9 m parapet and 18.9 m total height are clearly labeled estimates, not measurements.'],
       'deduction':'No published elevation or height measurement; exact roof equipment/profile and story heights remain unverified.'},
      {'name':'Facade, entrances, and distinctive architecture','points':1.3,'max_points':2,
       'status':'partially_verified',
       'evidence':['The official Purdue Research Foundation photo shows light facade fields, dark repeated windows, brick end masses and a courtyard-facing residential elevation.','SCB’s project description supports two courtyards, a transparent amenity ground floor, and patterned brick/glazing; the model represents broad courtyard wings, repeated windows and brick accents.'],
       'deduction':'The model is a coarse proxy: bay spacing, glazing proportions, entrance/plaza placement and distinctive corner study volumes are not measured and are only partly expressed.'},
      {'name':'Modular export, portability, and complete evidence','points':2.0,'max_points':2,
       'status':'verified',
       'evidence':['Fresh Blender reopen found the expected scene and collection with 19 mesh objects.','A fresh empty Blender file linked the named collection and loaded all 19 meshes.','No external images, fonts or linked libraries are required; the builder, source snapshots, preview, validation records and uncertainties are saved.']}
    ]
    score=round(sum(c['points'] for c in criteria),2)
    findings=[
      'PASS: this is a source-informed upgrade from an undifferentiated block; official sources confirm identity, five stories and two-courtyard design.',
      'Limit: the OSM outline was used as the build geometry, so node-level agreement is an implementation check, not independent footprint validation.',
      'Limit: vertical dimensions, roof equipment, facade bay sizes and exact entrance placement remain estimates or unverified.'
    ]
    return {'score':score,'max_score':10,'status':'PASS' if score>=8 else 'FAIL','criteria':criteria,
            'evidence':{'independent_probe':'independent_probe.json','builder_evidence':'../massing_3rd_and_west_ffa3d05/build_evidence.json','builder_record':'../massing_3rd_and_west_ffa3d05/evidence.md','model_preview':'../massing_3rd_and_west_ffa3d05/3rd_and_west_preview.png','official_photo':'../massing_3rd_and_west_ffa3d05/sources/purdue_3rd_west_exterior.png','primary_sources':[s['url'] for s in sources]},
            'findings':findings}

if __name__=='__main__':
    result=evaluate()
    (GRADE/'result.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2,ensure_ascii=False))
