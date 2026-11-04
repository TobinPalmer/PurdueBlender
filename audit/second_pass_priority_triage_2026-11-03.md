# Second-pass priority triage — November 3, 2026

Read-only triage by independent agent `priority_eval`. Scope: Bell Tower rank 3 and Wetherill rank 4, after Mechanical Engineering rank 2. WALC remains user-handled. The user has now requested modeling toward 9.5/10. That numerical target does not waive the independent visual rubric, evidence-coverage or saved-file gates. Neither asset receives a new numerical grade or acceptance from this triage.

## Recommendation

Continue Mechanical Engineering first, then Bell Tower, then Wetherill, preserving the README order. Wetherill has the larger visible architectural deficit; Bell Tower is simpler, already has its basic defining structure, and offers a smaller next upgrade. Both need real revision plus fresh matched renders and a separate exact-asset evaluator before a 9.5 claim. Do not carry forward old technical first-pass scores as second-pass visual scores.

| Priority | Asset and builder | Severity / evidence readiness |
| --- | --- | --- |
| 3 Bell Tower | `modular/buildings/bell_tower.blend`; canonical `modular/buildings/build_bell_tower.py`; legacy work `modular/bell_tower_work/` | Moderate visible detail/proportion risk; strong upper-tower/roof/bell references, incomplete lower four-face survey and registered bell layout. |
| 4 Wetherill | `modular/buildings/wetherill_laboratory_of_chemistry.blend`; existing dedicated builder `audit/wetherill_lab/build_wetherill_detailed.py` (no canonical `modular/buildings/build_wetherill_laboratory_of_chemistry.py` found) | High: defining south composition, pane divisions, relief sequence and generic other elevations/roof. Stronger research than current implementation, but incomplete recent west/rear/roof counts. |

## Saved assets inspected

Both files successfully reopened read-only in fresh Blender 5.2.3 background processes. No source model, master, manifest, geometry or live Blender state was modified. Current hashes:

- Bell Tower: `a99f1a20f53cc132cc33c3a376ed17c55762ca0928e5f12ccf0455af6c7c2c81`; 578 objects in `Asset_bell_tower`, 581 scene objects including preview collection.
- Wetherill: `e94d053c69ce3ca462e0bbee0f44f8c395c39e880964c72c9b8425ef847790c7`; 362 objects in `Asset_wetherill_laboratory_of_chemistry`, 371 scene objects; no linked libraries. Saved chemistry field text and positions inspected directly.

Existing renders were inspected, but were not regenerated or proven hash-matched. Consequently the observations below combine current saved-file structure, builder inspection, prior renders and references and are actionable triage, not a formal review of fresh matched views.

## Bell Tower

Read `research/second_pass/buildings/bell_tower/README.md`, `audit/bell_tower_independent_grade/result.json`, and the canonical builder. Compared existing `audit/bell_tower_independent_grade/overview.png` with the inspected high-resolution `research/second_pass/buildings/bell_tower/sources/commons_2024.jpg` (A Hazy, June 23, 2024, CC BY-SA 4.0).

The old 9.3 result uses five two-point technical criteria. Much of its award comes from tracing GIS and equaling the published 160 ft number. It is not a 9.3 second-pass exterior score. Its missing-canonical-builder finding is also obsolete: the canonical builder exists now.

Next corrections/checks:

1. Generate matched upper-tower views. The 2024 image shows substantial panel joints, deep stepped cornice, square posts with distinct blocks/capitals and overlapping rails; the old overview is too small to verify their proportions and some members look much thinner. Verify arch span/spring, post thickness and the height relationships between clock enclosure, chamber and roof before changing them.
2. Preserve the open chamber, four nonidentical bells and hollow mouths, and refine shoulder rings/raised inscription bands and suspension heads using `sources/alumnus_four_bells.jpg`. The existing builder includes unequal profiled bells and clappers, so this is a detailed comparison rather than a request to add nonexistent missing bells. Obtain an opposite bearing to locate the suspension frame in plan; one image-relative layout cannot support all sides.
3. Verify dark reddish-brown roof field, bright raised seams, stepped finial and pale eave against the 2024 source. The current material is very dark neutral gray; match in neutral daylight and close view before selecting new color. Do not infer alloy from color.
4. Compare `sources/purdue_base_arch.webp` with fresh passage close-ups. Real base includes tapered dark-gray rough plinths, masonry courses, stepped pale caps, joints and deep arch soffits. The canonical builder starts with plain pale cuboid feet/piers and applied caps; the source calls for actual surface/profile transitions. Hidden access/lighting faces remain unverified.
5. Count full shaft belts/recesses with unobstructed references; do not assume four identical faces. Keep current footprint/orientation. Reconcile 160 versus 165 ft published height with reliable dimensions; copied numeric agreement alone is not height verification.

Evidence needed for 9.5 support: four-face base/access/lighting sequence, opposite-side bell/hanger view, registered complete belt/recess count, and measured or well-constrained vertical landmarks. Available LiDAR is sparse unclassified 2018 returns and cannot measure dials/arches/finial precisely. The research dossier records these limitations honestly.

## Wetherill

Read the research dossier and its source-linked schedules, old `audit/wetherill_lab/independent_review.md`, current builder, and actual saved text fields. Compared `audit/wetherill_lab/entrance_detail.png` with the high-resolution `research/second_pass/buildings/wetherill_laboratory_of_chemistry/sources/purdue_front.jpg`.

The old review mixes interiors with exterior scores and is not the current second-pass rubric. Its buried-label finding should not be blindly reapplied: current builder offsets labels/relief farther outward and the existing render shows labels. The major current defect is the incorrect composition and sequence, not merely hiding text.

Next corrections/checks:

1. Replace the generic five-story uniform grid with source-specific vertical/bay schedules. Builder currently uses `range(5)`, one 1.78 m window family, `int(L/4.25)` bay count and a two-column/three-row pane pattern on every perimeter edge. The actual front has much taller divided windows and four narrow pane columns in clear central samples; attic windows are shorter. Rear service windows/infill/louvers deliberately differ. Saved research describes the north drive-under and seven-item ground run. Those cannot be produced by the current perimeter loop.
2. Rebuild the signature south pilasters/frieze/reliefs against the full front and close Optics source. Existing render locates low, thin relief/label boxes and bulky horizontal bands in a simplified entrance frame. Actual six projecting Ionic pilasters, scroll capitals, tall five relief/window bays and main building-name frieze extend through a much larger vertical composition. Keep three rectangular deep entry recesses, actual carved overdoors and low barred flank openings.
3. Correct chemistry field order from the actual south-facing view: ANALYTICAL, BIOLOGICAL, INORGANIC, ORGANIC, PHYSICAL left to right. Fresh saved data puts BIOLOGICAL at x=-5.3998, PHYSICAL at -2.6998, INORGANIC at 0, ORGANIC at +2.7000, ANALYTICAL at +5.4000, matching the old render's wrong visual order. Motifs must move with their correct fields and have source-backed relief rather than arbitrary geometric substitutes. Reconcile local edge direction explicitly before assigning labels.
4. Add actual named scientist fields and detailed dark sash/reveals, current AC exceptions, greenish cornice with underside blocks, pale stone joints/profiles and red-brown brick at correct physical scale. The old render has pale frame-heavy, squat windows and pinkish wall color compared with the source; tune lighting and materials together, without baking exposure differences into arbitrary surface colors.
5. Segment the roof into the observed pitched perimeter and inset/service zones. The current builder uses one flat slab at z15.95 and edge cornice at16.05 plus a small plant cluster, while research aerial describes red/brown pitched perimeter sections and extensive irregular service fields. Resolve current roof equipment before claiming exact placement.
6. Preserve Wetherill/Brown asset boundary and glazed links. Do not assign Brown's wall to Wetherill to fill a hidden elevation, and do not spend this exterior iteration adding interior Commons content for visual points.

Evidence needed for 9.5 support: a complete recent west frontal bay sequence; current rear/east face counts and lower connector geometry; roof updates and sections; dimensioned or otherwise constrained facade/roof vertical levels. Existing 2017 rear, 2019 east, 2022 front and 2006 plan must be reconciled to one intended condition. Useful sources already saved include separate north-service, northwest, northeast and southeast viewpoints, high-resolution south, Optics close-up and overhead. This supports substantial immediate correction, but does not certify unseen/current details.

## Next review contract

For each revised building, preserve before/after renders, exact SHA-256, all elevations, roof, opposing obliques and signature close-ups under its building-specific second-pass audit. Have a reviewer who did not author that geometry compare sources directly and run the weighted exterior evaluator (3 opening, 2.5 signature architecture, 2 silhouette, 1.5 materials/depth, 1 whole-building consistency). Use 9.5 as the user-authorized threshold, retain uncertainty deductions and all independent gates. Master integration remains a separate Tobin-owned step.
