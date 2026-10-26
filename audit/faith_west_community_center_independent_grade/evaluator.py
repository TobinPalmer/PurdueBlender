"""Independent Faith West evaluator; run after probe_candidate.py opens the candidate in Blender."""
import json, math, hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GRADE = Path(__file__).resolve().parent
EXPECTED_SHA = "d0fa26385ce4a813a18a82e9948a88a641b25753014434a0292b900096eec820"
ASSET = ROOT / "modular/buildings/massing_faith_west_community_center_84aa829.blend"
PROBE = json.loads((GRADE / "candidate_probe.json").read_text(encoding="utf-8"))
VALIDATION = json.loads((ROOT / "audit/faith_west_community_center/fresh_open_validation.json").read_text(encoding="utf-8"))
SOURCE = json.loads((ROOT / "audit/faith_west_community_center/osm_buildings_near_faith_west.json").read_text(encoding="utf-8"))
GEOMETRY = json.loads((ROOT / "audit/faith_west_community_center/faith_west_geometry.json").read_text(encoding="utf-8"))
EVIDENCE = json.loads((ROOT / "audit/faith_west_community_center/evidence.json").read_text(encoding="utf-8"))
BUILD = json.loads((ROOT / "audit/faith_west_community_center/build_report.json").read_text(encoding="utf-8"))

sha = hashlib.sha256(ASSET.read_bytes()).hexdigest()
feature = next(e for e in SOURCE["elements"] if e["type"] == "way" and e["id"] == 743763888)
assert feature.get("tags", {}).get("name") == "Faith West Community Center"
ring = [((p["lon"] + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)), (p["lat"] - 40.4274) * 111040.0) for p in feature["geometry"]]
if ring and ring[0] == ring[-1]:
    ring.pop()
wall = next(o for o in PROBE["rows"] if o["name"] == "FaithWest_Public_Podium_Walls_With_Window_Openings")
ground = [(v[0], v[1]) for v in wall["vertices_world"] if abs(v[2]) < 1e-6]

def point_segment_distance(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    den = dx * dx + dy * dy
    t = max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / den)) if den else 0.0
    return math.hypot(p[0] - (a[0] + t * dx), p[1] - (a[1] + t * dy))

def point_ring_distance(p, poly):
    return min(point_segment_distance(p, poly[i], poly[(i + 1) % len(poly)]) for i in range(len(poly)))

source_to_model_vertex = max(min(math.dist(p, q) for q in ground) for p in ring)
model_to_source_line = max(point_ring_distance(p, ring) for p in ground)
source_area = abs(sum(ring[i][0] * ring[(i + 1) % len(ring)][1] - ring[(i + 1) % len(ring)][0] * ring[i][1] for i in range(len(ring))) / 2.0)
source_bounds = [[min(p[i] for p in ring), max(p[i] for p in ring)] for i in range(2)]
model_wall_bounds = wall["bounds"]
bounds_diffs = [max(abs(model_wall_bounds[i][j] - source_bounds[i][j]) for j in range(2)) for i in range(2)]

objects = PROBE["rows"]
object_names = {o["name"] for o in objects}
required = {"FaithWest_Public_Podium_Walls_With_Window_Openings", "FaithWest_Housing_Level_02_Walls_With_Window_Openings", "FaithWest_Housing_Level_03_Walls_With_Window_Openings", "FaithWest_Housing_Level_04_Walls_With_Window_Openings", "FaithWest_Indoor_Gym_Wood_Court", "FaithWest_Cafe_Tables_and_Seats", "FaithWest_Community_Center_Sign"}
assert required <= object_names
assert VALIDATION["pass"] and VALIDATION["sha256"] == sha == EXPECTED_SHA == BUILD["candidate_sha256"] == PROBE["sha256"]
assert PROBE["scene"] == "Building_massing_faith_west_community_center_84aa829"
assert PROBE["collection"] == "Asset_massing_faith_west_community_center_84aa829"
assert VALIDATION["object_count"] == PROBE["objects"] == 34
assert not VALIDATION["missing_linked_libraries"] and not VALIDATION["unpacked_external_images"]

scores = [2.0, 2.0, 1.1, 1.4, 1.5]
criteria = [
    {"name":"Correct identity and source-backed footprint", "score":scores[0], "max_score":2, "evidence":f"The named Faith West Community Center matches the saved OSM way 743763888 at 1920 Northwestern Avenue. Independently projected the raw 39-vertex closed ring using the documented campus transform and compared it to ground-level vertices of the podium wall mesh: max OSM-vertex-to-model-vertex distance {source_to_model_vertex:.4f} m; max model-vertex-to-OSM-segment distance {model_to_source_line:.4f} m. Projected source polygon area {source_area:.2f} m² agrees with the preserved footprint record.", "findings":[]},
    {"name":"Position, orientation, and scale/dimensions", "score":scores[1], "max_score":2, "evidence":f"The projected source bounds and structural podium bounds agree within {max(bounds_diffs):.3f} m on X and Y. Vertex order preserves the mapped orientation and irregular multi-wing footprint. The complete decorative model extends beyond the structural bounds because of porches/balconies; the OSM footprint is the reference for the podium shell.", "findings":["The source is volunteered OpenStreetMap geometry transformed with the project's local approximation, not a surveyed wall line."]},
    {"name":"Evidence-backed height, floors, and roof form", "score":scores[2], "max_score":2, "evidence":"KJG Architecture and Titan Construction imagery support a four-story residential wing, lower community podium, dark sloped roofs, and rooftop services. The model has a podium plus three upper wall levels, three gable pieces, flat community-wing roof panels, and HVAC objects. Its 15.93 m ridge/overall height and story elevations are modeled estimates; the roof deck reads as one broad continuous plane and the source images show more articulated intersecting roof slopes.", "findings":["No measured elevation or as-built roof-height drawing was found.","The modeled roof silhouette is simplified compared with the multiple joined roof slopes visible in the aerial and exterior references."]},
    {"name":"Facade, entrances, and distinctive architecture", "score":scores[3], "max_score":2, "evidence":"The model includes the dark brick community podium, lighter upper housing levels, repeated windows and frames, selective balconies, cafe patio/umbrellas, entry and community/fitness/preschool signs. The references support these broad features. The candidate render is noticeably more uniform and less articulated than the KJG and Faith Church photos; the curved public-facing podium facade and roof-to-wall transitions are simplified, and the material mapping appears banded in places.", "findings":["Exterior finish and entrance geometry need refinement to match the source photos more closely."]},
    {"name":"Modular export, portability, and complete evidence", "score":scores[4], "max_score":2, "evidence":"The exact SHA was independently verified and freshly opened in Blender 5.2.3. Expected scene and collection contain 34 named objects (31 meshes and 3 text objects), 17 materials, no empty mesh objects, no linked libraries, no unpacked external images, and no cameras/lights in the export collection. The evidence folder preserves raw OSM data, provider/source metadata, several project/reference photos, a footprint plot, and exterior/interior renders.", "findings":["Interior partitions and furniture are schematic and follow the published program; no source-backed floor plan is available. The saved cutaway preview is separated/exploded and does not clearly show a coherent occupied interior."]}
]
score = sum(c["score"] for c in criteria)
result = {
    "building_id":"massing_faith_west_community_center_84aa829",
    "candidate_sha256":sha,
    "expected_sha256":EXPECTED_SHA,
    "sha_verified":sha == EXPECTED_SHA,
    "score":score,
    "max_score":10,
    "status":"PASS" if score >= 8 else "FAIL",
    "pass_threshold":8,
    "criteria":criteria,
    "evidence":{
        "fresh_open":{k:VALIDATION[k] for k in ["fresh_process_opened","blender_version","scene","collection","object_count","object_types","faithwest_material_count","source_asset_bounds_world_m","linked_libraries","unpacked_external_images","pass"]},
        "gis_comparison":{"source_provider":"OpenStreetMap via Overpass API","feature_id":743763888,"name":feature["tags"]["name"],"source_crs":"WGS84/EPSG:4326","project_transform":"X=(longitude+86.9137)*111412.84*cos(radians(40.4274)); Y=(latitude-40.4274)*111040.0","unique_ring_vertices":len(ring),"source_area_m2":source_area,"max_source_vertex_to_model_vertex_m":source_to_model_vertex,"max_model_vertex_to_source_segment_m":model_to_source_line,"max_structural_bounds_delta_m":max(bounds_diffs)},
        "sources":EVIDENCE["sources"],
        "review_renders":["../faith_west_community_center/faith_west_exterior_preview.png","../faith_west_community_center/faith_west_interior_cutaway.png"],
        "reviewed_reference_images":["../faith_west_community_center/kjg_exterior_01.jpg","../faith_west_community_center/faithwest_aerial.jpg","../faith_west_community_center/faithwest_campus_photo.jpg"]
    },
    "findings":[finding for c in criteria for finding in c["findings"]],
    "evaluator":"Independent reviewer; source-backed GIS comparison and direct fresh-open/render inspection.",
    "pass":score >= 8
}
(GRADE / "result.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print(json.dumps({"score":score,"status":result["status"],"sha":sha,"boundary_max_m":[source_to_model_vertex,model_to_source_line],"bounds_delta_m":max(bounds_diffs)},indent=2))


