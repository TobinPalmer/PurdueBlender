# Acacia independent grade — round 2

**Score: 8.35/10 — PASS**

| Criterion | Score | Evidence |
| --- | ---: | --- |
| Correct identity and source-backed footprint | 1.80/2 | Purdue GIS FID 791 and Acacia's official contact/history pages identify the 608 Waldron Street house. The WGS84 and EPSG:2968 rings agree within 0.226 m² (0.049%). The modeled structural shell overlaps the GIS ring at IoU 0.933; it is smaller by -0.609%, with 3.211 m maximum boundary residual. The GIS ring includes a small southern projection consistent with the modeled entrance/porch; the shell itself remains unshifted. |
| Position, orientation, and scale/dimensions | 1.50/2 | Fresh-open inspection confirms the original direct campus-coordinate frame, zero object/collection offset, and main-shell bounds [[-334.7135, -315.2749], [342.1364, 370.6293], [0.0, 9.45]] m. The north-up Esri overlay shows the FID 791 footprint aligned with the roof and west-side approach path. Matching that path to the official porch elevation supports the front-bearing inference. |
| Evidence-backed height, floors, and roof form | 1.60/2 | Official renovation/elevation drawings show three above-grade floor levels and a basement; the modeled envelope reaches 9.45 m above the asset datum. The saved facade photo and plans support a dark shingle pitched roof, central front gable, dormers, and chimney, which are represented in the asset. |
| Facade, entrances, and distinctive architecture | 1.55/2 | Direct comparison of the saved chapter facade photo and model render shows the distinctive brick tower and vertical ACACIA lettering, central illuminated-name entry arch, pale porch frame, brick lower facade, cream infill with dark timber framing above, central gable, repeated windows, dormers, and chimney. The render now places the half-timber gable above the entrance. The modeled interior depicts plan-supported lobby/atrium, heritage room, study hall, bedrooms, stairs, and circulation; the room plan is schematic. |
| Modular export, portability, and complete evidence | 1.90/2 | Fresh-open asset has the expected stable scene/collection, 508 objects and 502 meshes; 13 local materials; 0 meshes missing material slots; 0 unpacked absolute image paths; and 0 linked Blend libraries. The source folder preserves GIS, official plans, facade imagery, aerial overlay, provenance, validation, and exterior/interior renders. |

## Findings

- The ArcGIS Shape__Area/Shape__Length summary fields conflict materially with the encoded polygon. The encoded rings are mutually consistent and were used, but the structural shell does not reproduce the entire southern projection.
- The official facade photo is not geotagged and the Esri tile acquisition date is undisclosed, so the west-facing bearing is an inference rather than surveyed or direct photo orientation.
- The plan set may depict renovation/project design rather than the fully verified as-built condition. Floor spacing, overall roof height, and roof geometry remain estimated.
- The entry arch lettering and illumination have low contrast in the render, and facade/window/porch proportions remain simplified compared with the photograph and architectural elevations.
- The interior is legible as a schematic cutaway but uses estimated room placement, furnishings, and finishes; it is not verified as-built.
