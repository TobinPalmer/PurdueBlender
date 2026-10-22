# WALC east neighbor review — 2026-10-22

Reviewed WALC, Potter, Mechanical Engineering (ME), Brown Electrical Engineering (BHEE), and Knoy. Changed four libraries; Knoy is preserved. No master, placement, manifest, or shared report edits were made.

## Evidence

Provider: Purdue official campus map, BuildingShapesZip4 layer. URL: https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0 . Raw source snapshot and feature provenance are retained in ../official_building_references.json (snapshot date 2026-10-22) and adjacent official layer metadata. Source publication date and surveyed accuracy are unavailable. Reference coordinates are the project's local conversion of geographic longitude/latitude: X=(lon+86.9137)*84810.60416539927, Y=(lat-40.4274)*111040, meters. This is an approximate campus coordinate convention, not a certified survey. Use original source metadata for the service CRS; normalized reference is local meters.

Building identity is established by official building codes, not nearest centroid: POTR FID864; ME FIDs857 and108; BHEE FIDs292 and109; KNOY FID243; WALC FID906. Small ME and BHEE polygons are retained as separate official features in their corresponding asset, without substituting one part for the whole building. Internal heights of those parts remain uncertain.

## Corrections

Potter previously had an invented 46m by68m rectangular core at campus X59–105,Y−44–24. Official irregular footprint bounds are X77.820–136.272,Y−18.037–49.395. Its coarse core, bands, displaced ribbon glass, and unsupported terrace were replaced by the actual irregular official outline extrusion and footprint-following roof/bands. The inherited 15.5m wall-height estimate remains unverified.

ME had a rectangular historic core and a crude detached Gatewood block: neither followed the complex official outline. Rebuilt both official feature outlines with footprint-following roofs/bands; removed incompatible placeholder portico, belts, and displaced glass. Main height18.5m is the prior historic-core estimate; the smaller feature also uses this estimate. The previous Gatewood21m block height is not promoted to a measured height. Exact wing heights, roof details, and facade reconstruction remain unverified.

BHEE had an invented 88m by95m rectangle and generic cap/portal. Rebuilt the irregular official feature292 and feature109 outlines, each with roof and horizontal bands. Retained18m as an unverified prior wall-height estimate. Curved/stepped footprint edges are retained at source precision.

WALC exported four large Campus terrain meshes extending roughly220 by276m around the building. These unrelated ground plates overlapped neighboring assets; removed those four objects. All249 other collection objects remain, including the detailed interior and plaza. Its structural facade bounds approximately X15.83–63.53,Y−40.47–38.03 differ from official footprint X12.07–70.99,Y−45.49–45.04. This is an unresolved shape discrepancy. Uniformly scaling the model would distort the interior, so no unsupported shape correction was applied.

Knoy wall bounds match the official irregular footprint envelope: campus X195.927–240.852,Y−2.461–90.701, within rounding. Preserved its existing complex walls, fenestration, floor slabs, and roof equipment. Envelope match alone is not full topology or elevation certification; height, internal arrangement, roof equipment and solar details remain unverified.

## Reopen checks and integration

All five libraries reopened with the expected exported collection. The three rebuilt shells have maximum vertex-to-source discrepancies below0.000003m after applying the unchanged manifest placement origins. This measures construction consistency with the cached reference, not geographic source accuracy. Check results: verification.json; initial evaluated geometry: inspection.json; object changes: changes.json. Individual top views are *_after_top.png. Backups before mutation are *_before.blend.

Local origins and placement markers must remain unchanged. Parent should unlink matching old massing libraries for POTR, ME, and BHEE, including separate component features if represented. Reload the master and inspect their relationship to WALC, engineering fountain, roads and other neighbors. Three buildings now have source-matched horizontal massing, one has environment overlap corrected, and one is unchanged after review. None have verified heights; WALC detailed outline discrepancy remains unresolved and must stay visible in project status.

## Follow-up: WALC exterior rebuilt

The earlier WALC outline exception is superseded by the saved perimeter correction. Built exact official FID906 exterior edges in the existing local frame, with28cm inward wall thickness, footprint-shaped roof, masonry/limestone spandrels, glass bands and piers. Exterior vertices are copied from the official reference; reopened roof outline discrepancy is recorded in verification.json. The prior undersized exterior facade and four incompatible roof surfaces have been preserved in disabled collection WALC_Previous_Exterior_Reference, outside exported Asset_walc. Furniture, interior partitions, basement, stairs, and landscape remain. Original pre-correction library remains walc_before.blend; the additional pre-shell state is walc_before_shell.blend.

Facade/window arrangement is a visual estimate rather than surveyed architectural detail. Roof was simplified to a footprint-shaped flat17m cap;16.7m wall elevation is inherited from the previous roof spring level and remains an estimate. The preserved interior is not certified as the real WALC interior. Four buildings now have corrected horizontal envelopes; Knoy remains unchanged with matching outline bounds. No known identified horizontal discrepancy is intentionally retained in the exported WALC shell.

Old Knoy duplicate inspection: massing_knoy_hall_knoy_f598616.blend exports Asset_massing_knoy_hall_knoy_f598616, containing object Knoy Hall (KNOY). Parent should unlink this collection if present in master. Evidence: knoy_old_massing.json. File left unmodified.
