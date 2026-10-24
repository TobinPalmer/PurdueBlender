# Mechanical Engineering — R3 registered roof surface

**Revision:** R3  
**Asset:** `modular/buildings/mechanical_engineering.blend`  
**Collection:** `Asset_mechanical_engineering`  
**Scope:** The Mechanical Engineering asset and its dedicated audit folder only. The campus master and shared indexes were not edited; no commit was made.

## Change

R3 gives the large FID 857 roof a source-registered 2023 aerial surface. The image is applied only to the 102 upward-facing polygons in `ME_Official_857_Roof`. The projection uses the saved Indiana ImageServer crop bounds in EPSG:3857 and the project's approximate campus-local-to-longitude/latitude conversion. The source image is packed into the Blender file, so the material has no external image dependency. The existing roof membrane remains assigned to vertical roof edges.

This makes the current red tile roofs, dark membrane sections, mechanical areas, and interior court visible in overhead/oblique asset views. The orthophoto records observed surface appearance; it does not establish roof slopes, structural heights, parapet heights, or which 2018 LiDAR returns belong to each wing. Accordingly, R3 leaves FID 857's 18.5 m shell, 18.50–18.75 m roof cap, and all wall/facade geometry unchanged.

## Evidence and registration

- **Provider:** Indiana Geographic Information Office, Indiana Current Imagery ImageServer.
- **Source:** [ImageServer](https://di-ingov.img.arcgis.com/arcgis/rest/services/DynamicWebMercator/Indiana_Current_Imagery/ImageServer); catalog identify returned `in2023_30001885_06`, Tippecanoe 2023, 6-inch nominal imagery, CC0.
- **Retrieval date:** 2026-10-24. The JPEG crop and its GIS overlay are retained as `indiana_current_orthophoto_me_r2.jpg` and `indiana_current_orthophoto_me_r2_gis_overlay.jpg`.
- **Image extent:** EPSG:3857 bounds `[-9675191.1145, 4928297.9356, -9675001.5073, 4928454.8307]`, 1800 × 1500 pixels, recorded in `mechanical_engineering_ortho_registration_r2.json`.
- **Registration method:** For each FID 857 roof-mesh loop, add the building placement origin `[66.3000011, 86.5]` m to mesh-local XY, convert with the documented project tangent-plane approximation around 40.4274°N, 86.9137°W, then project to EPSG:3857 and normalize against the saved image extent. The roof's shared GIS footprint and orthophoto outline align in the saved overlay. This is approximate geographic registration, not survey control.
- **Geometric identity check:** R3 retains the GIS shell's local XY bounds `[-54.3292, 62.6990] × [-33.8952, 57.9013]` m and shell height `0–18.5` m. Roof cap remains `18.5–18.75` m. No footprint or height is changed.

## Why other findings were not edited

The R2 independent review identifies three unresolved areas: wing-specific height/roof form, facade-to-edge registration, and current circulation. The source review found no public, direction-registered measured roof/elevation drawing or scaled as-built plan for the completed renovation. Purdue's 2022 renovation brochure has clearly labeled planned floor diagrams and an oblique roof photo; the project cost request confirms renovation of the ground through third floors and a new stair/elevator connection; the 2025 evacuation maps show egress routes and cores. These sources do not supply a reliable scale and orientation transform from plan pixels to the GIS polygon, nor a roof datum for individual wings. They support broad qualitative topology only.

The 2018 DSM and 2016–2020 bare-earth DTM remain too coarse and mixed with canopy/equipment to attribute a height to a specific FID 857 wing. The 2015 directional north/east facade photos establish qualitative architectural variation but predate the latest work and are not registered to GIS edges. The current 2025 egress slides are route diagrams rather than measured architectural plans. R3 therefore makes no unsupported facade openings, height, roof massing, stair, elevator, or partition changes. Evidence and measurement limits are recorded in `mechanical_engineering_r3_evidence.json`.

## Reopen and technical validation

`build_mechanical_engineering_r3.py` saved and reopened the asset with Blender 5.2.3 LTS. `mechanical_engineering_r3_validation.json` reports a passing check: identity root, named export collection, unchanged FID 857 footprint and height, all 102 upward roof faces assigned the source image, UV range inside the registered crop, and the image packed into the file. The verification render is `mechanical_engineering_r3_registered_roof_top.png`.

R3 adds only the FID 857 roof surface texture and evidence metadata. FID 108 geometry, FID 857 facade/window schedule, entrance, floors, partitions, and all shared/master files are unchanged. The R2 7.5/10 review remains the last independent grade; R3 is ready for a fresh review, with the unresolved structural/detail uncertainties above retained.
