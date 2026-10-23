# Hovde Hall — independent review, round 7

**Score: 7.8/10. Does not meet the 9/10 target.** I independently reopened `modular/buildings/hovde_hall.blend` in Blender 5.2.3 and inspected the round 7 exterior, portico close-up, presidential-office cutaway, trustees-boardroom cutaway, export/material check, and key door/portico geometry. Round 7 fixes a real entry failure: the three door assemblies now face the east facade, and the limestone surrounds are open frames instead of solid blocks. The two room studies now show perimeter walls and floors in an oblique cutaway. These are tangible improvements, but the portico still obscures the central facade, the interior layouts remain interpretive, and master/GIS placement has not been verified.

## Evidence checked

- `exterior_round7.png`, `portico_detail_round7.png`
- `presidential_office_cutaway_round7.png`, `trustees_boardroom_cutaway_round7.png`
- `final_asset_check_round7.json`, `REVIEW_round7.md`, `round7_door_alignment.py`
- Independently reopened the saved blend. The export collection contains 727 objects / 715 meshes, with no unmaterialed meshes. `HOVD_Root` remains at `[-62.85, 93.0, 0]`, Z rotation `0.689754 rad`, unit scale. This verifies saved asset identity and transform only; it does not prove the root aligns correctly in the campus master.

## Findings and ranked corrections

1. **Make the entry and portico work together.** The three bronze door leaves and glazed transoms now read in the close view; the open limestone surrounds line up with them. However, the six supports remain so close to the door jambs that they visually overlap the openings, and the broad pediment/entablature covers adjacent brick bays. The front image still reads as a large pale overlay with narrow vertical strips rather than a clearly detached, dimensional portico. Pull the support rhythm away from the door openings, add visible depth and base/capital separation, and reduce or reposition the assembly so the central facade and entry stay legible. Keep dimensions marked estimated until a measured elevation is found.
2. **Show a more convincing enclosed interior.** The two round 7 renders are a meaningful improvement over furniture-only plan views: each now shows a floor and three enclosing walls in an oblique cutaway. The office has a single executive desk and sparse seating; the boardroom has a long table and chair row. Both remain largely blank-wall schematic studies, without verified plans, a clear door-to-corridor relationship, or much architectural detailing. Retain their interpretive label, improve opening/circulation cues and human scale, and avoid presenting the layouts as surveyed interiors.
3. **Verify exterior color and roof form.** The brick texture, pale stone bands, recessed dark glazing, and limestone portico materials are coherent and all exported mesh objects have material assignments. From the renders, the brick pattern repeats strongly at building scale; the glass reads as uniform dark blue panes. The roof is a nearly flat dark red-brown plane with a small raised cap. The cited street-level sources do not establish its profile or finish, so this remains an estimate. Check roof silhouette and facade color against overhead or archival material before adding more detail.
4. **Complete master/GIS alignment and neighborhood review.** The building-side root remains unchanged, but the round 7 evidence explicitly leaves the official footprint overlay and linked-master check to integration. Compare the structural wall shell with official Purdue building GIS feature 618, check orientation and scale, and inspect the entrance projection and footprint among neighbors in the master. Do not use the portico, steps, or plaza to judge the structural-wall fit.

## Category assessment

| Area | Assessment |
|---|---|
| Identity and massing | Recognizable long, four-story brick administration block. |
| East facade openings | Recessed window bays and three entry voids remain visible; window cadence/details are estimated. |
| East entrance | Correctly oriented leaves/transoms and hollow frames now read. Column positions and portico mass still compete with the doors and hide facade bays. |
| Materials | Brick/stone/glass assignments are coherent and complete in the exported meshes; render-level color and texture repetition need refinement. |
| Roof | Finished material is assigned, but the broad shallow profile and raised cap are not verified by the cited sources. |
| Interior | Enclosed three-wall cutaways and furnishings are present; office and boardroom layouts remain schematic and unverified. |
| Export and placement | Saved file reopens; export collection, materials, and root transform pass. Master/GIS fit is still pending. |

**Decision:** revise before calling complete. Round 7 resolves the door-axis and solid-frame defects and improves interior presentation. It is still short of 9/10 because the portico masks its entrance/facade, and roof, interior layout, and campus placement remain unverified.

## Source basis

- Julian Herzog's dated, geotagged Hovde exterior photo (18 September 2016): [Wikimedia Commons source page](https://commons.wikimedia.org/wiki/File:Frederick_L_Hovde_Hall_of_Administration_Purdue_University_2016_01.jpg). It supports the brick wings and classical central entrance as visible from the ground; it is not a measured elevation.
- [West Lafayette visitor guide](https://assets.simpleviewinc.com/simpleview/image/upload/v1/clients/westlafayettein/2022_Visitors_Guide_0481c246-c159-4d01-a3a6-e00c4eddae3e.pdf), which includes a Hovde exterior image.
- [Purdue Archives Hovde Hall corporate record](https://archives.lib.purdue.edu/agents/corporate_entities/573), cited by the modeling evidence for the historic four-story administration building and Board room. It does not document the submitted room plans or measured portico geometry.
