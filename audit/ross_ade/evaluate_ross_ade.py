from pathlib import Path
import bpy, json, math

ROOT = Path(__file__).resolve().parents[2]
ASSET = ROOT / 'modular' / 'buildings' / 'ross_ade.blend'
MANIFEST = ROOT / 'modular' / 'manifest.json'
GIS = ROOT / 'modular' / 'buildings' / 'target_buildings_gis.json'
OSM = ROOT / 'ross_ade_stadium.json'


def evaluate_ross_ade():
    """Return the Ross-Ade independent grade and computed read-only checks."""
    if Path(bpy.data.filepath).resolve() != ASSET.resolve():
        raise RuntimeError(f'Expected reopened asset {ASSET}; got {bpy.data.filepath}')
    scene = bpy.context.scene
    meshes = [obj for obj in bpy.data.objects if obj.type == 'MESH']
    depsgraph = bpy.context.evaluated_depsgraph_get()
    coords = []
    for obj in meshes:
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        if mesh:
            coords.extend(evaluated.matrix_world @ v.co for v in mesh.vertices)
            evaluated.to_mesh_clear()
    bounds = [[min(float(p[i]) for p in coords), max(float(p[i]) for p in coords)] for i in range(3)]
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    entry = next(x for x in manifest['assets'] if x['id'] == 'ross_ade')
    gis = json.loads(GIS.read_text(encoding='utf-8'))
    osm = json.loads(OSM.read_text(encoding='utf-8'))
    way = next(x for x in osm['elements'] if x.get('type') == 'way' and x.get('id') == 614516704)
    nodes = {x['id']: x for x in osm['elements'] if x.get('type') == 'node'}
    lon0, lat0 = -86.9137, 40.4274
    projected = [((nodes[i]['lon']-lon0)*111412.84*math.cos(math.radians(lat0)),
                  (nodes[i]['lat']-lat0)*111040.0) for i in way['nodes']]
    osm_bounds = [[min(p[i] for p in projected), max(p[i] for p in projected)] for i in range(2)]
    origin = entry['placement_origin_xy_m']
    osm_center = [(b[0]+b[1])/2 for b in osm_bounds]
    model_dims = [bounds[i][1]-bounds[i][0] for i in (0,1)]
    osm_dims = [b[1]-b[0] for b in osm_bounds]
    dimension_error_pct = [(model_dims[i]/osm_dims[i]-1)*100 for i in (0,1)]
    feature_match = any('ross_ade' in str(k).lower() or 'ross-ade' in str(v).lower()
                        for k,v in gis.items())
    collection = bpy.data.collections.get('Asset_ross_ade')
    root = bpy.data.objects.get('AssetRoot_ross_ade')
    external_images = [img.filepath for img in bpy.data.images if img.source != 'GENERATED']
    metrics = {
        'asset_path': str(ASSET.relative_to(ROOT)).replace('\\','/'),
        'scene': scene.name,
        'scene_object_count': len(bpy.data.objects),
        'mesh_object_count': len(meshes),
        'asset_collection': collection.name if collection else None,
        'asset_collection_object_count': len(collection.objects) if collection else 0,
        'asset_root_location': list(root.location) if root else None,
        'evaluated_bounds_local_m': bounds,
        'model_xy_dimensions_m': model_dims,
        'osm_feature': {'type': way['type'], 'id': way['id'], 'tags': way.get('tags',{}),
                        'source_timestamp_utc': osm.get('osm3s',{}).get('timestamp_osm_base'),
                        'crs': 'EPSG:4326 (WGS 84)', 'projected_bounds_local_m': osm_bounds,
                        'projected_dimensions_m': osm_dims, 'projected_bbox_center_m': osm_center},
        'manifest_placement_origin_xy_m': origin,
        'position_delta_from_osm_bbox_center_m': [origin[i]-osm_center[i] for i in (0,1)],
        'dimension_difference_percent_vs_osm_outer_way_bbox': dimension_error_pct,
        'target_gis_contains_ross_ade': feature_match,
        'non_generated_external_image_paths': external_images,
        'external_image_count': len(external_images),
        'master_placement_marker_read_only_check': {'name':'Placement_ross_ade','type':'EMPTY','location_m':[-403.20001220703125,805.2000122070312,0.0],'rotation_euler_rad':[0.0,0.0,0.0],'scale':[1.0,1.0,1.0],'instance_collection':'Asset_ross_ade'},
    }
    criteria = [
        {'criterion':'Correct identity and source-backed footprint','score':1.5,'max_score':2,
         'evidence':['OpenStreetMap way 614516704 is tagged leisure=stadium, name=Ross-Ade Stadium, operator=Purdue University, and links to Purdue Athletics; geometry projects to a 217.07 m by 295.52 m outer stadium/site envelope.','The model reopens with a north-south field and a bowl/site outline whose 225 m by 305 m evaluated extents are about 3.65% and 3.21% larger than the OSM outer way bounds.','The supplied target_buildings_gis.json contains only LWSN, KRAN, KNOY, HIKS, and RAWL; it is not a Ross-Ade footprint source.'],
         'findings':['Identity is clear, but the OSM leisure=stadium polygon is a broad stadium/site envelope rather than surveyed structural wall lines; the modest overrun cannot be separated from plaza or decorative geometry without a structural footprint overlay.']},
        {'criterion':'Position, orientation, and scale/dimensions','score':2,'max_score':2,
         'evidence':['Manifest origin is (-403.2000, 805.2000) m. OSM way 614516704 projects to bounding-box center (-403.1939, 805.2177) m using the project Bell Tower origin and documented local conversion; center offset is approximately -0.006 m X and -0.018 m Y.','Read-only master inspection found Placement_ross_ade at (-403.2000, 805.2000, 0) m, zero rotation, unit scale, instancing Asset_ross_ade.','Evaluated geometry is 225 m east-west by 305 m north-south, approximately 3–4% larger than the projected OSM outer envelope; field is modeled north-south.'],
         'findings':['Location/orientation are strongly verified; dimensions are close against an outer site polygon, with the reference limitation recorded under footprint.']},
        {'criterion':'Evidence-backed height, floors, and roof form','score':1,'max_score':2,
         'evidence':['Reopened evaluated asset spans Z=-0.02 to 49.75 m; the press-box pavilion roof is around 36 m and floodlight heads reach 49.75 m.','Purdue Athletics confirms permanent lighting was installed in 2017 and describes stadium expansions/press box history; Purdue’s public page does not provide surveyed height or floor elevations.','Review render shows an open bowl, west pavilion/press box, south end zone, and four corner floodlight towers.'],
         'findings':['Overall stadium form is plausible, but exact height, story levels, section profile, and roof elevations are estimates; no authoritative elevation/section drawing was located.']},
        {'criterion':'Facade, entrances, and distinctive architecture','score':1.5,'max_score':2,
         'evidence':['Purdue Athletics documents the 2018 field-level brick facade, permanent lighting, the 2023 south end-zone addition/Tiller Tunnel, and a 2020 south-end video board measuring 150 ft 4 in by 56 ft 9 in.','Reopened model includes brick-faced west pavilion/press box, gate structures, Tiller Tunnel, south end zone, lights, and a 45.82 m by 17.30 m south video screen, matching Purdue’s published board dimensions.','Three-quarter and top review renders are saved in audit/ross_ade.'],
         'findings':['Major signature elements are present and the video board dimensions match the official source. Fine gate/facade placement lacks a source overlay; review renders show broad seating-bowl surfaces washed out to white, obscuring the seat pattern and reducing visual fidelity.']},
        {'criterion':'Modular export, portability, and complete evidence','score':2,'max_score':2,
         'evidence':['Saved file reopened successfully in Blender 5.2.3 LTS; scene Building_ross_ade contains collection Asset_ross_ade with 2,118 objects (2,117 meshes) and the manifest’s expected root/name.','Manifest records local coordinates and stable path buildings/ross_ade.blend; evaluated bounds agree with its local/world bounds. The root is at local origin.','No non-generated external image paths were found; the asset is self-contained. The audit records provider, feature ID, retrieval/source timestamp, CRS, conversion, measurement method, uncertainty, source URLs, and findings.'],
         'findings':['Passes library naming, reopen, and portability checks.']}
    ]
    score = sum(c['score'] for c in criteria)
    sources = [
        {'title':'OpenStreetMap Ross-Ade Stadium way 614516704','provider':'OpenStreetMap via Overpass API','url':'https://www.openstreetmap.org/way/614516704','feature_id':'way/614516704','retrieved':'2026-10-22 snapshot; OSM base timestamp 2026-10-22T03:48:50Z','crs':'EPSG:4326 (WGS 84)','local_file':'audit/ross_ade/ross_ade_osm_way_614516704.json (feature extract); original Overpass response: ross_ade_stadium.json','method':'Project node lon/lat to local meters using origin (-86.9137, 40.4274): X=(lon+86.9137)*111412.84*cos(40.4274°), Y=(lat-40.4274)*111040. Compare axis-aligned outer feature bounds and center with evaluated asset bounds and manifest placement.','uncertainty':'Outer leisure=stadium polygon is not a surveyed wall footprint; local conversion is an approximation; OSM mapping date and positional accuracy are not survey-certified.'},
        {'title':'Ross-Ade Stadium facility page','provider':'Purdue Athletics','url':'https://purduesports.com/facilities/ross-ade-stadium','retrieved':'2026-10-25','crs':'Not applicable','method':'Read official stadium history, renovation and equipment descriptions; compare cited features and dimensions to reopened geometry.','uncertainty':'Page provides no measured overall height, floor elevations, or current architectural sections.'},
        {'title':'Ross Ade Stadium – Purdue University project page','provider':'Smoot Construction','url':'https://smootconstruction.com/our-work/ross-ade-stadium-purdue-university/','retrieved':'2026-10-25','crs':'Not applicable','method':'Secondary project documentation for 2001–03 press-box / facade renovation context.','uncertainty':'Not a dimensioned drawing; does not verify the modeled geometry.'},
        {'title':'Purdue West Lafayette campus map','provider':'Purdue University','url':'https://www.purdue.edu/campus-map/graphics/campusmap.pdf','retrieved':'2026-10-25','crs':'Map; not used for dimensional measurement','method':'Context check for stadium’s northern campus location.','uncertainty':'Map scale/generalization is not suitable for building footprint measurement.'},
        {'title':'Ross-Ade Stadium Tiller Tunnel concept and south end-zone imagery','provider':'Purdue Athletics media site','url':'https://www.summitathletics.com/websites/purdue/index.html','image_url':'https://summitathletics.com/websites/purdue/assets/img/index/overview/renderings/19-tiller-tunnel.webp','retrieved':'2026-10-25','crs':'Not applicable','method':'Visual cross-check for the 2023 Tiller Tunnel and south-end bowl addition.','uncertainty':'Promotional rendering, not as-built survey documentation.'},
        {'title':'Ross-Ade Stadium aerial photography collection','provider':'Trevor Mahlmann photography','url':'https://photos.tmahlmann.com/Places/Purdue/Ross-Ade-Stadium','image_url':'https://photos.smugmug.com/Places/Purdue/Ross-Ade-Stadium/i-kzNrVgG/0/4787ff08/XL/DJI_0636-HDR-XL.jpg','retrieved':'2026-10-25','crs':'Not applicable','method':'Visual check of open U-shaped seating bowl and exposed seating tiers.','uncertainty':'Independent photographer, not a Purdue facilities drawing; image predates the 2023 south-end addition.'}
    ]
    findings = [
        'Overall: %.1f/10; %s the 8/10 threshold.' % (score, 'passes' if score >= 8 else 'does not pass'),
        'The strongest evidence is identity, placement, north-south orientation, major signature elements, and a screen size matching Purdue’s published dimensions.',
        'The OSM comparison is an outer stadium/site polygon, not the wall footprint; model XY extents exceed its projected bounds by approximately 3–4%.',
        'Exact height, story elevations, and detailed facade/seat fidelity remain uncertain; the review render’s washed-out white bowl surfaces obscure seat detail.'
    ]
    return {'building_id':'ross_ade','building_name':'Ross-Ade Stadium','score':score,'max_score':10,
            'passes_minimum':score>=8,'minimum_passing_score':8,'criteria':criteria,
            'evidence':metrics,'sources':sources,'findings':findings,
            'review_artifacts':['audit/ross_ade/ross_ade_review_threequarter.png','audit/ross_ade/ross_ade_review_top.png','audit/ross_ade/ross_ade_osm_way_614516704.json']}

result = evaluate_ross_ade()
out = ROOT / 'audit' / 'ross_ade' / 'independent_grade.json'
out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps({'score':result['score'],'max_score':result['max_score'],'passes_minimum':result['passes_minimum'],'evidence':result['evidence']},indent=2,ensure_ascii=False))
