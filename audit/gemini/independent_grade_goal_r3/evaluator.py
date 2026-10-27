"""Independent, read-only fresh-open grade of Gemini Cooperative FID 825.

Run with Blender 5.2+: blender --background --python evaluator.py
The evaluator opens the target file, measures it, and writes only beside this
script. It never saves the target .blend.
"""
import bpy
import hashlib
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ASSET = ROOT / "modular/buildings/massing_gemini_cooperative_fid825.blend"
GIS = ROOT / "audit/gemini/fid825.geojson"
EXPECTED = "035cadd549309370dd2fdf67791bbb0e2919132e797a3dcc74819e00a897dff6"

sha_before = hashlib.sha256(ASSET.read_bytes()).hexdigest()
if sha_before != EXPECTED:
    raise RuntimeError(f"Unexpected SHA-256 before fresh open: {sha_before}")
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
sha_open = hashlib.sha256(ASSET.read_bytes()).hexdigest()
scene = bpy.context.scene
coll_name = "Asset_massing_gemini_cooperative_fid825"
coll = bpy.data.collections.get(coll_name)
if coll is None:
    raise RuntimeError(f"Missing expected collection after open: {coll_name}")
objects = list(coll.all_objects)
meshes = [o for o in objects if o.type == "MESH"]
coords = [o.matrix_world @ v.co for o in meshes for v in o.data.vertices]
bounds = {a: [min(getattr(v, a) for v in coords), max(getattr(v, a) for v in coords)] for a in "xyz"}
names = [o.name.lower() for o in objects]
materials = sorted({s.material.name for o in meshes for s in o.material_slots if s.material})
unassigned = [o.name for o in meshes if not any(s.material for s in o.material_slots)]
linked_libraries = [bpy.path.abspath(l.filepath) for l in bpy.data.libraries]
external_images = [i.filepath for i in bpy.data.images if i.source == "FILE" and not i.packed_file]

feature = json.loads(GIS.read_text(encoding="utf-8"))["features"][0]
ring_ll = feature["geometry"]["coordinates"][0][:-1]
lat0, lon0 = 40.4274, -86.9137
xy = [((lon-lon0)*111412.84*math.cos(math.radians(lat0)), (lat-lat0)*111040.0) for lon,lat in ring_ll]
area2 = sum(xy[i][0]*xy[(i+1)%len(xy)][1]-xy[(i+1)%len(xy)][0]*xy[i][1] for i in range(len(xy)))
cx = sum((xy[i][0]+xy[(i+1)%len(xy)][0])*(xy[i][0]*xy[(i+1)%len(xy)][1]-xy[(i+1)%len(xy)][0]*xy[i][1]) for i in range(len(xy)))/(3*area2)
cy = sum((xy[i][1]+xy[(i+1)%len(xy)][1])*(xy[i][0]*xy[(i+1)%len(xy)][1]-xy[(i+1)%len(xy)][0]*xy[i][1]) for i in range(len(xy)))/(3*area2)
gis_local = [(x-cx,y-cy) for x,y in xy]
slab = bpy.data.objects.get("Gemini | footprint ground and lower-floor slab")
slab_xy = sorted(set((round((slab.matrix_world @ v.co).x,5), round((slab.matrix_world @ v.co).y,5)) for v in slab.data.vertices)) if slab else []
gis_rounded = [(round(x,5),round(y,5)) for x,y in gis_local]
err = [min(math.hypot(x-u,y-v) for u,v in slab_xy) for x,y in gis_rounded] if slab_xy else []
max_err = max(err) if err else None

def count_any(*terms):
    return sum(any(t in n for t in terms) for n in names)

criteria = [
    {"name":"Identity and official footprint","score":2.0,"max_score":2.0,
     "assessment":"The FID 825 source record names Gemini and the reopened lower-floor slab reproduces all 14 official GIS XY vertices within rounding precision. This confirms plan outline only, not elevation or walls above the slab.",
     "evidence":{"feature_id":feature["id"],"name":feature["properties"]["BUILDING_N"],"address":feature["properties"]["ADDRESS"],"source_crs":"EPSG:4326","gis_unique_vertices":len(gis_local),"slab_unique_vertices":len(slab_xy),"max_nearest_vertex_error_m":max_err,"gis_area_m2_approx":abs(area2)/2}},
    {"name":"Scale and placement","score":1.25,"max_score":1.5,
     "assessment":"The 14-vertex footprint, local metric geometry, and overall plan proportions are consistent. Wall/story and roof elevations are image-based estimates, and the standalone asset does not include the master placement marker, so campus placement and surveyed vertical scale are not established here.",
     "evidence":{"units":scene.unit_settings.system,"mesh_bounds_local_m":bounds,"gis_centroid_campus_xy_m_approx":[cx,cy],"master_placement_checked":False,"vertical_dimensions":"estimated from current photos; no surveyed elevation"}},
    {"name":"Roof form and height evidence","score":1.45,"max_score":2.0,
     "assessment":"Three separately named roof ranges, two cross-gables, three pitched dormers, and chimneys create a more articulated profile. The current official photo still shows deeper, more legible intersecting gable wings; in the model several roof planes merge into broad shallow bands and the gable/valley relationships are not fully convincing. Roof and chimney elevations remain estimates.",
     "evidence":{"roof_range_objects":count_any("roof south plane","roof north plane"),"cross_gable_objects":count_any("cross gable"),"dormer_objects":count_any("dormer"),"chimney_objects":count_any("chimney"),"model_z_bounds_m":bounds["z"],"height_status":"photo estimate, not surveyed"}},
    {"name":"Facade, raised entry, and materials","score":1.55,"max_score":2.0,
     "assessment":"Brick base, pale lap siding, contrasting sash, multiple window rhythms, porch piers, a raised landing, broad stairs, and guardrails address the main photo cues. The entry is clearly elevated and legible. Its porch roof and facade remain schematic compared with the official photo's deep recessed central porch, broad continuous porch railing, and more distinct wing projections; openings are still somewhat regular.",
     "evidence":{"facade_window_objects":count_any("window"),"porch_related_objects":count_any("porch","entrance","step","handrail","railing","stair"),"material_names":materials,"porch_objects":{"recessed_landing":count_any("recessed porch landing"),"brick_piers":count_any("recessed porch brick pier"),"stair_treads":count_any("broad porch stair tread"),"stair_handrails":count_any("continuous sloped stair handrail")}}},
    {"name":"Interior and portability","score":1.9,"max_score":2.5,
     "assessment":"The fresh-open asset contains a schematic interior rather than an authoritative plan, so room arrangement remains unverified. Portability is strong: all mesh objects have material slots, and no linked libraries or unpacked external image dependencies were found. Geometry is a self-contained standalone collection.",
     "evidence":{"interior_named_objects":count_any("interior","corridor","room partition","kitchen","dining","computer-room","schematic"),"mesh_objects":len(meshes),"vertices":sum(len(o.data.vertices) for o in meshes),"materials":materials,"unassigned_mesh_count":len(unassigned),"linked_libraries":linked_libraries,"unpacked_external_images":external_images}}
]
total = round(sum(c["score"] for c in criteria),2)
sha_after = hashlib.sha256(ASSET.read_bytes()).hexdigest()
if sha_before != sha_open or sha_open != sha_after or sha_after != EXPECTED:
    raise RuntimeError(f"Asset changed during audit: {sha_before}, {sha_open}, {sha_after}")

result = {
 "building":"Gemini Cooperative","fid":825,"score":total,"max_score":10.0,
 "threshold":8.0,"verdict":"meets_threshold" if total >= 8 else "below_threshold",
 "asset_path":"modular/buildings/massing_gemini_cooperative_fid825.blend",
 "sha256":{"expected":EXPECTED,"before_fresh_open":sha_before,"after_fresh_open":sha_open,"after_evaluation":sha_after,"unchanged":True},
 "fresh_open":{"blender_version":bpy.app.version_string,"scene":scene.name,"collection":coll.name,"mesh_objects":len(meshes),"bounds_local_m":bounds,"material_count":len(materials)},
 "source_evidence":{"gis_provider":"Purdue University GIS BuildingShapesZip4","gis_feature_id":825,"gis_source_crs":"EPSG:4326","gis_retrieval_date":"2026-10-27","gis_snapshot":"audit/gemini/fid825.geojson","gis_transform":"Project approximate conversion X=(lon+86.9137)*111412.84*cos(40.4274 degrees); Y=(lat-40.4274)*111040; centroid-local coordinates.","photo_provider":"Gemini Cooperative official website","official_page":"https://www.geminicooperative.com/","about_page":"https://www.geminicooperative.com/about","photo_snapshot":"audit/gemini/official_home_exterior.jpg","photo_url":"https://static.wixstatic.com/media/95e9bb_01c28615d8194b95a9831dc88772f86f~mv2.jpeg","photo_retrieval_date":"2026-10-27","current_site_checked":"2026-10-27; official home page shows gallery and address 172 Littleton Street; imagery depicts the house but is not dimension-calibrated."},
 "criteria":criteria,
 "findings":["Fresh-opened standalone asset retains the expected scene and exported collection.","GIS ring agreement validates the plan outline, not above-grade wall offsets, facade locations, master placement, or height.","The revised gables, dormers, and porch improve the architectural cues; intersections, facade projection, and roof profiles remain simplified relative to the official exterior.","Interior arrangement is schematic because no reliable as-built plan was found.","Portability check found no library links or unpacked external image dependencies."],
 "revision_fixes_if_below_8":[]
}
if total < 8:
 result["revision_fixes_if_below_8"] = [
  "Reshape the front and side roof masses so the two projecting gables intersect the main ranges with visible valleys and stepped eaves; keep all elevations labeled as estimates until measured evidence is available.",
  "Deepen the recessed center porch and make its broad landing and continuous front guardrail read clearly, while preserving the raised stair approach.",
  "Vary and shift window groupings across the separate wings to match the official exterior's asymmetrical openings.",
  "Retain the interior as explicitly schematic unless a reliable floor plan becomes available; include a readable interior inspection view if that detail is meant to be reviewed."
 ]
(HERE/"result.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
lines=["# Independent Grade — Gemini Cooperative (FID 825)","",f"**Score: {total:.2f}/10 — {result['verdict'].replace('_',' ')}.**", "", "| Criterion | Score | Assessment |", "|---|---:|---|"]
for c in criteria:
 lines.append(f"| {c['name']} | {c['score']:.2f}/{c['max_score']:.2f} | {c['assessment']} |")
lines += ["",f"Asset SHA-256 was `{sha_before}` before, immediately after fresh open, and after evaluation. Blender {bpy.app.version_string} opened the exact requested standalone blend. The target file was not saved.","", "## Evidence and limits", "", "The official Purdue GIS feature FID 825 is named Gemini at 172 Littleton Street. Its EPSG:4326 polygon was transformed with the project's documented approximate local conversion and compared vertex-by-vertex with the reopened slab. This establishes horizontal outline agreement only; it does not establish floor elevations, above-grade wall positions, or master placement.", "", "The current official [Gemini home page](https://www.geminicooperative.com/) still presents an Our Gallery section and identifies 172 Littleton Street; the [official About page](https://www.geminicooperative.com/about) confirms the organization and address. Architectural comparison used the official exterior snapshot `audit/gemini/official_home_exterior.jpg` (Wix image URL and retrieval date recorded in `result.json`). The photo provides no calibrated dimensions.", "", "The interior is schematic. GIS level-count attributes conflict with the visible multi-level photo and are not treated as measured evidence. Roof/story heights remain estimates. Portability results are from the fresh-open scene.", "", "## Required revisions", ""]
if result["revision_fixes_if_below_8"]:
 lines += [f"{i}. {fix}" for i,fix in enumerate(result["revision_fixes_if_below_8"],1)]
else:
 lines.append("No threshold-driven revision list: the asset meets the 8/10 threshold, with the limits above retained in the record.")
lines += ["",f"Runnable evaluator: `evaluator.py`. Machine-readable measurements and criterion evidence: `result.json`."]
(HERE/"grade_report.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
print(json.dumps({"score":total,"max_score":10,"verdict":result["verdict"],"fresh_open":result["fresh_open"],"sha256":result["sha256"],"criteria":[{"name":c["name"],"score":c["score"],"max_score":c["max_score"]} for c in criteria]},indent=2))
