# Independent re-grade — Life Science Ranges Greenhouse and Service Building

**Score: 8.10/10 — pass.** Passing threshold: 8.0/10.

| Criterion | Score | Independent assessment |
| --- | ---: | --- |
| correct identity and source backed footprint | 2.00/2 | Official Purdue GIS FID 915 names the feature Life Science Ranges (BLDG_ABBR LSR), address 180 S Russell Street; its saved geometry lies over the greenhouse rows and west service wing. The Purdue 2022 board approval packet documents the LSR phenotyping greenhouse project and site relationship; Purdue College of Agriculture 2026 article/photos show the greenhouse facility and operations. |
| position orientation scale and dimensions | 1.60/2 | Independent footprint overlay shows candidate area 7705.8 m² vs GIS polygon 7305.7 m², IoU 0.8757; candidate bounds agree closely with the GIS envelope and the row axes match the aerial. Fresh-open Blender bounds are X -47.485 to 47.612 m, Y -61.201 to 61.201 m, with Z 0 to 7.875 m; proposed origin is [-440.05172262549604, -545.2148990903459] m from the GIS envelope midpoint. |
| evidence backed height floors and roof form | 1.20/2 | Purdue GIS records NUM_LEVELS=2 and CountOfFLO=2, but raw Extrution=12 and Elevation=620.1 have no defined vertical units or datum; the builder explicitly avoids interpreting them as measured height. Photographic and aerial evidence supports repeated pitched multi-span glass greenhouse roofs and a low service wing, consistent with the model’s broad roof form. |
| facade entrances distinctive features and interior | 1.70/2 | Exterior and roof views show seven greenhouse groups with low-iron glazing, repeated aluminum framing/mullions, pitched multi-span roofs and a distinct brick/service wing with curtain wall, service doors, vents, HVAC, sign and drainage. The interior view includes research benches/trays, modeled plants, LED lighting and a phenotyping conveyor; the 2026 Purdue article/photos support the conveyor, LED/humidity technology and brick-backed HVAC context. |
| modular export portability and complete evidence | 1.60/2 | The exact candidate hash is B90ADA781E76E8C7C3A08B59D95A28CD97CFA763C59D09278DDDA99781F0707E, matching the requested revision. Fresh Blender 5.2.3 open found scene Building_massing_life_science_ranges_greenhouse_and_service_building_c96231f and expected asset collection Asset_massing_life_science_ranges_greenhouse_and_service_building_c96231f with 49 objects, 48 meshes and 16 used materials. No mesh lacks a material; no external unpacked images are present. The builder uses procedural materials and a stable asset path/collection name. |

## Findings

1. The candidate is correctly associated with the Life Science Ranges greenhouse complex; dimensions of individual roof rectangles are reconstructed from current imagery.
2. Tobin should reconcile the current local-coordinate asset with the master manifest/placement before considering the campus placement verified. Candidate geometry overlay is good but not exact (IoU about 0.876), and direct master-instance position is still unverified.
3. The height treatment is honest and properly qualified, but the numerical heights and precise roof profile remain unmeasured estimates.
4. The model is visually legible and source-informed; exact service-facade dimensions, greenhouse bay sizes and interior layout remain reconstruction.
5. Asset-level save/reopen and source documentation pass; update/check project metadata and the master instance before calling the library fully integrated.

## Limits

- Master integration and placement marker were not changed or validated by this review; manifest still reflects superseded massing bounds/identity transform.
- No measured vertical dimensions or complete as-built architectural plan were found.
