# Rawls Hall round 4 handoff (2026-10-23)

## Saved asset

`modular/buildings/rawls_hall.blend` was saved, then reopened by the round 4 exterior, north-front, ray-check, and `final_checks.py` runs in Blender 5.2.3. The export collection remains 722 objects / 714 meshes, the root is identity and unparented, and no external image dependencies are missing (`checks.json`). No master blend, manifest, shared script, or other building was edited.

## North facade repair

The previous +0.60 m pane shift was unsupported. The north glass and frames now use +0.08 m world Y; measured glass and wall planes put the panes about 1–3 cm from the outer reveal at sampled X positions. The north wall was a continuous front and back skin over all 60 pane quads. Those two faces were replaced by masonry panels using the existing pane extents, with 60 openings and brick reveal returns. Neighboring wall faces and the original shell bounds/material assignment were preserved. The bronze object had 60 solid window-sized box panels (360 faces) that masked the glass; it now contains four narrow perimeter bars per pane (55 mm strip width, 40 mm depth), following the glass plane. This lets the blue-gray low-roughness glass and its reflections show in the rendered north facade.

## Verification and images

`round4_aperture_ray_checks.json` records nine rays distributed across three window bays and three floor bands. Each ray reaches the north glass, then continues to interior plan geometry or the opposite building skin. The exterior skin does not block those pane centers.

Useful views: `exterior_round4.png`, `north_aperture_after_rebuild.png`, `north_glazing_closeup_round4.png`, and `north_glazing_oblique_round4.png`. The facade closeups show blue-gray glazing, reflected light, slim bronze perimeter frames, limestone sills, and the existing brick mapping. The standard oblique/hero view is still stylized and does not establish exact current facade tint or survey fit.

## Remaining limits

The 2024 Purdue first-floor plan is the layout source; current upper-floor partitioning and atrium circulation remain estimated. No dimensioned control point resolves Plan1086's edge; the existing 1–2 m GIS registration uncertainty remains. The Google Maps observation has no reproducible facade capture date, and the saved historical Purdue atrium imagery supports broad character only. The Rawls asset is ready for independent round 4 review; no 9/10 score is claimed before that review.
