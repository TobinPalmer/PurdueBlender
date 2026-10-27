# Alpha Omicron Pi — independent grade R1

**Result: 7.6/10 — FAIL (revision required; threshold 8/10).**  
**Asset SHA-256:** `89f51d4f9bff3fdc24c1988017b34328715c20b5b183eed92241030de7256ae0`

## Criterion scores

| Criterion | Score | Evidence summary |
| --- | ---: | --- |
| Identity and source-backed footprint | 2.0/2 | Current AOII house page supports 242 S Grant; independently transformed OSM way 970455277 ring matches the model slab within 0.000018 m symmetric vertex Hausdorff distance and 0.000034 m² area difference. |
| Position, orientation, and scale | 1.8/2 | Local origin and structural ring are coherent; master marker placement remains unverified pending root integration. |
| Floors, height, and roof | 1.1/2 | Three functional levels and terrace match the 2015 city report; exact 9.25 m height is estimated. Flat roof conflicts with the nearest March 2026 Street View's low-pitched roofline. |
| Facade, entrances, architecture, and interior | 1.0/2 | Entry, parking, terrace, planters, windows, 15 bedroom bays and shared rooms are modeled. Street View shows beige lap siding above a brick base with dark shutters, unlike the model's red-brick upper floors; interior partitions/layout remain illustrative. |
| Modular export, portability, and evidence | 1.7/2 | Fresh-open Blender 5.2.3 confirms expected scene/collection, 614 nonempty mesh objects, 12 used Principled materials, no external images or linked objects; master manifest and placement still await root integration. |

## Review details

The current AOII chapter page and the city planning report support the house identity, program, and three-level arrangement. I independently transformed the saved OSM WGS84 footprint into project-local coordinates and compared it to the fresh-open model's level-one slab perimeter. The areas are 276.230285 m² (source) and 276.230318 m² (model); symmetric vertex Hausdorff distance is 0.000018 m.

The candidate needs facade and roof revision before integration. The March 2026 panorama `7sss79LqLjoubGgmBPYxng`, observed from roughly 21 m west of the candidate footprint, shows a beige horizontal-siding upper facade, a brick base, dark shutters, and a low-pitched roofline. The model preview instead shows two upper red-brick stories, no dark shutters, and a broad flat roof. Confirm that the visible panorama facade belongs to 242 S Grant when revising, then align the model to it or document stronger as-built evidence that explains the discrepancy.

The current plan layout is a plausible illustration, not a surveyed interior. The reported 15 bedrooms and shared areas align with public program descriptions, but exact partitions, furniture, stall counts, roof form, window dimensions, and elevations remain unverified. The source's 19,500 sq ft figure does not by itself validate this footprint times the modeled floor count.

## Required iteration

1. Verify the target facade in Street View relative to the 242 S Grant parcel.
2. Correct or substantiate upper-floor siding, shutters, and roof profile/material.
3. Preserve the OSM footprint and stable asset identity, then request a fresh independent grade. Do not integrate until the independent result is at least 8/10.

Machine-readable result: [`result.json`](result.json). Fresh-open and footprint probes: [`fresh_open_probe.json`](fresh_open_probe.json), [`footprint_comparison.json`](footprint_comparison.json).
