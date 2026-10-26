# Daniel Turf Center r2 iteration evidence

## Review findings addressed

- **Identity:** retained GIS FID 208 / DANL at 1340 Cherry Lane; the stale FID 855 is Old Purdue Exponent Building and rejected. TREC remains excluded as a separate facility.
- **Area:** corrected the apparent discrepancy by calculating the FID 208 ring shoelace area in its native EPSG:3857 coordinates. It is 1170.62890625 m² vs `Shape__Area=1170.62109375 m²`, a 0.0078125 m² difference. The local projected area of 677.0611 m² is the ground-scale approximation; Web Mercator's area is inflated by latitude distortion.
- **Roof vs wall line:** Esri World Imagery overlay places the GIS ring on the roof projection. The ring remains the massing plan boundary, but the audit now states that no wall-line/overhang survey was found.
- **Roof evidence:** retrieved the exterior photo attached to the June 11, 2011 J&D Turf / Smart Turf report. The caption immediately preceding the image identifies it as the Daniel Center building exterior. It shows a long, low, one-story metal-clad form with a shallow gable, centered entry canopy and windows. The gable ridge was modeled parallel to the long GIS axis. No detailed facade features were modeled.
- **Height:** removed the unsupported `Extrution=14` → 4.2672 m conversion. The raw GIS value is stored uninterpreted. The shell has low-confidence visual-only eave (3.25 m) and ridge (4.05 m) scale estimates because the exterior photo gives no calibrated dimensions and no measured elevation was located.
- **Proposed design references:** Purdue expansion artwork and Synthesis feasibility renderings remain excluded from as-built inference.

## Rebuild and reopen check

Rebuilt with Blender 5.2.3 LTS using `modular/buildings/build_massing_purdue_university_daniel_turf_center_e69b7da.py`. Clean-process reopen validation: PASS. One mesh in the stable asset collection; 28 vertices, 53 edges, 27 faces; no modifiers; one closed manifold shell; no unpacked external images; FID 208/address identity verified; maximum source ring XY error 0.0000777 m. Reopened bounds are X −1408.48047 to −1363.87646 m, Y 1609.48889 to 1627.12952 m, Z 0 to 4.05 m.

The Z bounds are modeling-scale estimates rather than source-backed survey dimensions. Blender shape, material, and display detail should be graded as massing, not a construction-accurate facade model.
