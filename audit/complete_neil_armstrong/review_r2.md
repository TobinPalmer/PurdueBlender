# Neil Armstrong Hall source review — R2

## R2 changes

- Rechecked placement read-only against the saved master placement audit and manifest. The marker is present at `(-109.0, 400.189331, 0)`, with 0 m position error, zero rotation and unit scale. The source asset origin, scene, collection, and 444-object count remain unchanged.
- Reprojected the official Purdue BuildingShapes FID 642 ring from EPSG:3857 to the project’s local tangent plane, then translated it by the verified marker. Added this 118-vertex / 5,065.7 m² GIS outline as a thin, transparent ground-level reference plate inside the existing atrium-floor mesh. This makes the authoritative building footprint trace available in the asset without asserting that the polygon is an upper-floor plan or a wall boundary.
- The official footprint remains substantially larger than the principal shell walls: GIS bounds are 162.3 × 56.8 m; the current shell-wall bounds are 126.0 × 26.5 m. The translated overlay is in [gis_vs_shell_r2.png](gis_vs_shell_r2.png). The exact GIS polygon is now represented, but exact upper-level wall/floor geometry remains unresolved; the additional ground trace is a reference surface, not a claim that the shell is complete.
- Rebuilt the two flat red roof slabs as gently warped, tapered wing forms with 2.5 m illustrative end overhangs. Purdue’s project case history calls the roof a warped, wing-like cantilever, and the structural engineer describes an elaborate cantilevered steel roof truss. Exact curvature and dimensions remain unverified.
- Moved the two existing long atrium slabs and their rails 13 m toward the atrium center so they read as bridge crossings at the two documented atrium levels. FRP’s structural project description confirms exposed concrete bridges through the atrium at two levels, but does not publish a registered bridge plan; the centerline is schematic.

## Source and orientation checks

The official GIS layer and manifest marker are now compared in the same local coordinate frame. The marker record confirms translation, rotation, and scale, but does not independently prove building orientation against surveyed corners. The asset remains at the existing zero rotation.

Purdue’s current emergency plan describes four levels. FRP describes a three-story concrete frame, a structural-steel mechanical penthouse, a basement and partial sub-basement, three concrete stairs, and bridges at two atrium levels. Those sources support the general internal structure but do not supply the dimensioned plans needed to close the footprint or place stairs and bridges precisely. The [Purdue Archives finding aid](https://collections.lib.purdue.edu/fa/pdf/msa5_armstrong_n.pdf) records a September 2004 development-plan set in Box 348, item 5; the finding aid does not include the drawings. That archive item is the strongest next source for registering the footprint, facades, floor plates, and roof.

The 2025 Purdue College of Engineering article documents the current anamorphic LED wall inside the atrium. It says the wall is flush-mounted above a doorway and gives its display size, but the source available to this revision does not register that doorway on the model. The screen is therefore recorded in evidence, not placed by guess.

## Validation and review views

The saved source was reopened before validation and rendering. The asset still has scene `Building_neil_armstrong_hall`, collection `Asset_neil_armstrong_hall`, root origin `(0, 0, 0)`, and 444 objects. The floor footprint mesh has the GIS trace; both bridge centers reopen at local Y −12.189 m and Z 4.8/9.6 m; roof panels reopen with 238 vertices each. Temporary render cameras and lights were removed and were never saved into the library.

- Exterior: [exterior_wing_r2.png](renders_r2/exterior_wing_r2.png)
- Roof oblique: [roof_oblique_r2.png](renders_r2/roof_oblique_r2.png)
- Atrium bridge cutaway: [atrium_bridges_r2.png](renders_r2/atrium_bridges_r2.png)
- Exact footprint comparison: [gis_vs_shell_r2.png](gis_vs_shell_r2.png)
- Structured sources and revision notes: [evidence_r2.json](evidence_r2.json)
- Reopen measurements: [validation_r2.json](validation_r2.json)
- Reproducible R2 edit/render script: [revise_source_r2.py](revise_source_r2.py)

The atrium view hides facade glazing/mullions, the south atrium wall, the side south walls, roof slabs/penthouses, and skylight **only for this cutaway render**. The display capsule is the historic Apollo I command-module exhibit, but its presence in the 2026 atrium remains unverified. The 2025 LED wall is a documented current exhibit, but awaits registered wall/door location evidence.

## Remaining geometry blockers

The ground footprint trace is source-backed; the wider upper-level shell remains unbuilt. The GIS layer does not provide wall lines, room layouts, courtyard voids, or floor plates. The saved master marker confirms origin and rotation metadata but cannot resolve the shell boundary mismatch. The archival 2004 plan set is the next actionable route; until those plans or an equivalently registered survey are accessed, do not stretch the building or invent the missing wings. Roof profile and bridge centerline remain qualitative.

R2 is ready for independent grading. No master, manifest, README, shared indexes, or other building assets were edited; no commit was made.
