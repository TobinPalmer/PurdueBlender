# Independent review — Stanley Coulter Hall

**Asset reviewed:** `modular/buildings/stanley_coulter_hall.blend`  
**Review date:** 2026-10-23  
**Result:** **4.7/10 — does not meet 9/10**

## Evidence inspected

- Reopened-asset report and geometry checks: `final_verification.json`, `geometry_and_reopen_check.json`.
- Latest exterior, entrance, courtyard, west-side, footprint, and interior renders in this folder, including the `_final` and `_round2` images.
- Purdue College of Liberal Arts current exterior photograph: [Stanley Coulter Hall](https://www.cla.purdue.edu/academic/english/images/stanleycoulterhall.jpg).
- Purdue Archives undated historic photograph: [PPBUC01117](https://earchives.lib.purdue.edu/digital/collection/pbuildings/id/1310/) and [image](https://earchives.lib.purdue.edu/digital/iiif/pbuildings/1310/full/full/0/default.jpg).
- Google Maps satellite view at the building, checked 2026-10-23: [Stanley Coulter Hall](https://www.google.com/maps/place/Stanley+Coulter+Hall+(SC)/@40.4264038,-86.9143489,17z/). Aerial imagery shows the building in its campus block; the capture date is not displayed. I did not use the indoor panorama as evidence for exterior geometry.
- Purdue's 2025 renovation description: [restoring University Hall](https://stories.purdue.edu/restoring-purdues-university-hall-as-a-campus-crown-jewel/). It supports broad uses (graduate hub, English office, office and research-lab space), not room-by-room placement.

## Scorecard

| Category | Score | Evidence and reason |
|---|---:|---|
| GIS footprint and asset transform | 8.0/10 | FID 56, local asset root at zero with unit scale, and the recorded prior GIS AABB-extrema check under 0.004 m are consistent. This verifies the supplied structural envelope against the GIS ring's extrema; it does not independently validate the whole 3D building or height. |
| Exterior massing and silhouette | 4.0/10 | The saved model has a very broad, dark hipped roof and thick pale fascia/bands that dominate the facade. The current Purdue photo shows a much more restrained roof edge and differentiated upper facade. Historic Archives evidence also does not support the modeled broad roof profile. |
| Facade, openings, and entry | 4.0/10 | The render repeats three rows of narrow, identical dark windows with oversized white triangular caps and heavy continuous sills. The current photo instead shows grouped, wider windows, a distinct upper window band, a pale lower level, and varied opening proportions. Its entrance has a layered stone surround, slender round columns, recessed double doors, and an arched glazed transom. The model uses square supports and a flat, blocky entry composition, so the projection and details are not close enough. |
| Materials and texturing | 4.0/10 | Brick material reads consistently, but the large pale bands/caps are too bright and heavy, window glass reads nearly opaque, and the roof is a featureless dark plane. Materials lack the variation and finer stone/metal/glass response visible in the current reference. |
| Interior | 2.5/10 | Current saved inspection shows floors and shell objects, but the interior presentation render is nearly blank, and the separate furniture image reads as a sparse overhead diagram. No evidence supports exact current room locations. The official 2025 source only supports broad use categories; it cannot validate the modeled arrangement. This is not a finished or properly textured interior. |
| Source/evidence quality | 6.0/10 | The author distinguishes current exterior imagery, undated historic imagery, the 2022 plan set, and broad 2025 uses. The cited sources are appropriate but the screenshots do not demonstrate a reliable full-building facade survey or current interior layout. |
| Saved file and organization | 8.0/10 | Reopen verification succeeds; collection structure is understandable and comparison geometry is hidden. There are still 734 exported objects, including many small components, which makes visual QA harder but does not break the file. |

**Overall architecture quality: 4.7/10.** The independent score excludes GIS placement from the visual architecture aggregate; footprint integrity is recorded separately above. A high geometric placement score cannot compensate for the visibly inaccurate roof, facade, entry, materials, and incomplete interior.

## Specific corrections before another review

1. Rework the visible roof profile from image evidence. Reduce the roof's apparent depth/height and fascia mass; do not retain a broad roof plane solely because the height is unverified. Keep uncertain roof components hidden until a current source supports them.
2. Replace the repeated triangular window caps and broad continuous sill courses with facade details that match the current photo: grouped, wider glazing, a more substantial upper window band, and differentiated lower-level openings. Use the historic photograph only for elements it actually depicts.
3. Rebuild the east entrance from the current Purdue photo: inset double doors, visible arched transom, pale layered rectangular stone surround, slender round supports, correctly scaled landing/stairs, and legible rails. The present square columns and flat, bulky canopy are not supported by the cited photo.
4. Tune materials against the photo: less pure white stone, more natural stone variation, brick scale/joint contrast, less opaque glazing, and visible roof material variation. Remove visual noise and white caps that read as separate wedges.
5. Make the interior reviewable: render a true cutaway/isometric with visible floor plates, partitions, doors, stair/core, and furnished spaces. Use labels that state that rooms are schematic. Avoid presenting a blank field or an overhead furniture-only image as the interior.
6. Keep the root transform/manifest origin and the original GIS foundation fixed during visual corrections. After revisions, compare the whole foundation outline to the source ring, not only AABB extrema, and state that height remains unverified.

## Placement versus architecture

The asset-level root transform and reported GIS footprint audit are internally consistent. This does not validate master-file placement because the master was not reviewed here. The model is not ready for 9/10 acceptance or master integration as a finished visual asset. The master agent can preserve the current origin and footprint while holding this building out of the final integrated set until a revised pass receives a new independent review.
