# Independent Whistler Hall regrade

**Score: 8.9 / 10 — passes the 8/10 threshold.** The earlier 7.9 score was driven chiefly by the asset's local geometry not yet being integrated under the detailed-building marker convention. That placement issue is now resolved in the master and manifest.

## Evidence checked

- Read `modular/AGENTS.md`, Whistler's source register, GIS/placement evidence, the archived official Purdue photo, and the saved exterior/top-down renders.
- Recomputed the source asset SHA-256: `CE3C33048AC70467C25317192839AD4B6290542F23024F909351EC05F84115DD`. It matches both the current library and the master fresh-open record.
- Reviewed `audit/master_integration/fresh_open_master_2026-10-26.json`: Blender 5.2.3 LTS fresh-open PASS; 91 expected and 91 actual detailed markers; no errors. Whistler uses `Placement_massing_whistler_hall_6f6bf8d` at `(-156.3101501, -497.0113831) m`, with reconstructed and manifest bounds equal (0.0 m maximum bounds error).
- Checked the FID 84 Purdue BuildingShapes feature identifying WSLR / Roy L. Whistler Hall of Agricultural Research. The documented 31-vertex ring is retained for the shell/roof perimeter. The old FID 263 match is correctly identified as Forest Products, not Whistler.

## Score breakdown

| Category | Score | Finding |
| --- | ---: | --- |
| GIS identity and source traceability | 1.0 / 1.0 | Identity matches official Purdue FID 84; raw feature, CRS notes, retrieval date, and correction of the prior FID 263 confusion are documented. |
| GIS footprint | 1.5 / 1.5 | All 31 vertices are retained. Reported local perimeter/roof and source transform agree; the area comparison is explicitly projection-adjusted and not presented as a survey. |
| Plan orientation | 1.0 / 1.0 | The footprint follows the GIS plan coordinates. The wall plan is well evidenced; exact compass-facing facade details remain uncertain from the single oblique photo. |
| Campus placement and convention | 1.5 / 1.5 | The manifest now classifies the asset as detailed and places its local geometry through the marker at the documented GIS-derived origin. Fresh-open reconstructed bounds match manifest bounds exactly. |
| Height and levels | 0.6 / 1.0 | Four above-grade levels are supported by GIS attributes. Parapet and gable heights remain estimates, not surveyed elevations. |
| Exterior architecture | 1.1 / 1.5 | The model captures the visible red-brown masonry, pale horizontal courses, grouped glazing, upper window band, and raised gable. Window grouping, pier rhythm, and the facade's GIS side are simplified or inferred. |
| Materials | 0.8 / 1.0 | Procedural masonry, concrete, glazing, and roof materials are portable and visually coherent. Brick texture reads subtly at the saved render scale. |
| Interior and use evidence | 0.6 / 0.75 | Schematic laboratory benches and slabs fit Purdue's documented lab use and are correctly labeled as non-plan geometry. Actual room layout is unverified. |
| Portability and saved-file validation | 0.75 / 0.75 | The library reports procedural assets only, its expected SHA matches, and both asset and integrated master fresh-open checks pass. |
| **Total** | **8.85 / 10 (8.9 rounded)** | **Pass** |

## Remaining accuracy limits

No blocking revisions remain for the 8/10 threshold. Height, exact facade-side assignment, window schedule, entrance details, and room layout are still estimates or schematic because the available Purdue photo is a single non-georeferenced 2015 winter view and the research sources establish use rather than plans. Higher fidelity would need a georeferenced elevation/photo set or surveyed elevations and floor plans.
