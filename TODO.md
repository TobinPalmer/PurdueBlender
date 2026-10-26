# Master blend integration handoffs

These building assets are independently graded at or above 8/10 and pushed to `master`. Tobin owns the master blend and should integrate each latest asset, place it from the manifest coordinates, remove or replace any older instance, and reopen the master to verify placement.

- **Chapel of the Good Shepherd** — pass: 8.25/10 (`audit/chapel_good_shepherd_5d4d103/independent_grade_r2/result.json`); model commit `9ef1a770b202bd9cb59a60d851b50a77ba6405e5`. Asset: `modular/buildings/massing_chapel_of_the_good_shepherd_5d4d103.blend`. Integrate the massing library into `purdue_campus_master.blend`, verify its campus placement, and remove this entry after integration.
- **Chaney-Hale Hall of Science (CHAS)** — pass: 8.15/10 (`audit/chaney_hale_hall_of_science_chas_independent_grade/result.json`); model commit `f8109a6b5c28a17ee8991c54e5b79d4033118c82`. Asset: `modular/buildings/massing_chaney_hale_hall_of_science_chas_6bb9ef7.blend`. Reload the directly linked library in `purdue_campus_master.blend`, preserve its campus position, and verify it appears once; remove this handoff after integration.
