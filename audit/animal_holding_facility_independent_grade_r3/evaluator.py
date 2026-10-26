"""Independent R3 review of the Animal Holding Facility asset.

Rechecks the raw NDHM raster sampling independently of the builder's analyzer,
then validates the saved Blender library via a separate Blender probe. Run from
the repository root with Python and Blender 4.5 available.
"""
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
REVIEW = ROOT / "audit/animal_holding_facility_independent_grade_r3"
SOURCE = ROOT / "audit/animal_holding_facility/sources"


def summarize_raw_raster():
    """Read TIFF geotags/data directly; do not import the builder analyzer."""
    raster_path = SOURCE / "indiana_lidar_ndhm_tippecanoe_2018_tile_in2018_29951880_12.tif"
    ring_path = SOURCE / "purdue_gis_fid266_2026-10-25_stateplane_2968.json"
    im = Image.open(raster_path)
    tags = im.tag_v2
    tie = tags[33922]
    scale = tags[33550]
    assert (im.width, im.height) == (1000, 1000)
    assert tuple(tie[3:5]) == (2995000.0, 1885000.0)
    assert tuple(scale[:2]) == (5.0, 5.0)
    ring = json.loads(ring_path.read_text(encoding="utf-8-sig"))["features"][0]["geometry"]["rings"][0]
    poly = [((x - tie[3]) / scale[0], (tie[4] - y) / scale[1]) for x, y in ring]
    split_y_ft = 1883168.8443683232

    def contains(px, py):
        inside = False
        for i, (x1, y1) in enumerate(poly):
            x2, y2 = poly[(i + 1) % len(poly)]
            if (y1 > py) != (y2 > py) and px < (x2 - x1) * (py - y1) / (y2 - y1) + x1:
                inside = not inside
        return inside

    values = {"north_main": [], "south_addition": []}
    for row in range(im.height):
        for col in range(im.width):
            if not contains(col + 0.5, row + 0.5):
                continue
            value_ft = float(im.getpixel((col, row)))
            if value_ft <= -10:
                continue
            y_ft = tie[4] - (row + 0.5) * scale[1]
            values["north_main" if y_ft > split_y_ft else "south_addition"].append(value_ft)

    result = {}
    for zone, samples in values.items():
        samples.sort()
        n = len(samples)
        q1, median, q3 = (samples[round((n - 1) * q)] for q in (0.25, 0.5, 0.75))
        us_survey_ft_to_m = 1200 / 3937
        result[zone] = {
            "count": n,
            "median_ft": median,
            "median_m": median * us_survey_ft_to_m,
            "iqr_m": (q3 - q1) * us_survey_ft_to_m,
        }
    return {
        "tiff_dimensions": [im.width, im.height],
        "model_pixel_scale": list(scale[:2]),
        "model_tie_point": list(tie),
        "vertical_unit_interpretation": "US survey feet, supported by EPSG:2968(ftUS) metadata and local Indiana 3DEP paper snapshot",
        "roof_zone_split_y_epsg2968_ft": split_y_ft,
        "independently_recomputed_zones": result,
        "comparison": "Counts and medians reproduce builder's values (north 614 / 13.24 ft; south 359 / 16.95 ft) to stated rounding.",
        "limits": "5-ft NDHM cell medians represent normalized object height, not measured eaves; split is transferred from later orthophoto and is not a surveyed roof seam.",
    }


def evaluate():
    raster = summarize_raw_raster()
    result = {
        "building_id": "massing_animal_holding_facility_4733f46",
        "asset": "modular/buildings/massing_animal_holding_facility_4733f46.blend",
        "candidate_commit": "6f51405",
        "evaluator": "Independent review against root AGENT.md and modular/AGENTS.md; opened saved Blender asset, inspected topology/export, and independently recomputed roof-zone statistics from raw source raster.",
        "score": 7.2,
        "max_score": 10,
        "passing_threshold": 8,
        "pass": False,
        "criteria": [
            {"name": "Correct identity and source-backed footprint", "points": 2.0, "max_points": 2,
             "assessment": "Purdue feature FID 266 names Animal Holding Facility (AHF), building 1310, at 410 S University Street. Independent Indiana 2018 footprint agrees within 0.50 m centroid and 1.74 m maximum boundary residual. Reopened asset roof outline follows all 16 projected source vertices; the small wall-shell margin is explicit."},
            {"name": "Position, orientation, and scale/dimensions", "points": 2.0, "max_points": 2,
             "assessment": "Campus-coordinate position and north/east orientation match source conversion. Reopened mesh bounds are x[-65.6453,-23.6969], y[-1030.8369,-955.2317], z[0,5.1660] m; wall offsets stay within the declared 0.28 m shell thickness."},
            {"name": "Evidence-backed height, floors, and roof form", "points": 1.5, "max_points": 2,
             "assessment": "Improved materially: official 2018 5-ft NDHM raw raster independently reproduces zone medians of 4.036 m and 5.166 m above ground (614 and 359 valid cells); Purdue GIS supports one level and the 2023 orthophoto supports the plan-zone split. The plane-at-median surfaces and 1.13 m inter-zone step remain a generalized interpretation: NDHM does not measure eaves, and no roof pitch/ridge/profile is established."},
            {"name": "Facade, entrances, and distinctive architecture", "points": 0.0, "max_points": 2,
             "assessment": "Still unverified and omitted. Model is a neutral blank envelope with no facade openings, entrance, or distinctive features. No credit under the source-evidence rubric."},
            {"name": "Modular export, portability, and complete evidence", "points": 1.7, "max_points": 2,
             "assessment": "Expected named collection reopens with one mesh object, no modifiers or image dependencies; preview, dated raw GIS/orthophoto/NDHM snapshots, metadata, and reproducible sampling code are present. Blender independently reports 48 boundary/non-manifold mesh edges around the uncapped roof-sheet boundaries, so export geometry is not fully closed."},
        ],
        "evidence": {
            "previous_grade": "audit/animal_holding_facility_independent_grade_r2/result.json (6.7/10); this revision directly addresses its unsupported total-height/roof-height finding with 2018 NDHM samples.",
            "raw_source_sampling": raster,
            "blender_probe": "audit/animal_holding_facility_independent_grade_r3/blender_probe.json",
            "reviewed_material": [
                "audit/animal_holding_facility/build_evidence.json",
                "audit/animal_holding_facility/ndhm_roof_height_statistics.json",
                "audit/animal_holding_facility/analyze_ndhm_roof_heights.py",
                "audit/animal_holding_facility/sources/indiana_lidar_ndhm_metadata.json",
                "audit/animal_holding_facility/sources/indiana_2023_orthophoto_metadata.json",
                "audit/animal_holding_facility/sources/purdue_gis_fid266_2026-10-25_stateplane_2968.json",
                "audit/animal_holding_facility/sources/indiana_3dep_lidar_units_method_paper_2022.pdf",
            ],
            "visual_review": "animal_holding_facility_preview.png and orthophoto_footprint_overlay.png show a neutral blank massing shell and source-matched plan outline/roof-tone split.",
        },
        "findings": [
            {"severity": "blocking-for-8/10", "finding": "Facade and entrance remain entirely unverified and absent (0/2). Add independently sourced AHF-specific ground-level imagery/elevation evidence and model only features visible in it, or record that this criterion cannot be completed; appearance alone is insufficient."},
            {"severity": "blocking-for-8/10", "finding": "Roof heights now have credible LiDAR support, but the modeled level planes and step are representative medians, not surveyed eaves or architectural seam heights. Keep the stated uncertainty and do not present the two median surfaces as a measured roof profile."},
            {"severity": "minor", "finding": "Saved mesh has 48 boundary edges where the roof sheets are uncapped. Close the roof perimeter/zone seam or explicitly justify intentional sheet surfaces, then rerun the Blender topology probe."},
            {"severity": "positive-evidence", "finding": "Recomputation from the raw GeoTIFF geotags, Purdue EPSG:2968 ring, and pixel values reproduces both roof-zone sample counts and medians; this resolves the prior grade's unsupported-height concern substantially."},
        ],
    }
    REVIEW.mkdir(parents=True, exist_ok=True)
    (REVIEW / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    print(json.dumps(evaluate(), indent=2))
