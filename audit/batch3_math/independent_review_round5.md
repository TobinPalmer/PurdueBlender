# Independent review — Mathematical Sciences Building, round 5

**Review date:** 2026-10-23  
**Asset reviewed:** `modular/buildings/math_sciences.blend`  
**Rating:** **6.9/10** (round 4: 7.1/10)  
**Recommendation:** Continue revision; round 5 does not meet the 9/10 completion threshold.

I independently reopened the saved blend in Blender 5.2.3, inspected the round-five overall and orthographic renders, the close facade detail, both the round-four plan view and round-five cutaway, and the saved-file checks and builder code. I did not edit the asset or builder scripts.

## Scorecard

| Area | Score | Assessment |
|---|---:|---|
| Identity, registration, footprint | 8.0 | The asset opens and retains `Asset_math_sciences` (551 direct objects, 593 with children). The GIS envelope remains at the local origin with the previously documented dimensions. The round-five checks do not themselves compare the footprint against the source polygon, so the earlier GIS edge comparison remains the evidence for fit. |
| Exterior massing and facade | 5.6 | The east and south elevations are recognizable and repeated window rhythm is clear. The east-facade lettering was not removed: the saved file still contains the visible `MATH_Signage_East` object, and the overall view retains gold marks at the lower window line. Large blank wall wings and an oversized, unverified rooftop slab/penthouse still dominate. Passage geometry is absent, which is appropriate given the evidence does not locate it. |
| Materials and texturing | 7.9 | The facade close-up reads as brick courses and mortar. The previous dark square corner artifacts around the pale reveals are no longer apparent; reveal joints look substantially cleaner. Brick scale/color, exact surround details, and glazing schedule remain estimates, and the overall view still has a pale/pink appearance. |
| Third-floor interior | 6.2 | `library_cutaway_round5.png` removes much of the shell/ceiling occlusion and is cleaner than the round-four interior, but broad opaque shapes and overlapping central furniture still obscure the layout. The intended zone labels are not legible in the cutaway. Room/furniture geometry remains schematic and exact current layout is not supported by the older plan/photo. |
| Upper floors and vertical form | 4.5 | Ten-story identity is supported, but the 33.2 m envelope, 42.9 m maximum, floor intervals, upper slabs and rooftop profile remain estimated. Large elevations without source evidence remain visibly unresolved. |
| Saved-file and geometry checks | 8.5 | I reopened the saved blend independently. The logged check reports all 81 chosen window-center rays clear and all six brick control rays hit brick. These samples do not validate actual-world window spacing, reveal seating, full footprint accuracy, or the passage. |

## Round-four blocker audit

1. **East lettering — not fixed.** The saved asset still has `MATH_Signage_East`, text `MATHEMATICAL SCIENCES BUILDING`, at `(17.5, -3.8, 4.65)` with dimensions approximately `(6.03, 0.252, 0.08)` m and `hide_render=False`. `finish_math.py` line 511 contains the purported removal statement as literal `\\n` sequences on a line whose first character is a comment marker, so Python treats the entire statement as a comment. The sign remains in the rendered facade area. Remove the object with executable code, rebuild, reopen and confirm it is absent before claiming correction.
2. **Dark surround marks — substantially fixed.** The round-five `brick_detail_after.png` no longer shows the previous dark corner blocks. The pale reveal bars now meet cleanly. Thin dark glazing/mullion edges remain, but I did not find the earlier block artifacts in this render.
3. **Passage — not modeled, appropriately qualified.** Purdue's admissions tour text refers to the land bridge under MATH, establishing its existence but not which elevation, dimensions, or support arrangement. No passage appears in the reviewed renders. Do not place or claim a modeled passage until a view or plan establishes its bearing/location.
4. **Interior readability — partly improved.** The new dedicated cutaway is less occluded than the round-four render, but opaque white/gray surfaces and clustered furniture continue to compete with the room boundaries. Zone labels do not read in the final image, and the view remains a schematic illustration rather than a verifiable as-built layout.

## Other unresolved evidence and quality issues

- The north and west elevations and large wall wings lack source-supported facade detail. Do not fill in windows or architectural features from guesswork.
- Roof and penthouse geometry remain estimated and visually prominent. The source record supports a 10-story identity, not the model's metric heights, floor spacing, or roof outline.
- The available third-floor plan is dated 2022. The 2025 library source supports use, finish/furniture types, group study and a windowless testing room, not current exact partitions, room positions, counts or furniture placement.
- The 81-window check proves that the modeled wall panels have openings at the sampled points, not that all 81 correspond to real windows. The six wall controls are limited spot checks.
- The round-five status text says lettering removal was completed, but the saved asset contradicts that claim. Correct the model and status note together.

## Evidence inspected

- `exterior_after.png`, `exterior_east_after.png`, `exterior_north_after.png`, `exterior_south_after.png`, `exterior_west_after.png`
- `brick_detail_after.png`, `library_cutaway_round5.png`, `library_after.png`, `library_plan_round4.png`, `library_plan_diagram.png`, `third_floor_core_after.png`
- `geometry_checks_round5.log`, `render_round5_jointfix.log`, `build_round5_jointfix.log`, `independent_review_round4.md`, `independent_review_round4_scorecard.json`
- `REVIEW.md`, `SCORE_NOTE.md`, `changes.json`, `finish_math.py`, `render_library_round5.py`
- Purdue admissions tour listing (land-bridge existence, no location/dimensions): https://ontour.admissions.purdue.edu/daily-visits/
- Purdue Trustees 2022 MATH third-floor renovation plan: https://www.purdue.edu/bot/meetings/past-meetings/2022/09.%20oct/pfc/Libraries%20Study%20Space%20Reno.pdf
- Purdue Statistics exterior photograph: https://www.stat.purdue.edu/images/about/Math-Bldg-.jpg

**Verdict:** The surround-joint cleanup is visible and the new interior camera selection reduces shell occlusion. The most direct round-four exterior blocker, the gold lettering, remains in the saved blend because the round-five removal code is commented out. Roof, heights, blank elevations, and interior as-built layout remain unsupported. The asset scores **6.9/10** and should remain in revision.
