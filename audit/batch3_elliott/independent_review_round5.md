# Elliott Hall of Music — independent round 5 review

**Independent score: 6.4/10. Below the requested 9/10 threshold.** I reopened `modular/buildings/elliott_hall_of_music.blend` in Blender 5.2.3 LTS, checked the 77-mesh `Asset_elliott_hall_of_music` collection, independently repeated all five wall-ray checks against the saved evaluated shell, inspected round-5 exterior/connector/auditorium renders and the saved interior views, and compared placement against the modular manifest/master marker. I did not edit the building or master.

## What improved

- The current source reopens. The export collection has 77 meshes and 79 total objects; the 496-object legacy reference collection remains separate.
- The recorded project registration is internally consistent: the modular master marker is at `(-111.0000, 49.9000, 0.0000)`, zero rotation, unit scale, instancing `Asset_elliott_hall_of_music`. This agrees with `placement_origin_xy_m` in the manifest. The asset's local GIS outline is approximately X `[-46.418, 44.075]`, Y `[-38.128, 46.926]` m; adding the marker gives X `[-157.418, -66.925]`, Y `[11.772, 96.826]` m. This supports the registered horizontal location and shape only. The manifest still describes the old two-object asset, so its count/bounds must be refreshed during master integration.
- Round 5 independently passes the five submitted center-ray checks on the saved shell. For North, South, Hovde ground west/east, and the upper Hovde opening, the center ray has no hit, while the corresponding above-opening control ray hits the wall. The measured edge projection offsets are 0.00001–0.00064 m. This verifies a sampled through-path at the current candidate coordinates, not opening width, full door clearance, or real-world location.
- The Elliott connector now terminates before Hovde, with an obvious physical separation in the close render. That is a safer representation of the evidence state than a bridge visibly colliding with an unverified Hovde wall. The asset metadata also says the Hovde portal remains deferred.
- The auditorium blockout still reads as a theater: stacked seating tiers, aisles, balconies, stage opening, curtain and pale interior finish are present in prior saved stage/rear views.

## Main issues

1. **The exterior facade remains substantially unfinished.** `exterior_round5.png` is still dominated by uninterrupted red-brown wall. Vertical pale strips read as a repeated generic pier pattern, but the four claimed limestone belt courses are not legible as continuous horizontal bands in the exterior render. The rendered brick surface has no readable brick bond; most visible wall faces remain smooth. No window schedule is modeled. Avoiding unsupported window counts is evidence-conscious, but the resulting blank wall is not a convincing final elevation. SAH's described brick, limestone banding and pilasters support feature/material types; they do not verify this mesh's 35-pilaster schedule, dimensions or elevations.
2. **The round-5 auditorium image does not show the interior.** `auditorium_round5.png` is an exterior roof/wall close-up, so it cannot validate seating or circulation. The older `from_stage.png`, `from_rear.png`, `from_balcony.png`, and `interior.png` do show the schematic seating and stage, but round 5 did not refresh an interior camera/render. Those views reveal repetitive block seats and broad dark tier/ceiling bands; aisle widths, seat count/spacing, accessibility positions, lobby and backstage remain unverified or conceptual.
3. **The gap annotation is not readable enough in the close render.** The image shows a small dark label at the stub, but its text is difficult to read at the delivered framing. The missing Hovde wall/portal is also intentionally absent from these Elliott-only renders, so this image cannot prove placement against the live Hovde asset. Keep the endpoint explicitly provisional and verify it jointly in the master before creating a bridge.
4. **The source descriptions conflict on the named Hovde approach corner.** The round-5 notes cite the Club Convos page as identifying the southeast entrance. Purdue's current accessibility page describes Hovde entry from the southwest corner and an adjoining bridge to Elliott's lobby. Both establish a second-floor route, but the corner naming differs; resolve the approach point against the Hovde asset/site map rather than using either description alone. The SAH page returned a 403 during this review, so its round-5 summary could be cross-checked only against the saved source notes, not the live article text.
5. **The opening ray evidence is narrow.** Center ray plus a solid control ray is a useful shell check, but does not establish opening extents or that a door leaf/threshold is clear. Round 5's target points lie close to the GIS boundary, but the positions and dimensions remain estimates and are not supported by an inspectable elevation/photo or measured plan.

## Score breakdown

| Criterion | Score | Basis |
|---|---:|---|
| Overall form and footprint | 7.0/10 | Recognizable auditorium footprint and mass; plan registration agrees with the project marker. Roof/flytower heights and form remain estimated. |
| Exterior fidelity and materials | 5.2/10 | Round-5 pilasters add a supported feature type, but horizontal courses and brick texture do not read in the view; no verified windows or source-matched elevation. |
| Entries and Hovde approach | 5.8/10 | Five sampled through-openings pass; the project route is supported, but locations/dimensions and the Hovde portal are not verified. The marked gap is appropriate but not jointly contextualized. |
| Interior | 6.5/10 | Theater, tiered seating, stage and aisles are recognizable in earlier interior views; the current round-5 auditorium image is misframed and layout is conceptual. |
| Materials and surface detail | 5.8/10 | Roof tile pattern reads. Exterior brick/limestone treatment is mostly smooth and the course pattern is visually unclear. |
| Placement and evidence | 8.0/10 | Local frame and master marker agree, and all five sampled rays reproduce. Manifest object inventory is stale and several dimensional/location claims are estimates. |

## Priority fixes

1. Make the limestone belts read as horizontal courses in an elevation render and add visible brick bond/surface relief. Check whether the belt mesh is exposed from the exterior shell rather than hidden or coplanar. Retain explicit estimates for course levels and pier spacing.
2. Replace the round-5 `auditorium_round5.png` view with a camera inside the hall, and show a clean stage-to-seating view plus a plan/top view. Keep seat counts, dimensions and clearances marked conceptual until a scaled source plan is available.
3. Resolve the Hovde entrance corner against the actual site/Hovde model, then do a linked-context render with both buildings. Model the Hovde-side portal only after confirming the shared opening; remove the temporary label only after the joint endpoint passes review.
4. Check all five apertures with multiple rays across each claimed width and at sill/head levels; document door, threshold and approach geometry separately. Confirm the two ground openings with an inspectable photo or plan before treating their locations as verified.
5. After acceptance, refresh the manifest object count/bounds and reload both master files. The saved marker is correctly placed, but the current manifest still lists two export objects.

## Source and project checks

- SAH Archipedia is cited by the builder for red brick, Indiana limestone, pilasters/banding, tile roof and the Hovde walkway: https://sah-archipedia.org/buildings/IN-01-157-0079. The page denied direct retrieval during this review; the feature summary here is attributed to the saved round-5 notes.
- Purdue Convocations currently says the north/south access doors have black-and-gold awnings and provide step-free access to main-floor seating; it also says the Hovde route uses an adjoining bridge: https://convocations.purdue.edu/accessibility/.
- Purdue's Club Convos page says access is from Hovde's southeast entrance and directs visitors to the second floor adjacent to Elliott's main lobby: https://convocations.purdue.edu/clubconvos/. These current Purdue pages describe different Hovde corners, which needs site/model resolution.
- Project placement check used `modular/manifest.json` and the read-only `Placement_elliott_hall_of_music` instance in `modular/purdue_campus_linked.blend`; no master data was changed.

The round-5 file is a measured improvement to verification and to the deliberately deferred Hovde endpoint. It remains far below 9/10 because the exterior is still blank and weakly textured, the new band courses are not visually clear, and the interior/render evidence does not verify the saved layout.
