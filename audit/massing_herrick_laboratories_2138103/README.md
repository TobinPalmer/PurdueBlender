# Herrick Laboratories / Herrick Acoustics evidence

**Stable ID:** `massing_herrick_laboratories_2138103`  
**Owner:** Rossen  
**Asset:** `modular/buildings/massing_herrick_laboratories_2138103.blend`  
**Export collection:** `Asset_massing_herrick_laboratories_2138103`  
**Scene:** `Building_massing_herrick_laboratories_2138103`

## Identity

The assigned massing record is the historic original Herrick Laboratories, now identified in Purdue GIS as **Herrick Acoustics**, abbreviation `HERL`, feature `FID 246`, address 140 S Martin Jischke Drive. Purdue's facility and history pages describe it as the original 1920s horse barn converted to acoustics research. It is distinct from Ray W. Herrick Laboratories' 2013 research building, GIS `HLAB`/`FID 878`, which has its own detailed manifest asset. No geometry from the 2013 building is included here.

## Sources and model decisions

- The Purdue BuildingShapesZip4 FeatureServer layer 0 feature `FID 246` supplies the footprint in a WGS84/EPSG:4326 response. Its 67-point ring was transformed with the documented local campus approximation and near-duplicate closing vertex removed, leaving 66 structural vertices. This approximate conversion is not a surveyed coordinate system. The modeled ground shell uses that outline directly.
- The GIS record supplies `NUM_LEVELS=3` and `Extrution=36`. The service metadata does not specify the units of `Extrution`; the builder interprets 36 as feet (10.9728 m) as a plausible nominal maximum. This is an interpretation, not a measured height. The low wings are estimated at 5.2 m, with the central barn roof and cupola brought to 10.95 m overall.
- Purdue Herrick's Spring 2009 newsletter includes a historic photo before the wings and an early photo after the wings. The accompanying retrospective says the horse barn was remodeled and east/west wings added in 1957; offices were added north of the barn in 1958; the hay loft was later adapted for student offices. The newsletter itself says the date of the early post-wing photo is disputed (circa 1960 or 1980).
- A Lab Manager article published 2020-03-09 captions its photograph as the original Herrick Labs. It supports the red-brick central barn, red pitched roof, cupola, dormers, low flanking wings, long window bands, and courtyard-facing entrance. It is a secondary visual source without a capture date, dimensions, or georeferencing.
- The updated shell replaces the existing 16 m rectangular massing fallback, whose bounds were X `[-633.171,-596.100]`, Y `[-536.568,-482.791]` m. The prior model was unverified and did not conform to the official `HERL` polygon. The new wall footprint is aligned to the FID 246 geometry; facade projections extend slightly beyond that GIS line.

All raw inputs, URLs, retrieval dates, CRS, methods, and uncertainty are recorded in `sources/source_catalog.json`. The source files are retained in `sources/`.

## Current model and remaining uncertainty

The model uses the GIS U-shaped complex outline for the lower wings and crossbar. It adds an approximate raised central barn, a pitched red roof, cupola, two roof dormers, brick piers, window bands, and a courtyard entrance/canopy/sign. These central-core subdivisions and facade stations follow the historic photographs and are not surveyed. Exact wall offsets, structural footprint versus GIS outline, finished floor heights, roof construction, and the 36 ft unit interpretation remain unverified.

## Validation files

The builder script is `modular/buildings/build_massing_herrick_laboratories_2138103.py`. The saved courtyard and top-down renders are in `renders/`. A separate Blender process opens the saved library and records evaluated collection bounds, source-ring matching, modifiers, material paths, and render presence in `review/reopen_validation.json`.
