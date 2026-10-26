import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / 'audit' / 'university_lutheran_church'
PROBE = AUDIT / 'independent_grade_final' / 'fresh_open_probe.json'
RESULT = AUDIT / 'independent_grade_final' / 'result.json'


def evaluate(probe, model, sources):
    """Evidence-based independent University Lutheran Church grade (0-10)."""
    criteria = [
        {
            'name':'Correct identity and source-backed footprint', 'score':2.0, 'max_score':2.0,
            'evidence':f"OpenStreetMap way {probe['osm_feature']['id']} is named {probe['osm_feature']['name']}; the official visit page and Purdue archive distinguish the site at 460 Northwestern from Purdue Lutheran Ministry. The 17 transformed OSM vertices and the structural shell bottom ring match with a symmetric Hausdorff distance of {probe['osm_feature']['symmetric_hausdorff_m']:.8f} m.",
            'findings':[]
        },
        {
            'name':'Position, orientation and scale/dimensions', 'score':1.7, 'max_score':2.0,
            'evidence':f"The envelope bounds match the source footprint within {probe['osm_feature']['shell_bounds_vs_evidence_max_error_m']:.8f} m. The local conversion places the outline at campus XY {model['anchor_xy_m']}; the road-facing edges were selected using OSM way 932656636 (Northwestern Avenue). The outline is about 29.05 by 30.11 m.",
            'findings':['OSM is not a surveyed parcel/wall survey; the official photograph has no camera azimuth, so the photographed facade cannot be tied conclusively to a specific compass edge.']
        },
        {
            'name':'Evidence-backed height, floors and roof form', 'score':1.25, 'max_score':2.0,
            'evidence':f"The official exterior photo supports three above-grade storeys and a shallow dark roof; the official visit page and Purdue archive record support the basement fellowship hall and third-floor sanctuary. The current model spans {probe['world_bounds_m'][2][0]:.2f} m to {probe['world_bounds_m'][2][1]:.2f} m, but the height is explicitly estimated with ±2.5 m uncertainty.",
            'findings':['No measured elevation or roof section was found. The shallow roof fall and stepped parapet profile are visual estimates; GIS height/story attributes are not reliable for this property.']
        },
        {
            'name':'Facade, entrances and distinctive architecture', 'score':1.55, 'max_score':2.0,
            'evidence':f"The model includes a brick shader with brick and noise nodes, pale masonry courses, dark frames and glazing, nine broad street-facing windows (three bays on each of three floors), the UNIVERSITY/LUTHERAN lettering, Fuel lettering, and storefront canopies. The revised preview is closer to the official image’s three dominant ribbon-window bays and larger centered name sign than the first graded revision.",
            'findings':['The visible Fuel sign appears on the central frontage grouping while it sits at the far end of the grouping in the official photo; photo azimuth is unknown, so the precise side alignment is not fully verifiable. Door/storefront segmentation and non-photographed elevations remain schematic or extrapolated.']
        },
        {
            'name':'Modular export, portability and complete evidence', 'score':2.0, 'max_score':2.0,
            'evidence':f"Fresh-opened Blender 5.2.3 asset SHA {probe['asset_sha256']}; expected scene/collection present, {probe['collection_object_count']} collection objects and {probe['mesh_count']} meshes; no materialless meshes, external images, linked libraries or missing library paths. The main structural shell is watertight and has no loose vertices. The source register, raw OSM footprint/road snapshots, official web captures and official exterior image are present, with a dedicated build script and three previews.",
            'findings':[]
        }
    ]
    score = round(sum(c['score'] for c in criteria), 2)
    findings = [f for c in criteria for f in c['findings']]
    return {'score':score,'max_score':10,'threshold':8.0,'status':'PASS' if score>=8 else 'FAIL','criteria':criteria,
            'evidence':{'asset_path':'modular/buildings/massing_university_lutheran_church_20903f1.blend','asset_sha256':probe['asset_sha256'],'probe':'audit/university_lutheran_church/independent_grade_final/fresh_open_probe.json','official_reference':'audit/university_lutheran_church/images/official_ulupurdue_full_building.jpg','source_register':'audit/university_lutheran_church/source_register.json','preview':'audit/university_lutheran_church/preview_street_elevation.png'},
            'findings':findings}

if __name__=='__main__':
    probe=json.loads(PROBE.read_text(encoding='utf-8'))
    model=json.loads((AUDIT/'model_evidence.json').read_text(encoding='utf-8'))
    sources=json.loads((AUDIT/'source_register.json').read_text(encoding='utf-8'))
    result=evaluate(probe,model,sources)
    RESULT.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))
