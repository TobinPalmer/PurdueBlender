import bpy, json, math, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSET_ID = 'massing_cary_quadrangle_northwest_cqnw_e8a861e'
ASSET = ROOT / 'modular' / 'buildings' / f'{ASSET_ID}.blend'
EVIDENCE = ROOT / 'audit' / ASSET_ID
OUT = ROOT / 'audit' / 'massing_cary_quadrangle_northwest_cqnw_independent_grade'
COLLECTION_NAME = f'Asset_{ASSET_ID}'
SOURCE = EVIDENCE / 'sources' / 'purdue_building_shapes_fid647_2026-10-26.geojson'


def project(lon, lat):
    return ((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
            (lat - 40.4274) * 111040.0)


def point_segment(p, a, b):
    dx, dy = b[0]-a[0], b[1]-a[1]
    d2 = dx*dx + dy*dy
    t = 0 if d2 == 0 else max(0.0, min(1.0, ((p[0]-a[0])*dx+(p[1]-a[1])*dy)/d2))
    return math.hypot(p[0]-(a[0]+t*dx), p[1]-(a[1]+t*dy))


def min_outline_distance(p, ring):
    return min(point_segment(p, ring[i], ring[(i+1) % len(ring)]) for i in range(len(ring)))


def bounds_xy(points):
    return [[min(p[0] for p in points), max(p[0] for p in points)],
            [min(p[1] for p in points), max(p[1] for p in points)]]


def area(ring):
    return abs(sum(ring[i][0]*ring[(i+1)%len(ring)][1] - ring[(i+1)%len(ring)][0]*ring[i][1]
                   for i in range(len(ring))) / 2)


def run():
    OUT.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(ASSET))
    scene = bpy.context.scene
    collection = bpy.data.collections.get(COLLECTION_NAME)
    if collection is None:
        raise RuntimeError('Expected exported asset collection is absent')
    objs = list(collection.objects)
    mesh_objs = [o for o in objs if o.type == 'MESH']
    depsgraph = bpy.context.evaluated_depsgraph_get()
    all_verts = []
    object_summary = []
    for ob in mesh_objs:
        ev = ob.evaluated_get(depsgraph)
        me = ev.to_mesh()
        coords = [ev.matrix_world @ v.co for v in me.vertices]
        ev.to_mesh_clear()
        all_verts.extend(coords)
        object_summary.append({'name': ob.name, 'type': ob.type,
                               'vertices': len(ob.data.vertices), 'faces': len(ob.data.polygons),
                               'location': list(ob.location), 'rotation_euler': list(ob.rotation_euler),
                               'scale': list(ob.scale), 'modifiers': [m.type for m in ob.modifiers],
                               'external_image_paths': [im.filepath for im in ob.data.materials if im and im.use_nodes
                                                        for node in im.node_tree.nodes if node.type == 'TEX_IMAGE' and node.image]})
    all_world = [(v.x, v.y, v.z) for v in all_verts]
    total_bounds = [[min(p[i] for p in all_world), max(p[i] for p in all_world)] for i in range(3)]
    foundation = bpy.data.objects.get('CQNW_Stone_Foundation')
    if foundation is None:
        raise RuntimeError('Foundation mesh used for footprint evaluation absent')
    foundation_world = [(foundation.matrix_world @ v.co)[:] for v in foundation.data.vertices]
    base_ring = [(float(x), float(y)) for x, y, z in foundation_world if abs(z) < 1e-5]
    fc = json.loads(SOURCE.read_text(encoding='utf-8-sig'))
    feat = fc['features'][0]
    raw = [project(lon, lat) for lon, lat in feat['geometry']['coordinates'][0]]
    if math.dist(raw[0], raw[-1]) < 1e-5:
        raw.pop()
    raw_to_model = [min_outline_distance(p, base_ring) for p in raw]
    model_to_raw = [min_outline_distance(p, raw) for p in base_ring]
    gis_bounds = bounds_xy(raw)
    mesh_bounds = bounds_xy(base_ring)
    gis_area = area(raw)
    mesh_area = area(base_ring)
    # Cross-reference prior manifest inventory as a separate, older AABB reference.
    manifest = json.loads((ROOT/'modular'/'manifest.json').read_text(encoding='utf-8'))
    m = next(a for a in manifest['assets'] if a['id'] == ASSET_ID)
    mb = m['bounds_world_m']
    bb_center = lambda b: [(b[i][0]+b[i][1])/2 for i in range(2)]
    gis_center = bb_center(gis_bounds)
    manifest_center = bb_center(mb)
    center_delta = math.dist(gis_center, manifest_center)
    width_delta = [gis_bounds[i][1]-gis_bounds[i][0] - (mb[i][1]-mb[i][0]) for i in range(2)]
    metadata = {k: collection.get(k) for k in ('asset_id','building_name','source_feature','coordinate_contract','height_status','architecture_status')}
    probe = {
      'asset_path': str(ASSET.relative_to(ROOT)), 'blender_version': bpy.app.version_string,
      'scene': scene.name, 'expected_scene': f'Building_{ASSET_ID}',
      'collection': collection.name, 'object_count': len(objs), 'mesh_object_count': len(mesh_objs),
      'collection_metadata': metadata, 'evaluated_bounds_world_m': total_bounds,
      'asset_object_checks': {'all_mesh': len(mesh_objs)==len(objs),
        'all_scales_unit': all(all(abs(x-1)<1e-6 for x in o['scale']) for o in object_summary),
        'all_rotations_identity': all(all(abs(x)<1e-6 for x in o['rotation_euler']) for o in object_summary),
        'no_modifiers': all(not o['modifiers'] for o in object_summary),
        'no_external_texture_files': all(not o['external_image_paths'] for o in object_summary),
        'scene_name_matches': scene.name == f'Building_{ASSET_ID}'},
      'gis_footprint_independent_comparison': {'feature_id':feat['properties']['FID'],
        'building_abbreviation':feat['properties']['BLDG_ABBR'], 'building_name':feat['properties']['BUILDING_N'],
        'raw_ring_vertices':len(raw), 'simplified_shell_vertices':len(base_ring),
        'projected_gis_bounds_xy_m':gis_bounds, 'shell_bounds_xy_m':mesh_bounds,
        'projected_gis_area_m2':gis_area, 'shell_area_m2':mesh_area,
        'area_ratio_shell_to_gis':mesh_area/gis_area,
        'raw_gis_to_model_boundary_distance_m': {'max':max(raw_to_model),'mean':sum(raw_to_model)/len(raw_to_model)},
        'model_to_raw_gis_boundary_distance_m': {'max':max(model_to_raw),'mean':sum(model_to_raw)/len(model_to_raw)},
        'transform':'project_lon_lat from modular/AGENTS.md, using WGS84 EPSG:4326 source geometry; approximate local conversion, not survey CRS'},
      'comparison_to_manifest_prior_aabb': {'manifest_bounds_xy_m':mb[:2], 'gis_aabb_center_difference_m':center_delta,
         'gis_width_depth_difference_m':width_delta,
         'interpretation':'Manifest AABB is older prior model inventory; GIS-derived reconstruction directly uses official FID 647. The difference is recorded, not treated as proof of a placement error.'},
      'asset_objects':object_summary
    }
    (OUT/'blender_probe.json').write_text(json.dumps(probe,indent=2)+'\n',encoding='utf-8')
    return probe

if __name__ == '__main__':
    result=run()
    print(json.dumps(result,indent=2))



def evaluate():
    probe = json.loads((OUT/'blender_probe.json').read_text(encoding='utf-8'))
    ev = EVIDENCE
    src = ev/'sources'
    ndhm = json.loads((src/'cqnw_ndhm_analysis.json').read_text(encoding='utf-8'))
    criteria = [
      {'name':'Correct identity and source-backed footprint','score':2.0,'max_score':2,
       'evidence':['Purdue BuildingShapesZip4 FID 647 identifies BLDG_ABBR=CQNW and Franklin Levering Cary Quadrangle (NW).',
         'The rebuilt shell uses the returned 112-point GIS boundary simplified to 55 vertices at the stated 0.5 m tolerance.',
         f"Independent boundary comparison: max raw GIS vertex to shell-boundary distance {probe['gis_footprint_independent_comparison']['raw_gis_to_model_boundary_distance_m']['max']:.3f} m; shell area is {probe['gis_footprint_independent_comparison']['area_ratio_shell_to_gis']:.4f} of projected source-polygon area."],
       'findings':['Source attributes Shape_Area/Shape_Length conflict with the returned polygon measurements; model consistently uses the actual returned geometry.']},
      {'name':'Position, orientation, and scale/dimensions','score':1.6,'max_score':2,
       'evidence':['The model remains in the repository campus world frame with unit object scales and identity rotations; coordinates are computed directly from the authoritative source geometry using the conversion documented in modular/AGENTS.md.',
         f"The prior manifest AABB center differs from the current GIS-derived AABB center by {probe['comparison_to_manifest_prior_aabb']['gis_aabb_center_difference_m']:.2f} m; source-derived current bounds are independently recorded in blender_probe.json.",
         'Plan extent is derived from the polygon, approximately 67.6 by 16.5 m; footprint comparison is detailed in blender_probe.json.'],
       'findings':['Campus conversion is a local approximation rather than a survey CRS. The prior inventory AABB differs by about 1.46 m at center and needs coordinator review if the master marker or neighbor alignment is later adjusted.']},
      {'name':'Evidence-backed height, floors, and roof form','score':1.4,'max_score':2,
       'evidence':['Purdue GIS records five levels. A current 2023 IndianaMap orthophoto supports the long east-west mass and repeated roof interruptions.',
         f"The 2018 3DEP normalized height model has {ndhm['samples']} interior samples: roof/vegetation surface median {ndhm['percentiles_m']['median']:.2f} m, p10-p90 {ndhm['percentiles_m']['p10']:.2f}-{ndhm['percentiles_m']['p90']:.2f} m.",
         'The modeled 14.9 m ridge lies inside the sampled surface range; the asset metadata labels it an estimate.'],
       'findings':['NDHM is a normalized roof/vegetation surface and does not separately measure wall height, eave height, or ridge height. The chosen 14.9 m peak is near the surface p90, not a measured ridge. GIS five-level count does not state whether basement or attic counts; four window rows plus a raised base are an interpretation.']},
      {'name':'Facade, entrances, and distinctive architecture','score':0.7,'max_score':2,
       'evidence':['The current aerial supports the overall roof plan; current housing documentation confirms the complex/unit context.',
         'A 1928 Cary archive image shows contextual brick, repeated windows, and roof forms but predates CQNW construction in 1938 and does not identify the NW unit.'],
       'findings':['Brick/stone color, window cadence, stone courses, gable projection geometry, and the pointed-arch entrance are not established by a CQNW-specific elevation or photograph. The builder labels the facade and entry as interpretations; these details must remain provisional.']},
      {'name':'Modular export, portability, and complete evidence','score':1.8,'max_score':2,
       'evidence':['Reopened the saved asset in Blender 4.5.15 LTS. Expected scene and collection exist; 21 collection meshes evaluate to bounds -433.12..-364.10 m X, 581.23..601.31 m Y, and 0..14.90 m Z.',
         'All asset objects have identity rotations, unit scales, and no modifiers. No external texture paths were found.',
         'The building evidence includes raw GIS GeoJSON, orthophoto, NDHM raster and reproducible sampling script, historical/source snapshots, preview views, and reopen validation.'],
       'findings':['The static manifest still declares one named object while the rebuilt export has 21 mesh objects and no object named exactly “Cary Quadrangle Northwest (CQNW)”. The collection contract is met, but the manifest object inventory may need coordinator reconciliation.']}
    ]
    score = round(sum(c['score'] for c in criteria),1)
    result = {
      'asset_id':ASSET_ID, 'asset_path':'modular/buildings/massing_cary_quadrangle_northwest_cqnw_e8a861e.blend',
      'evaluator':'Independent source-and-asset inspection; separate process reopened saved Blender file and compared foundation boundary to raw GIS geometry.',
      'score':score,'max_score':10,'passing_threshold':8,'passed':score>=8,
      'criteria':criteria,
      'evidence':{
        'blender_probe':'blender_probe.json','blender_log':'blender_reopen_grade.log',
        'preview_paths':['../massing_cary_quadrangle_northwest_cqnw_e8a861e/cqnw_preview.png','../massing_cary_quadrangle_northwest_cqnw_e8a861e/cqnw_top_preview.png','../massing_cary_quadrangle_northwest_cqnw_e8a861e/sources/cqnw_orthophoto_footprint_overlay.png'],
        'primary_sources':[
          {'title':'Purdue BuildingShapesZip4 FeatureServer FID 647','url':'https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query?where=FID%3D647&outFields=*&returnGeometry=true&outSR=4326&f=geojson','snapshot':'../massing_cary_quadrangle_northwest_cqnw_e8a861e/sources/purdue_building_shapes_fid647_2026-10-26.geojson'},
          {'title':'IndianaMap 2023 orthophoto','url':'https://di-ingov.img.arcgis.com/arcgis/rest/services/DynamicWebMercator/Indiana_2023_Imagery/ImageServer','snapshot':'../massing_cary_quadrangle_northwest_cqnw_e8a861e/sources/indiana_2023_orthophoto_cqnw.jpg'},
          {'title':'Indiana 3DEP 2018 normalized height model tile','url':ndhm['url'],'snapshot':'../massing_cary_quadrangle_northwest_cqnw_e8a861e/sources/in2018_29951885_12_ndhm.tif'},
          {'title':'Purdue Campus Facilities and Buildings Historic Database, record 358','url':'https://collections.lib.purdue.edu/campus/buildings/358','snapshot':'../massing_cary_quadrangle_northwest_cqnw_e8a861e/sources/purdue_historic_building_entry_358_2026-10-26.html'},
          {'title':'Purdue Archives and Special Collections, item 165 (1928 Cary context; predates CQNW)','url':'https://earchives.lib.purdue.edu/digital/collection/pbuildings/id/165/','snapshot':'../massing_cary_quadrangle_northwest_cqnw_e8a861e/sources/purdue_archives_cary_exterior_1928_item165.jpg'}
        ]},
      'findings':[
        'FAILS the required 8/10 threshold at the current evidence level. Strong identity and footprint matching make this a usable massing asset, but facades, entrance, and a precise ridge height are not independently established.',
        'Do not describe the NDHM median or p90 as ridge measurements. Preserve 14.9 m as an estimate unless a building-specific elevation or roof-height source is found.',
        'No building or shared files were changed by this grader.'
      ]
    }
    (OUT/'result.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    return result

if __name__ == '__main__':
    result = evaluate()
    print(json.dumps({'score':result['score'],'max_score':result['max_score'],'passed':result['passed'],'criteria':result['criteria'],'findings':result['findings']},indent=2))

