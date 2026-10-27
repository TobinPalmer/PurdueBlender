# Horticulture Building asset review packet

**Assignment:** Rossen
**Stable ID:** `horticulture_building`
**Asset:** `modular/buildings/horticulture_building.blend`
**Export collection:** `Asset_horticulture_building`
**GIS feature:** Purdue Campus GIS BuildingShapesZip4 layer 0, FID 232

## Source-backed geometry and orientation

The official GIS outline was transformed to the project frame (meters; X east, Y north, Z up) and centered at `(-61.8249448797, -630.9233290000)`. The 14-point structural shell matches all source vertices with a maximum nearest-vertex difference of `0.00001 m` after serialization. The local geographic transform is an approximation; the GIS service gives no survey tolerance or source date. Campus placement remains controlled by the existing master marker, which this task did not edit.

The official north-up Purdue campus map places HORT east of Agriculture Mall. Purdue’s Agriculture Mall article independently describes green strips between Nelson/Whistler to the west and Horticulture/Forestry to the east. The official building photo shows planted green space in the foreground. Together these sources support registering that photographed principal elevation to the west-facing GIS edge. The exact door offset along the facade remains estimated.

## Facade and entry revision

The west facade now has tall narrow sash windows and a source-matched central single-pair-single group on both upper rows, with the flanking window rhythm continued outward. The doorway bay remains open at grade. Fine horizontal brick bed joints, shallow pilasters, and the pale foundation follow the photo. The stone portal is centered and shallow; the lettering fits within its stone block, and the balcony rail sits directly above the portal beneath the upper sash. Unsupported canopy and freestanding piers remain removed. Fine dimensions and bay spacing are photo-based estimates.

## Height and vertical field conflict

The BuildingShapes layer metadata reports `verticalSpatialReference: null` and does not document units or meanings for the custom vertical fields. `F02=11.7`, `F03=23.4`, and `R=35.1` form 11.7-unit intervals. The nearby Purdue Airport field elevation is about 606 ft, making GIS `Elevation=615.9` plausible as feet, but this is only a unit plausibility check and does not prove the building fields use feet.

Under that feet hypothesis, `R=35.1` gives a best-estimate roof height of `10.70 m`; `Extrution=48` gives a conditional upper scenario of `14.63 m`. The model uses the roof field for its three visible levels and retains `10.70–14.63 m` as a conditional range, not a verified bound. `NUM_LEVELS=5` and `CountOfFLO=5` conflict with the three visible window levels; they may count basement/ground levels, but that interpretation is not verified. Height is not surveyed.

## Reopen validation

Blender 5.2.3 reopened the saved `.blend`. Stable ID/FID, local origin, shell-to-GIS vertex correspondence, and the `10.70 m` modeled height were verified. The asset has 39 objects, no external image paths, and all materials connect to output. SHA-256 and machine-readable measurements are in `reopen_validation.json`.

## Candidate files for r3 grading

- Builder: `modular/buildings/build_horticulture_building.py`
- Saved asset: `modular/buildings/horticulture_building.blend`
- GIS snapshot and layer metadata: `sources/purdue_gis_fid232.json`, `sources/purdue_buildingshapes_layer_metadata.json`
- Official photo and capture: `sources/purdue_events_exterior.jpg`, `sources/purdue_events_horticulture_building.html`
- Campus map and Agriculture Mall context: `sources/purdue_campus_map.pdf`, `sources/purdue_agriculture_mall_context.html`
- Exterior, top, and entry renders: `renders/horticulture_exterior.png`, `renders/horticulture_top.png`, `renders/horticulture_entry.png`
- Reopen validator/results: `reopen_validate.py`, `reopen_validation.json`
- Structured evidence: `evidence.json`

The asset and evidence are frozen at this revision for independent r3 review.

## Independent completion grade

Round 3 independently passed at **8.3/10** against frozen SHA-256 `20aed83e827c75d57c12e7dfc417bc6d1e4ccaebf5336b4e96c6121e13297cb7`. Result: `independent_grade_r3/result.json`. The asset itself was not resaved after grading. Its historical metadata phrase "upper bound" is conditional on the feet hypothesis; 14.63 m is not a verified limit. Tobin master validation remains pending.
