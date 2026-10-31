# Haas front composition audit for r05

Independent source audit, 2026-10-31. **No r05 score or acceptance is assigned.** This is construction advice before a stable saved r05 revision and user opening, not an exact-file review. The previous r04 review remains historical. The default 9.9 acceptance threshold and exterior rubric are unchanged.

Only this `reference_audit/` folder was written. No builder, geometry, asset, master, placement or shared index was changed.

## Evidence and method

Primary: `../../sources/user_front_detail_2026-10-28.png`, 496×403, user-supplied real photograph; capture date, photographer, camera, focal length and dimensions unknown. Corroboration: Purdue Events front photograph and saved Google Street View west-entry/upper-wall photographs, April 2026. Source provenance is in `../../sources/reference_index.json`. Baseline comparison: `../../detail_color_r04/renders/front_detail.png`, with r04 geometry schedule inspected to identify the mechanism of the mismatch. Baseline asset hash supplied by coordinator: `7c608ff383548bfb2159fba7734d4cf461813f06ab024117a7d3201d4ba045fb`.

Derived enlargements in this folder preserve the source pixels and are **not new independent views or enhanced source detail**. `source_and_crop_manifest.json` records original hashes, crop bounds and resampling. Native pixels constrain all precision below. Positions and ratios are visual estimates, not measured elevations or recommended surveyed dimensions. Perspective has not been calibrated or metrically rectified.

## Primary correction: material regions, not just brick color

The front is predominantly pale stone. R04's broad stepped brick fields behind each upper window and lower arch are a materially wrong composition. Its generator makes three brick polygons approximately 5.02–5.30 m wide, repeated in two vertical registers (3.24–6.82 m and 7.18–10.75 m), then subtracts them from the stone cladding. This creates three large red rectangles and a uniform pale mid-band. The photo establishes a different pattern:

1. **Upper windows sit in pale stone surrounds/fields**, with small isolated brick tablets to either side. They do not sit inside large rectangular red panels. The red tablets are approximately square in the architectural plane, although the oblique photo compresses their horizontal dimension. Their observed width is roughly 0.20–0.28 of the adjacent visible upper glazing width; exact metric size remains estimated.
2. **A shallow brick spandrel lies below each flanking upper-window sill and above its lower arch.** It is bordered by projecting pale sill molding above and the pale arched surround/key below. Shape it around the arch rather than making a full-height red background. The central bay instead has a pale carved frieze/inscription panel above the portal.
3. **Two narrow, long brick strips flank each of the three lower opening bays: six strips across the front.** Their inner edges are separated from the actual openings by substantial pale jamb strips. They continue from just below the upper-window sill zone almost to the lower sill/basement belt, rather than being severed by the r04 full-width mid-band.
4. **The brick strips have alternating broad rectangular blocks and narrower stems**, with a broader cap/foot. The pattern is quoin-like, not a fine sawtooth and not an eight-step boundary around one large rectangle. Both edges change width; do not merely notch the outside edge of an oversized brick field. Exact native pixel detail supports a small number of coarse blocks; it does not establish a surveyed course-by-course count.
5. **The broad pale piers between adjacent bays remain broad and continuous.** The lanterns mount on these stone fields, not on red brick. The upper relief panels sit on the pale piers. Small brick pockets are also visible under the eaves between stone/bracket divisions; do not turn those into a continuous red band.

For the clear right lower bay, a strip's visible width is approximately **0.18–0.28 times the local arched glazing width**. The pale interval between the inner brick-strip edge and glazing is about **0.24–0.35 times that glazing width**, including jamb/frame/reveal. These ranges are useful for relative composition and should be checked in a matched perspective. They are not direct metre conversions. The stepped strips' overall span is taller than the flanking arch itself, starting near the upper sill and ending a little above the basement belt.

Keep this pattern specific to the front. Real west/side photographs corroborate broad red brick wall fields, narrow middle openings, projecting brick piers and pale basement/upper surrounds. Applying the pale front treatment to those elevations would introduce a new error.

## Bands, stone profiles and opening proportions

The upper sill has a **layered projecting molding**, with several distinct horizontal steps and small terminal/support blocks. The upper-window heads join a stepped pale cornice/stone network. Thin unrelated bars and a single rectangular window outline lose this profile. At the lower belt the photo shows a projecting main cap and finer subordinate line; retain their separate depths.

R04's uniform white strip between 6.82 and 7.18 m is not a valid front-wide material separator. At that height, the flanking bays and the carved central frieze have different boundaries. The lower vertical brick strips must remain continuous past that level.

Do not derive a definitive new window aspect from the unrectified photograph alone. In the right upper opening, approximate native-image aperture corners are `(322,61), (402,43), (402,90), (323,104)`. The apparent group width is about 78–80 px and local vertical height 43–47 px, yielding about **1.7–1.9 before horizontal foreshortening**. Therefore a claimed measured aspect of 1.5–1.6 is unsupported. Three columns and two rows are well established; panes are approximately square/slightly oblong, with a near-mid-height horizontal sash. Their visible proportions also depend on frame/reveal thickness.

The same right bay suggests visible upper glazing about **1.15–1.22 times the lower arch's visible glazing width** (about 78–80 px versus 65–68 px). R04 uses equal 3.55 m hole widths and similar offsets. Check whether the upper aperture should be wider, the lower stone/reveal/frame should be thicker, or both, rather than changing only heights. This ratio is medium confidence because aperture edges are only a few pixels wide and the lower reveal is deeper.

At a local vertical near the right bay center, approximate source levels are: eave underside `y≈31–35`, upper aperture `y≈52–99`, lower arch glazing crown `y≈144`, lower sill `y≈226–230`, basement belt `y≈232`. The upper height is around 0.23 of eave-to-belt height and lower arch height around 0.41. These rough same-bay ratios are close to r04's `1.85/8.31≈0.223` and `3.45/8.31≈0.415`. They **do not establish a need** to increase heights to 2.35 m and 3.95 m. Fix material regions and profiles first, then compare a perspective from the source's low oblique angle. Orthographic render proportions should not be judged as though the photo were an orthographic elevation.

The lower flank arches are shallow segmental arches with substantial molding and a projecting crown key. Keep the crown, springing points, sill and jamb width separate. The red spandrel must meet the *outside* stone profile; it must not run behind a thin arch floating over a huge red panel.

## Portal and entry details

`portal_detail_8x.png` clearly shows deep fluted/reeded jambs, layered carved capitals/entablature and a dark recessed soffit. The portal's geometry is richer than several concentric plain arch bands. The pale frieze above contains real incised/relief work and lettering; reproduce supported relief depth/shapes, and do not invent readable text from blurred pixels.

There is a **tall dark timber/glazed transom above the low oak door leaf**, well inside the portal. R04's solid pale infill above the door materially changes the dark/solid balance and should be replaced by the supported recessed composition. The small glazed lights in the leaf appear to be **three narrow vertical lights**, rather than r04's two broad ones, but this is medium confidence at native resolution. Seek corroboration before treating the fine pane count as verified. The transom divisions are also not sufficiently resolved for exact reconstruction.

The front stair handrail in the supplied photograph is a **close pair offset to the left of the central stair run**, leading toward the door's left side. R04's two widely separated outer rails do not reproduce that placement. The solid cheeks, cap profiles and end piers should follow the photographed stair outline; do not add campus-wide landscaping or site features to disguise the entry.

## Suggested comparison sequence for the builder

1. Replace broad front brick fields with the six continuous narrow stepped strips, isolated upper tablets and shallow flank spandrels; retain the verified local footprint and front plane.
2. Rebuild linked sill/head/stone profiles and the bay-specific central frieze. Compare material masks in a frontal view before tuning color.
3. Add the deep dark portal/transom and correct the stair-rail placement. Keep unresolved fine ornament/pane divisions explicit.
4. Render a low oblique perspective matching the supplied photo, then adjust relative widths/heights only where that comparison supports them. Render the existing all-face/roof/detail set to detect regressions.
5. After the exact saved revision is opened for the user, submit its hash and renders for independent r05 review. No score is implied by adopting these recommendations.

Previously recorded rear-entry, roof-tile and coverage findings remain applicable unless the new revision resolves them. This front audit does not silently verify unseen south/return elevations or change any acceptance gate.
