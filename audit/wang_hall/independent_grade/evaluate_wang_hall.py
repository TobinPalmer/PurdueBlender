"""Independent rubric evaluator for the Wang Hall modular asset.

This evaluator checks saved-asset metadata/hash and source-derived structural bounds,
then records visual source comparison notes. It does not modify the building asset.
"""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "audit" / "wang_hall"
ASSET = ROOT / "modular" / "buildings" / "massing_wang_hall_wang_0dac5ab.blend"
MANIFEST = ROOT / "modular" / "manifest.json"
VALIDATION = AUDIT / "fresh_open_validation.json"
RESULT = Path(__file__).resolve().parent / "result.json"


def evaluate():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    entries = manifest.get("buildings", manifest.get("assets", []))
    # Project manifest schema stores buildings inside a top-level list; allow nested key variants.
    if not entries:
        for value in manifest.values():
            if isinstance(value, list) and any(isinstance(x, dict) and x.get("id") == "massing_wang_hall_wang_0dac5ab" for x in value):
                entries = value
                break
    entry = next(x for x in entries if x.get("id") == "massing_wang_hall_wang_0dac5ab")
    validation = json.loads(VALIDATION.read_text(encoding="utf-8"))
    asset_hash = hashlib.sha256(ASSET.read_bytes()).hexdigest()
    source_bounds = validation["structural_footprint_source_bounds_local_m"]
    shell_bounds = validation["structural_shell_evaluated_bounds_local_m"]
    local_bbox_delta = max(abs(shell_bounds[a][i] - source_bounds[a][i]) for a in "xy" for i in range(2))
    manifest_bounds = entry.get("bounds_world_m")
    asset_is_centered = max(abs(sum(validation["evaluated_bounds_local_m"][a]) / 2) for a in "xy") < 0.5
    manifest_world_center = [sum(manifest_bounds[i]) / 2 for i in (0, 1)] if manifest_bounds else None
    planned_anchor = [98.2954902278031, 339.9100960000692]
    manifest_center_matches_anchor = bool(manifest_bounds) and max(abs(manifest_world_center[i] - planned_anchor[i]) for i in (0, 1)) < 0.001

    criteria = [
        {
            "name": "Identity and source-backed footprint",
            "score": 1.9,
            "max_score": 2,
            "evidence": [
                "OSM way 301932787 is named Wang Hall (WANG); Purdue GIS feature FID 895 independently identifies Wang Hall.",
                "The saved outline is derived from the 17-vertex OSM ring. Structural shell XY bbox agrees with the projected source bbox within %.6f m." % local_bbox_delta,
                "Aerial overlay shows OSM follows the visible roof edge more closely than the Purdue GIS ring, although the sources differ by several metres (reported IoU ~0.812)."
            ],
            "deduction": "Small deduction because OSM is a community-mapped roof outline, not surveyed wall geometry, and the GIS/aerial boundary remains conflicting."
        },
        {
            "name": "Position, orientation, scale and dimensions",
            "score": 1.6,
            "max_score": 2,
            "evidence": [
                "Structural footprint dimensions and outline match the projected OSM ring; the evaluated shell bbox differs by only %.6f m." % local_bbox_delta,
                "Asset geometry is centered at local XY origin. The manifest source bounds center is %s, matching the planned Placement marker anchor %s." % (manifest_world_center, planned_anchor),
                "Master marker integration was not available in this building-only review; planned integration still needs coordinator verification."
            ],
            "deduction": "Campus placement is supported by the exact planned bbox center, but the final master Placement marker and rotation still need integration review."
        },
        {
            "name": "Evidence-backed height, floors and roof form",
            "score": 1.5,
            "max_score": 2,
            "evidence": [
                "Four floors are independently supported by Purdue/CSO descriptions and OSM building:levels=4.",
                "OSM tags height=14.8 m; the manifest massing bounds also top at 14.8 m. The new shell-body Z span is 13.88 m before roof/parapet and is an estimate, not a survey.",
                "Preview roof plan includes a long central skylight and rooftop equipment, consistent with aerial and architect imagery at a schematic level."
            ],
            "deduction": "Exact floor heights and roof elevations are not supported by dimensioned drawings; total evaluated model reaches 15.9 m because of rooftop components, 1.1 m above the OSM tagged height. Roof features remain simplified."
        },
        {
            "name": "Facade, entrances and distinctive architecture",
            "score": 1.0,
            "max_score": 2,
            "evidence": [
                "The model has a red brick texture, pale horizontal bands, repeated divided windows, a central glass panel, entrance canopy and sign, consistent in broad material vocabulary with architect photos.",
                "The central atrium tower in the reference is a distinctive projecting brick pavilion with tall glass, a raised curved/capped top and a recessed entry; the model shows a flush rectangular glazed panel, no raised tower/cap and a broad low canopy. The generated preview visibly shows brick texture behind the central glass, so the atrium opening is not convincingly legible.",
                "Facade reference also has taller, fewer window bays than the many small, squarish repeated units in the model."
            ],
            "deduction": "The recognizable central tower, its projection and cap, window proportions, and atrium transparency are not reproduced closely enough."
        },
        {
            "name": "Modular export, portability and evidence",
            "score": 1.8,
            "max_score": 2,
            "evidence": [
                "Fresh Blender 5.2.3 open reports expected scene Building_massing_wang_hall_wang_0dac5ab and collection Asset_massing_wang_hall_wang_0dac5ab with 9 objects and evaluated mesh geometry.",
                "No linked external libraries were found; materials are procedural and the preview rig is separate from the asset collection.",
                "The audit contains raw OSM/GIS/official/architect/aerial source snapshots, an overlay, two renders, structured evidence and fresh-open validation. Asset SHA-256 checked independently as %s." % asset_hash
            ],
            "deduction": "Portability and evidence are strong; coordinator still needs to change the manifest integration class and verify the final placement marker."
        }
    ]
    result = {
        "building": "Wang Hall (WANG)",
        "asset": str(ASSET.relative_to(ROOT)),
        "asset_sha256": asset_hash,
        "score": round(sum(c["score"] for c in criteria), 1),
        "max_score": 10,
        "criteria": criteria,
        "evidence": {
            "independently_read": [
                "Saved .blend via Blender fresh-open validation",
                "Purdue manifest row and modular/AGENTS coordinate-frame rule",
                "OSM way 301932787 raw JSON",
                "Purdue GIS FID 895 GeoJSON and aerial overlay",
                "Purdue official articles and CSO architect images",
                "Three-quarter and roof-plan model previews"
            ],
            "structural_bbox_delta_m": local_bbox_delta,
            "asset_centered_xy": asset_is_centered,
            "manifest_kind": entry.get("kind"),
            "manifest_world_center_m": manifest_world_center,
            "planned_anchor_xy_m": planned_anchor,
            "manifest_world_center_matches_planned_anchor": manifest_center_matches_anchor
        },
        "findings": [
            "Coordinator must implement the planned detailed-asset integration: change manifest kind to detailed and set Placement_massing_wang_hall_wang_0dac5ab to [98.2954902278031, 339.9100960000692], then verify placement/orientation in the master.",
            "Model the projecting brick atrium pavilion and raised curved/capped crown from the architect references, with recessed/tall central glazing and a readable entrance; the current flat rectangular screen lacks Wang Hall's signature feature.",
            "Correct the central pane/atrium so interior structure or open depth reads through it; the rendered panel currently looks like a dark brick-backed rectangle.",
            "Review overall roof top against the 14.8 m source height; the model currently reaches 15.9 m including rooftop component geometry."
        ]
    }
    RESULT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    print(json.dumps(evaluate(), indent=2))
