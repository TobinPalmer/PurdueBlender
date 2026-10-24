# Life Science Plant and Soils Laboratory — Independent Review R2

**Score: 6.7/10 — below the 8/10 finish threshold.**

| Category | Score |
| --- | ---: |
| Identity and footprint | 1.8/2.0 |
| Placement, orientation, and scale | 1.0/2.0 |
| Height, floors, and roof evidence | 1.1/1.5 |
| Exterior and materials | 1.0/2.0 |
| Interior, program, and circulation | 0.9/1.5 |
| Technical portability and evidence | 0.9/1.0 |
| **Total** | **6.7/10** |

## Findings

- **Identity and footprint:** The Purdue BuildingShapes feature 917 is named for the correct building. R2 replaces rectangular slabs with extrusions of the feature’s 12-vertex ring; validation reports all four floor slabs within 0.000001 m of the transformed GIS vertices. This verifies reproduction of the selected GIS plan geometry, not surveyed as-built walls. The project uses an approximate local geographic conversion and the selected ring contains no interior courtyard.
- **Placement, orientation, and scale:** The evidence recommends master marker XY `(-426.819, -466.398)` from the transformed feature bounds, but this review did not verify the current master marker against the manifest or independent ground control. Orientation and campus-scale error therefore remain unverified; exact local slab-to-ring agreement does not establish campus registration.
- **Height, floors, and roof:** The feature records four levels and an extrusion value of 36, interpreted as feet to model a 10.97 m main wall. The GIS schema’s extrusion semantics are not documented, so height is an estimate. The render shows a broad, simple flat-roof mass with a raised central volume; roof form and equipment are not independently verified.
- **Exterior and materials:** The August 2019 Street View reference supports broad red-brown brick, gray/glazed volumes, and a narrow glazed bay. The model has repeated window bays, running-bond procedural brick, and separate concrete/glazing materials. The comparison is uncalibrated and historical. The supplied west render reads as a simplified, flat facade with uniform window rhythm and little entrance depth; it does not establish the facade’s measured bay spacing or the other elevations.
- **Interior, program, and circulation:** R2 contains 15 sample dryers and four soil-grinding units with dust arresters, matching counts in the cited 2021 Agronomy report. The report does not establish their modeled room positions; the builder explicitly labels those positions illustrative. The interior preview shows equipment on a large open slab but does not demonstrate source-verified room partitions, circulation, or the reported cold-storage rooms.
- **Technical portability and evidence:** The R2 validator reports a successful reopen, 521 exported objects / 519 meshes, 77 interior objects, and no unpacked external image dependencies. The validation JSON reports 14 unique materials, while the adjacent evidence JSON still says 10, so that summary count is stale or inconsistent. The preview set is useful for checking the current simplified exterior and schematic equipment but is not a substitute for source plans or registration evidence.

## Source and uncertainty boundary

The main geometry source is Purdue University’s BuildingShapesZip4 FeatureServer, layer 0, feature 917, retrieved 2026-10-24; the snapshot and transformation are documented in `audit/batchC_life_science_plant_soils_official_footprint.json` and `audit/batchC_life_science_plant_soils_evidence.json`. Purdue’s 2021 Department of Agronomy five-year report supports the equipment counts, not the equipment locations. The Google Street View citation is dated August 2019 and explicitly qualitative; no calibrated facade measurements, current floor plans, or independent campus placement check were supplied for this review.

**Disposition:** keep In progress. The exact transformed GIS floorplates and successful asset reopen are meaningful improvements, but unverified placement, estimated height/roof, generic exterior treatment, and schematic interior layout keep this revision below 8/10.
