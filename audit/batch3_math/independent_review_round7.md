# Independent review — Mathematical Sciences Building (MATH), round 7

**Review date:** 2026-10-24  
**Asset:** `modular/buildings/math_sciences.blend`  
**Rating:** **7.0/10**  
**Decision:** Continue revision; this is below the 9/10 completion bar.

I reviewed the round-seven reopen/GIS validation, the saved-file evidence and source notes, and the available exterior and interior renders. I did not edit the source asset, master blend, manifest, README, or shared status files. Round seven makes no model geometry changes, so the review treats the corrected sign and stronger footprint audit as validation/correction improvements rather than a new design pass.

## Scorecard

| Category | Score | Evidence and assessment |
|---|---:|---|
| Identity and placement | 8.0/10 | Purdue Archives supports the 10-story Mathematical Sciences identity. The asset retains `Asset_math_sciences` and its manifest origin. The round-seven shell bounding edges agree with the transformed GIS FID 227 bounding edges within 0.00434 m. This is a bounding-box check, not proof of a survey-grade polygon fit or master-scene placement. |
| Exterior massing and facade | 5.8/10 | The overall render communicates a tall brick tower, and the repeated window rhythm is legible on the east/south modeled elevations. The prior unsupported east lettering is now absent. Large featureless wall wings dominate parts of the east, north, and south views; the west view shows a stack of deep horizontal bays whose relationship to the documented land bridge is not established. The roof slab and penthouse remain visually prominent estimates. |
| Materials and texturing | 7.8/10 | Brick, pale surrounds, and blue-gray glazing read consistently and the prior corner artifacts/signage issue are improved. Rendered brick is still smooth at the overall scale; exact color, brick dimensions, window schedule, and north/west finish are not verified. No exterior image registers the detailed pattern to all elevations. |
| Interior and circulation | 6.0/10 | The third-floor cutaway contains study tables, group rooms, shelving, and labeled zones consistent with the documented use and plan context. It remains schematic: strong shadows, broad opaque surfaces, and disjoint-looking core/stair elements make circulation and adjacency hard to interpret. The source plan is from 2022 and furniture/partition positions are partly inferred. |
| Vertical form, roof, and height | 4.5/10 | Ten stories are supported, but the 33.2 m wall top, 42.9 m maximum, story intervals, mast, roof and penthouse profile remain estimates. The available GIS level-like fields have no published definitions or units, so they cannot resolve these dimensions. |
| Technical integrity and verification | 8.8/10 | The saved asset reopened with the expected collection, 550 direct/592 total objects, and the unwanted east sign absent. The GIS-envelope AABB comparison is close, and the previous ray checks recorded 81 clear sampled openings and six brick controls. These checks do not establish the true window schedule, facade accuracy, mesh quality throughout, or registration in the master file. |

## Findings

- **Fixed since the previous scored pass:** `MATH_Signage_East` is absent in the reopened saved asset and the east elevation no longer shows its gold lettering.
- **Useful validation added:** the updated check compares saved shell extents with the transformed GIS polygon bounds and corrects the direct-versus-total object-count distinction.
- **Main quality blockers:** large blank elevations, uncertain rooftop massing, and the unverified west-side horizontal bay/passage treatment keep the exterior from reading as a well-supported finished model.
- **Interior needs clearer presentation and structure:** furniture types are plausible, but the current cutaway does not convincingly show continuous circulation or the core-to-room connections.
- **Height remains an evidence gap:** no metric elevations or reliable roof measurements were supplied; story count alone cannot validate the modeled height or floor spacing.
- **Master placement was not rechecked in this round:** the standalone asset's manifest origin is unchanged, but this validation did not open the main blend and compare its placement marker.

## Recommended next revision

1. Find a source image/elevation that identifies which faces are east, west, north, and south; only add facade detail where a view or drawing supports it.
2. Revisit the large blank wings and roof/penthouse against oriented source material. Keep unsupported dimensions explicitly marked as estimates.
3. Clarify the interior cutaway by showing one coherent floor and readable core/circulation connections; avoid unrelated floating elements in the same camera view.
4. Reopen the master file and verify the linked asset's marker, rotation, and scale against its manifest entry before claiming placement is checked.
5. Keep the GIS bound comparison and sign-absence check as regression checks, but do not treat them as substitutes for visual/elevation evidence.

## Evidence inspected

- `audit/batch3_math/round7_validation.json`
- `audit/batch3_math/validate_round7.py`
- `audit/batch3_math/REVIEW.md`
- `audit/batch3_math/exterior_after.png`
- `audit/batch3_math/exterior_east_after.png`
- `audit/batch3_math/exterior_west_after.png`
- `audit/batch3_math/exterior_north_after.png`
- `audit/batch3_math/exterior_south_after.png`
- `audit/batch3_math/library_cutaway_round5.png`
- `audit/batch3_math/third_floor_core_after.png`
- `audit/batch3_math/geometry_checks.json`

**Verdict:** The saved-file sign correction and footprint-envelope verification are valid improvements, but round seven does not add the missing facade, roof/height, or interior evidence. Score **7.0/10**; continue revision.
