# Independent Review — John T. McCutcheon Residence Hall R3

**Review date:** 2026-10-24  
**Reviewed asset:** `modular/buildings/mccutcheon_hall.blend`  
**Reference package:** `REVIEW_R3.md`, R3 evidence and validation JSON, R3 hero and entrance renders, GIS FID 57 snapshot, and the prior R2 independent review for context.  
**Scope:** Read-only review of the separate McCutcheon asset. No model, master, or shared index was edited or saved.

## Result

**7.65/10 (7.7/10 rounded) — below the 8.0 threshold.** R3 makes no building geometry changes. It improves the standalone sky and hero camera and adds a saved entrance view. The asset clearly reads as McCutcheon: two tall brick wings, a low connector, repeated vertical window groups, rooftop equipment, and a recognizable entry zone. The GIS envelope registration and standalone portability checks are strong. The score remains under threshold because there is no measured height/floor/roof evidence, the available official photo cannot verify full elevations or exact feature placement, the interior remains unverified shell geometry, and no master placement check was done.

## Criterion scores

| Project criterion | Score | Evidence and deduction |
|---|---:|---|
| Correct identity and source-backed footprint | 1.9 / 2 | Purdue identifies McCutcheon Hall. GIS FID 57 transformed bounds agree with the base-plinth AABB to under 0.0001 m at recorded precision. Deducted because the layer is not survey control and matching AABBs does not prove every wall edge or the complete polygon shape. |
| Position, orientation, and scale/dimensions | 1.6 / 2 | The asset follows the documented approximate local tangent-plane transform and the GIS envelope aligns. No master placement check was performed; the transform is approximate, and full structural shape, facade direction, and measured dimensions remain unverified. |
| Evidence-backed height, floors, and roof form | 0.9 / 2 | The model presents two tall wings, a low connector, rooftop equipment, and roof enclosures. The 30.35 m modeled top and GIS ten-level attribute are explicitly unverified; no measured elevation or full-height direction-registered photo resolves them. |
| Facade, entrances, and distinctive architecture | 1.45 / 2 | Purdue's official exterior image supports qualitative red brick, blue-gray glazing, a perforated concrete screen, low glazed entry, light base, name sign, lawn/planting, and rooftop mechanical equipment. The saved entrance view contains corresponding feature categories. The image is cropped, oblique, undated, unscaled, and not direction-identified; it cannot verify exact position/dimensions or the blank elevations and repeated window cadence. |
| Modular export, portability, and complete evidence | 1.8 / 2 | Blender 5.2.3 reopened the asset; expected collection/root transforms persisted; all 10 foliage images are packed; there are no unresolved unpacked images; R3 renders were saved; GIS diagnostic overlay is hidden in renders. Deducted because master integration/placement was not evaluated and no as-built interior was supplied. |

**Scoring:** Sum of the five project rubric criteria = 7.65/10; display rounded to one decimal = **7.7/10**. These are evidence-based reviewer judgments, not measured accuracy.

## Visual and source comparison

The R3 hero render shows tall brick wings with dense, repeated narrow windows framing a wide central lower roof/connector. The entrance render shows brick signage, glazing, a large perforated screen, ramps/steps and rails. Those categories match the official Purdue Residences exterior photograph, including the distinctive screen and entry composition. However, the official photo is only 640×360, oblique, partially screened by trees, undated, and has no scale or camera direction. It is not a reliable basis for shifting the screen, assigning it to a compass elevation, or extrapolating the whole tower facade. The broad blank wall surfaces and exact opening cadence remain open verification issues; I did not infer fixes from an unmatched view.

The hero render has improved from R2's flat gray world: the sky reads as a clear daylight environment. The site still reads as simplified green lawn and gray asphalt/concrete planes with sparse planting, and the hero lighting/render remains stylized. These are secondary to the unverified architectural dimensions and elevations.

## Interior and uncertainty

Purdue's residence-hall page confirms shared bathrooms and common study/social spaces, but its typical-room plan is approximate and does not locate as-built rooms, corridors, stairs, or elevators. The model's interior shells are explicitly unverified. R3 wisely adds no guessed interior geometry; this review does not count an exterior render as evidence of accurate internal circulation.

The GIS feature's ten-level attribute is marked unverified. The modeled top near 30.35 m is likewise not supported as a measured height. The official image shows some roof-level mechanical equipment but does not resolve the roof silhouette or penthouse dimensions. Retain these limitations until measured drawings, verified elevations, or direction-identified imagery are available.

## Technical decision

The standalone R3 asset is technically reopenable and portable according to the saved validation report. The GIS check is an envelope comparison in the project's approximate local frame, not a survey and not a check of its placement in the master. The R3 report also confirms no master-scene placement review.

**Decision:** R3 is a solid presentation and evidence update, but it does not meet the 8.0 full-building bar. No geometry correction is justified solely by the current unregistered photo. A fresh master-position check plus reliable elevations or direction-identified photos would address the main evidence gaps; as-built plans would be required before claiming verified interior circulation.

## Sources

- [Purdue University Residences — McCutcheon](https://www.housing.purdue.edu/my-housing/options/residence-halls/mccutcheon.html) — identity, residence hall use, opening date, amenities; no measured elevation or as-built plan.
- [Purdue University Residences — accommodations page and exterior image](https://www.housing.purdue.edu/visit/conferences/accommodations.html) — qualitative facade/entry features only.
- [Purdue BuildingShapesZip4 FeatureServer layer 0](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0) — feature FID 57 and GIS envelope snapshot.
- [Purdue News Service photo finding aid MSP19](https://archives.lib.purdue.edu/fa/MSP19_News_Service.pdf) — historical photo catalog entries; not treated as inspected elevation evidence.

The criterion-level evaluator and machine-readable result are in `independent_review_r3_evaluate.py` and `independent_review_r3_scorecard.json`.
