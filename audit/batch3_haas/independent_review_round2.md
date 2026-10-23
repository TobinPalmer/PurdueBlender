# Felix Haas Hall — independent review round 2

**Asset inspected:** `modular/buildings/felix_haas_hall.blend`, saved correction evidence and reopened renders dated 2026-10-23.  
**Overall score: 6.4/10.** The revisions fix the entrance stair count, remove the most unsupported far-side window treatment, and simplify the uncertain rooftop ornament. The building is still a rough reconstruction and does not meet the requested 9/10 bar.

## Category scores

| Area | Score | Review |
|---|---:|---|
| Building form and architectural detail | 6/10 | The GIS wall shell preserves the irregular campus footprint, and the roof is now a restrained hipped form. In the exterior render, however, most of the near long elevation remains a large, flat brick-colored plane. The Purdue photo shows repeated limestone piers, lintels, sills and masonry panels across the façade; the model puts most of that detail on the small entrance projection. The entrance elevation also appears much narrower than the main façade in the source photo. The comparison is qualitative because the photo has perspective and no survey scale. |
| Materials and textures | 5.5/10 | The asset has distinct brick, limestone, roof, glass and interior materials, and the roof material uses a procedural brick/tile node. At the saved render scale, the roof reads as broad plain reddish-brown planes, the long wall as a nearly uniform peach-brown surface, and the entrance stone as cool blue-gray. These do not reproduce the warm pale limestone and red-brown brick contrast in the Purdue exterior photo. The material inventory alone does not establish that the patterns read correctly on the model. |
| Windows and roof | 5.5/10 | The visible long side now has five upper and five lower openings, with frames/sills, and the rejected far-side window treatment is gone. The openings still read as simple inset panels on a largely blank elevation; the opposite elevations are not verified. The hipped roof silhouette is plausible, but its dimensions and tile detailing are image-based estimates. The reduced cupola is a short circular drum in the render; its real form remains unverified and the evidence correctly labels it estimated. |
| Main entrance and stairs | 7.5/10 | I verified 17 separately named tread meshes (`HAAS_Photo_Entry_Stair_Tread_00` through `_16`), matching Purdue Archives’ stated count of 17 memorial steps. The stair and low cheeks are clear in the close render. The approach remains schematic: riser height, tread depth, width and landing geometry are estimated, and the modeled central limestone surround is simpler than the photo’s broad, articulated entrance façade. |
| First-floor rooms and circulation | 6.5/10 | The cutaway includes the three labeled stair cores, lift, restrooms 117/119, conference rooms 111/101, student organization room, TA-office area and room furniture. Those names and broad adjacencies are supported by Purdue CS’s first-floor diagram. At the supplied render size, several labels are difficult to read and many perimeter offices are generic; there is no measured registration, and the diagram is nondimensioned. Upper floors and current layouts are not verified. |
| Scale and placement | 8.5/10 | Reopened asset reports 771 direct export objects. The GIS shell remains at bounds `[-26.2203, -25.9795, 0]` to `[12.9812, 26.7597, 11.5]` m, unit scale and zero rotation; the two roof objects also have unit scale and zero rotation. This confirms the local shell envelope was preserved. Roof heights, interior registration and cupola dimensions remain estimates. The batch evidence says the master and manifest have not yet been refreshed. |
| File and integration hygiene | 7.5/10 | The individual file reopened, the expected export collection is present, and the recovery archive is hidden. The parent integration still needs to refresh manifest metadata and re-open the linked master after accepting this 771-object asset. These checks do not confirm master linkage or scene placement. |

## Source checks and limits

- Purdue Archives’ historical timeline identifies Felix Haas Hall as Memorial Gymnasium and says 17 steps lead to the entrance in memory of those killed in the 1903 train wreck. This supports the corrected tread count, not the estimated metric dimensions: [Purdue University Historical Timeline](https://collections.lib.purdue.edu/timelines/puhistorical).
- Purdue Computer Science’s first-floor plan names the rooms, three stair locations, elevator, restrooms, and two conference rooms. It has no scale, so it supports adjacency and room identity only: [HAAS Hall — First Floor](https://www.cs.purdue.edu/resources/docs/HAAS_first.pdf).
- Purdue’s event page identifies the building and provides a qualitative exterior photo. The archived `audit/batch3_haas/exterior_reference.jpg` is consistent with that reference: pale limestone framing, contrasting brick fields, arched lower windows, and a broad hipped roof. The saved exterior render does not yet carry those façade details across the long elevation: [Felix Haas Hall, Purdue Events](https://events.purdue.edu/felix_haas_hall).
- I attempted to open Google Maps directly through the web lookup, but that route did not expose the Maps gallery in this review session. The prior batch’s recorded Maps photo review is user-contributed and useful only as qualitative evidence; it cannot establish dimensions. I therefore used the preserved Purdue photo and current asset renders for this visual comparison.
- `reopen_check.json` confirms the individual file reopen, collection count, selected bounds, and transforms. It does not measure facade accuracy or prove that the current master has linked the updated asset.

## Highest-value remaining fixes

1. Extend the documented limestone and brick bay rhythm across the primary long façade, matching the Purdue photo’s repeated piers, window surrounds and horizontal courses.
2. Tune the rendered materials and lighting together so warm limestone, red-brown brick and roof tile colors read like the source photo; make tile texture visible at the campus-view scale.
3. Verify the remaining elevations and cupola with better photo or archival references before adding detailed geometry. Keep unverified parts clearly marked as estimates.
4. Improve the room-plan presentation so the supported stair cores, elevator, restrooms and named rooms are legible, and document the estimated registration separately from the plan’s proven adjacencies.
5. Have the master agent refresh manifest object metadata and run the linked-master reopen/placement check after integrating this saved source asset.

**Conclusion:** not 9/10. The 17-step correction is verified, but the façade coverage/material read and unverified elevations still dominate the score.
