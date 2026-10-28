# Felix Haas Hall — independent exterior review r01

**5.2/10 — revision required; not accepted.** Default threshold: 9.9/10. No threshold exception is approved. This score assesses the whole building's exterior under the second-pass rubric.

Reviewed saved revision `exterior_r01`, SHA-256 `445c1499ef1b1c0bb2c5520304cff9784a572e0478abcc17a72157f951ba88f4`. The reviewer independently reopened the saved library in Blender 5.2.3, inspected all nine revision renders and the real source photographs, and ran [evaluator.py](evaluator.py). The reviewer made no source-asset or builder edits.

| Exterior criterion | Awarded | Maximum |
| --- | ---: | ---: |
| Windows/openings across all elevations | 1.50 | 3.0 |
| Signature architecture | 1.25 | 2.5 |
| Overall proportions, wings, roof and silhouette | 1.50 | 2.0 |
| Materials, color, surface scale, trim and depth | 0.65 | 1.5 |
| Whole-building consistency | 0.30 | 1.0 |
| **Total** | **5.20** | **10.0** |

The new west facade makes a visible improvement over the baseline: nine upper groups and nine narrow middle openings establish the three-register rhythm visible in the elevated May 2016 photograph and April 2026 Street View. The result remains a partial facade revision. Large discrepancies survive on the front, the west basement, and the side elevations.

## Required corrections

1. **Expose the three front upper windows correctly.** The front render shows pale blocked panels where the official photograph shows dark framed glass. Independent mesh bounds place `HAAS_Photo_Glazing_-7.65_7.7`, `HAAS_Photo_Glazing_0_7.7`, and `HAAS_Photo_Glazing_7.65_7.7` at X=12.76–12.82, behind facade/jamb geometry near X=13.0–13.25. Create proper openings/recesses and check visible glazing and mullions. Changing the hidden glass color alone cannot fix the occlusion.
2. **Correct the west basement material register and entrance.** The source has broad pale limestone around basement windows and the double-door opening, with brick insets between bays. The model retains mostly brick with a thin pale stripe. Its door also lacks the source's transom/frame division and recessed/downward approach. Confirm the approximate door bay against the plan/footprint and photographs.
3. **Refine the west middle windows.** The source has narrow dark openings with pale sills and keystones. The model's full pale jamb frames are too heavy. The upper west grouping is useful, but detailed sill/head/stepped corner profiles remain simplified.
4. **Match the front arches and stone/brick articulation.** The real lower openings have shallow segmental heads. The model uses semicircular profiles and broad pale wall areas, with simplified brick inlays and framing. Match the official front oblique rather than retaining the current generic arch shape.
5. **Research and model the remaining side elevations.** North and south render as near-blank grids. The winter oblique source visibly contains upper and basement openings on the shown side. The opposite side remains unverified. Obtain correctly oriented distinct views; do not mirror the new west arrangement onto unseen walls.
6. **Retain dimensional uncertainty.** The broad hipped roof is supported qualitatively. Absolute facade heights, roof/eave dimensions, opening station/dimensions, fine eave details and tile scale remain estimates requiring stronger evidence.

## Evidence and integrity checks

- Real references inspected: official Purdue Events front photograph, Purdue Libraries 2017 exterior, Maps front photograph by Mike A, May 2016 elevated west photograph by Jay’ Discovery, winter oblique with January 2015 capture label, April 2026 Google Street View west entry and upper facade.
- Render views inspected: east, west, north, south, southeast, northwest, roof, west window close-up, and entrance close-up. These show the exact saved revision according to `revision_r01/render_settings.json`.
- Saved hash matched. Expected `Asset_felix_haas_hall` collection reopened with 1,259 objects. No external libraries or image dependencies were found.
- All 863 retained baseline objects are identical in mesh coordinates/topology, transforms, bounds, material names, and render flags. The change removes 56 old west attachments and adds 396 west objects. This supports no regression to the retained GIS shell, roof and placement frame; it does not prove geographic accuracy independently.
- Exterior-reference coverage and absence-of-material-discrepancies gates **fail**. Other source-library integrity gates pass. Master integration was not inspected and remains a separate Tobin/coordinator gate.

The full criterion evidence, findings, uncertainties, gates, and independently recomputed score are in [result.json](result.json). North/south coverage and a current complete exterior reference set remain incomplete. The photographs are qualitative perspective references, not measured elevations.
