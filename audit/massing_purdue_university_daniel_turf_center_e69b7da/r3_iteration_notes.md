# Daniel Turf Center r3 facade-evidence iteration

## Independent r2 finding addressed

The r2 reviewer identified the facade criterion as the main remaining gap. This iteration adds only treatments visible in the attributed J&D Turf / Smart Turf exterior photograph dated 2011-06-11: pale metal siding, a long dark window band, and a centered entrance canopy. No extra window subdivisions, door shape, signage, or ornament are inferred.

## Photo-to-plan method and uncertainty

The photo has no compass heading or dimensions. The facade orientation is therefore an explicit plan-matching inference: (1) the Esri aerial export is north-up and shows the parking apron south of the building; (2) the FID 208 roof-outline ring has a centered south-side projection bump measuring approximately 4.23 m wide by 2.35 m deep; (3) the photo shows a centered entrance canopy on the long elevation. Matching the centered photo canopy to that centered plan bump assigns the photographed long elevation to the south side (negative Y); the long GIS axis is X. This is not claimed as photo georeferencing.

The source ring remains the exact plan extent. The modeled main-wall outline bridges the two rear corners of the south bump, and the centered canopy occupies the bump, preserving the source's exact outer XY bounds. The canopy and wall surfaces are simple massing geometry. Window band Z (2.30–2.80 m), canopy underside/top (2.62/2.72–3.02 m), eave (3.25 m), and ridge (4.05 m) are visual estimates with no calibration; eave and ridge remain explicitly low confidence. The raw GIS `Extrution=14` remains uninterpreted and is not used for height.

## Rebuild and validation

Rebuilt the dedicated Daniel asset with Blender 5.2.3 LTS. A clean-process reopen check records the collection/object, exact FID 208 identity, source-ring XY coverage, bounds, materials and facade mapping, manifold edges, modifiers, and external image dependencies in `reopen_validation.json`. The checks must report PASS before this revision is frozen for independent regrade.

Expected plan bounds remain X −1408.480415 to −1363.876410 m and Y 1609.488838 to 1627.129485 m; Z is 0 to 4.05 m. Expected maximum nearest-vertex error for the source ring is below 0.001 m. Plan extent/placement and identity are source-backed; facade orientation is inferred; all vertical dimensions are low-confidence visual estimates.
