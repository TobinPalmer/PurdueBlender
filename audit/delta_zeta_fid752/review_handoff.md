# Delta Zeta FID 752 independent review handoff

Please review the exact current candidate SHA-256 in `evidence.json` and `fresh_open_validation.json`. The individual library fresh-opens in Blender 5.2.3 LTS with its stable one-object scene and collection. Review is requested as read-only.

## Packet

- Asset: `modular/buildings/massing_house_301841601_7ae6159.blend`
- Source record and limitations: `source_record.json`
- Evidence summary: `evidence.json`
- Raw Purdue GIS FID 752 and layer metadata: `sources/`
- GIS/model and OSM comparison: `final_geometry.json`, `footprint_comparison.json`, `final_footprint_comparison.png`
- Exterior: `exterior_three_quarter.png`
- Front-entry detail: `entry_front_detail.png`
- Interior cutaway and room layout: `schematic_interior_cutaway.png`, `room_layout.json`
- Fresh-open: `fresh_open_validation.json`

## Main review limits

- The modeled wall base follows the official 11-vertex FID 752 ring after inverse Web Mercator and the repository's local approximation. That transform is not survey control. An unnamed OSM polygon provides a secondary cross-check (IoU 0.893; Hausdorff 3.50 m; centroid offset 1.16 m).
- Purdue GIS says one level, while the façade photo and public-area summary suggest a taller structure without proving a floor count. Two modeled levels, a 7.2 m eave, and a 9.0 m roof peak are estimates. GIS `Extrution=36` has undocumented units and is not treated as measured height.
- Official Purdue imagery qualitatively supports brick, entry stairs, wood double doors, an arched upper window, globe lamps, and a chapter sign. Facade dimensions, exact window rhythm, the entry's surveyed edge position, trim and roof remain interpretive.
- The 2023 national chapter article names foyer, living room, dining room and kitchen, but supplies no measured floor plan. The cutaway's room locations and furniture are diagrammatic and not current as-built evidence.
- The README crosswalk row also lists Crosswalk Commons. Its own OSM identity/address is 925 Hilltop Drive; that separate asset was not edited or merged.

Please score source/identity, GIS geometry, facade evidence, materials, presentation/technical quality, and interior evidence separately, give the weighted total on a 10-point scale, and list revisions needed to reach 8/10. Do not edit the asset during review.
