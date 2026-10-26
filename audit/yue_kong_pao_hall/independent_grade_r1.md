# Independent Yue-Kong Pao Hall R1 grade

**Score: 8.0/10 — passes the 8.0 threshold**  
**Evaluated asset SHA-256:** `b7b9c7be7abad3ad2c25588b299330ff721d81bcb47ced1ed2aa6c7d6e04378d`  
**Review date:** 2026-10-26  
**Scope:** exact frozen canonical asset, fresh Blender reopen, independent roof-slab/GIS comparison, source-photo review, and read-only master link check.

## Scorecard

| Criterion | Score | Evidence and limitations |
|---|---:|---|
| Identity and source-backed plan geometry | 1.55/2.00 | Correct match to Purdue GIS FID 72 / PAO / 552 W Wood Street. Model bounds are close to the GIS bounds. Independent comparison of the two roof-slab top faces to the transformed GIS ring yields **IoU 0.788** and **13.01 m symmetric Hausdorff distance**; roof slabs are simplified rectangles and do not capture the full irregular roof outline. Builder's 0.896 source-ring screening is not substituted for this check. |
| Campus placement, orientation, and scale | 1.45/1.50 | The asset remains in campus coordinates as required for a massing asset. Read-only master reopen confirms the relative library link and a 363-object collection. Bounds are close to the source; geographic conversion is approximate and there is no survey control. |
| Massing, floors, height, and roof | 1.15/1.50 | The lower south frontage and taller set-back north performance volume follow the official exterior photo. Asset bounds are z=-0.065 to 18.87 m. GIS reports six levels, but its height-related units are undocumented. Roof and penthouse heights are estimates; the flat roof slabs/equipment remain schematic. |
| Facade, windows, and entrances | 1.15/1.50 | South facade has Purdue red brick, repeated tall glazed bays, mullions/transoms, signage, limestone trim, and a west entry canopy that match the main cues in the official photo. Side and rear elevations are sparse/generic; exact window dimensions and other elevation details are not documented. |
| Materials and surface finish | 0.80/1.00 | Eleven assigned materials cover brick, limestone, glazing, mullions, roof, and interior surfaces. Brick uses procedural Brick Texture and Bump nodes. No image-texture dependencies are present. The finish is coherent but stylized; roof and side surfaces read flat in neutral diagnostic renders. |
| Interior and building program | 0.65/1.00 | Lobby/gallery/studio/classroom spaces, dance studio, black-box stage/acoustic room, and seating are modeled. Purdue sources support these programs, but no architectural plans were found; room distribution and geometry are representative assumptions, not verified interiors. |
| Technical integrity, portability, and evidence | 1.25/1.50 | Exact file freshly reopened in Blender 5.2.3 LTS: 363 mesh objects, 25,382 vertices, 22,839 faces, 11 used materials, zero materialless meshes, no image nodes, and no linked-library dependencies. The master loads the relative library link and same 363-object collection. Topology and as-built survey checks are absent. |
| **Total** | **8.00/10** | **Passes; remaining uncertainty is documented below.** |

## Findings

- The model is recognizable as PAO and includes substantially more than the previous one-piece extrusion: a stepped performance volume, articulated south glazing, entry, roof equipment, and program-informed interior rooms.
- I independently checked the exact candidate hash and reopened the saved `.blend`; the master file currently links that library by a relative path. As a massing asset it correctly retains campus-coordinate geometry, so no separate placement marker is expected.
- The independent roof-slab comparison is a screening metric, not a surveyed wall footprint. It highlights a real simplification: the two roof slabs are broad rectangles and diverge from the irregular GIS outline. The segmented walls and openings do not provide a single unambiguous closed wall polygon for a precise independent footprint score.
- The strongest facade evidence is the south/plaza view. Rear/side facade features, exact height, and interior room positions remain unverified or schematic.

## Evidence renders

- [South facade candidate](south_facade_candidate.png)
- [North oblique independent render](independent_grade_r1_north_oblique.png)
- [West oblique independent render](independent_grade_r1_west_oblique.png)
- [Official Purdue exterior reference](purdue_pao_reference.jpg)
- [Esri roof/context image](world_imagery_context.jpg)

## Sources

- [Purdue GIS BuildingShapesZip4, FID 72 / PAO](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/72?f=pjson) — source CRS EPSG:3857; retrieved 2026-10-25.
- [Purdue College of Liberal Arts PAO exterior photo](https://cla.purdue.edu/academic/rueffschool/theatre-and-dance/visit/images/pao-hall.jpg) — source image date not stated; retrieved 2026-10-25.
- [Purdue Theatre and Dance visit page](https://cla.purdue.edu/academic/rueffschool/theatre-and-dance/visit/index.html) — identity and address.
- [Purdue Theatre facilities brochure](https://www.cla.purdue.edu/theatre/documents/PurdueTheatreFacilities.pdf) — building program and auditorium capacities; not a floor plan.
- [Purdue Archives corporate entity record](https://archives.lib.purdue.edu/agents/corporate_entities/691) — building history/program context.
- [Esri World Imagery export](https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/export?bbox=-9675268,4927477,-9675068,4927677&bboxSR=3857&imageSR=3857&size=1200,1200&format=jpg&f=image) — image vintage not exposed by the export endpoint.

All GIS-based dimensions are approximate because the source outline is generalized and the project conversion is not survey-grade. Height and interior layout remain estimates. See the machine-readable record and evaluator for exact metrics and reproducible checks.
