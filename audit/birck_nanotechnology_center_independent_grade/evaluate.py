import json
from pathlib import Path
BASE=Path(__file__).resolve().parent

def evaluate():
    p=json.loads((BASE/'probe_actual.json').read_text(encoding='utf-8'))
    b=json.loads((BASE/'probe_rebuilt.json').read_text(encoding='utf-8'))
    master=json.loads((BASE/'probe_master_placement.json').read_text(encoding='utf-8'))
    exp=json.loads((BASE/'export_actual_reopened.json').read_text(encoding='utf-8'))
    expr=json.loads((BASE/'export_rebuilt_reopened.json').read_text(encoding='utf-8'))
    review=json.loads((BASE/'source_review.json').read_text(encoding='utf-8'))
    f=p['footprint']; m=p['manifest']; attr=p['gis_feature']; names=set(p['object_names'])
    marker=[o for o in master['birck_objects'] if o['name']=='Placement_birck_nanotechnology_center']
    marker_ok=(len(marker)==1 and marker[0]['type']=='EMPTY' and marker[0]['instance_type']=='COLLECTION'
       and marker[0]['instance_collection']==m['collection'])
    if marker_ok:
        marker_err=max(abs(marker[0]['location_world'][i]-m['placement_origin_xy_m'][i]) for i in range(2))
        marker_ok=marker_err<0.01
    else: marker_err=None
    library_records=[c for c in master['birck_collections'] if c['name']==m['collection']]
    link_ok=len(library_records)==1 and library_records[0]['library'] in ('//modular\\buildings\\birck_nanotechnology_center.blend','//modular/buildings/birck_nanotechnology_center.blend') and library_records[0]['objects']==110
    gis_ok=(attr['fid']==604 and attr['abbr']=='BRK' and attr['name']=='Birck Nanotechnology Center'
       and attr['address']=='1205 Mitch Daniels Blvd' and f['model_shell_base_vertex_count']==201
       and f['symmetric_point_to_polyline_hausdorff_m']<0.025 and f['area_relative_error']<0.001)
    placement_ok=(marker_ok and link_ok and m['placement_origin_xy_m']==[-927.154,-525.43]
       and m['names_match_exactly'] and len(names)==110)
    export_ok=(exp['collection']==m['collection'] and exp['object_count']==110
       and set(exp['object_names'])==names and not exp['camera_or_light']
       and not exp['unpacked_external_images'] and not exp['linked_libraries']
       and expr['collection']==m['collection'] and expr['object_count']==110
       and set(expr['object_names'])==names and not expr['camera_or_light']
       and not expr['unpacked_external_images'] and not expr['linked_libraries']
       and not p['unpacked_external_images'] and not p['linked_libraries']
       and (not p['fonts'] or all(x['filepath']=='<builtin>' or x['packed'] for x in p['fonts'])))
    criteria=[
      {'name':'Correct identity and source-backed footprint','max_points':2,'points':2 if gis_ok else 0,
       'status':'verified' if gis_ok else 'failed',
       'evidence':f"Independent read of raw Purdue GIS FID {attr['fid']} identifies {attr['name']} ({attr['abbr']}) at {attr['address']}. After project-coordinate conversion and closure removal, the {f['model_shell_base_vertex_count']}-vertex evaluated shell perimeter is within {f['symmetric_point_to_polyline_hausdorff_m']:.4f} m symmetric point-to-boundary distance of the official polygon; relative plan-area difference is {f['area_relative_error']:.7%}.",
       'limitation':'Purdue campus GIS polygon is a public map feature, not a certified survey.'},
      {'name':'Position, orientation, and scale/dimensions','max_points':2,'points':2 if placement_ok and gis_ok else 0,
       'status':'verified' if placement_ok and gis_ok else 'failed',
       'evidence':f"Manifest origin {m['placement_origin_xy_m']} m; independently reopened master has one collection-instance marker at {marker[0]['location_world'][:2] if marker else None}, maximum marker/manifest difference {marker_err:.6f} m. Master collection link is relative and includes exactly 110 objects. GIS perimeter comparison confirms plan scale, footprint and orientation.",
       'limitation':'GIS is mapped in EPSG:4326 using the project local meters-per-degree approximation, not a surveyed local CRS. Facade photographs are perspective and were not used to estimate orientation or dimensions.'},
      {'name':'Evidence-backed height, floors, and roof form','max_points':2,'points':1,
       'status':'partially verified',
       'evidence':'Purdue News Service source describes a two-floor facility with a third level housing air-filtration equipment. Reopened model shows three facade bands and a distinct rooftop mechanical level.',
       'limitation':'The floor description dates to 2005 and precedes a 2024 renovation program. No verified elevation, floor-to-floor dimensions, roof section, or current equipment layout supports model bounds of 16.2 m; these remain estimates.'},
      {'name':'Facade, entrances, and distinctive architecture','max_points':2,'points':1.5,
       'status':'photo-supported broad cues; details remain schematic',
       'evidence':'Direct comparison of two Purdue-published photos with the fresh front render supports the broad central bronze/brown name volume, flanking glazed wings, curved/angled glazing, and an entrance next to the cladding. The raw page/image snapshots and fresh render are in the grade folder.',
       'limitation':'Unregistered perspective photos support motifs only. Exact panel width/joints, curtain-wall module rhythm, glazing extent, entry proportions/location, rooftop details, and facades outside the pictured view are not measured or fully verified.'},
      {'name':'Modular export, portability, and complete evidence','max_points':2,'points':1.5 if export_ok else 0,
       'status':'export verified; source metadata partly incomplete' if export_ok else 'failed',
       'evidence':f"Canonical builder rebuilt from the raw GIS/source snapshot in an isolated replica. Actual and rebuilt collection-only exports reopen in Blender {p['blender_version']}; each contains 110 objects with names identical to the manifest and source collection, no camera/light, external image or linked-library dependencies; the text font is Blender's built-in Bfont. The canonical asset's evidence and raw source files are preserved.",
       'limitation':'The building evidence records source providers, URLs, hashes and use but does not explicitly record retrieval dates for source snapshots; this loses 0.5 point under evidence completeness.'}
    ]
    score=round(sum(c['points'] for c in criteria),2)
    return {'score':score,'max_score':10,'passing_threshold':8,'pass':score>=8,'criteria':criteria,
      'evidence':{'actual_probe':str(BASE/'probe_actual.json'),'rebuilt_probe':str(BASE/'probe_rebuilt.json'),
       'master_placement_probe':str(BASE/'probe_master_placement.json'),'reopened_collection_export':str(BASE/'export_actual_reopened.json'),
       'source_review':str(BASE/'source_review.json'),'builder_rebuild_log':str(BASE/'canonical_builder_rebuild.log'),
       'views':[str(BASE/'views'/n) for n in ('birck_official_front_2026.jpeg','purdue_ece_birck_2023.jpg','birck_front_rebuilt.png','birck_plan_rebuilt.png')],
       'original_asset_sha256':p['asset_sha256'],'isolated_rebuild_sha256':b['asset_sha256']},
      'findings':[
       'FID 604 identity and GIS-derived plan geometry, orientation, and manifest placement were independently checked; actual master placement marker matches the refreshed manifest.',
       'Broad facade motifs agree with Purdue official photographs, but no perspective image was treated as a dimensioned or georeferenced elevation.',
       'Height, current floor datums, roof form and rooftop equipment layout remain estimated/unverified; the two-floor-plus-equipment story source is historic and renovation is documented in 2024.',
       'The builder and asset were not edited; a fresh rebuild was produced only inside the audit replica.'
      ]}

if __name__=='__main__':
    result=evaluate()
    (BASE/'result.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2,ensure_ascii=False))
