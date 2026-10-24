# Independent Review — John T. McCutcheon Residence Hall R4

**Review date:** 2026-10-24  
**Reviewed asset:** `modular/buildings/mccutcheon_hall.blend`  
**Grade:** **8.05/10 (8.1 displayed) — meets the 8.0 threshold.**  
**Scope:** Independent read-only review of the reopened R4 asset, evidence, LiDAR calculation, validation, and R4 hero/entrance renders. No McCutcheon, master, or shared files were edited or saved.

## Criterion scores

| Project criterion | Score | Evidence and deduction |
|---|---:|---|
| Correct identity and source-backed footprint | 1.90/2.00 | Purdue identifies McCutcheon Hall, and the saved building plinth bounds agree with the transformed Purdue GIS FID 57 envelope to under 0.0001 m at recorded precision. This is a useful source registration, but the project-local conversion is approximate and an AABB match does not validate every wall segment. |
| Position, orientation, and scale/dimensions | 1.60/2.00 | The asset root remains at the expected identity transform and the local footprint is aligned to FID 57. No master marker was checked; the projection is not survey control, and the facade heading/complete structural outline are not independently measured. |
| Evidence-backed height, floors, and roof form | 1.30/2.00 | **R4 receives clear credit** for removing 16 unsupported rooftop penthouse components and lowering the tower roof edge from the previously modeled 30.35 m to 27.72 m. The LiDAR candidate distribution has p95 25.93 m, p99.9 26.09 m, and maximum 26.16 m above nearby ground; no candidate returns are at or above 27 m. Indiana Commission for Higher Education records support eight renovation floors in each tower. **Remaining deductions:** the roof edge is still about 1.56 m above the candidate maximum, existing HVAC fans bring the model to 28.50 m, no building-class returns (class 6) were present, candidates are class-1 unclassified, and the point-cloud metadata reports vertical accuracy as N/A. These readings make removing the much taller penthouse reasonable, but do not prove an exact roof height or absence of all roof enclosures. Floor count does not verify floor spacing or parapet elevation. |
| Facade, entrances, and distinctive architecture | 1.45/2.00 | Purdue's official residence-hall exterior image supports the brick, blue-gray glazing, perforated concrete screen, low glazed entrance, light base, name sign, and some rooftop equipment, all represented in the model. The image is cropped, oblique, undated, unscaled, and direction-unidentified; it cannot establish exact facade position, dimensions, or openings on the blank elevations. R4 did not change the facade. |
| Modular export, portability, and complete evidence | 1.80/2.00 | Blender 5.2.3 independently reopened the asset with the expected `Asset_mccutcheon_hall` collection (one direct root, 219 child-inclusive objects), root at origin/unit scale, and a 28.50 m maximum caused by existing HVAC. R4 validation records the 27.72 m roof edge separately, 16 removed penthouse objects, retained parapets/coping, ten packed foliage images, no unresolved unpacked textures, and two renders. The relative foliage-library link resolves in the project. Deducted because master placement/integration and interior circulation remain unverified. |

**Total:** 8.05/10 (8.1 when displayed to one decimal). The score is a reviewer judgment based on available evidence, not a claim of survey accuracy.

## LiDAR and penthouse assessment

R4's penthouse removal is supported as a cautious correction. The analysis used the official Purdue GIS FID 57 polygon, transformed into the USGS LiDAR tile's NAD83(HARN) / Indiana West (ftUS) coordinate system. It selected returns at least 15 m above the local ground baseline inside the footprint. Candidate surface p95 is 25.929 m, p99.9 is 26.092 m, and maximum is 26.161 m above the nearby class-2 ground median. The analysis found no candidate returns at or above 27 m. Relative to the old 30.35 m penthouse, the R4 roofline is materially closer to those returns and the tall brick penthouses no longer dominate the model silhouette.

These are useful height clues with important limits. The tile contains **no class-6 building returns**, so the selected 11,588 returns are class-1 unclassified. They may include vegetation and may omit building points. The USGS product metadata lists vertical accuracy as **N/A**; the point cloud was acquired in 2017–2018 and the local terrain baseline uses nearby ground points. Consequently, the p95/max values are not a certified building roof elevation or a rigorous bound. The current tower roof edge at 27.72 m remains 1.56 m above the candidate maximum, and HVAC fans remain at 28.50 m; neither is resolved by a roof plan or measured elevation. R4 appropriately keeps these caveats rather than claiming the new roof heights are surveyed.

## Other remaining limits

- Eight renovation floors per tower are supported by 2014/2015 Indiana CHE agenda documents, but those records do not measure floor-to-floor heights or the total roof elevation.
- The official exterior photograph is useful for broad feature categories but cannot orient the photographed facade or register the entry/screen and window schedule to the GIS boundary.
- The residence-hall interior remains a simplified, unverified shell. No as-built floor plans or current circulation/elevator source was supplied in R4.
- The standalone asset passed its validation, but this review did not check its placement marker in the campus master.

## Sources reviewed

- [USGS 3DEP LiDAR metadata](https://thor-f5.er.usgs.gov/ngtoc/metadata/waf/elevation/lidar_point_cloud/laz/IN_Statewide_Opt2_B2_2017/USGS_LPC_IN_Indiana_Statewide_LiDAR_2017_B17_in2018_29951885_12.xml) and [tile download](https://rockyweb.usgs.gov/vdelivery/Datasets/Staged/Elevation/LPC/Projects/IN_Indiana_Statewide_LiDAR_2017_B17/IN_Statewide_Opt2_B2_2017/LAZ/USGS_LPC_IN_Indiana_Statewide_LiDAR_2017_B17_in2018_29951885_12.laz); analysis, classification counts, quantiles, and limits recorded in `mccutcheon_r4_lidar_height.json`.
- [Indiana Commission for Higher Education, November 2014 agenda](https://www.in.gov/dA/a0641c5d3d/November_2014_CHE_Agenda.pdf?language_id=1) and [September 2015 agenda](https://www.in.gov/che/files/Sept_2015_Commission_Meeting_Agenda.pdf); renovation descriptions identify floors 1–8 for north and south towers, respectively.
- [Purdue Residences — McCutcheon](https://www.housing.purdue.edu/my-housing/options/residence-halls/mccutcheon.html) and [official exterior photo page](https://www.housing.purdue.edu/visit/conferences/accommodations.html); qualitative feature reference only.
- Saved asset and R4 evidence/validation: `mccutcheon_r4_evidence.json`, `mccutcheon_r4_validation.json`, `mccutcheon_r4_hero.png`, and `mccutcheon_r4_entrance.png`.

**Decision:** R4 clears 8.0 because it replaces a notably unsupported penthouse mass with a roof form closer to the available LiDAR surface distribution and documents eight tower floors. Height/roof certainty remains limited by unclassified returns and missing vertical accuracy metadata; the residual roof/HVAC maxima are not verified. No master placement or interior accuracy is claimed.
