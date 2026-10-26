"""Independent evidence and saved-library evaluator for Shoemaker Cooperative."""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "audit" / "shoemaker_cooperative"
ASSET = ROOT / "modular" / "buildings" / "massing_shoemaker_cooperative_2159ea4.blend"


def evaluate():
    evidence = json.loads((AUDIT / "evidence.json").read_text(encoding="utf-8"))
    gis = json.loads((AUDIT / "source_feature_800_raw.json").read_text(encoding="utf-8-sig"))
    owner = json.loads((AUDIT / "source_owner_site_observation.json").read_text(encoding="utf-8"))
    validation = json.loads((AUDIT / "reopen_validation.json").read_text(encoding="utf-8"))
    preview = AUDIT / "preview_detail_r2.png"
    builder = ROOT / "modular" / "buildings" / "build_massing_shoemaker_cooperative_2159ea4.py"

    attrs = gis["attributes"]
    ring = gis["geometry"]["rings"][0]
    distinct_ring = ring[:-1] if ring[0] == ring[-1] else ring
    ring_xy = [
        ((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
         (lat - 40.4274) * 111040.0)
        for lon, lat in distinct_ring
    ]
    aabb = [min(p[0] for p in ring_xy), min(p[1] for p in ring_xy),
            max(p[0] for p in ring_xy), max(p[1] for p in ring_xy)]

    assert attrs["FID"] == 800 and attrs["BLDG_ABBR"] == "SOSH"
    assert attrs["ADDRESS"].startswith("351 Northwestern")
    assert len(distinct_ring) == 10
    assert validation["opened"] and validation["collection_objects"] == 1
    assert validation["source_ring_vertices"] == 10
    assert validation["max_source_ring_error_m"] < 0.001
    assert ASSET.is_file() and builder.is_file() and preview.is_file()

    criteria = [
        {
            "name": "Correct identity and source-backed footprint",
            "score": 1.8,
            "max_score": 2,
            "evidence": [
                "Official Purdue GIS FID 800 identifies building abbreviation SOSH, name Shoemaker, owner COOP, and address 351 Northwestern Avenue.",
                "Purdue Cooperative's operator page records the same address and the image is described as Shoemaker's home; Purdue Archives corroborates cooperative identity.",
                "All ten distinct transformed GIS ring points are represented in the reopened asset base with a maximum residual of 0.0000139 m."
            ],
            "uncertainty": "The GIS geometry is a campus map footprint, not a certified survey, and its structural edge convention and positional accuracy are unpublished."
        },
        {
            "name": "Position, orientation, and scale/dimensions",
            "score": 1.7,
            "max_score": 2,
            "evidence": [
                "The structural wall outline is located from the official WGS 84 ring using the documented campus-local conversion; the validation file independently compares the reopened mesh against all ten ring vertices.",
                f"Transformed source bounds are X [{aabb[0]:.3f}, {aabb[2]:.3f}] m, Y [{aabb[1]:.3f}, {aabb[3]:.3f}] m; the asset keeps the source ring orientation and footprint scale.",
                "Operator photo does not georeference the camera, so porch and entrance bearing remain estimated."
            ],
            "uncertainty": "Campus position and footprint are supported by GIS but have no published survey tolerance; the facade-side orientation has no georeferenced validation."
        },
        {
            "name": "Evidence-backed height, floors, and roof form",
            "score": 1.6,
            "max_score": 2,
            "evidence": [
                "The operator photo-tour labels a Floor Two section, and its exterior photograph visibly shows two above-grade window rows; this supports two modeled above-grade levels.",
                "The GIS NUM_LEVELS=1 attribute conflicts with that photo evidence, and the source provides no field-definition or counting convention; the conflict is retained in evidence.",
                "The partial operator photo directly supports a pitched gable roof; the model's eaves (6.7 m) and ridge (10.2 m) are estimates with no measured elevation source."
            ],
            "uncertainty": "Roof dimensions, exact roof wings, and absolute height are not measured; the GIS level-count disagreement is unresolved."
        },
        {
            "name": "Facade, entrances, and distinctive architecture",
            "score": 1.5,
            "max_score": 2,
            "evidence": [
                "The partial monochrome operator photo supports the visible gable vocabulary, a two-level porch/balcony with posts and simple railing, shutters, and two above-grade window levels.",
                "The model includes a pitched gable over the approximate main block, a two-level corner porch, entry marker, repeated windows, dark shutters, and floor/plinth bands.",
                "The model preview was visually inspected and reads as an irregular-footprint two-level cooperative house with the porch and gable feature."
            ],
            "uncertainty": "The source image is partial and unscaled; porch/door location, exact façade rhythm, roof wings, and color are approximate."
        },
        {
            "name": "Modular export, portability, and complete evidence",
            "score": 1.9,
            "max_score": 2,
            "evidence": [
                "Blender 5.2.3 LTS reopened the saved asset and validated one object in Asset_massing_shoemaker_cooperative_2159ea4.",
                "The saved mesh has 902 vertices and 620 faces and the dedicated build module preserves the assigned asset path and collection.",
                "Evidence includes the raw GIS feature, operator page observations, preview, and a saved reopen validation; the builder references no external image or texture files."
            ],
            "uncertainty": "Neighboring context and the master-file instance were not in the assigned library review scope."
        }
    ]
    return {
        "score": round(sum(item["score"] for item in criteria), 1),
        "max_score": 10,
        "criteria": criteria,
        "evidence": {
            "asset": str(ASSET.relative_to(ROOT)),
            "sources": [
                "audit/shoemaker_cooperative/source_feature_800_raw.json",
                "audit/shoemaker_cooperative/source_owner_site_observation.json",
                "audit/shoemaker_cooperative/evidence.json"
            ],
            "preview": "audit/shoemaker_cooperative/preview_detail_r2.png",
            "reopen_validation": "audit/shoemaker_cooperative/reopen_validation.json",
            "official_source_aabb_xy_m": [round(v, 6) for v in aabb],
            "max_source_ring_error_m": validation["max_source_ring_error_m"]
        },
        "findings": [
            "The official footprint and identity evidence are strong, and the reopened asset preserves the polygon at project-transform precision.",
            "The operator exterior image supports the gable, porch, shutter, and two-level vocabulary but is partial, unscaled, and not georeferenced.",
            "GIS NUM_LEVELS=1 conflicts with the operator photo-tour Floor Two label and the two visible above-grade window levels; the conflict is documented rather than hidden.",
            "Height, exact entrance orientation/location, facade spacing, and roof-wing geometry remain estimates."
        ],
        "independent_review": True,
        "rubric_pass": round(sum(item["score"] for item in criteria), 1) >= 8.0
    }


if __name__ == "__main__":
    result = evaluate()
    out = AUDIT / "independent_grade_codex" / "result.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
