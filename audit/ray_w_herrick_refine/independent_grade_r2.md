# Independent grade — Ray W. Herrick Laboratories R2

**Result: 8.1/10 — passes the 8.0/10 threshold.**  
**Candidate SHA-256:** `5dfe15ad317dad3661fab756b312e2d0ce2de9b64b53bb3ecb0523a93525bbbf`  
**Fresh reopen:** Blender 5.2.3 LTS, 80 objects in `Asset_ray_w_herrick_laboratories`, 68 meshes, 17 used materials; no materialless meshes, invalid material references, external image dependencies, or linked libraries.

R2 is a substantial improvement over the previous 7.2/10 model. It represents the 2013 HLAB building (Purdue GIS FID 878), not the separate historic Herrick Acoustics / HERL (FID 246). The south entry orientation is supported by Purdue visitor information. The distinct office/living-lab glazing, brick-and-metal office frontage, and dark high-bay are recognizable against Purdue’s 2013 photograph and the 2011–12 annual-report elevations. The model remains schematic in roof construction and interior detail.

## Scorecard

| Criterion | Score | Findings |
|---|---:|---|
| Identity, GIS footprint, and plan | 1.85/2.0 | The candidate’s 58-point raised-foundation loop has a maximum symmetric source-vertex-to-boundary distance of 0.197 m against the raw Purdue FID 878 polygon, within the stated 0.25 m simplification tolerance. Candidate area is 2,593.797 m² versus 2,588.772 m² for the transformed raw ring (5.025 m², about 0.19%). This is a comparison to the same GIS footprint used to author the candidate, not an independent wall survey. |
| Local frame and placement basis | 1.35/1.5 | The geometry is in a local coordinate frame, preserves the documented campus origin, and places the entry on the south side as Purdue states. The master placement marker and neighboring campus alignment were not part of this standalone review. |
| Exterior form and roof | 1.45/2.0 | The three-storey office/lab mass, glazed living-lab wing, and distinct high-bay volume read as HLAB. The roof is still a broad flat cap. Purdue’s design elevations and 2013 image show a more articulated high-level glazed/steel monitor or canopy condition; the model’s roof vents and equipment remain schematic. |
| Facade, entrance, and materials | 1.65/2.0 | R2 replaces the plain prism with punched facade panels, brick piers, pale metal spandrels, a dark high-bay face, framed glazing, and a south-facing entry. Procedural materials give the major materials clear separation. Window rhythm and facade module dimensions are simplified; the entrance, canopy, and site planting remain small schematic cues rather than a photo-level match. |
| Interior and laboratory use | 1.0/1.5 | The candidate contains three schematic floor plates, a connected corridor/stair/elevator cue, partitions, work surfaces, and lab/test-rig silhouettes. The published floor diagrams support broad use zones, but the modeled room divisions and equipment placement are interpretive. The supplied exterior renders do not show an interior cutaway. |
| Saved asset, evidence, and portability | 0.8/1.0 | The exact candidate hash independently reopened; the 80-object building collection has 17 used materials, no materialless meshes, invalid material slots, external images, or linked libraries. The four preview objects (camera, lights, ground) are outside the building collection. There is no dedicated root object, so the coordinator should confirm the linked collection’s origin and master marker during integration. |
| **Total** | **8.1/10** | **Pass.** |

## Required coordinator checks before integration

1. Confirm the existing `Placement_ray_w_herrick_laboratories` marker matches the manifest origin and inspect its neighbors in the master.
2. Keep the four preview-stage objects outside the linked building collection; they are currently outside it.
3. Preserve the documented distinction from the adjacent historic HERL building.
4. Retain the uncertainty labels for roof profile, room partitions, equipment layout, and GIS-to-wall registration.

## Evidence and limits

- Purdue’s 2013 opening article identifies the 68,000-square-foot 2013 building and describes the living-laboratory office wing: [Purdue News Service](https://www.purdue.edu/newsroom/archive/releases/2013/Q4/purdues-new-herrick-labs-building-open-for-business.html).
- Purdue visitor information says HLAB’s main entrance faces south and identifies the 177 South Russell Street address: [Visit Herrick Labs](https://engineering.purdue.edu/Herrick/AnnualReport/information/visit).
- The published 2011–12 annual-report page includes south/east design elevations and first-, second-, and third-floor diagrams. It is design-stage, not proof of final as-built construction: [Herrick Laboratories annual report PDF](https://engineering.purdue.edu/Herrick/information/AnnualReports/2012%20fall.pdf).
- The exterior photographic reference is Purdue’s 2013 image, accessed through the opening article: [Purdue Herrick Labs exterior photo](https://www.purdue.edu/uns/images/2013/herrick-newbuilding.jpg).
- GIS measurements use Purdue BuildingShapesZip4 layer 0, FID 878, retrieved 2026-10-22. The source date/tolerance are not supplied; the project’s local-meter conversion and 0.25 m simplification are approximate. The candidate was authored from the same outline.
- Independent reopen and geometry audit: `independent_reopen_r2.json` and `independent_reopen_r2.py`.
- Candidate views inspected: `preview_r2.png` and `south_r2.png`.

This grade applies to the isolated candidate only. It does not verify the master placement marker or neighborhood composition.
