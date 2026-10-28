# Mackey Arena — independent second-pass visual review, r1

**Score: 5.10 / 10. Not accepted** (threshold 9.9, no lower threshold approved). Two gates fail: reference coverage, and unresolved material exterior discrepancies.

- Asset: `modular/buildings/mackey_arena.blend`. SHA-256 `0ee720103158d666f345f21adfc96aa6ef1f75cd1f6dde6617ff645edee31151`, checked before and after the review.
- Reviewer: an independent subagent that did not author r1. I opened the saved file headlessly in Blender 5.2.3 and never saved it.
- Evaluator: `evaluator.py`, which writes `result.json`. The score is the unrounded sum of itemized awards.

## How the review was done

- I opened every exterior source image directly. I made reviewer renders using the same Standard view transform, sun 2.6 and sky 0.45 as the modeler's set. These include views matched to the following sources:
  - `2016_02` (SW, ground level)
  - `drone_04` (SW, elevated)
  - `2016_01` (SE, ground level)
  - `drone_05` (E, elevated)
  - `hntb_Purdue-2` (Weist Plaza)
- I also rendered extra views: north oblique, north end of the east facade, SDAC lobby, west annex and a drum close-up.
- I made a top view registered to the 2023 orthophoto's local box (`renders/rv_top_overlay_blend.png`).
- Source-vs-model strips are in `comparisons/` and source crops are in `crops/`.
- I sampled colors (median sRGB + HSV) from matched photo and render regions (`color_compare.json`).
- I treated the modeler's coverage matrix, checklist and change log as claims to check, not as evidence.

## Criterion table

| Criterion | Max | Awarded | Main deductions |
| --- | ---: | ---: | --- |
| Windows/openings | 3.0 | **1.30** | • Drum slots are dark glass spanning ~80% of the drum height; photos show light louvres in the lower part of brick channels (−0.35)<br>• SE wing east face rhythm, corner bay and arcade (−0.30)<br>• East wing has 3 window tiers where the source shows 2 (−0.30)<br>• SDAC west facade has 3 tiers where the source shows 2 (−0.25)<br>• North entrance (−0.10)<br>• P towers (−0.10)<br>• Unseen elevations (−0.30) |
| Signature architecture | 2.5 | **1.30** | • East entrance front is flat; the source shows it curved, with different banner layout (−0.30)<br>• SDAC curved glass lobby missing (−0.25)<br>• Fascia corrugation (−0.10)<br>• Drum brick channels (−0.10)<br>• P-tower composition (−0.10)<br>• SE wing corner bay, canopy and inlays (−0.15)<br>• North entrance lettering and plaza monuments (−0.10)<br>• Coverage (−0.10) |
| Proportions/roof/silhouette | 2.0 | **1.20** | • Drum-to-concourse proportion and dome crown visibility (−0.50)<br>• Heights are estimates only (−0.10)<br>• North massing unverified (−0.15)<br>• Curved elements missing from the silhouette (−0.05) |
| Material/color/surface/depth | 1.5 | **0.80** | • Louvre color (−0.25)<br>• Fascia color and finish (−0.10)<br>• Dome value (−0.05)<br>• Ring roof value (−0.05)<br>• Brick value (−0.05)<br>• Missing recess and arcade depth (−0.15)<br>• P-tower materials (−0.05) |
| Whole-building consistency | 1.0 | **0.50** | • SW, SE, E and plaza matched views each differ (−0.40)<br>• No current N/NE/NW daylight match (−0.10) |
| **Total** | **10.0** | **5.10** | |

## What r1 gets right

- **Footprint and plan.** The registered top render overlays the 2023 orthophoto closely, covering:
  - the drum circle
  - the east/north wing outline, including the rounded north end and the concave west curve
  - the four penthouse boxes
  - the west annex
  - the south block

  This is a large improvement over r0 (`renders/rv_top_overlay_blend.png`).
- **Dome.** The dome is ribbed and copper-tan with concentric seam rings and a small central cap. The dome hue (28–30°) matches the photos (18–31°).
- **Drum.** The brick drum has 24 limestone pilasters and a 2-slotted : 1-plain bay rhythm, as in `2016_02` and `drone_04`. Drum brick (164,128,103) is close to the photo (173,133,99), and limestone (207,200,182) is close to (224,212,188).
- **Entrances.** Both the SW and east entrances exist with the correct 2025 signage text. The concourse ring has a water table, two limestone stripes and coping.
- **Technical gates.** Reopen, collection, portability and footprint/orientation/scale are clean.

## Color check (photo vs render, median sRGB / hue / S / V)

| Material | Photo | Model render | Verdict |
| --- | --- | --- | --- |
| Drum brick | 173,133,99 / 28° / .43 / .68 (`2016_02`) | 164,128,103 / 25° / .37 / .64 | OK |
| Concourse brick | 197,157,122 / .77 | 164,130,103 / .64 | Slightly dark |
| Wing brick | 214,178,149 / .84 (sunlit `2016_01`) | 148,112,89 / .58 | Dark; partly lighting |
| Limestone | 224,212,188 | 207,200,182 | OK |
| Fascia | 188,158,112 / S .40 | 182,159,131 / S .28 | Too grey; smooth instead of corrugated |
| Dome | 217,195,172 V .85 (sun); 201,173,161 V .79 (overcast) | 177,160,144 V .69 | Hue OK; somewhat dark |
| Drum slot infill | **150,146,132 light warm-grey louvres** | **41,47,52 near-black glass** | **Mismatch** |
| Ring roof | 167,162,154 V .65 (ortho) | 96,101,103 V .40 | Too dark |
| Wing roof | 226,226,236 | 223,228,236 | OK |
| Signage | Black banners, white text, gold P | Same | OK |

## Key proportion finding

The model's drum is too tall for its concourse ring. I measured this as ratios between features, so it does not depend on absolute heights:

| Ratio | Photo | Matched model render |
| --- | ---: | ---: |
| Visible drum (concourse roof to fascia underside) : concourse wall, `drone_04` | ≈1.2 | ≈2.1 |
| Same ratio from the ground, `2016_02` | ≈0.8 | ≈1.6 |
| Drum height : 15° bay chord | ≈0.79–0.80 | ≈0.96 |

- In `2016_02` the dome crown rises clearly above the fascia. From the matched model position it is completely hidden.
- See `comparisons/cmp_SW_drone04.jpg` and `comparisons/cmp_SW_ground_2016_02.jpg`.
- The likely fix is a taller concourse ring and/or a shorter drum, with the fascia and dome rise re-derived.

## Prioritized corrections for the next revision

1. **Drum, concourse and dome proportions.** Re-derive the drum, concourse, fascia and dome heights. Lower the drum top and/or raise the concourse ring until:
   - visible drum ≈ 1.2× the concourse wall in the `drone_04` matched view
   - drum height ≈ 0.8× the 15° bay chord
   - the dome crown shows above the fascia from the `2016_02` position
2. **Drum slot groups.** Replace the dark glazed slits with light warm-grey louvre panels (≈150,146,132). Confine them to the lower ~55–65% of each slotted bay, inside full-height recessed vertical brick channels.
3. **East entrance.** Make the front above the 3-bay portal a convex curve. Make the 44 and 59 banners large separate panels on projecting piers, with captions. Add the vertical MACKEY ARENA / KEADY COURT blade banners.
4. **East wing between the P towers and north of the third P.** Use two tiers:
   - a recessed ground-floor storefront arcade between brick piers with limestone bases
   - one row of paired/single upper windows with limestone heads and sills
   - a blank banded parapet above

   Remove the third tier.
5. **SDAC west facade.** Use storefront plus one tier of tall upper windows (wide gridded units alternating with narrow pairs). Remove the extra row.
6. **SDAC SW corner.** Model the convex two-storey curved curtain-wall lobby with its mullion grid and metal fascia.
7. **SE wing.** Add:
   - the glazed corner bay with grey metal surround on both floors at the tip
   - 4 aligned narrow slit windows per floor
   - the projecting second-floor canopy over a recessed ground-floor arcade
   - limestone accent inlays in the attic band
8. **Fascia.** Make it vertically corrugated and shift the color toward the sampled golden bronze (188,158,112).
9. **P towers and penthouses.** Mount the P on a grey horizontal-louvre metal band, with glazing above and below and a storefront base. Use metal-panel cladding on the penthouses.
10. **Coverage and north side.** Get current daylight photos of:
    - the north elevation and rounded north end
    - the north half of the east facade
    - the west annex facades
    - the drum's north/east bays

    Add MACKEY ARENA lettering and a full-height storefront at the north entrance.
11. **Colors.** Lighten the concourse ring roof toward (167,162,154). Raise the dome and brick values slightly toward the sunlit samples while keeping their hue.
12. **Manifest (coordinator).** After acceptance, update the `modular/manifest.json` object list, `object_count` (still 391 from r0) and bounds for the new asset.

## Gates

| Gate | Result | Reason |
| --- | --- | --- |
| Correct identity | PASS | Matches the Mackey photos and the 2023 orthophoto. Brees Center and Lambert Fieldhouse are excluded. |
| Adequate exterior-reference coverage | **FAIL** | No current daylight source for the north elevation, rounded north end, north half of the east facade, west annex or drum N/E bays. |
| No unresolved material exterior discrepancies | **FAIL** | Drum proportions, drum louvres, flat east entrance front, missing SDAC curved lobby, tier counts, SE wing. |
| Saved-file reopen | PASS | Exact file opened headlessly with the hash verified; 311 objects load; not saved. |
| Expected collection/export | PASS | `Asset_mackey_arena` holds all objects; `AssetRoot_mackey_arena` sits at the origin with identity transform. The manifest object list is stale (coordinator note). |
| Portable dependencies | PASS | No libraries, images, text blocks or absolute paths. |
| No regression to footprint/orientation/scale | PASS | Placement origin and local frame are unchanged, and the outline matches the orthophoto better than r0. |

## Uncertainties

- The Commons camera positions and the panorama projections of `2016_01`/`2016_02` are approximate. That is why the proportion finding uses feature ratios from several sources rather than absolute heights.
- The color sources mix lighting: sunlit 2016 photos, overcast or dusk 2025 drone shots, and the 2023 orthophoto. I deducted lightly for value differences of about 0.1.
- The east entrance changed between 2016 (curved glass bay) and 2025 (banner wall). Both versions are curved.
- I don't know whether the SDAC's tall upper windows span two floors inside. From outside they read as a single tier.

## Files in `review_r01/`

- `evaluator.py` and `result.json`
- `review.md` (this file)
- `color_compare.json`
- Reviewer renders in `renders/` and `renders2/`, with their camera JSON and render settings
- `comparisons/` (source vs model) and `crops/` (source crops)
- `reviewer_inspect.py`, `reviewer_inspect_output.json` and `reviewer_render.py`

Nothing outside this folder was modified, and the asset was never saved.
