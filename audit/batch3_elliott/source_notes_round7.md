# Elliott Hall of Music — round 7 sources and change notes

Work date: 2026-10-23. Scope: Elliott modular source and evidence in this folder. The campus master, manifest, building index, and Hovde source were not edited.

## Sources

- [SAH Archipedia: Elliott Hall of Music](https://sah-archipedia.org/buildings/IN-01-157-0079) describes red brick with Indiana-limestone banding, pilasters and ornament; a curving entry canopy; stepped limestone side-exit walls; the flytower and apsidal stage projection; and two sets of three heroic allegorical sculptures. The modeled features follow those descriptions at a conceptual level. SAH does not provide the dimensions used here.
- [Purdue Convocations: Elliott 75th anniversary](https://convocations.purdue.edu/elliott-hall-of-music-75th-anniversary-1940-2015/) links construction photos and a panorama. Their pixels were not visually inspectable during this pass; no facade window schedule is claimed from them.
- [Purdue Convocations accessibility guidance](https://convocations.purdue.edu/accessibility/) documents north/south accessible entrances and step-free access guidance. It does not verify the modeled door dimensions or paths.
- [Purdue Convocations: Club Convos directions](https://convocations.purdue.edu/clubconvos/) describes the Hovde second-floor approach to Elliott's lobby. The exact shared portal and continuous accessible route remain unresolved.
- Elliott's horizontal footprint follows Purdue BuildingShapes Feature 617: https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0.

## Round 7 changes

- Added two three-figure groups because SAH describes two groups of three. Simplified poses/material, group placement on the south-facing modeled perimeter, pedestal shape, and dimensions are estimates; they are not verified reproductions of the sculpture program.
- Added two canopy meshes to suggest the SAH-described curved entry canopy above the Elliott-side upper walkway interface. Profile, exact facade location, span, and dimensions are estimates.
- Added four corner pilasters to articulate the flytower. SAH supports the flytower and limestone trim vocabulary; the corner treatment, tower dimensions, and pilaster positions are not measured.
- Rendered the linked Hovde collection only in a temporary unsaved context session at `(61.197312832, 28.344248772, 0)`. The existing Elliott-side connector is still deferred at the unverified Hovde interface. The temporary collection instance is removed before rendering Elliott's interior views.
- Interior evidence remains conceptual and cutaway. Seat layout, counts, aisles, ceiling, dimensions, and accessibility are not supported by a dimensioned plan in the available evidence.

## Reopen and scope check

Blender 5.2.3 LTS saved and reopened `modular/buildings/elliott_hall_of_music.blend`. The Elliott asset collection contains 126 mesh objects after round 7. Rendering-only context objects were not saved. No Hovde, master, or manifest data was changed.

Unverified: facade window schedule, exact sculpture and canopy placement, flytower dimensions/profile, door dimensions and clearances, continuous accessible paths, Hovde portal geometry, interior dimensions/seating/circulation, and bridge tie-in.
