# Neil Armstrong Hall — independent R11 review

**Grade: 7.8/10 — below the 8.0 completion target.** The prior recorded R10 independent grade was 7.6/10. R11 merits a small improvement for its cleaner exterior presentation and photo-supported dark red-brown canopy, but it does not resolve the principal roof, facade-registration, and footprint deductions.

## R11 checks

I reopened the supplied saved asset in Blender 5.2.3. Its SHA-256 is `d3d90d21ad60b985826270be18c016220944e3c87545fc179af7b51d5084b8b4`, matching the requested revision. The exported collection contains 445 objects (415 meshes); the 445 listed names in `modular/manifest.json` match exactly. All mesh objects have valid material assignments, and the file contains no external image dependencies.

All three coarse R5 NDHM envelope objects remain in the collection, but each has `hide_get=true` for the active view layer and `hide_render=true`. They therefore remain available as references without appearing in viewport display or renders. The canopy deck and fascia both use `ARMS_Sea_Wolf_ACM`. Its shader uses linear base color `[0.08, 0.037, 0.027]`, metallic `0.55`, and roughness `0.36`; the resulting dark red-brown hue agrees qualitatively with the local 2016 exterior photo. The image is not color-calibrated, so these shader values are an estimate rather than a verified manufacturer color.

The mesh/polygon/world-transform digest and object names match the previous `.blend1` snapshot. The exact master placement marker was checked read-only: it instances the expected asset at `[-109.0, 400.1893310546875, 0.0]`, with zero rotation and unit scale, matching the manifest origin. This verifies the marker and library link, not the shell’s surveyed alignment or facade orientation.

## Scorecard

| Criterion | Score | Main finding |
|---|---:|---|
| Identity and source-backed footprint | 1.6/2 | Building identity and GIS record are correct, but wall/roof-to-polygon correspondence is unresolved. |
| Position, orientation, and scale | 1.6/2 | Master marker exactly matches the manifest; shell orientation and wall registration remain approximate. |
| Height, floors, and roof form | 1.4/2 | The 53 ft atrium and four-level description are sourced; the signature warped roof is still not measured or faithfully verified. |
| Facade, entrance, and distinctive architecture | 1.5/2 | Canopy color now aligns with the photo, but facade cadence and roof-wing geometry remain generic or uncertain. |
| Modular export, portability, and evidence | 1.7/2 | Reopen, manifest, materials, image dependencies, and placement-link checks pass; architectural footprint evidence is still weak. |
| **Total** | **7.8/10** | **Below target** |

## Remaining deductions

1. Register the architectural wall outline to a suitable plan or calibrated source. The master marker’s exact translation does not prove that the walls are oriented or fitted correctly.
2. Find dimensioned roof/elevation evidence or improve the wing-like roof silhouette using clearly bounded visual inference. The current R11 update changed only the canopy finish and presentation visibility.
3. Provide whole-building, multi-side renders with a comparable source image or measured elevation so the facade and roof form can be judged beyond the entry close-up.

The score remains below 8/10. R11 correctly hides the coarse height-envelope proxies and improves the canopy hue, but those presentation/material refinements do not resolve the major architectural evidence gaps.

## References

- [Neil Armstrong Hall project case history](https://designandbuildwithmetal.com/featured-projects/neil-armstrong-hall-of-engineering) — supports the 53 ft atrium, warped wing-like roof, and named ACM finishes.
- [Purdue Armstrong Hall emergency plan](https://www.purdue.edu/operations/emergency-preparedness/arms/) — supports the four-level facility description.
- [Wikimedia Commons 2016 exterior photo](https://commons.wikimedia.org/wiki/File:Neil_Armstrong_Hall_of_Engineering_Purdue_University_2016_03.jpg) — qualitative canopy color reference only.

This was a read-only grade of the building and shared project files. The independent report and validation outputs are under `audit/neil_armstrong_hall_refine/`.
