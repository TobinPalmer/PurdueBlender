# Hovde Hall — round 11 source-model revision

Round 10 received an independent 7.6/10. This focused revision responds to the review direction to make the capitals read more clearly as restrained leafy Corinthian forms and deepen the sheltered entry. Roof geometry and material were left unchanged because available roof-specific evidence does not support further edits.

## Round 11 changes

- Replaced the previous small capital relief with six pointed, ribbed limestone leaf blades per capital. Their restrained, vertically layered outline follows the leafy carving visible in Julian Herzog’s 2016 exterior photo. Exact leaf count, carving, and dimensions remain interpretations from the photograph.
- Shifted the six-column front portico assembly outward by 1.15 m in the building’s local frame. The entry doors and facade windows remain in their original positions, so the modeled sheltered threshold is deeper. The added projection is a visual estimate from the photo, not a surveyed measurement.
- Retained the terracotta tile pattern, low roof edge, and roof silhouette. The photo supports the red tile roof; no roof plan or measured profile was found to justify extra changes.

## Reopen and render check

Blender 5.2.3 reopened the saved source asset, rendered comparison views, and produced `final_asset_check_round11.json`. The check reports 754 exported objects (740 meshes, two curves), no unmaterialed meshes, valid face indices, six columns at 0.79 m diameter, preserved root location `[-62.85, 93, 0]`, Z rotation `0.689754 rad`, and unit scale. The master/GIS alignment was not checked in this building-only pass.

- `same_angle_reference_round11.png` — near-frontal comparison with the 2016 photo.
- `portico_detail_round11.png` and `portico_oblique_round11.png` — entrance and door/window relationship.
- `portico_capital_close_round11.png` — elevated close view of the leaf relief.
- `roof_detail_round11.png` — roof silhouette/material retained from round 10.
- `round11_edit.py`, `round11_refine_caps.py`, `render_round11.py`, `render_capital_close_round11.py`, and `final_check_round11.py` record the source-only build/review steps.

## Remaining limits

The portico projection, dimensions, roof pitch, and column spacing are visual estimates. The photo is perspective imagery with tree obstruction; it is not a calibrated elevation. Capital carving and entablature details are interpretations. Hidden roof structure and interior plans are unverified. Coordinator review remains necessary for GIS registration and the master placement marker.

**Ready for a fresh independent grade.**
