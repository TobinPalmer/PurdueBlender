# Felix Haas Hall — batch 3 source work

## Status

The standalone linked asset is saved and reopened successfully at `modular/buildings/felix_haas_hall.blend`. Its export collection is still `Asset_felix_haas_hall`; it contains 687 direct objects. The master scene and manifest were not edited in this building task. The master agent must refresh the manifest’s object list and bounds when it integrates this updated asset; the existing manifest lists several door/window/step objects that were deliberately archived or retired.

Exterior and interior QA renders were produced after the final save:

- `exterior_final.png` — overall roof, cupola and entrance elevation
- `entrance_final.png` — close exterior view of the facade, doors and corrected stairs
- `interior_plan_final.png` — top-down cutaway of the modeled first floor

## Source checks

- Official Purdue GIS building polygon: **Felix Haas Hall**, feature ID 233, code HAAS. Cached in `audit/official_building_references.json`; GIS source was retrieved 2026-10-22. Its local campus bounds are approximately 39.20 m × 52.74 m; the rotated rectangle is 52.54 m × 38.93 m at 90.41° east-counterclockwise. Source is an official campus-map polygon, not a certified survey; its height is unverified. The library’s local shell bounds remain approximately [-26.22, 12.98] m east and [-25.98, 26.76] m north. No footprint or placement-origin edit was made.
- Purdue Computer Science first-floor diagram: [HAAS Hall — First Floor](https://www.cs.purdue.edu/resources/docs/HAAS_first.pdf). Source PDF metadata identifies author Pamela Graf and creation date 2016-08-16. It names faculty and staff offices, TA spaces, a student organization room, two conference rooms, restrooms, an elevator, and three stair locations. The diagram has no scale or surveyed dimensions. It supports room adjacency and circulation only; furniture and metric registration remain estimates.
- Purdue Events exterior photo gallery: [Felix Haas Hall](https://events.purdue.edu/felix_haas_hall), reviewed 2026-10-23. It supports the light limestone and dark brick contrast, arched lower windows, central entry, broad steps, and hipped roof form qualitatively. It does not provide measured dimensions.
- Google Maps photo gallery: [Felix Haas Hall](https://www.google.com/maps/search/Felix+Haas+Hall+Purdue), reviewed 2026-10-23. A user-contributed exterior image showed the red/brown roof and brick/stone facade. Photo dates and camera geometry are not reliable measurement evidence.

## Changes in the asset

- Removed the horizontal cap faces from the GIS-derived shell so the separate hipped roof is visible. Twelve top faces were removed; the shell’s footprint walls remain. The GIS roof slab was removed.
- Added a procedural red clay roof tile shader and two hipped roof pieces. Eaves at 11.7 m, main ridge at 14.0 m, entrance ridge at 13.2 m, and the cupola alignment are image-based estimates, not measured elevations.
- Added a light limestone entrance elevation skin around three upper window openings, two lower arched windows, and a central raised doorway. Its material and placement follow the Purdue photo qualitatively; the openings and panel widths are estimated.
- Raised the entrance door to a 1.5 m floor datum and rebuilt a ten-tread approach that rises toward the entry. The stair rise and door datum are estimates from imagery. Removed three overlapping inherited step slabs and archived six superseded door/window parts in `Reference_Incompatible_Geometry_felix_haas_hall` for recovery.
- Archived the previous invented rotunda/roof-piercing interior pieces outside the export collection. Added a schematic first-floor room arrangement and estimated desks/chairs from the 2016 diagram. No upper-floor layout has been verified or modeled.

## Reopen check and remaining uncertainty

`reopen_check.json` confirms the expected export collection, 687 direct objects, unchanged local shell bounds, unit scale and zero rotation for the shell and both roofs, and the hidden reference archive. The master placement marker remains controlled by the unchanged master manifest origin.

The south/east entry elevation and complete roof are still reconstructions from qualitative photographs. The other elevations, exact window dimensions and positions, measured heights, current upper-floor plan, interior finishes, and furniture layouts remain unverified or estimated. The exterior still needs independent reviewer scoring before assigning a quality rating; this asset has not been claimed as 9/10.
