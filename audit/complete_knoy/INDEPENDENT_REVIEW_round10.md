# Knoy Hall — independent full-building review, round 10

**Grade: 7.8/10 — below the 8/10 acceptance threshold.** I reviewed the current R10 asset, its R10 evidence and reopen validation, available facade/interior renders, and the earlier evidence records. This is a new full-building review; the prior score was not carried forward as a grade. No geometry or project files were changed for this review.

| Category | Score |
| --- | ---: |
| Identity, GIS footprint, and campus placement | 1.8/2 |
| Floors, height, and roof evidence | 1.2/2 |
| Exterior, facade materials, and entrance | 1.6/2 |
| Interior plan and circulation | 1.3/2 |
| Technical integrity and evidence quality | 1.9/2 |
| **Total** | **7.8/10** |

## Findings

### Identity, footprint, and placement — 1.8/2

The available Indiana orthophoto/GIS overlay and plan-registration work support the identity and broad outline of Knoy Hall, and the prior coordinator check found the master placement marker consistent with the manifest. The R10 sign was corrected to use the shell's GIS-to-local parent inverse; its reopen validation confirms the text sits in the modeled south entry wall's vertical band. These checks support broad placement and local alignment, but the orthophoto overlay uses the approximate project conversion and is context evidence, not surveyed shell-to-wall registration. R10 did not independently reload the master marker, so the previous marker check remains the evidence for campus placement.

### Floors, height, and roof — 1.2/2

The 2018 Purdue Gateway planning study provides a useful L1–L4 interval: the model's intervals are 4.481, 4.480, and 4.481 m against 4.4704 m in the study. The 2018 3DEP DSM/DEM comparison is a plausible roof-surface cross-check, but its approximately 59.9 ft median difference mixes roof levels, edges, and rooftop objects and is not a roof survey. It does not establish that L5 is occupied, its exact datum, the parapet or penthouse height, or reconcile the GIS 48 ft field. The modeled L5/roof/penthouse therefore remain explicitly uncertain.

### Exterior and entrance — 1.6/2

The exterior render has recognizable repeated ribbon glazing, brick courses, pale horizontal bands, a screened roof zone, and the modeled south entrance identity. Round 10 adds the photo-supported “KNOY HALL OF TECHNOLOGY” lettering and brick finish on two existing sign-wall faces. The local 2018 Purdue History Project photo supports the wording and general entry context but is uncalibrated and does not give exact letter dimensions, mounting position, metal finish, or full facade cadence. The R10 close-up reads clearly, though the letters appear large relative to the photograph; scale cannot be confirmed from the perspective source. The broader facade remains schematic and visually repetitive, with no calibrated elevations establishing window cadence, wall materials, or all-sided appearance. R9's broader facade/material limitations remain substantially unchanged.

### Interior and circulation — 1.3/2

The L2–L4 partition traces use a 2018 typical-plan source with approximately ±1 m registration uncertainty; L1 traces use a separate thesis plan and are less certain. Current plan cutaways show partition geometry, but render-only high-contrast materials are not saved finishes. Candidate door gaps remain unresolved, the illustrative stair cores do not establish a continuous basement-to-roof path, and furniture/room contents are sparse or unsupported. This is more useful than a bare massing model, but it does not verify a complete or current interior layout.

### Technical integrity and evidence — 1.9/2

R10 reports a successful saved-file reopen, 64 asset objects and 63 meshes, and a passed sign-placement check. The geometry SHA-256 of all 62 pre-existing meshes matches the prior expected fingerprint; the localized sign lettering is the only reported new mesh. Roof/L5/PV/registration geometry was not changed. The R10 evidence includes a source URL, source date limits, edit scope, and measurement uncertainty. The review renders are useful visual checks. However, the R10 validation does not itself verify a full master reload/link, all library portability conditions, or the whole asset's exterior and interior against calibrated references.

## Highest-value next work

1. Find a measured elevation or stronger as-built source for upper levels, roof, penthouse, and facade bay rhythm; keep the L5 and roof geometry labeled uncertain until then.
2. Use additional dated facade angles or elevations to improve the repetitive shell and verify the R10 sign's scale and precise location.
3. Improve the whole-floor interior read and circulation only from plans or photos that can resolve door positions and stair/elevator continuity; keep illustrative furniture clearly labeled.
4. Keep the 28-panel count historical, the 4-by-7 array schematic, and the retracted cyan alignment overlay excluded from grading.

## Evidence reviewed

- `modular/buildings/knoy_hall.blend`
- `audit/complete_knoy/evidence_round10.json`
- `audit/complete_knoy/entrance_detail_validation_r10.json`
- `audit/complete_knoy/knoy_entrance_detail_r10.png`
- `audit/complete_knoy/knoy_exterior_full_r10.png`
- `audit/complete_knoy/knoy_south_facade_source_review_r9.png`
- `audit/complete_knoy/knoy_ground_interior_legible.png`
- `audit/complete_knoy/ref_knoy_main_entrance_hist152_2018.jpg`
- `audit/complete_knoy/INDEPENDENT_REVIEW_round9.md`
- `audit/complete_knoy/roof_height_assessment_r8.json`
- `audit/complete_knoy/roof_levels_sources_r8.json`

