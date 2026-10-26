# WALC independent grade — R3

**Result: 7.9/10 — below the 8.0/10 completion threshold.**

**Asset SHA-256:** `c9ca2cfe413898780445bade8e729e22510535aed123407c4d11e5c28f53ec65`  
**Independent reopen:** Blender 5.2.3 LTS. I independently opened the exact hashed standalone asset. `Asset_walc` contains 951 objects and 879 meshes. `AssetRoot_walc` has identity location, rotation, and scale. The foliage library resolves from `//..\site\foliage_library\engineering_foliage_library.blend`; all mesh objects have valid material slots, and the image texture is packed. Reopen details are in [independent_grade_r3_reopen.json](independent_grade_r3_reopen.json).

R3 improves exterior readability over R2: the newly added vertical blades establish a stronger vertical rhythm, the glass/brick/limestone/bronze materials are brighter, and the official reference renders are documented. The north, southeast and southwest daylight renders remain dominated by uninterrupted horizontal glazing and red-brown horizontal bands. In Purdue's 2018 exterior photo, solid masonry piers separate window groups and the entry has stronger depth and articulation. R3's thin blades do not yet produce those large-scale bays and masonry masses, so the recognizable façade mismatch remains significant. The broad roof plane and pale roof inset also remain weakly verified. Interior geometry/program is unchanged from R2: useful spaces are represented but layouts and finishes are still schematic, with no as-built floor plans checked.

## Scorecard

| Category | Score | Findings |
|---|---:|---|
| Identity and plan footprint | 2.0/2.0 | The footprint continues to trace the cached Purdue GIS FID 906 outline. The reported sub-millimeter residual repeats the trace used during modeling; it is not an independent wall survey. |
| Local frame and structure | 0.9/1.0 | Identity root/local frame are preserved, and the relative foliage library resolves. No master `Placement_walc` marker or adjacent campus alignment was checked in this standalone review. |
| Exterior architecture | 1.35/2.0 | Vertical fins improve bay rhythm and facade depth. The renders still show long horizontal ribbons instead of the solid pier-separated window groups, more articulated entry and roof edge seen in official exterior imagery. Roof shape/heights remain estimates without a dimensioned elevation. |
| Materials and surface finish | 1.05/1.5 | R3's material coordination and brightness improve inspection over R2. At the scale and lighting of the saved renders, brick/stone texture is subdued and the overall facade remains stripe-like; plaza/paving treatment is still generic. |
| Interior and program | 1.45/2.0 | The reading room, atrium, stairs/bridges, stacks, theatre, active-learning classroom and basement remain represented. These are useful schematic spaces, but R3 did not change them and no architectural plans verify room locations or layouts. |
| Reopenability and evidence | 1.15/1.5 | Exact SHA reopened independently in Blender 5.2.3; linked foliage path exists, image texture is packed, and no materialless meshes or invalid slots were found. The record includes official photo/program sources and explicit uncertainty, but the master placement, roof dimensions and as-built interior are unverified. |
| **Total** | **7.9/10** | **Below 8.0/10.** |

## R3 change assessment

- **Facade articulation: partial improvement.** The added 162 vertical blades read in all three daylight renders and improve the horizontal bands. Their slender, fin-like appearance does not substitute for the deeper solid masonry piers and grouped windows evident in Purdue's exterior photo.
- **Materials and daylight: partial improvement.** Materials and exposure are easier to inspect than R2, but the renders still make most large surfaces read as broad, uniform bands. A clearer brick/limestone response and stronger glazing depth would improve the normal campus-scale view.
- **Interior: unchanged.** The R2 program representation remains useful for visualization but schematic. Do not treat the classroom configurations or room locations as verified construction plans.
- **Footprint and placement: limited claim.** Cached GIS outline agreement supports the author's traced roof polygon only. This review did not open the campus master or validate the building marker against roads and neighboring assets.

## R4 priorities

1. Rework representative elevations into actual window groups separated by substantial, source-supported masonry piers; use the official photo for visible rhythm and retain uncertainty about dimensions.
2. Add depth at the entry and show the ground-floor glazing, piers and canopy as distinct masses. Improve brick/limestone contrast and texture at the southwest and southeast campus-view distances.
3. Verify roof edge, inset and level changes against authoritative imagery or drawings; clearly label estimates where no measured source is available.
4. Compare interior zones with official program and available floor references; maintain `schematic` status for unverified room positions and layouts.
5. Have the master integrator verify `Placement_walc` and surrounding plaza/roads in the full campus file.

## References and uncertainty

- [Purdue News — Then & Now: Wilmeth Active Learning Center](https://www.purdue.edu/newsroom/archive/purduetoday/releases/2018/Q4/then-and-now-wilmeth.html) (2018-11-18) and its [official exterior photo](https://www.purdue.edu/uns/images/2018/pt-wilmeth-6446.jpg) provide visible facade/entry context, not a dimensioned elevation.
- [Purdue Office of Emergency Preparedness — WALC Building Emergency Plan](https://www.purdue.edu/operations/emergency-preparedness/walc/) (revision 2026-04-03) supports the floor/program description, not exact interior layouts.
- [Purdue Chemistry — Wilmeth Active Learning Center](https://www.chem.purdue.edu/media/news/2017/wilmeth.html) (2017-04-12) supports opening-era classroom program and configurations, not room-by-room as-built geometry.
- Footprint reference: cached Purdue BuildingShapesZip4 FID 906 in `audit/official_building_references.json` (retrieved 2026-10-22). This is the same trace used for authoring and is not independent survey evidence.
- Reviewed R3 renders: `southwest_r3_daylight.png`, `southeast_r3_daylight.png`, and `north_r3_daylight.png`. Builder's change log: `r3_change_log.md`.

**Asset/master/shared files modified:** no. **Commit created:** no.
