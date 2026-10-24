# Hovde Hall — round 10 building-side revision

Round 9 scored 7.5/10. This revision directly addresses the coordinator's findings: the six shafts are slimmer; capital and entablature details follow the 2016 geotagged reference; the pediment profile is less squat; the roof has terracotta tile relief, a low eave tile lip, and no unsupported box penthouse; and the long facades gained recessed window surrounds and muntins.

## Source-backed changes

- **Portico supports:** retained the six supports visible in Julian Herzog's near-frontal 2016 photo; shaft diameter is now 0.79 m. The source confirms count and slender classical character but not exact column diameter or spacing.
- **Capitals and entablature:** added a flared echinus and abacus at each support, small paired scroll/leaf reliefs, a taller frieze/entablature, 37 dentils, separate cornice bands, raking moldings, and an apex acroterion. These features match visible photo cues; their detailed geometry and dimensions remain interpretive.
- **Pediment:** the triangular rise is about 5 m, with its base near z=11.8 m and apex near z=16.8 m. This is a visual estimate to match the source proportions, not a measured elevation.
- **Roof:** the existing low hip silhouette now has mapped terracotta tile courses and shallow relief. A short eave tile lip makes the red tile roof edge legible. The raised penthouse block was removed because it rendered as a large exposed box absent from the 2016 frontal reference; roof plans were not found, so hidden equipment and exact roof construction remain unverified.
- **Facade:** softened the brick/mortar contrast, reduced surface bump, and added pale stone reveals and fine mullions to the long facades. Window schedule and frame details are still approximate.

## Reopen and render check

Blender 5.2.3 reopened the saved source and rendered three views:

- `same_angle_reference_round10.png` — near-frontal 34 mm perspective from the entrance axis, compared with the 2016 photograph. The exact source camera location is unknown; this matches view direction, not a calibrated camera pose.
- `portico_detail_round10.png` — six slimmer supports, capitals, layered entablature, pediment, stair, and entry.
- `roof_detail_round10.png` — tile courses and low hip silhouette from above.
- `final_asset_check_round10.json` — 770 export objects, 756 meshes, 2 curves, no unmaterialed meshes, six columns, portico dimensions, roof material, and preserved root transform `[-62.85, 93, 0]`, Z rotation `0.689754 rad`, scale `[1,1,1]`.
- `round10_edit.py`, `render_round10.py`, and `final_check_round10.py` are the reproducible edit, evidence render, and reopen check.

## Remaining limits

- The 17.9 m portico width is an approximate image-ratio estimate compared with Purdue Archives' 70 by 230 ft record; uncertainty is about ±0.04 in the image ratio. No dimensioned elevation was located.
- No exact portico/roof dimensions, roof plan, window schedule, or interior room plan were available.
- Root placement and Purdue GIS feature 618 still require coordinator/master verification. The source model's local root transform was preserved.
- Room layouts remain interpretive and labeled as unverified in prior cutaway evidence.

**Independent round 10 score not yet assigned.** Send the reopened source, comparison render, roof view, and evidence record to a fresh reviewer.
