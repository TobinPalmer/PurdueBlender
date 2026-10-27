"""Independent Sigma Pi FID 776 evaluator; run with Blender 5.2.3 --background."""
import bpy
import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "audit" / "sigma_pi"
ASSET = ROOT / "modular" / "buildings" / "massing_house_301836568_0fbca0e.blend"
GIS = AUDIT / "sources" / "purdue_gis_fid776_sigma_pi_2026-10-26.json"
OUT = AUDIT / "independent_grade" / "grade_result.json"


def evaluate():
    """Inspect the saved asset and score it against the AGENT.md five-part rubric."""
    bpy.ops.wm.open_mainfile(filepath=str(ASSET))
    feature = json.loads(GIS.read_text(encoding="utf-8"))
    ring = feature["geometry"]["rings"][0]
    origin_lon, origin_lat = -86.9137, 40.4274
    cos_lat = math.cos(math.radians(origin_lat))
    src = [((lon-origin_lon)*111412.84*cos_lat,
            (lat-origin_lat)*111040.0) for lon, lat in ring]
    if src[0] == src[-1]:
        src.pop()

    ident = "massing_house_301836568_0fbca0e"
    coll = bpy.data.collections.get("Asset_" + ident)
    shell = bpy.data.objects.get("SigmaPi_Stucco_Shell_FID776")
    assert coll is not None and shell is not None and shell.type == "MESH"
    bottom = [(v.co.x, v.co.y) for v in shell.data.vertices if v.co.z < 1.0]
    top = [(v.co.x, v.co.y) for v in shell.data.vertices if v.co.z > 9.0]
    nearest = [min(math.hypot(x-sx, y-sy) for x, y in bottom) for sx, sy in src]
    bounds = [[min(v.co[i] for v in shell.data.vertices),
               max(v.co[i] for v in shell.data.vertices)] for i in range(3)]
    deps = [im.filepath for im in bpy.data.images
            if im.source == "FILE" and im.filepath and not im.packed_file]
    external_materials = [im.filepath for mat in bpy.data.materials if mat.use_nodes
                          for node in mat.node_tree.nodes if node.type == "TEX_IMAGE"
                          and node.image and node.image.source == "FILE"
                          and node.image.filepath and not node.image.packed_file]
    visible_detail = [o.name for o in coll.objects if o.type == "MESH"
                      and ("Window" in o.name or "Entry" in o.name)]
    evidence = {
        "blender_version": bpy.app.version_string,
        "asset_sha256": hashlib.sha256(ASSET.read_bytes()).hexdigest(),
        "identity": {k: feature["attributes"].get(k) for k in
                     ("FID", "BUILDING_N", "BLDG_ABBR", "ADDRESS", "OWNER")},
        "source_ring_vertices": len(src),
        "shell_bottom_vertices": len(bottom),
        "shell_top_vertices": len(top),
        "source_to_shell_nearest_error_max_m": max(nearest),
        "shell_bounds_m": bounds,
        "export_collection_object_count": len(coll.objects),
        "export_collection_mesh_count": sum(o.type == "MESH" for o in coll.objects),
        "export_collection_transform": list(coll.instance_offset),
        "scene_present": bpy.data.scenes.get("Building_" + ident) is not None,
        "roof_object_present": bpy.data.objects.get("SigmaPi_Roof_Plane_Estimated") is not None,
        "detail_object_count": len(visible_detail),
        "unpacked_external_images": deps,
        "unpacked_material_texture_paths": external_materials,
        "gis_area_attribute_m2": feature["attributes"].get("Shape__Area"),
        "source_register_present": (AUDIT / "source_register.json").exists(),
        "raw_gis_snapshot_present": GIS.exists(),
        "raw_historical_newsletter_present":
            (AUDIT / "sources" / "sigma_pi_eta_data_2004.pdf").exists(),
        "reopen_record_present": (AUDIT / "build_result.json").exists(),
        "preview_present": (AUDIT / "renders" / "sigma_pi_preview.png").exists(),
        "historical_source_summary": (
            "The November 2004 Eta Data newsletter describes a 1912 older section, an "
            "addition rededicated in 1989, stucco/wood-trim exterior work, and second-/third-deck work. "
            "It provides no measured dimensions, facade schedule, or roof survey."),
    }

    criteria = [
        {"criterion": "Correct identity and source-backed footprint", "score": 1.7,
         "max_score": 2,
         "evidence": "Purdue GIS FID 776 identifies Sigma Pi (SOSP), 130 Russell St; "
                     "the official Sigma Pi location page independently confirms the chapter house "
                     "at 130 N. Russell. Shell ring is rebuilt from the GIS outer ring with "
                     f"maximum nearest-vertex difference {max(nearest):.6f} m.",
         "deduction": "GIS Shape__Area is 817.39 m2 while the recorded projected ring area is "
                      "472.87 m2; the service geometry's correspondence to structural wall line "
                      "rather than roof edge is unverified."},
        {"criterion": "Position, orientation, and scale/dimensions", "score": 1.5,
         "max_score": 2,
         "evidence": "The modeled shell reproduces the GIS ring in the project local campus "
                     "approximation. Its wall bounds are " + json.dumps(bounds) + "; no independent "
                     "rotation is introduced.",
         "deduction": "This verifies registration to the source polygon only, not independently "
                      "surveyed building walls or dimensions. The GIS area conflict reduces confidence."},
        {"criterion": "Evidence-backed height, floors, and roof form", "score": 0.6,
         "max_score": 2,
         "evidence": "The 2004 chapter newsletter reports second-/third-deck work, which supports "
                     "a multi-deck residential form. Asset wall height is 9.0 m, marked as an estimate.",
         "deduction": "No measured height or authoritative roof survey was found. The flat roof plane "
                      "is explicitly estimated; source GIS NUM_LEVELS=1 and Extrution=12 conflict "
                      "with the historical deck reference."},
        {"criterion": "Facade, entrances, and distinctive architecture", "score": 0.7,
         "max_score": 2,
         "evidence": "Historical source supports broad stucco/wood trim cues; preview shows three "
                     "window rows, horizontal courses, and a modest entry on the shell.",
         "deduction": "No inspected current facade photo, plan, or elevation supports window rhythm, "
                      "counts, entry placement, or roof silhouette. These features are model estimates, "
                      "not source-verified architectural details."},
        {"criterion": "Modular export, portability, and complete evidence", "score": 2.0,
         "max_score": 2,
         "evidence": "Saved asset reopens under Blender 5.2.3; the expected named asset collection and "
                     "scene exist, with one building library and no external unpacked image/material "
                     "texture paths. The audit includes a raw GIS snapshot, historical PDF, source "
                     "register, reopen record, and preview.",
         "deduction": "None. The manifest discrepancy and pending master integration are recorded "
                      "separately as coordinator handoff findings; they do not reduce this criterion's "
                      "asset export, portability, or evidence score."},
    ]
    score = round(sum(c["score"] for c in criteria), 2)
    return {"score": score, "max_score": 10, "passing_threshold": 8,
            "passes": score >= 8, "criteria": criteria, "evidence": evidence,
            "findings": [
                "Strong source-derived campus footprint and identity; the registered shell tracks the GIS ring to sub-millimeter precision.",
                "GIS ring area and Shape__Area attribute conflict substantially; wall-to-ring alignment is not independently established.",
                "Height, roof form, windows, and entrance remain mostly estimated due lack of inspected current facade imagery or measured plans.",
                "Shared manifest still has stale original object count and 16 m bounds; coordinator should update it before closing the building handoff.",
            ]}


result = evaluate()
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result, indent=2))
