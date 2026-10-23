# Elliott Hall of Music — round 11 notes

Work date: 2026-10-23. Scope: `modular/buildings/elliott_hall_of_music.blend` and round11 evidence in this folder only. No master, manifest, BUILDINGS.md, Hovde source, or GIS placement edits.

## Pass changes

- Changed the auditorium seat fabric from brown to restrained neutral gray with fine procedural variation. Purdue Convocations' current venue-photo description identifies gray cushioned seats. Exact hue and fabric remain approximations; individual seat geometry, dimensions, and auditorium circulation remain schematic.
- Rendered `interior_from_stage_round11.png` after the material change and `exterior_round11.png` to show the current modeled roof, fly tower, curved auditorium shell and limestone/brick treatment.
- Preserved the previously repaired entry trim clearance and the Elliott-only provisional interface landing. No bridge, continuous Hovde route, accessibility, or egress claim was added.
- Did not add a facade window schedule or invented side-exit geometry. Available source text supports feature families/materials but not opening counts, spacing, or modeled dimensions; browser-accessible imagery could not be pixel-verified for those features.

## Source record

- [SAH Archipedia: Elliott Hall of Music](https://sah-archipedia.org/buildings/IN-01-157-0079) describes red brick with Indiana-limestone banding/pilasters/ornament, a red clay-tile roof, fly tower, apsidal projection behind the stage, curved entry canopy, secondary entrance surrounds, stepped side-exit walls and Hovde connection. This supports material and feature types only; dimensions and facade/window schedule are not supplied in the evidence available to this pass.
- [Purdue Convocations seating chart](https://convocations.purdue.edu/wp-content/uploads/2022/09/Elliott-Seat-Map.pdf) shows the main floor and two balconies with curved blocks. It is not a dimensioned plan.
- [Purdue Convocations venue/directions page](https://convocations.purdue.edu/directions/) has a current venue photo described as showing gray cushioned seats, a wide center aisle and high ceiling. This guided seat color only; the photo itself was not pixel-inspectable in this environment and does not establish the modeled geometry.
- [Purdue Convocations accessibility information](https://convocations.purdue.edu/accessibility/) identifies accessible venue entry information; the asset's door dimensions and route compliance remain unverified.
- The prior [Purdue BuildingShapes FID 617 footprint comparison](footprint_comparison_round9.json) is unchanged by this round. It reports 0.1668 m RMS and 0.2594 m max ordered-vertex residual, area delta -0.168%, perimeter delta -0.076%, using an approximate ground conversion. It supports horizontal footprint fit only, not height/elevation or route continuity.

## Reopen and evidence

`reopen_check_round11.py` reopened the saved asset in Blender 5.2.3 LTS. The Elliott asset collection contains 135 mesh objects, no `TEMP_R11_` objects remain, north/south door objects remain present, and the three portal trim meshes retain zero modifiers. The checked source and output paths are in `result_round11.json`.

## Remaining major gaps

The principal elevations remain incomplete: no source-verified window schedule, exterior opening positions, secondary-entry elevations, or side-exit geometry were added. Fly tower, roof profile, and apsidal massing still need dimensioned or pixel-verifiable evidence. Auditorium stairs, aisles, stage/backstage relationship, egress and dimensions remain schematic. The Hovde portal and connector require the Hovde owner's separate pass. This pass does not meet or claim the 9/10 target; independent review is requested.
