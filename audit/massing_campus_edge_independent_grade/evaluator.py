"""Independent Campus Edge rubric evaluator.
Run with system Python from the repository root: python audit/massing_campus_edge_independent_grade/evaluator.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GRADE = ROOT / "audit" / "massing_campus_edge_independent_grade"
BUILDING = ROOT / "audit" / "massing_campus_edge_343e3d8"
ASSET = ROOT / "modular" / "buildings" / "massing_campus_edge_343e3d8.blend"


def evaluate():
    probe = json.loads((GRADE / "probe.json").read_text(encoding="utf-8"))
    source = json.loads((BUILDING / "source_record.json").read_text(encoding="utf-8"))
    reopened = json.loads((BUILDING / "reopen_validation.json").read_text(encoding="utf-8"))
    build = json.loads((BUILDING / "build_report.json").read_text(encoding="utf-8"))

    criteria = [
        {
            "name": "Correct identity and source-backed footprint",
            "score": 2.0,
            "max_score": 2,
            "status": "verified",
            "evidence": "Directly inspected source_record.json and the saved GIS, OSM, and orthophoto snapshots. OSM way 886359911 is explicitly Campus Edge, 134 Pierce Street. Indiana 2018 LiDAR footprint OBJECTID 407824 is a matching footprint; the independently reported comparison is 0.914 IoU and 1.06 m centroid gap. The 2023 orthophoto overlay visibly confirms the roof outline. The asset shell is built from that GIS ring.",
        },
        {
            "name": "Position, orientation, and scale/dimensions",
            "score": 1.8,
            "max_score": 2,
            "status": "mostly verified; approximate projection",
            "evidence": f"Fresh Blender 4.5.15 reopen found the expected campus-world coordinates and asset bounds {probe['bounds_world_m']} m. The builder derives XY from all GIS footprint vertices with the repository's documented local geographic approximation and checks against a distinct OSM polygon. Metric accuracy is not survey-grade; rendered facade details intentionally extend beyond the structural outline.",
        },
        {
            "name": "Evidence-backed height, floors, and roof form",
            "score": 0.8,
            "max_score": 2,
            "status": "partly estimated; roof silhouette mismatch",
            "evidence": "The saved 2018 NDHM tile and analysis support an approximate roof-surface datum near 36.12 m (median; p90 about 36.88 m), with explicit caveats for 5-ft sampling, edge/tree outliers, and no surveyed eaves. Nine residential floors are visually estimated. Direct inspection of the asset and saved previews reveals one flat, continuous upper shell with a roof grid; the 2023 orthophoto and official oblique photo show multiple separated tower volumes and substantial open/recessed roof areas. Those roof steps and voids are absent, so the height proxy does not validate the roof form.",
        },
        {
            "name": "Facade, entrances, and distinctive architecture",
            "score": 1.2,
            "max_score": 2,
            "status": "photo-interpreted; major volume details missing",
            "evidence": "Official American Campus Communities photo was opened and compared directly with the saved render. The model includes a brick podium, repeated glazing, gray/charcoal panels, accent brick, balcony stacks, a canopy, and equipment. However, the photo clearly shows several distinct tower masses, recessed courts/terraces, a projecting podium with open column zones, and substantially varied tower elevations. The model merges these into a single uninterrupted footprint-wide tower shell and regularized facade grid. Door, bay, balcony, and material positions remain qualitative.",
        },
        {
            "name": "Modular export, portability, and complete evidence",
            "score": 2.0,
            "max_score": 2,
            "status": "verified",
            "evidence": f"Fresh Blender reopen reports scene {probe['scene']}, collection {probe['collection']}, stable ID {probe['collection_properties']['asset_id']}, {probe['object_count']} local mesh objects, no linked libraries, no unpacked external images, and campus-world bounds. Source record includes provider URLs, feature IDs, dates, CRS, measurement methods, source snapshots, and uncertainty. Saved model, build/reopen evidence, top/oblique previews, footprint overlay, NDHM map, official gallery image, and orthophoto are present. Evidence is complete, though some architectural claims remain explicitly approximate.",
        },
    ]
    score = round(sum(c["score"] for c in criteria), 1)
    result = {
        "building_id": "massing_campus_edge_343e3d8",
        "revision": "77404c0d660eeb94ee781be244aebffb0ee015fd",
        "score": score,
        "max_score": 10,
        "passing_threshold": 8,
        "status": "pass" if score >= 8 else "revise",
        "criteria": criteria,
        "evidence": {
            "fresh_blender_probe": "probe.json",
            "fresh_probe_script": "probe_asset.py",
            "source_record": "../massing_campus_edge_343e3d8/source_record.json",
            "saved_builder_reopen_validation": "../massing_campus_edge_343e3d8/reopen_validation.json",
            "independently_reopened_asset": "../../modular/buildings/massing_campus_edge_343e3d8.blend",
            "inspected_model_preview": "../massing_campus_edge_343e3d8/campus_edge_preview.png",
            "inspected_footprint_preview": "../massing_campus_edge_343e3d8/campus_edge_footprint_preview.png",
            "inspected_orthophoto_overlay": "../massing_campus_edge_343e3d8/orthophoto_footprint_overlay.png",
            "inspected_official_exterior": "../massing_campus_edge_343e3d8/sources/official_gallery_07.jpg",
            "inspected_2023_orthophoto": "../massing_campus_edge_343e3d8/sources/indiana_2023_orthophoto_campus_edge.jpg",
            "height_analysis": "../massing_campus_edge_343e3d8/campus_edge_ndhm_analysis.json",
        },
        "findings": [
            {
                "severity": "blocking",
                "finding": "The footprint-derived prism fills major roof areas that are open/recessed in the 2023 orthophoto, and the model does not represent the distinct tower masses visible in the official gallery photo. This materially changes Campus Edge's roof plan and overall silhouette.",
                "recommended_action": "Revise the upper shell into photo/orthophoto-supported tower volumes and roof voids/terraces while retaining the source-backed structural podium footprint. Reopen and render fresh previews, then request a fresh independent grade.",
            },
            {
                "severity": "major",
                "finding": "The single uniform upper facade grid does not capture the visible tower-to-tower offsets and podium's projecting/recessed and open-column zones. The entrance and balcony positions are illustrative rather than source-located.",
                "recommended_action": "Use the official oblique image and orthophoto to split tower masses and model only visible offsets, courts, and podium transitions; keep uncertain dimensions labeled as estimates.",
            },
            {
                "severity": "limitation",
                "finding": "NDHM supports only an approximate roof-surface height distribution. It cannot verify exact eaves, floor count, per-tower height, or roof stepback elevations.",
                "recommended_action": "Retain this uncertainty unless building-specific plans or elevations become available; do not present the raster median as a surveyed roof/eave height.",
            },
        ],
    }
    return result


if __name__ == "__main__":
    result = evaluate()
    (GRADE / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    (GRADE / "evidence.json").write_text(json.dumps(result["evidence"], indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
