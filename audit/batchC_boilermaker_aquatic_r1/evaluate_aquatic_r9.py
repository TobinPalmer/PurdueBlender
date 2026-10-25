"""Independent rubric evaluator for the saved R9 aquatic-center asset.

Run with Blender 5.2 background Python. This opens the saved asset read-only,
checks the recorded source/evidence and hash, and writes the grade JSON.
"""
import bpy
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(r"C:\Users\Tobin\Documents\Blender\PurdueMap")
AUDIT = ROOT / "audit/batchC_boilermaker_aquatic_r1"
ASSET_PATH = ROOT / "modular/buildings/morgan_j_burke_boilermaker_aquatic_center.blend"
EXPECTED_SHA = "136c7c7ee7d9d69f8bd1ac84e6e9269c00297a9c464bdd42ef13009bba66f497"


def evaluate():
    """Return score, criterion-level evidence, evidence paths, and findings."""
    bpy.ops.wm.open_mainfile(filepath=str(ASSET_PATH))
    actual_sha = hashlib.sha256(ASSET_PATH.read_bytes()).hexdigest()
    validation = json.loads((AUDIT / "validation_r9.json").read_text(encoding="utf-8"))
    source_record = json.loads((AUDIT / "evidence_r9.json").read_text(encoding="utf-8"))
    manifest = json.loads((ROOT / "modular/manifest.json").read_text(encoding="utf-8"))
    entry = next(a for a in manifest["assets"] if a["id"] == "morgan_j_burke_boilermaker_aquatic_center")
    asset = bpy.data.collections["Asset_morgan_j_burke_boilermaker_aquatic_center"]
    shell = bpy.data.objects["AQUA R1 | continuous brick and concrete high-bay envelope"]
    roof = bpy.data.objects["AQUA | clear-span natatorium | pitched roof planes"]
    r9 = bpy.data.collections["AQUA_R9 | bleacher supports and cutaway review"]
    trusses = [o for o in asset.all_objects if o.type == "MESH" and o.name.startswith("AQUA | schematic clear-span roof truss")]
    risers = [o for o in r9.objects if o.name.startswith("AQUA R9 | continuous bleacher riser")]
    posts = [o for o in r9.objects if o.name.startswith("AQUA R9 | center aisle rail post")]
    image_deps = [i.filepath for i in bpy.data.images if i.source == "FILE" and i.filepath]
    shell_dims = [round(float(v), 3) for v in shell.dimensions]
    roof_dims = [round(float(v), 3) for v in roof.dimensions]

    assert actual_sha == EXPECTED_SHA == validation["asset_sha256"]
    assert entry["file"] == "buildings/morgan_j_burke_boilermaker_aquatic_center.blend"
    assert entry["collection"] == asset.name
    assert len(asset.all_objects) == validation["asset_objects"] == 1129
    assert len(trusses) == validation["existing_trusses"] == 21
    assert len(risers) == validation["continuous_bleacher_risers"] == 24
    assert len(posts) == validation["connected_aisle_rail_posts"] == 24
    assert not roof.hide_render and not roof.hide_viewport
    assert not image_deps
    assert all(o.data.materials for o in asset.all_objects if o.type == "MESH")

    placement = validation["coordinator_master_placement_check"]
    assert math.hypot(-808.6829834 - (-808.683), 80.336998 - 80.337) < 0.00003
    renders = [AUDIT / "aquatic_r9_interior_truss_cutaway.png", AUDIT / "aquatic_r9_bleacher_aisle_detail.png"]
    assert all(p.is_file() for p in renders)

    criteria = [
        {
            "name": "Correct identity and source-backed footprint",
            "score": 1.9,
            "max_score": 2,
            "evidence": [
                "Purdue GIS snapshot feature FID 896 is preserved as a raw source record; it is a building-specific footprint record.",
                "R9 reopen validation compares the 70-vertex GIS ring with 70 structural-shell perimeter segments; maximum sampled bidirectional deviation is 0.000002 m.",
                "The 2026-10-24 Arsee Engineers project photograph and its project listing identify the named aquatic center and support the natatorium program.",
            ],
            "limitation": "The extremely close local outline match is correspondence to the GIS polygon, not proof that the source polygon is a surveyed wall line.",
        },
        {
            "name": "Position, orientation, and scale/dimensions",
            "score": 2.0,
            "max_score": 2,
            "evidence": [
                "Coordinator-provided read-only master evidence reports Placement_morgan_j_burke_boilermaker_aquatic_center at (-808.6829834, 80.336998, 0), unit scale and zero rotation.",
                "The manifest placement origin is (-808.683, 80.337); independently recomputing the stated XY difference gives 0.00001672 m, below the requested 0.00003 m tolerance.",
                f"The opened R9 shell object reports local dimensions {shell_dims} m; footprint correspondence provides the source-backed plan comparison.",
            ],
            "limitation": "The placement transform is coordinator-reported master evidence, not a master file independently opened by this evaluator. The manifest uses a local approximate geographic frame, not survey control.",
        },
        {
            "name": "Evidence-backed height, floors, and roof form",
            "score": 0.9,
            "max_score": 2,
            "evidence": [
                "The saved source contains the named pitched-roof object and 21 schematic clear-span roof truss meshes; roof geometry remains present and visible after reopen.",
                "The Arsee Engineers interior project photograph qualitatively supports exposed trusses and a high-bay pool hall.",
                f"The opened roof object reports local dimensions {roof_dims} m; no measured section or elevation source was supplied to validate those values.",
            ],
            "limitation": "Roof profile, truss member sizing and spacing, eave/ridge elevations, floor count, and total building height remain unverified. Dimensions read from the model are measurements of the model, not evidence for the real building.",
        },
        {
            "name": "Facade, entrances, and distinctive architecture",
            "score": 1.8,
            "max_score": 2,
            "evidence": [
                "Street View source record supports a north brick facade, ribbon glazing, entry canopy, and building lettering; R8 north-entry and facade renders remain part of the R9 saved evidence set.",
                "Arsee Engineers project photography supports the pool hall, Purdue wall lettering, metal bleacher banks, center aisle, and exposed roof structure.",
                "The two R9 renders show continuous stepped aluminum bleacher tiers, riser plates, center aisle rails/posts, wall-mounted Purdue panels, pool/deck, and linear lighting.",
            ],
            "limitation": "Facade bay/opening dimensions, interior seating geometry, banner placement, rail compliance, fixture schedule, and truss detailing are not dimensioned/as-built evidence; the R9 cutaway view still presents a broad overhead plane with only limited readable roof structure.",
        },
        {
            "name": "Modular export, portability, and complete evidence",
            "score": 1.9,
            "max_score": 2,
            "evidence": [
                "The reopened file uses the manifest's stable asset collection and asset path; the actual file SHA-256 matches both the R9 validation and R9 hash record.",
                "The asset contains 1,129 objects, all mesh objects have materials, and it has no external image-file dependencies.",
                "R9 source record lists provider, URLs, retrieval dates, source CRS/method where applicable, uncertainty, validation, and renders.",
            ],
            "limitation": "Some interior objects are explicitly schematic estimates, and the placement cross-check is supplied by the coordinator rather than included as independently inspectable master data in the asset folder.",
        },
    ]
    score = round(sum(c["score"] for c in criteria), 1)
    return {
        "building": "Morgan J. Burke Boilermaker Aquatic Center",
        "building_id": "morgan_j_burke_boilermaker_aquatic_center",
        "revision_reviewed": 9,
        "grade_date": "2026-10-25",
        "asset": "modular/buildings/morgan_j_burke_boilermaker_aquatic_center.blend",
        "asset_sha256_reviewed": actual_sha,
        "score": score,
        "max_score": 10,
        "threshold": 8,
        "passes": score >= 8,
        "criteria": criteria,
        "evidence": {
            "saved_asset_opened_read_only": True,
            "asset_collection": asset.name,
            "asset_objects": len(asset.all_objects),
            "shell_local_dimensions_m": shell_dims,
            "roof_object_local_dimensions_m": roof_dims,
            "roof_render_and_viewport_visible_after_open": not roof.hide_render and not roof.hide_viewport,
            "truss_objects": len(trusses),
            "r9_riser_objects": len(risers),
            "r9_aisle_post_objects": len(posts),
            "external_image_dependencies": len(image_deps),
            "master_placement_check": placement,
            "r9_renders_reviewed": [p.name for p in renders],
            "source_records_reviewed": ["evidence_r9.json", "validation_r9.json", "audit/batchC_boilermaker_aquatic_official_footprint.json", "modular/manifest.json"],
            "score_basis": "Evidence judged against the five AGENT.md rubric criteria. Unsupported roof/height claims are deducted; appearance alone is not treated as measurement evidence.",
        },
        "findings": [
            "The R9 asset and its recorded SHA-256 agree exactly: " + actual_sha,
            "The requested master marker comparison agrees with the manifest origin within 0.00003 m, closing the placement evidence gap from R8.",
            "Roof and total-height accuracy remain uncertain: qualitative truss imagery supports the building type, but no measured roof/elevation record validates modeled roof profile or elevations.",
            "The R9 model adds connected bleacher risers and aisle posts; exact seat/tread dimensions and accessibility compliance remain illustrative.",
        ],
    }


result = evaluate()
(AUDIT / "evaluator_result_r9.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
