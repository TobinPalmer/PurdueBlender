# Independent grade — Neil Armstrong Hall R12.8

**Score: 7.8/10** — below the project’s 8.0 passing threshold. I independently reopened the saved file with Blender 5.2.3 and compared current renders with the stored 2016 project photos and 2023 orthophoto evidence. The SHA-256 matched the requested R12.8 asset exactly.

## Saved-file check

The reopened `Asset_neil_armstrong_hall` collection contains 445 objects and 415 meshes. `AssetRoot_neil_armstrong_hall` is at local `[0, 0, 0]`; all mesh objects have material assignments, there are no null material slots, and no external images are missing. The canopy has 371 vertices and 342 faces. No duplicate-coordinate faces are recorded in the current validator.

## Criterion scores

| Criterion | Score | Evidence and deduction |
| --- | ---: | --- |
| Correct identity and source-backed footprint | 1.55/2 | Purdue’s Building Emergency Plan identifies Neil Armstrong Hall of Engineering (ARMS). The registered 2023 Indiana orthophoto supports the roof/eaves plan. Purdue GIS feature 642 is a generalized footprint and overlaps only part of the modeled roof slabs; it does not establish the structural wall or courtyard boundary. |
| Position, orientation, and scale/dimensions | 1.55/2 | Independent fresh reopen confirms the asset root at local origin. The manifest placement is `[-109.0, 400.1893310546875]` m, and the prior independent master-marker check recorded the same origin, zero rotation, and unit scale. The present R12.8 review did not reopen the whole campus master; wall stationing and measured dimensions remain unverified. |
| Evidence-backed height, floors, and roof form | 1.45/2 | Purdue’s BEP describes one lower level, grade, and two upper floors; FRP’s project description corroborates a three-story frame with basement and partial sub-basement. 2016 photos support a wing-like cantilever roof. R12.8 improves the thin edge and underside color, but the high roof/canopy remains a broad simplified inferred profile; the 21.5 m peak and shell warp are not measured. |
| Facade, entrances, and distinctive architecture | 1.45/2 | The asset retains brick and glass volumes, a curved glazed entrance, and the signature red-brown cantilever. R12.8 fixes duplicate deck/seam faces and improves the soffit. Current views still show broad plain brick faces and generic horizontal window strips where project photos show larger curtain-wall zones, framing, and sunshade outriggers; the folded wing and its relationship to the entrance remain approximate. |
| Modular export, portability, and complete evidence | 1.80/2 | Fresh Blender 5.2.3 reopen verifies the expected collection, 445-object export, identity root, complete mesh material assignment, and no missing external images. The folder contains source notes, validation, current renders, and independent evaluation. The evidence remains visual/generalized rather than a dimensioned as-built plan/elevation set. |
| **Total** | **7.80/10** | **Not passed** |

## Findings for the next iteration

1. Keep the 2023 eaves trace separate from the structural wall footprint. Find a measured plan or improve independent wall registration before changing wall geometry.
2. Rework the visible canopy silhouette and its connection to the glazed atrium from several photos. The thinner shell and red-brown soffit help, but the render still reads as a broad polygonal ring rather than the localized folded wing visible in the reference images. Keep canopy height and warp labeled as estimates.
3. Add evidence-backed curtain-wall and sunshade/outtrigger rhythm. The current facade remains too dominated by brick and thin generic horizontal strips relative to the project photos.
4. Keep the photo camera headings and roll uncertainty explicit; the views support qualitative shape/material comparison, not measured facade stationing.

## Sources inspected

- [Purdue Office of Emergency Preparedness — Armstrong Hall BEP](https://www.purdue.edu/operations/emergency-preparedness/arms/): current official four-level building description.
- [Kawneer — Neil Armstrong Hall of Engineering](https://www.kawneer.ca/projects/education/neil-armstrong-hall-of-engineering-purdue-university/): project photography and curtain-wall/sunshade system context.
- [Fink Roberts & Petrie — Neil Armstrong Hall](https://frpinc.com/projects/neil-armstrong-hall-of-engineering/): structural/project description, including the cantilevered truss and atrium bridges.
- [Wikimedia Commons — Purdue 2016 photo 01](https://commons.wikimedia.org/wiki/File:Neil_Armstrong_Hall_of_Engineering_Purdue_University_2016_01.jpg) and the locally reviewed 2016 photos 02–03.
- [Design and Build with Metal — project case history](https://designandbuildwithmetal.com/featured-projects/neil-armstrong-hall-of-engineering): project description; it does not provide dimensioned plans.
- Locally stored 2023 Indiana Current Imagery orthophoto and its registration record under `audit/complete_neil_armstrong/sources/` and `audit/neil_armstrong_hall_refine/`.

## Machine-readable evidence

- Independent fresh Blender probe: `independent_probe_r12_8.json`
- Builder validation and source limitations: `validation_r12_8.json`, `source_review_r12_8.md`
- Current rendered views: `renders_independent_r12_8/`
- Runnable evaluator and result: `independent_evaluator_r12_8.py`, `independent_grade_r12_8.json`
