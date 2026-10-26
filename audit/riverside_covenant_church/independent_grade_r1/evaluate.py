import json
from pathlib import Path

EVIDENCE = Path(__file__).resolve().parent.parent


def evaluate():
    """Independent Riverside asset grade against the five repository criteria."""
    src = json.loads((EVIDENCE / "source_osm_way_860918859_raw.json").read_text(encoding="utf-8-sig"))
    cmp = json.loads((EVIDENCE / "source_footprint_comparison_way_860918859.json").read_text(encoding="utf-8-sig"))
    obs = json.loads((EVIDENCE / "source_reference_observation.json").read_text(encoding="utf-8-sig"))
    valid = json.loads((EVIDENCE / "reopen_validation.json").read_text(encoding="utf-8-sig"))
    criteria = [
      {"name":"Correct identity and source-backed footprint", "score":1.5,"max_score":2,
       "evidence":[f"Preserved OSM way/{src['way']['id']} is named '{src['way']['tags']['name']}' and tagged as a place of worship at 1850 Woodland Avenue.", "Owner history page corroborates Riverside's address and acquisition of an existing church building.", f"OSM polygon area is {cmp['source_osm_polygon_area_m2']:.2f} m²; source geometry is the exact original source, not an independent surveyed footprint."],
       "deduction":"Identity is well corroborated, but the footprint source is the original OSM source only; no independent survey or Purdue GIS match establishes structural walls."},
      {"name":"Position, orientation, and scale/dimensions", "score":1.5,"max_score":2,
       "evidence":[f"Ordered projected OSM ring matches the retained original mesh with max symmetric nearest-vertex distance {cmp['max_source_mesh_to_filtered_osm_nearest_vertex_m']:.6f} m.", "Asset scene and object transforms remain identity; campus XY coordinates are retained in this massing library."],
       "deduction":"This proves consistency with the original OSM import and project approximation only; there is no independent positional, orientation, or dimensional check."},
      {"name":"Evidence-backed height, floors, and roof form", "score":0.5,"max_score":2,
       "evidence":["Reopened asset is 8.8 m tall with a gabled roof; build config labels 4.7 m eaves and 8.8 m ridge as illustrative estimates.", "OSM way has no height or building:levels tags; owner and architect text do not provide exterior elevations or roof-form evidence."],
       "deduction":"Height, story count, and roof silhouette are not supported by measured or visual exterior evidence."},
      {"name":"Facade, entrances, and distinctive architecture", "score":0.25,"max_score":2,
       "evidence":["Rendered preview shows one gable mass and four schematic side windows per long face.", "The saved preview does not show an entrance; cited KJG project documents interior renovation and an interior full-glass entry, not exterior placement or dimensions."],
       "deduction":"Facade rhythm, exterior openings, colors, gable form, and entrance treatment are not source verified; no distinctive architectural feature is documented in the evidence."},
      {"name":"Modular export, portability, and complete evidence", "score":1.5,"max_score":2,
       "evidence":[f"Blender 5.2.3 reopened scene '{valid['asset_id']}' with the expected single object '{valid['object']}' in its asset collection.", f"Reopen validation reports {valid['mesh_vertices']} vertices, {valid['mesh_faces']} faces, four materials, and {valid['max_source_ring_error_m']:.8f} m maximum source-ring error.", "Building-specific evidence includes raw OSM node/tag snapshot, projection/method notes, build config/script, preview render, and reopen validation."],
       "deduction":"The package is portable and validates the existing library, but it lacks an evaluator/build module under the prescribed modular/buildings path and the evidence cannot support full architectural completeness."}
    ]
    result={"score":round(sum(c["score"] for c in criteria),2),"max_score":10,"criteria":criteria,
      "evidence":["Independently opened the saved .blend in Blender 5.2.3 and inspected scene, collection membership, object transforms, mesh counts, bounds, modifiers, and materials.", "Read raw OSM source, source-to-mesh footprint comparison, source reference observations, build config, reopen validation, and both saved rendered views."],
      "findings":[
       {"priority":"high","finding":"Obtain a source independent of the imported OSM feature that verifies the structural footprint, campus position, and orientation; preserve the source snapshot and record comparison error.","status":"unresolved"},
       {"priority":"high","finding":"Add dated exterior photographs or architectural elevations that identify the roof profile, entrance location, facade openings, and exterior materials. Replace or clearly retain estimates where evidence remains unavailable.","status":"unresolved"},
       {"priority":"medium","finding":"Add the prescribed dedicated modular/buildings build module and a rendered view that includes the entrance after it is source supported.","status":"unresolved"}
      ],
      "asset_inspection":{"blender_version":"5.2.3 LTS","scene":valid["asset_id"],"collection_object_count":valid["collection_objects"],"object":valid["object"],"vertices":valid["mesh_vertices"],"faces":valid["mesh_faces"],"bounds_world_m":valid["bounds_world_m"],"materials":valid["materials"],"modifiers":[]},
      "grade_status":"fail: below the repository minimum of 8/10"}
    return result

if __name__ == "__main__":
    result=evaluate()
    (Path(__file__).parent/"result.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2))
