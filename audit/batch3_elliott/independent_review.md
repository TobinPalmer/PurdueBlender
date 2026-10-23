# Elliott Hall of Music — independent review

Reviewed 2026-10-23 by a separate evaluator. This review inspected the saved/reopened source library, the three current interior renders, the current Purdue seating chart, the official GIS footprint, and independent real-photo references. No asset or master edits were made.

## Rating

**Overall: 5.3/10. It does not meet the requested 9/10 threshold.** The auditorium now has a convincing high-level theatre arrangement and is organized cleanly for linking. It remains a conceptual interior inside a very simple shell; key exterior architecture, circulation, and dimensional evidence are absent.

| Criterion | Score | Evidence |
|---|---:|---|
| Architectural form | 4.5/10 | The official curved auditorium footprint is retained, and the interior is oriented toward a proscenium. The 22.5 m shell and auditorium sections are generalized estimates; no measured section or elevation establishes them. |
| Exterior fidelity | 2/10 | Independent exterior renders show a nearly blank brick mass with a flat gray roof. Window openings, entry composition, limestone trim, clay-tile roof, sculptural figures, and the fly-tower treatment visible in external architectural references are absent from the 17-object export. |
| Interior layout and circulation | 6.5/10 | The model has three seating levels, eight banks, 52/21/13 rows, aisle gaps, and 5,946 seats. The current Purdue chart supports the level, section, and row structure. The builder reports an aggregate capacity of 6,005; the 59-seat difference is small, but individual row lengths and positions were estimated from an unscaled illustration. There is no lobby/backstage plan or connected vertical circulation. |
| Materials and texturing | 5.5/10 | Materials are procedural and self-contained. Brown/tan upholstery, teal balcony fronts, pale wall panels, and curtains broadly resemble the photo references. Seat cushions/backs are repeated cuboids, and the fabric, carpet, plaster, and stage finishes remain generic rather than measured or closely matched. |
| Placement and scale | 7.5/10 | The exported shell’s local XY bounds match the official FID 617 GIS envelope (about 90.5 m by 85.1 m in axis-aligned bounds). The existing master marker is at approximately [-111.0, 49.9] m, consistent with the Elliott map pin. Horizontal placement is therefore plausible. The seating plan has no scale bar, so auditorium dimensions and seat centers remain unverified; 22.5 m height is an estimate. |
| File hygiene | 8/10 | The saved library reopens and its export collection contains 17 mesh objects. Its procedural export materials have no image-texture paths. The scene also retains 496 objects in `ELLT_Legacy_PreGIS_Reference_HIDDEN`, outside the export collection; they must not be mistaken for geometry included in the master link. The manifest still lists the old 2-object export and needs refreshing during master integration. |

The overall score weights architecture, exterior, and interior quality more heavily than file organization. The seat count being within 1% of the published capacity does not validate the seat coordinates or the room’s scale.

## Independent observations

- The official Convocations chart shows three levels, sections 1–8, accessible-seat markings on the main floor, and the row-label ranges the builder used. Purdue also states that Elliott has no elevators and accessible seating is on the main floor. The model marks 12 blue seats but does not model wheelchair positions, transfer space, accessible entrances, or an actual route connecting those seats to an exterior door.
- Seat counts inferred from `seat_centers.json` are 3,490 main-floor, 1,554 first-balcony, and 902 second-balcony seats. Counts are distributed symmetrically by section (main floor: 320/405/500/520/520/500/405/320). These totals are a generated approximation; they do not trace and verify each seat symbol in Purdue’s map. The model also uses the same 4.4–5.4 m section-width range across all banks, while the chart depicts different row lengths and changing block outlines by row.
- All visible render views show repetitive, uniformly spaced seat geometry. The model includes seat backs, frames, armrests, raised platforms, several aisles, two teal balcony fascias, a proscenium, stage, curtains, wall panels, and a tiled ceiling. The views do not show the seating rows and balcony structure as a measured cross-section, and no lobby or backstage room network is present.
- A fresh exterior render from the saved source was made with an orthographic camera. It shows the current export as simple red-brick walls and a planar gray roof without visible doors or windows. The model’s `ELLT_B3_Interior_Egress_Door_Panel` pieces are panels against solid walls, not confirmed openings through the shell.
- The source scene contains 513 scene objects but just 17 in `Asset_elliott_hall_of_music`; the other 496 are in the explicitly named legacy-hidden collection and are not part of the linked asset. Since the export’s original two shell meshes have no facade openings or architectural trim, master integration will not gain those omitted legacy details automatically.

## Highest-priority work before a 9/10 claim

1. Model and verify the public exterior: facade openings and window rhythm, real entry locations, brick/limestone transitions, roof edge and tile form, sculpture, tower, and loading/service areas. Use the official footprint and current exterior views; do not promote legacy geometry without checking it against those sources.
2. Register the seating drawing to a dimensioned plan or the 2026 facilities drawing, then compare row and section seat counts and positions bank by bank. The current public seating chart is not a scaled plan.
3. Add the auditorium’s measured balcony profiles, wall/ceiling section, stairs and accessible routes. Purdue’s accessibility guidance says there are no elevators, but that does not establish a complete route layout.
4. Reconcile the source library, export collection, and manifest. Decide which existing scene objects are valid facade detail, verify them, and explicitly link approved geometry into the stable export collection; otherwise leave them archived outside the export.
5. Render exterior elevations and additional audience views after those changes, save, reopen, and refresh the master manifest before scoring again.

## Sources checked

- Purdue Convocations, current seating chart and accessibility note: https://convocations.purdue.edu/seating-charts/ (current chart file noted by the builder: https://www.purdue.edu/hallofmusic/attend-a-show/ElliottHallSeatingChart.pdf; the PDF endpoint returned 404 during this review)
- Purdue Convocations, Elliott Hall of Music 75th anniversary and 6,000-seat proscenium description: https://convocations.purdue.edu/elliott-hall-of-music-75th-anniversary-1940-2015/
- Purdue Convocations, accessibility information: https://convocations.purdue.edu/accessibility/
- Purdue 2025 facilities request citing a 60 ft ceiling: https://secure.in.gov/che/files/September-25-Commission-Meeting.pdf
- Official building polygon snapshot, `audit/official_building_references.json`, FID 617; service: https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0
- Independent auditorium photo reference: https://www.thunderhearing.com/purdue-elliott-hall
- Purdue current venue page with auditorium imagery and map iframe: https://convocations.purdue.edu/venue/elliott-hall-of-music/
- Google Maps direct search page was inaccessible to this subagent browser session; I used independently retrieved Purdue and installer photographs instead of treating the builder’s image description as verified evidence.

Local evidence reviewed: `audit/batch3_elliott/from_stage.png`, `from_rear.png`, `from_balcony.png`, `seating-map-current.png`, `result_refined.json`, `seat_centers.json`, and the saved asset `modular/buildings/elliott_hall_of_music.blend`. Additional exterior review renders are `independent_exterior_north.png`, `independent_exterior_east.png`, and `independent_exterior_south.png` in this audit folder.
