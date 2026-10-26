"""Fresh independent r3 review for Hanley Hall.

The evaluator consumes a newly reopened Blender inspection and compares it
with the archived source/evidence package and repository AGENT.md rubric.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
AUDIT = ROOT / "audit/massing_hanley_hall_c8a4551"


def evaluate():
    inspect = json.loads((HERE / "asset_inspection.json").read_text(encoding="utf-8"))
    evidence = json.loads((AUDIT / "evidence_record.json").read_text(encoding="utf-8"))
    validation = json.loads((AUDIT / "review/reopen_validation_r2.json").read_text(encoding="utf-8"))
    criteria = [
        {
            "criterion": "Correct identity and source-backed footprint",
            "score": 1.7,
            "max_score": 2,
            "evidence": "Purdue GIS OBJECTID 310 / HNLY and OSM way 283275000 independently identify Hanley Hall. The archived georeferenced orthophoto overlay visibly shows the smaller blue GIS ring inset inside the larger red OSM/model ring along clear roof edges. The repair uses GIS as the structural wall shell and OSM only as the outer eave/roof plan. This is a plausible source reconciliation supported by the imagery and the model visibly carries both outlines, but neither provider defines wall/eave semantics and tree/shadow occlusion means it is not a surveyed finding.",
        },
        {
            "criterion": "Position, orientation, and scale/dimensions",
            "score": 1.8,
            "max_score": 2,
            "evidence": "Fresh Blender 4.5.15 reopen confirms direct campus-coordinate geometry at X [-805.8110,-752.7789] m, Y [-318.5515,-278.4328] m, Z [0,16.08] m. Validation reports the wall ring matches all transformed Purdue GIS vertices within 0.000033 m and the OSM roof/eave ring within 0.000031 m; model/source IoU is about 0.999999 for each ring. GIS and OSM source polygons themselves remain different (IoU about 0.8085; centroids offset 1.235 m), with the aerial supporting the inset-wall/outer-eave interpretation.",
        },
        {
            "criterion": "Evidence-backed height, floors, and roof form",
            "score": 1.4,
            "max_score": 2,
            "evidence": "The Purdue OEP emergency plan supports three floors. The current aerial shows several pitched roof planes and the Purdue HHS photograph shows a projecting dark eave; the model now represents a shallow hipped roof over the larger eave plan, an improvement over the prior flat cap. Eave height 14.8 m and ridge height 16.08 m remain estimates; no measured elevation, section, roof pitch, or exact ridge layout is available.",
        },
        {
            "criterion": "Facade, entrances, and distinctive architecture",
            "score": 1.4,
            "max_score": 2,
            "evidence": "The Purdue HHS photo visibly supports red-brown brick, extensive ground-floor glazing, repeated upper windows, horizontal light bands, and a projecting dark roof edge. The renders show those broad characteristics across the model. A glazed entrance bay was added toward the probable playground-facing side, but the photograph is not georeferenced and the entry location is inferred. The repeated rhythm and unphotographed sides remain generalized; no dimensioned elevations were found.",
        },
        {
            "criterion": "Modular export, portability, and complete evidence",
            "score": 1.8,
            "max_score": 2,
            "evidence": "Fresh read-only reopen in Blender 4.5.15 found the expected scene and collection with one Hanley Hall mesh (3,138 vertices, 2,320 faces), no modifiers, no linked libraries, and no external file images. The saved scene contains only the asset object. Archived raw Purdue GIS, OSM, emergency plan, Purdue photo/article, orthophoto and metadata, source catalog, validation, and two review renders are present. Blender 4.5.15 warns the file was authored by 5.2 but opened for geometry inspection successfully.",
        },
    ]
    result = {
        "score": round(sum(c["score"] for c in criteria), 1),
        "max_score": 10,
        "passing_threshold": 8,
        "passed": round(sum(c["score"] for c in criteria), 1) >= 8,
        "asset_id": "massing_hanley_hall_c8a4551",
        "review_revision": "r3",
        "criteria": criteria,
        "evidence": {
            "asset_path": "modular/buildings/massing_hanley_hall_c8a4551.blend",
            "builder_path": "modular/buildings/build_massing_hanley_hall_c8a4551.py",
            "direct_reopen_tool": "Blender 4.5.15 LTS, read-only fresh open; reports Blender 5.2 writer version",
            "direct_reopen": {
                "scene": inspect["scene"],
                "collection": inspect["collection"],
                "collection_objects": inspect["collection_objects"],
                "object_type": inspect["object_type"],
                "mesh_vertices": inspect["mesh_vertices"],
                "mesh_faces": inspect["mesh_faces"],
                "bounds_xyz_m": inspect["mesh_bounds_world_xyz_m"],
                "modifiers": inspect["modifier_names"],
                "linked_libraries": inspect["linked_libraries"],
                "external_file_images": inspect["external_file_images"],
            },
            "footprint_reconciliation": validation["source_difference_and_resolution"],
            "footprint_vertex_checks": {
                "wall_source": validation["wall_footprint"],
                "eave_source": validation["roof_eave_outline"],
            },
            "source_files": [
                "audit/massing_hanley_hall_c8a4551/sources/purdue_campus_gis_hanley.json",
                "audit/massing_hanley_hall_c8a4551/sources/osm_way_283275000_raw.json",
                "audit/massing_hanley_hall_c8a4551/sources/indiana_current_aerial_hanley.jpg",
                "audit/massing_hanley_hall_c8a4551/sources/purdue_hanley_emergency_plan.html",
                "audit/massing_hanley_hall_c8a4551/sources/purdue_hanley_playground_photo.jpg",
                "audit/massing_hanley_hall_c8a4551/sources/purdue_hhs_hanley_article.html",
            ],
            "reviewed_views": [
                "audit/massing_hanley_hall_c8a4551/review/hanley_current_aerial_footprint_overlay.jpg",
                "audit/massing_hanley_hall_c8a4551/renders/hanley_hall_facade.png",
                "audit/massing_hanley_hall_c8a4551/renders/hanley_entry_review.png",
            ],
        },
        "findings": [
            "The revised GIS-wall / OSM-eave reconciliation is plausible and better supported than the previous single-ring model: the georeferenced orthophoto visibly places the GIS perimeter inward from the larger roof edge. The difference remains interpretive because source polygon semantics are undocumented and the image is not a survey.",
            "The model now distinguishes the GIS structural shell from the outer roof/eave outline and matches both transformed rings within the recorded coordinate tolerances. The original source-ring disagreement (area ratio 1.229, IoU 0.8085, centroid separation 1.235 m) remains documented rather than hidden.",
            "Three floors are supported by the official OEP plan. Eave/ridge heights, roof pitch and exact roof facet geometry remain estimates; no measured vertical source was found.",
            "The entry bay's playground-facing location is inferred from an un-georeferenced photograph and aerial context. Window rhythm on other sides is generalized.",
            "The asset is portable and reopened successfully, though Blender 4.5.15 reports it was written by Blender 5.2.",
        ],
        "independent_review": True,
        "read_only_asset_source_and_shared_index": True,
    }
    assert result["max_score"] == 10
    assert abs(result["score"] - sum(c["score"] for c in criteria)) < 1e-9
    return result


if __name__ == "__main__":
    result = evaluate()
    (HERE / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
