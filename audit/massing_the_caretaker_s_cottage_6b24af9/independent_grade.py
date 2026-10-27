"""Independent source and reopened-Blender evaluator for the Caretaker's Cottage.

Run from the repository root with Blender's background Python. Writes only
independent_grade.json in this building's audit folder.
"""
import bpy
import json
import math
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "audit" / "massing_the_caretaker_s_cottage_6b24af9"
ASSET_ID = "massing_the_caretaker_s_cottage_6b24af9"
ASSET = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
SCENE = f"Building_{ASSET_ID}"
COLLECTION = f"Asset_{ASSET_ID}"


def evaluate():
    sources = json.loads((AUDIT / "source_index.json").read_text(encoding="utf-8"))
    registration = json.loads((AUDIT / "source_registration.json").read_text(encoding="utf-8"))
    evidence = json.loads((AUDIT / "evidence.json").read_text(encoding="utf-8"))
    bpy.ops.wm.open_mainfile(filepath=str(ASSET))
    scene = bpy.data.scenes.get(SCENE)
    coll = bpy.data.collections.get(COLLECTION)
    assert scene is not None and coll is not None
    objs = list(coll.objects)
    meshes = [o for o in objs if o.type == "MESH"]
    shell = bpy.data.objects.get("The Caretaker's Cottage")
    assert shell is not None and shell.type == "MESH"
    depsgraph = bpy.context.evaluated_depsgraph_get()
    shell_eval = shell.evaluated_get(depsgraph)
    shell_xy = set()
    for vertex in shell_eval.to_mesh().vertices:
        world_vertex = shell_eval.matrix_world @ vertex.co
        if abs(world_vertex.z) < 1e-5:
            shell_xy.add((round(world_vertex.x, 5), round(world_vertex.y, 5)))
    shell_eval.to_mesh_clear()
    osm_data = json.loads((AUDIT / "sources" / "osm_full_953041335.json").read_text(encoding="utf-8"))
    nodes = {e["id"]: (e["lon"], e["lat"]) for e in osm_data["elements"] if e["type"] == "node"}
    way = next(e for e in osm_data["elements"] if e["type"] == "way" and e["id"] == 953041335)
    osm_xy = []
    for node_id in way["nodes"]:
        lon, lat = nodes[node_id]
        x = (lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274))
        y = (lat - 40.4274) * 111040.0
        osm_xy.append((round(x, 5), round(y, 5)))
    if osm_xy[0] == osm_xy[-1]:
        osm_xy.pop()
    shell_point_errors = [min(math.dist(point, candidate) for candidate in shell_xy) for point in osm_xy]
    max_shell_error = max(shell_point_errors, default=float("inf"))
    shell_matches = len(osm_xy) == 10 and len(shell_xy) >= 10 and max_shell_error < 0.001
    # Read world-space evaluated bounds directly from Blender's depsgraph.
    corners = []
    for ob in objs:
        ev = ob.evaluated_get(depsgraph)
        if ev.type != "MESH":
            continue
        corners.extend([ev.matrix_world @ __import__("mathutils").Vector(c) for c in ev.bound_box])
    actual_bounds = [[min(v[i] for v in corners) for i in range(3)], [max(v[i] for v in corners) for i in range(3)]]
    materialless = [o.name for o in meshes if len(o.data.materials) == 0]
    external_images = [im.filepath for im in bpy.data.images if im.source == "FILE" and not im.packed_file]
    presentation = bpy.data.collections.get("Presentation_Only")
    presentation_disjoint = presentation is not None and not set(presentation.objects) & set(objs)
    transforms_identity = all(
        all(abs(v - target) < 1e-6 for v, target in zip(ob.location, (0, 0, 0)))
        and all(abs(v - target) < 1e-6 for v, target in zip(ob.rotation_euler, (0, 0, 0)))
        and all(abs(v - target) < 1e-6 for v, target in zip(ob.scale, (1, 1, 1)))
        for ob in objs
    )
    source_rows = sources["sources"]
    dates_complete = all(row.get("retrieved_utc_date") or sources.get("retrieved_utc_date") for row in source_rows)
    urls_complete = all(bool(row.get("url")) for row in source_rows)
    uncertainties_complete = all(bool(row.get("uncertainty")) for row in source_rows)
    roof_objs = [o for o in meshes if "Roof" in o.name or "Canopy" in o.name]
    criterion_details = [
        {
            "criterion": "Correct identity and source-backed footprint",
            "points": 1.9,
            "max_points": 2,
            "evidence": [
                "West Lafayette Public Library and City of West Lafayette sources independently identify the 1903 Caretaker's Cottage at 1496 N Salisbury Street.",
                f"OSM way 953041335 is explicitly named for the cottage; its 10 unique points independently match the reopened shell base vertices: {shell_matches}.",
                f"Indiana LiDAR footprint 433415 provides an independent roof-envelope check (IoU {registration['comparison']['intersection_over_union']:.3f}), while OSM is used as the wall/base outline.",
            ],
            "deduction": "0.1: community-mapped OSM outline is not a surveyed foundation, and the larger LiDAR polygon has a disclosed interpretation rather than a definitive structural boundary.",
        },
        {
            "criterion": "Position, orientation, and scale/dimensions",
            "points": 1.9 if shell_matches and transforms_identity else 1.2,
            "max_points": 2,
            "evidence": [
                f"Reopened structural shell ring matches all ten transformed OSM points: {shell_matches}.",
                f"World-space asset bounds directly measured from reopened exported meshes: {actual_bounds} meters.",
                "The massing remains in the project campus coordinate convention; individual object transforms are identity and no detailed-asset placement marker is expected.",
            ],
            "deduction": "0.1: local longitude/latitude approximation and OSM are not survey-grade controls; roof-overhang bounds are not a wall-dimension measurement.",
        },
        {
            "criterion": "Evidence-backed height, floors, and roof form",
            "points": 1.1,
            "max_points": 2,
            "evidence": [
                "Official historic photograph and current orthophoto support a terracotta multi-plane roof silhouette; roof components exist in the reopened asset.",
                "Official historic photo shows a low, articulated roof over a one-story cottage, but no scale or elevation is supplied.",
                "Builder explicitly labels 3.35 m wall height, 3.48 m eaves, 5.55 m ridge, roof pitch and roof intersection as qualitative estimates; no height-derived survey evidence is present.",
                "Top render shows broad roof planes and exposed gray areas/gaps; the generated roof footprint does not cleanly reproduce the stepped LiDAR/orthophoto roof outline.",
            ],
            "deduction": "0.9: height and ridge are unmeasured, and despite qualitative photo support, modeled roof outline/intersection is approximate and visibly incomplete in plan.",
        },
        {
            "criterion": "Facade, entrances, and distinctive architecture",
            "points": 1.0,
            "max_points": 2,
            "evidence": [
                "Official sources support Bedford limestone, terracotta tile, and double porches; the asset includes textured stone, a tile material, front porch, and short return porch.",
                "Historic photo directly shows rough rubble-stone walls and a broad porch/veranda under deep eaves.",
                "The street oblique render has a generic smooth/noisy stone surface, modeled windows and an entrance whose count, positions and dimensions are explicitly estimated; front and return porches are schematic.",
                "Renders show a detached-looking ramp/rail element and porch-to-wall gaps; no facade elevation or dimensioned plan verifies these placements.",
            ],
            "deduction": "1.0: distinctive materials and porch concept are supported, but modeled facade layout/porch treatment only loosely follows the photo and the openings/access elements are unverified estimates.",
        },
        {
            "criterion": "Modular export, portability, and complete evidence",
            "points": 1.9 if len(objs) > 0 and len(meshes) == len(objs) and presentation_disjoint and not external_images and not materialless and dates_complete and urls_complete and uncertainties_complete else 1.0,
            "max_points": 2,
            "evidence": [
                f"Reopened scene and named asset collection are present; exported collection has {len(objs)} mesh objects.",
                f"All exported meshes have materials: {not materialless}; no unpacked external images: {not external_images}; presentation collection is outside export: {presentation_disjoint}.",
                f"Source index has provider/URL, feature/source identifiers, retrieval/source date or date caveat, CRS where relevant, measurement method and uncertainty: urls={urls_complete}, dates={dates_complete}, uncertainty={uncertainties_complete}.",
                "Four named renders and raw OSM, Indiana LiDAR, orthophoto, official-library and City snapshots are present in the building-specific audit folder.",
            ],
            "deduction": "0.1: geometry is a simple massing approximation and the saved presentation relies on studio lighting; complete placement within the campus master remains a coordinator integration check.",
        },
    ]
    score = round(sum(c["points"] for c in criterion_details), 1)
    result = {
        "building_id": ASSET_ID,
        "grader": "independent subagent",
        "evaluator": "independent_grade.py::evaluate",
        "asset": "modular/buildings/" + ASSET.name,
        "score": score,
        "max_score": 10,
        "pass_threshold": 8,
        "passed": score >= 8,
        "criteria": criterion_details,
        "evidence": {
            "reopened_asset": str(ASSET.relative_to(ROOT)),
            "actual_blender_version": bpy.app.version_string,
            "source_evidence": "audit/massing_the_caretaker_s_cottage_6b24af9/source_index.json, source_registration.json, and preserved source snapshots",
            "actual_renders_reviewed": [f"audit/massing_the_caretaker_s_cottage_6b24af9/renders/{n}.png" for n in ("top", "street_oblique", "north_oblique", "side_oblique")],
            "reopened_geometry": {"object_count": len(objs), "mesh_count": len(meshes), "shell_ring_matches_osm": shell_matches, "max_shell_ring_error_m": max_shell_error, "world_bounds_m": actual_bounds, "roof_components": [o.name for o in roof_objs], "identity_object_transforms": transforms_identity},
            "source_comparison": {"osm_way": 953041335, "indiana_lidar_objectid": 433415, "liDAR_osm_iou": registration["comparison"]["intersection_over_union"], "liDAR_osm_centroid_separation_m": registration["comparison"]["centroid_separation_m"]},
        },
        "findings": [
            "Required before passing: rebuild the roof geometry to follow the stepped L-shaped roof envelope visible in the orthophoto and the Indiana LiDAR outline; remove visible exposed-gray gaps and overlapping roof artifacts, then regenerate all four views.",
            "Improve stone wall/porch treatment against the official 2017 photo: represent the broad continuous low veranda/parapet and heavy limestone piers more faithfully; review the detached ramp and rails against the actual front access side.",
            "Keep wall, eave and ridge heights explicitly estimated unless a measured elevation source is found; do not present current values as verified.",
        ],
    }
    return result


if __name__ == "__main__":
    result = evaluate()
    (AUDIT / "independent_grade.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
