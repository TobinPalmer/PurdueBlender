# Independent Grade — Lambert Fieldhouse R7 Candidate

**Score: 7.8/10 — does not yet meet the 8.0 acceptance threshold**  
**Candidate:** `audit/lambert_fieldhouse/lambert_fieldhouse_r7_candidate.blend`  
**SHA-256:** `6090F1BB1EC51FE6D16DBC6789F2E3D2FD5D16F90C98C57D13918EE5A70CB64F`  
**Review date:** 2026-10-26  
**Independent reopen:** Blender 5.2.3 loaded the candidate from disk. The exported `Asset_lambert_fieldhouse` collection contains 932 objects, including 929 meshes. Every mesh has material assignments. I found 36 used material datablocks and no image-texture nodes.

## Category scores

| Category | Score | Notes |
|---|---:|---|
| Site registration and footprint | 9.2 | The north/south allocation follows the distinct GIS lobes, with published archival dimensions closely matching each. Reported roof-to-GIS overlap is 98.6% and 98.8%. This is a strong registration hypothesis, not surveyed control. |
| Program and major massing | 8.3 | The one-story fieldhouse and larger gym volume are now assigned to the more plausible lobes. The retained 200 m track is consistent with Purdue Athletics’ description. The gym’s four-story height and exterior bay cadence remain schematic. |
| Exterior form and architectural detail | 7.6 | Brick, openings, glazing, roof volumes and the gym façade read clearly. The repeated window/door treatment remains generic, and the entrance treatment does not yet establish the building’s distinctive identity. |
| Interior completeness | 7.0 | The track, six lanes, lane boundaries, seating and competition area make the athletic use legible. The inspection view is sparse: it lacks convincing event equipment, wall/signage detail and stronger spatial lighting; the gym interior remains schematic. |
| Materials and texturing | 6.9 | The palette distinguishes brick, glass, limestone, metal, track, seating and concrete. Materials are shader-based but the reopened file has no image-texture nodes; the exterior reads as relatively flat in the supplied render, with little visible surface relief or weathering. |
| Visual presentation and asset cleanliness | 7.2 | The forms are understandable, but the exterior render shows thin perimeter/context lines extending well beyond the building that compete with it. The gray background and flat lighting also suppress material contrast. These could be separated into non-building context or removed from the review render. |
| Evidence and technical integrity | 9.0 | The candidate reopens, has no unassigned mesh materials, preserves the 200 m track measurement, and documents source limits. The evidence correctly avoids calling the GIS fit a surveyed historic plan. |

## Required improvements to reach 8/10

1. Improve exterior material response so the brick, concrete, glazing and roof read with visible scale-appropriate texture/relief in a close render. The current materials are assigned but visually subdued; no image-texture nodes are packed in the file.
2. Add a more specific, evidence-backed entry/façade treatment (including readable identity/signage where supported) and reduce the uniform repeated-window look. Keep the historical tower omitted unless a current source verifies it.
3. Make the gym and track interior feel like the documented athletic facility: add a small number of source-supported event fixtures, clearer infield markings/signage, and more convincing lighting. Avoid presenting schematic gym layout as verified.
4. Remove or hide the long context/perimeter line geometry in the exterior building review view, or document which site paths it represents and ensure it does not appear as detached building geometry.
5. Re-render the exterior and interior after changes and rerun fresh reopen/material checks. Preserve the current caveat that the footprint alignment is inferred from matching dimensions and polygon shape, not surveyed control.

## Evidence consulted

- Purdue Athletics, [Lambert Fieldhouse](https://purduesports.com/facilities/lambert-fieldhouse): current role and six-lane, 200-meter track.
- Purdue ArcGIS BuildingShapesZip4, [feature 261](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0): the saved 20-vertex outline used for plan comparison.
- Purdue Campus Facilities historic database, [Lambert, building 92](https://collections.lib.purdue.edu/campus/buildings/92): published volume dimensions/story counts cited in the candidate record.
- Purdue Archives, [UA134 Lambert Field House and Gymnasium](https://archives.lib.purdue.edu/repositories/2/resources/1478), and [1949 aerial item 2215](https://earchives.lib.purdue.edu/digital/collection/pbuildings/id/2215): archival context; available metadata does not georeference a historic plan.
- Visual review of `exterior_round7_candidate.png`, `interior_round7_candidate.png`, and `plan_registration_round7_candidate.png`, plus independent fresh-open inspection of the candidate.
