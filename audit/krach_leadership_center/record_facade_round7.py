import json
from pathlib import Path

evidence_path = Path(__file__).with_name("krach_evidence.json")
evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
evidence["facade_revision_round7"] = {
    "date": "2026-10-24",
    "review_context": {
        "previous_independent_score": "7.2/10",
        "findings": [
            "Sasaki's near/end elevation has three repeated upper window rows, which were absent.",
            "The tall bay belongs at the outside corner, not the mid-building GIS notch.",
            "The facade has three upper window levels above a continuous transparent public ground floor."
        ],
        "response": "Moved the full-height bay to the GIS southwest outer corner, placed the stair and floor openings behind it, cut three upper rows into the west end wall, removed ground-floor punched windows, and extended storefront glazing continuously along the south frontage."
    },
    "source_reference": {
        "provider": "Sasaki, project architect",
        "url": "https://www.sasaki.com/wp-content/uploads/2019/10/01-Krach_CornerView_2014_8789-1800x1200.jpg",
        "snapshot": "audit/krach_leadership_center/sasaki_krach_corner_view_reference.jpg",
        "supports": ["three upper window rows on near/end facade", "tall framed glazing at the near outside corner", "transparent ground-floor public frontage"],
        "measurement_limit": "Photo perspective is not calibrated; window spacing, width and floor elevations remain visual estimates."
    },
    "geometry": {
        "southwest_outer_corner_local_m": [-35.130669, -13.895864],
        "corner_bay_endpoint_local_m": [-26.462418, -13.970257],
        "corner_bay_width_m": 8.66857,
        "bay_yaw_degrees": -0.4917,
        "interior_stair_center_xy_m": [-30.796543, -9.3],
        "stair_floor_void_size_m": [8.8, 7.2],
        "end_facade_windows": {"upper_levels": 3, "bays_per_level": 4, "wall_apertures_cut": True},
        "long_facade_windows": {"upper_levels": 3, "bays": 8, "omitted_behind_corner_glazing": 2},
        "public_storefront": {"panes": 16, "extends_from_corner_bay_to_east_wing": True, "ground_floor_punched_windows_removed": True}
    },
    "verification": {
        "blender_version": "5.2.3 LTS",
        "saved_reopened_source": "modular/buildings/krach_leadership_center.blend",
        "sha256": "BDE08429342FD31EE3167D26F727E6BEDF6D94955031E0973DD2F8904BAA4316",
        "checks": [
            "Krach source reopened and rebuilt in Blender 5.2.3.",
            "GIS exterior shell bounds unchanged.",
            "Four window bays in each of three upper rows exist on the end elevation with matching mesh openings.",
            "Long elevations have three upper rows and omit two window bays hidden by the corner glass.",
            "Five floor opening ray tests pass at the shifted stair center; adjacent floor samples remain present.",
            "Eight stair flights, nine landings, and 32 guard/handrail splines retained.",
            "No missing external image dependencies.",
            "Exterior and lobby cutaway rerendered from reopened source."
        ],
        "preview": "audit/krach_leadership_center/source_preview.png",
        "cutaway_preview": "audit/krach_leadership_center/lobby_stair_preview.png",
        "same_angle_comparison": "audit/krach_leadership_center/sasaki_facade_comparison_round7.png",
        "validation_script": "audit/krach_leadership_center/validate_krach.py",
        "build_script": "audit/krach_leadership_center/facade_match_revision_round4.py",
        "stair_script": "audit/krach_leadership_center/align_lobby_to_outer_corner_round7.py"
    },
    "uncertainty": [
        "The official GIS footprint supports the southwest corner and wall outline; bay width, mullion rhythm, window dimensions, and entrance measurements remain photographic interpretations.",
        "Interior rooms, stair plan, exact story elevations, and penthouse footprint/height remain schematic or estimated."
    ],
    "status": "saved, reopened, validated, rerendered; awaiting fresh independent grade"
}
evidence_path.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
print(f"Updated {evidence_path}")
