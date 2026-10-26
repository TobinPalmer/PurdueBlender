import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
AUD=ROOT/'audit'/'chapel_good_shepherd_5d4d103'
OUT=AUD/'independent_grade_r2'

def evaluate():
    inspection=json.loads((OUT/'reopen_inspection.json').read_text(encoding='utf-8'))
    source=json.loads((AUD/'source_record.json').read_text(encoding='utf-8'))
    model=inspection['model']
    assert inspection['reopened_from_saved_blend'] is True
    assert model['collection']=='Asset_massing_chapel_of_the_good_shepherd_5d4d103'
    assert model['scene']=='Building_massing_chapel_of_the_good_shepherd_5d4d103'
    assert model['object_name']=='Chapel of the Good Shepherd'
    assert model['object_type']=='MESH' and len(model['modifiers'])==0
    assert model['unpacked_images']==[]
    assert abs(model['zero_z_xy_bounds_m'][0][0]-6.598265)<0.02
    assert abs(model['zero_z_xy_bounds_m'][1][0]-770.129028)<0.02
    assert len(source['sources'])>=6
    assert any(s.get('image_snapshot')=='sources/goodshep_about_image_5.jpg' and s.get('image_url') and s.get('raw_snapshot') for s in source['sources'])
    assert any(s.get('feature_id')=='way/869993661' and s.get('crs')=='WGS 84 (EPSG:4326)' for s in source['sources'])
    criteria=[
      {'name':'Correct identity and source-backed footprint','score':2.0,'max_score':2,'evidence':'OSM way/869993661 is named and addressed as the chapel; Nominatim resolves the same address to that feature. Direct reopen measured the zero-Z shell envelope at X 6.598..40.582 m and Y 770.129..787.807 m, matching the converted source polygon bounds; the notched campus-coordinate perimeter is retained.'},
      {'name':'Position, orientation, and scale/dimensions','score':1.75,'max_score':2,'evidence':'Object world matrix is identity and structural footprint lies in campus meters. The main gabled facade and centered entrance face south toward Meridian Street, while the secondary accessible entrance remains on the north side. The south-elevation and southeast renders confirm the left/west low wing and long right/east wing arrangement. XY geometry follows the mapped outline. Geographic and source-survey precision are limited by OSM mapping uncertainty.'},
      {'name':'Evidence-backed height, floors, and roof form','score':1.25,'max_score':2,'evidence':'The official photograph and elevation support a tall central gable with bell stage/spire and lower attached wings. The reopened renders show closed, continuous roof silhouettes without the prior dark triangular openings. Overall Z reaches 18.65 m, but no source gives measured heights or roof pitch; these remain estimates. Roof planes intersect at wing junctions and show seams in top view.'},
      {'name':'Facade, entrances, and distinctive architecture','score':1.25,'max_score':2,'evidence':'The saved model shows brick color, pale trim, centered red entrance on the south gable, flanking windows, gable vent, louvered bell stage, white steeple, and repeated windows on the long east wing, matching broad official photo/elevation cues. The official front elevation shows paired upper and lower window groups around the central entry; the model simplifies this to one flanking window on each side. Detailed dimensions and spacing are not documented.'},
      {'name':'Modular export, portability, and complete evidence','score':2.0,'max_score':2,'evidence':'Blender 4.5.15 reopened the saved asset directly. It contains the expected scene and collection with one mesh, identity transform, no modifiers, and no unpacked external images. Source record indexes the official elevation image and URL, raw OSM/Nominatim/site snapshots, provider, CRS, retrieval/source date limits, methods, and uncertainty; a preview and independent reopen views are retained.'}
    ]
    score=round(sum(c['score'] for c in criteria),2)
    result={'score':score,'max_score':10,'status':'pass' if score>=8 else 'fail','reviewer':'independent_grade_r2','criteria':criteria,'evidence':{'asset_file':'modular/buildings/massing_chapel_of_the_good_shepherd_5d4d103.blend','reopen_record':'audit/chapel_good_shepherd_5d4d103/independent_grade_r2/reopen_inspection.json','rendered_views':['audit/chapel_good_shepherd_5d4d103/independent_grade_r2/south_elevation.png','audit/chapel_good_shepherd_5d4d103/independent_grade_r2/southeast.png','audit/chapel_good_shepherd_5d4d103/independent_grade_r2/top.png'],'source_record':'audit/chapel_good_shepherd_5d4d103/source_record.json','directly_reviewed_sources':['audit/chapel_good_shepherd_5d4d103/sources/osm_way_869993661_2026-10-26.json','audit/chapel_good_shepherd_5d4d103/sources/osm_context_2026-10-26.osm','audit/chapel_good_shepherd_5d4d103/sources/goodshep_about_image_4.jpg','audit/chapel_good_shepherd_5d4d103/sources/goodshep_about_image_5.jpg'],'reopen_model_facts':{k:model[k] for k in ['scene','collection','object_name','vertices','polygons','modifiers','world_bounds_m','zero_z_xy_bounds_m','matrix_world','unpacked_images','boundary_edges','edges_with_more_than_two_faces']}},'findings':['Passes the 8/10 minimum. Remaining accuracy limitations: height and roof pitch are photo-based estimates; the central front elevation omits the upper pair of flanking windows shown in the official sketch; roof joins retain intersecting seams, though no open gaps are apparent in the reviewed views.']}
    (OUT/'result.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    return result

if __name__=='__main__':
    r=evaluate()
    print(json.dumps(r,indent=2))
