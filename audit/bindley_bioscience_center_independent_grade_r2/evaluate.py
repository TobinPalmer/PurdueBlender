"""Independent rubric evaluator for Bindley Bioscience Center revision 2.

Run after the Blender reopen probe with:
    python audit/bindley_bioscience_center_independent_grade_r2/evaluate.py
"""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROBE = json.loads((HERE / "blender_probe.json").read_text(encoding="utf-8"))
EXPORT = json.loads((HERE / "export_probe.json").read_text(encoding="utf-8"))
SOURCE = json.loads((ROOT / "audit/bindley_bioscience_center/evidence.json").read_text(encoding="utf-8"))
GIS = json.loads((ROOT / "audit/bindley_bioscience_center/sources/gis_feature_605.json").read_text(encoding="utf-8"))
ASSET_PATH = ROOT / PROBE["asset_file"]


def evaluate():
    """Return an evidence-backed score dictionary with five 0–2 criteria."""
    assert PROBE["scene"] == "Scene"
    assert PROBE["building_id"] == "bindley_bioscience_center"
    assert PROBE["collection"] == "Asset_bindley_bioscience_center"
    assert PROBE["gis_feature_id"] == 605
    assert PROBE["gis_building_abbreviation"] == "BIND"
    assert PROBE["gis_building_name"] == "Bindley Bioscience Center"
    assert PROBE["gis_address"] == "1203 Mitch Daniels Blvd"
    assert PROBE["gis_ring_vertex_count"] == 191
    assert PROBE["shell_base_xy_count"] == 191
    assert PROBE["manifest_names_match"] and PROBE["manifest_counts_match"]
    assert PROBE["max_footprint_hausdorff_m"] < 0.01
    assert PROBE["placement_centroid_residual_m"] < 0.01
    assert PROBE["dark_name_wall_present"] and PROBE["sign_text_present"]
    assert len(PROBE["roof_equipment_tops_local_m"]) == 8
    assert PROBE["max_roof_equipment_top_m"] <= 14.51
    assert not PROBE["external_image_files"] and not PROBE["linked_libraries"]
    assert not PROBE["camera_or_light_objects_in_export_collection"]
    assert EXPORT["collection"] == PROBE["collection"]
    assert EXPORT["object_count"] == PROBE["collection_object_count"]
    assert not EXPORT["camera_light_objects"]
    assert not EXPORT["external_image_files"] and not EXPORT["linked_libraries"]
    assert SOURCE["building_id"] == PROBE["building_id"]
    assert SOURCE["validation"]["dark_name_wall_present"] is True
    assert SOURCE["validation"]["roof_equipment_max_top_local_m"] <= 14.5
    assert GIS["feature"]["attributes"]["FID"] == 605

    criteria = [
        {
            "criterion": "Correct identity and source-backed footprint",
            "score": 2.0,
            "max_score": 2.0,
            "evidence": (
                "Official Purdue BuildingShapes feature 605 matches BIND, the full building name, "
                "and the 1203 Mitch Daniels Blvd address. Its 191-point exterior ring is preserved "
                "in the structural shell; independent bidirectional point-set Hausdorff residual "
                f"is {PROBE['max_footprint_hausdorff_m']:.6f} m."
            ),
        },
        {
            "criterion": "Position, orientation, and scale/dimensions",
            "score": 2.0,
            "max_score": 2.0,
            "evidence": (
                "The detailed model is in the GIS-centroid local frame. The independent projected "
                "GIS centroid and manifest placement origin differ by "
                f"{PROBE['placement_centroid_residual_m']:.6f} m; shell XY bounds match the "
                "source-derived local bounds to sub-millimeter precision, with the source ring "
                "vertices preserved without rescaling."
            ),
        },
        {
            "criterion": "Evidence-backed height, floors, and roof form",
            "score": 1.2,
            "max_score": 2.0,
            "evidence": (
                "Purdue GIS records three levels, matching the modeled three-level envelope. "
                "The evidence explicitly labels the 13.3 m eave and ≤14.5 m roof equipment tops "
                "as estimates/schematic; no measured roof plan, section, or elevation was located. "
                "The low-slope roof is visually plausible but not dimension-verified."
            ),
        },
        {
            "criterion": "Facade, entrances, and distinctive architecture",
            "score": 1.6,
            "max_score": 2.0,
            "evidence": (
                "The Purdue facility and Flad photographs support the light metallic panels, "
                "broad glazing, lobby curtain wall, entry canopy, and prominent charcoal name wall. "
                "The revised render shows the dark wall and legible name in front of the glazed lobby. "
                "Exact bay spacing, wall extent, entry dimensions, and unphotographed elevations "
                "remain interpretive."
            ),
        },
        {
            "criterion": "Modular export, portability, and complete evidence",
            "score": 2.0,
            "max_score": 2.0,
            "evidence": (
                f"The reopened named collection contains {PROBE['collection_object_count']} objects, "
                "and its object names/count match the manifest exactly. A collection-only .blend "
                "export was independently reopened with the same object count and no cameras/lights, "
                "external images, or linked libraries. The building record includes raw GIS, "
                "Purdue facility/photo, Purdue research directory, and architect sources, plus "
                "renders and validation."
            ),
        },
    ]
    total = round(sum(item["score"] for item in criteria), 2)
    findings = [
        "Three levels are supported by Purdue GIS, but eave/top height and floor-to-floor dimensions are estimates.",
        "The rooftop screens and vents are deliberately schematic and are not supported by a roof plan or section.",
        "The facade concept follows building-specific Purdue and Flad photographs; exact elevations and bay dimensions remain unverified.",
    ]
    return {
        "building_id": "bindley_bioscience_center",
        "asset_sha256": hashlib.sha256(ASSET_PATH.read_bytes()).hexdigest(),
        "score": total,
        "max_score": 10,
        "pass_threshold": 8,
        "passed": total >= 8,
        "criteria": criteria,
        "evidence": {
            "source_record": "audit/bindley_bioscience_center/evidence.json",
            "raw_gis_snapshot": "audit/bindley_bioscience_center/sources/gis_feature_605.json",
            "primary_photo": "audit/bindley_bioscience_center/sources/purdue_bindley_photo.jpg",
            "architect_photos": "audit/bindley_bioscience_center/sources/flad_bindley_1.jpg through flad_bindley_7.jpg",
            "overview_render": "audit/bindley_bioscience_center/overview.png",
            "entry_render": "audit/bindley_bioscience_center/entry_detail.png",
            "blender_asset_probe": "audit/bindley_bioscience_center_independent_grade_r2/blender_probe.json",
            "collection_export_probe": "audit/bindley_bioscience_center_independent_grade_r2/export_probe.json",
        },
        "findings": findings,
    }


if __name__ == "__main__":
    result = evaluate()
    (HERE / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
