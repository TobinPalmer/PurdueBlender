# WALC independent grade — R4

**Result: 7.9/10 — below the 8.0/10 completion threshold.** The façade is meaningfully improved over R3, but the building’s roof and principal elevation still diverge enough from the official exterior reference to keep the result just below threshold.

**Asset SHA-256:** `01f0ba7bd8fbdee2da267e85c8d35e327cf891d68a05cbeea5876b5b692b5dd4`  
**Independent reopen:** I reopened the exact standalone asset in a fresh Blender 5.2.3 LTS background process. The asset hash matched. `Asset_walc` contained 954 objects / 882 meshes; the root transform was identity; all meshes had valid material assignments; no external images were missing; the relative foliage library resolved. The traced roof object remained at 156 vertices and retained the reported bounds. Full details: [independent_grade_r4_reopen.json](independent_grade_r4_reopen.json).

## Scorecard

| Category | Score | Findings |
|---|---:|---|
| Identity and plan footprint | 2.0/2.0 | The GIS FID 906 traced footprint and roof polygon are retained. This is agreement with the source used during authoring, not a separate building survey. |
| Local frame and structure | 0.9/1.0 | Root is identity, and the relative foliage library resolves. The standalone review does not verify the campus master placement or neighboring alignment. |
| Exterior architecture | 1.4/2.0 | Deep brick fields and substantial piers create clearer façade bays than R3’s thin blades. However, the long elevations still read as repetitive, small, evenly spaced windows rather than the reference’s mix of grouped tall windows, larger glazed pavilion, and distinctive roof/eave silhouette. The broad flat gray roof and pale inset remain the largest visual mismatch. |
| Materials and surface finish | 1.05/1.5 | Brick, stone and glazing are separated more clearly, and daylight is readable. At these views the brick is mostly a uniform red-brown field, glazing is flat blue-gray, and the roof and paving are broad flat surfaces. The source photo has more material variation and shadow depth. |
| Interior and program | 1.45/2.0 | Existing library, atrium, classroom and circulation spaces remain useful as a schematic program model. R4 did not change them; published plans support program/layout context but are not registered to verify exact room positions, finishes or as-built partitions. |
| Reopenability and evidence | 1.1/1.5 | Independent exact-hash reopen succeeded; foliage path, packed image texture, root and mesh material slots check out. Three daylight views and official program/photo sources are documented. Roof elevations, interior as-built geometry and master placement remain unverified. |
| **Total** | **7.9/10** | **Below threshold.** |

## R4 assessment

R4 fixes the specific R3 problem: long horizontal bands now have visible brick fields and deeper piers, with window frames and grouped glazing. This is a real, legible improvement in the southwest, southeast and north renders. It does not fully reproduce the façade rhythm in Purdue’s official 2018 exterior photograph. The model’s main long walls show repeated small openings and a mostly continuous upper brick field; the reference has more variation in window proportions and groupings, a substantially glazed central entrance/pavilion, and strong eaves.

The roof remains unresolved. In all three saved views, a large flat gray plane dominates; the pale roof inset and narrow monitor do not match the prominent sloping roof/eave form visible in the official exterior photo. R4’s change log explicitly leaves roof geometry unchanged, and the 156-vertex GIS trace establishes an outline only, not roof form or height. This discrepancy weighs heavily because the roof is visually dominant in the model views.

The R4 daylight images use a neutral background and make the architecture easy to inspect, but surface response still feels schematic. Procedural brick patterning is not apparent at campus viewing distance, limestone surrounds have little relief, and the glazing lacks reflected environment/detail. The interior is unchanged and remains a programmatic visualization, not a verified as-built interior.

## Requirements for R5

1. Verify the roof silhouette, eaves, central pavilion and roof-level changes from authoritative oblique images or architectural elevations. Avoid treating the GIS roof outline as roof-form evidence; document estimates where measured data is unavailable.
2. Refine the principal elevation’s window proportions and groupings against the official image, including a visibly larger central glazed pavilion/entry and the solid brick-to-window balance.
3. Improve readable brick, limestone and glazing surface response at ordinary pedestrian/campus views, with relief and lighting/shadow depth that do not obscure the architecture.
4. Render at least one eye-level view from the official-photo direction and one overall oblique view. Recheck north and southeast elevations for consistent bay logic.
5. Keep interior positions/layouts labeled schematic unless scale-registered architectural plans or survey evidence are found; separately verify master `Placement_walc` in the integrated campus scene.

## Sources and limitations

- Purdue, [Then & Now: Wilmeth Active Learning Center](https://www.purdue.edu/newsroom/archive/purduetoday/releases/2018/Q4/then-and-now-wilmeth.html) and the associated [official 2018 exterior photo](https://www.purdue.edu/uns/images/2018/pt-wilmeth-6446.jpg). The photo supports architectural appearance but is not a measured elevation.
- Purdue, [WALC Classroom Floor Plans](https://www.purdue.edu/activelearning/walcrooms1/WALC_Classroom_FloorPlans.pdf), for published classroom program/configuration context, not survey-registered model geometry.
- Purdue Chemistry, [Wilmeth Active Learning Center](https://www.chem.purdue.edu/media/news/2017/wilmeth.html), and [Purdue WALC emergency plan](https://www.purdue.edu/operations/emergency-preparedness/walc/), for program/story-count context rather than exact as-built room geometry.
- Cached Purdue campus GIS BuildingShapesZip4 FID 906, as referenced in the R4 authoring log, supports the modeled plan trace only.
- I inspected `southwest_r4_daylight.png`, `southeast_r4_daylight.png`, `north_r4_daylight.png`, and `purdue_wilmeth_2018_official.jpg`. No master scene was opened, so this grade does not assess campus placement.

**Scope:** Only this independent report, its JSON score, and its separate reopen evidence were written under `audit/walc_refine/`. No `.blend`, master, or shared asset was modified; no commit was created.
