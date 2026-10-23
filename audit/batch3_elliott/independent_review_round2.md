# Elliott Hall of Music — independent review round 2

Reviewed 2026-10-23. This is an independent assessment of the saved and reopened source library after its exterior pass. I did not modify the source asset or either master blend. Blender 5.2.3 inspection confirms that `Asset_elliott_hall_of_music` contains 26 meshes and the source scene still contains a separate hidden collection with 496 legacy objects. The saved exterior render and three auditorium views were reviewed alongside the current seating map and available architecture / accessibility references.

## Rating

**Overall: 5.9/10. It does not meet 9/10.** The exterior pass materially improves the asset, and the auditorium reads clearly as a large three-level theater. Key dimensions, entrance locations, room connections, and much of the exterior rhythm remain approximate or unverified.

| Criterion | Score | Review |
|---|---:|---|
| Architectural form | 5.5/10 | The 188-point official footprint still defines a recognizable, curved hall. The shell is 22.5 m high and its flytower reaches about 33.15 m; neither vertical measure nor the fitted tower footprint is sourced from a measured elevation. A large flat main roof and plain rectangular flytower are evident in the top / exterior views. |
| Exterior fidelity | 4.5/10 | The asset now has brick, five limestone courses, pilaster/window trim, tile geometry, a canopy, and six small figures. The visible result has a very regular, repeated window rhythm and thin bands; the main entrance composition and curved canopy do not read clearly in the saved exterior views. The builder's script labels the single ground-level entrance as inferred. Purdue currently identifies north and south accessible doors with black-and-gold awnings; the asset has only one modeled door and does not show that pair. Secondary entrances and the stepped side-exit walls described by architectural history are not clearly represented. |
| Interior layout and circulation | 6.0/10 | Three seating levels, eight sections and the corresponding broad row ranges are present, with aisle stair treads, railings, stage and curtains. The saved count of 5,946 is within 1% of Purdue's 6,005 capacity, but the current published seating map is explicitly a seating chart rather than a scaled architectural plan. Row lengths and seat centers therefore remain generated estimates. Twelve blue markers do not by themselves establish wheelchair clearances or the route from the documented north/south entrances. The images show no verified lobby, backstage room layout, or continuous stairs/corridors to both balcony levels. |
| Materials and texturing | 6.0/10 | The asset uses named, local procedural materials for brick, tile, limestone, glass, seats, curtains and stage. The palette is plausible, but renders show mostly uniform brick and uniformly repeated seat blocks; roof pitch and surface, masonry scale, upholstery fabric, and stone finish have no measured or close material reference. Blender confirms there are no image-texture paths in the named materials, so the claim is of procedural material coverage, not photo-textured surfaces. |
| Placement and scale | 7.5/10 | The shell stays aligned to official GIS FID 617 and retains its horizontal registration. This supports a useful campus-scale footprint. Entrance/window positions and all important vertical dimensions remain inferred; GIS establishes the horizontal polygon only. |
| File hygiene | 7.5/10 | The source reopened successfully. Its 26-mesh export is compact relative to the 496-object hidden legacy reference collection, which remains outside the export. The source report says the master manifest still carries the prior 2-object count; root integration must refresh and reopen the master before considering the batch integrated. |

Scores prioritize architectural / interior fidelity over source-file convenience. In particular, matching the aggregate seat count does not validate the seat layout at its actual scale.

## Evidence and specific findings

- The opened source reports 26 objects in `Asset_elliott_hall_of_music` and 496 in `ELLT_Legacy_PreGIS_Reference_HIDDEN`. The export does not accidentally include the old axis-aligned massing collection.
- Geometry bounds confirm the exterior shell spans about 90.5 × 85.1 m and rises 22.5 m. The single glazed entry object is a one-face panel, about 2.24 × 1.54 × 3.98 m by bounds; its run/location is explicitly described as inferred in the generator. The entry route is a flat 12 m carpet quad and is not evidence of a verified lobby plan.
- The saved roof image displays many raised tile courses over a flat, broad plane. The cited architectural history establishes a red clay tile roof, but this review found no elevation evidence validating the current flat roof, 22.5 m level, tile spacing, or 33.15 m tower top.
- The exterior openings and 140-window count come from a procedural layout: the build script places narrow, 1.45 m-wide windows at regular intervals on substantial straight runs. The count is not supported by a window schedule or measured elevations. The final render shows small repeated windows, a simple box flytower, and several low-poly figures; the key entry canopy is not legible as a prominent curved entrance feature from the provided angles.
- The stage / rear / balcony renders demonstrate an assembled fan-shaped audience area with two balcony fascias, repeated seating, aisle steps, proscenium and curtains. The official current seating drawing supports the three levels, eight sections, row labels and marked accessible locations. Its diagram cannot certify this model's seat coordinates, balcony heights, aisle widths, or stair connections.
- Purdue Convocations describes north and south accessible doors with black-and-gold awnings and says there are no elevators in Elliott. The model's one inferred lower entrance and conceptual flat route do not document these two access points or prove a connected route to the marked seats.

## Priority changes for another pass

1. Add and place both north/south accessible doors and awnings from verified map/photo views; verify the Hovde bridge entry and any lower doors before labeling a door as the main entrance.
2. Use orthogonal exterior photos to refine each facade: confirm opening counts and spacing, secondary entrance surrounds, stepped side exits, sculpture group positions, curved canopy shape, and the flytower / main roof profile.
3. Find a dimensioned section / elevation or building plan. Until then, label the roof, tower, openings, auditorium section, and seating coordinates as estimates.
4. Reconcile seating rows and accessible wheelchair spaces from seat-level source data or a registered plan; build connected lobby and balcony circulation only when the plan evidence supports it.
5. Rebuild and reopen the linked master, verify all placements / paths, and refresh the manifest count for the updated 26-mesh export.

## Sources

- SAH Archipedia, building materials, curving entrance canopy, secondary entrance frames, stepped side exits, flytower, and sculptures: https://sah-archipedia.org/buildings/IN-01-157-0079
- Purdue Convocations, current accessible entrances and no-elevator guidance: https://convocations.purdue.edu/accessibility/
- Purdue Convocations, Elliott seating charts: https://convocations.purdue.edu/seating-charts/
- Purdue Convocations, official 2022 seating-map PDF: https://convocations.purdue.edu/wp-content/uploads/2022/09/Elliott-Seat-Map.pdf
- Purdue Convocations, 6,000-seat proscenium auditorium history: https://convocations.purdue.edu/elliott-hall-of-music-75th-anniversary-1940-2015/
- Purdue Archives, historical 280 × 190 ft / five-story description: https://archives.lib.purdue.edu/agents/corporate_entities/543
- Official Purdue GIS BuildingShapesZip4 FeatureServer, FID 617: https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0

## Local evidence reviewed

`modular/buildings/elliott_hall_of_music.blend`; `audit/batch3_elliott/exterior_final_reopened.png`; `exterior_finish_top.png`; `exterior_finish_southwest.png`; `from_stage.png`; `from_rear.png`; `from_balcony.png`; `seating-map-current.png`; `result_exterior_final.json`; `exterior_pass.py`; `source_inventory.json`; `seat_centers.json`.
