# Felix Haas Hall — independent review round 6

**Asset reviewed:** `modular/buildings/felix_haas_hall.blend`, reopened independently in Blender 5.2.3 on 2026-10-23. I inspected the overall exterior, entrance close-up, all four elevation renders, the first-floor cutaway, Purdue's saved exterior photograph and CS first-floor diagram, and the continuity evidence. Reopen confirmed the expected `Asset_felix_haas_hall` collection with 1,059 direct objects. The new brick-inlay mesh has 20 faces, representing five four-sided rings. The two interior door meshes report 47 leaves and 47 frames.

**Overall: 6.9/10. It does not meet 9/10.** The inlay rings and estimated first-floor doors are additions, but the rendered model still reads as a generic brick gym with a white entrance overlay. The reference photo shows a pale stone facade integrated with conspicuous brick inlay around openings and corners. The current entrance insert is too shallow and simplified, and the surrounding building elevations retain broad brick fields with regular bright grids. Interior doors are an unverified layout inference and do not read clearly in the cutaway.

## Category scores

| Area | Score | Findings |
|---|---:|---|
| Overall massing and roof | 7/10 | The preserved envelope and large hipped roof convey the building's gymnasium form. The roof is a strong, dark red surface with a repeated tile pattern. Its profile and tile dimensions remain estimates, and the roof's faceted color variation is conspicuous in the overall render. |
| Facade and entrance | 6.5/10 | Round six adds a limestone material field and five brick rings around the two lower arches and three upper windows. These are visible in the close render, but read as thin rectangular red strokes and a separately attached white frame. Purdue's photo shows a more continuous pale facade with brick panels and bands integrated around openings and corners. The large flanking areas in the model remain dark brick with a regular white grid. |
| Texturing and materials | 6.5/10 | Brick and stone are distinct, and the roof reads as red tile. The entrance limestone appears cool gray under the current lighting rather than warm Bedford limestone. Main wall colors and grid trim are too uniform and high-contrast relative to the reference, and the ring mesh has no visible brick coursing at this scale. |
| Windows and elevations | 6/10 | All four elevations have been rendered. Repeated window bays add rhythm, but long elevations still appear schematic. Several wall/window assemblies remain overlays on the GIS shell; the evidence correctly says that this does not prove through-wall openings. East/side schedules and dimensions remain estimates. |
| Interior plan and doors | 6/10 | The top-down cutaway contains recognizable rooms, stairs, labels, and furniture, and the source plan supports room names and broad adjacencies. Round six adds 47 doors and frames, but the source plan does not show metric door widths or swings, and the modeling script places one inferred doorway at the lower edge of each room rectangle with a uniform swing orientation. The screenshot does not make these doors or a coherent route through them readily legible. Exact room dimensions, door locations, and circulation remain unverified. |
| Placement and file integrity | 8.5/10 | Independent reopen confirmed the expected linked collection and object count. The saved continuity record says GIS shell bounds/origin and roof transforms remain unchanged, the 17 entrance treads remain, and there are no exported cupola objects. These checks establish continuity, not surveyed height or facade accuracy. |
| Evidence and limitations | 8/10 | Round-six evidence identifies the qualitative photo basis, plan-derived room names/adjacencies, and estimated dimensions and door placement. The exterior and plan renders are available. The evidence does not present the guessed door positions as source-measured facts. |

## Prioritized fixes

1. **Carry the photo's material composition across the full primary facade.** Build a continuous pale limestone facade with inset brick surrounds/panels and corner detailing. The five rings are a useful directional change, but presently resemble thin red outlines around a separate entrance frame. Check the result against the reference in an orthographic view and a full-building view.
2. **Integrate the entrance into the wall.** The render shows a pale, shallow pavilion panel mounted against the brick mass. Reconcile its depth and boundary with the GIS shell and source image, and make the arch/brick/stone layers read as masonry rather than a stack of trim.
3. **Make the material comparison readable in neutral daylight.** Warm the rendered limestone response, moderate the stark white trim and deep uniform brick fields, and ensure the brick rings show coursing or credible masonry texture at the camera distance.
4. **Review the 47 interior door placements individually against the plan.** The plan establishes rooms and adjacencies, not a door at every room's lower edge or a uniform swing direction. Place estimated doors at plausible connecting openings, orient each to its actual partition, and render a close cutaway where leaves, frames, and connected circulation can be checked. Keep uncertain dimensions identified as estimates.
5. **Improve depth at facade windows and refine less-documented elevations.** Recess glazing into wall openings or clearly model jamb depth. Seek corroborating views before treating estimated side-window positions as factual.

## Evidence reviewed and limitations

- Purdue Events' [Felix Haas Hall](https://events.purdue.edu/felix_haas_hall) photo supports the qualitative pale limestone, red-brick inlay, arched openings, central entry, broad stairs, and hipped roof. The perspective image does not establish measured facade extents or side-window locations.
- Purdue CS's [HAAS first-floor plan](https://www.cs.purdue.edu/resources/docs/HAAS_first.pdf) supports first-floor room names and broad adjacencies only. It is nondimensional and does not establish door positions, widths, or swings.
- Purdue's [historical timeline](https://collections.lib.purdue.edu/timelines/puhistorical) supports the 17-step count, not tread dimensions.
- The builder's reopen and continuity records report 1,059 objects, five inlay rings, 47 estimated doors and frames, unchanged GIS envelope/origin, and no cupola in the export. My independent reopen confirmed the current file and collection. These checks do not verify estimated geometry against a measured elevation or plan.

**9/10 decision:** No. Round six adds the requested facade and interior details, but their presentation remains schematic and the defining exterior masonry pattern is not yet carried convincingly across the main facade. The first-floor door locations and swings are inferred and need individual review.

