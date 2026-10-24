import json
from pathlib import Path

evidence_path = Path(__file__).with_name("krach_evidence.json")
evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
evidence["facade_revision_round8"] = {
    "date": "2026-10-24",
    "review_context": {
        "previous_independent_score": "7.8/10",
        "findings": [
            "Sasaki's long south elevation shows a more continuous window rhythm; the model had a large blank span.",
            "Corner glazing frame read heavy.",
            "Isolated lobby stair preview was flat gray and unreadable."
        ],
        "response": "Added four intermediate window bays to continue the three-level cadence across the blank span, positioned on the shallow GIS diagonal. Narrowed curtainwall frame members. Recentered the isolated preview camera on the moved corner stair, added key/fill lighting and a contrasting ground plane."
    },
    "geometry_and_material_changes": {
        "south_window_centers_local_x_m": [-23.1, -18.6, -14.1, -9.6, -5.1, -0.6, 4.0, 9.3, 14.6, 19.9, 25.2, 30.0],
        "south_upper_window_count": 36,
        "west_end_upper_window_count": 12,
        "levels": [4.88, 8.78, 12.68],
        "corner_frame_change": "Internal vertical frame bars reduced from 0.24 m to 0.14 m; horizontal transoms from 0.22 m to 0.14 m; outer uprights from 0.40 m to 0.24 m. Three glazing modules retained.",
        "storefront_panes": 16,
        "uncertainty": "Window centers on the shallow connector and all opening/frame dimensions remain photo interpretations; the connector facade plane is estimated from GIS endpoints."
    },
    "stair_preview": {
        "file": "audit/krach_leadership_center/lobby_stair_preview.png",
        "camera_target_local_m": [-30.7965, -9.3, 7.3],
        "changes": "Camera moved from obsolete pre-relocation stair coordinates, widened to a 22 mm lens to fit the full stair height, added warm/cool area lights and a dark ground plane. Preview omits guard polygons only; saved asset retains glass guards and handrails."
    },
    "verification": {
        "blender_version": "5.2.3 LTS",
        "saved_reopened_source": "modular/buildings/krach_leadership_center.blend",
        "sha256": "F6D4BE3728688A27968B4E833F283CC3F652433109EAB01CD69C9A266E90D8DB",
        "checks": [
            "Saved source reopened successfully.",
            "GIS shell bounds unchanged.",
            "48 facade window ray checks pass through the south and west-end wall openings.",
            "Five floor void checks pass with adjacent floor samples retained.",
            "36 long-facade upper panes, 12 west-end upper panes and 16 continuous storefront panes present.",
            "Eight stair flights, nine landings and 32 saved handrail/guard splines retained.",
            "No missing external image dependencies.",
            "Exterior, isolated stair and Sasaki comparison renders refreshed from reopened source."
        ],
        "exterior_preview": "audit/krach_leadership_center/source_preview.png",
        "cutaway_preview": "audit/krach_leadership_center/lobby_stair_preview.png",
        "same_angle_comparison": "audit/krach_leadership_center/sasaki_facade_comparison_round8.png",
        "validation_script": "audit/krach_leadership_center/validate_krach.py",
        "build_script": "audit/krach_leadership_center/facade_match_revision_round4.py",
        "render_script": "audit/krach_leadership_center/reopen_render_v2.py"
    },
    "uncertainty": [
        "Facade window cadence follows the Sasaki image but is not a measured elevation schedule.",
        "Story heights, penthouse location/shape, interior room plan, circulation dimensions and exact stair dimensions remain schematic or estimated."
    ],
    "status": "saved, reopened, validated, rerendered; ready for independent round 8 grade"
}
evidence_path.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
print(f"Updated {evidence_path}")
