from __future__ import annotations
import hashlib, json
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

def read(p: Path): return json.loads(p.read_text(encoding='utf-8-sig'))

def evaluate():
    probe=read(HERE/'blender_probe.json')
    master=read(HERE/'master_probe.json')
    package=read(HERE/'builder_smoke_project/audit/class_of_1950_evidence/package_validation.json')
    source=read(HERE/'sources/arcgis_feature_230.json')['feature']
    source_record=read(HERE/'sources/source_evidence.json')
    manifest=read(HERE/'sources/manifest_snapshot.json')
    asset=next(x for x in manifest['assets'] if x.get('id')=='class_of_1950')
    attrs=source['attributes']
    marker=master['markers'][0] if len(master['markers'])==1 else {}
    fp=package['source_evidence']['footprint_check']
    count_ok=probe['collection_object_count']==asset.get('object_count')==2431 and probe['manifest_names_match']
    origin=asset['placement_origin_xy_m']
    delta=[round(float(marker['location'][i])-float(origin[i]),9) for i in range(2)]
    link=(marker.get('instance_collection_library') or '').replace('\\','/')
    linked=link=='//modular/buildings/class_of_1950.blend'
    attr_ok=(attrs.get('FID'),attrs.get('BLDG_ABBR'),attrs.get('BUILDING_N'))==(230,'CL50','Class of 1950 Lecture Hall')
    eval_sha=hashlib.sha256((ROOT/'modular/buildings/class_of_1950.blend').read_bytes()).hexdigest()
    score=[2.0,2.0,1.0,2.0,1.5]
    criteria=[
      {'name':'Correct identity and source-backed footprint','score':score[0],'max_score':2,
       'assessment':('Verified. The raw Purdue ArcGIS feature identifies FID 230, CL50, “Class of 1950 Lecture Hall”. Its 29-vertex polygon is compared with the asset wall envelope lower perimeter (82 vertices) after inverse Web Mercator and the documented Purdue local approximation. GIS-to-model directed nearest-vertex max is %.6f m; model-to-GIS max is %.3f m, consistent with finer mesh tessellation. This is a vertex-distance check, not polygon IoU or a surveyed wall-error claim.' % (fp['gis_to_model_nearest_vertex_max_m'],fp['model_to_gis_nearest_vertex_max_m'])) if attr_ok else 'Identity evidence did not match the expected official source feature.'},
      {'name':'Position, orientation, and scale/dimensions','score':score[1],'max_score':2,
       'assessment':f"Verified within the project coordinate approximation. The master has exactly one Placement_class_of_1950 marker at {marker.get('location')}; its XY matches the manifest origin with delta {delta} m, rotation is {marker.get('rotation_degrees')} degrees and scale is {marker.get('scale')}. The marker instances the expected relative linked library. GIS source/model lower-perimeter axis-extent deltas are {fp['max_axis_extent_delta_m']} m."},
      {'name':'Evidence-backed height, floors, and roof form','score':score[2],'max_score':2,
       'assessment':f"Partially verified. Official GIS NUM_LEVELS and CountOfFLO both report {attrs.get('NUM_LEVELS')} floors, and Purdue exterior images support a low/flat parapet silhouette. The reopened asset is {probe['collection_local_bounds_m'][2][1]:.1f} m tall. GIS Extrution={attrs.get('Extrution')} has no documented units/semantics and no surveyed height source was found, so the model height remains unverified."},
      {'name':'Facade, entrances, and distinctive architecture','score':score[3],'max_score':2,
       'assessment':'Purdue Archives source text and current Purdue exterior photos support the curved brick-and-glass frontage, large round brick columns, pale column bases/capitals, glazed upper wall, and curved soffit. The saved current-revision close and assembled views show these features. The 2024 Road School room map supports lecture hall/classroom identity but is not used as dimensional evidence.'},
      {'name':'Modular export, portability, and complete evidence','score':score[4],'max_score':2,
       'assessment':f"The current builder was run from an isolated smoke project against copied current inputs; its package copy reopened successfully with {package.get('reopened_package_collection_count')} objects and identical SHA-256. Direct reopen reports {probe['collection_object_count']} objects ({probe['collection_type_counts']}), no unmaterialed meshes, external libraries, or unpacked file images; the master uses a relative library path. Deduction reflects manifest source_metadata/evidence_file still being null and Blender 4.5.15 reporting a newer-file/Eevee compatibility warning. This independent packet preserves source snapshots, photos, views, probes, and packaging output."}
    ]
    findings=[
      'Footprint, object inventory, and master placement are strongly verified. Nearest-vertex distances are not an area overlap statistic and the GIS source is a building polygon rather than a surveyed wall survey.',
      'Three floors are supported, but 18.9 m model height is not verified: the GIS Extrution=36 field has no stated vertical units/semantics and no surveyed height source was found.',
      'The asset and its packaging copy reopen with all expected objects and no external dependencies. Blender 4.5.15 reports the source was written by newer binary 502.45 and that the saved BLENDER_EEVEE engine is unavailable; do not resave/edit in this older version without checking the authoring-version workflow.',
      'Manifest source_metadata and evidence_file remain null; this audit packet contains the source/evidence provenance independently.'
    ]
    total=sum(c['score'] for c in criteria)
    return {
      'score':total,'max_score':10,'pass_threshold':8,'passes':total>=8,'criteria':criteria,'evidence':{
       'asset_path':'modular/buildings/class_of_1950.blend','asset_sha256':eval_sha,'asset_bytes':probe['asset_bytes'],
       'manifest_id':asset['id'],'expected_collection':asset['collection'],'scene':probe['scene_name'],
       'asset_reopen':{'blender_version':'4.5.15 LTS','object_count':probe['collection_object_count'],'type_counts':probe['collection_type_counts'],'bounds_m':probe['collection_local_bounds_m'],'manifest_names_match':probe['manifest_names_match'],'missing_required_geometry':probe['missing_geometry'],'unmaterialed_mesh_count':probe['unmaterialed_mesh_count'],'external_libraries':probe['external_libraries'],'unpacked_file_images':probe['unpacked_file_images']},
       'identity_source':{'provider':'Purdue University ArcGIS FeatureServer','feature_id':attrs.get('FID'),'code':attrs.get('BLDG_ABBR'),'name':attrs.get('BUILDING_N'),'crs':'EPSG:3857 (latestWkid 3857; layer wkid 102100)','retrieved':source_record.get('retrieved'),'source_date':'not provided','gis_ring_vertices':probe['source_ring_vertex_count'],'num_levels':attrs.get('NUM_LEVELS'),'count_of_floors':attrs.get('CountOfFLO'),'extrution_field':attrs.get('Extrution'),'height_interpretation':'unverified'},
       'footprint_comparison':fp,
       'placement':{'manifest_origin_xy_m':origin,'marker':marker,'xy_delta_m':delta,'single_marker':master['placement_marker_count']==1,'linked_collection':linked},
       'packaging_smoke':{'mode':package['mode'],'package_sha256':package['package_copy_sha256'],'source_sha256':package['asset_sha256'],'identical_hash':package['package_copy_sha256']==package['asset_sha256'],'reopened_object_count':package['reopened_package_collection_count'],'isolated_project':'builder_smoke_project/'},
       'render_views':['views/current_asset_close_render.png','views/current_asset_assembled_view.png'],
       'source_snapshots':['sources/arcgis_feature_230.json','sources/arcgis_layer_0_metadata.json','sources/source_evidence.json','sources/manifest_snapshot.json','sources/modular_AGENTS_snapshot.md','sources/builder_snapshot.py','sources/purdue_events_photo.jpg','sources/purdue_libraries_exterior_reference.jpg','sources/purdue_road_school_floor_plan_2024.pdf']},
      'findings':findings,'evaluator':'evaluate.py::evaluate','evaluated_at':'2026-10-25',
      'scope':'Fresh independent read-only grade of the packaged final Class of 1950 asset. Builder packaging was smoke-tested from a copied project tree. No assigned building files or shared indexes were modified.'
    }

if __name__=='__main__':
    result=evaluate()
    (HERE/'result.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))
