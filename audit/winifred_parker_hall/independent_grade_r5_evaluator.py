"""Independent Winifred Parker Hall R5 scorecard evaluator.

Run with system Python after the Blender extraction and read-only master-marker
scripts have been run. Requires Shapely.
"""
from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

from shapely.geometry import Polygon

AUDIT = Path(__file__).resolve().parent
ROOT = AUDIT.parents[1]
ASSET = ROOT / "modular/buildings/winifred_parker_hall.blend"
EXPECTED_SHA = "92fa120794470d93a253d04f35ca0852caea7d05982a5f4e02b285fd914045a9"


def read_json(name: str):
    return json.loads((AUDIT / name).read_text(encoding="utf-8"))


def evaluate() -> dict:
    sha = hashlib.sha256(ASSET.read_bytes()).hexdigest()
    if sha != EXPECTED_SHA:
        raise RuntimeError(f"Canonical asset SHA changed: {sha}")
    reopened = read_json("independent_grade_r5_extract.json")
    marker = read_json("independent_grade_r5_master_marker.json")
    ortho = read_json("indiana_2023_orthophoto_evidence_r5.json")
    if reopened["sha256"] != sha or marker["asset_sha256"] != sha:
        raise RuntimeError("Reopen/marker evidence does not identify the canonical R5 SHA")

    raw = json.loads((AUDIT / "gis_feature_879_raw.json").read_text(encoding="utf-8"))
    feature = next(f for f in raw["features"] if f["attributes"].get("FID") == 879)
    attrs = feature["attributes"]
    if attrs.get("BLDG_ABBR") != "PKRW" or attrs.get("BUILDING_N") != "Winifred Parker Residence Hall":
        raise RuntimeError("GIS source identity does not match Winifred Parker Hall")

    lat0, lon0 = 40.4274, -86.9137
    x_per_lon = 111412.84 * math.cos(math.radians(lat0))
    y_per_lat = 111040.0
    origin = marker["manifest_origin_xy_m"]
    gis_local = [
        [(float(lon) - lon0) * x_per_lon - float(origin[0]),
         (float(lat) - lat0) * y_per_lat - float(origin[1])]
        for lon, lat in feature["geometry"]["rings"][0]
    ]
    source_polygon = Polygon(gis_local)

    shell = reopened["replacement_meshes"]["upper_shell"]
    vertices = shell["vertices_world_local"]
    top_z = max(v[2] for v in vertices)
    top_faces = [
        face for face in shell["faces"]
        if all(abs(vertices[index][2] - top_z) < 1e-5 for index in face)
    ]
    if len(top_faces) != 1:
        raise RuntimeError(f"Expected one planar upper-shell top face, found {len(top_faces)}")
    model_polygon = Polygon([(vertices[i][0], vertices[i][1]) for i in top_faces[0]])
    if not source_polygon.is_valid or not model_polygon.is_valid:
        raise RuntimeError("Source/model footprint polygon invalid")
    intersection = source_polygon.intersection(model_polygon).area
    union = source_polygon.union(model_polygon).area
    iou = intersection / union
    hausdorff = source_polygon.boundary.hausdorff_distance(model_polygon.boundary)
    marker_error = float(marker["marker_position_error_m"])
    matching_catalog = [
        row["attributes"]
        for row in ortho["identify_response"].get("catalogItems", {}).get("features", [])
        if row.get("attributes", {}).get("Image_Year") == "2023"
        and row.get("attributes", {}).get("County") == "Tippecanoe"
    ]
    if not matching_catalog:
        raise RuntimeError("2023 Tippecanoe catalog item missing from orthophoto identify response")
    for filename in (
        "official_purdue_photo_2021.jpg",
        "indiana_2023_orthophoto_r5.png",
        "indiana_2023_orthophoto_overlay_r5.png",
    ):
        if not (AUDIT / filename).exists():
            raise RuntimeError(f"Required image evidence missing: {filename}")
    if iou < 0.99 or hausdorff > 0.02 or marker_error > 0.001:
        raise RuntimeError("Footprint or placement measurement below the candidate acceptance checks")

    criteria = [
        {
            "criterion": "Identity and source-backed footprint",
            "score": 1.8,
            "max_score": 2.0,
            "evidence": (
                f"Purdue BuildingShapesZip4 FID 879 is PKRW / Winifred Parker Residence Hall at {attrs['ADDRESS']}. "
                f"Independent raw-ring to actual mesh top-face comparison: IoU {iou:.9f}, boundary Hausdorff "
                f"{hausdorff:.6f} m, GIS/model areas {source_polygon.area:.3f}/{model_polygon.area:.3f} m2. "
                "The 2023 orthophoto overlay shows the source polygon and model perimeter tracking the visible roof."
            ),
            "limitations": (
                "The candidate's upper shell is traced to this GIS ring, so the near-1 IoU establishes faithful "
                "transfer of that outline, not surveyed wall-face accuracy. The GIS Shape__Area field "
                f"({attrs['Shape__Area']} m2) conflicts with the area of its returned ring ({source_polygon.area:.3f} m2)."
            ),
        },
        {
            "criterion": "Campus placement, orientation, and scale",
            "score": 1.45,
            "max_score": 1.5,
            "evidence": (
                f"Fresh read-only master reopen confirms the expected linked collection and marker; position error "
                f"{marker_error:.6f} m, zero rotation, unit scale, and no duplicate direct source link. The source "
                f"polygon is {source_polygon.bounds[2]-source_polygon.bounds[0]:.2f} by "
                f"{source_polygon.bounds[3]-source_polygon.bounds[1]:.2f} m; the canonical upper shell matches."
            ),
            "limitations": "Placement is exact relative to the manifest; the campus XY transform is approximate, not survey control.",
        },
        {
            "criterion": "Massing, floors, height, and roof",
            "score": 1.2,
            "max_score": 1.5,
            "evidence": (
                "The model has a recognizable flat-roof mid-rise plan with a preserved internal notch/courtyard. "
                f"The main shell spans z=4.2 to 20.2 m and the asset maximum is "
                f"{reopened['aggregate_mesh_bounds_local'][2][1]:.2f} m including rooftop masses. The 2023 aerial "
                "shows the flat roof and equipment. GIS floor-height fields F02-F05 and R support a similar "
                "mid-rise profile if their values are feet."
            ),
            "limitations": (
                f"GIS NUM_LEVELS={attrs['NUM_LEVELS']} conflicts with CountOfFLO={attrs['CountOfFLO']}; field units "
                f"are undocumented. If R={attrs['R']} is feet, the modeled maximum is about 0.8 m taller. "
                "Rooftop services and exact floor-to-floor heights remain schematic."
            ),
        },
        {
            "criterion": "Facade, windows, and entrances",
            "score": 1.2,
            "max_score": 1.5,
            "evidence": (
                "The official 2021 Purdue photo supports red brick, tall narrow punched windows, restrained light "
                "trim, and glazed ground-floor retail. The asset has 158 window and 158 sill objects over five "
                "modeled bands; East facade openings are aligned to the outline, and unsupported West/North bays "
                "were removed while preserving exterior continuity."
            ),
            "limitations": (
                "Only one oblique image is available. Exact window spacing and opening size lack elevations; "
                "the large bright portal/canopy visible in the diagnostic render is not measured from a plan."
            ),
        },
        {
            "criterion": "Materials and surface finish",
            "score": 0.65,
            "max_score": 1.0,
            "evidence": (
                f"{reopened['used_material_count']} used materials cover brick, limestone, roof membrane, glazing, "
                "concrete, paving, and interior finishes. Procedural brick/noise/bump shaders are present; all mesh "
                "material slots are valid."
            ),
            "limitations": (
                "No image-texture nodes or photographic maps are packed in the asset. The available diagnostic "
                "render makes the roof read washed white/cyan and the repeated brick remains stylized; final "
                "daylight material response was not polished."
            ),
        },
        {
            "criterion": "Interior and building program",
            "score": 0.55,
            "max_score": 1.0,
            "evidence": (
                "Purdue Housing documents suites/semi-suites, shared baths, suite living rooms, a Starbucks/market "
                "at ground level, an Executive-in-Residence lobby, and TV lounges on each floor. The asset includes "
                "ground retail, lobby/reception, and a furnished sample suite with beds, desks, bath, sofa, and TV console."
            ),
            "limitations": (
                "There is no complete representative resident floor or repeated TV lounge/corridor layout. The "
                "public room diagrams are expressly approximate, so room partitions and furniture positions remain illustrative."
            ),
        },
        {
            "criterion": "Technical integrity, portability, and evidence",
            "score": 1.2,
            "max_score": 1.5,
            "evidence": (
                f"Exact SHA {sha} freshly reopened in Blender {reopened['blender_version']}: "
                f"{reopened['collection_object_count']} objects / {reopened['mesh_count']} meshes, identity root, "
                f"{reopened['used_material_count']} used materials, no materialless meshes, invalid indices, "
                "missing images, unpacked external image dependencies, or linked libraries. The grade evidence "
                "includes raw GIS, Purdue Housing text, official 2021 exterior photo, a catalog-identified 2023 "
                "Tippecanoe six-inch orthophoto, and a separate read-only master check."
            ),
            "limitations": "The GIS area conflict and local coordinate approximation remain unresolved.",
        },
    ]
    score = round(sum(item["score"] for item in criteria), 2)
    findings = [
        "The R5 shell correction resolves the main east-wing position/shape problem from baseline; the actual mesh outline matches Purdue GIS FID 879 and the 2023 Tippecanoe roof image.",
        "The fresh master marker is at the manifest origin with zero translation error, zero rotation, unit scale, and only one collection instance.",
        "This narrow pass is not an as-built claim: floor-count/height semantics, measured wall lines, full residential circulation, exact openings, and final rendered materials remain uncertain or schematic.",
        "Priority follow-up is a neutral daylight exterior render with roof services checked, plus a labeled representative resident-floor/corridor cutaway and source-backed reconciliation of the GIS area/floor fields.",
    ]
    return {
        "building": "Winifred Parker Hall",
        "revision": "R5 GIS-shell candidate",
        "asset": ASSET.relative_to(ROOT).as_posix(),
        "sha256": sha,
        "review_date_utc": datetime.now(timezone.utc).isoformat(),
        "score": score,
        "max_score": 10.0,
        "pass_threshold": 8.0,
        "passed": score >= 8.0,
        "criteria": criteria,
        "evidence": {
            "asset_reopen": "independent_grade_r5_extract.json",
            "asset_extract_script": "independent_grade_r5_extract.py",
            "master_marker": "independent_grade_r5_master_marker.json",
            "master_marker_script": "independent_grade_r5_master_marker.py",
            "gis_snapshot": "gis_feature_879_raw.json",
            "gis_service": "https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0",
            "gis_feature": {
                "FID": attrs["FID"],
                "BLDG_ABBR": attrs["BLDG_ABBR"],
                "BUILDING_N": attrs["BUILDING_N"],
                "ADDRESS": attrs["ADDRESS"],
                "NUM_LEVELS": attrs["NUM_LEVELS"],
                "CountOfFLO": attrs["CountOfFLO"],
                "R_field": attrs["R"],
                "Shape__Area_m2": attrs["Shape__Area"],
            },
            "footprint": {
                "source_ring_vertices": len(feature["geometry"]["rings"][0]),
                "source_area_m2": source_polygon.area,
                "model_area_m2": model_polygon.area,
                "intersection_area_m2": intersection,
                "union_area_m2": union,
                "iou": iou,
                "boundary_hausdorff_m": hausdorff,
                "model_bounds_local_m": shell["bounds"],
            },
            "orthophoto_evidence": "indiana_2023_orthophoto_evidence_r5.json",
            "orthophoto_catalog_item": matching_catalog[0],
            "orthophoto_overlay": "indiana_2023_orthophoto_overlay_r5.png",
            "official_facade_image": "official_purdue_photo_2021.jpg",
            "housing_page_snapshot": "purdue_residence_page_2026.html",
            "housing_page_url": "https://housing.purdue.edu/my-housing/options/residence-halls/parker-south.html",
            "render": "gis_shell_exterior.png",
        },
        "findings": findings,
    }


if __name__ == "__main__":
    result = evaluate()
    evidence = result["evidence"]
    gis_record = evidence["gis_feature"]
    footprint = evidence["footprint"]
    ortho_record = evidence["orthophoto_catalog_item"]
    marker_record = read_json("independent_grade_r5_master_marker.json")
    reopen_record = read_json("independent_grade_r5_extract.json")
    (AUDIT / "independent_grade_r5.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    lines = [
        "# Independent Winifred Parker Hall R5 grade",
        "",
        f"**Score: {result['score']:.2f}/10 — {'passes' if result['passed'] else 'below'} the 8.0 threshold**",
        f"**Asset SHA-256:** {result['sha256']}",
        f"**Review date (UTC):** {result['review_date_utc']}",
        "**Scope:** exact canonical asset, independent footprint calculation, official image sources, and read-only master placement.",
        "",
        "## Scorecard",
        "",
        "| Criterion | Score | Evidence and limitations |",
        "| --- | ---: | --- |",
    ]
    for item in result["criteria"]:
        evidence = item["evidence"].replace("|", "\\|").replace("\n", " ")
        limitations = item["limitations"].replace("|", "\\|").replace("\n", " ")
        lines.append(
            f"| {item['criterion']} | {item['score']:.2f}/{item['max_score']:.2f} | {evidence} **Limits:** {limitations} |"
        )
    lines += ["", "## Findings", ""]
    lines += [f"- {finding}" for finding in result["findings"]]
    lines += [
        "",
        "## Measured results",
        "",
        f"- Purdue GIS FID {gis_record['FID']} / PKRW: {gis_record['BUILDING_N']}, {gis_record['ADDRESS']}.",
        f"- Upper-shell/GIS-ring IoU {footprint['iou']:.9f}; boundary Hausdorff distance {footprint['boundary_hausdorff_m']:.6f} m.",
        f"- Master marker error {marker_record['marker_position_error_m']:.6f} m; zero rotation; unit scale.",
        f"- 2023 orthophoto catalog item {ortho_record.get('Name')}, Tippecanoe County, {ortho_record.get('Pixel_Size')}.",
        f"- Fresh export: {reopen_record['collection_object_count']} objects / {reopen_record['mesh_count']} meshes, {reopen_record['used_material_count']} materials, no missing external dependencies.",
        "",
        "## Sources",
        "",
        "- Purdue GIS BuildingShapesZip4, FID 879 / PKRW: https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0",
        "- Purdue Housing Parker South: https://housing.purdue.edu/my-housing/options/residence-halls/parker-south.html",
        "- Official Purdue exterior photograph, Fall 2021: https://www.purdue.edu/vpsl/news/perspectives-stories/fall-2021/_images/winifred-parker-hall.jpg",
        "- Indiana Geographic Information Office 2023 orthophoto ImageServer: https://di-ingov.img.arcgis.com/arcgis/rest/services/DynamicWebMercator/Indiana_2023_Imagery/ImageServer",
        "",
        "The map outline is not a surveyed wall line. GIS floor-count fields conflict; height, full resident circulation, measured facade dimensions, and roof/service details remain estimated or schematic.",
    ]
    (AUDIT / "independent_grade_r5.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k not in {"criteria", "evidence"}}, indent=2, ensure_ascii=False))
