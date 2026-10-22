# Independent review — attempt 4

Reviewed 2026-10-22. Actual score: **8.0/10**. One implementation attempt remains. This is a source-limited reconstruction, not surveyed or fully dimensionally verified.

| Criterion | Score |
|---|---:|
| Geographic placement, orientation, footprint | 2.6/3 |
| Supported dimensions and architecture | 1.9/3 |
| Visible materials and details | 1.0/1.5 |
| Honest interior/floorplan treatment | 1.5/1.5 |
| Asset integrity | 1.0/1 |

## Independent checks

Read AGENTS.md, EVIDENCE.md, official_BELL_reference.json, verification.json and inspected all three current renders against the official base photograph, 2016 and 2006 full photographs, and clock closeup. Reopened the saved asset in a separate Blender 5.2.2 process using grading/independent_check.py; output is independent_check.json. Export contains 541 objects, no cameras/lights or external image/library dependencies. Measured shaft width/depth 5.486313m, center (-31.1215935,-12.9836273), rotation 39.360973deg, highest geometry 48.767998m. These agree with the supplied mapped reference/model convention. This independently checks geometry, not the GIS provider's survey precision.

Opened Purdue's original 2020 news release directly: https://www.purdue.edu/newsroom/archive/releases/2020/Q4/university-to-mark-25th-birthday-of-purdue-bell-tower.html . It supports approximate 160ft overall height and red brick/limestone, but not subordinate dimensions. The documented caveats about the map envelope, vertical datum, estimated subdimensions and representative plaque are necessary and appropriate.

## Actionable corrections for attempt 5

1. **Clock lower facade:** the 2016 and 2006 photographs show a framed rectangular panel beneath each clock and a substantially projecting wedge/sloped hood below it. Current render shows an exposed dark horizontal louver with a thin flat sill. Reproduce the visible frame and hood geometry, using photographic proportions explicitly labeled estimated. Do not claim the interior vent function is verified.
2. **Belfry support details:** real corner supports show conspicuous longitudinal recesses/channels and layered projecting capital/joint blocks in the 2016 photo. Current broad flat square columns and small added strips look appreciably simpler. Add clearly visible recessed column faces and cap profiles where photo evidence is sufficient; retain uncertain rear/internal support arrangements as estimates.
3. **Base arch keystone:** official Purdue photo shows a trapezoidal projecting keystone widening toward its upper end and an underside panel/lighting treatment. Current long rectangular strip down the arch reads as a simplified applied board. Prioritize a tapered keystone matching the visible outline, then add only photo-supported underside panels/lights if feasible.
4. **Clock typography and hands:** current stock font is thin and compact compared with the strong narrow radial Roman numerals and shaped hands in reference_clock.jpg. Improve proportions if feasible, preserving correct XII-top orientation. Exact shown time is not a static fidelity criterion.

The first three corrections are the highest-value final pass. Do not change geographic placement or scale solely to improve a perspective photograph match.

## Remaining limitations

No measured floorplans or elevations establish clock diameter, arch spring heights, belfry dimensions, roof pitch, bell sizes, actual ground elevation or mechanism details. Four modeled bells and clocks are visible, but shape/arrangement are not dimensionally verified. The model successfully captures the major silhouette, central brick strips, continuous open limestone base and pyramidal seamed roof. The evidence does not justify a 9/10 fully supported accuracy grade at this stage. A perfect map-center residual is fit to a reference representation, not absolute positional certainty.
