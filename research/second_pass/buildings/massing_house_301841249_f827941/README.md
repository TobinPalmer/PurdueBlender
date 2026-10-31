# Glenwood Cooperative — exterior second pass (#64)

**Research status:** exterior brief prepared with major coverage and dimensional gaps retained; provisional. **Phase:** research only. No Blender asset, builder, placement, or master scene was changed.

## Identity, reference condition, and boundary

Purdue BuildingShapes **FID 794** is named **Glenwood**, abbreviation **SOGL**, owner `COOP`, address **503 University St**. Glenwood's historic site gives its current location as 503 University Street; the contact page spells it 503 N University Street. Purdue Agriculture also identifies the pictured house as Glenwood Cooperative. These sources and OSM way **301841249** (house number 503; `amenity=social_centre`) resolve the former queue's ambiguous manifest proxy to the actual cooperative house. The fresh Oct. 30, 2026 GIS feature matches the Oct. 28 snapshot. Its GIS-derived centroid is `(-86.91706714, 40.42943729)` WGS84, or `(-285.5690, 226.2204) m` in the repository's approximate campus plane. The priority was recomputed and Glenwood remains rank 64.

The official eight-unique-vertex ring, transformed with the repository's local campus conversion, bounds a roughly **28.97 m east–west by 10.43 m north–south** envelope and **272.68 m²** ring area. The OSM way has eight unique vertices, **286.35 m²** ring area, centroid separation **0.29 m**, and boundary Hausdorff separation **0.58 m** from the GIS ring. The broad outline agreement supports identity and placement; neither line is a surveyed wall trace. Purdue's `Shape__Area=471.38 m²` materially disagrees with area calculated from its returned ring. Keep ring-derived plan dimensions separate from this attribute and do not scale the building to match it. The 2018 overhead crop includes projections and neighboring surfaces that are not cleanly separable at its resolution.

The historic page says the cooperative was founded in 1939, occupied earlier addresses, and “moved to its current location at 503 University Street” in 1969. This is cooperative site history, **not** evidence that the present building was built, moved, or completed in 1969. The two street addresses are formatting variants. No reliable construction year for the extant house was found. GIS `NUM_LEVELS=1` and `CountOfFLO=1` conflict with the directly observed two occupied-looking facade levels and dormered attic; field semantics are undocumented. `Extrution=12` has no documented units or method.

The mapped white, horizontally sided house is the target. In northeast-station views, the larger red-brick/timbered **Alpha Xi Delta** house is the separate neighbor to the right; it is outside Glenwood's outline and must not be joined to the cooperative. Minor porch/entry projections and steps may extend beyond a wall-footprint polygon. The overhead crop cannot reliably assign every eave, small outbuilding, walk, or service object; keep unverified site items separate.

## Viewpoint register

Retained Google Street View thumbnails are 900 × 600. Yaw rotations are headings at one pano station, **not** new camera positions. Capture month is what Google Maps displayed during inspection; local retrieval was Oct. 30, 2026. Camera height and exact exposure timestamp were not supplied. Original yaw images are retained under `sources/streetview/`; `sources/source_manifest.json` maps each file to its station, pano, heading, capture month, hash, and limitations.

| View ID | Station, date, heading | Inspected evidence | Limits |
|---|---|---|---|
| GLEN-SV-S26 | 903 5th St; pano `Z6Z3HXdLaFHgsd8xhaDm-g`; approx. `40.4292582, -86.9170921`; Apr. 2026; yaw 0° north | Near-frontal current south / 5th Street facade; best present opening and porch evidence. | Tree masks west/left run; crop clips east/right continuation; low street position and perspective; no camera height or scale. Other rotations mostly show context. |
| GLEN-SV-S23 | Same station; pano `PMF7obsfuKPsv0aRlySOIg`; same approx. coordinates; Jul. 2023; yaw 0° north | Same south face before the triangular-gable porch state; Glenwood sign and curved/arched canopy visible. | Seasonal foliage, shadow and crop differ; not an elevation drawing. Same station, not a second location. |
| GLEN-SV-NE26 | 509 N University St; pano `1h3Ywq1HzNg-ffCeexwJ3w`; approx. `40.4295484, -86.916706`; Apr. 2026; yaw 270° west | Distant oblique across north/rear and end region: siding, partial windows/base/roof, plus separation from Alpha Xi Delta. | Large foreground tree and evergreen mask the wall/corner; not a complete or orthogonal elevation. Camera height unknown. |
| GLEN-SV-NE23 | Same station; pano `kW5raFvrIsB1ttBNvtx_Cw`; approx. `40.429546, -86.9167057`; Jul. 2023; yaw 270° west | Dated comparison of the same partly screened rear-side view and neighbor separation. | Summer foliage further obscures wall; same station as GLEN-SV-NE26. Other yaw rotations do not establish missing faces. |
| GLEN-ORT-18 | Indiana 2018 orthophoto export; north-up, 1,400 × 1,400 crop; bounds and request in `sources/indiana_2018_ortho_glenwood_request.json` | Broad roof-plan arrangement, connected roof areas and context; cross-check against GIS plan. | Soft image; only 2018 year known. Does not establish roof material, height, small equipment, facade, porch phase, or surveyed wall lines. |
| GLEN-FSCL-UND | Purdue FSCL official hero image; capture date unknown | Oblique identity/appearance: light siding, dark shutters, repeated windows, entry/sign, dormers and low base. | Unknown orientation/date; may show earlier porch condition; no measured elevations or full coverage. |
| GLEN-2008 | Indiana Connection photo retained from prior audit, labeled 2008 | Broad historic white-house identity only. | Small/low-resolution; not used for opening counts, roof joints or material assignment. |

**Coverage result:** a strong current front view, a dated same-station front comparison, and one partly blocked rear-side oblique pair exist. No full walkaround was found. Yaw 0°/90°/180° from 509 N University and 90°/180°/270° from 903 5th mostly frame road, nearby property, or context; they are not counted as additional Glenwood elevations.

## Face and opening schedule

Counts are source-relative visual positions/groups, not measured rough openings. Use GLEN-SV-S26 for present south-face layout and GLEN-SV-S23 only for the earlier porch. Read the frontal photo left-to-right (west-to-east is provisional from street registration; verify compass orientation before construction). Tree, crop and perspective make edge counts uncertain.

| Face / zone | Observed sequence and relationships | Confidence / unresolved portions |
|---|---|---|
| South / 5th Street, upper wall — GLEN-SV-S26 | About **five** rectangular dark-glazed window positions with dark shutters across the visible upper wall; westmost region is tree-obscured and east crop incomplete. A broad central shed/box dormer projects from the roof with **two** side-by-side windows. Separate narrow arched-top eyebrow dormers sit to either side, each with a small window. Keep the four dormer windows separate from wall-floor openings. | Strong central run; provisional end count. Sash divisions, reveals, exact heads/sills and total wall count unresolved. |
| South, lower wall — GLEN-SV-S26 | From west/tree side: one wide grouped glazing unit with multiple divisions; a central grouped unit of roughly two lights; recessed entry/porch; another wide grouped unit near east crop. At least three primary grouped window locations are visible. Low shrubs/base landscaping conceal portions of the foundation. | Group-level sequence only; exact panes, widths, east continuation, basement and service openings unknown. Do not treat each mullion as a building bay. |
| South entry, Jul. 2023 — GLEN-SV-S23 | Near the east half: curved/arched canopy or pediment with visible Glenwood sign; door set beneath it, reached by steps/walk with metal rails. Lower grouped windows flank entry. | Outline/sign are clear; column count, profile and dimensions are not. The view does not establish whether the 2024 permit describes this exact change. |
| South entry, Apr. 2026 — GLEN-SV-S26 | Same station now shows triangular gable/portico with white trim, shallow projection, recessed door, concrete approach/steps and dark metal handrails. The 2023 sign is not legible/visible. Stair/rail arrangement differs. | Direct date-bounded change, likely porch alteration between Jul. 2023 and Apr. 2026. Permit log is consistent but has no drawings; exact permit-to-as-built attribution is unresolved. |
| North / rear long face — GLEN-SV-NE26 / NE23 | Fragments show light horizontal siding, upper/lower rectangular window positions, low dark base and roof continuation behind a large tree and evergreen. A small porch/entry-like projection appears near the left of the oblique; its connection and exact corner cannot be resolved. | Partial only: no full sequence, door count, corner tie, level schedule, vents or service openings. Two dates are one station. |
| East and west short ends | No retained orthogonal face view. 2018 overhead crop is plan-only. | Unknown; do not infer blank ends, gables, openings or symmetry from south facade. |
| Corners, foundation and grade | South view shows a low dark reddish/brown masonry-looking band below pale siding; rear oblique suggests similar base. Grade, shrubs, steps and sidewalk obscure true base/corner lines. | Photo-level appearance only; no measured foundation height, bond, material or section. |

### Porch chronology and permit cross-check

West Lafayette's August 2024 permit log (page 28 of the retained PDF extract) lists permit **27013**, issued **14 Aug. 2024**, Glenwood Co-Op / Heartland Contractors Inc., 503 N University St, parcel `79-07-19-127-060.000-026`, scope “Place front porch, electrical upgrade, insulation,” estimated value **$83,000**. The same 5th Street station shows the curved-sign canopy in Jul. 2023 and a triangular gable in Apr. 2026. These records strongly support a porch change during the interval and make the permit a plausible explanation; the log alone does not prove which geometry was built or when. Apr. 2026 is the current visual reference, not the undated FSCL hero or 2023 porch.

## Roof, massing, and dimensions

The mapped outline is an elongated E–W house with small east-end steps; it is not a surveyed above-grade wall trace. The 2018 crop shows several connected roof planes, including a long main field and intersecting/offset sections. The front projection is not cleanly separable at this resolution. Frontal and oblique photographs show a low-pitched dark gray/brown shingle-looking roof and three prominent front dormer forms: two narrow arched eyebrow dormers and a wider central shed/box dormer with paired windows. A chimney appears near the east/right end in street views; exact plan location and cross-section need elevated corroboration. Trees and soft aerial pixels prevent a reliable count of valleys, small equipment, or every eave.

The south elevation visually reads as two facade levels plus dormered attic, while GIS reports one level and the previous audit/model used an estimated **9.15 m** roof/ridge height. A targeted 2018 COPC query supplies a bounded surface-height distribution (method below), but no plan, elevation, section, roof survey, or eave datum was obtained. Keep 9.15 m as a prior illustrative estimate; its proximity to the new class-1 median does not independently validate it. GIS `Extrution=12` has no documented units or method. The orthophoto remains plan evidence only.

### Plan comparison method

The Oct. 30 Purdue ring is EPSG:4326. Unique vertices were converted with the repository's approximate local campus transform documented in `modular/AGENTS.md`: `X=(lon+86.9137)*111412.84*cos(40.4274°)`, `Y=(lat-40.4274)*111040`. OSM way 301841249 was compared using the same transform. Calculated results: GIS ring **272.6846 m²**, OSM ring **286.3458 m²**, centroids **0.2873 m** apart, maximum boundary Hausdorff separation **0.5821 m**. The GIS ring matches the Oct. 28 snapshot. These are map calculations, not a survey or eave/porch dimensions. `Shape__Area=471.3789 m²` does not reconcile with either ring and is not a scaling input.

### 2018 LiDAR height constraint

A bounded COPC range query was made against the Indiana 2018 3DEP Tippecanoe tile `in2018_29951885_12.copc.laz`, hosted by iDiF at Purdue. The retained crop `sources/indiana_2018_copc_glenwood_12m_buffer.las` contains 8,598 returns selected within the official GIS polygon plus a 12 m buffer; `sources/indiana_2018_copc_glenwood_stats.json` records the URL, query, CRS, classifications, counts, statistics and SHA-256. The footprint was transformed from EPSG:4326 to **EPSG:2968, NAD83(HARN) / Indiana West (ftUS)**. The vertical coordinate is **NAVD88 height – Geoid12B (ftUS)**, read from the LAS compound CRS. The 0.5 source-unit query resolution is 0.5 ftUS.

For a conservative interior sample, class-1 returns inside the GIS polygon eroded by 3 m were compared with class-2 ground returns in a 5 m outer ring. There are **338** interior class-1 returns (z median **657.405 ftUS**, p95 **658.434 ftUS**, p99 **661.530 ftUS**) and **1,217** nearby class-2 ground returns (median **625.400 ftUS**). Their median-ground differences are **9.755 m** at the class-1 median, **10.069 m** at p95 and **11.012 m** at p99. There are **zero class-6 building returns** inside the polygon. Class 1 is unclassified and can include vegetation, residual wall returns or other surfaces; the p99 is especially vulnerable to isolated tree points. These distributions constrain the 2018 roof/surface scale only and do not establish eave, ridge, floor-to-floor height or current roof shape. No point-derived roof plane was fitted.

## Facade materials and color evidence

| Element | Supported appearance | Evidence and limitations |
|---|---|---|
| Main walls, front and rear fragments | Pale/white horizontal lap siding with regular narrow shadow lines | Current front and rear oblique plus FSCL hero. Pattern and appearance are visible; wood/vinyl/fiber cement or underlying substrate is unknown. |
| Windows / shutters | Dark near-black shutters flank many front openings; light trim; blue-gray/dark reflective glass | Front strongest, rear partial; glazing tone changes with sky/tree reflections. Frame material, exact sash pattern and reveals unresolved. |
| Foundation/base | Low dark reddish-brown masonry-looking band | Front and rear oblique; shrubs/shadow hide bond, material, thickness and full height. |
| Roof | Dark gray/brown shingle-like appearance in 2023/2026 views | Color varies with exposure; 2018 overhead is not reliable color evidence. Shingle type, fascia, soffit, gutter and flashing unknown. |
| Porch / rails | Current white-trim triangular gable; dark metal rails; concrete steps/approach | Current front image; 2023 canopy differs. Permit log has no drawings; support count, sections, projection, and rail layout unresolved. |
| Chimney | Reddish/brown masonry-looking stack near east/right roof end in front view | Perspective/crop make exact position/height and roof junction provisional; no close view. |

These are photographic appearances, not calibrated colors or product specifications. Lighting and reflections vary. The undated FSCL image may show another porch phase. No uninspected rendering or previous model color was treated as material evidence.

## Evidence-led construction brief

Preserve the mapped long E–W outline as a plan constraint while keeping porches, steps, eaves and foundation offsets separate from the unresolved wall trace. The current south facade is pale-sided, two levels under a low sloped roof with dormered attic; it has shuttered upper openings, grouped lower glazing and a recessed entry near the east half. The north/rear is also sided and fenestrated, but evidence is too masked to copy the south schedule. Keep the three front dormer families distinct (two narrow arched eyebrow forms and one wider paired-window shed/box form), retain the likely east-end chimney as provisional, and treat current triangular-gable porch, approach and rails as projecting architecture. The low dark base is distinct from siding. Current porch evidence is Apr. 2026; Jul. 2023 shows a curved canopy and sign. Do not merge Alpha Xi Delta or incidental site objects into Glenwood.

**Discrepancy checklist against prior audit/model evidence:**

- Former GIS match was unresolved and used a manifest proxy. FID 794 is now supported by official name, COOP owner/address, cooperative pages and OSM; queue location now uses mapped centroid. Rank remains 64.
- Cooperative move history in 1969 is not an extant-house construction date.
- GIS one-level fields conflict with visible two-level facade and dormered attic; count and field meaning remain unresolved.
- GIS Shape__Area (471.38 m²) is unsupported by returned-ring area (272.68 m²); use mapped vertices only as a plan constraint, not survey truth.
- Prior 9.15 m ridge, roof pitch, facade compass placement, dormer sizes, exact window bays and hidden faces were illustrative. Current evidence adds a registered south face and rear oblique, but does not verify those dimensions or other faces.
- Porch change is visually bounded by Jul. 2023 and Apr. 2026. The Aug. 2024 permit log is consistent but not an as-built drawing.
- The 2018 roof crop and COPC distribution add plan and bounded vertical evidence; neither validates exact current roof material, equipment, eave/ridge datums or porch form.

## Gap and conflict register

| Priority / affected element | Why evidence is inadequate / tried | Evidence needed | Effect on accuracy |
|---|---|---|---|
| High — complete north/rear elevation and entrance | Only a tree/evergreen-screened two-date oblique pair from one station; official photos do not show the full rear. | Mapped daylight rear walkaround with near-frontal and opposite obliques; permit/as-built drawings if a rear porch is related. | Doors, opening sequence, grade shifts and offsets remain unknown; no symmetry assumption is justified. |
| High — east/west ends and corner ties | No clear short-end view; aerial is plan-only and soft. | Street-level positions beyond both ends, elevated corner views, or dated elevations. | Gable/roof termination and return openings cannot be placed reliably. |
| High — levels, eave/ridge, pitch and roof junctions | One-level GIS conflicts with photos; extrusion units undocumented; 9.15 m is old estimate; aerial has no elevation. | As-built/renovation elevations/sections, permit drawings or datum-tied survey; resolve the 2018 class-1 vegetation/surface ambiguity with roof-specific returns or an independent measured elevation. | Silhouette and floor proportions remain unverified. |
| High — exact opening/sash schedules on every face | Front is perspective/cropped/tree-obscured; rear masked; group-level counts only. | Orthogonal high-resolution corner-to-corner photos and original plans/elevations; close views of muntins/reveals. | Bay spacing, alignment, concealed openings and sash pattern are uncertain. |
| High — 2024 porch as-built | Log records work but has no plan/elevation; photos bound change but do not tie it definitively to permit. | City permit drawings/inspection record, contractor/cooperative records, close current side/front views. | Pediment, supports, projection, rails and steps cannot be dimensioned. |
| Medium — roof planes, chimney, fascia and small equipment | Overhead supports broad plan only; street view too low to show valleys and fixtures. | High-resolution current aerial/drone, roof plan, chimney-side oblique or survey. | Roof intersections and attached features may be missed or misplaced. |
| Medium — siding, base, roof and frame specifications | Photographs reveal appearance but not composition; daylight and reflections differ. | Close daylight details, permit/specification notes, maintenance records or product data. | Materials remain appearance-level; no calibrated color or texture scale. |
| Medium — construction/alteration chronology | Cooperative history dates moves, not the current house; street dates establish only porch-state interval. | Local permit/property archive, cooperative records, dated historic photos and plans. | Building phase history cannot be resolved. |
| Medium — mapped ring versus wall, porch and attribute area | GIS/OSM outlines broadly agree but do not locate eaves/porch; GIS area attribute conflicts. | Survey/as-built site plan and authoritative GIS field metadata; check walks/steps separately. | Footprint is useful for orientation, not exact above-grade perimeter or wall thickness. |

## Source package

`sources/source_manifest.json` inventories retained bytes with SHA-256, provider, URL or retrieval lead, source/retrieval date, role, limitations, and camera grouping. The four Street View pano IDs each represent one position; saved yaw files are rotations from that point. Exact capture day, camera height and full original Google metadata were not supplied. The City permit file is page 28 of the 255-page August 2024 log; it preserves the cited record, not permit drawings. Research only; no model, builder, placement or master asset was altered.
