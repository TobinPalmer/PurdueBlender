# Rawls Hall independent review — round 4

## Result

**Independent rating: 6.6/10.** The north elevation now has real masonry openings, pane centers are visible in the façade render, and the bronze window-sized blockers are replaced by narrow perimeter bars. The north panes read as blue-gray reflective glazing under the supplied lighting. The material is still nearly opaque, and the improvement is limited to the north elevation: the saved south-facing brick/glazing closeup still shows flat, brown-gray window panels. Interior circulation, exact upper-floor layout, and survey placement remain weakly evidenced.

| Category | Score | Review |
|---|---:|---|
| Exterior form and detail | 7.2/10 | Massing, entrance, floor bands, curved end bay, rooftop skylight, and the repeated window rhythm are clear. The reconstructed north openings have brick returns and slim frames. Other elevations still contain flat-looking window panels, and the overall model remains a simplified representation. |
| Materials and texturing | 6.7/10 | The north closeup shows blue-gray panes with broad light reflections; they read as coated glass at a glance. Saved material values are base color (0.08, 0.24, 0.38), roughness 0.14, metallic 0.20, and transmission 0.03, so there is little actual see-through behavior. The brick scale looks plausible at close range, but the mortar is bright and graphic. The south-side `brick_glazing_closeup_round4.png` still shows opaque brown-gray panels. |
| Interior completeness | 5.8/10 | The 1086 classroom has a coherent desk/chair layout and the top-down first-floor cutaway communicates broad plan organization. The core detail render is too faint to audit, and the atrium section shows columns and floor bands without legible circulation, stairs, or bridges. Upper floors and current room finishes remain unverified. |
| Technical integrity and placement | 7.5/10 | Reopened `modular/buildings/rawls_hall.blend` in Blender 5.2.3. The asset has 722 collection objects / 714 meshes, no missing image dependencies, and an identity unparented root. The rebuilt wall has 730 faces; the north glass has 60 quads and the frame mesh 1,440 faces. All nine saved sample rays hit north glass first, then continue to interior plan geometry or the opposite shell. GIS registration is still approximate. |
| Evidence and source fit | 6.4/10 | The 2024 Purdue first-floor plan supports the broad plan layout. The historical atrium image supports its general multilevel character, not exact present-day circulation or finishes. The Google Maps access note has no saved facade screenshot or exposed satellite capture date, so it is not reproducible current-condition evidence. The Plan1086 edge remains unresolved within the stated 1–2 m registration uncertainty. |

Weighted using the prior review formula (exterior 30%, materials 20%, interior 30%, technical 10%, evidence 10%): **6.63/10, rounded to 6.6/10**.

## North openings and glazing

`north_aperture_after_rebuild.png`, `north_glazing_closeup_round4.png`, and `north_glazing_oblique_round4.png` show blue panes at the window centers, with dark bronze perimeter strips and brick reveal depth. The ray evidence independently supports the geometry: each of nine rays intersects `RAWL_North_Windows_Glass` before reaching interior plan objects or the far shell. Thus the pane centers are exposed through the outer wall and have an unobstructed path into the modeled interior at those sample points. At the higher sample points, the next surface is the opposite building skin rather than a furnished interior, so this does not demonstrate a finished room behind every window.

The surface looks reflective because the closeup lighting produces broad highlights, but the saved transmission weight is only 0.03 and alpha is 1. The view does not show clear interior depth through the panes. I would describe it as convincing tinted, reflective glazing from the façade view, with transparency still unproven. The front and oblique closeups are stronger evidence than the standard exterior, where panes are small.

The saved `brick_glazing_closeup_round4.png` uses a camera at negative Y and still shows flat brown-gray window panels on that elevation. The round 4 glazing improvement is therefore north-side-specific; the handoff statement that the facade closeups show blue-gray glazing overstates what this image demonstrates. The brown-gray panels in `brick_course_detail_round4.png` have the same limitation.

## Materials, interiors, and placement

Brick courses appear consistently scaled across the north openings and corners; the recorded 0.215 m brick width and 0.075 m course height are plausible. The close material view makes the light mortar prominent and repetitive, so reducing its contrast would help the wall read more naturally. The apertures are a meaningful geometry improvement: the ray tests and frontal view are consistent with actual openings through the north wall, not just a new pane color.

The first-floor cutaway remains the clearest interior evidence. It broadly follows the saved Purdue plan but is not a close, source-overlaid core audit. The core-only view is nearly empty, while the atrium section is legible as a four-level structural void but not as a circulation space. Existing notes appropriately avoid inventing unsupported upper-floor partitions or stair locations.

The saved evidence reports 1–2 m horizontal GIS registration uncertainty. The 1086 wall still reaches 2.10 m beyond the approximate shell at a bounding-box corner, with centroid 1.27 m outside. Without survey control or a dimensioned plan-to-map tie, this remains unresolved rather than a confirmed modeling error. The Google Maps observation is only a written access record and cannot be reproduced from a saved facade capture.

## Prioritized fixes

1. Apply the aperture and perimeter-frame check to the remaining elevations. At minimum, revise the south-side flat panels shown in `brick_glazing_closeup_round4.png` so the material reads consistently across the building.
2. Improve pane transmission/reflection balance and show an interior behind representative windows. Keep the north ray test as geometric evidence; add a lit room-facing view to verify what is visible through the glazing.
3. Make the core plan view auditable with the source plan in the same orientation and clearer wall/door contrast. Improve the atrium section only where source evidence supports added circulation detail.
4. Reduce the bright mortar contrast while preserving the plausible brick/course scale.
5. Resolve the Plan1086 edge and overall registration only when a dimensioned control or better map reference is available; preserve the current uncertainty in the asset notes.

This round does **not** support a 9/10 rating. It verifies a substantial north-window geometry repair and improved appearance, while leaving other elevations, interior completeness, glass transparency, and GIS fit below that bar.
