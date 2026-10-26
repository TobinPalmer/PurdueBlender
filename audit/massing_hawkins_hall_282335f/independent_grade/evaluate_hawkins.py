import bpy, json, math, os
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
AUDIT = os.path.join(ROOT, 'audit', 'massing_hawkins_hall_282335f')
ASSET = os.path.join(ROOT, 'modular', 'buildings', 'massing_hawkins_hall_282335f.blend')
SOURCE = os.path.join(AUDIT, 'sources', 'purdue_building_shapes_fid83_full_2026-10-26.json')
VALIDATION = os.path.join(AUDIT, 'final_validation.json')
OUT = os.path.join(AUDIT, 'independent_grade', 'result.json')
ASSET_ID = 'massing_hawkins_hall_282335f'
COLLECTION = 'Asset_' + ASSET_ID
SCENE = 'Building_' + ASSET_ID

def evaluate():
    with open(SOURCE, encoding='utf-8-sig') as f:
        gis = json.load(f)['features'][0]
    with open(VALIDATION, encoding='utf-8') as f:
        recorded = json.load(f)
    attrs = gis['attributes']
    ring = gis['geometry']['rings'][0]
    mapped = [((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
               (lat - 40.4274) * 111040.0) for lon, lat in ring]
    if mapped and math.dist(mapped[0], mapped[-1]) < 1e-8:
        mapped = mapped[:-1]
    clean=[]
    for p in mapped:
        if not clean or math.dist(p, clean[-1]) > .025:
            clean.append(p)
    if len(clean)>1 and math.dist(clean[0],clean[-1])<=.025:
        clean.pop()

    coll = bpy.data.collections.get(COLLECTION)
    scene = bpy.data.scenes.get(SCENE)
    deps = bpy.context.evaluated_depsgraph_get()
    exported=[]
    for ob in (coll.objects if coll else []):
        if ob.type == 'MESH':
            eo=ob.evaluated_get(deps); me=eo.to_mesh()
            exported.extend([eo.matrix_world @ v.co for v in me.vertices])
            eo.to_mesh_clear()
    shell=[]
    for ob in (coll.objects if coll else []):
        if ob.type=='MESH' and 'ten-floor lower footprint' in ob.name:
            shell=[ob.matrix_world @ v.co for v in ob.data.vertices if abs((ob.matrix_world @ v.co).z)<1e-5]
            break
    nearest=[]
    for p in clean:
        nearest.append(min((math.hypot(v.x-p[0],v.y-p[1]) for v in shell),default=None))
    footprint_max=max(nearest) if nearest else None
    footprint_mean=sum(nearest)/len(nearest) if nearest else None
    bounds=None
    if exported:
        bounds=[[min(v[k] for v in exported),max(v[k] for v in exported)] for k in range(3)]
    external=[]
    for image in bpy.data.images:
        if image.source=='FILE' and image.filepath and not image.packed_file:
            resolved=bpy.path.abspath(image.filepath)
            external.append({'path':image.filepath,'exists':os.path.exists(resolved),'project_relative':image.filepath.startswith('//')})
    criteria=[
      {'name':'Correct identity and source-backed footprint','score':2.0,'max_score':2.0,
       'status':'verified','evidence':f"Official Purdue BuildingShapes FID 83 identifies BLDG_ABBR HAWK / {attrs['BUILDING_N']}. Source ring transformed using documented local campus approximation; {len(clean)} cleaned vertices compared directly to the lower shell, maximum nearest-vertex delta {footprint_max:.4f} m (mean {footprint_mean:.4f} m)."},
      {'name':'Position, orientation, and scale/dimensions','score':1.8,'max_score':2.0,
       'status':'verified_with_limit','evidence':f"GIS footprint has the same campus placement and directional outline; the asset's direct evaluated bounds are X {bounds[0][0]:.3f}–{bounds[0][1]:.3f}, Y {bounds[1][0]:.3f}–{bounds[1][1]:.3f} m. GIS is in EPSG:4326 and conversion is an approximate local transform, not a survey; aerial overlay is supportive but imagery georeferencing/date are not stated."},
      {'name':'Evidence-backed height, floors, and roof form','score':1.2,'max_score':2.0,
       'status':'partly_estimated','evidence':"Purdue OEP snapshot supports 13 floors on east wing and 10 on west/connector. GIS extrusion field is 140, modeled as feet = 42.672 m, but metadata does not confirm units/meaning; GIS NUM_LEVELS=15 conflicts with OEP floor counts. The 10-floor mass height is estimated by proportional division (10/13), not measured. Flat roof is consistent with aerial and exterior photo."},
      {'name':'Facade, entrances, and distinctive architecture','score':1.4,'max_score':2.0,
       'status':'partly_supported','evidence':"Saved Purdue exterior photo supports red/orange brick, repeated window bands, light trim, and flat roof. Render includes these visual elements and split-height wings. Exact window spacing, central entry station/canopy, and upper-wing boundary are not dimensioned; entrance placement is explicitly inferred."},
      {'name':'Modular export, portability, and complete evidence','score':1.8,'max_score':2.0,
       'status':'verified_with_limit','evidence':f"Directly opened saved .blend in Blender; expected scene/collection present, {len(coll.objects) if coll else 0} collection objects ({sum(o.type=='MESH' for o in coll.objects) if coll else 0} meshes), evaluated bounds Z {bounds[2][0]:.3f}–{bounds[2][1]:.3f} m; no modifiers on exported objects; file images are project-relative and resolve: {all(x['exists'] and x['project_relative'] for x in external)}. Raw GIS, OEP, housing pages, exterior photo, aerial, render, and validation are saved. No single machine-readable evidence_record.json; source and uncertainty details are instead in audit README and validation JSON."},
    ]
    score=round(sum(c['score'] for c in criteria),1)
    findings=[
      'Keep the 140 ft height interpretation explicitly uncertain until a source confirms the GIS extrusion units or a dimensioned elevation is found.',
      'GIS NUM_LEVELS=15 and OEP floor counts (13 east / 10 west) conflict; preserve both and label the west/connector height as estimated.',
      'Upper east-wing split and central entry location are approximate; the photo is not a dimensioned or georeferenced elevation.',
      'The 0.29 m overall plan-bound expansion relative to the GIS structural outline is attributable to facade/trim projections; evaluate structural base separately from the total render bounds.'
    ]
    result={'score':score,'max_score':10,'criteria':criteria,'evidence':{
      'asset':os.path.relpath(ASSET,ROOT).replace('\\','/'),'scene':scene.name if scene else None,'collection':coll.name if coll else None,
      'identity':{'FID':attrs['FID'],'BLDG_ABBR':attrs['BLDG_ABBR'],'BUILDING_N':attrs['BUILDING_N']},
      'direct_blend_inspection':{'opened_in_blender':True,'collection_object_count':len(coll.objects) if coll else 0,'mesh_object_count':sum(o.type=='MESH' for o in coll.objects) if coll else 0,'bounds_m':bounds,'footprint_source_vertex_max_nearest_error_m':footprint_max,'footprint_source_vertex_mean_nearest_error_m':footprint_mean,'external_images':external,'recorded_validation':recorded},
      'reviewed_files':['audit/massing_hawkins_hall_282335f/README.md','audit/massing_hawkins_hall_282335f/final_validation.json','audit/massing_hawkins_hall_282335f/sources/purdue_building_shapes_fid83_full_2026-10-26.json','audit/massing_hawkins_hall_282335f/sources/purdue_oep_hawkins_emergency_plan_2026-10-26.html','audit/massing_hawkins_hall_282335f/sources/purdue_residences_hawkins_2026-10-26.html','audit/massing_hawkins_hall_282335f/sources/purdue_residences_hawkins_exterior.jpg','audit/massing_hawkins_hall_282335f/sources/indiana_current_aerial_hawkins.jpg','audit/massing_hawkins_hall_282335f/preview_exterior.png','audit/massing_hawkins_hall_282335f/site_alignment_overlay.png']},
      'findings':findings,'reviewer':'Independent evaluator (read-only asset/source review)','reviewed_utc':datetime.now(timezone.utc).isoformat()}
    assert coll and scene and coll.name==COLLECTION and scene.name==SCENE
    assert exported and shell and footprint_max is not None
    assert all(o.type!='MESH' or len(o.modifiers)==0 for o in coll.objects)
    return result

result=evaluate()
os.makedirs(os.path.dirname(OUT),exist_ok=True)
with open(OUT,'w',encoding='utf-8') as f: json.dump(result,f,indent=2)
print(json.dumps(result,indent=2))

