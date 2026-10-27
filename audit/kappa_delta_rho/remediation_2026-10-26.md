# Kappa Delta Rho — post-grade remediation (2026-10-26)

- Preserved the stable asset ID, scene, exported collection, house object, and GIS FID 801 footprint.
- Rebuilt roof planes as closed 0.16 m slabs and the interior diagram floor as a closed 0.12 m slab. The previous roof mesh had 68 boundary/non-manifold edges; fresh-open topology now reports zero boundary and zero non-manifold edges across all ten mesh objects (`topology_report.json`).
- Added a camera-facing “SCHEMATIC INTERIOR | NOT SURVEYED” note to the interior preview only. No inferred sign was placed on the house.
- Fresh-open validation passed in Blender 5.2.3. Exact current SHA-256 is recorded in `fresh_open_report.json` and `build_report.json`.
- The source search still did not locate an identified facade photograph for the exact 1134 Northwestern KDR building. The model retains its facade as a clearly labeled estimate; the unrelated Kappa Delta Sorority and other KDR chapters remain excluded.
- Interior layout is schematic and not based on a floor plan. Roof form/color is supported only by aerial evidence; facade color, fenestration, trim, portico, and dormers remain uncertain.
