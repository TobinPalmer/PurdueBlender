# CREC independent asset review — revision 3

**Score: 7.7/10 — still below the requested 8/10 pass threshold.**

| Category | Score | Review |
|---|---:|---|
| Location, footprint, and scale | 1.8/2 | The asset continues to follow Purdue GIS feature 315 and retains the campus-world coordinate convention. The east eyebrow extends outside the GIS outline, but stays near the prior massing envelope. The combined roof/building outline remains an approximation rather than a surveyed wall line. |
| Architectural and photo match | 1.4/2 | The east facade now has a tall blue curtain wall, visible return glazing at one end, lower entry portal, projecting lower canopy, and a red-brick wing. These cues match the Purdue and Moody Nolan photos. In the main render, the upper atrium still reads as a long, nearly flat glass frontage. The three-storey corner and its large roof overhang do not stand out as clearly as in the reference; the upper eyebrow is largely hidden by the continuous roof edge and the camera is close to frontal. |
| Facade materials and detail | 1.55/2 | Brick, stone, blue-gray glass, dark bronze framing, and floor bands are distinct. The glass is more reflective than in R2, the brick transition is clear, and the ground entry portal adds scale. Window rhythms remain repetitive and the surface treatment is still mostly procedural and smooth. |
| Supported interior and program | 1.3/2 | The roof-off image now has readable area labels, and it shows the lap pool, court zones, climbing wall, and fitness floor consistent with official facility descriptions. Most court lines remain faint at this view scale. Internal layouts and their relative positions are explicitly schematic, since no measured floor plan was found. |
| Modular integrity and evidence | 1.65/2 | The stable asset ID and collection contract appear preserved. Three renders document facade, roof, and interior. However, the saved `validation.json` hash (`a9a4344a…`) does not match the current blend hash, so the reopen validation record is stale after the last edits. The roof overview hides the footprint roof cap and reveals disconnected block tops over a black background; it helps illustrate height steps but is not a convincing roof-plan view. |
| **Total** | **7.7/10** | **Another focused pass is needed.** |

## Highest-value next fixes

1. Render the atrium from an oblique, street-level angle that shows both glazed return faces and the eyebrow underside. Ensure the main roof does not visually merge with or conceal the canopy.
2. Keep roof evidence connected to the footprint. The current roof-study render shows isolated flat blocks because the cap is hidden; instead show a continuous roof surface with visible step heights and differentiated wings, or a clearly labeled massing diagram.
3. Increase the contrast and scale of basketball court markings in the labeled program view, and refresh `validation.json` after the final saved blend so the recorded SHA matches.

## Evidence inspected

- Current blend: `modular/buildings/massing_france_a_c_rdova_recreational_sports_center_ae69df0.blend`
- Current blend SHA-256: `b801926540e46b70dff32d66ae5871eefcd6200594af349ef1f54ba50afe3135`
- Current images: `crec_east_entry.png`, `crec_roof_overview.png`, and `crec_interior_cutaway.png`
- Source record and Purdue GIS feature 315; the orthophoto overlay; Purdue Historic Building Database and RecWell fact sheet; Moody Nolan project description; the geotagged Julian Herzog photo and its attribution metadata.

This is an independent visual and source-backed review. It does not modify the blend or its builder.
