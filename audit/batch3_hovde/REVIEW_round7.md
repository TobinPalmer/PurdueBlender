# Hovde Hall — round 7 building-side pass

## Changes

- Fixed the east entrance doors after inspecting mesh axes. The three existing leaves, transoms, and handles were oriented edge-on to the east facade: their width ran across local X rather than along the facade opening. Rotated all three assemblies 90° so their broad faces now align with the east wall openings.
- Replaced each solid limestone door-frame cube with a hollow four-sided surround and transom rail. This was the main reason the cut openings still looked like blank masonry in earlier renders.
- Repositioned the six columns to centers `[-5.6, -4.1, -1.7, 1.2, 3.8, 5.6]` in local Y, leaving the three modeled door openings clear. The portico still covers parts of the central facade and remains an estimated interpretation rather than a measured elevation.
- Rendered the actual office and boardroom floors, furnishings, and three retained perimeter walls together in an oblique cutaway. The camera-side wall and ceiling are hidden only in the evidence render; no walls were removed from the saved asset. These room layouts are interpretive because no plans were found.
- No master, manifest, placement marker, shared script, or `HOVD_Root` transform edits. Root remains `[-62.85, 93, 0]`, Z rotation `0.689754 rad`, scale `[1,1,1]`.

## Reopen and evidence

Blender 5.2.3 reopened the saved canonical asset for all round 7 renders and the export check. `final_asset_check_round7.json` reports 727 exported objects, 715 meshes, no unmaterialed meshes, and the unchanged root transform.

- `audit/batch3_hovde/exterior_round7.png` — full building and visible entrance doors.
- `audit/batch3_hovde/portico_detail_round7.png` — low, nearly frontal approach view; the door leaves/transoms now read through the portico. Some facade remains obscured by the classical assembly.
- `audit/batch3_hovde/presidential_office_cutaway_round7.png` and `trustees_boardroom_cutaway_round7.png` — oblique, three-wall interior studies with furniture. Interpretive layouts, not verified plans.
- `audit/batch3_hovde/final_asset_check_round7.json` — reopen/export/material/root check.
- Reproducible edit scripts: `round7_edit.py`, `round7_door_alignment.py`; render setup: `render_round7.py`.

## References and limitations

Exterior features were compared with Julian Herzog's geotagged Hovde photo, taken 2016-09-18 at 40.428660, -86.913958 (EPSG:4326): https://commons.wikimedia.org/wiki/File:Frederick_L_Hovde_Hall_of_Administration_Purdue_University_2016_01.jpg; the West Lafayette visitor guide also shows the masonry wings, pedimented central entrance, and stairs: https://assets.simpleviewinc.com/simpleview/image/upload/v1/clients/westlafayettein/2022_Visitors_Guide_0481c246-c159-4d01-a3a6-e00c4eddae3e.pdf. Purdue Archives describes Hovde as a four-story, 70 × 230 ft office/administration building and mentions a board room, but the record found has no room plans or measured elevation: https://archives.lib.purdue.edu/agents/corporate_entities/573. The official building GIS snapshot is `audit/official_purdue_buildings_wgs84.json`, EPSG:4326, retrieved 2026-10-22; master/GIS overlay is still pending with the parent.

**Remaining uncertainty:** portico dimensions/support rhythm; roof profile and finish; exact window schedule; interior layout; and master/GIS placement. The doors now read, but the portico still hides sections of the facade. Do not claim a 9/10 score until independent review.
