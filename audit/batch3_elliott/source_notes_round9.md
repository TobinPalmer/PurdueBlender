# Elliott Hall of Music — round 9 sources and change notes

Work date: 2026-10-23. Scope: Elliott source asset plus evidence under `audit/batch3_elliott`. The campus master, manifest, building index, and Hovde asset were not edited.

## References

- [Purdue BuildingShapes FeatureServer, Feature 617](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/617?f=pjson), building abbreviation ELLT, identifies the footprint used for this check. Raw feature response: `building_shapes_fid_617_raw.json`. Layer metadata: `building_shapes_layer_metadata_raw.json`. Nearby feature query: `building_shapes_neighborhood_raw.json`. Retrieved 2026-10-23 10:31:04 UTC. Layer CRS is ArcGIS WKID 102100 / latest WKID 3857, WGS 84 Web Mercator Auxiliary Sphere (x=easting, y=northing).
- The source comparison applies a constant ground scale `cos(40.4274°)` to Web Mercator offsets from the project geographic origin (40.4274° N, 86.9137° W), then compares the ordered 188 unique source ring vertices directly with the local asset polygon translated by manifest origin `[-111.0000057, 49.8999977]` m. No rotation or best-fit transform was applied. This is a compact-area approximation, not survey control.
- Measured comparison: 0.1668 m RMS and 0.2594 m maximum vertex residual; area differs by -0.168%, perimeter by -0.076%. Full calculations, retrieval metadata, and limitations: `footprint_comparison_round9.json`; reproducible script: `footprint_compare_round9.py`.
- `footprint_neighborhood_overlay_round9.png` shows the north-up source neighborhood and the GIS/asset footprint outlines together, including the adjacent Hovde polygon. The source orientation/placement alignment is strong at the footprint level; it does not validate height, openings, or interior.
- [SAH Archipedia: Elliott Hall of Music](https://sah-archipedia.org/buildings/IN-01-157-0079) supports the red-brick/Indiana-limestone vocabulary, a curved canopy, and Hovde walkway feature types, but supplies no modeled dimensions or verified window schedule.
- [Purdue Elliott seating chart](https://convocations.purdue.edu/wp-content/uploads/2022/09/Elliott-Seat-Map.pdf) supports a main floor and two balconies with curved blocks, but is not dimensioned.
- [Purdue Convocations accessibility guidance](https://convocations.purdue.edu/accessibility/) and [Club Convos directions](https://convocations.purdue.edu/clubconvos/) describe access points and the Hovde approach; they do not verify this model's clearances, landing dimensions, or continuous route.

## Round 9 edits and evidence

- Removed the in-scene `LINK DEFERRED` text that overlapped the doorway. The deferred status remains in these notes and the result record.
- Added two simple estimated limestone corbels beneath the isolated Elliott-side interface landing to make its support legible. The landing, support geometry, and dimensions remain estimates. The open endpoint is intentionally not presented as a route to Hovde.
- Rendered a brighter, closer portal view and a readable audience-to-stage cutaway. The overhead interior view is now fully framed and oriented for inspection. These are presentation views; they do not convert schematic seating geometry into dimensioned architectural evidence.
- The exterior has no modeled window schedule because current reviewed references do not verify its count or spacing. No façade window pattern is claimed.

## Saved-file check and limits

Blender 5.2.3 LTS reopened `modular/buildings/elliott_hall_of_music.blend`. `Asset_elliott_hall_of_music` contains 135 mesh objects, including the two round 9 corbels. No temporary render objects or deferred text object remain. Reopen output: `reopen_check_round9.py`.

Still unverified: facade openings and exact ornament schedule; portal position and dimensions; canopy profile/support design; Elliott landing dimensions; the Hovde portal and any continuous connector/accessibility route; and interior dimensions, seat count, clearances, egress, and circulation.
