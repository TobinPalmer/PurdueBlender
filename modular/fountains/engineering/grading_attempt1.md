# Independent Engineering Fountain grade — attempt 1

Reviewed 2026-10-22. Read-only review of build.py, EVIDENCE.md, position_measurement.json, particle_verification.json, dry render, and official Purdue photograph. Independently opened primary source https://www.purduealumnus.org/class-of-1939-water-sculpture/campus/ confirming stated 38ft structural height, historical 588gpm upward jet, 2001 stainless cylinder, and incised patterns.

**Score: 4.9/10. Not accepted.**

| Criterion | Score | Reason |
|---|---:|---|
| Position and dimensions | 1.1/3 | Height uses sourced 11.5824m, but top is actually .12+11.5824=11.7024m in world coordinates. Attempt center from map viewport is approximately 20.3m from measured OSM feature centroid. Plan dimensions, orientation, and elevation lack verification. |
| Architecture and detail | 1.0/2 | Recognizable sweeping fins and segmented perimeter. Photo contains substantial incised relief, outer wall openings, plaza paving, and wider foot profiles absent in dry render. One photograph cannot establish all hidden geometry. |
| Actual fluid and physical behavior | 1.0/3 | Real FLIP particle evidence exists through frame48. Final mesh sequence and wet renders pending. Enlarged emitter materially changes discharge; open bottom is a drain surrogate, deck does not collide. No established measured current jet envelope. |
| Portability and master compatibility | .8/1 | Relative cache and separate collection good. Must confirm full bake, reopen, master link, and cache lookup after relocation. |
| Evidence and uncertainty | 1.0/1 | Primary reference, raw OSM, numeric residuals, and limitations are candid and retained. |

Priority corrections:
1. Translate sculpture, domain, inflow, and cameras coherently to OSM feature centroid; document OSM accuracy unknown and avoid calling this surveyed placement.
2. Complete data AND mesh caches; render multiple nonempty frames and compare time behavior. Independently inspect emitted volume or explicitly retain uncalibrated-flow status.
3. Add visible incised relief and perimeter wall detail with photographs supporting placement; do not manufacture a precise architectural claim.
4. Verify top height relative to intended base datum and resulting fin span; actual span is 11.5824m, while world top is 11.7024m.
5. Test linked master reopens and uses the baked domain without inflow displaying as geometry. Avoid multiple simulation domains or duplicate old fountain remnants.

A completed simulation alone cannot justify 9/10. Position error, underresolved discharge, and architectural omissions materially limit fidelity. Score describes this reviewed state, not the planned corrections.
