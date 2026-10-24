# Independent Review — John T. McCutcheon Residence Hall R2

**Review date:** 2026-10-24  
**Reviewed asset:** `modular/buildings/mccutcheon_hall.blend`  
**Reference package:** `REVIEW_R2.md`, `mccutcheon_r2_evidence.json`, `mccutcheon_r2_validation.json`, `mccutcheon_r2_hero.png`, retained R0 object inspection, and R1 footprint diagnostic.  
**Reviewer scope:** Read-only inspection. No McCutcheon model, script, master file, or shared index was changed.

## Independent result

**Overall: 7.5/10 — below the project's 8.0 acceptance threshold.**

The model is recognizably a large red-brick residence hall with two long, tall wings, a lower central connector, repeated vertical window strips, rooftop equipment/penthouses, an entrance zone, and a small site context. Its horizontal registration has strong GIS support, and R2 fixes two obvious material-category mistakes in the surrounding site. The render remains a simplified architectural massing/model presentation: the precise elevations and floor count are unverified, facade screens and opening cadence are not checked against a direction-identified reference, the large central roof is visually blank, and the purported interior is represented by explicitly unverified opaque shells rather than interior rooms or circulation.

The score reflects what is present and evidenced, not the reported completion label. The validation pass confirms that the file reopens and its resources are available; it does not establish architectural accuracy.

## Category scores

| Category | Score | Findings |
|---|---:|---|
| Identity and program | 9.0 | The asset and official Purdue housing source identify McCutcheon as a residence hall opened in 1963. Its broad massing reads as a residence hall. |
| Horizontal placement and footprint | 8.5 | FeatureServer FID 57 and the saved base-plinth bounds agree to under 0.0001 m at reported precision. This is a local approximate frame and axis-aligned bounding-box match; it is not survey control or proof that every structural wall follows the source polygon. |
| Massing and height | 7.0 | Two elongated residential wings and a lower connecting block are legible. The asset reaches about 30.35 m, but the R2 package explicitly says that height, floor spacing, and roof profile are unverified. No reliable elevation or direction-identified photo set in the package resolves this. |
| Facade and openings | 7.0 | Red brick and narrow, regularly repeated vertical window groups are plausible and read coherently from the hero view. The broad blank wall areas, exact window count/spacing, orientation, entrance distribution, and decorative concrete-screen placement remain unsupported or unverified. The hero image does not provide enough angles to validate all elevations. |
| Materials, site, and presentation | 7.3 | R2 correctly changes the lawn from gray concrete to a qualitative grass shader and the two drives from roof membrane to qualitative asphalt. The hero render still has a flat gray world, mostly uniform surfaces, weak environmental cues, and a broad hard-edged site slab. R2 makes no calibrated material claim, appropriately. |
| Interior and circulation | 5.0 | Purdue confirms shared bathrooms and common study/social spaces, but the source asset labels its north/south tower and central pavilion as `Unverified_Shell`. The exterior hero exposes no useful interior. There is no verified floor plan, corridor, stair, room, bathroom, or entrance-to-circulation route to grade as an accurate interior. |
| Technical integrity and handoff | 9.0 | R2 validation reports Blender 5.2.3 reopen, root transform identity, packed linked foliage images, no unresolved unpacked images, and a saved hero render. The diagnostic GIS outline is correctly hidden in render and retained in viewport. |

**Scoring method:** Equal-weight mean of the seven categories above, rounded to one decimal: 7.54 → **7.5/10**. Scores are reviewer judgments, not measurements.

## Evidence and limitations

- The Purdue University Residences page identifies McCutcheon, its 1963 opening, traditional residence-hall use, shared community bathrooms, and common study/social spaces. It says its standard room illustration is approximate; it does not establish the as-built interior or exterior dimensions. [Purdue University Residences — McCutcheon](https://www.housing.purdue.edu/my-housing/options/residence-halls/mccutcheon.html)
- The R2 audit links a Purdue BuildingShapesZip4 FeatureServer polygon, FID 57. Its reported near-exact match is between the polygon's transformed axis-aligned bounds and the plinth bounds. The same audit correctly cautions that this is approximate horizontal registration, not a structural survey, height source, or complete footprint-shape proof. [Purdue BuildingShapesZip4 FeatureServer layer 0](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0)
- The AS&U page includes a McCutcheon exterior image and confirms the hall opened in 1963 and houses 730 residents. The saved audit treats that image as qualitative context because its view direction and dimensions are not established. This review did not infer measurements or unseen facades from it. [American School & University, 2022-10-05](https://www.asumag.com/safety-security/article/21252186/student-slain-in-purdue-university-residence-hall)
- The R2 hero image visibly supports the broad massing and material-readability comments above. The R1 footprint diagnostic and R2 GIS report support a bounds check only; no claim is made here that the complete polygon shape or architectural footprint was independently surveyed.
- R2 is a site-material and diagnostic-overlay revision. It does not improve the building shell, height, windows, entrance/canopy, roof, interior, or trees. That is documented in its own evidence and is borne out by the supplied hero render.

## Most valuable next improvements

1. Obtain direction-identified current exterior photos or public measured drawings, then compare each elevation and roofline; do not derive heights from the unverified GIS level attribute.
2. Add or document facade-screen elements only where photos confirm their position and coverage; verify window cadence and entrances on all sides.
3. Replace the current interior placeholder shells with a clearly schematic, source-supported route and limited room/common-space layout, or label the model as exterior-only.
4. Improve render presentation (sky/world, light direction, shadows, and ground/path detail) after the architecture is checked. Keep procedural grass/asphalt labeled qualitative.

## Decision

**R2 is technically reopenable and the horizontal GIS envelope is well registered, but the building is not yet at the 8/10 whole-building bar.** The main reasons are unresolved elevation/facade evidence and the absence of a verifiable interior/circulation model. No geometry correction is recommended from this evidence set alone.
