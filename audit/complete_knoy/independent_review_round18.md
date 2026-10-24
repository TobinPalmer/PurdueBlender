# Knoy Hall R18 — independent full-building review

**Grade: 7.8/10 — unchanged from my R17 grade and below the 8.0 acceptance target.** Review date: 2026-10-24. I reopened `modular/buildings/knoy_hall.blend` in Blender 5.2.3, recomputed the four geometry fingerprints listed in R18 validation, inspected the R17 exterior render against Purdue Archives' official Knoy photo, and reviewed R18's source/evidence and the existing GIS, floor-plan, roof, and circulation records. The four R18 fingerprints match; the saved asset still has 191 scene objects, 169 meshes, and no unpacked external image files. R18 did not modify building geometry, materials, transforms, or placement.

## Scorecard

I retain the same six-category full-building rubric and score as R17. Normalization: 8.6/11 × 10 = **7.8/10**.

| Category | Score | R18 review |
|---|---:|---|
| Identity and footprint | 1.7/2 | Knoy identity and stepped form agree broadly with the GIS and orthophoto context. Approximate local conversion is not survey control. R18 adds no new plan/footprint measurement. |
| Placement, orientation, and scale | 1.6/2 | Prior manifest/placement checks remain relevant; R18 leaves the transform unchanged. No new independent survey or orientation control was introduced. |
| Height, floors, and roof | 1.2/2 | The DSM analysis gives a broad roof-like surface distribution, but the high samples sit outside the candidate penthouse bounds and may be edge returns, trees, or equipment. It cannot resolve the roof slab, L5 status, penthouse location, or GIS 48-ft conflict. No vertical geometry changed. |
| Exterior and entrances | 1.4/2 | R18 accurately documents the remaining facade mismatch and declines to assign interruptions to unregistered elevations. The saved facade is still repeated broad, continuous window bands; the official photo shows brick-dominant masses with much narrower, interrupted horizontal glazing strips on the visible faces. The photo supports that qualitative difference but not which GIS faces to edit or exact dimensions. No visual fidelity improvement occurred in R18. |
| Interior and circulation | 1.7/2 | Existing plan traces, illustrative doors, fixtures, and stairs remain inspectable, but they are not an as-built plan. R18 confirms no verified dimensioned stair/route source and makes no circulation change. Full vertical/accessibility continuity remains unverified. |
| Technical and evidence quality | 1.0/1 | Current R18 asset reopens; four recorded fingerprints match on independent recomputation; expected meshes and materials exist; no unpacked images. Evidence is clearer about uncertainty, but this category was already at its maximum in my R17 rubric. |
| **Total** | **7.8/10** | **Below target** |

## Facade comparison and R18 impact

The official [Purdue Archives Knoy Hall photo](https://collections.lib.purdue.edu/campus/buildings/75) shows a complex stepped brick mass with narrow horizontal windows interrupted by large areas of masonry. The R17 full-building preview shows a more regular stepped shell but gives its faces continuous repeated glazing ribbons and strong horizontal bands. R18 correctly records this discrepancy. Its decision not to place interruptions on a selected model elevation is prudent because the photo is perspective, uncalibrated, and not registered to the GIS footprint; it cannot identify the pictured face in local model coordinates. The inherited 1.40 m R17 glass height remains an unmeasured visual proxy.

R18 improves the audit trail, not the model's appearance or measured accuracy. The 2018 DSM percentiles clarify that a roof-like surface exists and that the highest cells do not overlap the current candidate penthouse bbox, but they cannot establish the roof/penthouse geometry. This is useful negative evidence and a reason to preserve uncertainty, not a basis to score modeled geometry higher. The model remains at **7.8/10**.

## Decision

R18 is a sound evidence-and-uncertainty update. It explicitly avoids inventing a face-specific facade correction and documents the roof and circulation limitations. Since the saved model geometry is unchanged, the full-building grade does not change. The building remains below 8/10; the most visible shortfall is the continuous all-around glazing cadence versus the interrupted, brick-heavy facade in the official photo.

Reopen and fingerprint check: `independent_review_round18_reopen.json`. Source evidence: `evidence_round18.json`, `validation_round18.json`, and `roof_spatial_check_r18.json`.
