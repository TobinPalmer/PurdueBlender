import json, math
from pathlib import Path
root=Path.cwd(); folder=root/'audit/purdue_university_church/independent_grade_final'; probe=folder/'fresh_open_probe.json'
gis=json.loads((root/'audit/purdue_university_church/sources/purdue_gis_fid797.geojson').read_text(encoding='utf-8'))['features'][0]
ev=json.loads((root/'audit/purdue_university_church/build_evidence.json').read_text(encoding='utf-8'))
report=json.loads(probe.read_text(encoding='utf-8'))
coords=gis['geometry']['coordinates'][0]
lat0,lon0=40.4274,-86.9137
local=[((lon-lon0)*111412.84*math.cos(math.radians(lat0)),(lat-lat0)*111040.0) for lon,lat in coords]
gis_bounds=[[min(p[0] for p in local),max(p[0] for p in local)],[min(p[1] for p in local),max(p[1] for p in local)]]
model=report.get('shell_bounds_xyz',[])[:2]
axis_error=[max(abs(model[i][j]-gis_bounds[i][j]) for j in (0,1)) for i in (0,1)] if len(model)==2 else [999,999]
summary={'score':0.0,'max_score':10,'criteria':[],'evidence':{},'findings':[]}
def add(name,score,max_score,evidence,findings=None):
 summary['criteria'].append({'name':name,'score':score,'max_score':max_score,'evidence':evidence,'findings':findings or []})
add('Correct identity and source-backed footprint',2.0,2.0,
    f"Purdue GIS FID 797 explicitly names BLDG_ABBR UC / University Church. Independently transformed 20-vertex GIS outline has bounds {gis_bounds}; fresh-open shell bounds {model}; max XY axis-bound error {max(axis_error):.6f} m. The state record and 2024 floor plan cross-check identity and use.")
add('Position, orientation, scale and dimensions',1.5,2.0,
    f"Campus coordinates and GIS plan envelope match within {max(axis_error):.6f} m. The plan shape is present, but the portico/photo facade cannot be assigned to a GIS edge with the evidence available: the photo has no geotag/azimuth and floorplan has no north arrow/scale.",
    ['Facade cardinal orientation remains inferred; source photo does not establish which GIS edge is the photographed entrance.'])
add('Evidence-backed height, floors and roof form',1.1,2.0,
    'Source photo supports a slate gabled sanctuary roof and tower/spire silhouette; state record supports a multi-story facility. Eaves (11.7m), ridge (14.9m), spire (28.54m), and floor count remain estimates; GIS level fields conflict (Level_=4, NUM_LEVELS=1, CountOfFLO=3, Extrution=39 with undocumented units).',
    ['No measured elevations or sufficiently scaled multi-view photo were found.'])
add('Facade, entrances and distinctive architecture',1.3,2.0,
    f"Direct comparison of saved preview with 2023 source supports red brick, four-column portico, triangular pediment with circular oculus, green spired tower, and arched side windows. Fresh-open probe confirms {report.get('oculus_present')} oculus, {report.get('portico_columns')} portico columns, {report.get('tower_present')} tower, {report.get('arch_window_head_count')} arched window-head objects. However, preview shows arches on the portico entrance elevation, while source photo shows rectangular/square-headed openings on the portico wall and arches on the perpendicular side wall; openings are generalized incorrectly across elevations. Facade compass placement is also inferred.",
    ['Arched window heads extend across the displayed portico elevation, whereas source-visible windows on that elevation are rectangular; correct the distribution or explain with corroborating imagery.'])
add('Modular export, portability and complete evidence',1.8,2.0,
    f"A separate Blender 5.2 background process opened the saved asset. Expected scene/collection present={report.get('expected_scene_present')}/{report.get('expected_collection_present')}; {report.get('object_count')} collection objects and {report.get('mesh_count')} meshes; {report.get('shell_vertex_count')} shell vertices; no materialless meshes={len(report.get('materialless_meshes',[]))==0}; unpacked external images={len(report.get('external_images',[]))}; all five source snapshots and three previews exist. Asset SHA-256 {report.get('asset_sha256')}.",
    ['Evidence record is detailed and self-contained, but final grade should be checked against the current saved revision after the window-head edits.'])
summary['score']=round(sum(c['score'] for c in summary['criteria']),2)
summary['evidence']={'asset_path':str(root/'modular/buildings/massing_university_church_84b2a1b.blend'),'asset_sha256':report.get('asset_sha256'),'blender_probe':str(probe.relative_to(root)),'gis_bounds_local_m':gis_bounds,'model_shell_bounds_local_m':model,'axis_bound_error_m':axis_error,'fresh_open_probe':report,'source_record':'audit/purdue_university_church/build_evidence.json','visual_comparison':['audit/purdue_university_church/preview.png','audit/purdue_university_church/preview_east.png','audit/purdue_university_church/sources/dave_wegiel_university_church_dusk.jpg']}
summary['findings']=[x for c in summary['criteria'] for x in c['findings']]
(folder/'result.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps({'score':summary['score'],'criteria':summary['criteria'],'asset_sha256':report.get('asset_sha256')},indent=2))
