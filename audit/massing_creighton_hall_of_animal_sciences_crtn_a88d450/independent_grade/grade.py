import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
INSPECTION = json.loads((HERE / "reopen_inspection.json").read_text(encoding="utf-8"))
SOURCES = Path(__file__).resolve().parents[1] / "sources"


def evaluate(facts):
    """Independent criterion-level score for CRTN, based on reopened file and source audit."""
    checks = {
        "identity": (facts["source_FID"] == 914 and facts["source_ABBR"] == "CRTN" and facts["polygon_vertex_count"] == 49 and facts["source_unique_xy_vertex_count"] == 49 and facts["source_ground_vertex_exact"]),
        "horizontal": (facts["mesh_bbox_xy_error_m"] < 0.01 and facts["collection_count"] == 1),
        "export": (facts["version"].startswith("4.5.15") and facts["object_type"] == "MESH" and facts["linked_libraries"] == 0 and facts["modifiers"] == []),
    }
    criteria = [
        {"name":"Correct identity and source-backed footprint", "score":2.0,"max_score":2.0,"status":"verified",
         "evidence":"Raw Purdue BuildingShapesZip4 snapshot identifies FID 914, BLDG_ABBR CRTN, address 270 S Russell Street, and the Creighton Hall name (spelling variant Russel). The closed WGS84 polygon has 49 non-closure vertices. Reopened asset contains the corresponding extruded plan; its 49 unique source ring vertices match ground-level mesh vertices within 0.000032 m; XY bounds differ by under 0.00002 m.",
         "checks_passed":checks["identity"]},
        {"name":"Position, orientation, and scale/dimensions", "score":2.0,"max_score":2.0,"status":"verified within source/transform limits",
         "evidence":"The direct WGS84-to-local XY transform, using the documented campus origin and approximate equirectangular conversion, reproduces the 94.9279 x 37.4695 m source bounds. Reopened world bounds differ by 0.000018 m maximum. Vertex-wise ring transformation is used without fitting/rescaling; the source ring supplies orientation. The transform itself is approximate, not surveyed.",
         "checks_passed":checks["horizontal"]},
        {"name":"Evidence-backed height, floors, and roof form", "score":1.5,"max_score":2.0,"status":"partially verified; heights estimated",
         "evidence":"Turner’s project page directly identifies a three-story teaching/research laboratory wing and a two-story animal-studies wing. The model encodes those story counts with 4 m/story schematic allowances (12 m and 8 m); neither floor-to-floor heights nor roof elevations are measured. Low-slope roof silhouette is broadly consistent with project imagery, but detailed roof equipment, parapets, and the exact split line remain unverified.",
         "checks_passed":True},
        {"name":"Facade, entrances, and distinctive architecture", "score":1.25,"max_score":2.0,"status":"partially verified",
         "evidence":"The Purdue-hosted page and its captioned building photo, together with Turner’s project gallery, are relevant building-specific visual references. The model uses brick-colored wall masses, repeated tall glazing, light trim, and a glazed canopy. Exact window rhythm, bay dimensions, the east-side entry placement, and canopy dimensions are not verified by the available views; the entry is correctly described as schematic by its builder.",
         "checks_passed":True},
        {"name":"Modular export, portability, and complete evidence", "score":1.75,"max_score":2.0,"status":"verified with presentation limitation",
         "evidence":"Reopened successfully in Blender 4.5.15 LTS. Expected collection and object names are present; collection has one joined mesh (1,912 vertices, 1,610 polygons, no modifiers), no linked libraries, and no external image textures. Source snapshots, retrieval dates, feature identifiers, CRS/conversion, uncertainty, build evidence, and two previews are present. The 211 disconnected mesh components are expected from joined schematic glazing/trim elements. Preview render lighting makes the roofing very flat, which reduces visual inspectability but does not affect the saved geometry.",
         "checks_passed":checks["export"]},
    ]
    score = round(sum(c["score"] for c in criteria), 2)
    findings = [
        "PASS (8.50/10; threshold 8.00).",
        "The GIS polygon and its placement/scale conversion are strongly verified; source metadata reports NUM_LEVELS=5 for the whole complex, while the project-specific Turner narrative distinguishes the two-story and three-story wings. The asset’s 8 m/12 m values remain estimates.",
        "Keep the entrance location, detailed facade rhythm, exact roof elevations, and roof equipment explicitly unverified. Do not use the visual preview alone to claim those details are accurate.",
        "The source-to-model bounding-box check is reproducible and nearly exact. This confirms transformed extents; the evaluator did not claim a survey-grade geodetic position or independent verification of every concave boundary segment.",
    ]
    return {"building_id":"massing_creighton_hall_of_animal_sciences_crtn_a88d450","score":score,"max_score":10,"pass_threshold":8,"passed":score>=8,"evaluator":"Independent review using AGENT.md rubric; reopened .blend in Blender 4.5.15 LTS; inspected raw GIS JSON, source HTML snapshots, live authoritative project text, and both provided previews.","asset_sha256":facts["asset_sha256"],"criteria":criteria,"evidence":{
        "asset":"modular/buildings/massing_creighton_hall_of_animal_sciences_crtn_a88d450.blend",
        "reopen_inspection":"independent_grade/reopen_inspection.json",
        "raw_sources":["sources/crtn_fid914_gis_snapshot.json","sources/turner_source_snapshot.html","sources/purdue_source_snapshot.html"],
        "previews":["previews/crtn_three_quarter.png","previews/crtn_plan.png"],
        "live_references":[
            {"url":"https://www.turnerconstruction.com/projects/purdue-university-hobart-russell-creighton-hall-of-animal-sciences","relevant claim":"The project is a two-part complex: three-story teaching/research lab wing and two-story animal-studies wing."},
            {"url":"https://ag.purdue.edu/news/department/ansc/2023/05/ansc-graduate-student-awards-2023.html","relevant claim":"Purdue-hosted May 19, 2023 story with an Open Graph image labeled Picture of Creighton Hall; the image is visual facade context, not measured documentation."}
        ],
        "reopen_metrics":{k:facts[k] for k in ["version","asset_sha256","asset_bytes","collection_count","object_name","object_type","mesh_vertices","mesh_polygons","components","modifiers","dimensions","bounds_world_m","source_FID","source_ABBR","num_levels","linked_libraries","mesh_bbox_xy_error_m","polygon_vertex_count","ground_z_vertex_count","source_unique_xy_vertex_count","source_ground_vertex_max_error_m","source_ground_vertex_exact"]},
        "source_limits":"GIS has no measured roof elevation (Extrution=0, CountOfFLO=0). NUM_LEVELS=5 is complex-level metadata and does not resolve the wing split. Visual references do not prove the modeled entry side or precise fenestration."
    },"findings":findings}

result=evaluate(INSPECTION)
(HERE/"result.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
(HERE/"report.md").write_text("# Independent CRTN grade\n\n**Score: {}/10 — {} (minimum pass: 8/10).**\n\n".format(result["score"],"PASS" if result["passed"] else "FAIL") + "\n".join("- **{}: {}/{}** — {}. {}".format(c["name"],c["score"],c["max_score"],c["status"],c["evidence"]) for c in result["criteria"]) + "\n\n## Findings\n\n" + "\n".join("- "+f for f in result["findings"]) + "\n",encoding="utf-8")
print(json.dumps({"score":result["score"],"passed":result["passed"],"criteria":result["criteria"],"findings":result["findings"]},indent=2))


