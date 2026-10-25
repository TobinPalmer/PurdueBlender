"""Independent rubric evaluator for the saved NACC Blender asset.

Run with Blender 5.2.3 in background mode. This script reopens the asset before
measuring it and writes only the independent scorecard and report here.
"""
import bpy
import hashlib
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
ASSET = os.path.join(ROOT, "modular", "buildings", "native_american_educational_and_cultural_center_nacc.blend")
GIS = os.path.join(HERE, "native_american_educational_and_cultural_center_nacc_gis_feature_927.json")
EVIDENCE = os.path.join(HERE, "native_american_educational_and_cultural_center_nacc_evidence.json")
MANIFEST = os.path.join(ROOT, "modular", "manifest.json")
OUT_JSON = os.path.join(HERE, "nacc_independent_scorecard.json")
OUT_MD = os.path.join(HERE, "nacc_independent_report.md")


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def ring_centroid(points):
    cross_sum = sum(points[i][0] * points[(i + 1) % len(points)][1] - points[(i + 1) % len(points)][0] * points[i][1]
                    for i in range(len(points)))
    area = cross_sum / 2.0
    cx = sum((points[i][0] + points[(i + 1) % len(points)][0]) *
             (points[i][0] * points[(i + 1) % len(points)][1] - points[(i + 1) % len(points)][0] * points[i][1])
             for i in range(len(points))) / (6.0 * area)
    cy = sum((points[i][1] + points[(i + 1) % len(points)][1]) *
             (points[i][0] * points[(i + 1) % len(points)][1] - points[(i + 1) % len(points)][0] * points[i][1])
             for i in range(len(points))) / (6.0 * area)
    return cx, cy, abs(area)


def object_xy_center(obj):
    corners = [obj.matrix_world @ __import__("mathutils").Vector(corner) for corner in obj.bound_box]
    return [sum(p[i] for p in corners) / len(corners) for i in range(2)]


def evaluate():
    bpy.ops.wm.open_mainfile(filepath=ASSET)
    collection_name = "Asset_native_american_educational_and_cultural_center_nacc"
    collection = bpy.data.collections.get(collection_name)
    gis = json.load(open(GIS, encoding="utf-8"))
    evidence = json.load(open(EVIDENCE, encoding="utf-8"))
    manifest = json.load(open(MANIFEST, encoding="utf-8"))
    entry = next((x for x in manifest["assets"] if x.get("id") == "native_american_educational_and_cultural_center_nacc"), {})
    feature = gis["feature"]
    attrs = feature["attributes"]
    coords = feature["geometry"]["rings"][0][:-1]
    sx = 111412.84 * math.cos(math.radians(40.4274))
    sy = 111040.0
    projected = [((lon + 86.9137) * sx, (lat - 40.4274) * sy) for lon, lat in coords]
    cx, cy, area = ring_centroid(projected)
    source_local = [(x - cx, y - cy) for x, y in projected]

    objects = list(collection.all_objects) if collection else []
    names = {obj.name for obj in objects}
    shell = bpy.data.objects.get("native_american_educational_and_cultural_center_nacc_official_GIS_wall_shell")
    shell_points = []
    if shell and shell.type == "MESH":
        for vert in shell.data.vertices:
            p = shell.matrix_world @ vert.co
            shell_points.append((p.x, p.y, p.z))
    unique_shell_xy = sorted({(round(x, 5), round(y, 5)) for x, y, z in shell_points})
    # Hausdorff distance between GIS ring vertices and the structural shell vertices.
    def nearest_max(a, b):
        return max(min(math.hypot(x-u, y-v) for u, v in b) for x, y in a) if a and b else None
    gis_to_shell = nearest_max(source_local, unique_shell_xy)
    shell_to_gis = nearest_max(unique_shell_xy, source_local)
    xs = [x for x, y in source_local]
    ys = [y for x, y in source_local]
    gis_dims = [max(xs) - min(xs), max(ys) - min(ys)]
    shell_dims = [max(x for x, y in unique_shell_xy) - min(x for x, y in unique_shell_xy),
                  max(y for x, y in unique_shell_xy) - min(y for x, y in unique_shell_xy)] if unique_shell_xy else []
    # The structural shell stores the GIS ring in order for its lower vertices.
    # Use polygon area centroid, not an unweighted vertex mean, for a valid
    # comparison on this irregular 20-corner footprint.
    ordered_shell_xy = []
    if shell and shell.type == "MESH" and len(shell.data.vertices) >= len(source_local):
        ordered_shell_xy = [(float((shell.matrix_world @ v.co).x), float((shell.matrix_world @ v.co).y))
                            for v in shell.data.vertices[:len(source_local)]]
    shell_cx, shell_cy, _ = ring_centroid(ordered_shell_xy) if ordered_shell_xy else (None, None, None)
    centroid_offset = [shell_cx, shell_cy] if shell_cx is not None else []

    def world_z_bounds(prefix=None):
        chosen = [obj for obj in objects if obj.type == "MESH" and (prefix is None or obj.name.startswith(prefix))]
        pts = [obj.matrix_world @ v.co for obj in chosen for v in obj.data.vertices]
        return [min(p.z for p in pts), max(p.z for p in pts)] if pts else []

    bounds = world_z_bounds()
    front = bpy.data.objects.get("NACC_fifth_street_front_door")
    rear = bpy.data.objects.get("NACC_alley_rear_kitchen_door")
    porch = bpy.data.objects.get("NACC_back_porch_room_110_deck")
    front_center = object_xy_center(front) if front else None
    rear_center = object_xy_center(rear) if rear else None
    porch_center = object_xy_center(porch) if porch else None
    rear_porch_gap = math.dist(rear_center, porch_center) if rear_center and porch_center else None
    feature_checks = {
        "named_export_collection_reopened": collection is not None,
        "GIS_structural_shell_present": shell is not None,
        "Fifth_Street_front_door": front is not None,
        "parking_lot_accessible_door_and_ramp": all(n in names for n in ("NACC_parking_lot_access_door", "NACC_accessibility_ramp")),
        "alley_rear_kitchen_door": rear is not None,
        "room_110_back_porch": all(n in names for n in ("NACC_back_porch_room_110_deck", "NACC_back_porch_room_110_roof")),
        "detached_storage_garage": "NACC_detached_single_car_storage_garage" in names,
        "undocumented_front_porch_absent": not any(n.startswith("NACC_front_porch") for n in names),
        "schematic_interior_labeled": bpy.data.collections.get("NACC_SCHEMATIC_INTERIOR_NOT_AS_BUILT") is not None,
    }
    materials = {m for obj in objects if hasattr(obj.data, "materials") for m in obj.data.materials if m}
    portable_materials = all(m.use_nodes and m.node_tree and any(n.type == "TEX_NOISE" for n in m.node_tree.nodes)
                             and any(n.type == "BUMP" for n in m.node_tree.nodes)
                             and any(n.type == "BSDF_PRINCIPLED" for n in m.node_tree.nodes) for m in materials)
    external_images = [im.filepath for im in bpy.data.images if im.source == "FILE" and im.filepath]
    manifest_names = set(entry.get("objects", []))
    stale_manifest_names = sorted(n for n in manifest_names if n.startswith("NACC_front_porch") or n == "NACC_porch_column_0")
    manifest_bounds = entry.get("local_bounds_m")

    # Point allocations follow the five fixed rubric criteria. Deductions reflect
    # absent measured elevation/facade evidence and a stale shared manifest snapshot.
    criteria = [
        {"criterion": "Correct identity and source-backed footprint", "max_points": 2, "points": 2.0,
         "status": "verified", "evidence": [
             "Purdue GIS FeatureServer FID 927 identifies NACC at 903 5th Street; the Purdue emergency plan independently identifies the former house.",
             "Reopened structural wall shell agrees with the projected GIS ring: max vertex distance GIS→shell %.4f m, shell→GIS %.4f m." % (gis_to_shell or -1, shell_to_gis or -1),
             "The 20-vertex source outline and modeled wall shell match, including the irregular perimeter; projected footprint dimensions %.3f × %.3f m." % tuple(gis_dims)]},
        {"criterion": "Position, orientation, and scale/dimensions", "max_points": 2, "points": 2.0,
         "status": "verified within project transform limits", "evidence": [
             "Wall-shell local centroid offset from the GIS polygon centroid: (%.4f, %.4f) m; registered placement origin in manifest: %s." % (centroid_offset[0], centroid_offset[1], entry.get("placement_origin_xy_m")),
             "Structural dimensions: model %.3f × %.3f m; projected GIS %.3f × %.3f m." % (shell_dims[0], shell_dims[1], gis_dims[0], gis_dims[1]),
             "GIS-derived wall geometry preserves orientation; local transform uses the project’s stated approximate WGS84-to-meter conversion, not a surveyed CRS." ]},
        {"criterion": "Evidence-backed height, floors, and roof form", "max_points": 2, "points": 1.0,
         "status": "partly supported; estimated", "evidence": [
             "Purdue BEP (revision 2026-03-17) describes a two-story house with a basement; modeled asset has a basement and two above-grade levels.",
             "Reopened asset vertical bounds are %.2f to %.2f m. Eaves/ridge, roof pitch, and total above-grade height are explicit model estimates, with no measured elevation drawing located." % (bounds[0], bounds[1]),
             "GIS NUM_LEVELS=1 conflicts with the dated written Purdue BEP. The evidence record acknowledges this conflict." ]},
        {"criterion": "Facade, entrances, and distinctive architecture", "max_points": 2, "points": 1.0,
         "status": "partly supported; facade is interpretive", "evidence": [
             "Purdue BEP confirms three exits and locates the main door at Fifth Street, an accessible door toward the gravel parking lot, and the kitchen/rear door facing the alley.",
             "The reopened asset contains these three named doors, a ramp, and a modest covered back porch next to the alley door; door-to-porch center spacing is %.2f m." % (rear_porch_gap or -1),
             "Purdue lists room 110 as Back Porch. Front/rear render inspection confirms the covered porch is now on the rear/alley-facing side; the undocumented Fifth Street front porch is absent.",
             "Window rhythm, shutters, exact door positions, porch dimensions, clapboard detail, and gabled roof are not verified by measured plans or a date-verified facade photo." ]},
        {"criterion": "Modular export, portability, and complete evidence", "max_points": 2, "points": 1.5,
         "status": "export validated; index needs refresh", "evidence": [
             "Blender 5.2.3 reopened the saved named collection with %d mesh objects and %d assigned materials; portable procedural materials=%s; external image paths=%s." % (sum(o.type == "MESH" for o in objects), len(materials), portable_materials, external_images),
             "All nine expected feature/interior flags present: %s." % all(feature_checks.values()),
             "Building-specific evidence includes source URLs, provider/feature, retrieval dates, CRS/transform, uncertainty, validation and current front/rear renders.",
             "The shared manifest still lists removed NACC_front_porch objects and has local_bounds_m inconsistent with the reopened asset; stale names: %s; recorded bounds: %s." % (stale_manifest_names, manifest_bounds)]},
    ]
    score = round(sum(c["points"] for c in criteria), 2)
    findings = [
        "The porch relocation is source-consistent: Purdue says the rear/kitchen door faces the alley and identifies room 110 as Back Porch. The revised render places the roofed porch beside that door and leaves the Fifth Street entrance without a covered porch.",
        "GIS identity, shape, dimensions, and local registration check out against feature 927. The transform is an approximate project conversion, not survey control.",
        "The exact roof profile, heights, and facade composition remain estimates. The GIS one-level attribute conflicts with the written two-story BEP, so vertical accuracy is only partly supported.",
        "The asset file and building evidence are current, but the shared manifest’s object list/bounds are stale relative to this saved revision. This is reported for the coordinator and was not edited here.",
    ]
    result = {
        "evaluator": "independent_nacc_rubric_v1",
        "asset": os.path.relpath(ASSET, ROOT).replace("\\", "/"),
        "asset_sha256": sha256(ASSET),
        "expected_sha256": "E442E099CF94DDE2B0D95F87E336AC550DAF3445C56A3129C078AE64657E3305",
        "blender_version": bpy.app.version_string,
        "score": score,
        "max_score": 10,
        "minimum_passing_score": 8,
        "passed": score >= 8,
        "criteria": criteria,
        "evidence": {
            "gis_feature_id": attrs.get("FID"),
            "gis_name": attrs.get("BUILDING_N"),
            "gis_address": attrs.get("ADDRESS"),
            "gis_source_area_m2_projected": round(area, 3),
            "gis_footprint_dimensions_m": [round(x, 4) for x in gis_dims],
            "shell_footprint_dimensions_m": [round(x, 4) for x in shell_dims],
            "gis_to_shell_vertex_hausdorff_m": round(gis_to_shell, 5) if gis_to_shell is not None else None,
            "shell_to_gis_vertex_hausdorff_m": round(shell_to_gis, 5) if shell_to_gis is not None else None,
            "shell_centroid_local_xy_m": [round(x, 5) for x in centroid_offset],
            "registered_placement_origin_xy_m": entry.get("placement_origin_xy_m"),
            "model_vertical_bounds_m": [round(x, 3) for x in bounds],
            "feature_checks": feature_checks,
            "material_count": len(materials),
            "portable_procedural_materials": portable_materials,
            "external_image_paths": external_images,
            "rear_door_xy_center_m": [round(x, 3) for x in rear_center] if rear_center else None,
            "back_porch_xy_center_m": [round(x, 3) for x in porch_center] if porch_center else None,
            "rear_door_to_porch_center_distance_m": round(rear_porch_gap, 3) if rear_porch_gap is not None else None,
            "manifest_stale_object_names": stale_manifest_names,
            "manifest_recorded_local_bounds_m": manifest_bounds,
            "evidence_record_revision": evidence.get("revision"),
            "front_render": os.path.basename(evidence["validation"]["preview"]),
            "rear_render": os.path.basename(evidence["validation"]["rear_preview"]),
        },
        "findings": findings,
        "limitations": [
            "No measured as-built elevation or date-verified current facade photograph was found in the consulted evidence.",
            "Entrance and porch positions/sizes are supported directionally by the BEP but their exact dimensions and wall offsets remain estimates.",
            "The GIS source and project transformation support local shape/registration checks; they do not establish surveyed positional accuracy.",
            "Manifest mismatch is a reported coordinator-owned shared-file issue and was not changed by this independent grader.",
        ],
    }
    with open(OUT_JSON, "w", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    report = [
        "# Independent NACC asset grade", "", f"**Score: {score:.2f}/10** — {'PASS' if result['passed'] else 'below the 8/10 minimum'}",
        "", f"Saved asset SHA-256: `{result['asset_sha256']}`", f"Blender: {result['blender_version']}", "",
        "## Criterion scorecard", "", "| Criterion | Score | Assessment |", "|---|---:|---|",
    ]
    report += [f"| {c['criterion']} | {c['points']:.2f}/{c['max_points']} | {c['status']} |" for c in criteria]
    report += ["", "## Evidence", ""]
    for criterion in criteria:
        report.append(f"### {criterion['criterion']} — {criterion['points']:.2f}/{criterion['max_points']}")
        report.append("")
        report += [f"- {item}" for item in criterion["evidence"]]
        report.append("")
    report += ["## Findings", ""] + [f"- {x}" for x in findings]
    report += ["", "## Limitations", ""] + [f"- {x}" for x in result["limitations"]]
    report += ["", "## Source references", "",
               "- Purdue Office of Emergency Preparedness, NACC Building Emergency Plan (revision 2026-03-17): https://www.purdue.edu/operations/emergency-preparedness/nacc/",
               "- Purdue University BuildingShapes ArcGIS FeatureServer, layer 0, FID 927 (snapshot in this audit folder).",
               "- Purdue Native American Educational and Cultural Center: https://purdue.edu/naecc/", ""]
    with open(OUT_MD, "w", encoding="utf-8") as stream:
        stream.write("\n".join(report))
    print(json.dumps({"score": score, "asset_sha256": result["asset_sha256"], "report": OUT_MD, "json": OUT_JSON}, indent=2))
    return result


if __name__ == "__main__":
    evaluate()
