# Engineering Mall Groundwork Patch

This is a standalone, unintegrated Blender library for Engineering Mall and Engineering Fountain paths, paving, turf, and campus plant inventory. All authoritative mapped features use the project-local campus coordinate system (X east, Y north, Z up; origin 40.4274, -86.9137), as documented in `modular/AGENTS.md`. The modeled focus extent is X -105 to 110 m and Y 90 to 300 m.

## Sources and evidence

- OpenStreetMap geometry snapshot retrieved 2026-10-23: `audit/engineering_precinct/osm_snapshot.xml`. It supplies 93 clipped path ribbons, 30 turf parcels, Engineering Fountain anchor way 283274213, and the filled outer plaza polygon way 283274215. Mapped path widths and surface descriptions can be estimates or contributor tags; this is not a new ground survey.
- Purdue Arboretum Open Data inventory snapshot retrieved 2026-10-23: `audit/engineering_precinct/arboretum_plants_snapshot.json`. The asset places 349 mapped tree/shrub records at their inventory points and stores species, habit, DBH, dimensions, and measured-versus-inferred status. Missing dimensions and canopy silhouettes are explicitly estimated.
- Purdue Engineering Computer Network Cam05 archive: [archive grid](https://engineering.purdue.edu/ECN/WebCam/cam05/grid) and fixed comparison frame [2023-06-19 image](https://engineering.purdue.edu/ECN/WebCam/cam05/2023_06_19_14_40.jpg). The image overlay reads `2023-06-19 13:12:37`; this differs from the filename time. Purdue identifies Cam05 as a third-floor MSEE view.
- The ECN camera's exact window, position, height, azimuth, lens, and ground calibration are not published. The candidate view uses an inferred mall-facing MSEE facade point XY=(55,185)m, Z=13m, azimuth 222 degrees, 9.5-degree downward pitch, and 24mm lens. These values are framing estimates within the mapped MSEE footprint. A separate `EngineeringMall.jpg` geotag belongs to another photo and is not used to place the ECN camera.
- Five staggered localized midground trees are **image-derived inferred planting points**, back-projected from canopy locations in the frame. Their regional species estimates draw on the StoryMap; individual species, exact position, height, and crown spread are not verifiable from the photo, and each object records that uncertainty. They are separate from the 349 authoritative inventory points. Inferred crowns use irregular multi-lobe geometry with per-tree green and roughness variations.
- The broad foreground forecourt drive and left diagonal approach are **image-derived inferred features**, traced from the fixed ECN frame by back-projecting image rays to the ground plane using the estimated camera. They are separately tagged with the reference URL, projection assumptions, and uncertainty; authoritative OSM path lines remain distinct and unchanged. Their image-space positions and widths are approximate, not survey data.
- Supplementary botanical context: [Purdue Arboretum BikePack LiDAR and camera survey StoryMap](https://storymaps.arcgis.com/stories/b3ec50be797645499ac2ac3d6e199aed). Tree points and names in the patch follow the Arboretum inventory where available.

## Files and review

- `modular/site/engineering_mall_groundwork_patch.blend`: standalone collection `Engineering_Mall_Groundwork_Patch`.
- `modular/site/build_engineering_mall_groundwork_patch.py`: reproducible patch builder.
- `modular/site/foliage_library/engineering_foliage_library.blend`: packed project-local Asset Browser library with linked/instanced tree, shrub, fir, fern and selective grass assets; seven reused campus materials; and four reusable site prop families. Rebuild with `modular/site/foliage_library/build_engineering_foliage_library.py`; see its README for source prerequisites and license/provenance.
- `modular/site/render_engineering_mall_candidate.py`: builds the lightweight comparison scene using the patch, fountain, and nearby context shells.
- `audit/engineering_precinct/engineering_mall_foliage_library_review.blend` and `.png`: latest candidate comparison scene and render with linked Poly Haven foliage and PBR ground/asphalt materials. The campus master Blend was not opened or saved.
- Reopen QA: 349 mapped plants + 5 inferred plants are linked collection instances, preserving mapped object locations and metadata; 93 clipped OSM path ribbons, 30 OSM turf parcels, and the plaza fill remain. The library contains 76 packed images, 18 marked collection assets, 9 marked material assets, and one relative library link.
- The preview adjusts context shells for legibility, including window bands on the visible Mechanical Engineering face and a clearly tagged, image-derived portico/pediment silhouette. These are preview-only treatments; source building libraries remain unchanged.
- Reopen/validate the saved patch with Blender using `audit/engineering_precinct/verify_patch.py`. Expected totals: 349 inventory plants plus 5 explicitly inferred canopy points, 93 OSM path ribbons, 30 turf parcels, and a filled plaza polygon.

This patch awaits review and integration by the master-file owner. It does not modify the campus master or its manifest.
