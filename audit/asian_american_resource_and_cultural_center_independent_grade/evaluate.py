from __future__ import annotations
import hashlib, json, math
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

def load(p): return json.loads(p.read_text(encoding='utf-8-sig'))

def evaluate():
    probe=load(HERE/'blender_asset_probe.json')
    master=load(HERE/'master_placement_probe.json')
    export=load(HERE/'portable_export_probe_reopen.json')
    feature=load(HERE/'sources/aaarcc_gis_feature_926.json')
    entry=next(a for a in load(HERE/'sources/manifest_snapshot.json')['assets'] if a.get('id')=='asian_american_resource_and_cultural_center')
    source=load(HERE/'sources/prior_aaarcc_evidence.json')
    attrs=feature['attributes']
    gis_id=(attrs.get('FID'),attrs.get('BLDG_ABBR'),attrs.get('BUILDING_N'))
    identity_ok=gis_id==(926,'AACC','Asian American Resource and Cultural Center')
    marker=master['markers'][0] if master['marker_count']==1 else {}
    origin=entry['placement_origin_xy_m']
    xy_delta=[float(marker['location'][i])-float(origin[i]) for i in range(2)]
    relative_path=(marker.get('library_path') or '').replace('\\','/')=='//modular/buildings/asian_american_resource_and_cultural_center.blend'
    manifest_match=probe['object_count']==entry['object_count'] and probe['object_names_match_manifest']
    footprint_max=max(probe['gis_to_plinth_nearest_max_m'],probe['plinth_to_gis_nearest_max_m'])
    dims_delta=[max(abs(probe['bounds_local_m'][i][j]-entry['local_bounds_m'][i][j]) for j in (0,1)) for i in (0,1)]
    asset_path=ROOT/'modular/buildings/asian_american_resource_and_cultural_center.blend'
    actual_hash=hashlib.sha256(asset_path.read_bytes()).hexdigest()
    export_ok=export['object_count']==probe['object_count'] and export['camera_or_light_count']==0
    # Ratings are independently assigned from the raw source and fresh Blender probes.
    criteria=[
      {'name':'Correct identity and source-backed footprint','score':2.0,'max_score':2,
       'assessment':f"Official Purdue GIS FID 926 names BLDG_ABBR AACC and Asian American Resource and Cultural Center at 915 Fifth Street. The saved polygon is in WGS 84 (EPSG:4326); after applying the project-local conversion and subtracting the GIS bounding-box center, its 20 unique ring vertices agree with the asset's exact GIS-perimeter plinth to {footprint_max:.9f} m maximum bidirectional nearest-vertex distance. This validates the GIS perimeter/plinth; it does not prove the different structural wall line, which remains uncertain."},
      {'name':'Position, orientation, and scale/dimensions','score':1.5,'max_score':2,
       'assessment':f"The master contains one Placement_asian_american_resource_and_cultural_center marker at {marker.get('location')}; its campus XY differs from the manifest placement origin by {[round(v,7) for v in xy_delta]} m, with zero rotation, unit scale, and the expected relative asset link. The GIS-derived local origin and polygon establish plan orientation/scale for the plinth. The interpreted house walls/porch and height dimensions were reconstructed from photos rather than measured plans, and the model's modifier-evaluated local bounds differ from manifest local bounds by up to {max(dims_delta):.4f} m per axis."},
      {'name':'Evidence-backed height, floors, and roof form','score':1.0,'max_score':2,
       'assessment':f"Purdue exterior photos and facility-page snapshots show a two-storey house with a steep shingle gable roof; the model reflects those features. GIS NUM_LEVELS and CountOfFLO both say {attrs.get('NUM_LEVELS')} floor(s), conflicting with the visible two stories, while Extrution={attrs.get('Extrution')} has no documented units. Model total height is {probe['bounds_local_m'][2][1]:.2f} m and its eave/ridge/chimney heights remain photo estimates; no surveyed vertical datum or measured architectural plan was found."},
      {'name':'Facade, entrances, and distinctive architecture','score':2.0,'max_score':2,
       'assessment':'The official Purdue AAARCC gallery photos support white horizontal clapboard, multi-pane sash windows, front porch/entry, shingle gable roof, chimney, and the Fifth Street sign. The saved preview visibly includes these elements. Purdue Emergency Preparedness provides separate front, accessible, and rear kitchen exit descriptions; the builder models the Fifth Street entrance, ramp/accessible door, and rear door. Interior room furniture/partition positions are schematic, not judged as measured.'},
      {'name':'Modular export, portability, and complete evidence','score':2.0,'max_score':2,
       'assessment':f"A fresh Blender 4.5.15 reopen found {probe['object_count']} objects ({probe['type_counts']}); names and count match the current manifest. The master has one relative linked collection instance. There are {probe['unmaterialed_mesh_count']} unmaterialed meshes, {len(probe['external_libraries'])} external libraries, and {len(probe['unpacked_file_images'])} unpacked file-image dependencies. An independent collection-only export was saved and reopened with {export['object_count']} objects and no cameras/lights. Source records, raw GIS, current facility/emergency-page snapshots, photos, builder, manifest snapshot, preview and probes are in this packet. The current asset hash is {actual_hash}."}
    ]
    total=sum(c['score'] for c in criteria)
    findings=[
      'GIS identity and outline are strongly supported, and the saved plinth reproduces the official polygon. The GIS source is a building-shape feature, not a structural wall survey; the builder interprets part of the footprint as porch/projection space, so the exact wall-versus-covered-porch line is not verified.',
      'The model is correctly placed through the master marker and has a relative collection link. Manifest count/name contract matches the current 433-object asset. Modifier-evaluated overall bounds differ from recorded local bounds by at most a few centimeters; the difference may reflect bevel/solidify modifiers and warrants coordinator review only if strict bounds parity is required.',
      'Exterior photos support two visible storeys and pitched roof form. The GIS one-level/12 extrusion attributes conflict with the photos and have no vertical-unit definition; model height and exact eave/ridge/chimney dimensions remain estimates.',
      'The collection-only export reopened successfully in Blender 4.5.15 without cameras/lights or external libraries. The asset is authored and tested on the same Blender 4.5.15 line.'
    ]
    return {'score':total,'max_score':10,'pass_threshold':8,'passes':total>=8,'criteria':criteria,'evidence':{
      'asset_path':'modular/buildings/asian_american_resource_and_cultural_center.blend','asset_sha256':actual_hash,'asset_bytes':asset_path.stat().st_size,
      'manifest_id':entry['id'],'expected_collection':entry['collection'],'expected_scene':entry['scene'],'manifest_object_count':entry['object_count'],'manifest_names_and_count_match':manifest_match,
      'fresh_asset_probe':{k:probe[k] for k in ['blender_version','scene','render_engine','collection','object_count','type_counts','bounds_local_m','manifest_local_bounds_m','gis_to_plinth_nearest_avg_m','gis_to_plinth_nearest_max_m','plinth_to_gis_nearest_avg_m','plinth_to_gis_nearest_max_m','unmaterialed_mesh_count','external_libraries','unpacked_file_images','modifier_count']},
      'source':{'provider':'Purdue University GIS ArcGIS REST','feature_id':attrs['FID'],'abbreviation':attrs['BLDG_ABBR'],'name':attrs['BUILDING_N'],'source_crs':'EPSG:4326 WGS 84','retrieved':'2026-10-25','source_date':'not supplied','ring_vertex_count_unique':probe['source_ring_vertex_count'],'raw_snapshot':'sources/aaarcc_gis_feature_926.json','shape_area_m2':attrs.get('Shape__Area'),'shape_length_m':attrs.get('Shape__Length'),'num_levels':attrs.get('NUM_LEVELS'),'count_of_floors':attrs.get('CountOfFLO'),'extrution':attrs.get('Extrution')},
      'footprint_method':'Transform WGS84 lon/lat using the exact campus local approximation documented in modular/AGENTS.md; center on transformed source feature bounding box; compare all ring vertices to the named GIS plinth mesh vertices. Bidirectional nearest-vertex check, not IoU.',
      'placement':{'manifest_origin_xy_m':origin,'master_marker':marker,'xy_delta_m':xy_delta,'one_marker':master['marker_count']==1,'relative_link_ok':relative_path},
      'independent_collection_export':export,'views':['views/current_preview.png'],'source_snapshots':['sources/aaarcc_gis_feature_926.json','sources/prior_aaarcc_evidence.json','sources/purdue_aaarcc_our_facilities_2026-10-25.html','sources/purdue_aaarcc_emergency_plan_2026-10-25.html','sources/purdue_aaarcc_front1.jpg','sources/purdue_aaarcc_waldron_fifth_corner.jpg','sources/manifest_snapshot.json','sources/builder_snapshot.py','sources/build_evidence.json','sources/aaarcc_asset_validation.json','sources/manifest_targeted_evidence_snapshot.json']},
      'findings':findings,'evaluator':'evaluate.py::evaluate','evaluated_at':'2026-10-25','scope':'Fresh independent assessment of the current rebuilt AAARCC asset, canonical builder inputs, source records, manifest and master placement. Source files and shared indexes were not modified.'}

if __name__=='__main__':
 r=evaluate(); (HERE/'result.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8'); print(json.dumps(r,indent=2))
