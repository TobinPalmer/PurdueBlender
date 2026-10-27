# Independent Grade — Lambert Fieldhouse R8 Candidate

**Score: 7.8/10 — FAIL (minimum passing score: 8/10)**  
**Candidate:** `audit/lambert_fieldhouse/lambert_fieldhouse_r8_candidate.blend`  
**SHA-256:** `b0e931109230641be77e8d3fc64cadf7d77c4e7d5f318e7fcf3103de7836124f`  
**Review date:** 2026-10-26  
**Independent reopen:** Blender 5.2.3 freshly loaded the saved candidate. The expected `Asset_lambert_fieldhouse` collection exists with 972 objects (967 meshes). I found 39 used materials, a packed brick image texture, no linked libraries, and 24 hurdle component meshes without material slots.

## Criteria

| Criterion | Score | Findings |
|---|---:|---|
| Correct identity and source-backed footprint | 1.8/2 | Facility identity and GIS footprint are well-supported. Purdue Athletics confirms six lanes and 200 m; the prior saved track measurement is 199.989 m. Historic archive dimensions support the major volumes, but do not register the volumes against the current GIS footprint. |
| Position, orientation, scale/dimensions | 1.4/2 | The archival plan dimensions match the candidate’s documented volume targets and the GIS perimeter segments align accurately. Relative hall/gym placement remains an acknowledged hypothesis. Exterior review still shows perimeter bands/lines detached beyond the apparent walls; the source record states that the footprint does not uniquely resolve the hall/gym allocation. |
| Evidence-backed height, floors, roof form | 1.5/2 | The one-story hall and four-story gym are source-supported. The arched hall roof and flat gym roof are plausible, but heights, trusses, roof profiles, and floor levels are estimates. The rendered hall roof appears nearly flat gray and lacks visible scale-appropriate finish. |
| Facade, entrances, distinctive architecture | 1.5/2 | R8 adds image-textured brick, glazing, concrete bands/pilasters, an entrance, signage and some event props. Facade cadence and entrance identity remain generic in places; detached perimeter linework distracts from the exterior. The interior views are poorly framed: one mostly shows the roof, while the event view crops the track and clips floor lettering. |
| Modular export, portability, complete evidence | 1.6/2 | Fresh-open succeeded; expected collection is present; the brick texture is packed; no linked libraries. Twenty-four hurdle component meshes have no material assignments, and the audit folder lacks an R8-specific structured evidence/validation record. This candidate is separate from the production asset. |
| **Total** | **7.8/10** | **Does not meet the 8/10 threshold.** |

## What improved from R7

The brick now has an actual packed image texture and reads with more surface variation. The event view includes hurdles and more seating/infield detail. The glass-block façade and entrance treatments are also more developed. The persistent shortcomings below prevent acceptance.

## Required before another grade

1. Resolve the floating pale perimeter bands/lines: attach them plausibly to the facade, or identify them as site/context data and keep them out of the building review view.
2. Render a useful true interior view showing the full track, seating, event setup, and lighting without the roof blocking the camera.
3. Improve evidence-backed entrance and gym façade identity while keeping uncertain historical features labeled as conjecture.
4. Assign materials to all hurdle meshes and generate R8-specific evidence and validation records.
5. Keep the volume placement and roof-height uncertainties explicit; source dimensions do not georeference the volumes or measure elevations.

## Evidence consulted

- Fresh reopen report: `audit/lambert_fieldhouse/independent_grade_r8/fresh_probe.json`.
- Exterior, interior and event renders: `audit/lambert_fieldhouse/exterior_round8.png`, `interior_round8.png`, and `interior_event_round8.png`.
- Source/uncertainty record: `audit/lambert_fieldhouse/evidence_round6.json`.
- Prior R7 independent grade: `audit/lambert_fieldhouse/independent_grade_r7.md`.
- Purdue Athletics, [Lambert Fieldhouse](https://purduesports.com/facilities/lambert-fieldhouse), confirms the facility identity and six-lane 200 m track.
- Purdue Archives, [Ward L. Lambert Field House and Gymnasium](https://archives.lib.purdue.edu/agents/corporate_entities/559?filter_fields%5B%5D=subjects&filter_values%5B%5D=Inventory+control), documents the historical fieldhouse plan dimensions.
