# Hovde Hall — round 6 building-side pass

## Changes made

- Replaced the east and west continuous facade cubes with brick mesh geometry leaving openings aligned with the existing 52 ribbon-glazing bays (13 locations × 4 modeled levels on each elevation). Glazing objects and their joined bronze sash detail are recessed 0.25 m into the wall thickness. These openings follow the existing model cadence; they are not claimed to be a verified historic window schedule.
- Added three wall openings on the east entrance elevation sized around the existing door/transom units. They are real voids in the masonry shell, although the current close render still does not make the entrance doors fully legible through the portico geometry.
- Re-spaced the six portico supports from an almost-touching 0.835 m center pitch to a deliberately wider sequence around the three modeled entry doors. The six-column rhythm reads better, but the portico/pediment still masks some entrance and facade detail in the close view and needs another review.
- Broadened the entablature/cornice and pediment to correspond with the spread supports. This is a visual modeling judgment rather than a dimension measured from an elevation.
- No edits to the master file, manifest, FID marker, or shared scripts. HOVD_Root remains location [-62.85,93,0], Z rotation 0.689754 rad, scale [1,1,1].

## Reopen and evidence

Blender 5.2.3 reopened the saved `modular/buildings/hovde_hall.blend` for the round 6 render set and final asset check. `final_asset_check.json` reports 727 export-collection objects, 715 meshes, no unmaterialed meshes, and the unchanged root transform.

- `audit/batch3_hovde/exterior_round6.png` — full exterior after reopening.
- `audit/batch3_hovde/portico_detail_round6.png` — entrance close-up; six supports are separated, but portions of the entrance and adjacent facade remain obscured.
- `audit/batch3_hovde/presidential_office_round6.png` and `trustees_boardroom_round6.png` — interpretive furnishing cutaways, not source-verified floor plans.
- `audit/batch3_hovde/final_asset_check.json` — reopened asset/export/material/root checks.
- Reproducible edits: `round6_edit.py`, `round6b_portico.py`, `round6c_door_openings.py`; renders: `render_round6.py`.

## References and limitations

The facade and portico were compared with Julian Herzog's geotagged Hovde exterior photo (photo date 2016-09-18; camera coordinates 40.428660, -86.913958; EPSG:4326): https://commons.wikimedia.org/wiki/File:Frederick_L_Hovde_Hall_of_Administration_Purdue_University_2016_01.jpg. The visitor-guide image also supports the brick wings, classical entrance, triangular pediment, and stairs: https://assets.simpleviewinc.com/simpleview/image/upload/v1/clients/westlafayettein/2022_Visitors_Guide_0481c246-c159-4d01-a3a6-e00c4eddae3e.pdf. Purdue Archives describes the building as a four-story, 70 × 230 ft office/administration building and identifies a board room, but the source located does not provide measured elevations or room plans: https://archives.lib.purdue.edu/agents/corporate_entities/573. The official GIS snapshot `audit/official_purdue_buildings_wgs84.json` is EPSG:4326, retrieved 2026-10-22; this pass did not overlay the Hovde mesh against the master/GIS footprint.

**Remaining uncertainty:** roof profile/material, exact portico dimensions and column rhythm, exact facade/window dimensions, interior layouts, and master/GIS placement remain unverified. The interior scenes remain interpretive because source floor plans were not found. Request independent round 6 review; do not describe this pass as 9/10 complete.
