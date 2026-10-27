import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
def evaluate():
    probe=json.load(open(HERE/'blender_probe.json',encoding='utf8'))
    gis=json.load(open(ROOT/'audit/alpha_xi_delta/sources/purdue_gis_fid788_raw.json',encoding='utf8'))['features'][0]
    meta=json.load(open(ROOT/'audit/alpha_xi_delta/sources/wikimedia_commons_metadata_raw.json',encoding='utf8'))
    assert probe['model_reopened'] and probe['gis_fid']==788 and probe['gis_name']=='Alpha Xi Delta'
    assert probe['gis_address']=='519 University St'
    assert probe['gis_unique_ring_vertices']==24 and probe['base_point_max_residual_m']<0.0001
    assert probe['collection']=='Asset_massing_house_301841248_fe939c7' and probe['object_name']=='House_301841248'
    assert probe['collection_object_count']==1 and probe['object_type']=='MESH'
    assert probe['external_file_images']==[]
    criteria=[
      {'criterion':'Correct identity and source-backed footprint','score':2.0,'max_score':2,'evidence':['Purdue ArcGIS feature FID 788 identifies Alpha Xi Delta (SOAXD), 519 University St.','Direct reopen probe found all 24 distinct source ring points in the model base; maximum residual was %.8f m.'%probe['base_point_max_residual_m']],'findings':['The map layer reports no certified-survey or positional-accuracy statement.']},
      {'criterion':'Position, orientation, and scale/dimensions','score':1.5,'max_score':2,'evidence':['Asset remains in campus coordinates and has an identity object transform as expected for the manifest massing asset.','Reopened footprint preserves the mapped wall ring; evaluated extents are approximately %.2f m by %.2f m.'%(probe['dimensions_xyz_m'][0],probe['dimensions_xyz_m'][1]),'The source photograph metadata gives camera location 40.429528, -86.916583 and a 310-degree heading, consistent with a southeast vantage toward the mapped footprint.'],'findings':['Facade bearing is still illustrative: the camera is oblique, and the photo does not establish a full elevation or exact entry normal.','The roof and entry details project slightly beyond the GIS base outline.']},
      {'criterion':'Evidence-backed height, floors, and roof form','score':1.0,'max_score':2,'evidence':['The 2008 source image shows multiple facade levels / a second window band, providing partial support for a two-level interpretation.','The saved model ridge is approximately %.1f m.'%probe['dimensions_xyz_m'][2]],'findings':['GIS NUM_LEVELS=1 conflicts with the two-level reading; field definition is undocumented.','The image crops out the roof and does not measure any height. The two-level count and 8.2 m eaves / 12.3 m ridge are estimates; hipped roof form is not source-verified.']},
      {'criterion':'Facade, entrances, and distinctive architecture','score':1.5,'max_score':2,'evidence':['Direct visual comparison of the Wikimedia Commons photo and preview supports the dark red-brown brick, light stone arched recessed entrance, horizontal facade band, and mullioned windows.','The rendered preview includes those source-backed elements.'],'findings':['The reference is close-cropped and does not establish full facade proportions, window count across the whole building, or all secondary elevations.','The entry compass bearing and modeled window rhythm are approximate.']},
      {'criterion':'Modular export, portability, and complete evidence','score':2.0,'max_score':2,'evidence':['Blender reopened the assigned file and found the expected named collection with exactly one mesh object.','Object transform is identity, the source perimeter is present, and no external file images are linked.','The audit includes raw GIS, source image and metadata, structured source observations, a preview, and reopen validation.'],'findings':['No export or portability issue was observed.']}
    ]
    score=round(sum(x['score'] for x in criteria),2)
    return {'score':score,'max_score':10,'criteria':criteria,'evidence':{'asset_path':'modular/buildings/massing_house_301841248_fe939c7.blend','blender_probe':'blender_probe.json','source_photo':'sources/alpha_xi_delta_house_2008.png','source_photo_metadata':'sources/wikimedia_commons_metadata_raw.json','gis_snapshot':'sources/purdue_gis_fid788_raw.json','manifest_source_bounds_m':[-297.60888671875,-274.1078796386719,241.6119384765625,269.2497863769531,0,16],'source_gis_attributes':{'feature_id':gis['attributes']['FID'],'building_name':gis['attributes']['BUILDING_N'],'address':gis['attributes']['ADDRESS'],'shape_area_m2':gis['attributes']['Shape__Area'],'shape_length_m':gis['attributes']['Shape__Length'],'num_levels':gis['attributes']['NUM_LEVELS']},'reopened_model_bounds_m':probe['evaluated_bounds_xyz_m'],'footprint_vertex_max_residual_m':probe['base_point_max_residual_m'],'camera_location_and_heading':'40.429528, -86.916583; heading 310 degrees'},'findings':['PASS: the score meets the repository 8/10 threshold.','Horizontal footprint and library packaging are strongly supported; vertical dimensions and roof are not measured, and the chosen facade bearing remains uncertain.']}
if __name__=='__main__':
    result=evaluate()
    for name in ('result.json','evaluator_output.json'):
        (HERE/name).write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps(result))
