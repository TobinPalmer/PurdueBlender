# Elliott Hall of Music — round 6 source and change notes

Work date: 2026-10-23. Scope remains Elliott's modular asset plus evidence in this folder. The campus master, manifest, building index, and Hovde asset were not edited.

## Sources

- SAH Archipedia describes Elliott's red brick, Indiana-limestone banding/pilasters, tile roof, and second-story Hovde-to-Elliott route: https://sah-archipedia.org/buildings/IN-01-157-0079. The reviewer could not retrieve this page directly in round 5; these features are used as source-described types only. The modeled schedules and dimensions remain estimated.
- Purdue Convocations' access guidance supports north/south black-and-gold awnings and step-free access to main-floor seats: https://convocations.purdue.edu/accessibility/.
- Purdue's Club Convos directions describe the Hovde second-floor approach to Elliott's main lobby: https://convocations.purdue.edu/clubconvos/. Purdue pages differ on the named Hovde approach corner; the location is unresolved and no Hovde-side portal is claimed.
- Purdue Convocations links construction images/panorama, but image pixels were not inspectable in this workflow. No window count or placement was inferred from them: https://convocations.purdue.edu/elliott-hall-of-music-75th-anniversary-1940-2015/.
- Horizontal shell remains Purdue BuildingShapes Feature ID 617 (188-point outline): https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0.

## Round 6 changes

- Rebuilt the four limestone belt courses as continuous full-edge extruded bands along the footprint. Round 5's bands were malformed point-level fragments; this fixes their geometry and makes them read as horizontal facade courses. 0.56 m face height, 0.50 m projection, and levels 4.9/9.8/14.7/19.6 m are still illustrative estimates.
- Reworked the red-brick material as a staggered, UV-mapped brick/mortar pattern with shallow bump. UVs run along each shell edge and up the wall so the courses remain horizontal around the curved footprint. Nominal 0.25 x 0.07 m brick dimensions and color/bond are material estimates, not a verified specification.
- Corrected the view evidence. `interior_round6.png` is a camera placed inside the auditorium at the stage end and aimed across the seating; `interior_plan_round6.png` is an overhead seating/aisle view. Exterior shell, exterior detail, roof and ceiling objects are hidden for these renders only; their original visibility is restored and the asset is saved/reopened without render-only hiding.
- Repositioned the temporary Hovde pending label onto the Elliott-side landing and aligned it across the landing width for legibility. The physical gap remains visible. This review marker is not an architectural sign and should be removed after the Hovde portal is modeled and checked jointly.
- The Elliott connector still ends before the estimated Hovde wall. The Hovde-side opening is unresolved. No building or master connection is claimed.

## Saved asset and limits

Blender 5.2.3 LTS saved and reopened `modular/buildings/elliott_hall_of_music.blend`; `Asset_elliott_hall_of_music` contains 78 mesh objects. Rounds 5's five shell-opening ray checks remain applicable because the shell was not altered in round 6. They only sample the current mesh at opening centers and do not validate actual locations, sizes, door clearance, or routes.

Still unverified: window count/layout, exact masonry/limestone schedule, door positions/dimensions, bridge/portal site tie-in, interior plan dimensions and circulation, seat count/spacing, and vertical dimensions. No 9/10 score is claimed.
