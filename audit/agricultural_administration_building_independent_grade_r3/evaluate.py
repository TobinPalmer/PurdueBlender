from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ID = "agricultural_administration_building"
AUDIT = ROOT / "audit" / f"{ID}_independent_grade_r3"
EVIDENCE_DIR = ROOT / "audit" / ID
ASSET = ROOT / "modular" / "buildings" / f"{ID}.blend"
GIS_FILE = EVIDENCE_DIR / "sources" / "agricultural_administration_gis_feature_267_current.json"
BUILD_FILE = EVIDENCE_DIR / "build_evidence.json"
PROBE_FILE = AUDIT / "blender_probe.json"
MANIFEST_FILE = ROOT / "modular" / "manifest.json"

def directed_hausdorff(a, b):
    return max(min(math.dist(p, q) for q in b) for p in a)

def bounds_xy(points):
    return [min(p[0] for p in points), min(p[1] for p in points),
            max(p[0] for p in points), max(p[1] for p in points)]

def polygon_centroid(points):
    cross = [points[i][0] * points[(i+1) % len(points)][1] - points[(i+1) % len(points)][0] * points[i][1]
             for i in range(len(points))]
    twice_area = sum(cross)
    cx = sum((points[i][0] + points[(i+1) % len(points)][0]) * cross[i]
             for i in range(len(points))) / (3 * twice_area)
    cy = sum((points[i][1] + points[(i+1) % len(points)][1]) * cross[i]
             for i in range(len(points))) / (3 * twice_area)
    return cx, cy

def evaluate():
    raw = json.loads(GIS_FILE.read_text(encoding="utf-8"))
    features = raw["features"] if isinstance(raw, dict) and "features" in raw else [raw]
    feature = next(f for f in features if f.get("attributes", {}).get("FID") == 267)
    attrs = feature["attributes"]
    lonlat = [tuple(map(float, p[:2])) for p in feature["geometry"]["rings"][0][:-1]]
    lat0, lon0 = 40.4274, -86.9137
    xscale = 111412.84 * math.cos(math.radians(lat0))
    campus_xy = [((lon - lon0) * xscale, (lat - lat0) * 111040.0) for lon, lat in lonlat]
    cx, cy = polygon_centroid(campus_xy)
    source_local = [(x-cx, y-cy) for x, y in campus_xy]

    probe = json.loads(PROBE_FILE.read_text(encoding="utf-8"))
    actual = [tuple(p) for p in probe["shell_bottom_unique_vertices_xy_m"]]
    assert len(source_local) == 24 and len(actual) == 24
    hausdorff = max(directed_hausdorff(source_local, actual), directed_hausdorff(actual, source_local))
    source_bounds = bounds_xy(source_local)
    model_bounds = bounds_xy(actual)
    bounds_error = max(abs(a-b) for a,b in zip(source_bounds, model_bounds))
    source_center = (cx, cy)

    manifest = json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))
    entry = next(x for x in manifest["assets"] if x.get("id") == ID)
    origin = entry.get("placement_origin_xy_m")
    origin_error = math.dist(source_center, origin)
    names_match = sorted(entry.get("objects", [])) == probe["collection_object_names"]
    count_match = entry.get("object_count") == probe["collection_object_count"]
    manifest_matches = names_match and count_match
    identity_match = (attrs.get("BLDG_ABBR") == "AGAD" and
                      attrs.get("BUILDING_N") == "Agricultural Administration Building" and
                      attrs.get("ADDRESS") == "615 Mitch Daniels Blvd" and
                      attrs.get("OWNER") == "PURDUE")
    build = json.loads(BUILD_FILE.read_text(encoding="utf-8"))
    asset_hash = hashlib.sha256(ASSET.read_bytes()).hexdigest()
    hash_matches_probe = asset_hash == probe["asset_sha256"]
    assert identity_match and hash_matches_probe
    assert probe["export_reopened"] and probe["export_object_names_match"]

    criteria = [
        {
            "name": "Correct identity and source-backed footprint",
            "score": 2.0 if identity_match and hausdorff < 0.01 else 0.0,
            "max_score": 2.0,
            "evidence": [
                "Purdue University BuildingShapes FeatureServer feature 267 identifies AGAD by building code, full name, street address, and Purdue ownership.",
                f"The reopened shell's 24 base vertices match the raw GIS exterior ring with symmetric Hausdorff error {hausdorff:.6f} m."
            ]
        },
        {
            "name": "Position, orientation, and scale/dimensions",
            "score": 2.0 if origin_error < 0.01 and bounds_error < 0.01 and entry.get("local_coordinates") else 0.0,
            "max_score": 2.0,
            "evidence": [
                f"The GIS centroid is ({cx:.6f}, {cy:.6f}) m and matches manifest placement origin within {origin_error:.6f} m.",
                f"Local GIS/model XY bounds differ by at most {bounds_error:.6f} m; a 24-vertex shape comparison verifies orientation and dimensions beyond a bounding-box-only check."
            ]
        },
        {
            "name": "Evidence-backed height, floors, and roof form",
            "score": 0.9,
            "max_score": 2.0,
            "evidence": [
                "Current GIS reports NUM_LEVELS=5 and CountOfFLO=5, supporting a five-level diagrammatic treatment; neither field defines floor datums or measurement units.",
                "The modeled 17.2 m height and 3.44 m bands are explicitly estimates. Purdue Archives supports a tile roof and two stories plus a basement only at the 1908 opening, and notes later renovations; the present roof is not established, so the neutral cap is correctly marked as a placeholder."
            ]
        },
        {
            "name": "Facade, entrances, and distinctive architecture",
            "score": 1.6,
            "max_score": 2.0,
            "evidence": [
                "The 2023 Purdue Stories entrance photograph supports present-day brick and limestone, repeated window bays, and a tall glazed entrance; an archival Purdue photograph supports the historical brick/stone vocabulary.",
                "The inspected entrance render now includes a tall glazed portal with stacked panes, paired lower doors, mullions, and limestone jamb/lintel. Exact doorway location, pane count, window cadence, and dimensions remain estimates from uncalibrated imagery."
            ]
        },
        {
            "name": "Modular export, portability, and complete evidence",
            "score": 2.0 if manifest_matches and not probe["external_unpacked_image_dependencies"] and not probe["linked_library_paths"] and probe["export_reopened"] else 0.0,
            "max_score": 2.0,
            "evidence": [
                f"A separate Blender 4.5.15 process reopened the saved asset and exported/reopened {probe['export_collection']} with {probe['export_object_count']} objects; the shared manifest's names and count match exactly.",
                "The exported collection has no missing unpacked image dependencies or linked libraries. The evidence folder includes raw GIS and layer-metadata snapshots, two Purdue photo files, source provenance, rendered overview/entrance views, and a reopen-validation report."
            ]
        }
    ]
    score = round(sum(c["score"] for c in criteria), 2)
    return {
        "building_id": ID,
        "score": score,
        "max_score": 10,
        "pass_threshold": 8,
        "passed": score >= 8,
        "criteria": criteria,
        "evidence": {
            "gis_feature_id": attrs.get("FID"),
            "source_identity": {k: attrs.get(k) for k in ("BLDG_ABBR", "BUILDING_N", "ADDRESS", "OWNER")},
            "source_crs": "GIS snapshot returned as EPSG:4326; project-prescribed local approximation used for ground coordinates",
            "source_vertex_count": len(source_local),
            "model_base_vertex_count": len(actual),
            "symmetric_hausdorff_error_m": hausdorff,
            "source_local_bounds_m": source_bounds,
            "model_local_bounds_m": model_bounds,
            "bounds_error_m": bounds_error,
            "source_centroid_xy_m": list(source_center),
            "manifest_placement_origin_xy_m": origin,
            "placement_origin_error_m": origin_error,
            "modeled_height_m": probe["shell_bounds_evaluated_local_m"][2][1],
            "gis_NUM_LEVELS": attrs.get("NUM_LEVELS"),
            "gis_CountOfFLO": attrs.get("CountOfFLO"),
            "gis_Extrution_raw_value": attrs.get("Extrution"),
            "manifest_count_and_names_match": manifest_matches,
            "external_unpacked_image_dependencies": probe["external_unpacked_image_dependencies"],
            "linked_library_paths": probe["linked_library_paths"],
            "asset_sha256": asset_hash,
            "blender_version": "4.5.15",
            "probe_file": "audit/agricultural_administration_building_independent_grade_r3/blender_probe.json",
            "evidence_record": "audit/agricultural_administration_building/build_evidence.json",
            "raw_gis_snapshot": "audit/agricultural_administration_building/sources/agricultural_administration_gis_feature_267_current.json",
            "visuals_inspected": [
                "audit/agricultural_administration_building/agricultural_administration_building_overview.png",
                "audit/agricultural_administration_building/agricultural_administration_building_entrance.png",
                "audit/agricultural_administration_building/sources/agad_entrance_2023.jpg"
            ]
        },
        "findings": [
            "PASS: source identity, GIS outline, local bounds, centroid/placement origin, and orientation are independently verified from reopened geometry.",
            "PASS: the revised entrance composition is photo-backed and visible in the close render; present facade materials are supported by Purdue imagery.",
            "LIMITATION: only five-level count is supported by current GIS; height, floor spacing, and present roof remain estimated or unverified. The tile roof and two stories plus basement apply to the 1908 historical state.",
            "PASS: expected collection exports and reopens; manifest count/names match; no unpacked images or linked-library dependencies were found."
        ]
    }

if __name__ == "__main__":
    result = evaluate()
    (AUDIT / "result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
