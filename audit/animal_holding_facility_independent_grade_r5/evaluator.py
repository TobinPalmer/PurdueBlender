"""Independent AHF R5 evaluator. Reads saved probes from raw source and reopened Blender library."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
AUDIT=Path(__file__).resolve().parent

def evaluate():
    blender=json.loads((AUDIT/"blender_probe.json").read_text(encoding="utf-8"))
    source=json.loads((AUDIT/"source_probe.json").read_text(encoding="utf-8"))
    built=json.loads((ROOT/"audit/animal_holding_facility/build_evidence.json").read_text(encoding="utf-8"))
    facade=json.loads((ROOT/"audit/animal_holding_facility/sources/ahf_facade_source_search_2026-10-25.json").read_text(encoding="utf-8"))
    assert blender["candidate_commit"]=="c40be18b4f6c70ae8a101d84549b3c89f25c0db5"
    assert blender["result"]=="PASS" and blender["fresh_scene_link"]["pass"]
    assert blender["boundary_edges"]==0 and blender["nonmanifold_edges"]==0
    assert source["ndhm"]["samples"]["north_main"]["n"]==614
    assert source["ndhm"]["samples"]["south_addition"]["n"]==359
    assert facade["retrieved"]=="2026-10-25"

    criteria=[
      {"name":"Correct identity and source-backed footprint","points":2.0,"max_points":2,
       "assessment":f"Purdue GIS FID 266 and Purdue facilities history identify AHF; a separate Indiana 2018 footprint is also recorded. Independent conversion of all {source['source_outline_vertex_count']} source vertices yields the published local outline, and every transformed GIS outline vertex appears in the reopened mesh within {blender['source_ring_vertex_nearest_mesh_vertex_m']['max']:.6f} m."},
      {"name":"Position, orientation, and scale/dimensions","points":2.0,"max_points":2,
       "assessment":f"Reopened world bounds are x {blender['bounds_world_m'][0]}, y {blender['bounds_world_m'][1]}, z {blender['bounds_world_m'][2]} m. The footprint vertex sequence preserves plan orientation; the roughly 0.18 m outer expansion is consistent with the documented wall/trim thickness. Independent GIS footprints corroborate site location (0.50 m centroid offset and 1.74 m max symmetric boundary residual in the previous source comparison)."},
      {"name":"Evidence-backed height, floors, and roof form","points":1.75,"max_points":2,
       "assessment":f"Independent raw 2018 Indiana 5-ft NDHM sampling reproduces n=614 north cells (median {source['ndhm']['samples']['north_main']['median_m']:.3f} m) and n=359 south cells (median {source['ndhm']['samples']['south_addition']['median_m']:.3f} m). Regressions from four spatial-bin sizes reproduce a stable south-zone Y surface trend of about -4.0% to -4.8%; the R5 model replaces the prior level south plane with a corresponding low-slope plane while keeping the north/main roof at its median. Purdue GIS reports one level. NDHM is a normalized surface raster rather than a roof/eave survey, and the roof-zone seam and structural pitch remain uncertain."},
      {"name":"Facade, entrances, and distinctive architecture","points":0.0,"max_points":2,
       "assessment":"The reopened asset remains a neutral, unfenestrated envelope with no entrance or facade features. The dated public-source search documents a null image field and no indexed AHF-specific exterior, elevation, or plan; the search is explicitly non-exhaustive. With no building-specific visual/elevation evidence, this criterion remains unverified and receives no credit."},
      {"name":"Modular export, portability, and complete evidence","points":2.0,"max_points":2,
       "assessment":f"{bpy_version()} reopened the saved candidate: the expected named collection contains {blender['object_count']} mesh object with {blender['vertices']} vertices/{blender['faces']} faces, zero boundary and non-manifold edges, no modifiers or external image dependencies, and it links into a fresh factory-startup scene. Evidence includes raw GIS/orthophoto/NDHM snapshots, reproducible scripts, height/profile analyses, reopening checks and preview."}
    ]
    score=round(sum(c["points"] for c in criteria),2)
    return {
      "building_id":"massing_animal_holding_facility_4733f46",
      "candidate_commit":"c40be18b4f6c70ae8a101d84549b3c89f25c0db5",
      "score":score,"max_score":10,"passing_threshold":8,"pass":score>=8,
      "criteria":criteria,
      "evidence":{
        "blender_probe":"audit/animal_holding_facility_independent_grade_r5/blender_probe.json",
        "source_probe":"audit/animal_holding_facility_independent_grade_r5/source_probe.json",
        "render":"audit/animal_holding_facility_independent_grade_r5/reviewed_asset_preview.png (directly inspected; blank facade envelope, split north/south roof planes)",
        "orthophoto":"audit/animal_holding_facility_independent_grade_r5/reviewed_orthophoto_overlay.png (directly inspected; supports roof-tone zones only)",
        "facade_search":"audit/animal_holding_facility/sources/ahf_facade_source_search_2026-10-25.json",
        "roof_fit":"Independent recomputation from the raw official NDHM tile; see source_probe.json for counts, medians and 2.5/5/7.5/10 m bin fits.",
        "prior_grade":"audit/animal_holding_facility_independent_grade_r4/result.json (7.5/10); R5 addresses its flat south plane finding."
      },
      "findings":[
        {"severity":"blocking-for-8/10","finding":"No AHF-specific exterior photograph, measured elevation, or plan is in the documented public search; facade and entrance remain absent and unsupported. Another distinct sourced iteration or archival access is needed to earn this criterion."},
        {"severity":"minor","finding":"R5 materially improves roof-profile consistency: independently recomputed binned NDHM values show the south-zone normalized-surface trend across four scales, and the asset models that zone with a low slope. NDHM may capture roof equipment, local ground-normalization artifacts, or edge contamination; it is not structural pitch or surveyed eaves."},
        {"severity":"minor","finding":"The north/main zone is represented by a median-height plane because its weak fitted trend is not stable across bin scales. The orthophoto identifies zone colors in plan but not the exact roof seam or structure."},
        {"severity":"positive-evidence","finding":"Reopened topology is closed (0 boundary and 0 non-manifold edges), and the named asset collection links into a clean factory-startup scene without external images."}
      ]
    }

def bpy_version():
    # Version observed from the successful independent Blender 4.5.15 probe.
    return "Blender 4.5.15 LTS"

if __name__=="__main__":
    result=evaluate()
    (AUDIT/"result.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2))

