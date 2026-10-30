# Matthews Hall — second-pass exterior research

**Queue rank:** 36 · **stable ID:** `massing_matthews_hall_mthw_9326885` · **model owner:** Unassigned
**Identity:** Matthews Hall (MTHW), Purdue GIS FID 235, 812 Mitch Daniels Boulevard
**Review date:** 2026-10-30 · **Status:** focused exterior pass saved with major coverage, level and roof gaps retained; provisional.

This pass re-inspected the saved Purdue Events photograph and checked it against the current 2026 Purdue Building Emergency Plan and Purdue's named GIS feature. The photo supports a red-brick three-story rectangular mass, repeated dark double-hung window groups, pale horizontal masonry belts, a shallow dark eave and a central columned portico. Its one oblique viewpoint does not establish complete window schedules or any opposing elevation. The 2026 plan calls the building three-story, while several GIS attributes report four levels; this discrepancy remains unresolved, as do surveyed height and exact roof form.

## Identity, location and footprint

The current Purdue GIS feature FID 235 identifies MTHW as Matthews Hall at 812 Mitch Daniels Blvd., Purdue owner. The official 2026-09-22 emergency plan confirms the name, address and a “three story, rectangular building” description. The 14-vertex GIS outline is the documented plan basis, not a surveyed wall-line; its feature-level positional accuracy is not published. In the project-local east/north meter approximation (not a survey CRS), the source outline bounds are X −240.405 to −214.287 m and Y −332.718 to −256.121 m, an axis-aligned envelope about 26.12 × 76.60 m. The long dimension is north–south in this project conversion. The inferred principal portico/front is on the south side toward Mitch Daniels Boulevard; that facing is consistent with the address/photo context but is not fixed by a compass-tagged elevation or building plan.

The source outline has 14 distinct vertices. The previous saved asset's wall shell follows those outline edges to about 0.0001 m in the project coordinate conversion. This is a geometry-to-source match, not a proof that the source map polygon is a surveyed wall boundary. The previous asset's estimated wall height 11.4 m, roof top 11.95 m and 3.8 m floor spacing are model assumptions, not measured building dimensions.

## Source and viewpoint register

| ID | Source | View / observed evidence | Provenance and limitation |
|---|---|---|---|
| **M1** | Purdue Events, [Matthews Hall page](https://events.purdue.edu/matthews_hall); original image retained in `audit/matthews_hall_mthw_9326885/sources/purdue_events_matthews_hall.jpg` and referenced in this dossier's source register. | Low-to-mid-height oblique from the lawn toward the apparent south entrance frontage. Shows the central portico, one long wall segment, two story bands, upper sash rows, near corner/return, and shallow eave. | Page shows photo activity on 2022-06-12 and 2022-06-15; actual image capture date and photographer are not stated. The lawn tree at image-left and trees at right hide wall edges and lower corners. Camera position, bearing and height unknown. |
| **M2** | Purdue OEP, [2026 MTHW Building Emergency Plan](https://www.purdue.edu/operations/emergency-preparedness/mthw/); raw page retained in first-pass audit. | Textual current building description; no photo. | Revised 2026-09-22; says three-story rectangular. Supplies no floor heights or facade data. |
| **M3** | Purdue campus map ArcGIS FID 235; WGS84/raw snapshots and layer metadata retained in `audit/matthews_hall_mthw_9326885/sources/`. | Polygon identity, position and plan shape. | Layer last-edit metadata 2026-08-31; feature-level created/edited dates blank; CRS is Web Mercator raw and EPSG:4326 saved reprojection. Campus map is not a certified survey. |
| **M4** | Purdue Archives UA 62 catalog entry for Home Economics Building / Matthews Hall exteriors, including undated and 1961 materials. | Historical-photo lead only; no specific archival image downloaded or inspected as facade proof in this pass. | Search finding aid records potential historic exterior views; archive image identities and phase are unresolved. |

M1 is the only inspected ground-level exterior station. Crops do not add a viewpoint. There is no aerial/roof image or current rear, north, east or west frontal view retained in this second-pass evidence package. A broad, distinct walk-around has not yet been achieved.

## M1 image-relative entrance facade schedule

Read from left to right in the image. The wall is foreshortened; this schedule distinguishes visible features from totals that the single view cannot safely support.

| Zone | Visible sequence and form | Confidence / limit |
|---|---|---|
| Upper story | Repeated pairs/groups of dark rectangular sash across the red brick wall; light-colored sills/lintels frame individual window units. | Rhythm is clear; a complete count is not fixed here because the tree/corner and oblique crop hide the full run. Exact sash subdivision requires a closer frontal image. |
| Middle story | Another repeated dark window row, broadly aligned with upper openings; horizontal pale stone-like string course below/around the level. | Story band and repeated rhythm are visible; exact group count, sill/head heights and reveals unmeasured. |
| Lower story | Larger windows flank a centrally positioned portico/entry; the wall meets lawn/approach with little exposed basement visible in this frame. | Local arrangement only. Tree and landscape mask the ends; full door/window count, accessible threshold and grade transitions unknown. |
| Central entrance | Small projecting portico with pale horizontal entablature/cap, supported by paired/slender columns (four supports are plausible in the view); dark doorway recessed behind it. | Distinctive composition is confirmed. Exact column count/profile, capital/base form, door leaf count, portico depth, stair/landing and canopy dimensions are not measurable. |
| Horizontal wall bands | Pale stone-like sill/belt course at the lower edge of upper windows and at the level transition; bands visually wrap/continue toward the corner. | Visible but material identity and section depth are not established. Do not treat the prior model's stone color as a specification. |
| Roof edge | Low dark projecting eave/cornice; small repeated warm-colored blocks are visible under the outer edge. | Shallow edge is clear; the small details may be brackets/rafter ends or lighting/shadow artifacts. No roof-top surface, pitch, parapet or mechanical layout is visible. |
| Corner and side return | The building turns at image-right into a shorter/receding wall; several additional windows are partly visible. | Return exists, but its opening sequence and length are unknown. Do not duplicate the front schedule there. |

## Materials, massing and vertical evidence

M1 supports deep red/brown brick with visible horizontal mortar courses, light buff/white stone-like entrance and floor-band elements, dark sash/glazing, and a dark roof edge. Bright sun on the lawn and shade on the facade affect apparent color; these are uncalibrated photographic impressions. The exact stone versus cast stone/concrete, brick blend/bond, sash material/frame color, roof type, and weathering have not been independently documented. No finish schedule was found in the retained evidence.

The OEP description provides a three-story rectangular mass. GIS `NUM_LEVELS` and `CountOfFlo` are 4, and `Extrution=27` is also present but lacks documented units/meaning. `F04=0` appears in the prior source record, but no field dictionary was available. The current emergency-plan narrative and one photo favor three above-grade stories, yet the database conflict should not be erased by assumption. None of these attributes establishes floor datums or total height. The asset's shallow roof edge follows M1 qualitatively; hidden roof geometry remains unknown.

No roof plan, as-built elevation, elevation raster or building-specific LiDAR clip is in the retained MTHW package. Indiana 3DEP regional availability alone does not identify a MTHW tile/date/CRS or provide building height. Any future point data must retain acquisition date, horizontal/vertical reference, units, class filters and method; roof returns or mixed vegetation cannot stand in for wall/eave measurements.

## Evidence-led future construction brief

- Preserve the official FID 235 footprint and campus registration as source-based plan data, with the 26.12 × 76.60 m envelope labeled as projected GIS-derived rather than surveyed.
- Use the south-facing portico as a well-supported but not compass-registered facade hypothesis: red brick, pale horizontal bands, repeated sash windows, central pale-column portico and dark shallow roof edge.
- Keep window and door counts source-limited. Do not mirror M1 onto the hidden side or opposite end.
- Follow the current emergency plan's three-story description provisionally while recording GIS four-level fields as an unresolved conflict. Do not treat the old model's 11.95 m roof or 3.8 m floor spacing as measured.
- Keep the entry portico, light bands, sash, brick wall and roof edge as visually distinct systems; get close detail and side profile before fixing geometry depth or material.

## Gap and conflict register

| Gap | Evidence tried / why insufficient | Evidence needed | Effect on accurate model |
|---|---|---|---|
| Complete sides and opposing corners | One Purdue Events oblique only; edges and base are tree/landscape occluded. | Current georeferenced all-face walk-around, with frontal and opposing obliques and positions along both long walls. | Rear/service openings, end walls, blank bays and corner transitions remain unknown. |
| Full opening schedule and sash detail | M1 shows a repeated pattern but is too oblique and distant for exact total/mullion widths. | Close square-on photos for each facade and floor; measured/elevation drawings if accessible. | Exact bay counts and divisions cannot be safely modeled. |
| Portico profile and approach | M1 confirms a columned entry but gives no scale/section; vegetation hides lower geometry. | Frontal and oblique detail with scale, accessible-entry plan and portico section. | Columns, caps, bases, steps/ramp and door dimensions remain schematic. |
| Three-story vs four GIS levels | Current OEP 2026 plan explicitly says three-story; GIS level-count attributes say four. | GIS data dictionary, current floor plans, roof/elevation section, or campus facilities confirmation. | Floor stack and roof silhouette can be mis-scaled. |
| Roof form and services | M1 sees only the eave; no roof image or as-built plan. | Current high-angle/aerial photo and roof plan/elevation. | Hidden slopes, mechanicals, parapet and drainage remain invented if modeled. |
| Face direction | South frontage is inferred from address/photo and previous asset setup; image has no GPS/azimuth. | Geotagged camera station/bearing registered against the 14-vertex GIS polygon. | Portico facade may be misassigned or building rotated. |
| Historical phases | UA 62 catalog lists Home Economics/Matthews exterior material but individual photos not inspected. | Retrieve cataloged 1961/undated photographs and match to current wings; obtain phase drawings. | Renovation seams and original-vs-added facade treatment unknown. |
| Material identity/current condition | One sunlit official photo, unknown capture date; no specifications. | Current shaded/sunlit close-ups and facilities finish schedule. | Stone/concrete, mortar, frame and roof colors remain visual estimates. |
| LiDAR/elevation constraints | No exact tile or clip in the retained audit. | Select the appropriate 3DEP/IndianaMap tile, record CRS, vertical datum, units, date and class counts, and analyze ground and roof separately. | No defensible absolute roof/eave elevations available. |

## Retained provenance

`source_register.json` hashes the inspected M1–M3 evidence and points back to the local source files in `audit/matthews_hall_mthw_9326885/sources/`. Raw GIS feature JSON, reprojection, layer metadata, 2026 emergency-plan page, official event page and image remain preserved. Search results for archival exteriors are catalog leads, not inspected visual evidence. This second-pass dossier does not modify the building, builder, placement, manifest or master scene.
