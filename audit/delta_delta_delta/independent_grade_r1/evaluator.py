"""Independent evaluation of the frozen Delta Delta Delta library."""
import hashlib
import json
import math
from pathlib import Path

from shapely.geometry import Polygon

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ASSET_ID = "massing_house_301841333_affe21e"
asset_path = ROOT / "modular" / "buildings" / f"{ASSET_ID}.blend"
probe = json.loads((HERE / "fresh_probe.json").read_text(encoding="utf-8"))
evidence = json.loads((ROOT / "audit" / "delta_delta_delta" / "evidence.json").read_text(encoding="utf-8"))
geojson = json.loads((ROOT / "audit" / "delta_delta_delta" / "sources" / "purdue_building_fid_753.geojson").read_text(encoding="utf-8"))

origin = evidence["placement"]["origin_xy_m"]
feature = geojson["features"][0]
ring = feature["geometry"]["coordinates"][0]
gis_local = []
for lon, lat in ring:
    x = (lon + 86.9137) * 111412.84 * math.cos(math.radians(40.4274))
    y = (lat - 40.4274) * 111040.0
    gis_local.append((x - origin[0], y - origin[1]))
gis_poly = Polygon(gis_local)
model_poly = Polygon(probe["foundation_outline_local_xy_m"])
intersection = gis_poly.intersection(model_poly).area
union = gis_poly.union(model_poly).area
gis_comparison = {
    "fid": feature["properties"]["FID"],
    "model_ring_vertices": len(probe["foundation_outline_local_xy_m"]),
    "gis_ring_vertices_including_closure": len(ring),
    "iou": intersection / union,
    "symmetric_hausdorff_m": gis_poly.hausdorff_distance(model_poly),
    "centroid_delta_m": [model_poly.centroid.x - gis_poly.centroid.x,
                         model_poly.centroid.y - gis_poly.centroid.y],
    "caveat": "Model foundation ring was generated from this same GIS polygon; agreement verifies projection/recentering/serialization, not independent correctness of the wall line or FID identity.",
}

sha = hashlib.sha256(asset_path.read_bytes()).hexdigest()
checks = {
    "sha_matches_frozen_candidate": sha == probe["expected_sha256"] == evidence["asset_sha256"],
    "fresh_open_expected_scene_and_collection": probe["scene"] == f"Building_{ASSET_ID}" and probe["collection"] == f"Asset_{ASSET_ID}",
    "portable_without_linked_library_or_external_images": not probe["linked_libraries"] and not probe["unpacked_external_images"],
    "independent_gis_overlay_computed": gis_poly.is_valid and model_poly.is_valid and gis_comparison["iou"] > 0.999,
}
if not all(checks.values()):
    raise RuntimeError(f"A fresh-open or integrity check failed: {checks}")

criteria = [
    {
        "criterion": "Correct identity and source-backed footprint",
        "score": 1.8,
        "max_score": 2.0,
        "evidence": "Purdue GIS FID 753 attributes name Delta Delta Delta at 1200 Tower Dr; Purdue's current FSCL directory links the active Gamma Iota chapter; a current map place result also identifies Delta Delta Delta at the GIS coordinate. The official chapter-home page itself provides no address or architecture. The Street View panorama is visually attributed to the same house in the evidence package, but its viewpoint card says 898 Tower Dr, leaving an unresolved address mismatch.",
        "findings": "Identity is well supported by GIS, current chapter listing and map place result, with a small location-label uncertainty. The footprint is source-derived and is not independent confirmation that the chosen feature is the house's true structural wall line.",
    },
    {
        "criterion": "Position, orientation, and scale/dimensions",
        "score": 1.8,
        "max_score": 2.0,
        "evidence": f"The local foundation ring independently recomputed from the fresh-open asset matches the GIS polygon with IoU {gis_comparison['iou']:.9f} and Hausdorff distance {gis_comparison['symmetric_hausdorff_m']:.9f} m. The local coordinate origin derives from the GIS polygon centroid; the mapped place-point offset is recorded as 0.2273 m.",
        "findings": "Near-perfect ring agreement is a same-source transform/serialization check because the mesh was generated from the same GIS polygon. The campus Placement marker has not yet been integrated or fresh-open checked in the master, and exact wall registration/dimensions are not independently surveyed.",
    },
    {
        "criterion": "Evidence-backed height, floors, and roof form",
        "score": 1.3,
        "max_score": 2.0,
        "evidence": "The candidate models two occupied levels and a low, dark roof consistent with the described current Street View silhouette. The measured asset bounds reach 10.05 m in local Z.",
        "findings": "Two floors and 10.05 m are visual estimates, not measured elevations; Purdue GIS reports NUM_LEVELS=1 and its significance is unresolved. Roof pitch and ridge height lack plans or survey evidence.",
    },
    {
        "criterion": "Facade, entrances, and distinctive architecture",
        "score": 1.6,
        "max_score": 2.0,
        "evidence": "The render shows buff masonry, lower arched windows, upper rectangular windows, a central rounded portico with four columns, balcony rail, double doors, and broad entrance stairs. The source imagery description supports these overall features.",
        "findings": "Facade rhythm and material blocks are simplified; no measured elevations were found. A distinctive Greek-letter/three-triangle feature is reported in the source description but does not read clearly in the supplied front render. Interior is schematic, with generic halls/partitions/stairs/tables and no verified plan.",
    },
    {
        "criterion": "Modular export, portability, and complete evidence",
        "score": 1.8,
        "max_score": 2.0,
        "evidence": f"Independent fresh-open in Blender {probe['blender_version']} found the expected scene/collection, {probe['collection_object_count']} objects ({probe['mesh_object_count']} mesh objects), nine used procedural material families, no linked libraries, and no unpacked external images. The asset preserves the stable library path and records its local origin, source register, uncertainty, and fresh-open checks.",
        "findings": "The master Placement marker and shared manifest still need root integration and fresh-open validation. Height, roof, street-number crosswalk, and room-layout uncertainties are explicitly recorded.",
    },
]
score = round(sum(item["score"] for item in criteria), 1)
result = {
    "building_id": ASSET_ID,
    "building_name": "Delta Delta Delta (Gamma Iota)",
    "grade": "R1",
    "independent": True,
    "score": score,
    "max_score": 10,
    "pass_threshold": 8.0,
    "pass": score >= 8.0,
    "asset_sha256": sha,
    "checks": checks,
    "criteria": criteria,
    "gis_comparison": gis_comparison,
    "fresh_open": {
        "blender_version": probe["blender_version"],
        "scene": probe["scene"],
        "collection": probe["collection"],
        "collection_object_count": probe["collection_object_count"],
        "mesh_object_count": probe["mesh_object_count"],
        "evaluated_local_bounds_m": probe["evaluated_local_bounds_m"],
        "materials": probe["material_names"],
        "unpacked_external_images": probe["unpacked_external_images"],
        "linked_libraries": probe["linked_libraries"],
    },
    "findings": [
        "The candidate meets the independent 8/10 gate for the available evidence.",
        "Purdue GIS FID 753 and current Gamma Iota chapter identity are supported, but the 1200 Tower Dr GIS/map label versus 898 Tower Dr panorama card still needs reconciliation.",
        "The GIS footprint comparison checks the same polygon used to construct the model, so it does not independently establish structural-wall fidelity.",
        "Floor count, 10.05 m height, roof form/dimensions, and interior plan remain estimated; GIS NUM_LEVELS=1 conflicts with the two-level imagery interpretation.",
        "The master Placement marker is pending root integration and has not contributed to this asset-only score beyond the small placement deduction.",
    ],
    "render_review": "audit/delta_delta_delta/delta_delta_delta_front.png",
    "source_register": "audit/delta_delta_delta/source_register.md",
}
(HERE / "result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
(HERE / "gis_comparison_independent.json").write_text(json.dumps(gis_comparison, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"score": score, "pass": result["pass"], "gis_comparison": gis_comparison}, indent=2))
