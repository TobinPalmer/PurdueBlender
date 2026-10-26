"""Independent evidence and saved-asset grader for TREC; run with Blender Python.

Returns a criterion-level JSON result per AGENT.md section 5. Geometry facts are
recomputed from the raw GIS/OSM snapshots and the reopened .blend; evidence
limitations and visual observations are independently stated below.
"""
import json
import math
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "audit" / "massing_turf_recreation_exercise_center_9622f45"
ASSET = ROOT / "modular" / "buildings" / "massing_turf_recreation_exercise_center_9622f45.blend"
GIS = AUDIT / "sources" / "purdue_gis_trec_oid312_2026-10-26.geojson"
OSM = AUDIT / "sources" / "osm_trec_way_283275002_2026-10-26.json"
EVIDENCE = AUDIT / "evidence.json"
OVERLAY = AUDIT / "orthophoto_footprint_overlay.png"
VIEWS = [AUDIT / n for n in ("preview.png", "preview_top.png", "preview_north_gable.png")]
LAT0, LON0 = 40.4274, -86.9137


def campus_xy(lon, lat):
    return ((lon - LON0) * 111412.84 * math.cos(math.radians(LAT0)),
            (lat - LAT0) * 111040.0)


def polygon_area(points):
    return abs(sum(points[i][0] * points[(i + 1) % len(points)][1]
                   - points[(i + 1) % len(points)][0] * points[i][1]
                   for i in range(len(points))) / 2)


def bounds(points):
    return [[min(p[0] for p in points), max(p[0] for p in points)],
            [min(p[1] for p in points), max(p[1] for p in points)]]


def evaluate():
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    gj = json.loads(GIS.read_text(encoding="utf-8-sig"))
    feature = gj["features"][0]
    props = feature["properties"]
    gis_ring = [campus_xy(*p) for p in feature["geometry"]["coordinates"][0][:-1]]
    osm = json.loads(OSM.read_text(encoding="utf-8-sig"))
    nodes = {e["id"]: e for e in osm["elements"] if e["type"] == "node"}
    way = next(e for e in osm["elements"] if e["type"] == "way")
    osm_ring = [campus_xy(nodes[n]["lon"], nodes[n]["lat"]) for n in way["nodes"][:-1]]

    # Reopen the shipped library independently; do not rely on the builder's reopen report.
    bpy.ops.wm.open_mainfile(filepath=str(ASSET))
    scene_name = "Building_massing_turf_recreation_exercise_center_9622f45"
    collection_name = "Asset_massing_turf_recreation_exercise_center_9622f45"
    scene = bpy.data.scenes.get(scene_name)
    collection = bpy.data.collections.get(collection_name)
    if scene is None or collection is None:
        raise RuntimeError("Expected scene or exported collection is missing")
    wall = bpy.data.objects.get("TREC_Metal_Wall_Envelope")
    roof = bpy.data.objects.get("TREC_Gabled_Metal_Roof_ESTIMATED")
    if wall is None or roof is None:
        raise RuntimeError("Expected wall envelope or gabled roof is missing")

    wall_xy = []
    zs = []
    for v in wall.data.vertices:
        w = wall.matrix_world @ v.co
        wall_xy.append((float(w.x), float(w.y)))
        zs.append(float(w.z))
    # The wall mesh duplicates vertices edge-by-edge; compare each unique planar
    # coordinate to the raw GIS ring and quantify maximum nearest-vertex offset.
    unique_xy = sorted(set((round(x, 6), round(y, 6)) for x, y in wall_xy))
    max_xy_to_gis_m = max(min(math.hypot(x - gx, y - gy) for gx, gy in gis_ring)
                          for x, y in unique_xy)
    gis_b = bounds(gis_ring)
    osm_b = bounds(osm_ring)
    gis_dims = [gis_b[0][1] - gis_b[0][0], gis_b[1][1] - gis_b[1][0]]
    osm_dims = [osm_b[0][1] - osm_b[0][0], osm_b[1][1] - osm_b[1][0]]
    gis_center = [(b[0] + b[1]) / 2 for b in gis_b]
    osm_center = [(b[0] + b[1]) / 2 for b in osm_b]
    center_delta = [gis_center[i] - osm_center[i] for i in range(2)]
    z_bounds = [min(zs), max(zs)]
    has_images = [p.exists() and p.stat().st_size > 0 for p in VIEWS]
    ext_images = [p.stat().st_size for p in VIEWS if p.exists()]
    external_images = [im.filepath for im in bpy.data.images
                       if im.source == "FILE" and im.filepath and not im.packed_file]
    collection_objects = list(collection.objects)
    types = sorted({o.type for o in collection_objects})

    # Rubric scoring (0-2 per criterion); unsupported attributes are not awarded
    # based on visual plausibility. The roof silhouette receives credit for plan evidence.
    criteria = [
        {
            "criterion": "Correct identity and source-backed footprint",
            "score": 1.5, "max_score": 2,
            "status": "verified with a source conflict",
            "evidence": [
                f"Raw Purdue feature {props.get('OBJECTID')} is named {props.get('Name')!r}, ABBR={props.get('ABBR')!r}; raw OSM way {way['id']} is tagged name=Turf Recreation Exercise Center/ref=TREC.",
                f"Saved wall envelope's maximum XY nearest-source-vertex deviation from current Purdue GIS is {max_xy_to_gis_m:.4f} m; GIS ring has {len(gis_ring)} non-closure vertices and computed area {polygon_area(gis_ring):.1f} m².",
                f"Area cross-check remains imperfect: raw Purdue GIS squarefootage attribute is {props.get('squarefootage')} ft², while the Purdue RecWell fact sheet reports TREC project size as 29,037 ft²; polygon plan area is {polygon_area(gis_ring)*10.7639:.0f} ft².",
                "The official campus map and the 2023 orthophoto identify the right long-roofed field hall; no confusion with CoRec/Aquatic Center or the Intercollegiate Athletic Sports Turf Building is evident.",
                f"Orthophoto overlay shows the Purdue red line and OSM blue line on the same roof, but not coincident: GIS center relative to OSM is {center_delta[0]:.2f} m east-west and {center_delta[1]:.2f} m north-south; OSM outline tracks the visible roof edge more closely."
            ],
            "findings": ["Building identity is strong; structural wall ring follows the named current Purdue polygon. The roof-edge evidence favors the OSM ring, so actual wall/roof-perimeter relationship remains a source conflict."],
        },
        {
            "criterion": "Position, orientation, and scale/dimensions",
            "score": 1.0, "max_score": 2,
            "status": "partly verified; source/manifest position conflict",
            "evidence": [
                f"Wall plan dimensions from raw Purdue GIS are {gis_dims[0]:.2f} m east-west by {gis_dims[1]:.2f} m north-south; model wall ring matches GIS vertices within {max_xy_to_gis_m:.4f} m.",
                f"Orthophoto and both polygon sources show a long north-south axis; model ridge is north-south.",
                f"GIS is {center_delta[0]:.2f} m west and {center_delta[1]:.2f} m south of OSM/prior manifest bounds; GIS is {gis_dims[0]-osm_dims[0]:.2f} m narrower east-west. Overlay indicates the GIS perimeter is inside the observed roof edge along portions of the building.",
                "The saved asset retains the required direct campus-coordinate massing convention, but the shared manifest still contains the previous OSM-matching bounds pending coordinator update."
            ],
            "findings": ["Do not treat placement as fully resolved until the coordinator updates the manifest/crosswalk and validates the roof-to-wall perimeter. The geometric scale is accurate to the selected GIS record, not confirmed against a definitive as-built outline."],
        },
        {
            "criterion": "Evidence-backed height, floors, and roof form",
            "score": 1.0, "max_score": 2,
            "status": "roof plan supported; vertical dimensions unverified estimates",
            "evidence": [
                "Orthophoto supports the pale roof and two-plane gable silhouette with a north-south ridge; saved gable shape matches this broad profile.",
                f"Wall mesh rises from {z_bounds[0]:.2f} m to {z_bounds[1]:.2f} m; evidence labels eave 7.4 m and ridge 11.2 m as estimates, not measured.",
                "No cited plan, elevation, section, lidar, or source confirms eave/ridge heights or floor count. The model's single clear-span hall is consistent with facility use, but floors/height are not evidence-backed."
            ],
            "findings": ["Height and story count remain unsupported. Roof seam direction in the model's top view is parallel to the ridge, while visible repeated bands in the 2023 orthophoto run across the short dimension; that detail should be reconciled before calling the roof pattern evidence-backed."],
        },
        {
            "criterion": "Facade, entrances, and distinctive architecture",
            "score": 0.5, "max_score": 2,
            "status": "mostly illustrative",
            "evidence": [
                "The saved views show a plain single-volume metal-clad hall with generic base course and wall ribs.",
                "No facade/elevation/street-level evidence in the provided sources establishes cladding material, rib spacing, door count, or entry side/location.",
                "The west personnel door object is explicitly named LOCATION_ILLUSTRATIVE; its placement is not corroborated by source evidence."
            ],
            "findings": ["Most facade detail and the entrance are inferred rather than source-backed; the render cannot substitute for facade evidence."],
        },
        {
            "criterion": "Modular export, portability, and complete evidence",
            "score": 2.0, "max_score": 2,
            "status": "verified for standalone asset",
            "evidence": [
                f"Saved library reopened independently with expected scene/collection; collection has {len(collection_objects)} objects and types {types}; stable asset path and collection names are preserved.",
                f"All three requested views exist ({has_images}) and the registered orthophoto overlay exists ({OVERLAY.exists()}).",
                f"No unpacked external file images are referenced by the blend: {external_images}.",
                "Evidence folder contains raw official Purdue GIS and OSM snapshots, official RecWell/campus-map material, 2023 Indiana orthophoto, comparison overlay, method, CRS, dates, and uncertainties.",
                "Master integration/neighboring context was not part of this isolated asset grade."
            ],
            "findings": ["Standalone export and evidence organization are complete; master placement and integration remain coordinator-owned."],
        },
    ]
    score = round(sum(c["score"] for c in criteria), 1)
    return {
        "building_id": "massing_turf_recreation_exercise_center_9622f45",
        "building_name": "Turf Recreation Exercise Center (TREC)",
        "reviewer": "independent evaluator; raw-source and reopened-library inspection",
        "score": score, "max_score": 10,
        "passing_standard": 8,
        "criteria": criteria,
        "evidence": {
            "raw_source_checks": {
                "purdue_feature_id": props.get("OBJECTID"), "purdue_name": props.get("Name"),
                "purdue_abbr": props.get("ABBR"), "gis_vertex_count": len(gis_ring),
                "gis_area_m2": round(polygon_area(gis_ring), 2),
                "osm_way_id": way["id"], "osm_tags": way.get("tags", {}),
                "osm_area_m2": round(polygon_area(osm_ring), 2),
                "purdue_gis_squarefootage_attribute_ft2": props.get("squarefootage"),
                "purdue_recwell_fact_sheet_area_ft2": 29037,
                "computed_gis_polygon_area_ft2": round(polygon_area(gis_ring) * 10.7639),
                "gis_center_minus_osm_center_m": [round(v, 3) for v in center_delta],
                "gis_minus_osm_dimensions_m": [round(gis_dims[i] - osm_dims[i], 3) for i in range(2)],
            },
            "saved_asset_checks": {
                "asset": str(ASSET.relative_to(ROOT)), "scene": scene.name,
                "collection": collection.name, "object_count": len(collection_objects),
                "object_types": types, "wall_unique_xy_points": len(unique_xy),
                "max_wall_xy_to_gis_vertex_m": round(max_xy_to_gis_m, 5),
                "wall_z_bounds_m": [round(v, 3) for v in z_bounds],
                "three_views_exist": has_images, "view_file_bytes": ext_images,
                "unpacked_external_images": external_images,
            },
            "visual_review": {
                "files": [p.name for p in VIEWS] + [OVERLAY.name],
                "roof_seam_axis_conflict": "model top view seams are parallel to N-S ridge; 2023 orthophoto shows repeated roof bands predominantly across the short E-W dimension",
                "limitations": ["Orthophoto is plan-only and cannot verify facade or height.", "No source corroborates the illustrative personnel door."],
            },
        },
        "findings": [finding for c in criteria for finding in c["findings"]],
        "recommendation": "Below 8/10. Resolve the roof seam direction and seek/record facade and vertical evidence where available; coordinator must reconcile the GIS-vs-OSM roof-edge/perimeter and shared manifest position before accepting placement.",
    }


if __name__ == "__main__":
    result = evaluate()
    out = AUDIT / "independent_grade.json"
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    print(f"Saved independent grade: {out}")
