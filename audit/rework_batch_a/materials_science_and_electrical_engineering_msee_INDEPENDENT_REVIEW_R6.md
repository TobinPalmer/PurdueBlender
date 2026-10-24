# MSEE R6 Independent Full-Building Review

**Result: 8.2/10 — meets the 8.0 review threshold, with material limitations.** Reviewed 2026-10-24. I reopened the saved standalone library in Blender 5.2.3 and visually inspected the R6 overview and entrance detail alongside both saved Purdue ECN reference photographs. I also reviewed the R6 source/validation records, GIS feature 646, archived building context, and the read-only master placement check. This review made no MSEE geometry or shared-file changes.

## Scores

| Category | Score | Assessment |
|---|---:|---|
| Identity and footprint | 1.9/2.0 | Purdue ECN and Archives identify MSEE; GIS feature 646 supports the four-corner plan. The 74.18 × 80.13 m shell bounds are preserved. The local conversion is approximate, not surveyed. |
| Placement, orientation, and scale | 1.8/2.0 | The read-only master check finds one collection instance at the manifest origin (87.421, 215.992 m), unit scale, zero rotation, and a relative library link that resolves. Registration is verified against the project manifest, not independent survey control or neighboring property corners. |
| Form, height, and roof | 1.0/1.5 | The broad low-rise mass and four modeled window courses are plausible for the documented building. Shell height is 14.7 m (z 0.3–15.0 m), while the GIS snapshot carries an `Extrution` value of 36 with no documented units. No elevation or roof drawing resolves the conflict; flat roof, monitor, level datums, and exact height remain interpretive. |
| Facade, texturing, and entrance | 1.6/2.0 | R6 fixes the prior high/overlapping entry: paired doors and the fanlight now sit at the atrium-screen base, with a muted dark glass/frame and a smaller top window course. This aligns with the ECN photo’s red-brown brick, dark central entrance, semicircular fanlight, and smaller top course. The full render remains highly repetitive and the glass reads as opaque blue-gray panels; material appearance, bay dimensions, and all-side cadence are still estimates from uncalibrated photos. |
| Interior and circulation | 0.5/1.0 | The Archives supports a two-storey glass atrium, laboratories, and two pedestrian skyways. The saved asset has 32 atrium-named objects and a few schematic contents, but no source-backed floor plan or verified connection between spaces. The exterior renders do not show a legible interior view. |
| Technical and evidence quality | 1.4/1.5 | Blender reopen passes; collection and shell exist; the 16-vertex shell has no non-manifold edges in the saved validation; all mesh objects have material assignments; no unpacked external images. R6 object count and shell bounds match the dedicated validation. Source dates, uncertainties, and geometry edits are documented. |
| **Total** | **8.2/10** | **Passes the numerical threshold; not a claim of survey or as-built accuracy.** |

## Evidence and remaining limits

- The official Purdue ECN page [MSEE in ECN](https://engineering.purdue.edu/ECN/AboutUs/History/MSEE) supplies two local reference photos. The exterior image qualitatively supports the entrance arch, red-brown brick, dark framing, and smaller upper window course. It is uncalibrated, has no published capture date, and does not establish facade orientation or dimensions.
- [Purdue Archives MSEE history](https://archives.lib.purdue.edu/agents/corporate_entities/703) supports the two-storey atrium, laboratories, and skyways, but offers no as-built interior plan or section in the reviewed material.
- GIS feature 646 supports the footprint and records four levels, a 36 `Extrution` field, and an elevation attribute. The field units are not documented in the evidence package; it cannot verify the modeled 15 m roof height or roof monitor.
- R6 corrects the most visible R5 entrance problem. The result is materially more coherent against the official photo, but the large glazing field, arch dimensions, brick tint, procedural course scale, and window schedule remain visualization estimates.
- The interior remains a schematic atrium vignette. There is no basis to claim verified circulation, room layout, stair placement, or present-day atrium contents.

## Decision

R6 earns 8.2/10 because it preserves the GIS shell, verifies its project placement, corrects the entrance against a building-specific photo, and is technically portable and reopenable. The score is close to the threshold, and the strongest remaining deficits are unsupported metric height/roof form and the absence of verified interior circulation. These should remain clearly labeled as uncertain unless better drawings or elevation data are found.

Machine-readable rubric and direct reopen results: `materials_science_and_electrical_engineering_msee_R6_independent_scorecard.json` and `materials_science_and_electrical_engineering_msee_R6_independent_reopen.json`.
