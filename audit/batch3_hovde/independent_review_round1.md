# Hovde Hall — independent review, round 1

**Score: 5.8/10. Does not reach 9/10.** This is a recognizable low-detail Hovde massing with its long brick wings, central entrance, four visible levels, and site approach. The saved file reopens and the asset export/material checks pass, but the exterior still misses several defining features visible in the cited photo, the interior cutaways do not read as complete rooms, and placement/height remain only partly verified.

## What I checked

- Read `audit/batch3_hovde/REVIEW.md`, `final_asset_check.json`, and `final_check.log`.
- Inspected `exterior_material_preview.png`, `presidential_office_cutaway.png`, and `trustees_boardroom_cutaway.png`, produced after reopening the saved asset.
- Confirmed the saved export has 638 objects, including 626 meshes; all meshes have materials, the `Asset_hovde_hall` collection and `Building_hovde_hall` scene are present, and the root scale is 1. The check log shows Blender reopened the target file and exited normally.
- Compared the exterior against the dated, geotagged 2016 Julian Herzog photograph and other Hovde exterior photos. The references show a central classical portico with six substantial columns, a triangular pediment, a broad stone stair, symmetrical brick wings, and a visibly red roof. The cited photo file page identifies the photo date and coordinates: [Wikimedia Commons photo record](https://commons.wikimedia.org/wiki/File:Frederick_L_Hovde_Hall_of_Administration_Purdue_University_2016_01.jpg). A second exterior image with the same major elements is available from [Purdue Agriculture](https://ag.purdue.edu/news/2024/index.html).
- Placement source evidence in the project identifies Purdue GIS feature 618 and its 2026-10-22 snapshot. The manifest placement marker is `[-49.8026928902, 78.2442455292]`; the saved asset's internal `HOVD_Root` is at `[-62.85, 93.0, 0]` with a 0.68975 rad rotation. These are different transforms with different roles, so I did not treat the internal root position as a campus-placement error. The current audit does not provide a fresh master-neighborhood render or a post-edit polygon overlay, so I cannot independently certify final placement from these three building renders.

## Findings and prioritized fixes

1. **Rebuild the portico silhouette and materials from the photo.** The render's entrance reads as a flat, deep rectangular box with narrow, evenly spaced poles. The source shows six prominent columns supporting a triangular stone pediment, with an integrated classical facade and broad stairs. The current visible pediment is flat/rectangular, and the columns lack the substantial proportions and capitals needed to carry the reference silhouette. Increase the central portico's visual prominence and match the light Bedford limestone against the red brick.
2. **Resolve the roof appearance.** The current roof is a large uninterrupted charcoal membrane slab and competes with the building's facade. The Hovde exterior photo shows a red roof surface. Use a Hovde-specific roof-visible reference to decide between tile and another red roofing material, then model/texture its visible edge and roof form accordingly. Avoid carrying the dark slab forward without explaining the source conflict.
3. **Improve window readability.** The window openings appear nearly black and flat, with small uniform sills. Add visible glazing/reflection, frame depth, and reasonable muntins or sash cues based on the facade photo. The procedural brick shader is a useful addition, but in the wide render the wall still reads as mostly uniform red; check the course pattern at building scale and ensure mortar does not dominate or disappear.
4. **Make the two interior views read as rooms.** The presidential-office cutaway shows an almost entirely open square with a small central desk assembly; the boardroom shows a table/chair strip in a much larger open square. The oversized empty floor areas and absent readable walls, doors, and circulation make the spaces feel like furniture placed on a slab. The review notes both floor extents are about 26.1 × 26.0 m; verify that each layout is contained by the actual shell and scale it to a credible room footprint. Add enough partitions, door openings, and circulation to communicate an office and trustees' boardroom. Keep the furnishings marked as illustrative unless an interior plan or photo is found.
5. **Finish geometry/placement verification.** The four-story count and historic 70 × 230 ft dimensions are useful context but do not verify the model's 19.25 m penthouse height. Record wall-only plan agreement separately from overhang/site objects and verify orientation and location with an overlay against feature 618 in the master context. The existing documentation explicitly says the core offset, height, site, and interior layout are estimates; preserve those limits until better source drawings are available.

## Category assessment

| Area | Assessment |
|---|---|
| Building identity and broad massing | Recognizable; four-level long wings and centered entrance read correctly at a glance. |
| Facade detail | Below reference: portico proportions/pediment and window treatment need substantial refinement. |
| Materials | Material assignments are complete and colored preview sync works. Brick pattern is subtle at overview scale; stone and roof appearance need source-based adjustment. |
| Interior | Both named spaces exist, but the views show broad empty slabs and weak room enclosure; accuracy is unverified. |
| Geometry and dimensions | Historic plan dimensions provide a check target, but no fresh wall-only footprint comparison or measured height is included in this review packet. |
| Placement | Manifest marker is documented. A current master overlay/render is needed to confirm neighborhood placement after this asset's updates. |
| File integrity | Reopen check succeeded; expected scene and collection exist; no unmaterialed mesh objects were reported. |

**Recommendation:** continue building-side revisions and request another independent review after correcting the portico, roof, windows, and room enclosure. Do not mark this asset complete or rate it 9/10 yet.
