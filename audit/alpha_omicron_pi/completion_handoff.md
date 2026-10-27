# Alpha Omicron Pi candidate handoff

Prepared 2026-10-27. R1 revision candidate; awaiting the coordinator's fresh independent R2 grader.

## Identity and crosswalk

The assigned README entry was conflicting. The current AOII Phi Upsilon chapter site identifies its house at **242 S Grant St**. That location matches the parcel-aligned source asset `massing_house_970455277_a3fb72a` / OSM way `970455277`. It does not match Purdue GIS FID 756. Current Phi Sigma Rho information identifies 1001 David Ross Rd, consistent with the FID 756 location. Therefore I modeled AOII in the 970455277 source asset and left `massing_house_301841607_63d85b5.blend` (the FID 756 asset) untouched. Supporting material and uncertainty are in `source_register.json`.

**Coordinator shared-file follow-up:**

1. Correct the README AOII row: remove the FID 756 association and point it to `massing_house_970455277_a3fb72a.blend` / 242 S Grant; preserve the Tobin assignment as appropriate.
2. Reconcile FID 756 to the Phi Sigma Rho building at 1001 David Ross and correct the Phi Sigma Rho row (currently README says FID 744 with no asset). Independently check FID 744 before reassigning it; do not silently delete it.
3. The current manifest entry for `massing_house_970455277_a3fb72a` is `kind: massing`, expects object `House_970455277`, uses campus-world geometry, and has direct-identity placement. Change it to a detailed local-geometry instance after the grader accepts this candidate. Preserve ID, file, scene, and collection names. Replace the stale expected object/count/bounds metadata; this asset contains 1,780 meshes, not the old single mesh.
4. Create/update `Placement_massing_house_970455277_a3fb72a` at **(308.7021179199, -719.9722595215, 0) m** in project campus XY, with identity rotation and scale. Detailed geometry was recentered at this origin. Keep project conversion/origin unchanged.
5. In the master, remove the old direct-linked campus-coordinate massing instance for this AOII parcel and link/instance the detailed collection once through that placement marker. Do not replace FID 756's asset with this model.

## Candidate geometry

- Exact GIS footprint polygon retained from the original asset, transformed to local XY; area 276.2303 square meters. Local footprint vertices are recorded in `source_register.json`.
- Ground-level brick facade and centered entry, with parking access on the east alley side; two beige horizontal-siding residential levels with dark shutters on the Grant-facing elevation; screened parking openings, terrace in the northeast footprint notch, shallow hip roof, downspouts and planters. Street-facing materials and roof were revised from direct March 2026 Street View evidence; see revision_r1.md and source_register.json.
- Plausible but explicitly estimated interior: garage supports and stalls, shared kitchen/dining/lounge/study, and 15 bedroom bays. No plan or room layout was claimed as measured.
- Fresh-opened in Blender 5.2.3 LTS. Scene and collection names are preserved. Validation found 1,780 mesh objects, 14 materials, bounds including decorative/site geometry X[-11.300, 8.212] Y[-10.012, 10.012] Z[-0.100, 9.785] m; three renders are included.
- Asset SHA-256: `3ac83c2841058b6de3a7f19c587e151df6b3751589a82f03ecf1c6460da5ec7`. Build script SHA-256: `014e9ae03861455294898ff60767fc9fdf5d2ba19adb78be571b540be7ccfeea`.

## Inspection renders

- `preview_front_west.png`
- `preview_entry_isometric.png`
- `preview_terrace_aerial.png`

## Remaining verification

Exact as-built elevations, facade/window schedule, roof details and interior plan remain unverified. The city staff report is a 2015 planning document, not an as-built survey. Contractor-reported floor area does not reconcile neatly with the footprint and modeled floor count. The model should not be integrated as finished until the fresh independent R2 grader reviews it against the saved sources and renders.
