# Independent grade — Alpha Phi (FID 764), revision 3

**Reviewed:** 2026-10-28  
**Artifact:** `modular/buildings/massing_house_301841331_735e92f.blend`  
**Requested SHA-256:** `0E588FFDB41AA611CAB94CBD04B336ADFE816AF8C0FE6962C46A28782C060F03`  
**Verified commit:** `5470affcbe242aec3f823147b30b24cc441db3b4` (`Revise Alpha Phi roof and cutaway evidence`)  
**Result:** **8.085 / 10 — PASS** (8.09 rounded)

The saved file hash matches the exact revision requested. The primary improvements over revision 2 are visible in the saved previews: the exterior is now well-lit with a visible entry plaque, the unsupported broad gable/ridge/chimney have been removed, and the room modules are framed by the full footprint in a roof-open view. The footprint still only matches the retained GIS polygon by construction, and the roof, heights, story count, facade details, and room layout remain interpretive.

## Weighted score

| Category | Weight | Score / 10 | Weighted points | Basis |
|---|---:|---:|---:|---|
| Identity and provenance | 20% | 9.5 | 1.90 | Current Purdue GIS FID 764 identifies Alpha Phi at 801 David Ross Rd; the Panhellenic chapter page confirms Delta Mu, and the rights-aware listing identifies its drawing as the Purdue Alpha Phi house. Live response and layer metadata use WKID 102100/latestWkid 3857, and the raw response is retained. No independent survey or as-built record is available. |
| Plan and placement | 20% | 8.4 | 1.68 | Full 16-vertex source ring is retained in the documented local approximation; saved wall base matches it with max error 0.000058 m / RMS 0.000041 m, with no translation or rotation correction. The overlay demonstrates faithful construction from the ring, not current wall-line truth or independent ground-control accuracy. Bounds are 40.16 × 28.57 m. |
| Exterior | 20% | 7.6 | 1.52 | Revised footprint-following low-profile roof avoids the previous unsupported broad-gable direction and looks coherent with the irregular footprint; brighter lighting and improved plaque make the facade/details easier to read. Roof type, cap coverage/top height, wall height, story count, window rhythm, trim, porch dimensions, and elevation remain unsupported or estimated. The conservative roof cap is still an interpretation. |
| Materials | 10% | 7.5 | 0.75 | Procedural/native brick, stone, glass, roof, and wood palette is coherent and has no external texture/path dependencies. The source drawing supports a brick building and entrance/sign cues, but most colors, trim, shutters, and glazing treatment are still illustrative. |
| Interior | 15% | 7.4 | 1.11 | The roof-open image now places two upper-room modules within the full-footprint perimeter and communicates that the inserts are schematic. It is a stronger presentation than the isolated modules in R2. There is still no verified floor plan, room count, circulation, layout, or furnishing source; the interior occupies only a small central portion of the large footprint. |
| Technical presentation | 15% | 7.5 | 1.125 | Independently reopened the requested saved asset with Blender 5.2.3: expected scene, collection, object, identity transform, and 14 materials; 4,183 vertices, 6,165 edges, 2,961 faces. The export is still one composite mesh and has 543 boundary/non-manifold edges; it is not watertight or fabrication-ready. Previews are clearer and adequately framed for visual review. |
| **Total** | **100%** |  | **8.085 / 10** | **PASS — meets 8.0** |

Weighted calculation: (9.5 × 0.20) + (8.4 × 0.20) + (7.6 × 0.20) + (7.5 × 0.10) + (7.4 × 0.15) + (7.5 × 0.15) = **8.085**.

## Independent verification

- Computed SHA-256 for the current saved `.blend`; it equals the requested `0E588FFDB41AA611CAB94CBD04B336ADFE816AF8C0FE6962C46A28782C060F03`. The file is clean relative to the checked-out tree. Commit `5470affcbe242aec3f823147b30b24cc441db3b4` is present and names the revision 3 roof/cutaway change.
- Opened the saved `.blend` directly in a separate Blender 5.2.3 background process without saving. It loaded the expected scene `Building_massing_house_301841331_735e92f`, asset collection `Asset_massing_house_301841331_735e92f`, and single mesh object `House_301841331`, at location/rotation zero and scale one. I independently measured 4,183 vertices, 6,165 edges, 2,961 faces, 543 boundary edges, 543 non-manifold edges, and 14 materials. Bounds: X −1138.228…−1097.743 m, Y 750.299…779.209 m, Z −0.100…8.260 m.
- Queried the Purdue BuildingShapesZip4 live feature and layer metadata again. One feature returned for FID 764; live attributes include `BUILDING_N=Alpha Phi`, `ADDRESS=801 David Ross Rd`, `NUM_LEVELS=1`, and `Extrution=12`; live geometry is equal to the retained snapshot. Response and layer metadata declare WKID 102100/latestWkid 3857.
- Inspected `evidence.json`, `review_handoff.md`, source observation, plan comparison/overlay, fresh-open validation, exterior render, and roof-open cutaway. The polygon-to-wall match is by construction. The views support inspectability and design intent, not as-built validation.
- The HUBERart page states its subject is the Purdue Alpha Phi house and that its images may not be duplicated; its accessible description identifies brick, Alpha Phi signage, and entry stairs. The model appropriately retains a URL/observation instead of a local reference-image copy. The page is not a measured facade source.

## Remaining uncertainty and limitations

- GIS `NUM_LEVELS=1` conflicts with the modeled two-level interpretation; other source fields are ambiguous (`Extrution=12`, and the retained response also has `Level_=8` and `CountOfFlo=1`). None resolves actual story count or height. Wall height (7.4 m) and roof-cap top height (8.25 m) are estimates.
- The flat/low-profile cap, its type/coverage/profile, facade colors/details, entry geometry, window spacing, and interior positions are not verified by plans, surveyed elevations, or current photographs. Removing the prior ridge direction avoids a specific directional claim but does not verify the replacement cap.
- No georeferenced current aerial, survey, or CAD plan is retained. The exact wall-base overlay demonstrates adherence to the transformed source ring, not that the GIS feature describes a current wall line or exact wall dimensions.
- Bedroom/lounge partitions, floor plan, room count, circulation, and furnishings are invented representative inserts. The roof-open view is a schematic cutaway, not an as-built interior.
- The composite mesh has 543 boundary/non-manifold edges. It is suitable as a visual composite with open/intersecting parts, not a closed/fabrication solid.
- The revised lighting and cutaway are materially clearer than R2. The roof cap still reads as a broad planar cover, so an authoritative roof/elevation source would improve architectural confidence more than additional unsupported facade detail.

## Source references

- Purdue GIS feature: `https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query?where=FID%3D764&outFields=*&returnGeometry=true&outSR=3857&f=pjson`
- Purdue GIS layer metadata: `https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0?f=pjson`
- Purdue Panhellenic Alpha Phi chapter: `https://www.purduepanhellenic.com/cost/alpha-phi`
- HUBERart listing: `https://www.etsy.com/listing/237335509/alpha-phi-sorority-house-purdue`
