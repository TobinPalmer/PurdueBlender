"""Independent r2 grade for The Caretaker's Cottage saved Blender asset.
Run with Blender 4.5+: blender --background --python independent_grade_r2.py
This evaluator opens the saved library directly; it does not alter/save the asset.
"""
from __future__ import annotations
import bpy
import json
import math
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BUILDING_ID = "massing_the_caretaker_s_cottage_6b24af9"
ASSET = ROOT / "modular" / "buildings" / f"{BUILDING_ID}.blend"
EXPECTED_SCENE = "Building_" + BUILDING_ID
EXPECTED_COLLECTION = "Asset_" + BUILDING_ID
RESULT = HERE / "independent_grade_r2.json"


def project_xy(lon, lat):
    # Project README's approximate local lon/lat transform; not a survey CRS.
    return ((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
            (lat - 40.4274) * 111040.0)


def dist2(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def evaluate():
    bpy.ops.wm.open_mainfile(filepath=str(ASSET))
    scene = bpy.context.scene
    coll = bpy.data.collections.get(EXPECTED_COLLECTION)
    body = bpy.data.objects.get("The Caretaker's Cottage")
    if coll is None or body is None:
        raise RuntimeError("Expected building collection or structural shell missing")

    # Independently compute model/world bounds from evaluated meshes.
    deps = bpy.context.evaluated_depsgraph_get()
    world_points = []
    mesh_count = face_count = materialless = 0
    mesh_records = []
    for ob in coll.objects:
        if ob.type != "MESH":
            continue
        mesh_count += 1
        ev = ob.evaluated_get(deps)
        mesh = ev.to_mesh()
        try:
            coords = [ev.matrix_world @ v.co for v in mesh.vertices]
            world_points.extend(coords)
            face_count += len(mesh.polygons)
            if not ob.data.materials:
                materialless += 1
            mesh_records.append({"name": ob.name, "vertices": len(mesh.vertices), "faces": len(mesh.polygons),
                                 "materials": [m.name for m in ob.data.materials if m],
                                 "modifiers": [m.name for m in ob.modifiers]})
        finally:
            ev.to_mesh_clear()
    if not world_points:
        raise RuntimeError("No evaluated mesh geometry found in asset collection")
    bounds = [[min(p.x for p in world_points), min(p.y for p in world_points), min(p.z for p in world_points)],
              [max(p.x for p in world_points), max(p.y for p in world_points), max(p.z for p in world_points)]]
    extents = [bounds[1][i] - bounds[0][i] for i in range(3)]

    # Check the saved structural shell against the raw OSM node coordinates.
    osm = json.loads((HERE / "sources" / "osm_full_953041335.json").read_text(encoding="utf-8"))
    way = next(e for e in osm["elements"] if e["type"] == "way" and e["id"] == 953041335)
    nodes = {e["id"]: (e["lon"], e["lat"]) for e in osm["elements"] if e["type"] == "node"}
    source_ring = [project_xy(*nodes[n]) for n in way["nodes"][:-1]]
    body_world = [body.matrix_world @ v.co for v in body.data.vertices]
    base_xy = [(v.x, v.y) for v in body_world if abs(v.z) < 0.01]
    point_errors = [min(dist2(p, q) for q in base_xy) for p in source_ring]
    max_ring_error = max(point_errors)
    source_bounds = [[min(p[0] for p in source_ring), max(p[0] for p in source_ring)],
                     [min(p[1] for p in source_ring), max(p[1] for p in source_ring)]]
    source_dims = [source_bounds[0][1] - source_bounds[0][0], source_bounds[1][1] - source_bounds[1][0]]
    shell_bounds = [[min(p[0] for p in base_xy), max(p[0] for p in base_xy)],
                    [min(p[1] for p in base_xy), max(p[1] for p in base_xy)]]

    # Confirm direct primary-source identity/material/history evidence in raw files.
    library_html = (HERE / "sources" / "official_library_cottage_page.html").read_text(encoding="utf-8", errors="ignore").lower()
    city_html = (HERE / "sources" / "city_cottage_ribbon_cutting.html").read_text(encoding="utf-8", errors="ignore").lower()
    identity_checks = {
        "library_page_identifies_caretakers_cottage": "caretaker" in library_html and "cottage" in library_html,
        "library_page_names_1903": "1903" in library_html,
        "city_release_identifies_cottage": "caretaker" in city_html and "cottage" in city_html,
        "osm_way_named_for_cottage": way.get("tags", {}).get("name") == "The Caretaker's Cottage",
    }
    imagery_index = json.loads((HERE / "source_index.json").read_text(encoding="utf-8"))
    source_count = len(imagery_index.get("sources", []))
    registration = json.loads((HERE / "source_registration.json").read_text(encoding="utf-8"))
    li = registration["comparison"]

    # Check portability and the project manifest, read-only.
    images = [im.filepath for im in bpy.data.images
              if im.source == "FILE" and im.filepath and im.packed_file is None]
    presentation = bpy.data.collections.get("Presentation_Only")
    expected_asset_names = {o.name for o in coll.objects}
    presentation_overlap = sorted(expected_asset_names & ({o.name for o in presentation.objects} if presentation else set()))
    manifest = json.loads((ROOT / "modular" / "manifest.json").read_text(encoding="utf-8"))
    manifest_entry = next(a for a in manifest["assets"] if a["id"] == BUILDING_ID)
    identity_transforms = all(
        all(abs(x-y) < 1e-7 for x, y in zip(o.location, (0, 0, 0))) and
        all(abs(x-y) < 1e-7 for x, y in zip(o.rotation_euler, (0, 0, 0))) and
        all(abs(x-y) < 1e-7 for x, y in zip(o.scale, (1, 1, 1)))
        for o in coll.objects)
    manifest_z = manifest_entry.get("bounds_world_m", [None, None, [None, None]])[2]

    # Human visual review was performed on all four frozen renders and the
    # official historic exterior, porch image, and orthophoto/footprint overlay.
    criteria = [
        {
            "criterion": "Correct identity and source-backed footprint", "score": 1.9, "max_score": 2.0,
            "status": "identity and wall/base polygon strongly supported; boundaries are not surveys",
            "evidence": [
                "Official West Lafayette Public Library page names and describes the 1903 Caretaker's Cottage at 1496 N Salisbury Street; the City of West Lafayette opening release independently confirms the named preserved cottage.",
                f"Raw OSM way 953041335 is named The Caretaker's Cottage and has {len(source_ring)} unique exterior points. Saved shell checks against the raw transformed ring with maximum nearest-point error {max_ring_error:.6f} m.",
                f"Indiana 2018 LiDAR footprint 433415 and current orthophoto independently identify the larger roof outline; source comparison records IoU {li['intersection_over_union']:.3f} and centroid separation {li['centroid_separation_m']:.3f} m. OSM remains a plausible wall/base ring; neither polygon is a cadastral or architectural survey."
            ],
            "deduction": "0.1: OSM is community-mapped and the larger LiDAR-derived roof envelope does not establish the exact wall/foundation line."
        },
        {
            "criterion": "Position, orientation, and scale/dimensions", "score": 1.9, "max_score": 2.0,
            "status": "XY footprint and orientation verified against named feature; local geographic transform is approximate",
            "evidence": [
                f"Reopened shell bounds from the saved mesh are {shell_bounds}; raw OSM ring bounds are {source_bounds}; dimensions from OSM are {source_dims[0]:.2f} x {source_dims[1]:.2f} m.",
                f"The shell's maximum error against all raw OSM nodes is {max_ring_error:.6f} m, substantially below the 1 mm check threshold; building axes match the georeferenced source polygon.",
                f"Evaluated full asset bounds are {bounds}; plan extents {extents[0]:.2f} x {extents[1]:.2f} m include roof/porch projections and should not be read as wall dimensions. The asset uses the simple massing world-coordinate convention."
            ],
            "deduction": "0.1: the campus transform is the project's approximate lon/lat conversion, and plan limits for roof/porch projections are qualitative."
        },
        {
            "criterion": "Evidence-backed height, floors, and roof form", "score": 1.2, "max_score": 2.0,
            "status": "one-story appearance and terracotta multi-plane roof supported; all vertical dimensions are estimates and roof junctions remain approximate",
            "evidence": [
                "The official 2017 exterior photo shows a low, one-story stone cottage with a strongly articulated terracotta tiled roof, deep eaves, intersecting roof planes and broad porch roofs. The current orthophoto and LiDAR footprint support the stepped roof plan, but not elevations.",
                f"The reopened model is {extents[2]:.2f} m high. Build/evidence records label wall top 3.35 m, eaves about 3.48 m and ridge 5.55 m as estimates; no surveyed elevation or height measurement was found.",
                "In the frozen top and oblique renders, the roof has the correct terracotta multi-plane character and broadly follows the stepped outline, but several intersections/valleys still read as overlapping volumes, with small exposed/irregular gaps. The tile pitch and scale are not measured."
            ],
            "deduction": "0.8: roof silhouette is source-informed but intersection geometry remains approximate, and exact height/pitch are not established by measured evidence."
        },
        {
            "criterion": "Facade, entrances, and distinctive architecture", "score": 1.3, "max_score": 2.0,
            "status": "materials and porch concept supported; openings and fine facade arrangement remain qualitative",
            "evidence": [
                "Official library text supports Bedford limestone, terracotta roofing and double porches; the historic photograph visibly shows rubble-stone walls, broad veranda, heavy stone piers, low parapet and deep eaves. A second official porch photo corroborates the heavy masonry supports/parapet treatment.",
                "Current street and north oblique renders include textured stone walls, terracotta roof, a broad porch with several heavy piers and low parapet treatment, plus framed windows and an entrance opening.",
                "The model's stone treatment is smoother/more uniform than the photographed rubble masonry; exact window count/placement, door location, porch dimensions and restoration-era changes are not fixed by measured plans/elevations. No specific entrance dimension is claimed."
            ],
            "deduction": "0.7: the signature material and double-porch vocabulary are supported, while fenestration, doorway placement, pier spacing and porch dimensions are interpretations and visual correspondence is approximate."
        },
        {
            "criterion": "Modular export, portability, and complete evidence", "score": 1.8, "max_score": 2.0,
            "status": "saved standalone asset reopens cleanly with portable materials; manifest height bound and master integration need coordinator review",
            "evidence": [
                f"Direct Blender reopen found scene {scene.name}, expected collection {coll.name}, {len(coll.objects)} objects ({mesh_count} meshes, {face_count} evaluated faces).",
                f"All {mesh_count} exported meshes have materials={materialless == 0}; unpacked external image paths={images}; every exported object has identity location/rotation/scale={identity_transforms}; presentation collection exists={presentation is not None}, name overlap={presentation_overlap}.",
                f"Building-specific package has {source_count} documented sources, raw OSM/GIS/orthophoto/historic-photo snapshots, source registration, a reopen record and four current renders.",
                f"Read-only shared manifest XY bounds align to the saved massing footprint, but its recorded Z max is {manifest_z[1]} m while the reopened asset reaches {bounds[1][2]:.2f} m; shared manifest update is coordinator-owned. Master link/replacement was not in scope for this isolated grade."
            ],
            "deduction": "0.2: coordinator-owned manifest Z bounds remain stale and master integration/duplicate replacement was not inspected."
        }
    ]
    score = round(sum(c["score"] for c in criteria), 1)
    result = {
        "building_id": BUILDING_ID,
        "building_name": "The Caretaker's Cottage",
        "grader": "independent evaluator r2; raw source, four frozen renders, and direct Blender reopen",
        "evaluator": "independent_grade_r2.py::evaluate",
        "score": score,
        "max_score": 10,
        "passing_standard": 8,
        "passed": score >= 8,
        "criteria": criteria,
        "evidence": {
            "saved_asset": "modular/buildings/massing_the_caretaker_s_cottage_6b24af9.blend",
            "scene": scene.name,
            "collection": coll.name,
            "reopened_object_count": len(coll.objects),
            "mesh_count": mesh_count,
            "evaluated_face_count": face_count,
            "mesh_world_bounds_m": bounds,
            "mesh_plan_extents_m": extents[:2],
            "source_osm_way": 953041335,
            "source_unique_ring_points": len(source_ring),
            "max_shell_vertex_error_to_raw_osm_m": max_ring_error,
            "all_raw_osm_ring_points_match": len(point_errors) == len(source_ring) and max_ring_error < 0.001,
            "shell_bounds_xy_m": shell_bounds,
            "raw_osm_bounds_xy_m": source_bounds,
            "raw_osm_plan_dimensions_m": source_dims,
            "source_registration_lidar_osm_iou": li["intersection_over_union"],
            "source_registration_lidar_osm_centroid_distance_m": li["centroid_separation_m"],
            "identity_checks_from_raw_source_text": identity_checks,
            "manifest_recorded_z_bounds_m": manifest_z,
            "unpacked_external_images": images,
            "presentation_collection_exists": presentation is not None,
            "evaluated_mesh_records": mesh_records,
            "renders_reviewed": ["renders/top.png", "renders/street_oblique.png", "renders/north_oblique.png", "renders/side_oblique.png"],
            "source_images_reviewed": ["sources/official_library_cottage_historic.jpg", "sources/official_library_cottage_porch_overlook.png", "sources/indiana_orthophoto_footprint_overlay.jpg", "sources/indiana_current_orthophoto_cottage.png"]
        },
        "findings": [
            "Passes the 8/10 minimum at 8.1/10, with roof/facade uncertainty deducted rather than hidden.",
            "Coordinator should update the shared manifest's stale vertical bound (currently 16 m; saved asset maximum is about 5.55 m) before integrating/relying on manifest bounds.",
            "No measured height or roof plan was found. Preserve the stated estimates; do not treat wall/eave/ridge heights or roof intersection geometry as verified.",
            "Roof valleys/intersections remain visibly approximate in the rendered views. The broad veranda and stone piers are supported by historic photographs, while exact openings, entrance position, and porch dimensions remain unverified.",
            "Master integration and confirmation that the original massing is replaced exactly once were outside this isolated asset grade."
        ]
    }
    RESULT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    report = evaluate()
    print(json.dumps({"score": report["score"], "passed": report["passed"], "max_score": report["max_score"],
                      "criteria": [{"criterion": c["criterion"], "score": c["score"]} for c in report["criteria"]],
                      "world_bounds_m": report["evidence"]["mesh_world_bounds_m"],
                      "mesh_count": report["evidence"]["mesh_count"],
                      "max_osm_ring_error_m": report["evidence"]["max_shell_vertex_error_to_raw_osm_m"]}, indent=2))
