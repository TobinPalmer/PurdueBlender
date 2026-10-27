# Independent UPOF grade r2

**Score: 8.45/10 — passes the 8.0 threshold.**

- **2.00/2.00 — Identity and source-backed footprint:** Full credit. Stable identity and the non-rectangular footprint are verified numerically and visually.
- **2.00/2.00 — Position, orientation, and scale:** Full credit. Footprint and site anchor agree with supplied ArcGIS projection method to high precision.
- **1.55/2.00 — Height, floors, and roof evidence:** Strong two-floor low-profile roof treatment, but exact eave/parapet height and seam spacing remain estimates. Absence of HVAC/hatch is justified by the newer imagery, which does not substantiate them.
- **1.05/2.00 — Facade, east entry, and distinctive details:** Entry placement and restrained industrial material treatment are plausible and evidence-aware. Direct facade imagery is lacking: repeated window positions, glazing, wall panel system, and elevation composition are estimated; rendered window faces read nearly opaque and unusually dark. Interior is explicitly schematic/unverified.
- **1.85/2.00 — Modular export, portability, and evidence:** Portable self-contained asset with substantial evidence. Procedural, mostly monochrome surfaces are reliable and dependency-free but could use richer facade/window variation.

## Findings

- **Positive:** The roof equipment and hatch removal is a well-supported correction: the z20 outline overlays a largely uninterrupted roof and does not identify those objects.
- **Positive:** E-W roof rib direction now agrees with the north-up orthophoto.
- **Limitation:** Facade treatment remains uncertain because no direct UPOF elevation is provided by the available OEP, ECN, or overhead imagery.
- **Actionable:** For a higher facade score, seek a clearly geolocated/direct UPOF street or ground-level facade image; then replace the estimated repeated dark panels with evidenced window sizes, spacing, glazing reflectance, and cladding breaks. Keep these marked estimated until direct imagery is found.
- **Limitation:** The ArcGIS Extrution field unit is undocumented. Do not describe the 6.88 m shell / 7.32 m total as verified height; preserve as an estimate unless a reliable elevation source is found.
- **Limitation:** Interior rooms are schematic because the OEP page gives limited program facts rather than a measured architectural plan.

## Evidence

- `fresh_open_probe.json: current Blender 5.2.3 readback, geometry comparisons, dimensions, object/material/dependency counts.`
- `fresh_open_oblique.png: fresh render from opened asset; visual assessment of roof, facade, windows, entry and massing.`
- `../previews/utility_plant_office_facility_gis_orthophoto_overlay.png: z20 Esri roof/footprint comparison.`
- `../sources/arcgis_fid296_feature.json and ../source_provenance.json: raw GIS feature, projection method and stated uncertainty.`
- `../sources/purdue_oep_upof.html: official OEP program and east-entry source.`
- `../sources/purdue_ecn_webcam_from_upof_2026_05_18_11_00.jpg: contextual facade clue; not treated as confirmed elevation.`
