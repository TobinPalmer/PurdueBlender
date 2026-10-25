# Independent NACC asset grade

**Score: 7.50/10** — below the 8/10 minimum

Saved asset SHA-256: `E442E099CF94DDE2B0D95F87E336AC550DAF3445C56A3129C078AE64657E3305`
Blender: 5.2.3 LTS

## Criterion scorecard

| Criterion | Score | Assessment |
|---|---:|---|
| Correct identity and source-backed footprint | 2.00/2 | verified |
| Position, orientation, and scale/dimensions | 2.00/2 | verified within project transform limits |
| Evidence-backed height, floors, and roof form | 1.00/2 | partly supported; estimated |
| Facade, entrances, and distinctive architecture | 1.00/2 | partly supported; facade is interpretive |
| Modular export, portability, and complete evidence | 1.50/2 | export validated; index needs refresh |

## Evidence

### Correct identity and source-backed footprint — 2.00/2

- Purdue GIS FeatureServer FID 927 identifies NACC at 903 5th Street; the Purdue emergency plan independently identifies the former house.
- Reopened structural wall shell agrees with the projected GIS ring: max vertex distance GIS→shell 0.0000 m, shell→GIS 0.0000 m.
- The 20-vertex source outline and modeled wall shell match, including the irregular perimeter; projected footprint dimensions 16.215 × 11.576 m.

### Position, orientation, and scale/dimensions — 2.00/2

- Wall-shell local centroid offset from the GIS polygon centroid: (0.0000, -0.0000) m; registered placement origin in manifest: [-278.928, 190.077].
- Structural dimensions: model 16.215 × 11.576 m; projected GIS 16.215 × 11.576 m.
- GIS-derived wall geometry preserves orientation; local transform uses the project’s stated approximate WGS84-to-meter conversion, not a surveyed CRS.

### Evidence-backed height, floors, and roof form — 1.00/2

- Purdue BEP (revision 2026-03-17) describes a two-story house with a basement; modeled asset has a basement and two above-grade levels.
- Reopened asset vertical bounds are -2.35 to 9.35 m. Eaves/ridge, roof pitch, and total above-grade height are explicit model estimates, with no measured elevation drawing located.
- GIS NUM_LEVELS=1 conflicts with the dated written Purdue BEP. The evidence record acknowledges this conflict.

### Facade, entrances, and distinctive architecture — 1.00/2

- Purdue BEP confirms three exits and locates the main door at Fifth Street, an accessible door toward the gravel parking lot, and the kitchen/rear door facing the alley.
- The reopened asset contains these three named doors, a ramp, and a modest covered back porch next to the alley door; door-to-porch center spacing is 1.30 m.
- Purdue lists room 110 as Back Porch. Front/rear render inspection confirms the covered porch is now on the rear/alley-facing side; the undocumented Fifth Street front porch is absent.
- Window rhythm, shutters, exact door positions, porch dimensions, clapboard detail, and gabled roof are not verified by measured plans or a date-verified facade photo.

### Modular export, portability, and complete evidence — 1.50/2

- Blender 5.2.3 reopened the saved named collection with 806 mesh objects and 10 assigned materials; portable procedural materials=True; external image paths=[].
- All nine expected feature/interior flags present: True.
- Building-specific evidence includes source URLs, provider/feature, retrieval dates, CRS/transform, uncertainty, validation and current front/rear renders.
- The shared manifest still lists removed NACC_front_porch objects and has local_bounds_m inconsistent with the reopened asset; stale names: ['NACC_front_porch_deck', 'NACC_front_porch_fascia', 'NACC_front_porch_roof', 'NACC_porch_column_0']; recorded bounds: [[-16.351694107055664, 11.363021850585938], [-15.093632698059082, 6.431996822357178], [-2.3499999046325684, 9.350000381469727]].

## Findings

- The porch relocation is source-consistent: Purdue says the rear/kitchen door faces the alley and identifies room 110 as Back Porch. The revised render places the roofed porch beside that door and leaves the Fifth Street entrance without a covered porch.
- GIS identity, shape, dimensions, and local registration check out against feature 927. The transform is an approximate project conversion, not survey control.
- The exact roof profile, heights, and facade composition remain estimates. The GIS one-level attribute conflicts with the written two-story BEP, so vertical accuracy is only partly supported.
- The asset file and building evidence are current, but the shared manifest’s object list/bounds are stale relative to this saved revision. This is reported for the coordinator and was not edited here.

## Limitations

- No measured as-built elevation or date-verified current facade photograph was found in the consulted evidence.
- Entrance and porch positions/sizes are supported directionally by the BEP but their exact dimensions and wall offsets remain estimates.
- The GIS source and project transformation support local shape/registration checks; they do not establish surveyed positional accuracy.
- Manifest mismatch is a reported coordinator-owned shared-file issue and was not changed by this independent grader.

## Source references

- Purdue Office of Emergency Preparedness, NACC Building Emergency Plan (revision 2026-03-17): https://www.purdue.edu/operations/emergency-preparedness/nacc/
- Purdue University BuildingShapes ArcGIS FeatureServer, layer 0, FID 927 (snapshot in this audit folder).
- Purdue Native American Educational and Cultural Center: https://purdue.edu/naecc/
