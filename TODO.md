# Master blend integration handoffs

These building assets are independently graded at or above 8/10 and pushed to `master`. Tobin owns the master blend and should integrate each latest asset, place it from the manifest coordinates, remove or replace any older instance, and reopen the master to verify placement.

- **Cary Quadrangle South (CQS)** — pass: 8.5/10 (`audit/massing_cary_quadrangle_south_cqs_independent_grade/result.json`); model commit `17d6cb7c20f9090f34b6a0cae734779ca42f2fdc`. Asset: `modular/buildings/massing_cary_quadrangle_south_cqs_7ee2283.blend`. Replace the current master massing block with this library, verify placement and bounds, and reopen the master.
- **Burton D. Morgan Center for Entrepreneurship** — pass: 8.4/10 (`audit/burton_morgan_center_independent_grade/result.json`); model commit `d8df63f`, grade commit `a1ce3b2`. Asset: `modular/buildings/burton_morgan_center.blend`. Replace the corresponding master massing block with the detailed asset, verify its `Placement_burton_morgan_center` instance and placement, then reopen the master.

