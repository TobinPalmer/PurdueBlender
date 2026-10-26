# Kappa Sigma massing evidence

Stable asset ID: `massing_kappa_sigma_c1b36ec`, assigned to Rossen. The source library remains `modular/buildings/massing_kappa_sigma_c1b36ec.blend`, with scene `Building_massing_kappa_sigma_c1b36ec`, collection `Asset_massing_kappa_sigma_c1b36ec`, and object `Kappa Sigma`. It remains a simple massing asset in campus coordinates with identity object transform.

Purdue GIS BuildingShapesZip4 FID 804 names Kappa Sigma (SOKS) at 308 North St. The 66-vertex boundary was transformed directly using the project's local lon/lat approximation and now drives the wall perimeter. A separate Indiana 2018 LiDAR-derived feature (objectid 410022) overlaps the Purdue outline at IoU 0.8294 with 1.10 m centroid separation. The current Indiana orthophoto is saved with the FID overlay. Source URLs, dates, CRSs, measurements, and uncertainty are in [evidence.json](evidence.json); raw responses are in [sources](sources/).

The old mesh was a 24-vertex rectangular mass with measured bounds 41.97 x 22.30 x 16.0 m, using the manifest's identity transform. It was rebuilt from the source polygon: brick shell, repeated pale window trim and dark glazing, a central entry canopy/step, three front gables, and a chimney. The exterior photo supports red brick, three visible facade levels, repeated windows, an entry, raised KΣ letters, front gables, and a chimney. The 9.6 m wall top, 12.0 m gable ridges, 13.7 m chimney top, individual opening locations, gable extents, and roof pitches are estimates. The GIS `NUM_LEVELS` / `CountOfFLO` fields say 1 and `Extrution` is 12 with no documented units; those fields do not establish the visible height.

The chapter's alumni contact page associates its Chi Chapter with 308 North St. A current 308 North Street housing FAQ says the property is independent housing, not affiliated with an active fraternity or Purdue. The repo's historical building identity and GIS match are preserved; the model does not assert current fraternity use or current KΣ signage.

## Build and validation

- [build_massing_kappa_sigma_c1b36ec.py](../../modular/buildings/build_massing_kappa_sigma_c1b36ec.py) generates the single named mesh inside the expected asset collection.
- [build.log](build.log) records the successful Blender 4.5.15 build and render.
- [kappa_sigma_preview.png](kappa_sigma_preview.png) is the rendered facade view.
- [orthophoto_with_purdue_outline.png](sources/orthophoto_with_purdue_outline.png) compares the FID 804 and LiDAR 410022 outlines against the current aerial; [footprint_comparison.json](footprint_comparison.json) stores the calculated overlap and centroid separation.
- [validate_kappa_sigma.py](validate_kappa_sigma.py) directly reopens the saved `.blend` and checks the expected scene/collection/object, identity transforms, evaluated bounds, and bottom-ring match to the transformed FID 804 coordinates within 0.01 m rounding (Blender mesh vertices use 32-bit floats).
- [reopen_validation.json](reopen_validation.json) contains results from that reopen check: one mesh object in the expected collection, identity transform, no modifiers or external image files, exact source-ring coordinate match within 0.01 m rounding, and zero boundary/non-manifold/wire edges.

The roofline details and all heights remain estimated. No master blend, manifest, README, BUILDINGS index, or TODO file was changed. This lane is ready for independent grading; coordinator should request a fresh grader before considering it complete.
