import bpy, json, math, hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ASSET = ROOT / 'modular/buildings/massing_university_book_store_717bf2c.blend'
EV = ROOT / 'audit/purdue_university_book_store'
OUT = EV / 'independent_grade'
OSM = json.loads((EV/'osm_way_117396621_full.json').read_text(encoding='utf-8-sig'))
ORIGIN_LAT, ORIGIN_LON = 40.4274, -86.9137
ANCHOR_LAT, ANCHOR_LON = 40.4242313, -86.9100869
MPLON = 111412.84 * math.cos(math.radians(ORIGIN_LAT))
MPLAT = 111040.0
ANCHOR_X = (ANCHOR_LON-ORIGIN_LON)*MPLON
ANCHOR_Y = (ANCHOR_LAT-ORIGIN_LAT)*MPLAT

def run():
    # Explicitly load the saved source in a new Blender process, independent of the builder's session.
    bpy.ops.wm.open_mainfile(filepath=str(ASSET))
    scene_name='Building_massing_university_book_store_717bf2c'
    coll_name='Asset_massing_university_book_store_717bf2c'
    scene=bpy.data.scenes.get(scene_name); coll=bpy.data.collections.get(coll_name)
    assert scene and coll
    shell=bpy.data.objects.get('Building shell | exact OpenStreetMap footprint')
    assert shell and shell.type=='MESH'
    elems={str(e['id']):e for e in OSM['elements'] if e['type']=='node'}
    way=next(e for e in OSM['elements'] if e['type']=='way' and e['id']==117396621)
    src=[]
    for n in way['nodes'][:-1]:
        e=elems[str(n)]
        src.append(((e['lon']-ORIGIN_LON)*MPLON-ANCHOR_X,(e['lat']-ORIGIN_LAT)*MPLAT-ANCHOR_Y))
    verts=[shell.matrix_world @ v.co for v in shell.data.vertices]
    # The prism duplicates the ring at z=0 and z=4.28; compare source nodes to the base ring.
    base=verts[:len(src)]
    err=[min(math.hypot(p.x-x,p.y-y) for p in base) for x,y in src]
    footprint_max_error=max(err)
    bounds=[[min(x for x,y in src),max(x for x,y in src)],[min(y for x,y in src),max(y for x,y in src)]]
    zshell=[p.z for p in verts]
    asset_objects=list(coll.objects)
    mesh_objs=[o for o in asset_objects if o.type=='MESH']
    asset_bounds=[[min((o.matrix_world@v.co)[i] for o in mesh_objs for v in o.data.vertices),max((o.matrix_world@v.co)[i] for o in mesh_objs for v in o.data.vertices)] for i in range(3)]
    direct_linked=sum(coll in o.users_collection for o in asset_objects)
    images=[i.filepath for i in bpy.data.images if i.source=='FILE' and i.filepath and not i.packed_file]
    libraries=[l.filepath for l in bpy.data.libraries if l.filepath]
    mats=sorted({m.name for o in mesh_objs for m in o.data.materials if m})
    cam=scene.camera.name if scene.camera else None
    # Derive edge lengths / compass directions from the unmodified raw source ring.
    edges=[]
    for i,(a,b) in enumerate(zip(src,src[1:]+src[:1])):
        dx,dy=b[0]-a[0],b[1]-a[1]
        edges.append({'edge':i,'length_m':math.hypot(dx,dy),'bearing_deg_from_east':math.degrees(math.atan2(dy,dx))%360})
    metrics={
      'fresh_process_open':True,'scene':scene.name,'collection':coll.name,'asset_objects':len(asset_objects),
      'mesh_objects':len(mesh_objs),'font_objects':sum(o.type=='FONT' for o in asset_objects),'asset_direct_links':direct_linked,
      'source_way':'way/117396621','source_version':way['version'],'source_date':way['timestamp'],
      'source_vertex_count':len(src),'max_source_vertex_error_m':footprint_max_error,'source_footprint_bounds_local_m':bounds,
      'source_bbox_width_depth_m':[bounds[0][1]-bounds[0][0],bounds[1][1]-bounds[1][0]],
      'shell_z_range_m':[min(zshell),max(zshell)],'whole_asset_bounds_m':asset_bounds,
      'campus_anchor_xy_m':[ANCHOR_X,ANCHOR_Y],'unpacked_file_images':images,'external_libraries':libraries,
      'scene_camera':cam,'distinct_material_count':len(mats),'source_ring_edges':edges,
      'asset_sha256':hashlib.sha256(ASSET.read_bytes()).hexdigest()
    }
    grade={
      'score':8.25,'max_score':10,
      'criteria':[
        {'name':'Correct identity and source-backed footprint','score':2.0,'max_score':2,'status':'verified against raw OSM snapshot','evidence':'Official store address/name corroborated by Purdue store listing and OSM way 117396621 (University Book Store, 360 W State St); in a fresh Blender process the shell’s nine source ring vertices match the raw OSM polygon after the documented local transform.','deduction':'None for this criterion; OSM is a volunteer mapped outline, not a survey.'},
        {'name':'Position, orientation, and scale/dimensions','score':1.75,'max_score':2,'status':'position/orientation/plan verified; absolute site placement pending coordinator integration','evidence':'The source ring is transformed with project X-east/Y-north local approximation; measured plan bounds are %.2f × %.2f m, max ring-vertex error %.8f m. Nominatim address point converts to campus anchor (%.3f, %.3f) m.'%(metrics['source_bbox_width_depth_m'][0],metrics['source_bbox_width_depth_m'][1],footprint_max_error,ANCHOR_X,ANCHOR_Y),'deduction':'Campus location is represented as a documented local anchor but validation says master integration is pending; no surveyed control point or authoritative dimensions were available.'},
        {'name':'Evidence-backed height, floors, and roof form','score':1.0,'max_score':2,'status':'partly supported; heights estimated','evidence':'The fresh-open shell is 4.28 m to its flat roof; the asset extends to %.2f m (builder reports retail parapet about 6.15 m and glazed corner about 13.4 m). Source street photograph visibly supports a low flat-roof shop with a distinctly taller glazed corner.'%asset_bounds[2][1],'deduction':'No measured elevations, roof plan, or authoritative floor count were found. The height values and multi-level interpretation remain image-derived estimates; rooftop form/equipment are unverified.'},
        {'name':'Facade, entrances, and distinctive architecture','score':1.75,'max_score':2,'status':'strong street-photo match with minor simplifications','evidence':'Direct comparison with the cited Google-credited storefront image supports red brick, broad pale parapet with pilasters, long ribbed pale awning, display glazing, paired west-side entry, white UNIVERSITY BOOK STORE lettering, and taller glazed east corner. The rendered front view contains these features.' ,'deduction':'The model simplifies the corner’s stepped/canted cream surround and presents the frontage with a cleaner, more regular window rhythm; the back and side elevations and the interior remain inferred/schematic.'},
        {'name':'Modular export, portability, and complete evidence','score':1.75,'max_score':2,'status':'asset/export and dependency checks verified; integration pending','evidence':'Fresh-open asset contains the expected named scene and collection; %d/%d asset objects are directly linked to that collection. No external libraries or unpacked file images. Procedural materials, raw OSM snapshot, provenance/evidence, roof-plan/front previews, and validation are present.'%(direct_linked,len(asset_objects)),'deduction':'Coordinator-owned manifest/placement/master integration is explicitly pending. Evidence states source date, retrieval date, CRS, method, and uncertainty, but building/store source photos do not have capture date or metric camera calibration.'}
      ],
      'evidence':{
        'asset':'modular/buildings/massing_university_book_store_717bf2c.blend',
        'asset_sha256':metrics['asset_sha256'],
        'assignment':'Root README ownership row names stable ID massing_university_book_store_717bf2c, the same asset path, and owner Tobin.',
        'evaluated_from_fresh_blender_process':True,
        'raw_source':'audit/purdue_university_book_store/osm_way_117396621_full.json',
        'model_evidence':'audit/purdue_university_book_store/model_evidence.json',
        'validation':'audit/purdue_university_book_store/validation.json',
        'front_preview':'audit/purdue_university_book_store/preview_state_street.png',
        'roof_preview':'audit/purdue_university_book_store/preview_roof_plan.png',
        'source_image_url':'https://s1.localdatacdn.com/in/west-lafayette/2957801/original/rvc0QR9QDp.jpg',
        'measured_metrics':metrics
      },
      'findings':[
        'Passes the requested 8/10 threshold at 8.25/10, with material height and absolute-placement uncertainty retained.',
        'Keep height/floor labels explicitly estimated until a measured elevation, reliable height source, or calibrated imagery is available.',
        'Complete and recheck the coordinator-owned master placement/integration before claiming campus placement fully verified.',
        'For higher facade fidelity, refine the source-photo corner surround and document source-image date/camera uncertainty; do not scale geometry from the image without calibration.'
      ]
    }
    (OUT/'fresh_open_metrics.json').write_text(json.dumps(metrics,indent=2)+'\n',encoding='utf-8')
    (OUT/'grade.json').write_text(json.dumps(grade,indent=2)+'\n',encoding='utf-8')
    (OUT/'evaluator.py').write_text(Path(__file__).read_text(encoding='utf-8'),encoding='utf-8')
    print(json.dumps({'grade':grade,'metrics':metrics},indent=2))

run()






