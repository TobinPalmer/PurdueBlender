# Independent Knoy review

Rating: 5.4/10 (exterior 21/30, texture 11/20, interior 9/30, technical 8/10, evidence 5/10). Not a completion certification.

Reviewed source by offline Blender reopen and read-only top cutaway render reviewer_cutaway.png. No source or master edited. Ground trace wall bounds are Z0.15–2.95m, correctly above ground slab. Axis swap maps the source horizontal wing onto the model north-south wing. Overall silhouette correspondence is plausible, but .126m/pixel and .13m/pixel introduce 3.17% anisotropy without a documented calibrated source measurement. Claimed ±1.5m is an estimate, not measured registration residual.

Specific actionable defects:
- Continuous crossing office grid creates enclosed cells without doors or a clear accessible corridor. Split walls at evidence-supported door positions. Avoid presenting full crossed grid as accurate rooms.
- Long continuous ground partitions omit door openings; trace source wall gaps explicitly.
- Upper floors and basement do not have verified room layouts or finishes. Furnishings and vertical circulation remain incomplete.
- Existing roof equipment, story count and exterior details require photographic support; this review did not independently substantiate those features.
- Material names/colors alone do not verify brick course scale, mortar, UV distortion or indoor finishes. Need oblique exterior shader render and eye-level interior render with reference comparisons.
- Register at least three identifiable plan perimeter corners to official footprint; report fitting residual and explicit north orientation instead of relying on approximate scale.

Source raster ground_plan.png visibly shows room divisions and corridor structure. Read-only cutaway confirms partial partition addition but lacks doors, interior finishing, and usable circulation. A score of9/10 would not be supported by current evidence.

## Final saved revision re-review

Reopened final63object source and re-rendered reviewer_cutaway.png. Independently measured18paired wall openings:1.0499987–1.0500009m. Asset root matrix remains identity. Access splitting is correctly implemented geometrically. These are provisional central openings, not verified source door positions, and no reachability analysis establishes access to every crossed-grid cell. Earlier blanket statement that all walls are continuous is superseded for these18segments; perimeter/corridor segments00–07 remain continuous.

Updated rating:5.7/10 (exterior21/30, texture11/20, interior12/30, technical8/10, evidence5/10). The access improvement earns interior credit; evidence and finishing limitations still prevent9/10. The cutaway shows remaining cross-grid enclosed subdivisions, particularly toward the outer diagonals. Door registration, usable corridor routes, upper-floor partitions, stairs, finishes, furnishings and verified material scale remain required.
