# Alpha Epsilon Pi — evidence and modeling record

## Identity and footprint

Purdue BoilerLink currently lists the Alpha Epsilon Pi chapter at **1051 David Ross Road**: <https://boilerlink.purdue.edu/organization/aepi> (retrieved 2026-10-26). Purdue's BuildingShapesZip4 GIS feature for that address is **FID 754**, whose `ADDRESS` field is `1051 David Ross Rd`, but whose `BUILDING_N` field says **Chi Phi**. The conflict remains unresolved in the university GIS naming field. The 1051 address feature's polygon encloses the roof visible in the Esri World Imagery tile; the vertex overlay is saved as [satellite_footprint_overlay.png](satellite_footprint_overlay.png).

These sources serve different purposes: BoilerLink is current official evidence for the chapter's listed address; the FID 754 GIS address plus imagery overlay support the physical address-to-roof match; and the Wikimedia Commons image, retrieved 2026-10-26 and dated 2009-10-26, is historical Purdue AEPi facade evidence only. No recent direct chapter photograph was found to prove current occupancy or explain why Purdue GIS calls FID 754 “Chi Phi.” The current-address match is therefore documented as a supported but still qualified crosswalk, not a resolved GIS name correction.

The assignment's FID **821** is a separate candidate at **116 Fowler Ave.**, about 2.4 km southeast. It is named Alpha Epsilon Pi in GIS, but Purdue BoilerLink gives the current address as 1051 David Ross Road. Its own imagery overlay is [fid821_satellite_overlay.png](fid821_satellite_overlay.png). FID 821 is recorded as a possible legacy mapping and is not used for this current-house asset. A third-party listing calls 116 W Fowler apartments, but that source is not treated as proof of a historical chapter move.

OSM/Nominatim geocodes “1051 David Ross Road” to 40.4350240, -86.9251902, roughly 116 m from the FID 754 polygon centroid and near the 951 David Ross feature. That point was rejected for building geometry; the official GIS shape plus its imagery overlay is the spatial match used here. This is a geocoder discrepancy, not a measured address entrance.

## GIS geometry and placement

Raw features FID 754 and 821 are preserved in [purdue_gis_features_fid754_821.json](purdue_gis_features_fid754_821.json) in WGS 84 / EPSG:4326. The building polygon has 60 unique vertices. For the project local frame, coordinates use the documented local tangent approximation:

- `X = (longitude + 86.9137) × 111412.84 × cos(radians(40.4274))`
- `Y = (latitude - 40.4274) × 111040`

The FID 754 polygon centroid is approximately **40.4360392, -86.9248873**, giving parent placement origin **[-948.801726, 959.296980] m**. The local footprint bounds are approximately 31.34 × 35.00 m. Transform values and footprint area/perimeter are approximate, not survey-grade. The source `Shape__Area` and `Shape__Length` values do not numerically agree with metrics computed after the documented local conversion; source field units/scaling are unknown and are not used for metric dimensions.

The Esri World Imagery tile source is <https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer>. The tile response did not expose a capture date. The capture date of the public-domain exterior photo is 2009-10-26; it shows a three-story brick house with Greek letters, projecting bay windows and window AC units beneath a dark shingled mansard roof: <https://commons.wikimedia.org/wiki/File:PurdueAEPIhouse.jpg>. JNS republishes the same credited image: <https://www.jns.org/jewish-youth-promise-surpasses-10k-aepi-30k-total-signatures/>. It is historical evidence, not a current condition survey.

## Model detail and estimates

The exterior wall outline follows the 60-vertex official FID 754 ring. The 2009 photo supports the red brick, three visible stories, mansard shingles, bay windows, AC units and Greek-letter sign. Story heights, eave/break/cap elevations, exact window rhythm, entry canopy and steps, chimney, and shrubs are modeled estimates. The brick uses a running-bond shader mapped through a wall-specific UV layer in meters, with course height following Z and brick length following the measured perimeter; mortar relief is kept shallow so courses remain legible at the saved street-scale view. Roof offsets are generated from the footprint and triangulated without changing the master campus placement.

After the independent 7.80/10 review, the brick material was corrected to use the actual wall UV output (the prior node lookup silently missed the Brick Texture node), wall vertices were shared at GIS corners for smoother transitions, the side-window threshold was lowered for more complete facade coverage, and entry shrubs were reshaped as fuller rounded plants. The updated comparable exterior is [alpha_epsilon_pi_exterior_revision_7_8.png](previews/alpha_epsilon_pi_exterior_revision_7_8.png); the current canonical preview is [alpha_epsilon_pi_exterior.png](previews/alpha_epsilon_pi_exterior.png).

The modeled entry lobby, common lounge, dining space, kitchen, stair, upper shared halls and bedrooms form a representative fraternity-house interior. No public floor plan or verifiable interior photo was found. Room count, internal walls, furniture and room positions are illustrative and must not be read as measured conditions.

## Fresh-open validation and files

The standalone file was reopened in a separate Blender process and validated by [validate_asset.py](validate_asset.py). See [validation.json](validation.json) for scene/collection names, object/material counts, local bounds, parent relationships, external image checks and roof triangle counts. Preview renders are [exterior](previews/alpha_epsilon_pi_exterior.png) and [interior cutaway](previews/alpha_epsilon_pi_interior.png).

The stable asset output is `modular/buildings/alpha_epsilon_pi.blend`, scene `Building_alpha_epsilon_pi`, collection `Asset_alpha_epsilon_pi`. Shared README, manifest, verification, master blend, and Git history remain coordinator-owned.
