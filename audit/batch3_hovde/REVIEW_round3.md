# Hovde Hall — round 3 building-side update

**Self-review: 6.8/10; independent review requested.** The new neutral render is readable and the brick appears dark red-brown. It is a presentation and material pass plus selected geometry changes; the roof form and interior remain interpretive and source-limited. Round 2 independent score was 6.4/10; this round should not be treated as 9/10 or complete.

## Round 3 edits

- Reduced `HOVD_Penthouse` to approximately 5.0 × 8.4 × 1.2 m, relocated it on the roof, and recolored it to blend with the brick. Updated `HOVD_Penthouse_Louvers`. This removes the previously dominant 12 × 24 × 2.5 m block; the remaining small access feature is inferred, not verified by a Hovde roof plan.
- Added `HOVD_Inferred_Hipped_Roof`, a low-pitch hipped overlay over the existing roof slab. The specific roof geometry is still unverified; campus material context supports red clay tile generally, not a Hovde-specific roof survey.
- Darkened `Purdue_Red_Brick`, `Bedford_Indiana_Limestone`, and `Hovde_Roof_Membrane` procedural values. Added joined `HOVD_Window_Sash_Detail` geometry and adjusted glazing to read more clearly at facade scale.
- Reduced the office and boardroom plans again, then restored wall/story heights. Current floor objects measure approximately 9.58 × 9.07 m. Interior layouts and their dimensions remain illustrative; render cutaways hide selected walls and ceilings. They still need a better source plan and more convincing room enclosure/detail.
- No master file, manifest, placement marker, or shared status file was edited. `HOVD_Root` internal location/rotation/scale remains `[-62.85,93,0]`, `0.689754 rad` about Z, and `[1,1,1]`; master marker remains outside this building-side edit.

## Reopen and evidence

Opened the canonical `.blend` from disk for each new render and for the final asset check in Blender 5.2.3. The final check confirms scene `Building_hovde_hall`, export collection `Asset_hovde_hall`, 672 exported objects / 660 meshes, assigned material slots on every mesh, and unchanged root transform. The decrease in count from round 2 is consistent with deleting the 32 roof tile-hint cubes and replacing them with joined roof/window detail geometry; the scene reopened successfully.

- `audit/batch3_hovde/exterior_round3.png` — refreshed readable neutral three-quarter exterior. Brick now reads deep red-brown. Roof and stone stay dark/flat in this lighting, and portico still needs improved dimensional integration.
- `audit/batch3_hovde/presidential_office_round3.png` and `audit/batch3_hovde/trustees_boardroom_round3.png` — fresh room-only section renders from the reopened file. These show the furniture layouts, but also confirm the interiors remain simple/illustrative and not finished to a 9/10 standard.
- `audit/batch3_hovde/final_asset_check.json` and `audit/batch3_hovde/final_check_round3.log` — reopen/collection/material/root-transform check.
- `audit/batch3_hovde/render_exterior_round3.py`, `audit/batch3_hovde/render_interior_final.py` — render scripts for reproducibility.

## Sources and uncertainty

- [Wikimedia Commons, Hovde Hall exterior 01](https://commons.wikimedia.org/wiki/File:Frederick_L_Hovde_Hall_of_Administration_Purdue_University_2016_01.jpg), photo dated 2016-09-18, geotag 40.428660, -86.913958; perspective facade evidence, not measured elevation.
- [Wikimedia Commons, Hovde Hall exterior 02](https://commons.wikimedia.org/wiki/File:Frederick_L_Hovde_Hall_of_Administration_Purdue_University_2016_02.jpg), winter exterior image; corroborates front portico, no measured dimensions.
- [Purdue Archives Hovde Hall record](https://archives.lib.purdue.edu/agents/corporate_entities/573), checked 2026-10-23; historic administration function and room context, not an interior plan.
- [SAH Archipedia](https://sah-archipedia.org/buildings/IN-01-157-0079), checked 2026-10-23; supports campus palette context of red brick, Indiana limestone, and red clay tile, not the exact Hovde roof assembly.
- Official Purdue GIS feature FID 618 from `audit/official_purdue_buildings_wgs84.json`, WGS84/EPSG:4326 snapshot retrieved 2026-10-22. Existing placement marker is preserved. This pass did not reopen the master for an overlay, so the master agent must certify contextual placement.

**Remaining uncertainty:** roof profile and access structure; room footprint/layout and circulation; measured facade proportions and exact materials; precise GIS-to-wall registration and campus placement review. Request independent round 3 review of the reopened file and refreshed evidence.
