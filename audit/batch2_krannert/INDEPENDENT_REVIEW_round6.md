# Krannert Building — independent full-building review, round 6

**Grade: 7.4/10 — below the 8/10 completion threshold.** Reviewed the latest saved asset (R4 geometry/materials) and R5–R6 evidence supplements on 2026-10-24. R6 changed documentation/evidence only; it did not change the building asset.

| Category | Score |
| --- | ---: |
| Identity and source-backed footprint | 1.7/2 |
| Position, orientation, and scale | 1.6/2 |
| Height, floors, and roof | 1.2/2 |
| Facade, entrances, and distinctive architecture | 1.5/2 |
| Interior, courtyard, and circulation | 1.0/2 |
| Technical portability and evidence | 1.9/2 |
| **Raw points** | **8.9/12 = 7.4/10** |

## Findings

- **Identity and footprint:** Purdue Campus GIS BuildingShapesZip4 FID 54 is identified as KRAN, and the local footprint wire follows its 12-vertex ring. This supports a plausible building footprint and massing. However, the wire was generated from that same GIS feature, so its near-zero overlay error is construction alignment, not independent as-built confirmation. The structural masonry bounds extend about 0.20 m beyond the GIS bounds per side; this is documented as a screening check only.
- **Placement, orientation, and scale:** The read-only master check finds `Placement_krannert_building` at `(234.5345001, -412.7189941, 0)`, zero rotation, unit scale, and only 0.0000153 m XY difference from the manifest. This verifies marker-to-manifest registration. No independent survey or source comparison verifies shell orientation/scale against the campus or the GIS polygon.
- **Height, floors, and roof:** The model has a multi-level shell, slabs through L7, and a rooftop mechanical volume. GIS F01–F07 minus G numerically matches the modelled floor datums, and R-G matches its roof-deck datum under an inferred feet/common-datum interpretation. Those same GIS attributes informed the model; the layer schema supplies no units or definitions, and R/Extrution have ambiguous roof semantics. The historical 1965 image supports a flat roof edge and screened zone, not present roof/penthouse height. These levels remain unverified.
- **Facade and entrances:** The model captures a repeated narrow-window/broad-pier rhythm, pale masonry, dark glazing, a darker ground band, and a projecting entry. The 1965 *Indiana Architect* project photo provides useful contemporary design evidence, while the undated Purdue Events photo supports qualitative current exterior cues. Neither is a calibrated elevation. In the model views, the long black re-entrant gap reads as a large open vertical slot; its actual connecting walls and courtyard condition remain unresolved. The parapet, exact window cadence, brick module, and entry dimensions are not measured.
- **Interior, courtyard, and circulation:** The Drawing Room and Parrish Library have recognizable furnishings and materials supported by Purdue tour/renovation images. The room plans are unregistered or marked not-to-scale, and most of the building’s other floors remain schematic/empty; room positions, dimensions, furniture counts, and circulation are estimates. The courtyard/re-entrant seam is shown from two model angles, but no source resolves whether it matches the as-built condition.
- **Technical portability and evidence:** R4 reopen validation reports 670 objects/662 meshes, identity local root, no unmaterialed meshes or material-output issues, no unpacked external images, and no remaining validator issues. The evidence carefully labels uncertainty and distinguishes GIS alignment from independent verification. The shared manifest still lists the removed `KRAN_Surrounding_Plaza_Paving` object, which requires coordinator-side reconciliation before integration.

**Decision:** Do not mark finished. The exterior model and two interiors are substantial, and the R5/R6 evidence improves source context, but the grade remains below 8/10 because the shell-to-GIS fit is not independently verified, roof/floor semantics remain uncertain, the re-entrant opening is unresolved, and most interior floors lack source-registered detail. No asset geometry was changed by this review.
