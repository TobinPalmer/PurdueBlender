import json
from pathlib import Path

root = Path(__file__).resolve().parents[2]
evidence_path = Path(__file__).with_name("krach_evidence.json")
evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
evidence["facade_revision_round6"] = {
    "date": "2026-10-24",
    "review_context": {
        "previous_independent_score": "7.6/10",
        "finding": "box_mesh adds its origin after rotating local vertices; glazing pane centers already included an origin-relative offset, shifting the bay and connector east by approximately 4.33 m. The stair near x=-11.99 m was consequently off-center from the glazing.",
        "response": "Recentred every bay and connector pane/frame center around its supplied local origin before applying origin translation. Added build-time coordinate assertions to prevent another double-origin displacement."
    },
    "geometry_verification": {
        "gis_diagonal_endpoints_local_m": [[-16.3207893, -14.0572958], [0.9931201, -13.1601419]],
        "narrow_glass_bay_endpoints_local_m": [[-16.3207893, -14.0572958], [-7.6638346, -13.6087189]],
        "bay_span_m": 8.6685688,
        "bay_frame_mesh_bounds_local_m": [[-16.518, -7.449], [-14.357, -13.648], [-0.175, 15.375]],
        "bay_pane_mesh_bounds_local_m": [[-16.209, -7.768], [-14.154, -13.652], [0.075, 15.125]],
        "storefront_connector_mesh_bounds_local_m": [[-7.612, 0.948], [-13.708, -13.2], [0.04, 2.92]],
        "stair_clear_bounds_local_m": [[-16.091, -7.894], [-11.775, -6.825], [-0.970, 15.660]],
        "interpretation": "Frame overhang is approximately 0.20 m around the GIS-defined half-edge bay. The glass pane and stair ranges now overlap around the same bay midpoint x=-11.992 m. Connector spans the remaining diagonal to the Main Street wing."
    },
    "view_comparison": {
        "reference": "Sasaki project architect corner photograph, audit/krach_leadership_center/sasaki_krach_corner_view_reference.jpg",
        "render": "audit/krach_leadership_center/source_preview.png",
        "side_by_side": "audit/krach_leadership_center/sasaki_facade_comparison_round6.png",
        "camera_eye_local_m": [-85, -50, 11],
        "camera_target_local_m": [-4, -3, 7.4],
        "lens_mm": 58,
        "limitation": "Camera reproduces the southwest oblique corner/wing order, not calibrated perspective or exact photographic camera intrinsics."
    },
    "verification": {
        "blender_version": "5.2.3 LTS",
        "saved_reopened_asset": "modular/buildings/krach_leadership_center.blend",
        "sha256": "106F8DAACC121AD5C8B274C7F05B85CF234DC6940C77CA066FB14BBFDF06D019",
        "checks": [
            "Krach source asset reopened successfully in Blender 5.2.3.",
            "Build-time assertions confirm glazing bounds remain centered at GIS corner bay and connector bounds centered at connector midpoint.",
            "GIS shell extents unchanged.",
            "All five floor void ray checks pass; adjacent floor samples remain present.",
            "Eight stair flights, nine landings, and 32 handrail splines retained in saved source.",
            "No missing external image dependencies.",
            "Exterior and stair cutaway renders refreshed from reopened source."
        ],
        "validation_script": "audit/krach_leadership_center/validate_krach.py",
        "build_script": "audit/krach_leadership_center/facade_match_revision_round4.py",
        "render_script": "audit/krach_leadership_center/reopen_render_v2.py",
        "comparison_composer": "audit/krach_leadership_center/compose_sasaki_comparison_round6.ps1"
    },
    "uncertainty": [
        "GIS gives the simplified connector geometry; the exact glazing subdivision and facade projection remain visual interpretations.",
        "Story heights, penthouse dimensions/location, interior stair layout and entrance extents remain schematic or photo-estimated."
    ],
    "status": "saved, reopened, validated, rerendered, comparison refreshed; ready for fresh independent grade"
}
evidence_path.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
print(f"Updated {evidence_path}")
