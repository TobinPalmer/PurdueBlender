# Alpha Gamma Delta (FID 757) independent grade

**Review date:** 2026-10-28  
**Reviewed asset:** `modular/buildings/massing_house_301841608_d56a4c4.blend`  
**SHA-256:** `DEECE5A3370C60670BD876ED940DBBDDBF16620B73A85B66D6B0A85D45A270FF`  
**Result:** **8.1/10 — PASS** (weighted total 8.12/10)

Read-only cross-building review by the Alpha Phi building reviewer, who did not author the Alpha Gamma Delta asset. The reviewer compared the exact saved asset to the GIS/source packet and previews. The official [Purdue GIS FID 757 record](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query?where=FID%3D757%26outFields%3D*%26returnGeometry%3Dtrue%26outSR%3D3857%26f%3Dpjson) and [Alpha Gamma Delta Housing Corporation page](https://alphagammadeltahousing.org/locations/purdue-university/) identify the Beta Xi house at 1010 David Ross Road. The [Meyer Najem project page](https://www.meyer-najem.com/project/alpha-gamma-delta-sorority-house-purdue-university/) describes a two-story renovation; its 5,000-square-foot figure is the renovation scope, not the whole building.

| Category | Weight | Score | Review basis |
| --- | ---: | ---: | --- |
| Identity and provenance | 20% | 8.5/10 | FID 757 identity/address cross-checked with chapter housing source; building-specific illustration and photo references documented. |
| Plan geometry and placement | 25% | 8.0/10 | Structural shell derives from the full GIS polygon ring. No independent wall-position overlay/ground-control comparison was supplied. |
| Exterior silhouette and openings | 25% | 8.0/10 | Raised central volume, round window, lower wings, and entry motif correspond to the property-specific illustration; facade orientation and window spacing remain illustrative. |
| Materials and facade | 10% | 8.5/10 | Distinct material palette, trims, and entry treatments are present and source informed. |
| Interior and legibility | 10% | 7.5/10 | Furnished lounge/dining/study preview is photo informed, but partitions/circulation are sparse schematic inserts, not an as-built plan. |
| Presentation and technical | 10% | 8.2/10 | Blender 5.2.3 fresh-open passed; one stable export object, no external image paths. Composite mesh has documented open/non-manifold edges. |

**Weighted calculation:** `0.20×8.5 + 0.25×8.0 + 0.25×8.0 + 0.10×8.5 + 0.10×7.5 + 0.10×8.2 = 8.12`, rounded to **8.1/10**.

### Limits retained

- The GIS source layer's native coordinates are EPSG:3857. The independent reviewer initially flagged the source Shape__Area/local approximation difference; the coordinator later recovered the live FID query in both EPSG:4326 and EPSG:3857. The 3857 shoelace area/perimeter match the GIS attributes (1,786.0039 m² / 221.3358 m); the smaller local-approximation area reflects Web Mercator distortion. The independent grade remains conservative and unchanged.
- The 40-foot extrusion is a GIS attribute, not a surveyed roof height; it conflicts with the single-level `NUM_LEVELS` field and must not be called a verified height.
- Facade bearing, dimensions, and window stationing are illustrative. Interior partitions and circulation are schematic, not current as-built information.
- Mesh health is documented but non-watertight: 3,026 non-manifold edges, including 980 boundary edges.
- Master placement/integration is a separate coordinator check.
