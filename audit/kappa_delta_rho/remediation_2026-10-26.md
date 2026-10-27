# Kappa Delta Rho — post-grade remediation (2026-10-26)

- Preserved the stable asset ID, scene, exported collection, house object, and GIS FID 801 footprint.
- Rebuilt roof planes as closed 0.16 m slabs and the interior diagram floor as a closed 0.12 m slab. The previous roof mesh had 68 boundary/non-manifold edges; fresh-open topology now reports zero boundary and zero non-manifold edges across all ten mesh objects (`topology_report.json`).
- Added a camera-facing “SCHEMATIC INTERIOR | NOT SURVEYED” note to the interior preview only. No inferred sign was placed on the house.
- Fresh-open validation passed in Blender 5.2.3. Exact current SHA-256 is recorded in `fresh_open_report.json` and `build_report.json`.
- NPS Hills & Dales nomination Photo 37 directly identifies Kappa Delta Rho, Northwestern Ave, N. The supporting PDF caption says the view faces southeast and credits Jane Evans, June 2001. Its visible Tudor framing, pale wall fields, steep roof, three dormers, chimney, broad facade window groups, and offset entrance now guide the model. The source and rendered pages are recorded in `evidence.md` and `sources/`.
- Photo 37 is monochrome and shows only one oblique elevation. Exact colors/materials, heights, sash divisions, concealed elevations, and the interior remain uncertain. The interior layout is schematic and is not based on a floor plan. The unrelated Kappa Delta Sorority and other KDR chapters remain excluded.
- Final rebuilt asset SHA-256: `b6adaf3369e04593b2b65ea6d5b62c470076c1f913a6f7ae36e6439534488567`. Fresh-open validation confirms exact GIS FID 801 base footprint (maximum nearest-vertex error 0.000057 m), stable scene/collection/object, no unpacked image dependencies, and zero boundary/nonmanifold edges across all 12 mesh objects.
