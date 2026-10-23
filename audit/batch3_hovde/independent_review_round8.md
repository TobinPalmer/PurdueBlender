# Hovde Hall — independent review, round 8

**Score: 7.8/10. Does not meet the 9/10 target.** Round 8 makes the entry easier to read by removing the two supports from the doorway zone and reducing the pediment span. The saved asset reopens, the export collection has material assignments on all meshes, and the interpretive room studies are clearly labeled. The principal remaining exterior issue is that the portico still masks central facade windows and reads as a large, shallow stone overlay. The interior is furnished and enclosed, but remains a blocky, unverified diagram. Roof form and master placement are still unresolved.

## Evidence inspected

- `exterior_round8.png`, `portico_detail_round8.png`
- `presidential_office_cutaway_round8.png`, `trustees_boardroom_cutaway_round8.png`
- `final_asset_check_round8.json`, `REVIEW_round8.md`, `round8_edit.py`
- Independently inspected the saved asset check: 717 exported objects / 705 meshes; no unmaterialed meshes; root is `[-62.85, 93.0, 0]`, Z rotation `0.689754 rad`, scale `[1,1,1]`. This confirms asset integrity and retained local transform, not alignment in the campus master.
- Compared the visible massing/material cues against Julian Herzog's geotagged 2016 Hovde exterior photo ([Wikimedia source page](https://commons.wikimedia.org/wiki/File:Frederick_L_Hovde_Hall_of_Administration_Purdue_University_2016_01.jpg)) and the West Lafayette visitor guide. These support the four-story brick administration block and a classical central entrance, but are not measured elevations or roof references. Purdue Archives' Hovde record supports administration/boardroom context, not the modeled room plans.

## Findings and ranked corrections

1. **Make the portico sit cleanly on the facade.** Removing the inner supports clears the three door leaves in the close view, which fixes the most obvious entry obstruction from round 7. The four remaining supports are an acknowledged visual interpretation; no cited elevation verifies their count or spacing. The wide pale entablature/pediment still crosses and hides several central window bays, and the pale mass reads nearly flush with the brick instead of as a legible, deep portico. Reduce or lift the assembly to preserve the facade rhythm, expose the central windows, and show support depth, bases, capitals, and a clear door-to-entry relationship. Keep the geometry marked estimated until a measured elevation is found.
2. **Improve the interiors while keeping their status clear.** Round 8 adds a useful interpretive label to the office and boardroom cutaway images. Floors, three retained walls, tables, chairs, shelving, and office furniture make each room read as enclosed space. The furniture and fittings still use large simple blocks; walls are mostly blank, circulation and connections to corridors are absent, and source material does not establish these layouts. Add restrained, human-scale architectural details and opening/circulation cues only where supported. Preserve the explicit plan-not-verified label.
3. **Refine and verify exterior materials and roof.** Mesh material coverage is complete and the brick, pale limestone, dark glazing, and stone bands make the building identifiable. In the renders, the brick pattern is high contrast and repetitive at the facade scale; glazing reads as uniform opaque blue; the portico is a flat pale material with little separation between members. Reduce texture contrast/repetition and add subtle depth variation. The roof remains a broad dark red-brown plane with a small raised cap; the cited ground-level photos do not verify this silhouette or finish, so treat it as provisional pending an overhead/archival source.
4. **Complete the master placement check.** The local origin and rotation stayed unchanged. Compare the structural shell against official Purdue GIS feature 618 in the linked campus master, checking orientation and scale independently from steps, portico, and plaza. Inspect the entrance relation to Elliott Hall and nearby access. This remains outside the building-side evidence delivered for round 8.

## Category assessment

| Area | Assessment |
|---|---|
| Identity and massing | Recognizable four-story, long brick administration block with central classical entry. |
| Entry | Door openings are clearer after inner supports were removed; portico still hides central windows and looks shallow. Exact support count/proportions are unsupported. |
| Materials | All export meshes have materials; brick repetition and uniform glass/stone need refinement. Roof material and profile are unverified. |
| Interior | Two enclosed, furnished cutaways with honest interpretive labels; both remain schematic and not source-verified. |
| Saved asset | Reopens; export collection/material check passes; retained root transform is verified. |
| Campus placement | GIS/master fit and neighbor context remain pending. |

**Decision:** revise before calling complete. Round 8 resolves the support/door collision and improves clarity of the room evidence, but the portico still obscures facade openings, material finish and roof are only partly supported, interiors remain schematic, and master placement is unverified. It does not reach 9/10.

## Source basis and limitations

- [Julian Herzog's dated Hovde exterior photo](https://commons.wikimedia.org/wiki/File:Frederick_L_Hovde_Hall_of_Administration_Purdue_University_2016_01.jpg), photographed 18 September 2016, documents the exterior from street level and includes geolocation. It is a visual comparison, not a measured elevation.
- [West Lafayette visitor guide](https://assets.simpleviewinc.com/simpleview/image/upload/v1/clients/westlafayettein/2022_Visitors_Guide_0481c246-c159-4d01-a3a6-e00c4eddae3e.pdf) includes an exterior image and supports the broad classical entrance character.
- [Purdue Archives Hovde Hall record](https://archives.lib.purdue.edu/agents/corporate_entities/573) provides building/administration and boardroom context, not exact interior layouts.
- Roof plan/profile/finish, measured portico dimensions and exact column count, window schedule, room layouts, and GIS/master alignment remain unverified.
