# Heine Pharmacy R1 independent grade

**Score: 7.6/10 — NOT YET PASSING**

Exact SHA-256: `c2dcc0579641f3b6a3b0867ead07da0f789c47f83df1b50434ee77b17a98e017`

## Criteria

### Identity and source-backed footprint — 1.9/2.0

- Evidence: Official Purdue GIS FeatureServer FID 606 explicitly names Robert E. Heine Pharmacy Building and abbreviation RHPH.
- Evidence: The 44-vertex shell mesh provides a 22-point base ring; comparing it with the 92-point transformed GIS ring gives max GIS-to-shell segment deviation 0.267 m and shell-to-GIS 0.000002 m. The GIS source has no survey date/tolerance and the map transform is approximate.
- Finding: Identity and footprint crosswalk are strong; retain the project transform and source-tolerance caveat.

### Position, orientation, and dimensions — 1.8/2.0

- Evidence: Asset local bounds are X [-36.25848388671875, 36.23880386352539], Y [-37.041168212890625, 34.06120300292969], Z [-1.1799999475479126, 23.52248764038086] m; structural shell itself retains the transformed source outline.
- Evidence: Manifest campus origin is [-193.84218632570293, 259.60496004008974] m and is documented unchanged by R1; the master integration audit had previously checked the same marker origin, but this grade did not independently complete a fresh master reopen after the asset update.
- Finding: The local origin and plan extent are consistent with the documented GIS frame. A fresh master reopen against the updated linked asset is still needed before final integration sign-off.

### Height, floors, and roof form — 1.2/2.0

- Evidence: Purdue OEP building-plan evidence supports five above-grade floors, a G-floor and basement; the revised facade displays five window rows on the referenced elevation.
- Evidence: The modeled shell top is 23.52 m and the roof is modeled flat with a small rooftop penthouse. The official GIS lists 8 levels and a roof elevation attribute of 61 with datum/units uncertainty, while the evidence identifies height as estimated.
- Finding: Five above-grade floors have a source, but absolute height, lower-floor exposure, roof elevation and penthouse size remain unresolved. Do not present these dimensions as measured.

### Facade, entrances, and distinctive architecture — 1.0/2.0

- Evidence: The new renderer shows red/orange procedural brick, pale horizontal bands, seven facade bays and an entry/arcade object set. The source image also shows seven narrow dark vertical window strips, wide stone spandrels, a strongly expressed multi-arch entrance and a pale roof parapet.
- Evidence: Visual comparison of the saved fresh-open render with the cited source image shows the model’s seven bays subdivided into a regular grid of five small window panes per bay; the source photograph instead has tall narrow glazing strips with broad light stone panels within those bays. In the render the arcade reads as a small canopy with thin supports rather than a dominant multi-arch portal. The cited photograph is oblique and partly tree-occluded, so exact dimensions are uncertain, but the broad composition difference is visible.
- Finding: The facade revision has not yet achieved the cited facade rhythm. Rework each of the seven bays toward tall, narrow vertically continuous glazing and large stone spandrels; enlarge/raise the multi-arch portal to match its substantial share of the entry elevation. Preserve the evidenced brick palette and horizontal limestone courses.

### Modular export, portability, and complete evidence — 1.7/2.0

- Evidence: Blender 5.2.3 fresh-open probe found scene `Scene`, stable collection `Asset_heine_pharmacy`, 115 collection objects / 112 meshes, 18 used materials, and no missing external image textures.
- Evidence: Saved-file SHA-256 c2dcc0579641f3b6a3b0867ead07da0f789c47f83df1b50434ee77b17a98e017 matches the builder’s reported SHA. Evidence records the GIS source, photo license/date, official emergency-plan source, geometry method, uncertainty, and fresh-open render.
- Finding: The manifest still advertises object_count=133, but the current collection contains 115 objects; update the shared manifest and synchronization verification after a passing revision is integrated.
- Finding: No external texture dependency was found; evidence is unusually complete for the available sources.

## Overall findings

- Current grade is below the project pass threshold of 8/10. The next revision should focus on the seven-bay glazing proportions and portal scale, then rerender and request a new independent grade.
- Height and room layout must remain explicitly estimated/schematic without stronger source evidence.
