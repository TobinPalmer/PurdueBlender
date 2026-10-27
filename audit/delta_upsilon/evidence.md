# Delta Upsilon — coordinator integration record

**Status:** independently graded 8.4/10 on exact asset SHA `94ce070ec9329d2ed1ba4f8dc264a55f9e3eb5d682190948d570f29d8fef7328`; coordinator master integration in progress.

The Purdue Campus Map BuildingShapesZip4 FID 751 record identifies Delta Upsilon at 1300 Stadium. Its nine-vertex WGS84 boundary was projected using the project approximation, and the detailed wall base follows that ring within 0.00000088 m. The source collection is local-coordinate geometry centered at `(-1057.421769, 496.563548)` m; the master `Placement_massing_house_301841256_1cc7641` marker must use this origin.

The official 2023 chapter photo supports the red-brick facade, blue sash glazing, light stone window surrounds and bands, entry treatment, and freestanding sign. The low intersecting roof was interpreted from aerial imagery. Roof shape, story heights, and total height remain estimates; no reliable floor plan was found, so no interior is modeled. These limits and source provenance are in [`sources.md`](sources.md); the independent score and exact-SHA reopen are in [`independent_grade_codex/result.json`](independent_grade_codex/result.json).

The coordinator rebuilt the master and independently reopened it in Blender 5.2.3. The exact asset hash, linked library, and `Placement_massing_house_301841256_1cc7641` marker at the documented centroid passed; the manifest world bounds agree within 0.001 m, and no duplicate direct campus-root collection remains. See `master_integration_2026-10-26.json`.
