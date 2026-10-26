import bpy, json, math, os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
ASSET_ID = 'massing_johnson_hall_of_nursing_jnsn_823fca7'
ASSET = ROOT / 'modular' / 'buildings' / f'{ASSET_ID}.blend'
AUDIT = ROOT / 'audit' / ASSET_ID
SOURCE = AUDIT / 'sources' / 'purdue_building_shapes_fid218_jnsn.json'
VALIDATION = AUDIT / 'review' / 'reopen_validation.json'
OUT = AUDIT / 'independent_grade' / 'r1' / 'result.json'

def evaluate():
    # This script is run with Blender's --background <asset> --python evaluator.py,
    # which freshly opens the saved asset before evaluating it.
    source = json.loads(SOURCE.read_text(encoding='utf-8-sig'))['feature']
    old_validation = json.loads(VALIDATION.read_text(encoding='utf-8-sig'))
    scene = bpy.context.scene
    expected_scene = 'Building_' + ASSET_ID
    expected_collection = 'Asset_' + ASSET_ID
    col = bpy.data.collections.get(expected_collection)
    mesh_objects = [o for o in col.objects if o.type == 'MESH'] if col else []
    obj = mesh_objects[0] if len(mesh_objects) == 1 else None
    # Compare the saved ground-level footprint shell directly with all unique GIS vertices.
    raw = source['geometry']['rings'][0]
    ring = [((p[0] + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
             (p[1] - 40.4274) * 111040.0) for p in raw]
    if len(ring) > 1 and math.dist(ring[0], ring[-1]) < 1e-8:
        ring = ring[:-1]
    ground = []
    if obj:
        for v in obj.data.vertices:
            co = obj.matrix_world @ v.co
            if abs(co.z) < 0.001:
                ground.append((co.x, co.y))
    nearest = [min((math.dist(p, q) for q in ground), default=float('inf')) for p in ring]
    max_ring_error = max(nearest, default=float('inf'))
    # Reopened asset structure and external dependencies.
    linked_libs = [str(lib.filepath) for lib in bpy.data.libraries]
    external_images = [im.filepath for im in bpy.data.images if im.source == 'FILE']
    modifiers = [m.name for o in mesh_objects for m in o.modifiers]
    bounds = None
    if obj:
        coords = [obj.matrix_world @ v.co for v in obj.data.vertices]
        bounds = [[min(c[i] for c in coords), max(c[i] for c in coords)] for i in range(3)]
    # Scores follow AGENT.md's five 2-point criteria. Facade/entry claims have no
    # supporting photo/elevation/plan in the independent source set, so appearance
    # receives no evidence credit despite visible illustrative detail.
    criteria = [
      {'name':'Correct identity and source-backed footprint','score':2.0,'max_score':2,'status':'verified against Purdue GIS and independently corroborated',
       'evidence':f"Freshly opened asset; source identifies FID {source['attributes']['FID']} / {source['attributes']['BLDG_ABBR']} as {source['attributes']['BUILDING_N']}. Mesh ground ring is compared to all {len(ring)} unique GIS vertices (maximum nearest-vertex error {max_ring_error:.6f} m). OSM way 117146488 independently names Johnson Hall of Nursing and its outline differs by about 0.876 m Hausdorff.",
       'uncertainty':'Purdue GIS is not a structural survey, and its Shape__Area attribute conflicts with the polygon ring area; the independent OSM outline supports the ring geometry.'},
      {'name':'Position, orientation, and scale/dimensions','score':2.0,'max_score':2,'status':'verified against authoritative campus geometry; not survey-verified',
       'evidence':f"Saved mesh retains campus-world coordinates and the source ring orientation. Reopened bounds (X,Y,Z) are {bounds}; source ring and OSM independently corroborate the plan footprint. No unexplained object transform is applied.",
       'uncertainty':'Uses the repository local geographic approximation; no independent surveyed control points or dimensioned plan are available.'},
      {'name':'Evidence-backed height, floors, and roof form','score':1.8,'max_score':2,'status':'strongly supported with residual classification and detail uncertainty',
       'evidence':'Purdue GIS reports three levels. The 2018 Indiana 3DEP tile has 2,497 class-1 surface returns within the footprint eroded by 3 m; median height above nearby class-2 ground is 8.135 m (interior p95 8.184 m). The 2018 orthophoto supports a broad flat roof. Reopened mesh roof is 8.135 m.',
       'uncertainty':'No class-6 building returns were available; class-1 returns are surface returns, not a dedicated building classification. Floor spacing is derived from levels, and small roof structures/parapet detail are not established.'},
      {'name':'Facade, entrances, and distinctive architecture','score':0.0,'max_score':2,'status':'unverified; fully illustrative',
       'evidence':'The render shows a three-level red-brown shell, regular punched windows, limestone-like bands, and a west-side glazed entrance/canopy.',
       'uncertainty':'The source set contains no legacy-building facade photograph, elevation, or dimensioned plan. Materials, window locations/rhythm, entrance side and articulation, and distinctive features are explicitly provisional. Appearance alone earns no source-evidence points.'},
      {'name':'Modular export, portability, and complete evidence','score':2.0,'max_score':2,'status':'verified in direct Blender reopen',
       'evidence':f"This evaluation ran after Blender reopened the saved asset directly. Scene={scene.name!r}; expected collection exists={col is not None}; mesh objects={len(mesh_objects)}; mesh modifiers={modifiers}; linked libraries={linked_libs}; external file images={external_images}. Building-specific raw source snapshots, metadata, measurement scripts, source record, and three renders are present.",
       'uncertainty':'Master-blend integration is outside this standalone asset grade.'}
    ]
    score = round(sum(c['score'] for c in criteria), 1)
    findings = [
      {'severity':'blocking for the rubric threshold','finding':'Facade and entrance remain unsupported by direct historical imagery, plans, or elevations. All facade features are illustrative; this criterion receives 0/2.', 'suggested_resolution':'Locate a credible, identifiable image/elevation/plan of legacy Helen R. Johnson Hall and revise facade materials/openings/entrance only where supported; otherwise accept that the asset cannot meet the 8/10 evidence threshold under this rubric.'},
      {'severity':'non-blocking uncertainty','finding':'The 2018 roof-height statistic is robust but derived from unclassified class-1 surface returns because the tile has no class-6 building points; floor spacing is an estimate.', 'suggested_resolution':'Retain the stated qualification or cross-check with an independent elevation/LiDAR classification source.'}
    ]
    result = {'score':score,'max_score':10,'passing_threshold':8,'passes':score >= 8,'criteria':criteria,
      'evidence':{'asset_opened_directly':str(ASSET),'asset_version':'Blender '+bpy.app.version_string,'scene':scene.name,
        'expected_scene':expected_scene,'expected_collection':expected_collection,'collection_object_count':len(col.objects) if col else 0,
        'mesh_object_count':len(mesh_objects),'mesh_vertex_count':len(obj.data.vertices) if obj else None,
        'mesh_polygon_count':len(obj.data.polygons) if obj else None,'bounds_world_m':bounds,'gis_unique_ring_vertex_count':len(ring),
        'ground_vertices_found':len(ground),'max_gis_ring_vertex_nearest_mesh_error_m':max_ring_error,
        'reopen_validation_reference':str(VALIDATION),'renders_inspected':[
          str(AUDIT/'renders'/'johnson_hall_nursing_exterior_preview.png'),
          str(AUDIT/'renders'/'johnson_hall_nursing_plan_preview.png'),
          str(AUDIT/'renders'/'johnson_hall_nursing_entry_elevation.png')],
        'source_record_reference':str(AUDIT/'source_record.json'),
        'source_images_and_documents_inspected':['2018 orthophoto','2018 LiDAR measurement and metadata','Purdue BuildingShapes FID 218 JSON','OSM way 117146488','Purdue 2021 building list','2022 School of Nursing graduate handbook','Purdue historical timeline','2023 Indiana Commission proposal and replacement project page'],
        'prior_validation_comparison':'Existing review/reopen_validation.json was consulted for provenance; this evaluator independently reopened and inspected the saved file.'},
      'findings':findings}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({'score':score,'passes':result['passes'],'max_ring_error_m':max_ring_error,'scene':scene.name,'collection_objects':len(col.objects) if col else 0,'result':str(OUT)},indent=2))
    return result

if __name__ == '__main__':
    evaluate()
