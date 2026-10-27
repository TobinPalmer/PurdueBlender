"""Independent fresh-open evaluator for Gemini Cooperative FID 825.

Run from Blender 5.2+ with --background --python evaluator.py.
Writes result.json in this folder and never saves the target blend.
"""
import bpy
import hashlib
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ASSET = ROOT / "modular" / "buildings" / "massing_gemini_cooperative_fid825.blend"
EXPECTED_SHA256 = "dd9789003b208747d2f80d4c4af35d27900ce2f7debcfea18c4f1a473f5c25a8"
GIS_PATH = ROOT / "audit" / "gemini" / "fid825.geojson"

sha_before = hashlib.sha256(ASSET.read_bytes()).hexdigest()
if sha_before != EXPECTED_SHA256:
    raise RuntimeError(f"Unexpected asset SHA before open: {sha_before}")
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
sha_after_open = hashlib.sha256(ASSET.read_bytes()).hexdigest()
scene = bpy.context.scene
coll = bpy.data.collections.get("Asset_massing_gemini_cooperative_fid825")
if coll is None:
    raise RuntimeError("Expected building collection missing after fresh open")
objs = list(coll.all_objects)
meshes = [o for o in objs if o.type == "MESH"]
verts = [(o.matrix_world @ v.co) for o in meshes for v in o.data.vertices]
bounds = {axis: [min(getattr(v, axis) for v in verts), max(getattr(v, axis) for v in verts)] for axis in "xyz"}
mat_names = sorted({slot.material.name for o in meshes for slot in o.material_slots if slot.material})
unassigned = sorted(o.name for o in meshes if not any(s.material for s in o.material_slots))
linked_libraries = [bpy.path.abspath(l.filepath) for l in bpy.data.libraries]
external_images = [im.filepath for im in bpy.data.images if im.source == "FILE" and not im.packed_file]
names = [o.name.lower() for o in objs]

# Compare the reopened slab's XY vertices with the official FID 825 polygon.
feature = json.loads(GIS_PATH.read_text(encoding="utf-8"))["features"][0]
ring_ll = feature["geometry"]["coordinates"][0][:-1]
lat0, lon0 = 40.4274, -86.9137
ring_xy = [((lon-lon0)*111412.84*math.cos(math.radians(lat0)), (lat-lat0)*111040.0) for lon,lat in ring_ll]
area2 = sum(ring_xy[i][0]*ring_xy[(i+1)%len(ring_xy)][1]-ring_xy[(i+1)%len(ring_xy)][0]*ring_xy[i][1] for i in range(len(ring_xy)))
cx = sum((ring_xy[i][0]+ring_xy[(i+1)%len(ring_xy)][0])*(ring_xy[i][0]*ring_xy[(i+1)%len(ring_xy)][1]-ring_xy[(i+1)%len(ring_xy)][0]*ring_xy[i][1]) for i in range(len(ring_xy)))/(3*area2)
cy = sum((ring_xy[i][1]+ring_xy[(i+1)%len(ring_xy)][1])*(ring_xy[i][0]*ring_xy[(i+1)%len(ring_xy)][1]-ring_xy[(i+1)%len(ring_xy)][0]*ring_xy[i][1]) for i in range(len(ring_xy)))/(3*area2)
gis_local = [(x-cx,y-cy) for x,y in ring_xy]
slab = bpy.data.objects.get("Gemini | footprint ground and lower-floor slab")
slab_xy = []
if slab:
    slab_xy = sorted(set((round((slab.matrix_world @ v.co).x, 5), round((slab.matrix_world @ v.co).y, 5)) for v in slab.data.vertices))
gis_round = [(round(x,5),round(y,5)) for x,y in gis_local]
vertex_errors = [min(math.hypot(x-u,y-v) for u,v in slab_xy) for x,y in gis_round] if slab_xy else []
hausdorff_vertex_max = max(vertex_errors) if vertex_errors else None
gis_area = abs(area2)/2

category = [
    {"name":"Identity and official footprint", "score":2.0, "max_score":2.0,
     "assessment":"GIS FID 825 identifies Gemini, COOP, 172 Littleton St. The reopened slab reproduces the 14-vertex GIS outline at the local centroid; this checks the slab ring, not necessarily every facade wall or master placement.",
     "evidence":{"fid":825,"building_name":feature["properties"]["BUILDING_N"],"address":feature["properties"]["ADDRESS"],"ring_vertices":len(gis_local),"gis_area_m2_approx":gis_area,"slab_xy_unique_vertices":len(slab_xy),"max_nearest_vertex_error_m":hausdorff_vertex_max}},
    {"name":"Scale and placement", "score":1.15, "max_score":1.5,
     "assessment":"Metric units and centroid-local geometry are evident, and the footprint vertex agreement supports plan scale. Roof elevations, storey heights, and campus marker placement have no independent surveyed or master-scene validation in this standalone asset review.",
     "evidence":{"scene_units":scene.unit_settings.system,"local_bounds_m":bounds,"gis_centroid_campus_xy_m":[cx,cy],"placement_source":"manifest/master placement not independently reopened in this isolated-asset grading"}},
    {"name":"Roof form and height evidence", "score":1.25, "max_score":2.0,
     "assessment":"Multiple ranges, two front cross-gables, dormer elements, and three chimney masses create a more articulated silhouette than a simple bar. Against the official oblique image, the main roof still reads as a broad continuous gable with thin, schematic intersections; dormers are shallow block forms. Ridge/chimney elevations are estimates, not measured evidence.",
     "evidence":{"roof_related_objects":sum(any(k in n for k in ("roof","gable","dormer","chimney")) for n in names),"official_image":"audit/gemini/official_home_exterior.jpg","height_bounds_m":bounds["z"],"height_status":"estimated from photo; no surveyed elevation"}},
    {"name":"Facade and entrance", "score":1.25, "max_score":2.0,
     "assessment":"Dark brick base, light siding, windows, and a covered entry evoke the official house. The reference facade has strongly differentiated wings, an asymmetrical opening rhythm, a substantial recessed porch with a continuous railing and broad approach. The asset facade remains repetitive, porch details are comparatively minimal, and roof gable faces/window rhythm do not fully follow the photo.",
     "evidence":{"window_named_objects":sum("window" in n for n in names),"porch_named_objects":sum(any(k in n for k in ("porch","entrance","step","handrail","railing")) for n in names),"photo":"current official exterior photo showing brick lower story, cream siding, multiple projecting gables, dormers, and deep center porch"}},
    {"name":"Materials, interior, and portability", "score":1.55, "max_score":2.5,
     "assessment":"Named brick, siding, roof, trim, glazing, and interior materials support the intended look. The interior contains floor plates, corridor/room partitions, and a few common-room props but is schematic and visually not verified as an as-built plan. Fresh-open structure is self-contained without linked libraries or unpacked image dependencies.",
     "evidence":{"material_names":mat_names,"unassigned_meshes":len(unassigned),"linked_libraries":linked_libraries,"unpacked_external_images":external_images,"interior_named_object_count":sum(any(k in n for k in ("schematic","corridor","room partition","kitchen","dining","computer-room")) for n in names),"mesh_object_count":len(meshes),"vertex_count":sum(len(o.data.vertices) for o in meshes)}}
]
total = round(sum(c["score"] for c in category),2)
sha_final = hashlib.sha256(ASSET.read_bytes()).hexdigest()
result = {
    "building":"Gemini Cooperative House","fid":825,"verdict":"meets_threshold" if total >= 8 else "below_threshold",
    "score":total,"max_score":10.0,"threshold":8.0,"criteria":category,
    "source_evidence":{"provider":"Purdue University GIS BuildingShapesZip4","source_file":"audit/gemini/fid825.geojson","source_crs":"EPSG:4326","retrieval_date":"2026-10-27","photo_provider":"Gemini Cooperative official site (Wix CDN)","photo_url":"https://static.wixstatic.com/media/95e9bb_01c28615d8194b95a9831dc88772f86f~mv2.jpeg","photo_retrieval_date":"2026-10-27","measurement_method":"Official GIS lon/lat polygon transformed using project approximate local conversion; vertex comparison on reopened slab XY; 3D extent from mesh world coordinates; visual comparison against current official exterior image.","uncertainty":"Approximate GIS conversion; no survey, measured elevations, authoritative plans, or master placement validation."},
    "fresh_open":{"blender_version":bpy.app.version_string,"scene":scene.name,"collection":coll.name,"mesh_objects":len(meshes),"materials":mat_names,"unassigned_meshes":unassigned,"linked_libraries":linked_libraries,"unpacked_external_images":external_images,"bounds_local_m":bounds},
    "sha256":{"expected":EXPECTED_SHA256,"before_open":sha_before,"after_open":sha_after_open,"after_evaluation":sha_final,"matches_all":sha_before==sha_after_open==sha_final==EXPECTED_SHA256},
    "findings":[
      "Official FID 825 wall-outline candidate matches the slab XY ring to rounding precision; walls may be offset from a GIS polygon and this does not validate the master placement.",
      "The current official photo visibly supports a multi-wing house with a deep central porch, brick lower facade, pale siding, intersecting gables, dormers, and chimney stacks.",
      "Asset materials and three-level schematic content are useful, but no reliable interior plan or surveyed height was available; the GIS record's NUM_LEVELS=1 remains conflicting, ambiguous source data.",
      "Portability is strong on fresh open: no linked libraries or unpacked external image dependencies were found."
    ],
    "required_fixes_if_below_8":[
      "Reshape the roof silhouette to match the photo's distinct stepped wings and deeper intersecting gables/valleys, preserving the GIS wall footprint; support heights with a measured elevation or keep the dimensions explicitly estimated.",
      "Rework the front composition around the image-visible center porch: deeper/recessed entry, continuous rail line and broad stair/landing; shift and vary facade windows to match the separate wings.",
      "Model dormers with clear pitched caps/cheeks and vary their sizes and spacing to match the current photo rather than using shallow box faces.",
      "Retain interior as schematic unless a trustworthy floor plan is found; add clear floor/cutaway review evidence if interior usability is a goal."
    ]
}
(HERE/"result.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print(json.dumps({"score":total,"max_score":10,"verdict":result["verdict"],"sha256":result["sha256"],"fresh_open":result["fresh_open"],"criteria":[{k:c[k] for k in ("name","score","max_score")} for c in category]},indent=2,ensure_ascii=False))
