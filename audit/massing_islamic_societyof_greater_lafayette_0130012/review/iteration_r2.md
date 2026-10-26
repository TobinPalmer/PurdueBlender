# ISGL r2 iteration and review notes

Date: 2026-10-26  
Stable ID: `massing_islamic_societyof_greater_lafayette_0130012`  
Asset: `modular/buildings/massing_islamic_societyof_greater_lafayette_0130012.blend`

## Changes since r1

- Reviewed the r1 independent score of 7.2/10 and addressed the roof silhouette finding. The single-apex fan roof was replaced with two separate estimated four-plane hip roofs aligned to the west/east footprint wings. The Indiana 2022–2025 orthophoto supports multiple plane/ridge breaks, but does not establish exact roof construction, eave line, ridge heights, or pitch.
- Added Purdue Engineering’s 2022 event page, which associates the ISGL 1022 1st Street venue with Muslim Student Association participation, and Tippecanoe County’s 2010–2024 judgments list, which names North American Islamic Trust Inc. ISGL at 1022 First Street. These strengthen the physical-site identity match while leaving GIS FID 771’s `Muslim Student Association` / `1021 FIRST ST.` label discrepancy explicit.
- The county snapshot content is PDF despite its original `.xlsx` suffix; it was renamed `.pdf` with content unchanged and the source catalog documents that correction.
- Retained Purdue GIS FID 771’s returned polygon ring without rescaling. Its transformed ring area is 463.267 m² while `Shape__Area` reports 800.789 (units/calculation provenance unresolved). Neither value is treated as a definitive surveyed area.

## Reopen and export checks

Fresh direct reopen using Blender 4.5.15 LTS passed. Scene and exported collection names match the manifest; the collection contains one mesh object with 982 vertices and 747 faces, no modifiers, no linked libraries, and no unpacked external images. The source GIS base ring matches the saved shell vertices within 0.00001437 m maximum nearest-vertex error. The three r2 renders are present under `audit/massing_islamic_societyof_greater_lafayette_0130012/renders/`.

## Remaining uncertainty for grader

- GIS name/address and official ISGL name/address do not match exactly, and no parcel crosswalk was found.
- County judgments and event records corroborate organization/location, but do not prove building identity or dimensions as a parcel survey would.
- The roof geometry and vertical dimensions are estimated. GIS says one floor; the photo shows two facade bands. The entrance side and window rhythm remain inferred from a single un-georeferenced facade photo.
- GIS `Shape__Area` conflicts with the transformed polygon-ring area; shell uses the returned ring vertices as-is.

Fresh independent r2 grading is pending. Prior r1 result is preserved at `audit/massing_islamic_societyof_greater_lafayette_0130012/independent_grade/r1/result.json`.
