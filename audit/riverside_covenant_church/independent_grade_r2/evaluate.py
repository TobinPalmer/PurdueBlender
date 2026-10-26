import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent


def evaluate():
    """Independently grade the reopened Riverside asset against repository criteria."""
    ev = json.loads((EVIDENCE / "evidence.json").read_text(encoding="utf-8-sig"))
    gis = json.loads((EVIDENCE / "indiana_building_footprint_feature_409445.json").read_text(encoding="utf-8-sig"))
    fp = json.loads((EVIDENCE / "footprint_comparison_indiana_2018_vs_osm.json").read_text(encoding="utf-8-sig"))
    val = json.loads((EVIDENCE / "reopen_validation.json").read_text(encoding="utf-8-sig"))
    obs = json.loads((EVIDENCE / "source_reference_observation.json").read_text(encoding="utf-8-sig"))
    criteria = [
      {"name":"Correct identity and source-backed footprint", "score":1.8, "max_score":2,
       "evidence":["Riverside's official history identifies its church at 1850 Woodland Avenue; a preserved named OSM polygon and independent IndianaMap feature 409445 overlap at 0.8867 IoU.", f"The state GIS ring is the modelled structural outline; the reopened model's maximum ring error is {val['max_source_ring_error_m']:.8f} m.", f"The independent GIS footprint is {fp['official_footprint_area_m2']:.2f} m² versus {fp['osm_footprint_area_m2']:.2f} m² for OSM."],
       "deduction":"The Indiana statewide footprint is not a legal survey and differs from OSM by about 12.7% in area; exact structural-wall boundary is not established."},
      {"name":"Position, orientation, and scale/dimensions", "score":1.6, "max_score":2,
       "evidence":[f"Campus XY from the Indiana GIS ring is preserved with an identity world matrix; model geometry matches the projected ring within {val['max_source_ring_error_m']:.8f} m.", f"Independent Indiana and OSM polygon centroids differ {fp['centroid_offset_m']:.3f} m; polygon IoU is {fp['footprint_iou']:.4f}.", "The library remains a direct-link campus-coordinate asset and retains its expected scene, collection, object, and transform."],
       "deduction":"Local coordinate conversion is approximate; the photo does not establish true-north facade orientation, and no geodetic survey or independent dimensions are available."},
      {"name":"Evidence-backed height, floors, and roof form", "score":1.2, "max_score":2,
       "evidence":["The 2016 exterior photograph directly supports a low horizontal roof and prominent centered A-frame; the model represents these features.", "The photo supports a low one-level hall composition, but no floor count or measured elevation is provided.", "Eaves 4.5 m, main ridge 5.7 m, and glazed apex 11.5 m are explicitly estimates, not measured heights."],
       "deduction":"Vertical dimensions, floor count, and exact roof pitch remain unverified; the evidence only supports the relative silhouette."},
      {"name":"Facade, entrances, and distinctive architecture", "score":1.6, "max_score":2,
       "evidence":["The dated facade photo shows the centered glazed A-frame, light framing, and multiple glazed entry bays; the preview includes those same large features in the matching central arrangement.", "Brick frontage and a low continuous eave are visible in the reference. The preview also includes simplified side windows."],
       "deduction":"The side-window count and dimensions, facade proportions, materials, and exact door geometry are schematic; one perspective photo is not an orthographic elevation."},
      {"name":"Modular export, portability, and complete evidence", "score":1.8, "max_score":2,
       "evidence":[f"Blender 5.2.3 reopened the expected scene with one object in the named asset collection; the mesh has {val['mesh_vertices']} vertices, {val['mesh_faces']} faces, and no modifiers.", "Dedicated build module preserves the stable asset path/names and campus coordinate frame; its source inputs are repository-relative.", "Evidence includes raw Indiana GIS and OSM snapshots, layer metadata, a dated exterior photo, comparison method/results, preview, and reopen validation."],
       "deduction":"A stale modeling-limitations paragraph still describes the prior 4.7 m/8.8 m gable model, conflicting with the current 4.5 m/5.7 m/11.5 m configuration; update that evidence text before treating the package as fully clean."}
    ]
    score = round(sum(c["score"] for c in criteria), 2)
    result={"score":score,"max_score":10,"criteria":criteria,
      "evidence":["Independently reopened the saved .blend in Blender 5.2.3 and checked collection membership, object transforms, geometry counts, bounds, materials, and modifiers.", "Compared the current render with the preserved 2016 exterior photo and reviewed raw GIS/OSM feature snapshots, CRS/method notes, comparison metrics, build module, configuration, and reopen validation."],
      "findings":[
       {"priority":"medium","status":"unresolved","finding":"Refresh the modeling_limitations in source_reference_observation.json, which currently describes the superseded single-gable revision and old 4.7 m/8.8 m estimates."},
       {"priority":"medium","status":"unresolved","finding":"Keep floor count and all elevation/roof dimensions explicitly estimated until a measured elevation or suitable additional source is available."},
       {"priority":"low","status":"documented","finding":"The GIS/OSM overlap supports identity and plan placement, but the approximate projection and 2018 statewide outline do not constitute a structural-wall or cadastral survey."}
      ],
      "asset_inspection":{"blender_version":"5.2.3 LTS","scene":val["asset_id"],"collection_object_count":val["collection_objects"],"object":val["object"],"vertices":val["mesh_vertices"],"faces":val["mesh_faces"],"bounds_world_m":val["bounds_world_m"],"world_matrix":val["world_matrix"],"materials":val["materials"],"modifiers":val["modifiers"]},
      "grade_status":"pass" if score >= 8 else "fail: below the repository minimum of 8/10",
      "reviewer":"Independent rubric evaluation"}
    return result

if __name__ == "__main__":
    result=evaluate()
    (HERE/"result.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2))
