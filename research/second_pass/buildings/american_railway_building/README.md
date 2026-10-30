# American Railway Building — exterior research

**Queue rank:** 22 · **stable ID:** `american_railway_building` · **model owner:** Unassigned
**Asset:** `modular/buildings/american_railway_building.blend`
**Pass status:** Focused exterior research saved with significant gaps; no modeling or model-readiness claim.

## Identity and current use

Purdue calls the building the American Railway Building (RAIL), at 500 3rd Street. The Purdue Historic Campus Facilities and Buildings Database records it as constructed in 1926 and still present, with two mapped footprint phases: 1926–1997 and 1997–present. Purdue Mechanical Engineering’s history says the American Railway Association built and equipped it for railway draft-gear research. The association later moved; Purdue’s historic record says the building became a Mechanical Engineering annex. The exact transfer and re-designation dates were not established in this pass.

Purdue’s current emergency-preparedness page describes a very small, two-storey Mechanical Engineering graduate workspace: first-floor student-organization office, focus booth, touchdown desks and work café; second-floor resident and hot desks. This is occupancy evidence, not an exterior survey.

## Footprint and height evidence

The cached Purdue campus GIS snapshot contains two records named American Railway Building at the same address. Their layer and geometry attributes resolve their roles:

| Feature | GIS classification | Snapshot geometry | Use in this pass |
| ---: | --- | --- | --- |
| FID 107 | `BLDG Building Primary`, occupied `Y`, 2 levels | 226.99 m² shape area; 63.46 m perimeter; 5-point closed ring | Primary building footprint candidate |
| FID 110 | `BLDG Building Equipment`, `RefName=Equipment`, occupied `N` | 19.93 m² shape area; 17.91 m perimeter; 6-point closed ring | Equipment feature; exclude from wall/roof outline pending a separate field identification |

The queue’s centroid uses FID 107. Its GIS shape area and the model audit’s retained local footprint area (~142.83 m²) do not agree. The model audit also cites a 2015 planning study’s approximate 2,500 gross square feet, which does not reconcile cleanly with either area when treated as two floor plates. Coordinate conversion, survey/source date, and footprint-phase differences have not been resolved; do not silently scale or combine these measurements. GIS `NUM_LEVELS=2`, its extrusion field, the historic photo, and the 2015 narrative all support two storeys. The project model’s estimated roof heights are not survey measurements.

The database’s 1926–1997 and 1997–present phase labels establish that the outline changed. This pass did not retrieve or register the two historical polygons, so it cannot describe what was added, removed, or rebuilt in 1997. FID 110 is an equipment-layer polygon in the cached campus GIS, not evidence of the earlier/later footprint relationship.

## Exterior evidence and view register

| View / source | What it supports | Limits |
| --- | --- | --- |
| Undirected corner view, Purdue ME history page, image captioned “American Railway Association building 1926” | Compact rectangular, two-storey brick mass; pronounced horizontal upper and lower trim; upper segmental/round-headed window group; smaller rectangular lower windows; a glazed entry at one end; low parapet-like roof edge. | Historic black-and-white image; camera direction, dimensions, materials beyond visible appearance, and later alterations are unknown. It is not a current condition record. Retained as `audit/american_railway/purdue_rail_history_1926.jpg`. |
| West elevation photograph reproduced in the 2015 Purdue/MSKTD ME–RAIL–HAMP study, printed p. 104 | Red/brown brick appearance, light-colored horizontal coping/belt, upper arched window family, lower rectangular openings, and a glazed door at the visible west end. The photograph provides a partial face-level opening schedule. | Small embedded photograph and oblique framing obscure the complete end and exact counts. The PDF is a planning study, not a measured as-built elevation. Retained page image: `audit/american_railway/study_page104_architecture_narrative.jpg`. |
| 2015 study, printed pp. 105–106 | Proposed first- and second-floor arrangements and a west-end entry/stair relationship; the narrative describes the existing west-side entrance and notes a potential south-side accessible ramp. | Proposed plans distinguish new work from program retained; they are not verified current/as-built plans and must not be used to assert exact exterior opening coordinates. |
| Purdue ME history and 2026 Emergency Preparedness page | Identity, approximate era, current departmental context and current occupancy. | No complete façade survey, roof plan, dimensions, or finish schedule. |
| Structurepoint project page | Renovation context: earlier renovations in 1950 and 1979; later graduate workspace conversion; site survey informed wall locations; stair relocation and new restroom/workspace planning were in the design scope. | The page text and project photos document design/renovation context, but do not constitute an as-built elevation or a fully dated condition survey. |

### Partial facade schedule

- **West (as labeled in the 2015 study):** the reproduced photograph shows repeated upper arched openings above lower rectangular windows and a glazed entrance. At least two upper arches and two lower windows are clear in the small view; the crop is insufficient for a reliable whole-face count. The study narrative identifies the west-side entrance and existing stair. Do not infer exact bay spacing from the image.
- **Historic corner view (direction unregistered):** both visible faces are brick. The face with the entry includes a narrow glazed door and small square/rectangular side lights or adjacent openings; the longer face shows a repeated upper arched row over small rectangular lower openings. The historic photo is useful for the original pattern, not current counts.
- **Other current faces:** no complete, registered north, south, east, or service-side photo set was obtained. The 2015 narrative mentions a possible south accessible ramp as a design consideration; it does not prove the ramp was built.

### Materials, roof, and massing

Visible sources support a red/brown brick exterior with light-colored horizontal belt/coping and contrasting window trim. The historic view and 2015 photograph show a simple low, flat-looking roof edge/parapet. No source inspected here establishes the concealed roof construction, parapet profile, drainage, rooftop equipment, or exact trim stone. The project audit’s “limestone” and roof/elevation measurements remain model-side interpretations or estimates, not independently verified material/survey facts. The small primary GIS ring is an irregular quadrilateral in geographic coordinates and should be resolved against the 1997-present historical footprint and a current survey before changing the existing asset outline.

## Gaps to preserve

1. Register both historic-database footprint phases to the current Purdue GIS FID 107 polygon; determine the exact 1997 shape change and whether FID 110 represents an actual rooftop/ground equipment pad.
2. Resolve the FID 107 GIS area versus the existing asset polygon and the 2015 study’s approximate gross floor area. Confirm measurement units, building/footprint phase, and whether the reported GSF includes all floors.
3. Obtain current, orientation-registered photographs of all four faces, corners, entry, and adjoining ME connections; establish present opening counts and any accessible-ramp work.
4. Obtain as-built elevations, a current roof plan, floor plans, measured dimensions, parapet/eave heights, and rooftop equipment/drainage evidence. Keep 2015 proposed layouts separate from construction records.
5. Verify brick, stone/trim, window-frame, glazing, and entry materials and identify the dates and visible exterior scope of renovation work.

## Sources consulted

- [Purdue Mechanical Engineering — History](https://engineering.purdue.edu/ME/AboutUs/History), including the image captioned “American Railway Association building 1926”; accessed 2026-10-30. Image URL: `https://engineering.purdue.edu/ME/AboutUs/History/railbldgext2.jpg`.
- [Purdue Historic Campus Facilities and Buildings Database — Buildings](https://collections.lib.purdue.edu/campus/buildings), American Railway Building (RAIL) entry; accessed 2026-10-30. Reports 1926–present and footprint phases 1926–1997 and 1997–present.
- [Purdue ME–RAIL–HAMP Study](https://engineering.purdue.edu/~frosch/Renderings/Masterplans/ME-RAIL-HAMP%20Study.pdf), Purdue Project 14607 / MSKTD Project 6682, dated June 30, 2015 (revision noted). Printed pp. 104–106 inspected directly; pp. 104–105 include the west-elevation photograph and narrative, followed by proposed plans.
- [Purdue Office of Emergency Preparedness — RAIL](https://www.purdue.edu/operations/emergency-preparedness/rail/), page revision 2026-03-30; accessed 2026-10-30.
- [American Structurepoint — Purdue University American Railway Building Renovations](https://www.structurepoint.com/product-page/purdue-university-american-railway-building-renovations); accessed 2026-10-30.
- `research/second_pass/shared/official_purdue_buildings_wgs84_snapshot.json`: cached official GIS attributes and rings for FIDs 107 and 110. Snapshot age and layer-specific semantics remain relevant limits.
- Existing asset review: `audit/american_railway/REVIEW.md`; used only to identify prior project claims and unresolved model-side discrepancies, not as independent physical evidence.

## Research-only disposition

Focused pass complete with gaps. No building geometry, master Blender file, placement, owner assignment, or grade was changed. The existing audit discrepancy and estimated heights remain unresolved; this dossier is not a modeling approval.
