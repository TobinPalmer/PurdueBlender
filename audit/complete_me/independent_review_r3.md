# Mechanical Engineering R3 — Independent Full-Building Review

**Review date:** 2026-10-24  
**Revision reviewed:** R3  
**Asset:** `modular/buildings/mechanical_engineering.blend`  
**Reviewer:** Independent reviewer; did not build or edit R3  
**Score:** **8.0/10**  
**Decision:** Meets the project's 8.0/10 acceptance target, narrowly. Roof height/form, facade registration, and interior circulation remain unverified.

## Scorecard

| Criterion | Score | Review |
| --- | ---: | --- |
| Identity and footprint | 1.8/2.0 | The 2023 Indiana orthophoto and Purdue GIS FID 857 support the large Mechanical Engineering complex and visibly match its multi-wing outline. FID 108 remains a separate compact southeast mass. The project tangent-plane conversion and touching/overlapping polygons are not surveyed wall control. |
| Placement and orientation | 1.9/2.0 | Read-only inspection of the saved master confirms one `Placement_mechanical_engineering` collection instance at (66.300003, 86.5, 0) m, zero rotation, unit scale. Its relative library path resolves to the expected source file. The marker agrees with manifest XY (66.300001, 86.5) to approximately 0.000002 m; campus coordinates still inherit the approximate project conversion. |
| Form, height, and roof | 1.1/1.5 | R3 materially improves the broad roof surface representation: the official 2023 image is registered across all 102 upward FID 857 roof faces, and the render shows the red tile, membrane, courts, and rooftop zones visible in the orthophoto. This is a surface texture, not roof geometry. FID 857 remains an 18.5 m shell with a 0.25 m cap; wing-specific heights, roof slopes, parapets, and structural roof breaks remain unresolved. |
| Facade, materials, and entrance | 1.5/2.0 | Brick, windows, frames, stone bands, and the fountain-facing arch retain qualitative photographic support. R3 does not change the facade. The broad elevation still repeats a uniform four-course window schedule; exact openings and the entrance's along-wall location are not registered to a GIS edge. |
| Interior and circulation | 0.7/1.5 | The 2025 evacuation slides and 2022 renovation material support broad core/connection context but do not provide scale-registered current floor plans. Interior partitions, circulation, and the Gatewood connection remain schematic or unverified. |
| Technical integrity | 1.0/1.0 | Blender 5.2.3 reopened the source collection with the expected identity root. The R3 validator passes; the 1800×1500 orthophoto is packed, UV coordinates remain within the saved crop, and no external image dependency is present. The master link resolves and placement is verified read-only. A shared-index cleanup is still needed: the manifest lists 50 objects and omits five R1 facade objects, while the current source collection has 55. This is a coordinator-owned manifest mismatch, not a source portability failure. |
| **Total** | **8.0/10** | **Pass, narrowly** |

## Findings

R3 addresses a major visual gap from R2: the large roof was formerly a broad gray surface, while the model now shows the actual roof color/material pattern across the GIS-matched plan. I independently inspected the saved orthophoto/GIS overlay and the R3 top render. The outlines align at campus scale, and the rendered roof pattern follows the 2023 aerial, but the map image supplies no height or slope information. The main mass still has a uniform 18.5 m shell, so R3 does not resolve the earlier wing-height and roof-form deductions.

The saved model's `ME_Official_857_Roof` has 308 faces with two material slots; the R3 orthophoto slot is assigned to the top surface. The packed image is 1800×1500 pixels, and the reopened file has no unpacked external image. The export collection contains 55 objects. The current manifest's 50-object inventory predates the five R1 facade pieces and should be corrected by the coordinator before or during integration.

I independently read the saved campus master. It contains one placement marker linked to `Asset_mechanical_engineering`; the relative source path resolves, the marker is at the manifest origin within about 0.000002 m, and its rotation/scale are identity. This closes the R2 review's placement/path evidence gap. No master edits were made during this review.

The R1 facade and entrance renders remain the latest close views. They show coherent brick material, dark glazing, frames, sills/stringcourses, and an arched entry, but do not establish facade-to-edge mapping or current interior layout. R3 is therefore a narrow pass for the requested threshold, not a claim of fully surveyed architecture.

## Remaining work

1. Update the coordinator-owned manifest object count/name list from 50 to the 55-object source collection before final index synchronization.
2. Keep the 18.5 m FID 857 shell and flat roof labeled unverified until a direction-registered elevation or roof plan establishes wing datums and slopes.
3. Seek current scaled plans for post-renovation interior routes and facade openings; emergency evacuation slides alone do not verify dimensions or complete daily circulation.

## Sources reviewed

- `audit/complete_me/mechanical_engineering_r3_evidence.json`, validation JSON, registered roof render, and orthophoto/GIS overlay.
- [Indiana Geographic Information Office Current Imagery ImageServer](https://di-ingov.img.arcgis.com/arcgis/rest/services/DynamicWebMercator/Indiana_Current_Imagery/ImageServer), catalog item `in2023_30001885_06` (2023 Tippecanoe orthophoto; CC0 per source metadata).
- Purdue BuildingShapes FeatureServer, FIDs 857 and 108, as retained in the building evidence.
- [Purdue ME Building Renovation brochure](https://engineering.purdue.edu/ME/Giving/Renovation/ME-Building-Renovation-2022.pdf), [2023 project request](https://www.purdue.edu/treasurer/finance/wp-content/uploads/2023/04/Mechanical-Engineering-Building-Renovation-B-1-23-2-14.pdf), and 2025 Purdue emergency-plan material.
- R2 independent review and the R1 hero/entrance renders, for unchanged facade/interior context.
- Read-only Blender 5.2.3 inspection of the standalone source and root master placement/link.

No asset, master, shared index, or other building was changed during this review.
