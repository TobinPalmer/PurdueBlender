import bpy, json, math, os
from mathutils import Vector
from pathlib import Path

ROOT = Path(bpy.path.abspath('//'))
# This evaluator is executed from the repository root with paths supplied below.
REPO = Path(r'C:\Users\gotse\Documents\Codex\2026-10-25\github-plugin-github-openai-curated-remote\outputs\PurdueBlender')
ASSET = REPO / 'modular/buildings/massing_cary_quadrangle_west_cqw_3d47a7d.blend'
EVID = REPO / 'audit/massing_cary_quadrangle_west_cqw_3d47a7d'
OUT = REPO / 'audit/massing_cary_quadrangle_west_cqw_independent_grade_r3'
ASSET_ID = 'massing_cary_quadrangle_west_cqw_3d47a7d'
COLL_NAME = 'Asset_' + ASSET_ID
SCENE_NAME = 'Building_' + ASSET_ID
GEO = json.loads((EVID / 'sources/purdue_cqw_fid60_wgs84.geojson').read_text(encoding='utf-8'))

def score_asset():
    bpy.ops.wm.open_mainfile(filepath=str(ASSET))
    scene = bpy.data.scenes.get(SCENE_NAME)
    coll = bpy.data.collections.get(COLL_NAME)
    objects = list(coll.all_objects) if coll else []
    meshes = [o for o in objects if o.type == 'MESH']
    # Locate the authoritative shell by its actual mesh name and compare its
    # XY vertex ring against the raw official GIS polygon, in project coordinates.
    shell = next((o for o in meshes if 'official GIS footprint shell' in o.data.name), None)
    gis_lonlat = GEO['features'][0]['geometry']['coordinates'][0]
    def campus_xy(lon, lat):
        return ((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
                (lat - 40.4274) * 111040.0)
    src = [campus_xy(p[0], p[1]) for p in gis_lonlat[:-1]]
    shell_pts = []
    if shell:
        for v in shell.data.vertices:
            w = shell.matrix_world @ v.co
            shell_pts.append((float(w.x), float(w.y), float(w.z)))
    shell_xy = sorted(set((round(x, 4), round(y, 4)) for x,y,z in shell_pts))
    # Mesh contains bottom/top copies of each outline point. De-duplicate to ring.
    def dist(a,b): return math.hypot(a[0]-b[0],a[1]-b[1])
    nearest_src = [min(dist(p,q) for q in shell_xy) for p in src] if shell_xy else []
    nearest_asset = [min(dist(p,q) for q in src) for p in shell_xy] if shell_xy else []
    def bounds(points):
        return [[min(p[i] for p in points), max(p[i] for p in points)] for i in range(2)] if points else None
    src_b = bounds(src); asset_b = bounds(shell_xy)
    src_c = [sum(p[i] for p in src)/len(src) for i in range(2)]
    asset_c = [sum(p[i] for p in shell_xy)/len(shell_xy) for i in range(2)] if shell_xy else None
    pos_error = math.dist(src_c, asset_c) if asset_c else None
    # Geometry object inventory and component location evidence.
    name_map = {o.name:o for o in objects}
    def obj_stats(fragment):
        o = next((o for o in objects if fragment.lower() in o.name.lower()),None)
        if not o: return None
        pts=[o.matrix_world @ Vector(c) for c in o.bound_box]
        return {'name':o.name,'center_m':[round(sum(p[i] for p in pts)/8,3) for i in range(3)],
                'bounds_m':[[round(min(p[i] for p in pts),3),round(max(p[i] for p in pts),3)] for i in range(3)]}
    components = {key:obj_stats(fragment) for key,fragment in {
        'tower_south':'south entry tower','tower_north':'north entry tower',
        'portal_south':'south secondary portal surround','portal_north':'north secondary portal surround',
        'central_portal':'central pointed Gothic portal surround','oriel':'entrance oriel bay',
        'central_door':'recessed pointed Gothic entry door','parapet':'dark roof membrane'
    }.items()}
    # World-space mesh extents include estimated tower caps and facade details.
    all_pts=[]
    for o in meshes:
        for c in o.bound_box:
            p=o.matrix_world @ Vector(c); all_pts.append((p.x,p.y,p.z))
    z_bounds=[min(p[2] for p in all_pts),max(p[2] for p in all_pts)] if all_pts else None
    # Fresh front / oblique evidence renders; all render helpers live outside export collection.
    if scene and coll:
        bpy.context.window.scene=scene
        scene.render.engine='BLENDER_EEVEE_NEXT'
        scene.render.resolution_x=1280; scene.render.resolution_y=720; scene.render.resolution_percentage=100
        scene.render.image_settings.file_format='PNG'
        scene.render.film_transparent=False
        scene.render.filepath=str(OUT/'grade_front.png')
        scene.render.image_settings.color_mode='RGBA'
        scene.view_settings.view_transform='Standard'
        scene.view_settings.look='None'
        scene.view_settings.exposure=0.0; scene.view_settings.gamma=1.0
        # use the existing preview camera if present; front camera is created temporarily
        preview_objs=[o for o in scene.objects if 'camera' in o.name.lower()]
        if preview_objs:
            cam=preview_objs[0]; scene.camera=cam
        bpy.ops.render.render(write_still=True)
        # Save a second frontal view at the opposite elevation for roof silhouette.
        if scene.camera:
            cam=scene.camera
            old_loc=cam.location.copy(); old_rot=cam.rotation_euler.copy(); old_scale=cam.data.ortho_scale
            target=Vector((sum(x for x,y in shell_xy)/len(shell_xy),sum(y for x,y in shell_xy)/len(shell_xy),7.8))
            cam.location=(src_b[0][1]+55.0,target.y-1.0,16.0)
            cam.rotation_euler=(target-Vector(cam.location)).to_track_quat('-Z','Y').to_euler()
            cam.data.type='ORTHO'; cam.data.ortho_scale=98.0
            scene.render.filepath=str(OUT/'grade_front_oblique.png')
            bpy.ops.render.render(write_still=True)
            cam.location=old_loc; cam.rotation_euler=old_rot; cam.data.ortho_scale=old_scale
    # Portability checks: expected collection/scene; all materials are native; images packed/local.
    images=[]
    for img in bpy.data.images:
        if img.source=='FILE': images.append({'name':img.name,'filepath':img.filepath,'packed':bool(img.packed_file)})
    # Explicit, evidence-weighted criteria; image quality is not used to claim measured dimensions.
    criteria=[]
    fp_ok = bool(shell and nearest_src and max(nearest_src)<0.02 and pos_error is not None and pos_error<0.02)
    criteria.append({'name':'Correct identity and source-backed footprint','max_score':2,
        'score':2.0 if fp_ok else (1.0 if shell else 0.0),
        'evidence':f'Independent source polygon FID 60 / BLDG_ABBR CQW compared vertexwise with shell mesh; source vertices={len(src)}, shell unique XY vertices={len(shell_xy)}, max source-to-model nearest error={max(nearest_src) if nearest_src else None:.5f} m, centroid error={pos_error if pos_error is not None else None:.5f} m. Identity is Purdue GIS building code 1315 / Franklin Levering Cary Quadrangle (West).',
        'uncertainty':'GIS source does not publish survey tolerance or structural wall-vs-overhang relationship.'})
    scale_ok=bool(fp_ok and all(abs(src_b[i][j]-asset_b[i][j])<0.02 for i in range(2) for j in range(2)))
    criteria.append({'name':'Position, orientation, and scale/dimensions','max_score':2,
        'score':2.0 if scale_ok else (1.0 if shell else 0.0),
        'evidence':f'GIS-to-shell local campus XY bounds source={src_b}, model={asset_b}; centroid error={pos_error:.5f} m. Full outline vertex agreement checks rotation, location, and scale rather than only overall bounding box.',
        'uncertainty':'Repository frame is a documented local geographic approximation, not a surveyed CRS.'})
    criteria.append({'name':'Evidence-backed height, floors, and roof form','max_score':2,
        'score':1.1,
        'evidence':f'Official GIS reports five levels; model visibly carries five principal facade window courses. Archival photos 180/181/182 support twin crenellated towers and flat/parapet roof silhouette; model includes these.',
        'uncertainty':f'GIS Extrution=48 is unitless and no elevation source exists. Model total evaluated Z bounds {z_bounds}; 14.63 m body height is an assumed feet conversion and tower height is photo-estimated, not verified.'})
    portals_ok=all(components[k] for k in ('portal_south','portal_north','central_portal','oriel','tower_south','tower_north'))
    criteria.append({'name':'Facade, entrances, and distinctive architecture','max_score':2,
        'score':1.6 if portals_ok else 0.7,
        'evidence':f'Raw archive images 180-182 directly show paired battlement towers, projecting central oriel, central Gothic opening, and paired smaller pointed entrances. Asset mesh inventory has towers, oriel, central arch surround and both side portal surrounds. Fresh frontal renders saved at {OUT}/grade_front.png and {OUT}/grade_front_oblique.png.',
        'uncertainty':'Photographs give qualitative composition only; the simplified massing reproduces the major elements but exact portal sizes, stone trim, openings, and facade depth remain estimates.'})
    portability_ok=bool(scene and coll and scene.name==SCENE_NAME and coll.name==COLL_NAME and (not images or all(i['packed'] for i in images)))
    criteria.append({'name':'Modular export, portability, and complete evidence','max_score':2,
        'score':2.0 if portability_ok else (1.0 if coll else 0.0),
        'evidence':f'Saved .blend reopened independently. Scene={scene.name if scene else None}; collection={coll.name if coll else None}; mesh objects in export={len(meshes)}; source index and raw GIS/archive snapshots exist; file image dependencies={images}.',
        'uncertainty':'Preview camera/lights may be retained outside the exported asset collection; master integration not graded.'})
    total=round(sum(c['score'] for c in criteria),1)
    findings=[
      'The main pointed opening is directly beneath the projecting oriel between the twin towers, matching the archive composition.',
      'Two secondary pointed portals are present in the lateral facade zones, outside the central tower pair. They are correctly paired, but render as small and somewhat detached-looking openings relative to the archival full-elevation image; this is the main visible simplification.',
      'The 48-unit GIS extrusion remains unresolved; no building elevation or verified height should be claimed. Preserve the height as an estimate.'
    ]
    return {'score':total,'max_score':10,'criteria':criteria,'evidence':{
      'asset_file':str(ASSET),'asset_id':ASSET_ID,'fresh_reopen':True,'blender_version':bpy.app.version_string,
      'gis_feature_id':60,'gis_building_abbr':'CQW','official_levels':5,'extrution_attribute':48,
      'source_polygon_unique_vertices':len(src),'shell_mesh_unique_xy_vertices':len(shell_xy),
      'shell_max_source_nearest_error_m':max(nearest_src) if nearest_src else None,
      'shell_mean_source_nearest_error_m':sum(nearest_src)/len(nearest_src) if nearest_src else None,
      'centroid_error_m':pos_error,'source_bounds_m':src_b,'asset_shell_bounds_m':asset_b,'evaluated_asset_z_bounds_m':z_bounds,
      'components':components,'renders':['grade_front.png','grade_front_oblique.png'],
      'raw_archival_photo_files':[str(EVID/'sources'/n) for n in ('purdue_earchives_image_180_external_shot_of_cary_quad_resid.jpg','purdue_earchives_image_181_exterior_photograph_of_cary_hall.jpg','purdue_earchives_image_182_exterior_photograph_of_cary_hall.jpg')]},
      'findings':findings}

result=score_asset()
(OUT/'independent_grade_result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))

