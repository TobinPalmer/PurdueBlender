"""Independent rubric evaluator for Alpha Gamma Delta, Beta Xi, Purdue."""
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "audit" / "alpha_gamma_delta"
ASSET = bpy.data.filepath


def evaluate():
    gis = json.loads((AUDIT / "source_feature_757_raw.json").read_text(encoding="utf-8-sig"))
    operator = json.loads((AUDIT / "source_observations.json").read_text(encoding="utf-8-sig"))
    saved = json.loads((AUDIT / "reopen_validation.json").read_text(encoding="utf-8-sig"))
    source = gis["attributes"]
    assert source["FID"] == 757 and source["BLDG_ABBR"] == "SOAGD"
    assert source["BUILDING_N"] == "Alpha Gamma Delta"

    collection_name = "Asset_massing_house_301841608_d56a4c4"
    collection = bpy.data.collections.get(collection_name)
    assert collection is not None and len(collection.objects) == 1
    obj = collection.objects[0]
    assert obj.name == "House_301841608" and obj.type == "MESH"
    assert all(abs(v) < 1e-6 for v in (*obj.location, *obj.rotation_euler))
    assert all(abs(v-1.0) < 1e-6 for v in obj.scale)

    ring = gis["geometry"]["rings"][0]
    if ring[0] == ring[-1]:
        ring = ring[:-1]
    lat0, lon0 = 40.4274, -86.9137
    expected = [
        Vector(((lon-lon0)*111412.84*math.cos(math.radians(lat0)), (lat-lat0)*111040.0, 0.0))
        for lon, lat in ring
    ]
    base = [v.co.copy() for v in obj.data.vertices if abs(v.co.z) < 1e-5]
    errors = [min((candidate-p).length for candidate in base) for p in expected]
    max_error = max(errors)
    bounds = [
        [round(min(v.co[i] for v in obj.data.vertices), 6), round(max(v.co[i] for v in obj.data.vertices), 6)]
        for i in range(3)
    ]
    external = [
        image.filepath for image in bpy.data.images
        if image.source == "FILE" and image.filepath and not image.packed_file
    ]
    assert saved["reopened_in_background_blender"] and saved["passed"]
    assert saved["collection_object_count"] == 1
    assert max_error < 1e-4

    # The criterion scores reflect source quality and geometry evidence, not mesh density.
    criteria = [
        {
            "name": "Correct identity and source-backed footprint",
            "score": 1.9,
            "max_score": 2,
            "evidence": [
                "Purdue GIS feature FID 757 identifies Alpha Gamma Delta (SOAGD) at 1010 David Ross Road.",
                f"The saved mesh base contains all {len(expected)} distinct transformed source-ring vertices; independently recomputed maximum residual is {max_error:.9f} m.",
                "The housing operator independently lists the Beta Xi property at the same address."
            ],
            "uncertainty": "The campus-map polygon is not a certified survey and its structural-edge convention and positional tolerance are unpublished."
        },
        {
            "name": "Position, orientation, and scale/dimensions",
            "score": 1.7,
            "max_score": 2,
            "evidence": [
                "The footprint vertices match the Purdue WGS 84 polygon after the documented local-campus transform.",
                f"Saved mesh bounds are X {bounds[0]} m, Y {bounds[1]} m, Z {bounds[2]} m.",
                "The wall shell preserves source orientation and scale."
            ],
            "uncertainty": "No source records georeference the front door or porch; the selected west-facing side is a builder estimate."
        },
        {
            "name": "Evidence-backed height, floors, and roof form",
            "score": 1.2,
            "max_score": 2,
            "evidence": [
                "The Meyer Najem project description calls the house two stories, consistent with the modeled two levels.",
                "The GIS NUM_LEVELS field reports 1, so the level-count conflict remains unresolved.",
                "A stylized exact-address illustration supports a pitched roof silhouette, but the model's 7.6 m eaves, 10.0 m ridge, and compact central gable are not dimensioned by a plan."
            ],
            "uncertainty": "No measured elevations or roof plan were found; roof profile and absolute height are estimates."
        },
        {
            "name": "Facade, entrances, and distinctive architecture",
            "score": 1.0,
            "max_score": 2,
            "evidence": [
                "The custom illustration depicts a two-story cream house with pitched roof, columned entry, and red double doors.",
                "The model includes repeated windows, a portico, red door, front steps, cream walls, and a central gable.",
                "Visual inspection of preview_detail.png shows the intended elements, though the gable reads as a small central roof block and the facade rhythm is schematic."
            ],
            "uncertainty": "The illustration is stylized rather than a measured photo, and no georeferenced facade reference confirms the door side, proportions, materials, or window rhythm."
        },
        {
            "name": "Modular export, portability, and complete evidence",
            "score": 2.0,
            "max_score": 2,
            "evidence": [
                f"Blender reopened {Path(ASSET).name} with exactly one mesh object in {collection_name} and identity transforms.",
                f"The asset contains {len(obj.data.vertices)} vertices and {len(obj.data.polygons)} faces, with {len(external)} external unpacked images.",
                "A dedicated builder, raw GIS feature, structured source notes, validation, and preview are present."
            ],
            "uncertainty": "No portability issue was found in the assigned library."
        }
    ]
    return {
        "score": round(sum(item["score"] for item in criteria), 1),
        "max_score": 10,
        "criteria": criteria,
        "evidence": {
            "asset": "modular/buildings/massing_house_301841608_d56a4c4.blend",
            "source_paths": [
                "audit/alpha_gamma_delta/source_feature_757_raw.json",
                "audit/alpha_gamma_delta/source_observations.json"
            ],
            "reopen_validation": "audit/alpha_gamma_delta/reopen_validation.json",
            "preview": "audit/alpha_gamma_delta/preview_detail.png",
            "direct_source_checks": [
                "Fraternity Housing Corporation page lists Beta Xi at 1010 David Ross Road, year built 1965, capacity 74, and 23,288 square feet.",
                "Meyer Najem page identifies a 5,000-square-foot renovation and calls the project two stories; it does not establish total-building area or elevations.",
                "Two Tulips product page identifies the illustration as the house at 1010 David Ross Road; it is a stylized design reference, not an architectural drawing."
            ]
        },
        "findings": [
            "Identity and source footprint are strong; all 30 GIS base vertices match at project-transform precision.",
            "The two-story model conflicts with the GIS NUM_LEVELS=1 field, whose counting convention is not documented.",
            "The roof and entry vocabulary have an exact-address illustration as a reference, but the gable scale and entrance orientation are not verified.",
            "The facade reads as a basic massing with sparse schematic windows; roof, heights, and entrance details remain uncertain."
        ],
        "independent_review": True,
        "rubric_pass": round(sum(item["score"] for item in criteria), 1) >= 8.0
    }


if __name__ == "__main__":
    result = evaluate()
    path = AUDIT / "independent_grade_codex" / "result.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("INDEPENDENT_GRADE_JSON=" + json.dumps(result, sort_keys=True))
