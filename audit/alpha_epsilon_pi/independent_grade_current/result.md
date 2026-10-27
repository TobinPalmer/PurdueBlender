# Independent Alpha Epsilon Pi review

**Score: 7.80/10 — needs refinement.** The 8.0 passing threshold is not met.

| Criterion | Score | Independent assessment |
| --- | ---: | --- |
| identity and source backed footprint | 1.35/2 | The current Purdue BoilerLink chapter profile is cited as listing 1051 David Ross Road. Purdue GIS FID 754 lists that same address and its polygon overlays a roof in the saved Esri imagery overlay. |
| position orientation and plan dimensions | 2.00/2 | Fresh-open measurement found 60 corresponding GIS/model outline vertices; maximum vertex error is 1.11e-06 m under the project's documented local tangent transform. The exported collection uses the expected local-coordinate frame and centroid placement origin [-948.801726, 959.29698] m. |
| evidence backed height floors and roof | 1.40/2 | The saved dated 2009 Purdue AEPi photograph is attributed and depicts the broad three-story brick/mansard-roof character used by the model. A fresh-open inspection measured walls from Z=0.58 to 9.36 m, lower mansard slope 9.48–11.03 m, upper slope 11.03–12.38 m, plus a chimney to 13.57 m. |
| facade entrances and distinctive architecture | 1.15/2 | The fresh-open asset contains 30 named facade window fronts, 20 window AC units, 9 dormer glazing objects, an entry portal, and Greek-letter signage. The 2009 source image supports brick, three visible stories, projecting bay windows, window AC units, Greek letters, and a shingled mansard roof. |
| modular export portability and evidence | 1.90/2 | A separate Blender 5.2.3 background process opened the exact candidate file (SHA256 de01abd4cb52f856630d11906f7ded9517da6f584a0ea088ce50ebbc1c634763) and found the named scene, building ID, named collection, and local-coordinate flag. Fresh-open inspection counted 710 collection objects, 708 meshes and 20 referenced materials; no meshes lack materials, no mesh misses the asset root parent, and no external file images are unpacked. |

## Required refinements

1. Identity crosswalk is supported by address and roof location but not conclusively verified; retain the conflict in all project records.
2. These are high-precision comparisons to the GIS source polygon, not survey-grade verification of GIS accuracy or identity.
3. Keep story heights and total building height explicitly estimated. A newer elevation, LiDAR return, or measured roof evidence would improve confidence.
4. Tune the brick mapping/scale so the facade reads as masonry at the saved render scale; improve the visible bay depth, window AC detail, and facade transitions; verify side/rear roof volumes against newer imagery if available.
5. The saved previews demonstrate the asset but do not verify integration into the campus master; that remains a coordinator-side check.

## Limits

- The review does not certify current occupancy at the GIS footprint or master-blend integration. Interior arrangement is representative and not tied to a measured plan.
