# Windsor Halls independent grade

**Asset:** `modular/buildings/massing_windsor_halls_80aeb51.blend`  
**SHA-256:** `667db1b371209d8ddd46aaf57ecf3edaafe1e7840f4353eb8344a5b0db2302cc`  
**Review date:** 2026-10-26  
**Decision:** 7.4/10 — below the 8.0 acceptance threshold; do not yet mark finished or integrate as a finished detailed asset.

## Method

I reopened the exact candidate file in Blender 5.2.3 using `fresh_open_probe.py`, checked the saved collection/object/material inventory and bounds, compared the documented FID 63–66 structural-shell results against the preserved Purdue GIS GeoJSON and the footprint overlay, and visually inspected `previews/windsor_halls_overview.png`. I reviewed the builder's evidence and compared the exterior character against Purdue's Windsor page and its official Windsor exterior photo. This is an independent visual/technical grade, not a survey; the candidate's exact footprint metrics were independently recomputed by the builder's validation script from the fresh-opened shell rings.

## Scorecard

| Category | Weight | Score | Weighted | Finding |
| --- | ---: | ---: | ---: | --- |
| Identity, footprint, plan and campus placement | 25% | 9.8 | 2.45 | FIDs 63–66 map to the named Warren, Wood, Vawter, and Windsor Dining Court features. Each structural shell's reported IoU is 0.9999984–0.9999990; maximum boundary discrepancy is about 0.000031 m, consistent with Blender float precision after the documented local projection. Source positions and plan outlines are exceptionally well supported. |
| Massing, height, level count and vertical placement | 20% | 7.0 | 1.40 | Four visible facade levels in Warren and Vawter are consistent with current Purdue emergency-plan descriptions. Wood's level count and all wall/roof dimensions remain estimates. The Dining Court is represented as a lower schematic shell; GIS footprints touch rather than overlap in 2D and the exact subsurface elevation/exposure cannot be established from the available data. |
| Roof and facade specificity | 25% | 6.4 | 1.60 | Red-brown masonry, pale trim, repeated window bays, and an entrance treatment communicate the historic residence-hall character. The visible roofs read as broad, low, mostly uninterrupted caps rather than the steep pitched/gabled roofs and roofline variation evident in Purdue's official exterior reference. Dormers, chimneys, hall-specific entrance/stonework, and other identifiable ornaments are absent or generic. The highly regular generated window grid is a plausible approximation, not a verified elevation. |
| Materials and texturing | 10% | 6.8 | 0.68 | Six named, self-contained procedural material slots are present for brick, limestone, roof, glass, doors, and dining base. There are no missing external image textures, which is good for portability. The visible surfaces are still largely uniform color blocks; there is little brick/stone relief or weathering and glazing/frame depth is minimal. |
| Interior and functional completeness | 10% | 3.0 | 0.30 | No interior is modeled. The evidence explains that no hall-specific floor plans were verified and avoids fabricating a false layout, but this remains a major gap for a residence complex when judged for overall completeness. Generic room-photo references cannot validate a building-specific interior. |
| File integrity, editability and evidence | 10% | 9.5 | 0.95 | Fresh-open passed: expected scene and stable collection; 28 mesh objects plus the origin marker; 20,236 vertices, 9,232 faces, six material definitions; no missing external image dependencies. Component-specific geometry, provenance, CRS, transform and uncertainties are documented. |

**Weighted total:** 7.38/10 (reported as 7.4/10).  

## Fresh-open findings

The asset reopened successfully with scene `Building_massing_windsor_halls_80aeb51` and collection `Asset_massing_windsor_halls_80aeb51`. Bounds are X −673.591 to −562.038 m, Y −168.406 to −25.403 m, Z 0 to 20.661 m. The exact SHA remained unchanged after review. See `fresh_open_probe.json` for the independent object/material inventory.

## Priority revisions before regrade

1. Replace the generic low hipped caps with source-supported roof profiles. In particular, verify each hall's roof silhouette and include steep gables/dormers/chimneys only where current images or archival photos support them. Avoid applying one assumed roof shape to all wings.
2. Make the facade elevations less uniform: verify window bay counts and spacing per hall/elevation; model distinct entry placement and documented stone surrounds or projections from specific photos. Keep assumptions labeled where images do not resolve detail.
3. Add a modest, explicitly schematic interior shell for each residence hall and the dining court (corridors/common spaces/room blocks), or otherwise request a criteria exception from the coordinator if the project standard treats unverifiable interiors as intentionally omitted. Do not claim room layout accuracy without hall-specific plans.
4. Increase material relief and variation for brick and limestone, plus glazing/frame depth, while keeping the current asset self-contained and avoiding unsupported facade color differences.
5. Re-render close exterior views of all four components and a section/cutaway of the dining court relationship. Preserve the exact GIS wall footprints; confirm any added eaves/porches do not alter wall-footprint metrics.

## Evidence and limitations

- Purdue University Residences, [Windsor Halls](https://housing.purdue.edu/my-housing/options/residence-halls/windsor.html): confirms the five-hall complex and that Dining Court is beneath Vawter and Warren; it does not give detailed hall-specific architectural plans.
- Purdue StarRez portal, [official Windsor exterior reference](https://purdue.starrezhousing.com/StarRezPortalXConference/File/GetImage?dateCreatedTicks=638309106832699833&hash=3B0DB762&imageName=52483840151_ea5f2e6ade_k.jpg&tableID=13617&tableName=PortalPageWidget): general complex exterior, not individually labeled by hall; supports broad masonry/roof character but not exact hall-specific details.
- Purdue GIS, preserved snapshot `../sources/purdue_gis_windsor_fids_63_66_277_278_2026-10-26.geojson`: official outlines. The builder's validation uses the repository local approximate lat/lon-to-meter conversion; it is not a surveyed CRS and cannot establish Z, facade, roof, interior, or exact dining-court vertical exposure.
- `../validation.json`, `../evidence.md`, and `../previews/windsor_gis_footprints.png` document source match, measured footprint fit, excluded adjacent FIDs 277/278, and the principal uncertainties.

No independent height survey, hall-specific elevation drawings, or floorplans were available in the evidence reviewed. Roof profile and interior precision remain unverified rather than measured.
