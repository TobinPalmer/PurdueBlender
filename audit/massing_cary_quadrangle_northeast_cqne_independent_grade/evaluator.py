"""Independent, reproducible CQNE massing grade. Run with Blender Python."""
import json
import math
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[2]
ID = "massing_cary_quadrangle_northeast_cqne_0a76fca"
ASSET = ROOT / "modular" / "buildings" / f"{ID}.blend"
EVIDENCE_DIR = ROOT / "audit" / ID
SOURCES = EVIDENCE_DIR / "sources"
REPORT_DIR = ROOT / "audit" / "massing_cary_quadrangle_northeast_cqne_independent_grade"
REPORT_DIR.mkdir(parents=True, exist_ok=True)
GIS = json.loads((SOURCES / "purdue_gis_feature_638_cqne_4326.json").read_text(encoding="utf-8"))
FEATURE = GIS["features"][0]
RING = FEATURE["geometry"]["rings"][0]
ATTR = FEATURE["attributes"]
LAT0, LON0 = 40.4274, -86.9137
XSCALE = 111412.84 * math.cos(math.radians(LAT0))
YSCALE = 111040.0

bpy.ops.wm.open_mainfile(filepath=str(ASSET))
scene_name = f"Building_{ID}"
collection_name = f"Asset_{ID}"
scene = bpy.data.scenes.get(scene_name)
collection = bpy.data.collections.get(collection_name)
objects = list(collection.objects) if collection else []
depsgraph = bpy.context.evaluated_depsgraph_get()
points = []
missing_external = []
modifier_map = {}
for image in bpy.data.images:
    if image.source == "FILE" and image.filepath:
        p = Path(bpy.path.abspath(image.filepath))
        if not p.exists():
            missing_external.append(image.filepath)
for obj in objects:
    if obj.modifiers:
        modifier_map[obj.name] = [f"{m.name}:{m.type}" for m in obj.modifiers]
    if obj.type == "MESH":
        ev = obj.evaluated_get(depsgraph)
        mesh = ev.to_mesh()
        points.extend([ev.matrix_world @ v.co for v in mesh.vertices])
        ev.to_mesh_clear()

mins = [min(p[i] for p in points) for i in range(3)] if points else []
maxs = [max(p[i] for p in points) for i in range(3)] if points else []
dimensions = [maxs[i] - mins[i] for i in range(3)] if points else []
wall = bpy.data.objects.get("CQNE | GIS footprint walls")
wall_vertices = list(wall.data.vertices) if wall and wall.type == "MESH" else []
source_xy = []
for lon, lat in RING:
    xy = ((lon - LON0) * XSCALE, (lat - LAT0) * YSCALE)
    if not source_xy or math.dist(source_xy[-1], xy) > 0.005:
        source_xy.append(xy)
if len(source_xy) > 1 and math.dist(source_xy[0], source_xy[-1]) < 0.005:
    source_xy.pop()
wall_xy = sorted(set((v.co.x, v.co.y) for v in wall_vertices))
source_xy_unique = sorted(set(source_xy))
source_set = set(source_xy_unique)
wall_xy_unique = set(wall_xy)
nearest_deltas = [min(math.dist(p, q) for q in wall_xy_unique) for p in source_set] if wall_xy_unique else []
reverse_deltas = [min(math.dist(p, q) for q in source_set) for p in wall_xy_unique] if source_set else []
max_vertex_delta_m = max(nearest_deltas + reverse_deltas) if nearest_deltas and reverse_deltas else None
footprint_exact = (len(source_set) == len(wall_xy_unique) and max_vertex_delta_m is not None and max_vertex_delta_m < 0.001)
source_bounds = [min(x for x, y in source_xy), min(y for x, y in source_xy),
                 max(x for x, y in source_xy), max(y for x, y in source_xy)]
wall_bounds = ([min(x for x, y in wall_xy), min(y for x, y in wall_xy),
                max(x for x, y in wall_xy), max(y for x, y in wall_xy)] if wall_xy else [])
footprint_bounds_delta = (max(abs(a-b) for a, b in zip(source_bounds, wall_bounds))
                          if wall_bounds else None)

# The ArcGIS service has no unit/definition metadata for the `Extrution` field.
# Keep the numerical value and the unsupported unit interpretation explicit.
asset_files = [str(x.relative_to(ROOT)).replace("\\", "/") for x in
               [ASSET, EVIDENCE_DIR / "build_evidence.json", SOURCES / "purdue_gis_feature_638_cqne_4326.json"]]
checks = {
    "expected_scene": scene is not None,
    "expected_collection": collection is not None,
    "GIS_feature_identity": ATTR.get("FID") == 638 and ATTR.get("BLDG_ABBR") == "CQNE",
    "source_footprint_vertex_set_exact": footprint_exact,
    "footprint_bbox_max_abs_delta_m": round(footprint_bounds_delta, 6) if footprint_bounds_delta is not None else None,
    "all_mesh_geometry_in_expected_collection": bool(objects) and all(o.type == "MESH" for o in objects),
    "no_missing_external_images": not missing_external,
    "no_modifiers": not modifier_map,
}
criteria = [
    {"criterion": "Correct identity and source-backed footprint", "points": 2.0,
     "score": 2.0 if checks["GIS_feature_identity"] and footprint_exact else 0.5,
     "evidence": ["Purdue GIS FeatureServer Feature 638 identifies Franklin Levering Cary Quadrangle (NE), abbreviation CQNE.",
                  f"The asset wall mesh has {len(wall_xy_unique)} unique plan vertices versus {len(source_set)} in the raw GIS ring after the repository local approximation; maximum bidirectional vertex mismatch={max_vertex_delta_m} m (float precision tolerance 0.001 m).",
                  "The service feature describes an individual CQNE footprint, though its broader historic label is the Cary Quadrangle."],
     "findings": [] if footprint_exact else ["Wall footprint does not exactly reproduce the source ring."]},
    {"criterion": "Position, orientation, and scale/dimensions", "points": 2.0,
     "score": 2.0 if footprint_exact and footprint_bounds_delta is not None and footprint_bounds_delta < 0.01 else 1.0,
     "evidence": ["Asset uses campus-coordinate massing geometry; walls reproduce source coordinates after the repository's documented approximate conversion.",
                  f"Raw GIS axis-aligned bounds in local metres: {source_bounds}; wall mesh bounds: {wall_bounds}; max edge delta {footprint_bounds_delta} m.",
                  f"Rendered aggregate bounds include roof/window projections and measure {dimensions} m; these are not the structural plan dimensions."],
     "findings": ["The coordinate conversion is a local approximation, not a surveyed CRS; GIS source units and survey tolerance are not documented in the snapshot."]},
    {"criterion": "Evidence-backed height, floors, and roof form", "points": 2.0,
     "score": 0.5,
     "evidence": [f"Purdue GIS records CountOfFLO={ATTR.get('CountOfFLO')} and Extrution={ATTR.get('Extrution')}.",
                  "FeatureServer schema describes Extrution only as an editable integer field; it provides no unit or semantic definition. The 48 ft interpretation and 14.6304 m peak are therefore not established by the source metadata.",
                  "The five window rows match the five-level count. Roof form is acknowledged by the author as an aerial-informed schematic; the aerial shows the Cary complex collectively, not CQNE-specific measured roof structure."],
     "findings": ["Claimed 48 ft / 14.63 m height is unsupported by available field metadata; retain as unverified.",
                  "Exact eave height, roof pitch, and CQNE-specific roof bays are unverified."]},
    {"criterion": "Facade, entrances, and distinctive architecture", "points": 2.0,
     "score": 0.75,
     "evidence": ["Preview visibly renders five storeys of repeated windows, brick color, stone courses, projecting gabled bays and an entry cue.",
                  "Purdue's current Cary aerial and historic general-quadrangle photograph support broad material/style context only; neither isolates CQNE or locates its entrance.",
                  "Builder evidence correctly labels facade bays, entrance, and material dimensions as schematic/estimated."],
     "findings": ["No source verifies this building's exact facade rhythm, entrance location, trim, or projecting dormers; these are visual interpretation rather than source-backed details."]},
    {"criterion": "Modular export, portability, and complete evidence", "points": 2.0,
     "score": 1.75 if scene and collection and not missing_external and not modifier_map else 0.75,
     "evidence": [f"Expected scene and collection: {scene_name}; {collection_name}. Collection has {len(objects)} mesh objects.",
                  f"Evaluated mesh world bounds: min={mins}, max={maxs}, dimensions={dimensions} m.",
                  f"Modifiers={modifier_map}; missing external image files={missing_external}.",
                  "Evidence includes raw GIS JSON, raw official housing page, aerial image, historical image, URLs, retrieval date, CRS/method, and uncertainty statements."],
     "findings": ["Evidence has no field definition or source-date/tolerance for GIS vertical attributes; height evidence remains incomplete."]},
]
score = round(sum(c["score"] for c in criteria), 2)
report = {
    "building_id": ID,
    "grade_type": "fresh independent source and saved-asset review",
    "grade_date": "2026-10-26",
    "asset": str(ASSET.relative_to(ROOT)).replace("\\", "/"),
    "source_evidence": [str((EVIDENCE_DIR / "build_evidence.json").relative_to(ROOT)).replace("\\", "/"),
                        str((SOURCES / "purdue_gis_feature_638_cqne_4326.json").relative_to(ROOT)).replace("\\", "/")],
    "score": score,
    "max_score": 10,
    "pass_threshold": 8,
    "passed": score >= 8,
    "criteria": criteria,
    "evidence": {"checks": checks, "scene": scene_name if scene else None,
                 "collection": collection_name if collection else None,
                 "object_count": len(objects), "mesh_count": sum(o.type == "MESH" for o in objects),
                 "world_bounds_m": [mins, maxs], "world_dimensions_m": dimensions,
                 "source_footprint_bounds_local_m": source_bounds, "wall_footprint_bounds_local_m": wall_bounds,
                 "source_feature_attributes": {k: ATTR.get(k) for k in ["FID", "BUILDING_N", "BLDG_ABBR", "NUM_LEVELS", "CountOfFLO", "Extrution", "Shape__Area", "Shape__Length"]},
                 "source_service_metadata": "https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0?f=pjson",
                 "source_urls": ["https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query?where=FID%3D638&outFields=*&returnGeometry=true&outSR=4326&f=pjson",
                                 "https://www.housing.purdue.edu/my-housing/options/residence-halls/cary-quad.html",
                                 "https://www.housing.purdue.edu/images/banners/ur-aerial-view-of-cary-visit-hero.jpg",
                                 "https://earchives.lib.purdue.edu/digital/collection/pbuildings/id/159/"]},
    "findings": [f for c in criteria for f in c["findings"]],
    "evaluator": str((REPORT_DIR / "evaluator.py").relative_to(ROOT)).replace("\\", "/"),
}
(REPORT_DIR / "result.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
