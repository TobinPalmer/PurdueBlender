# CL50 batch 4 refinement notes — 2026-10-23

Asset: `modular/buildings/class_of_1950.blend`; collection `Asset_class_of_1950`. Only this standalone asset and `audit/batch4_cl50` were edited. `CL50_Root` remains at `(-115.19, -116.95, 0)` with unit scale and zero rotation; the source GIS wall envelope and roof bounds match the batch-start copy exactly. The canonical master and manifest were not edited.

## Sources checked

- Official 2024 Purdue Road School floor plan: <https://www.roadschool.purdue.edu/maps/2024%20Class%20of%201950%20Lecture%20Hall.pdf>. The one-page diagram supports room organization and the main auditorium identity; it has no scale, so registration and dimensions remain approximate.
- Purdue Libraries exterior photo: <https://collections.lib.purdue.edu/campus/images/buildings/195-class-of-1950-lecture-hall.jpeg>. The image shows red brick arcade columns, pale stone bases/capitals, a pale curved soffit band, and the broad curved glazing. The photo's capture date is not supplied. Local review copy: `purdue_archive_exterior_reference.jpg`.
- Purdue Admissions visit page: <https://ontour.admissions.purdue.edu/daily-visits/>. Search snippet available on 2026-10-23 identifies CL50 as a preferred 470-seat venue. Direct page fetch timed out; treat 470 as a current public listing, not an on-site seat inventory.
- Google Maps: <https://www.google.com/maps/place/Class+of+1950+Lecture+Hall/@40.4263482,-86.9150559,17z>. Opened 2026-10-23. Satellite view rendered with imagery credits to Airbus/CNES and Maxar; the visible map attribution says 2026 but gives no imagery capture date. Street View imagery/date was not opened or verified. This view is contextual only and was not used to infer facade detail.

## Changes this pass

- Enlarged each of the seven image-visible brick arcade shafts by 20%, added dressed pale-stone plinths, enlarged pale capitals, and inserted a segmented pale curved soffit tied to the shaft line. These dimensions are image-derived estimates, not surveyed dimensions.
- Changed the modeled auditorium seat count from 480 to 470, matching the public preferred-capacity listing while retaining the existing twenty row platforms and 480 supporting tier segments.
- Left GIS shell and roof mesh, FID230/local root, auditorium tier supports, material assignments, and master placement unchanged.

## Reopen and render checks

`reopen_check.json` records a successful reopen from the saved file, unchanged root transform/GIS shell/roof bounds, 470 auditorium seat meshes, 480 tier segments, and no unmaterialed meshes. Render files: `exterior.png`, `interior.png`, `cutaway.png`. The roof/penthouse height, all vertical measurements, plan-to-shell registration, door/stair details, and current Google imagery capture date remain uncertain. Master placement and neighborhood context still need the orchestrator's review.
