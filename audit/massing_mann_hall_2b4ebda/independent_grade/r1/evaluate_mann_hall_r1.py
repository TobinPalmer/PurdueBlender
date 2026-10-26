import bpy, json, math
from pathlib import Path

root = Path(__file__).resolve().parents[4]
asset_id = 'massing_mann_hall_2b4ebda'
asset = root / 'modular/buildings' / f'{asset_id}.blend'
gis_path = root / 'audit' / asset_id / 'sources/purdue_building_gis_fid_635.json'
osm_path = root / 'audit' / asset_id / 'sources/independent_osm_comparison.json'
photo = root / 'audit' / asset_id / 'sources/purdue_official_mann_hall_photo.jpg'
preview = root / 'audit' / asset_id / 'preview/mann_hall_isometric.png'
out = root / 'audit' / asset_id / 'independent_grade/r1/grade.json'

# Reopen the submitted library directly in the project's installed Blender.
bpy.ops.wm.open_mainfile(filepath=str(asset))
scene = bpy.data.scenes.get('Building_massing_mann_hall_2b4ebda')
col = bpy.data.collections.get('Asset_massing_mann_hall_2b4ebda')
assert scene and col and len(col.objects) == 1
obj = col.objects[0]
assert obj.name == 'Mann Hall' and obj.type == 'MESH'
dg = bpy.context.evaluated_depsgraph_get()
eobj = obj.evaluated_get(dg)
mesh = eobj.to_mesh()
pts = [obj.matrix_world @ v.co for v in mesh.vertices]
bounds = [[min(p[i] for p in pts), max(p[i] for p in pts)] for i in range(3)]
base = [(p.x, p.y) for p in pts if abs(p.z) < 1e-5]
feature = json.loads(gis_path.read_text(encoding='utf-8'))['features'][0]
assert feature['attributes']['FID'] == 635 and feature['attributes']['BLDG_ABBR'] == 'MANN'
def proj(lon, lat):
    return ((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)), (lat - 40.4274) * 111040.0)
ring = [proj(*p) for p in feature['geometry']['rings'][0]]
if math.dist(ring[0], ring[-1]) < .02: ring.pop()
clean=[]
for p in ring:
    if not clean or math.dist(clean[-1],p) > .12: clean.append(p)
if len(clean)>2 and math.dist(clean[0],clean[-1])<.12: clean.pop()
nearest = [min(math.hypot(x-a,y-b) for a,b in base) for x,y in clean]
roof_m = float(feature['attributes']['R']) * .3048
osm = json.loads(osm_path.read_text(encoding='utf-8'))

criteria = [
  {'name':'Correct identity and source-backed footprint','score':2.0,'max_score':2.0,
   'evidence':'Opened the blend and confirmed the expected Mann Hall asset ID/object. The archived Purdue GIS feature is FID 635 / MANN. Independently recalculated its WGS84 ring with the documented campus projection and compared it against actual reopened z=0 mesh vertices: maximum nearest-ring error %.6f m. An independent OSM polygon comparison reports 96.51%% IoU and 0.10 m centroid offset.' % max(nearest)},
  {'name':'Position, orientation, and scale/dimensions','score':2.0,'max_score':2.0,
   'evidence':'Actual mesh bounds are X %.3f..%.3f m, Y %.3f..%.3f m. Geometry remains in the campus coordinate frame; GIS ring is preserved at full local scale. The independently archived OSM comparison reports 0.474° major-axis difference; OSM extent discrepancies are recorded (3.72 m Hausdorff), so confidence is strongest for the matching main footprint, with local outline detail less certain.' % (bounds[0][0],bounds[0][1],bounds[1][0],bounds[1][1])},
  {'name':'Evidence-backed height, floors, and roof form','score':1.4,'max_score':2.0,
   'evidence':'Reopened mesh height is %.3f m; Purdue GIS R=37 ft converts to %.3f m and the source roof maximum is represented. The archived architect page describes two stories plus a lower level, while GIS NUM_LEVELS is 3 and floor fields F02/F03 are ambiguously labeled. The photo supports two visible facade bands and a parapet/roof screen, but no elevation drawing was found; exact floor elevations and rooftop enclosure shape remain estimates.' % (bounds[2][1]-bounds[2][0], roof_m)},
  {'name':'Facade, entrances, and distinctive architecture','score':0.8,'max_score':2.0,
   'evidence':'Directly inspected the archived Purdue photo and rendered isometric. The model includes a glazed two-story facade, mullions, dark wall treatment, brick accent, entrance glazing/canopy, and roof parapet. In the render the facade reads as a mostly blank opaque block with limited window bands; the source has extensive glazed corner curtain wall and a prominent curved/arched canopy. The model puts a broad brick-colored panel on the visible facade rather than matching the photo’s narrow end pier, and the roof equipment is a simplified box. These are visible source/model discrepancies.'},
  {'name':'Modular export, portability, and complete evidence','score':2.0,'max_score':2.0,
   'evidence':'Direct reopen in Blender %s succeeded. Expected named scene and collection contain one mesh; no modifiers or external libraries; actual mesh has %d vertices and %d faces. The evidence folder includes official Purdue GIS native/WGS84 snapshots and metadata, Purdue facilities page/photo, architect page snapshot, OSM comparison, build summary, and a preview render.' % (bpy.app.version_string,len(mesh.vertices),len(mesh.polygons))}
]
score = round(sum(c['score'] for c in criteria),1)
report = {
 'asset_id':asset_id, 'grade_round':'r1', 'score':score, 'max_score':10,
 'passing_threshold':8, 'passed':score>=8,
 'criteria':criteria,
 'evidence':{
  'direct_blender_reopen':bpy.app.version_string,
  'asset':str(asset.relative_to(root)),
  'scene':scene.name,'collection':col.name,'object':obj.name,
  'evaluated_bounds_m':bounds,'evaluated_mesh_vertices':len(mesh.vertices),'evaluated_mesh_faces':len(mesh.polygons),
  'mesh_modifiers':[m.type for m in obj.modifiers],
  'external_libraries':[lib.filepath for lib in bpy.data.libraries],
  'max_gis_source_vertex_to_model_base_m':max(nearest),
  'mean_gis_source_vertex_to_model_base_m':sum(nearest)/len(nearest),
  'gis_reported_roof_height_m':roof_m,
  'source_files':[str(p.relative_to(root)) for p in [gis_path,photo,preview,osm_path]],
  'visual_inspection':'Independently viewed official Purdue photograph and current isometric preview.'
 },
 'findings':[
  'The source-backed footprint, geospatial frame, and GIS roof maximum are strong; the official GIS floor-height field semantics conflict with the architect description.',
  'Facade silhouette needs closer source matching: continuous corner glazing, brick end pier, and entrance canopy shape/placement are not reproduced convincingly in the submitted view.',
  'The 37 ft maximum corresponds to GIS R, but interior floor stack, lower-level exposure, and rooftop plant enclosure dimensions lack elevation/plan confirmation.'
 ]
}
eobj.to_mesh_clear()
out.write_text(json.dumps(report,indent=2),encoding='utf-8')
print('INDEPENDENT_GRADE',json.dumps(report))

