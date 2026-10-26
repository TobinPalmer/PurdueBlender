# WALC R3 refinement record

Date: 2026-10-25  
Asset: `modular/buildings/walc.blend`  
SHA-256 after save and fresh reopen: `c9ca2cfe413898780445bade8e729e22510535aed123407c4d11e5c28f53ec65`

## Changes

- Rebuilt the R2 facade-fin object as 162 more visible, slightly deeper vertical blades along the existing three levels of glazed wall segments. Their spacing is an approximate visual rhythm; it is not an as-built bay schedule. Existing source wall bands, GIS roof trace, roof outline, local origin, and identity root were preserved.
- Brightened and coordinated the brick, limestone, glass, bronze, roof, plaza tile, and limestone viewport colors, so the material divisions read under neutral Workbench lighting.
- Added a subdued procedural running-bond brick pattern with mortar color to the brick shader. Preserved the existing stone variation and bump treatment. Tuned the glass shader to a lighter blue-gray with a lower roughness and metalness for more legible window planes.
- Rendered new neutral daylight review views: `southwest_r3_daylight.png`, `southeast_r3_daylight.png`, and `north_r3_daylight.png`. The repeating tall glazed bays and warmer masonry now read separately in ordinary exterior views. The remaining horizontal floor bands are part of the simplified existing massing; R3 did not change their elevations or claim measured facade dimensions.
- Did not change the interior geometry. Purdue's available program information confirms four total floors (three above grade, one basement), 27 classrooms, second-floor library stacks, and first-floor cafe. Exact room plans, partition layouts, facade dimensions, and roof assembly remain schematic/unverified where dimensioned/as-built sources were unavailable.

## Source evidence

- Purdue University, “Then & Now: Wilmeth Active Learning Center,” published 2018-11-18, accessed 2026-10-25. Official campus exterior image and context: https://www.purdue.edu/newsroom/archive/purduetoday/releases/2018/Q4/then-and-now-wilmeth.html and https://www.purdue.edu/uns/images/2018/pt-wilmeth-6446.jpg. Supports red-brick facade, tall rectangular windows, and landscaped plaza; does not supply a measured elevation or mullion schedule.
- Purdue University Office of Emergency Preparedness, WALC Building Emergency Plan, revision 2026-04-03, accessed 2026-10-25: https://www.purdue.edu/operations/emergency-preparedness/walc/. Supports story count and listed program; not architectural plans.
- Purdue Department of Chemistry, “Wilmeth Active Learning Center,” published 2017-04-12, accessed 2026-10-25: https://www.chem.purdue.edu/media/news/2017/wilmeth.html. Supports 27 classrooms and confirms contemporary program/context, not room-by-room as-built plan.
- Footprint/identity check uses cached Purdue Campus GIS BuildingShapesZip4, FID 906, in `audit/official_building_references.json` retrieved 2026-10-22. R3 uses the same outline as the prior asset. Its near-zero residual demonstrates agreement against that same cached source trace and is not independent survey verification.

## Fresh-open validation

`independent_reopen_r3.py` freshly reopened the saved asset in Blender 5.2.3 LTS and wrote `independent_reopen_r3.json`. It verified the saved hash, expected `Asset_walc` collection, identity `AssetRoot_walc`, 951 objects / 879 meshes, 24 used materials, no materialless meshes, no invalid material slots, no missing external images, and a resolving project-relative foliage library at `//../site/foliage_library/engineering_foliage_library.blend`. The artwork image is packed. The check remains standalone and does not verify the master `Placement_walc` marker or neighboring campus alignment.

## Unresolved

- No dimensioned elevation, facade bay schedule, roof plan, or measured height source was found for this pass. Vertical blade spacing, masonry pattern scale, and roof detail remain visual estimates.
- Interior features remain schematic because public program references do not verify room-by-room layouts. A master-file inspection is still required for campus placement and context.
- No commit was created. Only `modular/buildings/walc.blend` and WALC-specific records in `audit/walc_refine/` were changed.
