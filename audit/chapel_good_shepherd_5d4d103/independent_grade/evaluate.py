"""Independent evaluator for Chapel of the Good Shepherd massing asset.
Run with Blender: blender.exe --background --python <this file>
Writes result.json beside this script. Visual judgments are recorded in criterion evidence.
"""
import bpy, json, math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent / "result.json"
ASSET_ID = "massing_chapel_of_the_good_shepherd_5d4d103"
COLLECTION = "Asset_" + ASSET_ID
BLEND = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
SRC = ROOT / "audit" / "chapel_good_shepherd_5d4d103" / "sources"

# Open the candidate file independently, then inspect its actual linked library scene.
bpy.ops.wm.open_mainfile(filepath=str(BLEND))
scene = next((s for s in bpy.data.scenes if s.name == f"Building_{ASSET_ID}"), None)
col = bpy.data.collections.get(COLLECTION)
obj = bpy.data.objects.get("Chapel of the Good Shepherd")
if obj is None or col is None or scene is None:
    raise RuntimeError("Expected massing scene, asset collection, or building object is missing")

def world_bounds(o):
    pts = [o.matrix_world @ __import__('mathutils').Vector(c) for c in o.bound_box]
    return [[min(p[i] for p in pts), max(p[i] for p in pts)] for i in range(3)]

bounds = world_bounds(obj)
external_images = [im.filepath for im in bpy.data.images if im.source == 'FILE' and im.filepath and not im.packed_file]
mesh_data = {
    "object_name": obj.name,
    "type": obj.type,
    "vertices": len(obj.data.vertices),
    "polygons": len(obj.data.polygons),
    "modifiers": [m.name for m in obj.modifiers],
    "world_bounds_m": bounds,
    "location": list(obj.location),
    "rotation_euler": list(obj.rotation_euler),
    "scale": list(obj.scale),
    "asset_collection_object_count": len(col.objects),
    "external_unpacked_images": external_images,
}
# The 12 OSM perimeter nodes map to the same project-local conversion described in source_record.json.
osm = json.loads((SRC / "osm_way_869993661_2026-10-26.json").read_text(encoding="utf-8"))
way = next(e for e in osm['elements'] if e['type'] == 'way' and e['id'] == 869993661)
nodes = {e['id']: e for e in osm['elements'] if e['type'] == 'node'}
lat0, lon0 = 40.4274, -86.9137
lon_m = 111412.84 * math.cos(math.radians(lat0))
xy = [((nodes[n]['lon'] - lon0) * lon_m, (nodes[n]['lat'] - lat0) * 111040.0) for n in way['nodes']]
if xy[0] == xy[-1]: xy.pop()
foot_bounds = [[min(p[i] for p in xy), max(p[i] for p in xy)] for i in range(2)]

criteria = [
  {"name":"Correct identity and source-backed footprint", "score":2.0,"max_score":2,
   "evidence":"OSM way/869993661 is tagged name=Chapel of the Good Shepherd, building=church, denomination=episcopal, address 610 Meridian Street. Nominatim independently resolves that address/name to the same way. The saved mesh has 12 source perimeter vertices; its XY bounds match the OSM conversion envelope (%.3f..%.3f m east, %.3f..%.3f m north). The footprint includes the notched outline rather than a fallback rectangle." % (foot_bounds[0][0],foot_bounds[0][1],foot_bounds[1][0],foot_bounds[1][1]),
   "findings":[]},
  {"name":"Position, orientation, and scale/dimensions", "score":1.25,"max_score":2,
   "evidence":"The object has identity transform and its mapped shell sits in campus coordinates; horizontal dimensions follow the OSM perimeter. The official accessibility page identifies the Meridian Street front entrance and the north-side accessible entrance. In the supplied OSM context, Meridian Street runs immediately south of the building (road latitude about 40.43420; footprint south edge 40.4343356). However, the candidate puts the main door/canopy on its east boundary (x≈40.7 m) and places the front gable at the east end; the principal street-facing entrance is therefore on the wrong side. The north-side secondary door is placed on the north wall as stated, though its exact location is an estimate.",
   "findings":["Move the main entrance and porch to the south/Meridian-facing elevation. Orient the principal gable so that its facade faces south; keep the accessible entrance on the north side."]},
  {"name":"Evidence-backed height, floors, and roof form", "score":1.25,"max_score":2,
   "evidence":"The official exterior photograph and official site elevation drawing both support a prominent two-story central gabled sanctuary, a white bell stage/spire, and much lower attached wings. Numeric wall, eave, ridge, and spire heights are estimates; the photo/drawing provide no scale or measured vertical dimensions. In the saved preview, the sanctuary ridge/gable is oriented toward the east side instead of the south-facing front, and dark triangular roof gaps appear where lower wings join the taller volume. The candidate roof massing does not follow the official elevation's simple low side-wing silhouette cleanly.",
   "findings":["Rebuild the roof junctions as closed, non-overlapping planes that match the official elevation: central two-story gable, low left/west wing, and long low right/east wing. Keep all heights explicitly labeled as estimates."]},
  {"name":"Facade, entrances, and distinctive architecture", "score":0.75,"max_score":2,
   "evidence":"The official, undated exterior photograph shows red brick, pale trim, red central door, tall white steeple with louvered bell stage, central gable vent, repeated tall windows on the long wing, and a circular window. Those broad visual cues appear in the candidate. The official site also includes a front elevation drawing (goodshep_about_image_5.jpg) with the central entrance under the gable, flanking windows, lower west wing, and a long windowed east wing. The candidate puts the door on the east end wall; its front/back composition and window arrangement differ from that elevation. Individual dimensions and exact window/door positions remain estimated.",
   "findings":["Match the south-facing official elevation: put the red door under the central gable, flanking windows on that facade, lower west wing and the long windowed east wing. Update source_record.json to identify and preserve the official elevation drawing as an evidence image."]},
  {"name":"Modular export, portability, and complete evidence", "score":1.75,"max_score":2,
   "evidence":"The saved .blend reopens and contains scene Building_%s, collection %s, and one mesh object with %d vertices/%d polygons. Its object transform is identity and there are no modifiers or external unpacked image dependencies. The source record preserves raw OSM/Nominatim/site snapshots and clearly labels vertical quantities as estimates. A rendered preview is included. The official site elevation drawing is present in the downloaded source snapshots but is absent from source_record.json's cited source list, so evidence indexing is incomplete." % (ASSET_ID,COLLECTION, len(obj.data.vertices),len(obj.data.polygons)),
   "findings":["Add the official site elevation drawing image and its page URL/source date limitations to source_record.json. Re-run Blender reopen validation after geometry changes."]},
]
score = round(sum(c['score'] for c in criteria),2)
result = {
  "score":score,"max_score":10,"criteria":criteria,
  "evidence":{
    "asset_file":"modular/buildings/%s.blend" % ASSET_ID,
    "scene":scene.name,"collection":col.name,"model_inspection":mesh_data,
    "footprint_osm_way":869993661,"footprint_node_count":len(xy),"footprint_bounds_xy_m":foot_bounds,
    "direct_source_inspection":[
      {"path":"audit/chapel_good_shepherd_5d4d103/sources/osm_way_869993661_2026-10-26.json","observation":"way tags explicitly name the chapel and address; version 2 was timestamped 2025-12-10T09:20:29Z; closed 12-node perimeter."},
      {"path":"audit/chapel_good_shepherd_5d4d103/sources/osm_context_2026-10-26.osm","observation":"Meridian Street geometry lies south of the building outline; Ravinia Road is on the north side."},
      {"path":"audit/chapel_good_shepherd_5d4d103/sources/goodshep_about_image_4.jpg","observation":"Official undated photograph confirms brick, centered south/front gable and door, white spire, lower side wings, tall long-wing windows and circular window."},
      {"path":"audit/chapel_good_shepherd_5d4d103/sources/goodshep_about_image_5.jpg","observation":"Official site elevation sketch confirms front door under central gable, low west wing, and long low east wing; it is a valuable unindexed source snapshot."},
      {"path":"audit/chapel_good_shepherd_5d4d103/chapel_good_shepherd_preview.png","observation":"Candidate's main door/gable faces east; dark triangular gaps are visible at lower-wing/sanctuary roof junctions."},
      {"path":"audit/chapel_good_shepherd_5d4d103/reopen_validation.json","observation":"Prior reopen validation reports saved asset reopens, identity coordinate frame and expected collection; this evaluator independently opened the file and inspected the scene/object."}
    ],
    "source_supported_facts":["building identity/name/address and footprint polygon from OSM/Nominatim","Meridian street frontage south and accessible entry on north from official site/context","broad material/color, gable, spire, wing and window composition from official site photo/elevation"],
    "estimates_not_measurements":["wall/eave/ridge/spire heights","roof pitch","window and entrance dimensions/spacing","precise secondary entrance location"]
  },
  "findings":[
    "FAIL: main facade/entrance is placed on the east edge although official sources place the principal entry on the south, Meridian-facing side.",
    "Roof planes have dark triangular openings at the sanctuary/lower-wing junctions and differ from the official elevation silhouette.",
    "The downloaded official elevation sketch is not indexed in the source record.",
    "Score is below 8/10; the revised asset needs a fresh independent review after these changes."
  ]
}
OUT.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"score":score,"result":str(OUT),"bounds":bounds,"footprint_bounds":foot_bounds},indent=2))
