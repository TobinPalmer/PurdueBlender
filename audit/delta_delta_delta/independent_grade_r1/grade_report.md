# Independent Delta Delta Delta Grade R1

**Score: 8.3/10 — PASS** (minimum: 8.0/10)  
**Frozen asset SHA-256:** `0890efdbbb2eff92dfbfd6a60d69a6d4006108a029e8d209ef7791b34182b376`

I opened the asset in a separate Blender 5.2.3 process and inspected the front render, source register, official chapter sources, and Purdue GIS snapshot. The identity is supported by Purdue GIS FID 753 and the current Purdue FSCL listing for the Gamma Iota chapter. The panorama card still labels the nearby viewpoint `898 Tower Dr`, while GIS and the map place result identify `1200 Tower Dr`; the exact street-number relationship is unresolved.

I independently extracted the foundation ring from the fresh-open Blender asset and recomputed its overlay against FID 753 using the project coordinate conversion. The result is IoU **0.999999965** and symmetric Hausdorff distance **0.000000886 m**. Because the model ring was created from this same GIS polygon, this checks projection, local recentering and serialization. It does not independently establish the true wall line or prove that the GIS feature corresponds to the visible building.

| Criterion | Score | Evidence and findings |
| --- | ---: | --- |
| Correct identity and source-backed footprint | 1.8/2.0 | GIS labels FID 753 Delta Delta Delta at 1200 Tower Dr; Purdue FSCL lists the Gamma Iota chapter; a current map place result also identifies the house at the GIS coordinate. The panorama viewpoint card says 898 Tower Dr, leaving a small address-label uncertainty. The exact shell overlap is same-source evidence, not independent wall-line validation. |
| Position, orientation, scale and dimensions | 1.8/2.0 | The fresh-open asset uses the expected local coordinate frame and its ring independently recomputes to the source GIS ring; place-point offset is documented as 0.2273 m. Master marker placement remains pending, and exact wall registration/dimensions are not surveyed. |
| Evidence-backed floors, height and roof | 1.3/2.0 | Two occupied levels and a low dark roof match the Street View description; fresh-open geometry reaches 10.05 m. Height and floor count are visual estimates, not measured. GIS `NUM_LEVELS=1` conflicts with the two-level interpretation, and exact roof elevations remain unknown. |
| Facade, entrance and distinctive architecture | 1.6/2.0 | The render includes buff masonry, lower arched windows, upper rectangular windows, a central rounded four-column portico, balcony rail, double doors and broad steps. The source descriptions support the overall design. Facade rhythm is simplified, and the reported three-triangle mark is not clearly legible in the front render. The interior exists but is schematic and not based on a measured plan. |
| Modular export, portability and evidence | 1.8/2.0 | Fresh-open found the expected scene/collection, 1,328 objects (1,327 meshes), nine used materials, no linked libraries and no unpacked external images. The source register and uncertainty record are present. Shared manifest and master Placement marker still need root integration and fresh-open validation. |
| **Total** | **8.3/10** | **Pass** |

## Remaining uncertainty

- Reconcile the GIS/map address 1200 Tower Dr with the panorama's 898 Tower Dr viewpoint card.
- Validate the detailed library through its master Placement marker after root integration.
- Keep two floors, 10.05 m ridge height, roof dimensions and interior layout marked as estimates.
- Do not treat the near-zero GIS overlay as independent confirmation of structural walls; the model was generated from that same polygon.

Machine-readable scoring and the independent comparison are in [`result.json`](result.json) and [`gis_comparison_independent.json`](gis_comparison_independent.json). The fresh-open inspection is in [`fresh_probe.json`](fresh_probe.json), and the inspected asset render is [`delta_delta_delta_front.png`](../delta_delta_delta_front.png).
