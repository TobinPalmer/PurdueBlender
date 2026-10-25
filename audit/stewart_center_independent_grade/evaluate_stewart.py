"""Independent, evidence-led Stewart Center grade for the saved asset probe.

This deliberately scores the saved asset from fresh-open geometry/material
inspection, GIS comparison, manifest facts, and source-backed visual review.
It does not edit the Blender asset or shared project data.
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def evaluate(reopen: dict, walls: dict, comparison: dict | None = None) -> dict:
    """Return criterion-level grade in the required 0–10 schema."""
    # The measured comparison numbers are independently recorded in this
    # function from the GIS polygon / Blender structural-wall overlay.
    comp = comparison or {
        "official_gis_feature": "Purdue campus MapServer layer 0, OBJECTID 615",
        "model_wall_bounds_m": [[-74.55, 60.25], [-49.925, 42.375], [0, 16.5]],
        "official_polygon_bounds_local_m": [
            [-74.1533514, 64.2650141], [-49.9649158, 42.0581421]
        ],
        "official_polygon_area_m2": 10197.47,
        "wall_rectangle_area_m2": 12442.04,
        "intersection_area_m2": 10157.15,
        "iou": 0.81372,
        "official_polygon_covered_by_wall_rectangle": 0.99605,
        "wall_rectangle_covered_by_official_polygon": 0.81636,
        "hausdorff_distance_m": 21.87,
        "method_uncertainty": (
            "Official 3857 service geometry requested in 4326, then transformed with the project's "
            "approximate local conversion around the manifest placement origin; not a survey-grade CRS. "
            "The model comparison is an axis-aligned envelope of the eight structural wall mesh bounds, "
            "not a traced union of wall polygons."
        ),
    }

    criteria = [
        {
            "name": "Correct identity and source-backed footprint",
            "score": 1.2,
            "max_score": 2,
            "evidence": (
                "The Purdue campus GIS feature identifies OBJECTID 615 as Stewart Center. "
                f"Its transformed footprint has about {comp['official_polygon_area_m2']:.0f} m² area. "
                f"The model's structural wall envelope covers {comp['official_polygon_covered_by_wall_rectangle']:.1%} "
                f"of that polygon, but envelope IoU is {comp['iou']:.3f}: the model is a broad rectangle "
                "where the GIS outline has substantial recesses and stepped edges."
            ),
            "status": "partially verified",
        },
        {
            "name": "Position, orientation, and scale/dimensions",
            "score": 1.6,
            "max_score": 2,
            "evidence": (
                "Manifest uses a local-coordinate asset and places its origin at [91.05, -253.375] m. "
                "Fresh-open probe shows the asset root at identity transform and local origin. "
                "The structural envelope and GIS polygon bounds agree closely on the west, north, and south "
                "extents; the model extends about 4 m farther east. Orientation is consistent with the campus "
                "map overlay. The master placement marker was not reopened in this independent asset grade."
            ),
            "status": "mostly verified; master link not checked",
        },
        {
            "name": "Evidence-backed height, floors, and roof form",
            "score": 1.0,
            "max_score": 2,
            "evidence": (
                "Purdue archival material supports three floors in the central part of the complex. "
                "The model probe reports overall height 22.5 m and structural walls to 16.5 m, with a flat "
                "roof and three block-like rooftop forms. No authoritative elevation or roof plan was found "
                "to verify those heights or rooftop shapes, and the source notes that Stewart Center incorporates "
                "the former library and reconstructed Fowler Hall, which are not legible as distinct volumes here."
            ),
            "status": "floor count source-supported; height and roof unverified",
        },
        {
            "name": "Facade, entrances, and distinctive architecture",
            "score": 0.7,
            "max_score": 2,
            "evidence": (
                "Fresh Blender renders show red-brown wall material, repeated window/grid strips, horizontal "
                "bands, and a simple entry treatment. The facade reads as a generic rectangular box. Available "
                "Purdue imagery shows a more distinctive columned/stone-framed entrance and broad stair; the "
                "official archives describe the incorporated library/Fowler Hall composition and a mural above "
                "the HSSE library entrance. These distinctive features are not represented clearly in the asset."
            ),
            "status": "partially represented",
        },
        {
            "name": "Modular export, portability, and complete evidence",
            "score": 1.5,
            "max_score": 2,
            "evidence": (
                f"Fresh reopen confirms collection {reopen['collection_name']} in scene {reopen['scene']}, "
                f"with {reopen['collection_object_count']} objects, a zeroed root, and "
                f"{len(reopen['missing_external_images'])} missing external image paths / "
                f"{len(reopen['materialless_meshes'])} materialless meshes. The asset is self-contained "
                "with respect to image textures. Evidence is incomplete: no dimensioned elevation/roof "
                "evidence or pre-existing source record was found for this building, and the master link was "
                "not checked."
            ),
            "status": "asset portability verified; provenance/evidence incomplete",
        },
    ]

    evidence = {
        "asset": str((HERE.parent.parent / "modular" / "buildings" / "stewart_center.blend").resolve()),
        "fresh_open_probe": str((HERE / "reopen_probe.json").resolve()),
        "structural_wall_probe": str((HERE / "structural_wall_probe.json").resolve()),
        "gis_snapshot": str((HERE / "purdue_gis_feature_615.json").resolve()),
        "footprint_overlay": str((HERE / "footprint_overlay.png").resolve()),
        "renders": [
            str((HERE / "south_oblique.png").resolve()),
            str((HERE / "north_oblique.png").resolve()),
            str((HERE / "top.png").resolve()),
        ],
        "asset_sha256": reopen["sha256"],
        "measurement": comp,
        "sources": [
            {
                "url": "https://mapsweb.lib.purdue.edu/arcgis/rest/services/Purdue/campus/MapServer/0",
                "provider": "Purdue University campus GIS",
                "feature": "layer 0, OBJECTID 615, ABBR STEW, Name Stewart Center",
                "retrieved": "2026-10-25",
                "source_crs": "EPSG:3857; requested as EPSG:4326; project-local approximate conversion applied",
                "method": "feature polygon overlaid with the axis-aligned bounds of named structural wall meshes",
                "uncertainty": comp["method_uncertainty"],
            },
            {
                "url": "https://archives.lib.purdue.edu/agents/corporate_entities/548?filter_fields%5B%5D=primary_type&filter_values%5B%5D=accession",
                "provider": "Purdue University Archives and Special Collections",
                "feature": "Stewart Center corporate entity entry",
                "retrieved": "2026-10-25",
                "source_date": "construction 1954–1958; renamed in 1972",
                "method": "used for documented building history and central-part floor count",
                "uncertainty": "Not a dimensioned elevation or complete footprint source.",
            },
            {
                "url": "https://roadschool.purdue.edu/maps/Stewart%20Center%20Maps.html",
                "provider": "Purdue Road School",
                "feature": "Stewart Center floor maps (first, second, and third floors)",
                "retrieved": "2026-10-25",
                "method": "floor labels and functional zones cross-check",
                "uncertainty": "Plans are not dimensioned building elevations; cannot verify height or roof.",
            },
            {
                "url": "https://events.purdue.edu/stewart_center",
                "provider": "Purdue University events site",
                "feature": "Stewart Center image",
                "retrieved": "2026-10-25",
                "method": "visual facade/entrance comparison",
                "uncertainty": "Single exterior view does not establish all facades or geometry dimensions.",
            },
            {
                "url": "https://blogs.lib.purdue.edu/news/2017/08/27/from-the-archives-a-beginning/",
                "provider": "Purdue Libraries and School of Information Studies, From the Archives",
                "feature": "Memorial Center / Stewart Center construction history",
                "retrieved": "2026-10-25",
                "method": "documented composition and mural cross-check",
                "uncertainty": "Historical account is not a dimensioned architectural plan.",
            },
        ],
    }

    findings = [
        "Trace the structural wall geometry to the stepped GIS footprint, including the pronounced recesses and east-side projections; the current wall envelope is oversized and too rectangular.",
        "Separate major building volumes where the floor plans and archival history support the former library and reconstructed Fowler Hall; avoid representing the entire complex as one uniform block.",
        "Improve and source-check the principal columned/stone-framed entrance and broad stair, plus the library entrance and mural location; add additional facade rhythm from current oblique photographs.",
        "Find authoritative elevations, roof plans, or measured height data before treating the 16.5 m wall top and 22.5 m overall height as verified; label them estimates until sourced.",
        "Reopen the master and verify the single collection instance against the manifest origin/orientation, and add a building-specific evidence record with source dates, CRS, measurement steps, previews, and limitations.",
    ]
    score = round(sum(c["score"] for c in criteria), 2)
    return {
        "score": score,
        "max_score": 10,
        "criteria": criteria,
        "evidence": evidence,
        "findings": findings,
    }


if __name__ == "__main__":
    reopen = json.loads((HERE / "reopen_probe.json").read_text(encoding="utf-8"))
    walls = json.loads((HERE / "structural_wall_probe.json").read_text(encoding="utf-8"))
    result = evaluate(reopen, walls)
    (HERE / "independent_grade.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps({"score": result["score"], "max_score": result["max_score"]}, indent=2))
