# Elliott Hall of Music — independent review, round 11

**Score: 7.0/10 (unchanged from round 10).** The seat-fabric color change is source-based and appropriate, but it is a finish pass and does not correct the major exterior or interior geometry gaps. The asset does not reach 9/10.

## What I checked

- Independently reopened `modular/buildings/elliott_hall_of_music.blend` in Blender 5.2.3 LTS using the supplied read-only reopen check. It reports 135 meshes, no `TEMP_R11_` objects, both north/south door objects, and zero modifiers on the three named portal trim meshes. The seat material is gray with a source note.
- Compared `exterior_round11.png` and `interior_from_stage_round11.png` with the round 10 stage view, round 9 audience/plan views, and round 8 exterior elevation.
- Read round 11 handoff, source notes and saved-file check. I made no model, master or script edits.
- Checked current Purdue Convocations pages and the SAH Archipedia building entry. The current Convocations page describes its Elliott image as gray cushioned seats with a wide central aisle and high ceiling. The seat map documents three seating levels and curved blocks. SAH documents red brick, Indiana limestone, clay-tile roof, fly tower, apsidal stage-end projection, curved canopy, secondary entrance surrounds, side-exit stairs and the Hovde connection. These sources substantiate the broad feature palette and auditorium arrangement, but do not provide measured facade dimensions or a window schedule.

## Findings

### Round 11 delta from round 10

The upholstery changed from tan/brown to restrained gray. This agrees with Purdue Convocations' current written image description, and the material includes procedural variation. The comparison renders show the color change clearly. The geometry and room arrangement appear unchanged. Round 10's portal clearance repair remains present and passes the supplied reopen checks. The score stays at 7.0 because the new change improves material fidelity without addressing the larger remaining modeling issues.

### Exterior and texturing

The round 11 oblique exterior makes the footprint massing and roof easier to read, but the large wall fields remain mostly blank brick surfaces crossed by repetitive pale horizontal and vertical strips. The fly tower is a plain rectangular box with a flat cap, and the apsidal end, secondary entries, side-exit stairs and limestone details are still absent, indistinct, or not demonstrated in the provided render. The red brick, limestone-like bands and red roof material are distinguishable, yet the repetitive pattern and broad flat surfaces still read as a schematic exterior. The available source supports these named features generally; their presence should be added from inspectable imagery or drawings, while exact dimensions and window spacing remain labeled as estimates unless measured evidence is found.

### Interior

The gray seat color is an improvement, but the stage view still reads as regular dense arrays of repeated seats across three levels. It does not make a wide center aisle, stair runs, cross-aisles, stage/backstage relationship or circulation legible. The stage floor is empty and simple; red curtain strips and teal balcony edges dominate the view. The seating chart supports three levels and curved blocks, but not row pitch or aisle dimensions. Purdue's current Convocations description specifically mentions a wide central aisle, which is not clearly represented in this view. Keep unsupported dimensions and backstage layout identified as schematic.

### Footprint, portal and neighboring building

The previously reported GIS FID 617 fit is unchanged: 0.1668 m RMS and 0.2594 m maximum ordered-vertex residual under approximate map conversion, with -0.168% area delta and -0.076% perimeter delta. This supports only horizontal footprint fit. The round 11 saved asset retains the previous portal-trim clearance; it does not add a whole-building entrance context. No Elliott-to-Hovde continuous route or accessibility claim can be confirmed from this asset or polygon contact.

## Remaining work before 9/10

1. Add evidence-backed exterior articulation: actual openings and entry/exit features, fly tower profile, apsidal projection and roof treatment. Use source images/drawings that can be visually inspected; avoid filling the currently blank facades with guessed window grids.
2. Rework the auditorium view and geometry so the center aisle, cross-aisles, stairs, stage and balcony transitions read clearly. Use available plan evidence where it exists and label the rest schematic.
3. Improve the large-scale surface treatment and details so masonry, limestone bands/ornament, roof tile and metal/glass have believable variation and depth rather than a repetitive strip grid.
4. Show a wider entry context after both Elliott and Hovde sides are independently verified. Keep the connector and accessibility status unresolved until that check is complete.

## Sources checked

- [Purdue Convocations directions and parking](https://convocations.purdue.edu/directions/) — current page includes the image description of gray cushioned seats, wide central aisle and high ceiling.
- [Purdue Convocations Elliott seat map](https://convocations.purdue.edu/wp-content/uploads/2022/09/Elliott-Seat-Map.pdf) — main floor, first balcony, second balcony and curved seat blocks; nondimensional.
- [SAH Archipedia, Edward C. Elliott Hall of Music](https://sah-archipedia.org/buildings/IN-01-157-0079) — exterior materials and named architectural features; no metric elevation or window schedule in the checked text.
- [Purdue Convocations 75th-anniversary history](https://convocations.purdue.edu/elliott-hall-of-music-75th-anniversary-1940-2015/) — building history and exterior/construction images.
- [Purdue Archives, Elliott Hall of Music records](https://archives.lib.purdue.edu/repositories/2/resources/1467) — historic records and the 1940 dedication context.

**Decision:** round 11 improves upholstery color and preserves the round 10 portal repair. It remains **7.0/10**, below the 9/10 target because the exterior remains schematic and the interior circulation/stage arrangement is not sufficiently resolved.
