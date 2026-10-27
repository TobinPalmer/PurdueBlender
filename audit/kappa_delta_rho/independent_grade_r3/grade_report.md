# Independent Kappa Delta Rho Grade — Round 3

**Asset reviewed:** `modular/buildings/massing_house_1089876362_14ecd2c.blend`  
**SHA-256 verified before grading:** `b6adaf3369e04593b2b65ea6d5b62c470076c1f913a6f7ae36e6439534488567`  
**Result:** **8.4/10 — passes the 8.0 project threshold**  
**Review date:** 2026-10-26  
**Review method:** Read-only open in Blender 5.2.3, topology and fresh-open report review, visual comparison of the current exterior/interior previews against the identified NPS Photo 37, GIS record, and 2023 orthophoto.

## Rubric

| Category | Score | Evidence and limits |
| --- | ---: | --- |
| Identity and source attribution | 1.50 / 1.50 | Purdue BuildingShapesZip4 FID 801 identifies Kappa Delta Rho at 1134 Northwestern Avenue. The NPS Photo 37 caption independently identifies “Kappa Delta Rho, Northwestern Ave, N,” names Jane Evans, states June 2001, and says the view faces southeast. The address/identity is specific; Kappa Delta Sorority imagery is not substituted. |
| Footprint, placement, and orientation | 2.00 / 2.00 | The fresh-open evidence compares all 20 GIS ring vertices with the model base: maximum nearest-vertex error 0.0000567 m and RMS 0.0000322 m under the documented campus conversion. The 2023 orthophoto overlay corroborates the parcel/roof plan. This checks the footprint and transform, not height. |
| Massing and roof form | 1.30 / 1.50 | The saved view shows the steep roof, three dormers, chimney, and gabled end supported by Photo 37; aerial evidence informs the roof plan. Wall height (7.5 m) and ridge height (11.4 m) remain estimates. The single historic oblique view cannot prove concealed slopes or exact vertical dimensions. |
| Facade fidelity | 1.25 / 2.00 | The revision now follows the directly identified Photo 37: dark Tudor half-timbering across the visible upper facade and gable, pale infill, broad window groups, an offset entrance, three dormers, and a chimney. The low-resolution monochrome photo supports silhouette and placement, but exact opening dimensions, sash divisions, color, and hidden elevations remain uncertain; current repeated windows and simplified entry are still interpretive. |
| Geometry, materials, and portability | 1.45 / 1.50 | The topology report is tied to this exact SHA and reports zero boundary/non-manifold edges across all 12 mesh objects. Blender 5.2.3 reopened the stable scene and collection with 12 objects and no unpacked external images. Procedural materials are portable. Their colors/finishes remain estimates because the identified facade source is monochrome. |
| Interior and labeling | 0.90 / 1.50 | A floor, partitions, and furnishings are included as a schematic, and the separate preview explicitly says “SCHEMATIC INTERIOR | NOT SURVEYED.” This is appropriately caveated but is not an as-built plan: no KDR floor plan was found and the room arrangement is generic. |
| **Total** | **8.40 / 10.00** | **Passes the project threshold.** |

## Decision

The new, address-captioned NPS photo materially improves the facade assessment over the previous 7.9/10 grade, which had no directly identified facade source. The current timbering, gable, dormers, chimney, and offset entrance correspond to visible features in that source. The reported topology repairs and fresh-open check also pass for the exact SHA above. This building is eligible for coordinator review and master integration under the README threshold.

Do not describe the model as fully measured: the NPS source is monochrome and oblique; height, precise colors/materials, exact facade dimensions, concealed elevations, and the interior remain estimated or unverified. This independent grade does not certify placement in the master blend.
