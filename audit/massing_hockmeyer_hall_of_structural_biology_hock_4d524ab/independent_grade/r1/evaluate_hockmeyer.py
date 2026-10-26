"""Independent rubric evaluator for the saved Hockmeyer Hall asset.

Run from any working directory with Python. It reads the persisted source,
build, and reopen evidence and returns criterion-level scoring plus findings.
Visual comparison is documented as an evaluator observation in the result.
"""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
AUDIT = ROOT / "audit/massing_hockmeyer_hall_of_structural_biology_hock_4d524ab"
ASSET = ROOT / "modular/buildings/massing_hockmeyer_hall_of_structural_biology_hock_4d524ab.blend"
BUILDER = ROOT / "modular/buildings/build_massing_hockmeyer_hall_of_structural_biology_hock_4d524ab.py"


def evaluate() -> dict:
    build = json.loads((AUDIT / "build_evidence.json").read_text(encoding="utf-8"))
    reopen = json.loads((AUDIT / "reopen_validation.json").read_text(encoding="utf-8"))
    source_dir = AUDIT / "sources"
    renders = [AUDIT / "renders" / name for name in (
        "hockmeyer_exterior_oblique.png",
        "hockmeyer_courtyard_entry.png",
        "hockmeyer_roof_plan.png",
    )]
    source_gis = source_dir / "purdue_building_shapes_hock.json"
    source_photo = source_dir / "purdue_hockmeyer_exterior_2009.jpg"
    emergency_page = source_dir / "purdue_emergency_plan_page.html"
    osm = source_dir / "osm_local_map.xml"
    expected_collection = build["collection"]
    shell_error = float(reopen["max_source_to_shell_xy_vertex_error_m"])
    gis = json.loads(source_gis.read_text(encoding="utf-8-sig"))
    attrs = gis["features"][0]["attributes"]
    fid = attrs.get("FID")
    gis_name = attrs.get("BUILDING_N", "")
    identity_supported = fid == build["source_feature_id"] == 669 and "Hockmeyer" in gis_name
    exact_shell_copy = (reopen.get("ring_vertices_source") == reopen.get("ring_vertices_shell_lower")
                        == reopen.get("ring_vertices_shell_upper") == 58 and shell_error < 0.001)
    all_renders = all(p.is_file() and p.stat().st_size > 100_000 for p in renders)
    collection_ok = bool(reopen.get("collection_found")) and reopen.get("expected_collection") == expected_collection
    expected_scene_ok = bool(reopen.get("scene_name_matches"))

    criteria = [
        {
            "name": "Identity and source-backed footprint",
            "score": 1.5,
            "max_score": 2,
            "evidence": [
                f"Purdue BuildingShapes feature FID {fid} is named {gis_name!r}; build evidence also records HOCK and the matching address.",
                "The saved shell uses all 58 vertices from that feature's exterior ring.",
                "OSM way 283274991 independently matches the name/address, but its outline differs (reported Hausdorff distance about 16.27 m).",
                "Purdue Shape__Area 3358.58 m² conflicts with local ring area 1943.10 m² (about 73%); its semantics are undocumented. The discrepancy is disclosed but not resolved against a survey source.",
            ],
            "deduction": "Partial credit: building identity is well supported and a traceable Purdue footprint is used, but footprint-source conflict remains material.",
        },
        {
            "name": "Position, orientation, and scale/dimensions",
            "score": 1.5,
            "max_score": 2,
            "evidence": [
                f"Reopen check compared source and shell XY vertices; maximum recorded error is {shell_error:.6f} m, with 58 vertices at both shell levels.",
                "Builder uses the repository's documented local geographic approximation and keeps the source in campus coordinates.",
                "No independent survey/control-point check is included, and the compared Purdue/OSM outlines differ by up to about 16.27 m.",
            ],
            "deduction": "The model faithfully reproduces its chosen GIS ring, but independent positional/dimensional corroboration is weakened by the conflicting outline and undocumented area field.",
        },
        {
            "name": "Evidence-backed height, floors, and roof form",
            "score": 1.0,
            "max_score": 2,
            "evidence": [
                "Purdue emergency-preparedness source supports three occupied floors, a penthouse, and a basement.",
                "Official 2009 exterior photo and Storrow Kinsella imagery support a roof/penthouse presence and broad roof/courtyard context.",
                "Main wall height 11.4 m, 3.8 m floor bands, penthouse 2.8 m, and 14.2 m total are explicitly estimates; no measured height/elevation source is supplied.",
                "GIS Extrution=60 is undocumented and correctly not treated as height evidence.",
            ],
            "deduction": "Floor count and the existence of rooftop mass are supported; quantitative height, floor-to-floor spacing, penthouse dimensions/location, and precise roof silhouette remain estimates.",
        },
        {
            "name": "Facade, entrances, and distinctive architecture",
            "score": 0.75,
            "max_score": 2,
            "evidence": [
                "The saved Purdue photo visibly supports red brick, substantial multi-story blue-green glazing, and a courtyard-facing glazed entrance; the model includes these broad material cues.",
                "The three renders show a three-level brick mass with localized windows, selected glass curtainwall strips, a simple canopy, and a centered rooftop block.",
                "Photo comparison reveals a major facade cue not represented in the model: extensive pale opaque upper cladding alongside the large glazed curtainwall. The model presents an almost entirely brick shell outside localized glass strips.",
                "Exact bay placement, entry location/orientation, and facade proportions are explicitly visual interpretations from non-georeferenced images.",
            ],
            "deduction": "Only coarse palette and courtyard glazing are supported. Facade composition is materially incomplete relative to the official photo, while entrance registration and specific detailing remain speculative.",
        },
        {
            "name": "Modular export, portability, and complete evidence",
            "score": 1.5,
            "max_score": 2,
            "evidence": [
                f"Saved asset exists: {ASSET.is_file()}; builder exists: {BUILDER.is_file()}.",
                f"Reopen evidence confirms the stable collection {expected_collection!r} with {reopen.get('collection_object_count')} objects and no external unpacked dependencies.",
                f"Source snapshots and all three review renders are present: {source_gis.is_file()}, {source_photo.is_file()}, {emergency_page.is_file()}, {osm.is_file()}, and renders={all_renders}.",
                f"Expected scene name {reopen.get('expected_scene_name')!r} does not match reopened scene {reopen.get('actual_scene_name')!r}: Blender 4.5.15 truncation is explicitly recorded; scene contract passed={expected_scene_ok}, collection contract passed={collection_ok}.",
            ],
            "deduction": "Collection export, dependencies, and evidence are strong; the expected scene-name contract is an explicit integration failure even though the stable collection survives.",
        },
    ]
    score = round(sum(c["score"] for c in criteria), 2)
    findings = [
        "FAIL (6.25/10; minimum pass 8/10). Do not accept as complete yet.",
        "Resolve the GIS versus OSM footprint/area conflict with authoritative survey or plan evidence, or retain the issue as an integration limitation.",
        "Restore the expected full scene name in a compatible Blender version or update the export contract through the coordinator; do not assume the collection name alone satisfies consumers that expect the scene ID.",
        "Improve the facade massing to represent the large pale cladding volume and extensive curtainwall seen in the official exterior photo; georeference the principal entrance before claiming its location is verified.",
        "Keep total height and penthouse dimensions labeled estimated until a measured source is found.",
    ]
    return {
        "building_id": build["building_id"],
        "asset": str(ASSET.relative_to(ROOT)).replace("\\", "/"),
        "evaluator": "independent Hockmeyer Hall review r1",
        "score": score,
        "max_score": 10,
        "pass_threshold": 8,
        "passed": score >= 8,
        "criteria": criteria,
        "evidence": {
            "build_evidence": str((AUDIT / "build_evidence.json").relative_to(ROOT)).replace("\\", "/"),
            "reopen_validation": str((AUDIT / "reopen_validation.json").relative_to(ROOT)).replace("\\", "/"),
            "visual_review": [str(p.relative_to(ROOT)).replace("\\", "/") for p in renders] + [str(source_photo.relative_to(ROOT)).replace("\\", "/")],
            "gis_snapshot": str(source_gis.relative_to(ROOT)).replace("\\", "/"),
            "gis_feature_id": fid,
            "source_to_shell_xy_vertex_error_m": shell_error,
            "expected_collection_found": collection_ok,
            "expected_scene_name_matches": expected_scene_ok,
            "all_review_renders_present": all_renders,
        },
        "findings": findings,
    }


if __name__ == "__main__":
    print(json.dumps(evaluate(), indent=2, ensure_ascii=False))
