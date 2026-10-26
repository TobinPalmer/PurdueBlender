"""Second independent review of the saved Wang Hall asset after requested revisions."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "audit" / "wang_hall"
ASSET = ROOT / "modular" / "buildings" / "massing_wang_hall_wang_0dac5ab.blend"
VALIDATION = AUDIT / "fresh_open_validation.json"
EVIDENCE = AUDIT / "evidence.json"
RESULT = Path(__file__).resolve().parent / "result.json"


def evaluate():
    digest = hashlib.sha256(ASSET.read_bytes()).hexdigest()
    validation = json.loads(VALIDATION.read_text(encoding="utf-8"))
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    source_bounds = validation["structural_footprint_source_bounds_local_m"]
    shell_bounds = validation["structural_shell_evaluated_bounds_local_m"]
    max_delta = max(abs(shell_bounds[a][i] - source_bounds[a][i]) for a in "xy" for i in range(2))
    center = evidence["placement_anchor_campus_xy_m"]
    asset_bounds = validation["evaluated_bounds_local_m"]
    is_local = max(abs(sum(asset_bounds[a]) / 2) for a in "xy") < 0.5
    checks = validation["checks"]
    external = validation["external_libraries"]
    max_height = validation["height_m"]
    ray = validation["atrium_front_raycast"]
    criteria = [
        {
            "name": "Correct identity and source-backed footprint",
            "score": 1.9,
            "max_score": 2,
            "evidence": [
                "OSM way 301932787 is named Wang Hall (WANG), has 17 unique outline vertices, four levels and a 14.8 m height tag; Purdue GIS FID 895 independently identifies Wang Hall.",
                f"The fresh-open structural shell bbox matches the projected OSM footprint bbox within {max_delta:.6f} m.",
                "The aerial overlay supports the selected OSM rooftop outline visually; Purdue GIS remains shifted/jittered with approximately 0.812 OSM/GIS IoU."
            ],
            "deduction": "OSM is community-mapped and GIS/roof outlines disagree by several metres, so the wall line is not survey-verified."
        },
        {
            "name": "Position, orientation and scale/dimensions",
            "score": 1.7,
            "max_score": 2,
            "evidence": [
                f"Asset is centered in local geometry coordinates: {is_local}.",
                f"The planned campus anchor {center} is the center of the source bounds and matches the current manifest bbox center to less than 0.001 m.",
                "The primary outline and orientation are built directly from the projected source ring; the coordinator will apply this anchor using a detailed placement marker."
            ],
            "deduction": "The new master Placement marker and final in-master instance/orientation have not yet been inspected; campus placement remains an explicit integration step."
        },
        {
            "name": "Evidence-backed height, floors and roof form",
            "score": 1.7,
            "max_score": 2,
            "evidence": [
                "Four stories are supported by OSM and official Purdue/architect descriptions.",
                f"Fresh-open evaluated asset top is {max_height:.2f} m; this is within 0.01 m of OSM's 14.8 m tag. The main roof/parapet is approximately 14.8 m and HVAC blocks have been lowered.",
                "Top-down preview shows a central skylight strip, perimeter parapet and low rooftop equipment consistent with available aerial/project imagery at a schematic level."
            ],
            "deduction": "The exact story elevations and equipment dimensions remain estimates; no dimensioned roof/elevation survey was available."
        },
        {
            "name": "Facade, entrances and distinctive architecture",
            "score": 1.3,
            "max_score": 2,
            "evidence": [
                "The updated detail preview shows a projecting brick pavilion with a raised pale elliptical crown, a tall divided curtain wall, ground-floor entrance, canopy and signage, addressing the largest distinctive-feature gap from round one.",
                "The glass screen now reads translucent with atrium floor bands and internal structure behind it; a fresh-open ray sample records a first hit 6.06 m inward rather than on the outer structural wall.",
                "Window pitch is wider and units are taller than round one, closer to the architect photographs; masonry, glazing, trim and roof materials are assigned."
            ],
            "deduction": "At full-building scale the pavilion/crown still reads somewhat shallow and the facade rhythm remains more uniform and denser than the photos. Interior finishes, entrance recess and detailed atrium layout are schematic."
        },
        {
            "name": "Modular export, portability and complete evidence",
            "score": 1.7,
            "max_score": 2,
            "evidence": [
                f"Fresh-open SHA-256 agrees with the current asset ({digest == validation['asset_sha256'] == evidence['model']['asset_sha256']}).",
                f"Expected scene and collection reopen with {validation['asset_object_count']} exported objects and {validation['evaluated_mesh_vertex_count']} evaluated mesh vertices; no linked libraries are present.",
                "Procedural materials are self-contained; separate source snapshots, GIS/aerial overlay, three previews, structured evidence and fresh-open validation are saved."
            ],
            "deduction": "The coordinator still needs to change the manifest class to detailed and verify the marker/instance in the master file."
        }
    ]
    score = round(sum(c["score"] for c in criteria), 1)
    result = {
        "building": "Wang Hall (WANG)",
        "asset": str(ASSET.relative_to(ROOT)),
        "asset_sha256": digest,
        "score": score,
        "max_score": 10,
        "passing_threshold": 8,
        "passes": score >= 8,
        "criteria": criteria,
        "evidence": {
            "fresh_open_validation": str(VALIDATION.relative_to(ROOT)),
            "structured_evidence": str(EVIDENCE.relative_to(ROOT)),
            "footprint_bbox_delta_max_m": max_delta,
            "local_xy_centered": is_local,
            "planned_campus_anchor_xy_m": center,
            "fresh_open_max_z_m": max_height,
            "external_libraries": external,
            "atrium_opening_ray_probe": ray,
            "round_one_score": 7.8,
            "revision_effects": [
                "Added projecting brick atrium side piers and raised curved pale crown.",
                "Expanded the atrium cavity and made its central glass screen visibly translucent with internal floor/stair structure behind it.",
                "Reduced facade window-bay count, enlarged window widths/heights, and lowered rooftop mechanical geometry to the source height envelope."
            ]
        },
        "findings": [
            "The signature central atrium/pavilion is now present and recognizable in the close view, though still simplified relative to the architect's photos.",
            "Rooftop envelope now matches the OSM 14.8 m height tag to rounding (14.81 m evaluated extent).",
            "Keep master integration pending until the coordinator changes the manifest entry to detailed, applies anchor [98.2954902278031,339.9100960000692], and verifies its campus placement in the master."
        ]
    }
    RESULT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    print(json.dumps(evaluate(), indent=2))
