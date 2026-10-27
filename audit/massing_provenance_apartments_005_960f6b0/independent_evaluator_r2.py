"""Fresh independent r2 rubric evaluator for Provenance Apartments 005.

Checks the saved Blender asset against Purdue GIS FID 506, County plan C1.4,
Indiana 2025 orthophoto, Studio M project imagery and the full AGENT.md rubric.
FID 506 is a strong Building F / 143 crosswalk, but is still a pre-planning
polygon and is not treated as a surveyed as-built wall line.
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


def readj(p):
    return json.loads(Path(p).read_text(encoding="utf-8-sig"))


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
        "print('PROVENANCE_R2='+json.dumps(s))"
    )
    cp = subprocess.run([str(BLENDER), "--background", "--python-expr", expr],
                        cwd=ROOT, capture_output=True, text=True, timeout=180)
    if cp.returncode:
        raise RuntimeError("Blender reopen failed: " + cp.stderr[-1200:])
    match = re.search(r"PROVENANCE_R2=(\{[^\r\n]*\})", cp.stdout)
    if not match:
        raise RuntimeError("No Blender direct snapshot: " + cp.stdout[-1200:])
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
    base = d["base_vertices"][:len(expected)]
    residuals = [math.dist(p, (v[0], v[1])) for p, v in zip(expected, base)]
    max_residual = max(residuals)
    dims = [max(p[i] for p in expected) - min(p[i] for p in expected) for i in range(2)]
    bounds = d["bounds"]
    manifest = readj(ROOT / "modular" / "manifest.json")
    entry = next(e for e in manifest["assets"] if e["id"] == ID)
    mb = entry["bounds_world_m"]
    manifest_delta = [[bounds[i][j] - mb[i][j] for j in range(2)] for i in range(3)]
    max_manifest_delta = max(abs(x) for row in manifest_delta for x in row)
    crosswalk = readj(HERE / "crosswalk_analysis.json")
    build = readj(HERE / "build_evidence.json")
    validation = readj(HERE / "reopen_validation.json")
    plan = srcdir / "county_provenance_phase1_2_construction_plans.pdf"
    plan_crop = srcdir / "county_plan_sheet_C1_4_apartment_cluster.png"
    ortho = HERE / "indiana_current_orthophoto_2025_fid506_overlay.jpg"
    renders = [HERE / "preview_southwest.png", HERE / "preview_top.png"]
    photos = [srcdir / n for n in ("studio_m_photo_1.jpg", "studio_m_photo_2.jpg", "studio_m_photo_poi26.jpg")]
    assert d["version"].startswith("5.2.3")
    assert d["scene"] == f"Building_{ID}" and d["collection"] == f"Asset_{ID}"
    assert d["collection_count"] == 1 and d["type"] == "MESH"
    assert attrs["FID"] == 506 and attrs["BUILDING_N"] == "Building F"
    assert attrs["BLDG_ABBR"] == "143" and attrs["Layer"] == "BLDG Building Pre-planning"
    assert len(expected) == 32 and max_residual < 0.001
    assert all(p.is_file() for p in [plan, plan_crop, ortho] + renders + photos)

    criteria = [
        {
            "criterion": "Correct identity and source-backed footprint",
            "score": 1.8, "max_score": 2.0,
            "status": "Building F / 143 identity is strongly cross-checked; GIS ring remains a pre-planning roof/wall proxy, not an as-built survey",
            "evidence": [
                "Tippecanoe County approved construction-plan sheet C1.4 labels the central block BLDG F / 143 between BLDG E / 144 and BLDG G / 142. The sheet is a detailed site/construction plan but is not georeferenced or an as-built wall survey.",
                f"Purdue GIS FID {attrs['FID']} is Building F / abbreviation 143, with layer {attrs['Layer']!r}; its address field is blank and the feature is pre-planning. The no-warp overlay of its transformed ring follows the central Building F roof in Indiana's 2025 orthophoto.",
                f"The stable .005 assignment is supported by the inherited proxy center: FID 506 centroid is {crosswalk['candidate_polygon_centroid_distances_m'][6]['distance']:.2f} m away, while next-nearest FID 501 / Building E is {crosswalk['candidate_polygon_centroid_distances_m'][1]['distance']:.2f} m away. Plan label and current imagery independently corroborate this crosswalk.",
                f"The 32 model base-ring vertices reproduce Purdue GIS FID 506 after the documented transformation within {max_residual:.6f} m maximum residual. The orthophoto outlines roof/eaves, so exact structural wall registration remains uncertain."
            ],
            "findings": ["Retain explicit uncertainty that the pre-planning GIS and orthophoto roof outline are not a surveyed as-built wall line."]
        },
        {
            "criterion": "Position, orientation, and scale/dimensions",
            "score": 1.7, "max_score": 2.0,
            "status": "candidate plan geometry and campus placement are corroborated by site plan and current roof imagery; exact wall dimensions are approximate",
            "evidence": [
                f"Blender 5.2.3 reopened mesh bounds are X {bounds[0][0]:.3f}..{bounds[0][1]:.3f} m, Y {bounds[1][0]:.3f}..{bounds[1][1]:.3f} m and Z {bounds[2][0]:.3f}..{bounds[2][1]:.3f} m. The transformed GIS structural candidate envelope is {dims[0]:.2f} m by {dims[1]:.2f} m.",
                "Plan C1.4 supplies the neighboring block order and orientation; the no-fit 2025 orthophoto overlay shows close registration with the central roof. The plan is not georeferenced, and campus XY uses a local approximation; neither source confirms the exact exterior wall line."
            ],
            "findings": ["Use the reported footprint dimensions as approximate until a wall survey or georeferenced as-built plan is available; facade projections/roof eaves can differ from the base ring."]
        },
        {
            "criterion": "Evidence-backed height, floors, and roof form",
            "score": 1.1, "max_score": 2.0,
            "status": "three stories and repeated gables have project-level evidence; heights, segmentation and pitch are estimates",
            "evidence": [
                "Studio M's project description says the community has seven three-story buildings, supporting the model's storey count at development level. Project photos show repeated gabled forms, and the current orthophoto roof has a repeated segmented/gable pattern.",
                f"The model uses {build['dimensions']['wall_height_m']:.1f} m eaves and {build['dimensions']['ridge_height_m']:.1f} m ridge, both estimates with documented ±{build['dimensions']['height_uncertainty_m']['ridge_plus_minus']:.1f} m uncertainty. No building-specific elevation or measured vertical source was found.",
                "The five-break roof rhythm is consistent with imagery at a broad level, but ridge positions, pitch, exact gable count and the roof-to-facade alignment are not measured for this individual block."
            ],
            "findings": ["Keep 8.9 m eaves, 11.4 m ridge and the five-segment roof layout labeled as estimates; no building-specific elevation validates them."]
        },
        {
            "criterion": "Facade, entrances, and distinctive architecture",
            "score": 1.0, "max_score": 2.0,
            "status": "general apartment facade vocabulary is supported; detail placement and color/composition are generalized",
            "evidence": [
                "Studio M project photos support brick facades, dark framed windows/glazing, selected balconies, accent bays, shallow entry canopies and repeated gables at the development level.",
                "The rebuilt render includes window frames/mullions, three accent bays, selected balconies and two glazed entries/canopies. These elements now convey more of the project character, but the photos do not label Building F; exact locations, counts and rhythm are generalized. The render's facade tone and large blank end wall are not verified against a Building F elevation.",
                "No building-specific facade schedule, elevation or entrance map is included; the site-plan sheet does not document facade elements."
            ],
            "findings": ["Treat facade feature positions, material/color, and exact opening rhythm as schematic until an attributable Building F elevation or photo is available."]
        },
        {
            "criterion": "Modular export, portability, and complete evidence",
            "score": 1.5, "max_score": 2.0,
            "status": "saved asset reopens and evidence is extensive; shared manifest bounds still describe the superseded proxy",
            "evidence": [
                f"Direct Blender {d['version']} reopen confirms the expected scene/collection, one mesh ({d['vertices']} vertices, {d['faces']} faces), {len(d['modifiers'])} modifiers, {len(d['unpacked_images'])} unpacked file-linked images and {d['libraries']} linked libraries. The separate reopen validation reports the 32 point match within 0.000060 m, zero modifiers, and portable dependencies.",
                "The dedicated evidence includes raw Purdue GIS FID 506 and layer metadata, County C1.4 plan PDF/crops, current Indiana orthophoto and registration overlay, source register, Studio M photos, build result, two renders and reopened validation.",
                f"The shared manifest still declares old bounds {mb}; reopened mesh bounds are {bounds}. The maximum component difference is {max_manifest_delta:.2f} m, including the old over-wide proxy extent. The coordinator-owned manifest needs reconciliation before treating its bounds as current."
            ],
            "findings": ["Coordinator should reconcile shared manifest bounds to the rebuilt asset after accepting the source crosswalk; do not use the old broad proxy bounds for integration."]
        }
    ]
    score = round(sum(c["score"] for c in criteria), 2)
    findings = [f for c in criteria for f in c["findings"]]
    return {
        "building_id": ID,
        "building_name": "Provenance Apartments 005 / Building F (143)",
        "reviewer": "independent r2 evaluator; County plan C1.4, Purdue GIS FID 506, Indiana 2025 orthophoto overlay, Studio M project photos, current renders and Blender 5.2.3 direct reopen",
        "score": score, "max_score": 10, "passing_standard": 8,
        "criteria": criteria,
        "evidence": {
            "asset_path": str(ASSET.relative_to(ROOT)),
            "blender": d["version"], "reopened_scene": d["scene"], "reopened_collection": d["collection"],
            "direct_reopen_measurements": {k: d[k] for k in ("object", "type", "collection_count", "vertices", "faces", "bounds", "materials", "unpacked_images", "libraries", "modifiers")},
            "source_identity": {k: attrs.get(k) for k in ("FID", "BUILDING_N", "BLDG_ABBR", "Layer", "BUILDING_1", "ADDRESS", "NUM_LEVELS", "BUILT", "OCCUPIED")},
            "candidate_footprint": {"source_crs": "EPSG:3857; inverse-projected and transformed with the documented local campus approximation", "ring_vertex_count": len(expected), "candidate_envelope_m": dims, "vertex_residuals_m": residuals, "max_vertex_residual_m": max_residual, "as_built_wall_line": "uncertain; source is pre-planning and image shows roof/eaves"},
            "crosswalk": crosswalk,
            "height": {"wall_eave_estimate_m": build["dimensions"]["wall_height_m"], "ridge_estimate_m": build["dimensions"]["ridge_height_m"], "uncertainty_m": build["dimensions"]["height_uncertainty_m"], "three_story_source": build["dimensions"]["story_evidence"]},
            "manifest_bounds_m": mb,
            "reviewed_files": [str((HERE / "crosswalk_analysis.json").relative_to(ROOT)), str((HERE / "build_evidence.json").relative_to(ROOT)), str((HERE / "reopen_validation.json").relative_to(ROOT)), str(plan.relative_to(ROOT)), str(plan_crop.relative_to(ROOT)), str(ortho.relative_to(ROOT))] + [str(p.relative_to(ROOT)) for p in renders + photos],
            "limitations": ["FID 506 / Building F / 143 crosswalk is strongly supported by explicit plan label, inherited location proximity and current roof imagery, but its Purdue layer remains pre-planning.", "Plan C1.4 is site/construction information, not a georeferenced as-built survey or elevation.", "Current orthophoto shows roof/eaves rather than exact wall line.", "Height values and roof segmentation remain estimates; three-story evidence is at community level.", "Facade details use development-wide photos and are generalized for Building F.", "Shared manifest bounds still describe the earlier proxy and differ substantially from the rebuilt asset."]
        },
        "findings": findings,
        "recommendation": f"The asset scores {score}/10. The County C1.4 label and current orthophoto make the Building F/143 crosswalk substantially stronger than the prior review, and its candidate plan location is well supported. Wall-line registration remains approximate; verticals and roof segmentation are estimated; facade positions are generalized; and the shared manifest bounds still need coordinator reconciliation."
    }


if __name__ == "__main__":
    result = evaluate()
    (HERE / "independent_grade_r2.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
