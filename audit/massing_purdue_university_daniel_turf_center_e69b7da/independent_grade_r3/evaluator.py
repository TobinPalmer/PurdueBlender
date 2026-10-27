import bpy, json, math, os
from pathlib import Path

root = Path(__file__).resolve().parents[3]
audit = root / 'audit' / 'massing_purdue_university_daniel_turf_center_e69b7da'
asset = root / 'modular' / 'buildings' / 'massing_purdue_university_daniel_turf_center_e69b7da.blend'
src = audit / 'sources' / 'purdue_buildings_fid208_query_2026-10-26.json'
manifest_path = root / 'modular' / 'manifest.json'
# Force a clean direct reopen in this Blender process.
bpy.ops.wm.open_mainfile(filepath=str(asset))
scene_name='Building_massing_purdue_university_daniel_turf_center_e69b7da'
collection_name='Asset_massing_purdue_university_daniel_turf_center_e69b7da'
scene=bpy.data.scenes.get(scene_name)
collection=bpy.data.collections.get(collection_name)
obj=bpy.data.objects.get('Purdue University Daniel Turf Center')
assert scene and collection and obj and obj.type == 'MESH'
mesh=obj.data
coords=[tuple(float(v) for v in obj.matrix_world @ v.co) for v in mesh.vertices]
bounds=[[min(p[i] for p in coords),max(p[i] for p in coords)] for i in range(3)]
# Direct source query identity and source-ring comparison in project local coordinates.
query=json.loads(src.read_text(encoding='utf-8-sig'))
feature=next(f for f in query['features'] if f['attributes'].get('FID')==208)
attrs=feature['attributes']; ring=feature['geometry']['rings'][0]
lat0,lon0=40.4274,-86.9137
xf=111412.84*math.cos(math.radians(lat0)); yf=111040.0
ringxy=[((lon-lon0)*xf,(lat-lat0)*yf) for lon,lat,*_ in ring]
if ringxy[0]==ringxy[-1]: ringxy.pop()
max_nearest=max(min(math.hypot(x-v[0],y-v[1]) for v in coords) for x,y in ringxy)
# Export and geometry checks are direct from opened file.
edge_use={}
for poly in mesh.polygons:
    for key in poly.edge_keys: edge_use[tuple(sorted(key))]=edge_use.get(tuple(sorted(key)),0)+1
nonmanifold=sum(n!=2 for n in edge_use.values())
material_names=[m.name if m else None for m in mesh.materials]
manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
entry=next(x for x in manifest.get('assets',[]) if x.get('id')=='massing_purdue_university_daniel_turf_center_e69b7da')
mb=entry.get('bounds_world_m')
manifest_delta=max(abs(bounds[i][j]-mb[i][j]) for i in range(3) for j in range(2)) if mb else None

criteria=[
 {"criterion":"Correct identity and source-backed footprint","score":1.9,"max_score":2.0,"status":"Purdue GIS FID 208 identity is corroborated by official HLA address page and attributed exterior photo; source plan ring is directly reproduced but represents roof projection rather than surveyed walls.","evidence":["Direct query attributes: FID 208, DANL, William H. Daniel Turfgrass Research & Diagnostic Court, 1340 Cherry Lane, NUM_LEVELS=1.",f"Model source identity properties agree with FID 208; transformed source ring maximum nearest-vertex error measured from reopened geometry: {max_nearest:.6f} m.","Purdue HLA page independently identifies the Daniel Center/address. The 2011 J&D Turf post explicitly attributes its attached exterior photograph to the Daniel Center building.","Esri aerial overlay supports the polygon's roof-plan correspondence. Wall line and eave overhang are not separately surveyed; GIS/imagery may map roof projection."],"findings":["Keep wall-line and roof-overhang offset explicitly unverified; GIS polygon match alone does not establish structural wall line."]},
 {"criterion":"Position, orientation, and scale/dimensions","score":1.8,"max_score":2.0,"status":"Campus XY placement, long-axis orientation, and plan dimensions agree with identified GIS feature under project's documented approximate transform; exact wall dimensions are unmeasured.","evidence":[f"Clean reopen model world bounds: {bounds} m.","Source ring transformed using the project's published local approximation gives approximately 44.60 m by 17.64 m; the model traces the same footprint and south projection bump.","North-up aerial places the parking apron on the south long elevation and is consistent with the source-ring plan. Coordinate approximation and roof-vs-wall uncertainty remain."],"findings":["The local degrees-to-meters formula is approximate rather than a survey-grade CRS transformation; no surveyed wall dimension was found."]},
 {"criterion":"Evidence-backed height, floors, and roof form","score":1.4,"max_score":2.0,"status":"Single story and shallow gable are supported; absolute vertical scale, pitch and detailed heights remain low-confidence visual estimates.","evidence":["Purdue GIS NUM_LEVELS=1 supports one level. The attributed exterior photo depicts a single-story, elongated structure with a shallow gable roof and ridge parallel to the long axis.",f"Clean reopen bounds show Z {bounds[2][0]:.3f} to {bounds[2][1]:.3f} m. Builder explicitly labels 3.25 m eave and 4.05 m ridge as visual estimates; no calibrated elevations were located.","Raw GIS Extrution=14 has undocumented units and is retained uninterpreted rather than treated as height."],"findings":["Absolute eave/ridge height and roof pitch remain unverified, low-confidence estimates; appearance is not measurement."]},
 {"criterion":"Facade, entrances, and distinctive architecture","score":1.7,"max_score":2.0,"status":"Photo-supported massing-level cladding tone, long horizontal window band and centered canopy are represented; exact fenestration and facade dimensions are not modeled.","evidence":["The 2011 attributed image directly shows light metal wall cladding, a long horizontal upper window band and centered entrance canopy.","Directly reopened object has pale siding, light metal roof and dark horizontal-window-band materials. The preview render visibly includes the long band and centered canopy; roof/facade massing corresponds to the photo.","Facade assignment to south side is a documented inference: the photograph has no compass orientation, and the match relies on parking apron plus centered source-ring bump. Individual doors/windows, siding ribs, and exact facade dimensions are omitted."],"findings":["Facade orientation and small-scale details are not directly georeferenced or dimensioned; current geometry is appropriately limited to massing-level evidence."]},
 {"criterion":"Modular export, portability, and complete evidence","score":1.8,"max_score":2.0,"status":"Expected single-building scene/collection directly reopens; manifold mesh and varied provenance package are present. Shared manifest still needs coordinator reconciliation.","evidence":[f"Blender {bpy.app.version_string} cleanly reopened expected file, scene '{scene.name}', and collection '{collection.name}' containing the expected single mesh object.",f"Reopened mesh: {len(mesh.vertices)} vertices, {len(mesh.edges)} edges, {len(mesh.polygons)} faces; modifiers={len(obj.modifiers)}, nonmanifold edges={nonmanifold}; materials={material_names}; linked libraries={len(bpy.data.libraries)}.","Building-specific package includes source register, raw native and WGS84 GIS snapshots, GIS layer metadata, official Purdue page snapshot, imagery export and overlay, directly attributed 2011 photo, two renders, build record, iteration notes, and clean-reopen validation.",f"Shared manifest bounds are stale by up to {manifest_delta:.3f} m versus reopened asset; manifest is coordinator-owned and requires update."],"findings":["Coordinator should update manifest bounds to the accepted r3 geometry; that shared file is outside grader/building ownership."]}
]
score=sum(c['score'] for c in criteria)
result={"building_id":"massing_purdue_university_daniel_turf_center_e69b7da","building_name":"Purdue University Daniel Turf Center / William H. Daniel Turfgrass Research & Diagnostic Court","reviewer":"Independent r3 grader; directly inspected source snapshots, attributed photo and aerial overlay, and cleanly reopened the .blend in Blender.","score":score,"max_score":10,"passing_standard":8,"passed":score>=8,"criteria":criteria,"evidence":{"asset_path":"modular/buildings/massing_purdue_university_daniel_turf_center_e69b7da.blend","blender":bpy.app.version_string,"scene":scene.name,"collection":collection.name,"object":obj.name,"bounds_world_m":bounds,"source_fid":attrs.get('FID'),"source_name":attrs.get('BUILDING_N'),"source_address":attrs.get('ADDRESS'),"source_levels":attrs.get('NUM_LEVELS'),"max_source_ring_nearest_vertex_error_m":max_nearest,"mesh":{"vertices":len(mesh.vertices),"edges":len(mesh.edges),"faces":len(mesh.polygons),"nonmanifold_edges":nonmanifold,"modifiers":len(obj.modifiers),"materials":material_names,"linked_libraries":len(bpy.data.libraries)},"manifest_bounds_world_m":mb,"max_manifest_bounds_difference_m":manifest_delta,"reviewed_source_artifacts":["audit/massing_purdue_university_daniel_turf_center_e69b7da/sources/purdue_buildings_fid208_query_2026-10-26.json","audit/massing_purdue_university_daniel_turf_center_e69b7da/sources/purdue_buildings_fid208_native3857_2026-10-26.json","audit/massing_purdue_university_daniel_turf_center_e69b7da/sources/purdue_buildings_layer_metadata_2026-10-26.json","audit/massing_purdue_university_daniel_turf_center_e69b7da/sources/purdue_daniel_turf_center_page_2026-10-26.html","audit/massing_purdue_university_daniel_turf_center_e69b7da/sources/daniel_center_exterior_2011_janddturf.jpg","audit/massing_purdue_university_daniel_turf_center_e69b7da/sources/gis_fid208_aerial_overlay.png","audit/massing_purdue_university_daniel_turf_center_e69b7da/renders/daniel_turf_center_top.png","audit/massing_purdue_university_daniel_turf_center_e69b7da/renders/daniel_turf_center_oblique.png"]},"findings":[f for c in criteria for f in c['findings']],"recommendation":"Passes the independent 8/10 gate for this massing asset. Keep height/pitch and wall-line uncertainty prominent. Coordinator must reconcile shared manifest bounds before project indexing; pass does not establish Tobin master integration."}
out=Path(__file__).with_name('independent_grade_r3.json')
out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))

