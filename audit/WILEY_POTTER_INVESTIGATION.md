# Wiley and Potter placement investigation

Reviewed 2026-10-22 against `official_building_references.json` and `object_world_bounds.json`. Measurements below use the existing campus coordinate convention in meters. They demonstrate specific defects but do not certify a correction from aggregate extents alone.

## Wiley: residence model anchored at the dining court

`test_wiley_import.py` imports `Wiley_Street_View_Reconstruction.blend`, including residence floors and common blocks, then adds **(-599.2, 125.6)** to every imported object. This anchor is near official **WDCT, Wiley Dining Court**, centroid (-597.574,124.804). Official **WILY, Harvey W. Wiley Residence Hall**, lies to the north, centroid (-595.820,230.372).

The inventory's material-joined limestone shell measures 80.560 by110.520 m. Its actual world bounds are X[-639.480,-558.920], Y[70.340,180.860]. This long north/south envelope is incompatible with the dining court footprint's roughly81.605 by46.645 m extents. It is closer in proportions to the residence hall's roughly90.326 by119.215 m extents. The imported hall has therefore been placed around the dining court location. Imported source naming and floor-count contents support the residence identity; inspect actual wall topology to resolve the remaining discrepancy.

Official residence bounds: X[-640.174,-549.848], Y[174.463,293.678]. To align west and east edges independently would require X translations of **-0.694 m** and **+9.072 m**, respectively. South and north edges would require Y translations of **+104.123 m** and **+112.818 m**. These differences prove that a translation alone cannot align the shell's complete envelope.

An AABB-center translation of approximately **(+4.189,+108.470,0)** would move this model from the dining-court location toward the residence hall, but is only a candidate gross relocation. It is not an evidence-certified footprint fit; shape, width, depth, orientation, and detailed source identity need review before acceptance. Do not scale the entire model from these bounds. WDCT should remain a separate building asset.

## Potter: displaced, narrow handcrafted core

`correct_walc_orientation_and_detail_surroundings.py`, function `build_potter_center_detailed`, explicitly generates `Potter_Center_Masonry_Core` at (82,-10,7.75), size(46,68,15.5). The saved scene confirms bounds X[59,105], Y[-44,24]. This is a rectangular invented mass, while the official POTR polygon is irregular.

Official POTR bounds are X[77.820,136.272], Y[-18.037,49.395]. West and east matching independently require X translations of **+18.820 m** and **+31.272 m**; south and north require **+25.963 m** and **+25.395 m**. The X disagreement of12.452 m proves a material width mismatch. Y span differs by0.568 m; official rotated rectangle is58.389 by67.486 m, compared with the modeled46 by68 m.

An AABB-center candidate shift of **(+25.046,+25.679,0)** would relocate the core toward POTR, but cannot establish accurate exterior geometry. Source centroid difference differs because POTR is asymmetric. The correct repair is to rebuild or revise the structural outline against the official polygon, retaining interiors and facade components only where compatible. The handcrafted15.5 m height remains unverified; official floor count is not a surveyed height.

## Disposition

Both flags are real concerns supported by script and world-bound evidence. Neither has a rigid translation satisfying all exterior-edge checks. No Blender edits were made during this investigation. Any gross relocation should be labeled provisional, with shape/dimension validation still outstanding, rather than reported as a fully accurate repair.
