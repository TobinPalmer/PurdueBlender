# Lyles-Porter Hall — independent full-building review, round 1

**Score: 8.2/10 — passes the project's 8/10 threshold.**

| Criterion | Score |
|---|---:|
| Identity and source-backed footprint | 1.9/2 |
| Position, orientation, and scale | 1.8/2 |
| Height, floors, and roof | 1.4/2 |
| Facade, entrances, and distinctive features | 1.4/2 |
| Modular export, portability, and evidence | 1.7/2 |
| **Total** | **8.2/10** |

## Evidence and inspection

I inspected the saved asset and its evidence package directly. An independent Blender background read measured the 40-vertex shell base face at **3,524.4204 m²**. The raw 131-vertex Purdue GIS ring measures **3,520.2580 m²**, a **0.118%** area difference; the GIS envelope bounds match the model's local envelope. The master `Placement_lyles_porter_hall` marker is at the manifest origin `(-257.675, -717.457, 0)`, with zero rotation and unit scale. This verifies the modular transform against the project's GIS-derived coordinate convention, but not against a surveyed control point.

Purdue's current emergency plan describes Lyles-Porter Hall as three stories plus a partial basement, with clinical, classroom, research, fitness, and mechanical uses across its floors. The modeled three-story volume, partial basement, brick exterior, pale horizontal precast bands, punched glazing, entrance canopy, and roof equipment are broadly consistent with the sources. Purdue's 2014 building photos and the 2018/2026 Street View references support the exterior materials and general window rhythm.

The saved export collection reopens with 11 objects (10 meshes), 10 materials, nine texture-connected materials, and no external image paths. The evidence package contains the raw GIS record and source metadata. The included preview reads well as a massing/exterior view, but does not demonstrate the interior in much detail.

## Limits

The source GIS footprint is generalized and the model simplifies it by 0.4 m. GIS vertical field units are not documented; the 45 ft roof datum and mechanical heights remain estimates. The basement extent, roof form, and exact facade bay dimensions are not survey-verified. Interior objects are illustrative rather than a dimensioned plan; the source mentions 30 audiology/speech sound booths, but the model shows only a schematic cue. These limitations remain recorded in `evidence.json` and do not outweigh the strong footprint, identity, and broad facade agreement for the project's minimum acceptance score.

The evaluator function and criterion-level evidence are in [`independent_review_round1.py`](independent_review_round1.py). The score is an acceptance grade, not a claim that every architectural dimension has been surveyed or verified.
