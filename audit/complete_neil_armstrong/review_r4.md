# Neil Armstrong Hall targeted source search — R4

## Finding

The R3 aerial/GIS comparison establishes that the source model omits substantial portions of the connected building footprint. I searched the cited Purdue archives records, building-specific image/tour sources, structural project material, and Street View around the hall for registered plans or enough elevation evidence to add those portions faithfully. No public dimensioned as-built plans or elevations surfaced.

The strongest lead remains the September 2004 development-plan item in Purdue Archives, [MSA 5, Box 348, item 5](https://archives.lib.purdue.edu/repositories/2/archival_objects/41754). Its catalog record requires 48 hours' notice and consultation with the Flight Archivist; it offers no digital scan, sheet list, scale, dimensions, or drawings. The record's storage description is “Realia,” so the title alone does not establish that it contains a complete architectural plan set. The physical item is the next viable source, but the online catalog cannot support geometry changes.

A second Purdue archival record for Armstrong Hall (accession 2023-097) inventories a dedication program, three spiral-bound books with CDs, and newspaper printouts. The online record does not expose their contents or identify dimensioned drawings. Purdue's historic-building database page currently exposes only the application shell for this entry.

## Visual references checked

- The Purdue Engineering [360 tour](https://web.ics.purdue.edu/~iswartz/ofe/virtual/images/360-tour/arms/index.html) lists atrium, second-floor skywalk, upper-floor labs, and other interior viewpoints. It confirms visual examples of the atrium and elevated circulation but does not give a registered plan or measurements.
- Fink Roberts & Petrie's [structural project page](https://frpinc.com/projects/neil-armstrong-hall-of-engineering/) confirms three stories, a mechanical penthouse, basement/partial sub-basement, an elaborate cantilevered roof truss, two atrium bridge levels, and three stairs. Its photographs are perspectives, not elevations or plans.
- Purdue e-Archives' [2007 statue/entrance photo](https://earchives.lib.purdue.edu/digital/collection/pbuildings/id/2632/) helps identify the entrance-side facade but gives no side/rear elevation or measurable registration.
- A Google Maps Street View lookup at the hall coordinate, followed by a nearby road point, returned “No Street View imagery available here.”

## Modeling decision and exact remaining gap

No source found in R4 supports reliable floor-by-floor wing geometry, the precise courtyard boundary at each level, exterior wall heights, roof elevation/curvature, or bridge/stair coordinates. I therefore kept the Blender asset unchanged. In particular, I did not extrude the GIS polygon into a uniform shell: that would turn a ground footprint into unsupported upper-floor and atrium geometry.

The documented mismatch remains: 162.3 × 56.8 m GIS footprint versus 126.0 × 26.5 m source shell-wall bounds. R3 aerial comparison indicates the current shell mainly represents the narrow central bar and misses connected wing/depth coverage. To model those missing volumes accurately, obtain the 2004 archive item in person or get a registered current as-built floor plan/elevation from Purdue Facilities or the design team. Until then, keep the wings, upper-level courtyard openings, exact roof profile, and vertical circulation marked unresolved/schematic.

## Validation

The asset was reopened read-only in Blender 5.2.3 after the source search. It remains the R3 file: 444 objects in `Asset_neil_armstrong_hall`, root `(0, 0, 0)`, wall bounds unchanged. There were no geometry or placement writes, so the R3 GIS/orthophoto comparison remains the current plan-review plate; no new Blender render is represented as an R4 geometry result.

- [R4 research log](research_r4.json)
- [R4 validation](validation_r4.json)
- [R3 georeferenced comparison plate](gis_ortho_shell_comparison_r3.png)
