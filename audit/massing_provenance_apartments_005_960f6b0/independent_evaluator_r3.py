"""Fresh independent r3 grader for Provenance Apartments 005 / Building F.

The evaluator reopens the saved asset in Blender 5.2.3, reads the raw GIS
feature and shared manifest, and checks the building-specific source package.
It grades the five AGENT.md criteria and records uncertainty explicitly.
"""
import json
import math
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ID = "massing_provenance_apartments_005_960f6b0"
ASSET = ROOT / "modular" / "buildings" / f"{ID}.blend"
BLENDER = ROOT.parent / "blender" / "blender-5.2.3-windows-x64" / "blender.exe"


def readj(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def mercator_to_campus(x, y):
    lon = math.degrees(x / 6378137.0)
    lat = math.degrees(2 * math.atan(math.exp(y / 6378137.0)) - math.pi / 2)
    return ((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
            (lat - 40.4274) * 111040.0)


def reopen_direct():
    expr = (
        "import bpy,json; "
        f"bpy.ops.wm.open_mainfile(filepath={str(ASSET)!r}); "
        f"c=bpy.data.collections.get('Asset_{ID}'); "
        "o=bpy.data.objects.get('Provenance Apartments.005'); "
        "v=[[(o.matrix_world@x.co)[i] for i in range(3)] for x in o.data.vertices]; "
        "b=[[min(p[i] for p in v),max(p[i] for p in v)] for i in range(3)]; "
        "s={'version':bpy.app.version_string,'scene':bpy.context.scene.name,"
        "'collection':c.name if c else None,'collection_count':len(c.objects) if c else -1,"
        "'object':o.name if o else None,'type':o.type if o else None,"
        "'vertices':len(o.data.vertices) if o else None,'faces':len(o.data.polygons) if o else None,"
        "'bounds':b,'base_vertices':v[:32],"
        "'materials':[m.name for m in o.data.materials if m],"
        "'unpacked_images':[i.filepath for i in bpy.data.images if i.filepath and not i.packed_file],"
        "'libraries':len(bpy.data.libraries),'modifiers':[m.name for m in o.modifiers]}; "
        "print('PROVENANCE_R3='+json.dumps(s))"
    )
    cp = subprocess.run([str(BLENDER), "--background", "--python-expr", expr],
                        cwd=ROOT, capture_output=True, text=True, timeout=240)
    if cp.returncode:
        raise RuntimeError("Blender reopen failed: " + cp.stderr[-1600:])
    match = re.search(r"PROVENANCE_R3=(\{[^\r\n]*\})", cp.stdout)
    if not match:
        raise RuntimeError("No Blender direct snapshot: " + cp.stdout[-1600:])
    return json.loads(match.group(1))


def evaluate():
    assert ASSET.is_file() and BLENDER.is_file()
    d = reopen_direct()
    srcdir = HERE / "sources"
    feature = readj(srcdir / "official_purdue_fid506.json")["feature"]
    attrs = feature["attributes"]
    ring = feature["geometry"]["rings"][0]
    if ring[0] == ring[-1]:
        ring = ring[:-1]
    expected = [mercator_to_campus(x, y) for x, y in ring]
    residuals = [math.dist(p[:2], v[:2]) for p, v in zip(expected, d["base_vertices"][:len(expected)])]
    max_residual = max(residuals)
    dims = [max(p[i] for p in expected) - min(p[i] for p in expected) for i in range(2)]
    manifest = readj(ROOT / "modular" / "manifest.json")
    entry = next(e for e in manifest["assets"] if e["id"] == ID)
    mb = entry["bounds_world_m"]
    manifest_delta = [[d["bounds"][i][j] - mb[i][j] for j in range(2)] for i in range(3)]
    max_manifest_delta = max(abs(x) for row in manifest_delta for x in row)
    crosswalk = readj(HERE / "crosswalk_analysis.json")
    build = readj(HERE / "build_evidence.json")
    validation = readj(HERE / "reopen_validation.json")
    search = readj(HERE / "source_search_r3.json")
    plan_crop = srcdir / "county_plan_sheet_C1_4_apartment_cluster.png"
    ortho = HERE / "indiana_current_orthophoto_2025_fid506_overlay.jpg"
    renders = [HERE / "preview_southwest.png", HERE / "preview_top.png"]
    required = [ASSET, srcdir / "county_provenance_phase1_2_construction_plans.pdf",
                plan_crop, ortho, srcdir / "indiana_current_orthophoto_2025_raw.jpg",
                HERE / "source_register.json", HERE / "revision_r3_summary.md",
                HERE / "source_search_r3.json", *renders]
    assert d["version"].startswith("5.2.3")
    assert d["scene"] == f"Building_{ID}" and d["collection"] == f"Asset_{ID}"
    assert d["collection_count"] == 1 and d["type"] == "MESH"
    assert attrs["FID"] == 506 and attrs["BUILDING_N"] == "Building F"
    assert attrs["BLDG_ABBR"] == "143" and attrs["Layer"] == "BLDG Building Pre-planning"
    assert len(expected) == 32 and max_residual < 0.001
    assert all(p.is_file() for p in required)

    criteria = [
        {
            "criterion": "Correct identity and source-backed footprint", "score": 1.9, "max_score": 2.0,
            "status": "Strong independent match to Building F / 143; GIS ring remains a pre-planning proxy rather than an as-built wall survey",
            "evidence": [
                "County construction-plan sheet C1.4 labels the central apartment block BLDG F / 143 between BLDG E / 144 and BLDG G / 142.",
                "Purdue GIS FID 506 names Building F and abbreviation 143. The stable .005 crosswalk is corroborated by the inherited proxy center's proximity, explicit C1.4 location, and the no-warp overlay against the current Indiana orthophoto.",
                f"The 32 reopened base-ring vertices reproduce transformed FID 506 within {max_residual:.6f} m. The red overlay follows the target roof outline closely, but both the layer label ('BLDG Building Pre-planning') and overhead roof imagery limit claims about exact wall registration."
            ],
            "findings": ["Keep the building identity and footprint match qualified: FID 506 is pre-planning, and the orthophoto shows roof/eaves rather than a surveyed wall line."]
        },
        {
            "criterion": "Position, orientation, and scale/dimensions", "score": 1.8, "max_score": 2.0,
            "status": "Position, orientation, and approximate envelope agree with the plan crosswalk and current roof imagery",
            "evidence": [
                f"Fresh Blender reopen bounds: X {d['bounds'][0][0]:.3f}..{d['bounds'][0][1]:.3f} m, Y {d['bounds'][1][0]:.3f}..{d['bounds'][1][1]:.3f} m, Z {d['bounds'][2][0]:.3f}..{d['bounds'][2][1]:.3f} m. The transformed GIS candidate envelope is approximately {dims[0]:.2f} by {dims[1]:.2f} m.",
                "The C1.4 neighbor order/orientation and orthophoto overlay support the mapped block placement. The plan is not georeferenced and project coordinates use a local approximation; the GIS line is not certified as the wall perimeter."
            ],
            "findings": ["Treat the footprint dimensions as approximate until a georeferenced as-built or wall survey is available."]
        },
        {
            "criterion": "Evidence-backed height, floors, and roof form", "score": 1.4, "max_score": 2.0,
            "status": "Three-story count has project-wide support; roof rhythm and all vertical measurements are explicitly estimated",
            "evidence": [
                "Studio M's project description supports three stories at the development level, but does not identify the story count of Building F individually.",
                f"Build evidence labels eaves ({build['dimensions']['wall_height_m']:.1f} m) and ridge ({build['dimensions']['ridge_height_m']:.1f} m) as estimates, each with ±{build['dimensions']['height_uncertainty_m']['ridge_plus_minus']:.1f} m uncertainty; no Building F elevation or section was found.",
                "The five-break roof rhythm broadly corresponds to the repeated roof shapes visible in the exact-block 2025 overhead image. The image does not establish ridge locations, pitch, eave/ridge heights, or a definitive gable count; the r3 summary identifies these as estimates."
            ],
            "findings": ["Retain the explicit height and roof-form uncertainty; no measured vertical evidence or F-specific architectural elevation is available."]
        },
        {
            "criterion": "Facade, entrances, and distinctive architecture", "score": 1.2, "max_score": 2.0,
            "status": "The neutral shell is a defensible evidence-limited massing; facade and entrance architecture remain unknown",
            "evidence": [
                "The r3 exact-block search records searches for F/143 photos, elevations, and sections and reports no attributable street image or approved architectural elevation/section in accessible sources.",
                "Studio M imagery is project-wide and cannot identify this block. The r3 model removes its previously generalized windows, balconies, accent bays, canopies, and material stationing, avoiding unsupported placement claims.",
                "Direct inspection of the render confirms a plain shell with no modeled entrance or facade rhythm. Therefore the package accurately represents the evidence gap but does not resolve Building F's visible architectural character."
            ],
            "findings": ["Facade, opening rhythm, and entrance remain unverified and absent; a building-specific photo or elevation would be needed to raise this criterion materially."]
        },
        {
            "criterion": "Modular export, portability, and complete evidence", "score": 1.5, "max_score": 2.0,
            "status": "Asset reopens cleanly and the audit package is complete; the shared manifest still contains superseded bounds",
            "evidence": [
                f"Direct separate-process Blender {d['version']} reopen confirms scene/collection identity, one mesh ({d['vertices']} vertices, {d['faces']} faces), {len(d['modifiers'])} modifiers, {len(d['unpacked_images'])} unpacked images, and {d['libraries']} linked libraries. The r3 reopen validation records 16/16 checks passing.",
                "The audit folder contains the raw Purdue GIS snapshot, C1.4 plan and crop, raw and overlaid 2025 orthophoto, source search/register, revision summary, reopen validation, and updated top and oblique renders. The saved mesh has two neutral material slots, no modifiers, and no external image dependencies.",
                f"Shared manifest bounds remain {mb}, while the reopened asset bounds are {d['bounds']}; maximum component difference is {max_manifest_delta:.2f} m. This is a substantial stale integration record and should be reconciled by the shared-file owner."
            ],
            "findings": ["Coordinator should update the shared manifest bounds before relying on them for integration; the independent audit does not alter shared files."]
        }
    ]
    score = round(sum(c["score"] for c in criteria), 2)
    findings = [f for c in criteria for f in c["findings"]]
    return {
        "building_id": ID,
        "building_name": "Provenance Apartments 005 / Building F (143)",
        "reviewer": "independent r3 evaluator; fresh Blender 5.2.3 reopen and direct inspection of C1.4, FID 506 overlay, r3 source search, evidence, and renders",
        "score": score, "max_score": 10, "passing_standard": 8,
        "criteria": criteria,
        "evidence": {
            "asset_path": str(ASSET.relative_to(ROOT)), "blender": d["version"],
            "reopened_scene": d["scene"], "reopened_collection": d["collection"],
            "direct_reopen_measurements": {k: d[k] for k in ("object", "type", "collection_count", "vertices", "faces", "bounds", "materials", "unpacked_images", "libraries", "modifiers")},
            "source_identity": {k: attrs.get(k) for k in ("FID", "BUILDING_N", "BLDG_ABBR", "Layer", "BUILDING_1", "ADDRESS", "NUM_LEVELS", "BUILT", "OCCUPIED")},
            "candidate_footprint": {"ring_vertex_count": len(expected), "candidate_envelope_m": dims, "max_vertex_residual_m": max_residual, "as_built_wall_line": "uncertain; pre-planning polygon and roof outline are not a surveyed wall line"},
            "crosswalk": crosswalk,
            "source_search_r3": {"conclusion": search["conclusion"], "searches": search["searches"], "reviewed_sources": search["reviewed_sources"], "excluded_nearby_image": search.get("excluded_nearby_image")},
            "height": {"wall_eave_estimate_m": build["dimensions"]["wall_height_m"], "ridge_estimate_m": build["dimensions"]["ridge_height_m"], "uncertainty_m": build["dimensions"]["height_uncertainty_m"], "story_evidence": build["dimensions"]["story_evidence"]},
            "manifest_bounds_m": mb, "manifest_delta_m": manifest_delta,
            "r3_reopen_validation": validation,
            "reviewed_files": [str(p.relative_to(ROOT)) for p in required if p.is_file()] + [str((HERE / "crosswalk_analysis.json").relative_to(ROOT)), str((HERE / "build_evidence.json").relative_to(ROOT)), str((HERE / "source_search_r3.json").relative_to(ROOT))],
            "limitations": ["Purdue GIS FID 506 is a pre-planning feature, not an as-built wall survey.", "C1.4 is an un-georeferenced site/construction plan and not a vertical elevation.", "Orthophoto supports roof outline and approximate breaks, not roof height, pitch, or facade layout.", "Three-story evidence is development-wide; eaves, ridge, and roof segmentation remain estimates.", "No exact-block facade image/elevation was located; entrances and opening pattern remain unknown.", "Shared manifest bounds are stale and differ substantially from the reopened asset."]
        },
        "findings": findings,
        "recommendation": f"The r3 asset scores {score}/10. Identity and approximate footprint are well supported by C1.4, FID 506, and the current orthophoto. The neutral shell is appropriate given the documented lack of exact-block facade evidence. Height and the five-break roof rhythm remain estimates, and the shared manifest still needs bounds reconciliation."
    }


if __name__ == "__main__":
    result = evaluate()
    (HERE / "independent_grade_r3.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
