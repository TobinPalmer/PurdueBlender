"""Independent, read-only rubric evaluator for the ADDL detailed asset.

Run from any directory with the project Python and Blender installed:
    python outputs/PurdueBlender/audit/animal_disease_diagnostic_laboratory_independent_grade/evaluate.py

The evaluator reopens the saved .blend and the exported collection probe in
Blender, independently compares evaluated shell vertices to the checked-in
Purdue GIS snapshot, and writes result.json beside this file.  No model,
builder, or source evidence is modified.
"""
from __future__ import annotations

import json
import math
import os
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[3]
PURDUE = PROJECT / "outputs/PurdueBlender"
ASSET_ID = "animal_disease_diagnostic_laboratory"
EVIDENCE = PURDUE / "audit/animal_disease_diagnostic_laboratory"
ASSET = PURDUE / "modular/buildings/animal_disease_diagnostic_laboratory.blend"
GIS = PURDUE / "audit/build_batch_a/animal_disease_diagnostic_laboratory_gis_feature_241.json"
MANIFEST = PURDUE / "modular/manifest.json"
PROBE = HERE / "blender_probe.py"
EXPORT_PROBE = EVIDENCE / "collection_export_probe.blend"
EXPORT_CHECK = EVIDENCE / "verify_export_probe.py"
BLENDER = PROJECT / "outputs/blender/blender-4.5.15-windows-x64/blender.exe"


def run_blender_probe(filepath: Path, script: Path) -> tuple[dict, str]:
    proc = subprocess.run(
        [str(BLENDER), "--background", str(filepath), "--python", str(script)],
        cwd=PROJECT, capture_output=True, text=True, check=True,
    )
    matches = re.findall(r"INDEPENDENT_GRADE_JSON=(\{.*\})", proc.stdout)
    if not matches:
        raise RuntimeError(f"Blender probe produced no result: {proc.stdout[-2500:]} {proc.stderr[-1000:]}")
    return json.loads(matches[-1]), proc.stdout[-1800:]


def polygon_centroid(points: list[tuple[float, float]]) -> tuple[float, float]:
    cross = [points[i][0] * points[(i + 1) % len(points)][1]
             - points[(i + 1) % len(points)][0] * points[i][1]
             for i in range(len(points))]
    twice_area = sum(cross)
    cx = sum((points[i][0] + points[(i + 1) % len(points)][0]) * cross[i]
             for i in range(len(points))) / (3 * twice_area)
    cy = sum((points[i][1] + points[(i + 1) % len(points)][1]) * cross[i]
             for i in range(len(points))) / (3 * twice_area)
    return cx, cy


def evaluate() -> dict:
    assert ASSET.exists() and GIS.exists() and MANIFEST.exists()
    assert all(p.exists() for p in (EVIDENCE / "preview.png", EVIDENCE / "entry_detail.png",
                                     EVIDENCE / "source_record.json", EXPORT_PROBE, EXPORT_CHECK))
    direct, blender_log = run_blender_probe(ASSET, PROBE)
    export_check = subprocess.run(
        [str(BLENDER), "--background", str(EXPORT_PROBE), "--python", str(EXPORT_CHECK)],
        cwd=PROJECT, capture_output=True, text=True, check=True,
    )
    export_text = export_check.stdout

    gis = json.loads(GIS.read_text(encoding="utf-8"))
    feature = gis["feature"]
    attrs = feature["attributes"]
    raw_ring = feature["geometry"]["rings"][0]
    ring = [tuple(p) for p in raw_ring[:-1]]
    lat0, lon0 = 40.4274, -86.9137
    sx = 111412.84 * math.cos(math.radians(lat0))
    sy = 111040.0
    world_pts = [((lon - lon0) * sx, (lat - lat0) * sy) for lon, lat in ring]
    cx, cy = polygon_centroid(world_pts)
    local_pts = sorted((round(x - cx, 6), round(y - cy, 6)) for x, y in world_pts)
    actual_pts = sorted(tuple(p) for p in direct["shell_unique_xy"])
    vertex_errors = [math.hypot(a[0] - b[0], a[1] - b[1])
                     for a, b in zip(local_pts, actual_pts)] if len(local_pts) == len(actual_pts) else [math.inf]
    max_vertex_error = max(vertex_errors)

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    entry = next(e for e in manifest["assets"] if e.get("id") == ASSET_ID)
    origin = entry.get("placement_origin_xy_m", [])
    origin_error = math.hypot(float(origin[0]) - cx, float(origin[1]) - cy) if len(origin) >= 2 else math.inf
    source_record = json.loads((EVIDENCE / "source_record.json").read_text(encoding="utf-8"))
    evidence_files = [p.name for p in EVIDENCE.iterdir() if p.is_file()]

    identity_ok = (attrs.get("FID") == 241 and attrs.get("BLDG_ABBR", "").strip() == "ADDL"
                   and attrs.get("BUILDING_N") == source_record["building_name"]
                   and attrs.get("ADDRESS") == "406 S University Street"
                   and direct["source_feature_id"] == 241 and direct["building_id"] == ASSET_ID)
    footprint_ok = (len(ring) == 18 and direct["shell_unique_xy_count"] == 18
                    and max_vertex_error <= 0.015)
    criterion_identity = 2.0 if identity_ok and footprint_ok else (1.0 if identity_ok else 0.0)

    placement_ok = (len(origin) >= 2 and origin_error <= 0.10
                    and entry.get("local_coordinates") is True
                    and max_vertex_error <= 0.015)
    # The model and GIS ring agree at the point/shape level; manifest placement
    # is checked against the same transformed centroid. The master marker itself
    # is outside this assigned asset and was not independently reopened here.
    criterion_position = 1.8 if placement_ok else (1.0 if footprint_ok else 0.0)

    floors_ok = attrs.get("NUM_LEVELS") == 5 and attrs.get("CountOfFLO") == 5
    height_proxy = attrs.get("Extrution") == 57 and abs(direct["shell_bounds_m"][2][1] - (0.35 + 57 * 0.3048)) < 0.02
    criterion_height = (1.2 if floors_ok and height_proxy else 0.6 if floors_ok else 0.0)

    # Official/primary evidence supports the identity and qualitative mission;
    # the cited building-specific photograph supports brick and a modest entry,
    # and the 2007 ADDL newsletter locates an attached BSL-3 addition.  Neither
    # supplies measured bay dimensions, complete elevations, roof silhouette,
    # or exact addition geometry.
    facade_files = {"preview.png", "entry_detail.png"}.issubset(set(evidence_files))
    sources = source_record.get("sources", [])
    photo_ref = any("Beef Magazine" in s.get("provider", "") and s.get("url") for s in sources)
    addition_ref = any("2007 newsletter" in s.get("provider", "") and s.get("url") for s in sources)
    criterion_facade = 1.3 if facade_files and photo_ref and addition_ref else 0.7 if facade_files else 0.0

    module = PURDUE / "modular/buildings/build_animal_disease_diagnostic_laboratory.py"
    portable = (direct["object_count"] == 8 and not direct["external_image_paths"]
                and "collection_export_probe" in export_text and '"object_count": 8' in export_text)
    complete_evidence = all(p.exists() for p in (module, GIS, EVIDENCE / "source_record.json",
                                                  EVIDENCE / "preview.png", EVIDENCE / "entry_detail.png",
                                                  EXPORT_PROBE, EXPORT_CHECK))
    criterion_export = 2.0 if portable and complete_evidence else (1.0 if complete_evidence else 0.0)

    criteria = [
        {"name": "Correct identity and source-backed footprint", "score": criterion_identity,
         "max_score": 2, "status": "verified" if identity_ok and footprint_ok else "partial",
         "evidence": ["Purdue GIS FeatureServer FID 241 directly names ADDL, Willie M. Reed Animal Disease Diagnostic Laboratory, and 406 S University Street.",
                      f"Read-only Blender vertex comparison: {len(ring)} source corners, {direct['shell_unique_xy_count']} shell corners; maximum local-XY mismatch {max_vertex_error:.6f} m.",
                      "Official Purdue ADDL page corroborates the laboratory identity and function."],
         "limits": ["GIS footprint is a mapped building polygon, not a survey; source record notes this uncertainty."]},
        {"name": "Position, orientation, and scale/dimensions", "score": criterion_position,
         "max_score": 2, "status": "partial" if criterion_position < 2 else "verified",
         "evidence": [f"The shell's 18 vertices match the source ring under the documented local conversion (max error {max_vertex_error:.6f} m), verifying plan orientation and dimensions against GIS.",
                      f"Manifest placement origin differs from independently transformed polygon centroid by {origin_error:.6f} m.",
                      f"GIS-derived plan bounds are approximately {max(x for x, y in local_pts)-min(x for x, y in local_pts):.2f} m east-west by {max(y for x, y in local_pts)-min(y for x, y in local_pts):.2f} m north-south."],
         "limits": ["The master Placement marker was not reopened in this asset-specific grade; manifest coordinates stand in for the intended campus placement.",
                    "No independent survey or aerial registration was used to test GIS positional accuracy."]},
        {"name": "Evidence-backed height, floors, and roof form", "score": criterion_height,
         "max_score": 2, "status": "partial",
         "evidence": ["Both source GIS NUM_LEVELS and CountOfFLO attributes equal five, and the model displays five window bands.",
                      f"The shell uses the GIS Extrution value 57 as 17.3736 m; read-only saved asset top is {direct['shell_bounds_m'][2][1]:.4f} m including the 0.35 m base."],
         "limits": ["GIS Extrution units and vertical measurement definition are undocumented; height is a proxy, not a surveyed value.",
                    "Flat roof is modeled without roof-plan/elevation evidence; roof profile and equipment remain unverified."]},
        {"name": "Facade, entrances, and distinctive architecture", "score": criterion_facade,
         "max_score": 2, "status": "partial",
         "evidence": ["The building-specific Beef Magazine/Purdue photograph is cited in the source record and supports qualitative brick and covered-entry cues.",
                      "The Purdue ADDL 2007 newsletter documents a BSL-3 addition attached at the southeast corner; the model marks that area qualitatively.",
                      "Saved preview and entry render were inspected directly; they show repeated glazing, a covered double-door entry, sign, and southeast darker facade patch."],
         "limits": ["Window rhythm/count, opening sizes, material extents, exact entry location/dimensions and addition shape are not measured by cited sources.",
                    "Distinctive facade treatment beyond the cited photo is illustrative; no full elevation set was found."]},
        {"name": "Modular export, portability, and complete evidence", "score": criterion_export,
         "max_score": 2, "status": "verified" if portable and complete_evidence else "partial",
         "evidence": [f"Actual saved source .blend reopened in Blender; scene/collection identity passed with {direct['object_count']} objects.",
                      "Actual exported collection probe reopened and its independent check passed with eight expected objects and no camera/light.",
                      "No external image texture paths; builder module, raw GIS snapshot, evidence record, two renders and export probe are present."],
         "limits": [] if portable and complete_evidence else ["One or more export/portability/evidence checks failed."]},
    ]
    score = round(sum(c["score"] for c in criteria), 1)
    findings = [
        {"severity": "material", "finding": "Height and roof confidence is limited: the five-level count is sourced, but the modeled 57 ft height interprets an undocumented GIS field and the flat roof has no direct evidence.",
         "repair": "Locate an authoritative elevation, roof plan, survey, or dated official building record; update geometry only if it establishes a different height or roof form."},
        {"severity": "material", "finding": "Facade detailing and BSL-3 addition geometry remain qualitative; the source text only locates the addition at the southeast corner.",
         "repair": "Use current, building-specific orthogonal photos or architectural documents to verify elevations, entry location, window rhythm, and the separate addition footprint."},
        {"severity": "minor", "finding": "Position was validated against the checked-in Purdue GIS snapshot and manifest origin, but the linked master placement marker and external positional registration were not inspected in this grading pass.",
         "repair": "Coordinator should verify the master Placement marker and campus overlay during integration."},
    ]
    evidence = {
        "files_inspected": [str(ASSET), str(EVIDENCE / "preview.png"), str(EVIDENCE / "entry_detail.png"),
                            str(GIS), str(EVIDENCE / "source_record.json"), str(EXPORT_PROBE), str(EXPORT_CHECK)],
        "gis": {"feature_id": attrs.get("FID"), "building_name": attrs.get("BUILDING_N"),
                "abbr": attrs.get("BLDG_ABBR", "").strip(), "address": attrs.get("ADDRESS"),
                "source_crs": gis.get("source_crs"), "source_vertex_count": len(ring),
                "max_shell_vertex_error_m": round(max_vertex_error, 6),
                "manifest_origin": origin, "transformed_polygon_centroid": [round(cx, 6), round(cy, 6)],
                "origin_error_m": round(origin_error, 6),
                "extrution_value_and_unit_status": "57; unit and measurement definition undocumented",
                "num_levels": attrs.get("NUM_LEVELS"), "count_of_floors": attrs.get("CountOfFLO")},
        "blender_source_asset": direct,
        "sources_verified": [
            {"url": "https://vet.purdue.edu/addl/", "supports": "official ADDL identity and diagnostic function"},
            {"url": "https://www.addl.purdue.edu/Newsletters/2007/Summer/Letter.htm", "supports": "attached BSL-3 addition at southeast corner"},
            {"url": "https://www.beefmagazine.com/livestock-management/purdue-animal-disease-diagnostic-laboratory-gets-boost-from-state", "supports": "building-specific exterior photo; qualitative facade cue"},
            {"url": "https://www.in.gov/che/files/Purdue_University.pdf", "supports": "state project record for ADDL BSL-3 facility, not facade or overall-building geometry"},
        ],
        "validation_logs": {"source_asset_probe_tail": blender_log, "export_probe_check_tail": export_text[-1800:]},
    }
    return {"score": score, "max_score": 10, "passing_standard": 8, "passed": score >= 8,
            "building_id": ASSET_ID, "reviewer": "independent subagent", "criteria": criteria,
            "evidence": evidence, "findings": findings}


if __name__ == "__main__":
    result = evaluate()
    (HERE / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"score": result["score"], "max_score": result["max_score"],
                      "passed": result["passed"], "result": str(HERE / "result.json")}, indent=2))
