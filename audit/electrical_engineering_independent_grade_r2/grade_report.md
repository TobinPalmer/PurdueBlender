# Electrical Engineering independent grade, R2

**Result: 8.3/10 — PASS**
**Inspected asset SHA-256:** `535ff224bd0105389a2fea01c5542e219d48716ad6089b173a42efbe0a7b4612`
**Asset:** `modular/buildings/electrical_engineering.blend`
**Fresh-open:** Blender 5.2.3 LTS, new background process.

## Criterion scores

| Criterion | Score | Review |
| --- | ---: | --- |
| Correct identity and source-backed footprint | 1.9/2 | Purdue GIS identifies both FID 292 and FID 109 as the Brown Family Hall. Independent plate-bound checks match each source polygon's XY bounds within 0.01 m. FID 109 boundary vertices match exactly; the FID 292 maximum source-vertex to mesh-vertex distance is 0.09552 m where the courtyard boolean clips the slab. The GIS snapshot does not publish survey accuracy or source epoch. |
| Position, orientation, scale/dimensions | 1.7/2 | Geometry uses the manifest's [143.8499984741211, 135.0] m placement origin; the facade follows the documented south-facing GIS side. The asset's current collection bounds exceed the manifest's cached local bounds by up to 0.30 m on Y and 0.21 m on X. Refresh those shared bounds during master integration. |
| Evidence-backed height, floors, and roof form | 1.2/2 | Purdue's 2013 ECE emergency plan identifies basement, ground, first, second, third, and attic levels; the model has four above-grade levels. The modeled 18.5 m height is estimated. The flat roof plane and front eave do not establish the full roof form, pitch, or roof equipment. |
| Facade, entrances, and distinctive architecture | 1.6/2 | The south elevation includes source-supported brick, limestone inscription band, dark windows, three entrance portals, and red-tile eave/cornice. Bay rhythm and portal profiles are simplified, while most other elevations lack direct photographic evidence. First-floor lab and collaboration details reflect Purdue renovation photos, but the proposed plan is not an as-built plan and room locations remain uncertain. |
| Modular export, portability, and complete evidence | 1.9/2 | The fresh-open file has the expected scene and collection names, identity AssetRoot, procedural materials, and no missing external image dependencies. It contains 4,774 collection objects (4,772 meshes). Building-specific evidence and validation outputs are present. The master link itself was not graded here. |
| **Total** | **8.3/10** | **Passes the 8/10 threshold.** |

## Independent inspection

I recomputed the asset SHA before opening it in a separate Blender process and confirmed it matches the requested frozen SHA. The file opened with scene `Building_electrical_engineering` and collection `Asset_electrical_engineering`. The collection has 4,772 meshes and procedural materials; no missing external image path was found. The geometry remains inside a local frame centered on the manifest origin.

The official GIS reference snapshot is `audit/official_building_references.json`, from Purdue's BuildingShapesZip4 FeatureServer layer. The two matching features carry the same Brown Family Hall name. The model contains a slab mesh for each feature with source-aligned XY bounds. This is useful footprint evidence, though the source does not provide survey accuracy.

The exterior comparison uses Purdue ECE's 2025 building-history photograph, saved as `audit/complete_bhee/facade.jpg`. It supports the brick, limestone inscription band, grouped stone entrances, dark windows, and roof-edge treatment. Purdue ECE's 2013 Building Emergency Plan supports the floor designations. Purdue's 2024 renovation article/photos support lab and collaboration functions; its separate fundraising plan says the design is subject to change, so it cannot certify the final room layout.

## Remaining limitations

- The full roof shape, exact elevation, and mechanical equipment are not source-verified.
- Basement and upper-floor interiors, circulation, and exact as-built room positions are incomplete or uncertain.
- Facade bay spacing and unphotographed sides are modeled by repetition and estimation.
- The manifest's cached collection bounds are stale relative to this revision and should be refreshed when the asset is integrated.

Supporting outputs: `probe.py`, `probe.json`, `blender.log`, `evaluate.py`, and `result.json` in this folder.

## Sources

- [Purdue ArcGIS BuildingShapesZip4 FeatureServer](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0), features 292 and 109 (local snapshot in `audit/official_building_references.json`).
- [Purdue ECE 2025 building-history page](https://engineering.purdue.edu/ECE/News/2025/a-century-of-circuits-and-community-purdues-electrical-engineering-building-turns-100).
- [Purdue ECE Building Emergency Plan, 2013](https://engineering.purdue.edu/ECE/Safety/EE_BEP_12-3-2013.pdf) (local PDF in `audit/complete_bhee/electrical_engineering_bep.pdf`).
- [Purdue ECE 2024 renovation article](https://engineering.purdue.edu/ECE/Wavelinks/2024/articles/max-w-and-maileen-brown-family-hall-of-electrical-engineering).
- [Purdue ECE proposed first-floor renovation plan](https://engineering.purdue.edu/ECE/Giving/BHEE/BHEE_First_Floor_Renovation.pdf) (local PDF in `audit/complete_bhee/renovation.pdf`; proposal only).
