import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

def evaluate():
    reopened=json.loads((HERE/'direct_reopen_inspection.json').read_text(encoding='utf-8'))
    source=json.loads((ROOT/'audit/massing_harrison_street_parking_garage_823c7d2/source_record.json').read_text(encoding='utf-8'))
    validation=json.loads((ROOT/'audit/massing_harrison_street_parking_garage_823c7d2/validation.json').read_text(encoding='utf-8'))
    result={
        'score':7.4,
        'max_score':10,
        'criteria':[
            {'criterion':'Correct identity and source-backed footprint','score':2.0,'max_score':2,'evidence':'Purdue GIS FID 892 identifies BLDG_ABBR PGH, Harrison Street Parking Garage, address 719 Clinic Drive. The builder transforms that official polygon ring directly and uses it for the garage decks. The archived Indiana aerial shows the same elongated, indented roof outline in the same campus context.'},
            {'criterion':'Position, orientation, and scale/dimensions','score':1.7,'max_score':2,'evidence':'Reopened structural deck bounds are X -361.5203 to -303.2453 m and Y -747.1450 to -662.7343 m, matching the transformed GIS bounds to rounding. Transform is stated and consistent with modular/AGENTS.md, and geometry remains direct campus coordinates. Overall collection bounds expand to X -361.7581 to -302.9874 m and Y -749.9656 to -662.5153 m because attached features (notably the inferred core/planters) exceed the GIS footprint. The final footprint is not independently quantified as a polygon overlay/IoU.'},
            {'criterion':'Evidence-backed height, floors, and roof form','score':1.0,'max_score':2,'evidence':'WGI’s archived project page states six levels, one below grade, supporting the floor count. The model uses 3.2 m level intervals and 17.1 m top-of-screen, explicitly as estimates. Purdue GIS vertical fields are documented as semantically/unit ambiguous. The archived aerial visibly shows parking stalls and a central roof structure/open area, while the model’s top is a blank full-footprint concrete slab with a small brick block; this roof treatment is not supported by that image.'},
            {'criterion':'Facade, entrances, and distinctive architecture','score':1.1,'max_score':2,'evidence':'WGI and contractor source notes support cast-in-place construction, brick veneer, architectural precast, and planter beds. The build models open bays, concrete piers, spandrels, one brick stair/service core, glazing, screen, and planter curbs. No dimensioned elevations or entrance/ramp location were located; bay spacing, core placement, screen, facade rhythm, planter locations, and entry/circulation are interpretations. Renders show little functional garage circulation or entrance articulation.'},
            {'criterion':'Modular export, portability, and complete evidence','score':1.6,'max_score':2,'evidence':'Direct Blender 4.5.15 reopen confirms the expected scene and collection, 542 mesh objects, no linked libraries or image dependencies, and direct campus-coordinate geometry. Evidence includes raw Purdue GIS/metadata, WGI page, Purdue campus map, Indiana imagery/metadata, source record, builder, validation JSON/log, and three renders. The file warns it was written by Blender 5.2; Blender 4.5 opened it for inspection but reports its saved BLENDER_EEVEE render engine unavailable, so render settings are not portable across these versions.'}
        ],
        'evidence':{
            'asset':reopened['asset'],
            'scene':reopened['scene_names'],
            'collection':reopened['expected_collection'],
            'direct_reopen_object_count':reopened['object_count'],
            'direct_reopen_bounds_xyz_m':reopened['bounds_xyz'],
            'validation_file_bounds_xyz_m':validation['world_bounds_xyz_m'],
            'source_record_retrieval_date':source['retrieved_utc'],
            'sources':[{'provider':s['provider'],'feature':s['feature'],'url':s['url']} for s in source['sources']],
            'reviewed_renders':['renders/harrison_oblique_review.png','renders/harrison_elevation_review.png','renders/harrison_roof_review.png'],
            'reviewed_aerial':'sources/current_aerial_harrison_crop.jpg',
            'reopen_tool':'Blender 4.5.15 LTS, read-only open; file header reports writer 5.2.0'
        },
        'findings':[
            'Below the repository 8/10 pass threshold (7.4/10). The roof is the largest evidence-backed discrepancy: the current aerial shows active rooftop parking and a central roof feature/open area; the model shows a featureless continuous slab and small isolated brick block.',
            'The garage footprint and campus position are strong at the deck level, but added features extend the overall object bounds by roughly 2.82 m south of the GIS polygon. Clarify which overhang/core pieces are supported or bring them inside if the visible feature is only an inferred volume.',
            'Show or document the entrance, ramp/vertical circulation, and roof access from sources. If exact design information is unavailable, make those elements clearly estimated and avoid presenting a blank roof as verified.',
            'Floor count is sourced; 3.2 m floor spacing and 17.1 m screen height remain estimated. GIS NUM_LEVELS=7 and CountOfFLO=6 conflict, and its vertical units are undocumented.',
            'Reopening in Blender 4.5.15 worked for geometry inspection, but emitted a newer-file warning and could not use the saved BLENDER_EEVEE engine. Verify editable compatibility in the project’s Blender 5.2 version or update the render engine after any rebuild.'
        ],
        'independent_review':True,
        'read_only_asset_source_index':True
    }
    assert result['max_score']==10
    assert abs(sum(c['score'] for c in result['criteria'])-result['score'])<1e-9
    return result

if __name__=='__main__':
    result=evaluate()
    (HERE/'grade_result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))
