# Elliott Hall of Music — round 10 evidence notes

Work date: 2026-10-23. Asset scope: Elliott modular source and `audit/batch3_elliott` only. No master, manifest or Hovde asset edits.

## Round 10 repair

The round 9 portal obstruction was traced to the continuous limestone belt courses and lower limestone band crossing the door aperture. The model now has a portal-specific clearance cut through those three trim meshes. Their dimensions are still estimated; no accessible-clear-width or route-compliance claim follows from the cut. The tinted door material was made rougher with lower specular response so the area light does not create an artificial white patch over the glass.

A wider portal render was saved after the cut. It shows both leaves clear of the pale trim and the remaining limestone band ending at the portal sides. The Elliott landing remains isolated. The fresh audience-facing-from-stage render makes the seat tiers, balcony aisles/rails, curtain, and stage front visible together; seating and circulation dimensions are still schematic.

## Evidence and sources

- [SAH Archipedia — Elliott Hall of Music](https://sah-archipedia.org/buildings/IN-01-157-0079) describes the brick/Indiana-limestone palette, clay-tile roof, limestone pilasters and ornament, secondary entrances, fly tower, apse-like stage projection and Hovde connection. This is feature-type evidence and does not give dimensions or verify a window layout. Exact facade schedule and flytower/apse proportions remain unresolved.
- [Purdue Convocations Elliott seating chart](https://convocations.purdue.edu/wp-content/uploads/2022/09/Elliott-Seat-Map.pdf) shows the main floor, first and second balconies, and curved seat blocks. It is not a dimensioned architectural plan. The interior remains explicitly schematic, including stair/aisle relationships, row pitch, egress, stage, and backstage.
- [Purdue Convocations accessibility guidance](https://convocations.purdue.edu/accessibility/) and [Club Convos directions](https://convocations.purdue.edu/clubconvos/) describe accessible venue entries and the Hovde approach, but do not verify the modeled portal's size or continuity.
- The previous round's [Purdue BuildingShapes Feature 617 comparison](footprint_comparison_round9.json) remains the horizontal placement evidence: 0.167 m RMS / 0.259 m max direct ordered-vertex residual, -0.168% area difference, and -0.076% perimeter difference under a documented approximate ground conversion. The GIS FID 617/FID 618 ring contact does not establish a door or route.
- Search located an Indiana state drawing titled “Elliott Hall of Music Main Floor Framing Plan” (search result: https://www.in.gov/idoa/mwbe/files/C4011859-Elliott-Hall-of-MusicBinder1.pdf), but the official host returned a 404 when opened. No plan measurements or geometry were taken from it.

## Reopen result and remaining work

Blender 5.2.3 LTS reopened the saved Elliott file. The linked collection has 135 mesh objects, the three affected trim meshes have no pending Boolean modifiers, the door roughness is 0.68, the deferred scene text is absent, and no round 10 temporary objects remain. Check: `reopen_check_round10.py`.

Still incomplete: verified facade windows/elevations; evidence-backed flytower and apse proportions; dimensional stage/backstage and circulation plan; portal, landing, canopy and support dimensions; Hovde-side opening and connector; accessibility/egress. Do not call the asset fully accurate or accessible on this evidence.
