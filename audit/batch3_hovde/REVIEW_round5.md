# Hovde Hall — round 5 building-side update

**Round 4 independent score: 7.0/10. Round 5 self-review: 7.2/10; not a 9/10 completion claim.** The latest pass reduces the central stone footprint and separates the triangular pediment from the cornice. The exterior remains partly obstructed at the entrance, the name inscription is still not clearly readable, and interior/roof/placement claims remain limited by sources.

## Changes in round 5

- Rebuilt the visual hierarchy of the central entrance by reducing the entablature to about 5.32 m wide × 0.35 m high and 1.10 m deep, the cornice to about 5.31 m wide × 0.14 m high, and the triangular pediment to about 4.80 m wide × 1.40 m high. Reduced the crown and projection to keep the triangle legible. Dimensions are asset measurements, not source-survey measurements.
- Kept all six shafts and compressed their spacing symmetrically under the smaller pediment. Their rendered shafts remain slender; the close view shows the pediment and six supports with adjacent brick/window bays visible.
- Reduced and centered the plaque, then moved it to the front of the fascia. The latest image no longer shows the previous wide text collision, but the title is not yet plainly legible; signage placement and wording are not verified against an archival elevation.
- Moved the interpretive office sofa within the modeled room footprint and reduced the oversized rug. The office and boardroom plans remain illustrative because no floor plans were located.
- No master, manifest, marker, or shared scripts were edited. `HOVD_Root` remains at `[-62.85, 93, 0]`, Z rotation `0.689754 rad`, scale `[1,1,1]`.

## Reopen and evidence

Blender 5.2.3 reopened the saved canonical asset for the round 5 exterior/interior render set and final asset check. Check output confirms `Asset_hovde_hall`: 727 objects, 715 mesh objects, zero unmaterialed meshes, and unchanged root transform.

- `audit/batch3_hovde/exterior_round5c.png` — full exterior after the reduced portico pass.
- `audit/batch3_hovde/portico_detail_round5c.png` — lower-angle close view showing the narrowed cornice, triangular tympanum, six shafts, and stairs. Some of the central entry/facade is still hidden by the portico assembly.
- `audit/batch3_hovde/presidential_office_round5c.png` and `trustees_boardroom_round5c.png` — interpretive top-down furnishing evidence. These use temporary neutral floors for presentation; those floor changes are not saved into the asset. The office layout is still schematic.
- `audit/batch3_hovde/final_check_round5.log` and `final_asset_check.json` — reopen/export/material/root check.
- `audit/batch3_hovde/round5_edit.py`, `round5_portico_revision.py`, `round5_fit_refine.py`, and `render_round5c.py` — reproducible editing/render steps.

## References and remaining uncertainty

Exterior form was checked against [Wikimedia Commons Hovde Hall exterior 01](https://commons.wikimedia.org/wiki/File:Frederick_L_Hovde_Hall_of_Administration_Purdue_University_2016_01.jpg) (photo dated 2016-09-18; geotag 40.428660, -86.913958), [exterior 02](https://commons.wikimedia.org/wiki/File:Frederick_L_Hovde_Hall_of_Administration_Purdue_University_2016_02.jpg), and the [West Lafayette visitor guide](https://assets.simpleviewinc.com/simpleview/image/upload/v1/clients/westlafayettein/2022_Visitors_Guide_0481c246-c159-4d01-a3a6-e00c4eddae3e.pdf). These establish the brick wings, central classical portico, triangular pediment, and broad stairs, but are perspective images rather than measured elevations. [Purdue Archives’ Hovde Hall record](https://archives.lib.purdue.edu/agents/corporate_entities/573) supports administration-building identity/context, not interior layout. Official GIS FID 618 source snapshot remains `audit/official_purdue_buildings_wgs84.json` (EPSG:4326, retrieved 2026-10-22); this pass did not compare the current master marker to GIS.

**Open items:** verify sign location/wording; check if central facade/window rhythm is still over-obscured; find a measured elevation or current reference view for portico proportions; obtain roof plan/overhead imagery before claiming its profile or finish; obtain interior plans or continue labeling the rooms schematic; master agent must check the linked placement against GIS and neighboring buildings. Request independent review of round 5 if another reviewer slot is available.
