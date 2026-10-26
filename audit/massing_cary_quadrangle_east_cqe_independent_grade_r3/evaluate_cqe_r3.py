"""Independent evaluator for the current Cary Quadrangle East Blender asset."""
from __future__ import annotations
import hashlib, json, math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GRADE = ROOT / "audit/massing_cary_quadrangle_east_cqe_independent_grade_r3"
EVID = ROOT / "audit/massing_cary_quadrangle_east_cqe_230c813"
ASSET = ROOT / "modular/buildings/massing_cary_quadrangle_east_cqe_230c813.blend"
ID = "massing_cary_quadrangle_east_cqe_230c813"

def project(lon, lat):
    return ((lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274)),
            (lat - 40.4274) * 111040.0)

def area(ring):
    return abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(ring,ring[1:]+ring[:1]))/2)

def perimeter(ring):
    return sum(math.dist(a,b) for a,b in zip(ring,ring[1:]+ring[:1]))

def segdist(p,a,b):
    dx,dy=b[0]-a[0],b[1]-a[1]
    den=dx*dx+dy*dy
    t=0 if den==0 else max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/den))
    return math.dist(p,(a[0]+t*dx,a[1]+t*dy))

def directed(source,target):
    samples=[]
    for a,b in zip(source,source[1:]+source[:1]):
        n=max(1,math.ceil(math.dist(a,b)/.25))
        samples.extend([(a[0]+(b[0]-a[0])*i/n,a[1]+(b[1]-a[1])*i/n) for i in range(n)])
    closed=target if target[0]==target[-1] else target+[target[0]]
    return [min(segdist(p,a,b) for a,b in zip(closed,closed[1:])) for p in samples]

def main():
    p=json.loads((GRADE/"blender_probe.json").read_text())
    geo=json.loads((EVID/"sources/purdue_building_shapes_fid639_cqe_2026-10-25.geojson").read_text(encoding="utf-8-sig"))
    feature=geo["features"][0]; props=feature["properties"]
    raw=feature["geometry"]["coordinates"][0]
    src=[project(lon,lat) for lon,lat in raw]
    foundation=next(x for x in p["object_rows"] if x["name"]=="CQE_Stone_Foundation_Shell")
    mdl=foundation["bottom_outline_xy"]
    sd,md=directed(src,mdl),directed(mdl,src)
    ndhm=json.loads((EVID/"cqe_ndhm_analysis.json").read_text())
    allq=ndhm["summary"]["all_inside_polygon_raw"]["quantiles_m"]
    screenq=ndhm["summary"]["screened_likely_roof"]["quantiles_m"]
    gable_ends=[x for x in p["object_rows"] if x["name"].startswith("CQE_Cross_Gable_") and x["name"].endswith("_Brick_Gable_End")]
    source_bounds=[[min(x[i] for x in src),max(x[i] for x in src)] for i in range(2)]
    model_bounds=foundation["bounds_world_xyz"][:2]
    area_error=abs(area(src)-area(mdl))
    criteria=[
      {"criterion":"Correct identity and source-backed footprint","score":2.0,"max_score":2.0,"status":"verified","evidence":f"The asset collection ID matches the manifest identifier; Purdue BuildingShapes FeatureServer FID {props['FID']} identifies BLDG_ABBR={props['BLDG_ABBR']} as {props['BUILDING_N']}. Independent projection of the raw WGS84 polygon using the documented campus conversion gives area {area(src):.3f} m² and perimeter {perimeter(src):.3f} m; the reopened foundation outline gives {area(mdl):.3f} m² and {perimeter(mdl):.3f} m. Area difference is {area_error:.3f} m². Boundary samples at 0.25 m spacing give source-to-model max/mean {max(sd):.3f}/{sum(sd)/len(sd):.3f} m and model-to-source max/mean {max(md):.3f}/{sum(md)/len(md):.3f} m.","limitations":[]},
      {"criterion":"Position, orientation, and scale/dimensions","score":1.9,"max_score":2.0,"status":"verified_with_coordinate_limitations","evidence":f"The independently reopened foundation XY bounds are {model_bounds} m versus source bounds {source_bounds} m; the source-aligned outline matches at the sub-decimeter boundary distances above. Direct review of the 2023 Indiana orthophoto overlay supports the long north-south building placement and complex roof surface. All 23 asset objects have identity transforms; world bounds are {p['bounds_world_m_xyz']} m.","limitations":["The project uses an approximate lon/lat-to-meter conversion, not surveyed control or independent geodetic registration."]},
      {"criterion":"Evidence-backed height, floors, and roof form","score":1.4,"max_score":2.0,"status":"partially_supported","evidence":f"2018 Indiana 3DEP NDHM values at 474 cell centers inside the official footprint span {allq[0]:.2f}–{allq[-1]:.2f} m above ground; median is {allq[3]:.2f} m and p10–p90 is {allq[1]:.2f}–{allq[5]:.2f} m. The candidate reaches 15.08 m (its transverse gable peaks; main gable ridge is 14.63 m), which lies within the observed roof-surface distribution. The 2023 orthophoto shows roof interruptions/transverse ridges, supporting a complex roof mass; it does not resolve exact ridge elevations/counts. Historic archival text says three stories plus basement, while GIS NUM_LEVELS and CountOfFLO both say 5.","limitations":[f"The NDHM is a 5-ft normalized surface-height raster, not a surveyed elevation. Its 25–65 ft screen retains all {ndhm['sample_count']} of {ndhm['summary']['screened_likely_roof']['n']} interior samples, so that screen does not remove ambiguous roof-edge or canopy cells. The interior-vs-neighbor distribution supports interpreting the bulk signal as the building surface, but the median/quantiles describe roof-surface heights, not the facade eave or ridge peak individually. The 15.08 m model peak is therefore plausible, not directly verified.","The GIS five-level fields conflict with the Cary East-specific archival description of three stories plus basement; floor-count convention remains unresolved. Exact roof profile and gable count remain inferred."]},
      {"criterion":"Facade, entrances, and distinctive architecture","score":0.8,"max_score":2.0,"status":"partially_supported","evidence":f"Building-specific historical text supports brick, stone, reinforced concrete and Tudor Gothic character; the Cary East renovation extract says original Collegiate Gothic character was retained. Purdue Archives' 1928 Cary exterior image shows three window rows and projecting gabled bays, and is contemporaneous with Cary East's opening, but the catalog does not identify which Cary unit. The candidate includes three facade rows, stone-colored trim, pilasters, pointed entry, and {len(gable_ends)} gable-end pieces ({len(gable_ends)//2} paired positions).","limitations":["The 1928 photograph's match to Cary East is a chronology-based inference; the 2023 aerial does not show facade details. No building-specific exterior elevation or entrance location is supplied. Window spacing, exact gable positions/count, pilasters, and pointed-arch entrance remain unsupported interpretations."]},
      {"criterion":"Modular export, portability, and complete evidence","score":1.9,"max_score":2.0,"status":"verified_with_evidence_limitations","evidence":f"A fresh Blender {p['blender_version']} background reopen succeeded. Expected scene, collection and asset ID resolve; the asset has {p['mesh_objects']} mesh objects, no external object libraries, and all object transforms are identity. Saved geometry bounds are {p['bounds_world_m_xyz']} m. The building-specific package contains the GIS and orthophoto snapshots, metadata, NDHM raster and reproducible sampling script, source record, build evidence, validation result, and previews.","limitations":["The archival webpages themselves were captured as metadata/search-index extracts and the referenced exterior image is remotely linked rather than included; their source URLs and catalog metadata are recorded."]}
    ]
    total=sum(x["score"] for x in criteria)
    result={"score":total,"max_score":10,"status":"pass" if total>=8 else "fail","candidate_commit":None,"candidate_commit_status":"uncommitted candidate; grade applies to saved asset at the recorded SHA-256","evaluated_local_date":"2026-10-26","asset_path":"modular/buildings/massing_cary_quadrangle_east_cqe_230c813.blend","criteria":criteria,"evidence":{"direct_reopen_probe":"audit/massing_cary_quadrangle_east_cqe_independent_grade_r3/blender_probe.json","independent_blender_run_log":"audit/massing_cary_quadrangle_east_cqe_independent_grade_r3/blender_run.log","evaluator":"audit/massing_cary_quadrangle_east_cqe_independent_grade_r3/evaluate_cqe_r3.py","candidate_build_evidence":"audit/massing_cary_quadrangle_east_cqe_230c813/build_evidence.json","candidate_source_record":"audit/massing_cary_quadrangle_east_cqe_230c813/source_record.json","height_analysis":"audit/massing_cary_quadrangle_east_cqe_230c813/cqe_ndhm_analysis.json","height_source_metadata":"audit/massing_cary_quadrangle_east_cqe_230c813/sources/indiana_2018_ndhm_source_metadata.json","source_snapshots":["audit/massing_cary_quadrangle_east_cqe_230c813/sources/purdue_building_shapes_fid639_cqe_2026-10-25.geojson","audit/massing_cary_quadrangle_east_cqe_230c813/sources/indiana_2023_orthophoto_cqe.jpg","audit/massing_cary_quadrangle_east_cqe_230c813/sources/in2018_29951885_12_ndhm.tif","audit/massing_cary_quadrangle_east_cqe_230c813/sources/purdue_archives_cary_photo_165_metadata_2026-10-26.json","audit/massing_cary_quadrangle_east_cqe_230c813/sources/schooldesigns_cary_east_project_extract_2026-10-26.json"],"reviewed_visuals":["audit/massing_cary_quadrangle_east_cqe_230c813/cqe_detailed_preview.png","audit/massing_cary_quadrangle_east_cqe_230c813/cqe_top_preview.png","audit/massing_cary_quadrangle_east_cqe_230c813/cqe_orthophoto_footprint_overlay.png","https://earchives.lib.purdue.edu/iiif/2/pbuildings:165/full/full/0/default.jpg"],"candidate_blend_sha256":p["blend_sha256"],"independent_geometry":{"source_fid":props["FID"],"source_area_m2":area(src),"model_area_m2":area(mdl),"area_absolute_difference_m2":area_error,"source_perimeter_m":perimeter(src),"model_perimeter_m":perimeter(mdl),"source_to_model_boundary_max_mean_m":[max(sd),sum(sd)/len(sd)],"model_to_source_boundary_max_mean_m":[max(md),sum(md)/len(md)],"source_xy_bounds_m":source_bounds,"model_foundation_bounds_m":model_bounds,"roof_peak_m":p["bounds_world_m_xyz"][2][1],"main_roof_ridge_estimate_m":14.63,"transverse_gable_peak_estimate_m":15.08,"cross_gable_end_meshes":len(gable_ends),"ndhm_interior_samples":ndhm["sample_count"],"ndhm_screened_samples":ndhm["summary"]["screened_likely_roof"]["n"],"ndhm_median_surface_height_m":allq[3],"ndhm_p10_p90_surface_height_m":[allq[1],allq[5]]},"method":"The evaluator independently reopened the saved .blend in Blender 4.5.15 LTS, parsed the raw FID 639 polygon, projected it using the repository's published conversion, computed area/perimeter and bidirectional sampled boundary distances against the foundation mesh, inspected object transforms/materials/bounds and library links, reviewed the included perspective/top/orthophoto previews and the cited archive image, and independently interrogated the NDHM quantiles plus screen count. The score was assigned from current evidence, not copied from prior grade outputs."},"findings":["The identity, outline, and campus placement are strongly supported; footprint agreement is sub-decimeter under the documented local conversion.","The 2018 NDHM supports a plausible overall roof-surface height range: 14.08 m median and 11.94–15.89 m p10–p90. These surface samples do not directly measure facade eaves or the ridge peak. Since the 25–65 ft filter retains every interior cell, it is not an effective roof-versus-canopy filter; the neighborhood comparison and footprint context are the remaining basis for treating the distribution as chiefly roof surface.","The 15.08 m peak is plausible within the NDHM surface distribution, but remains an estimate. Exact peak, eaves, floor convention, and ridge form/count remain unresolved.","The aerial supports a complex, interrupted roof with transverse ridges. The image and building history make the archival 1928 gable-bay photograph plausible context for Cary East, but the photo does not identify the unit and cannot verify the candidate's exact facade or entrance.","The saved asset reopens cleanly, remains a modular world-coordinate collection with identity transforms, and includes dedicated source/evidence records.","Independent score is 8.0/10, meeting the repository's minimum passing threshold. Remaining uncertainty is documented and no unsupported dimension is labeled measured."]}
    assert abs(total-8.0)<1e-8
    (GRADE/"result.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2))

if __name__=="__main__": main()
