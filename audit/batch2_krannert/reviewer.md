# Independent Krannert review

Rating: **5.7/10 (57/100)**. Exterior 20/30; textures 13/20; interiors 9/30; technical 8/10; evidence 7/10. This is partial completion, below the requested 9/10.

Reviewed improve.py, open_windows.py, refine.py, checks.json, exterior.png, drawingroom.png, parrish.png and official tour page 4. Source asset changes preserve the named collection. Image dependencies check reports none missing. Parent reports Google Maps Street View March 2026 comparison; I did not independently view that browser session.

Improvements: physical window openings; restrained bump distance; furniture corresponding to publicly documented room identities; oak grain refinement; chair direction and stool support corrections. Room XY and dimensions remain inferred.

Actionable findings:

- Parrish study desktops are floating: improve.py creates desk tops and chairs but no desk legs. Add supports before accepting.
- Library photo has distinctive upholstered booth seating, dark counter surfaces, warm wood dividers, ceiling lights and varied book colors; most remain absent. Current low shelves are generic approximations.
- Interior renders show largely empty open floors with generic flat ceilings, no room partitions, doors, ceiling fixtures, signage or documented circulation. Two furnished areas do not complete the ten-level building.
- Drawing Room partitions and furniture are blocky, material appearance remains simplified; directional wood revision improves the shader but no calibrated material sample exists.
- Exterior full-height dark facade gap near right of center needs an explicit source comparison. Basement preview below a thin site plane should be presented with correct grade masking.
- Verify masonry normals after opening reconstruction and inward solidify. The render alone cannot establish watertight geometry.
- Heights, roof details, exact furniture placement and complete interior dimensions remain unverified. Google Maps exterior evidence cannot establish interior accuracy.

No geometry or source library files edited by reviewer.
