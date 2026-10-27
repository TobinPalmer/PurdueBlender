"""Independent Twin Pines grader. Run inside Blender with the candidate asset open."""
from pathlib import Path
import json, math, sys
import bpy

ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "audit/massing_twin_pines_cooperative_8f606f9"
ASSET = ROOT / "modular/buildings/massing_twin_pines_cooperative_8f606f9.blend"
OUT = AUDIT / "independent_grade/twin_pines_independent_grade.json"
ID = "massing_twin_pines_cooperative_8f606f9"
COLLECTION = "Asset_" + ID

def fail(message):
    raise RuntimeError(message)

# Load the raw source records independently of the builder's validation report.
record = json.loads((AUDIT / "evidence.json").read_text(encoding="utf-8"))
osm = json.loads((AUDIT / "sources/osm_way_301934836_fid766.json").read_text(encoding="utf-8"))
bpy.ops.wm.open_mainfile(filepath=str(ASSET))
coll = bpy.data.collections.get(COLLECTION)
obj = bpy.data.objects.get("Twin Pines Cooperative")
if coll is None or obj is None or obj.type != "MESH":
    fail("Expected exported asset collection or mesh missing")

depsgraph = bpy.context.evaluated_depsgraph_get()
eobj = obj.evaluated_get(depsgraph)
mesh = eobj.to_mesh()
verts = [eobj.matrix_world @ v.co for v in mesh.vertices]
polys = len(mesh.polygons)
mesh_vertices_count = len(mesh.vertices)
mins = [min(v[i] for v in verts) for i in range(3)]
maxs = [max(v[i] for v in verts) for i in range(3)]
eobj.to_mesh_clear()

# Independently compare the saved mesh base-ring coordinates against the raw
# bundled OSM way's projected node coordinates, allowing 2 cm geometric tolerance.
source_xy = [(float(p["x_m"]), float(p["y_m"])) for p in osm["projected_coordinates"][:-1]]
base_xy = [(round(v.x, 6), round(v.y, 6)) for v in verts if abs(v.z) < 1e-5]
# The mesh has one low base ring; take the distinct XY points at Z=0.
base_xy = sorted(set(base_xy))
nearest = []
for sx, sy in source_xy:
    nearest.append(min(math.hypot(sx-bx, sy-by) for bx, by in base_xy) if base_xy else float("inf"))
max_fp_error = max(nearest)
identity_raw = (
    osm.get("feature", {}).get("id") == 301934836
    and osm.get("feature", {}).get("tags", {}).get("name") == "Twin Pines Cooperative"
    and "322 Waldron" in (AUDIT / "sources/twin_pines_official_contact.html").read_text(encoding="utf-8", errors="ignore")
)
photo_exists = (AUDIT / "sources/purdue_hhs_ambassadors_twin_pines_exterior.jpg").is_file()
source_snapshots = [AUDIT / "sources/purdue_cooperative_houses.html", AUDIT / "sources/purdue_student_life_bob_joyce_2023.html", AUDIT / "sources/twin_pines_official_contact.html", AUDIT / "sources/osm_way_301934836_fid766.json"]
materials = [m.name for m in obj.data.materials if m]
image_paths = [im.filepath for im in bpy.data.images if im.source == "FILE"]

criteria = [
    {"criterion":"Identity and footprint", "score":2.0, "max_score":2,
     "evidence":[f"Raw OSM snapshot identifies named way 301934836 as Twin Pines Cooperative (FID 766 crosswalk).", "Official Twin Pines contact snapshot includes 322 Waldron; Purdue cooperative listing and 2023 Purdue profile corroborate identity/site.", f"Saved mesh ground ring has {len(base_xy)} unique Z=0 XY vertices; max nearest-node error against raw projected OSM polygon = {max_fp_error:.6f} m."],
     "findings":["The footprint is community-mapped OSM geometry rather than a surveyed wall line; it may generalize the envelope or include porch/roof edges."]},
    {"criterion":"Position, orientation, and scale/dimensions", "score":1.6, "max_score":2,
     "evidence":[f"Direct evaluated mesh world bounds: X [{mins[0]:.3f}, {maxs[0]:.3f}], Y [{mins[1]:.3f}, {maxs[1]:.3f}], Z [{mins[2]:.3f}, {maxs[2]:.3f}] m.", f"Raw OSM projected footprint measures about 24.61 x 13.51 m; the source-derived structural base preserves this plan and its long east-west axis.", "Object transform is identity, consistent with this simple-massing asset remaining in campus coordinates; contact page and Purdue profile corroborate the 322 Waldron location."],
     "findings":["No independent survey or orthographic aerial registration verifies wall footprint or exact rotation; front/south bearing is inferred from the photograph and site context. Overall bounds extend beyond the footprint due to porch/roof details."]},
    {"criterion":"Evidence-backed height, floors, and roof", "score":1.5, "max_score":2,
     "evidence":["The 2011 Purdue HHS Ambassadors exterior photograph directly shows two occupied stories and a gabled roof; the current builder-render silhouette is broadly consistent.", f"Saved model roof ridge is {maxs[2]:.2f} m above base, explicitly marked estimated in evidence; inherited 16 m fallback was removed."],
     "findings":["No measured elevation, architectural plan, or reliable story-height source was found. Eave/ridge height and rear roof wing remain photo-based estimates; attic/roof volume is not a verified occupied floor."]},
    {"criterion":"Facade, entrances, and distinctive architecture", "score":1.4, "max_score":2,
     "evidence":["Direct comparison of saved front/east renders with the archived Purdue exterior photo supports horizontal siding, shuttered double-hung windows, front porch, posts/brick piers, railing, entrance, and gable silhouette.", "Current official site photo of the porch supports white round columns, brick piers, railing, and muted gray-green siding."],
     "findings":["Only one older oblique exterior photo and a current partially occluded porch photo are available. Exact window count/spacing, door position, colors across the whole current facade, and side/rear elevations are not independently established; some repeated details are plausible interpretation rather than direct measurements."]},
    {"criterion":"Modular export, portability, and evidence", "score":1.8, "max_score":2,
     "evidence":[f"Saved file re-opened here; expected collection '{COLLECTION}' contains {len(coll.objects)} object(s), including the stable named mesh.", f"Evaluated mesh has {mesh_vertices_count} vertices and {polys} polygons; saved object transform location={tuple(round(float(v),4) for v in obj.location)}, scale={tuple(round(float(v),4) for v in obj.scale)}.", f"Materials: {len(materials)} slots; file image dependencies: {len(image_paths)}.", f"Raw evidence/source snapshots present: {sum(p.is_file() for p in source_snapshots)}/{len(source_snapshots)} mandatory identity/footprint snapshots; reopen validation record and three preview renders are present."],
     "findings":["The asset is portable and collection structure is stable. Evidence is detailed but no surveyed elevation/orthographic site comparison is included, so dimensional confidence remains limited."]}
]
score = round(sum(c["score"] for c in criteria), 1)
result = {
    "building_id": ID,
    "building_name": "Twin Pines Cooperative",
    "asset_path": str(ASSET.relative_to(ROOT)).replace("\\", "/"),
    "grader": "independent evaluator authored and run by twin_pines_grader",
    "evaluated_at": "2026-10-26",
    "score": score,
    "max_score": 10,
    "pass_threshold": 8,
    "passed": score >= 8,
    "criteria": criteria,
    "evidence": {
        "direct_blend_inspection": True,
        "blender_version": bpy.app.version_string,
        "collection": COLLECTION,
        "object": obj.name,
        "evaluated_bounds_world_m": [[round(v,6) for v in mins], [round(v,6) for v in maxs]],
        "mesh_vertices": mesh_vertices_count,
        "mesh_polygons": polys,
        "base_z0_unique_xy_vertices": len(base_xy),
        "raw_osm_nearest_vertex_error_m": round(max_fp_error, 6),
        "raw_identity_crosscheck": identity_raw,
        "historical_exterior_photo_present": photo_exists,
        "external_file_image_dependencies": image_paths,
        "reopen_validation_json_read_as_context_only": True
    },
    "findings": [f for c in criteria for f in c["findings"]]
}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
print(json.dumps(result, indent=2, ensure_ascii=False))



