# Brown Laboratory of Chemistry — exterior research

**Queue rank:** 23 · **stable ID:** `brown_laboratory_of_chemistry` · **model owner:** Unassigned
**Asset:** `modular/buildings/brown_laboratory_of_chemistry.blend`
**Pass status:** Focused exterior research saved with substantial elevation, roof-detail, and dimension gaps; no modeling or model-readiness claim.

## Identity, chronology, and adjacency

Brown Laboratory of Chemistry (BRWN), at 560 Oval Drive, is the east chemistry building approved in 1967, completed in 1972, opened in 1973, and dedicated as the Herbert C. Brown Laboratory in 1987. Purdue Chemistry describes it as an east addition to Wetherill, while Purdue’s current emergency plan says Brown and Wetherill connect on floors 2, 3, 4, and basement and function nearly as one. They remain distinct exterior assets and footprints. The north-up aerial and official GIS polygon support Brown’s long east–west axis and close eastern/western site relationships, but do not define which connector segments belong to each facade.

The official OEP plan lists five main floors above grade and one basement. This aligns with the six Purdue Chemistry floor-plan sheets saved with the asset audit. The cached Purdue GIS row instead has `NUM_LEVELS=7` and `CountOfFLO=7`; it also supplies separate B, F01–F05 and R numeric fields. The snapshot’s field descriptions do not state the units or explain whether GIS counts the roof as a level, so retain the discrepancy rather than reading it as a seventh occupied story. Current use is research and teaching laboratories; the 2020 opening of Chaney-Hale moved undergraduate teaching labs out of Brown, according to Purdue Chemistry’s 150-year history.

## Footprint and measured limits

Cached Purdue campus GIS FID 247 is the occupied `BLDG Building Primary` record for BRWN. Its closed ring has 57 coordinate entries. Reprojecting that ring from EPSG:4326 to UTM zone 16N gives an approximate envelope of **112.24 m east–west by 35.80 m north–south**, perimeter **313.87 m**, and polygon area **3,240.79 m²**. These are calculations from the cached polygon, not a field survey. The existing massing audit reports a matching local envelope (~112.22 × 35.76 m), so the source asset’s broad placement and footprint extents are consistent with this snapshot.

The same GIS attributes report `Shape__Area=5603.05` and `Shape__Length=412.36`, labelled by layer metadata as esri metres. Those values do not match direct UTM measurements from the published coordinate ring (the raw area is about 73% larger). The calculation basis/projection behind the stored summary fields is unresolved; use the ring for the approximate reprojected plan calculation and preserve the raw values as a discrepancy. The GIS elevation/level attributes are `B=9`, `F01=23.25`, `F02=37`, `F03=50.75`, `F04=60.5`, `F05=73.25`, `R=87`; the units and vertical datum were not supplied with this cached feature. The project asset audit’s 16 m massing height and 18.81 m maximum including inferred roof details are also model-side values, not surveyed elevations.

## Exterior sources and view register

| View / evidence | Observations supported | Coverage limits |
| --- | --- | --- |
| North-up Esri World Imagery extract, `sources/current_world_imagery.jpg` | Confirms the long east–west footprint, stepped ends, a broad low-slope roof field, a raised central roof/mechanical zone, several rooftop equipment clusters, a repeated row of roof-edge projections along the south side, and a south-side central approach/entry stair. Brown remains visually separable from the adjacent Wetherill mass in the overhead view. | Image acquisition date is not exposed by the service response. Tree/shadow cover, resolution and straight-down view prevent reliable current window/door counts, heights, roof curb profiles, or connector ownership. Do not treat shadows as facade or equipment. Attribution and request extent are retained in `sources/current_world_imagery_provenance.json`. |
| Oblique exterior photograph, captioned Brown Laboratories of Chemistry, June 21, 1999, photo 91-16, Alexander Sergeev Purdue photo archive | Shows a long brick facade with repeated tall, narrow, dark window strips between pale, projecting full-height concrete piers/frames; pale roof-edge/corner trim; a tree-obscured lower entry zone. The visible contrast of red-brown brick and light concrete is strongly supported. | Camera bearing is not registered and the tree obscures the base. The page header/date metadata differs: its title/caption says June 21, while its page date field shows June 15, 1999. This is historic evidence, not a current facade survey. The downloaded image is retained at `audit/brown_laboratory_of_chemistry/brown_exterior_1999.jpg`. |
| Official Purdue Chemistry six floor-plan sheets (basement and floors 1–5), retained in `audit/brown_laboratory_of_chemistry/brwn-*-floorplan.jpg` | Confirms the stepped plan envelope and floor-specific internal circulation. The sheets and OEP identify Brown separately from Wetherill; OEP states which levels are connected. | Plans are undimensioned image sheets and were assembled for interior layout work. They are not exterior elevations and do not measure facade bays, floor heights, wall offsets, roof shape, or connector wall ownership. |
| Purdue campus GIS FID 247 and orthographic ring | Current campus identity, occupied primary layer, geographic position and overall plan envelope; the local bounds align with the supplied massing bounds. | Cached snapshot is retrieved from repository history, not a newly surveyed 2026 condition. GIS shape summary measurements conflict with direct projected geometry; vertical units/datum and 1997-present shape phase were not verified. |
| Purdue Archives and Special Collections UA 62 Series 3 finding aid | Catalogues “New Chemistry Building exteriors” (Brown), including the new visitor sign, in May 1973 and additional campus/New Chemistry Building scenes in June 1974. | Catalog entry points to physical contact sheets and negatives; those photographs were not available for inspection in this pass. They are a useful archival retrieval lead, not viewed evidence. |

### Partial facade and roof schedule

- **Long facade (1999 camera bearing unregistered):** repeated projecting pale concrete piers divide red/brown brick fields and narrow, dark, vertically elongated window groups. The photo’s perspective and tree cover prevent a complete bay count. Do not assign this face to a compass direction from this photograph alone.
- **South site edge (north-up overhead):** a central approach/stair interrupts the long facade line; repeated bright projections or rooftop-edge structures align along much of the same side. The imagery does not resolve door leaves, accessible ramp details, facade opening count, or whether every projection is a window bay or a canopy/roof feature.
- **End returns and connector faces:** the GIS plan and overhead image show stepped massing and adjacency, but no current frontal end/connector photograph was inspected. Avoid copying Wetherill’s south-entry pilasters, openings, or materials onto Brown.
- **Roof:** low-slope flat-looking roof area with multiple mechanical clusters and a central raised zone visible overhead. No surveyed roof plan, current equipment schedule, drainage direction, edge/parapet detail, screen dimensions, or exact roof elevations were found.
- **Materials:** brick and pale concrete are visible in the 1999 image. No current finish schedule or calibrated color reference was obtained; window frame and glazing materials, present-day repairs, and the exact pale trim material are unverified.

## Gaps to preserve

1. Inspect a current orientation-registered walkaround of north, south, east, west, both ends, entrances and the Brown–Wetherill connectors; establish complete per-floor opening counts and which bridge faces belong to which asset.
2. Retrieve the May 1973 / June 1974 UA 62 archival contact sheets and register the views; obtain a recent facade photo set because the current image is overhead and the only direct facade view is from 1999.
3. Obtain measured as-built elevations, sections, a dimensioned current roof plan and a field/survey height datum. Reconcile five occupied floors plus basement against GIS count and B/F/R elevation fields.
4. Resolve stored GIS `Shape__Area` / `Shape__Length` values versus measurements from its ring and the existing local footprint; identify the applicable historic footprint phase.
5. Verify present parapet/edge profiles, concrete/brick materials, window frames and glazing, rooftop mechanical/service screening, drainage, skylights and renovation chronology. Do not infer invisible facade treatment from symmetry or the adjacent Wetherill building.

## Sources consulted

- [Purdue Chemistry — Facts/History](https://www.chem.purdue.edu/about_us/facts-history.html), accessed 2026-10-30: east addition approval (1967), opening (1973), naming (1987), and Brown’s relation to Wetherill.
- [Purdue Office of Emergency Preparedness — BRWN](https://www.purdue.edu/operations/emergency-preparedness/brwn/), page revision 2026-04-03, accessed 2026-10-30: address, five above-grade floors plus basement, and connections on floors 2–4 and basement.
- [Purdue Chemistry — 150 Years of Chemistry](https://www.chem.purdue.edu/media/news/2024/chemistry150.html), accessed 2026-10-30: 1972 completion and the move of undergraduate teaching labs to Chaney-Hale in 2020.
- [American Chemical Society — Wetherill Laboratory of Chemistry at Purdue](https://www.acs.org/education/whatischemistry/landmarks/purdue-wetherill.html), accessed 2026-10-30: 1967 approval, 1972 completion, 1987 naming, and adjacency context.
- [Purdue Archives — UA 62, Series 3 finding aid](https://archives.lib.purdue.edu/fa/UA62_Series3.pdf), search-indexed entry for box 93, folder 27 (May 1973) and folder 33 (June 1974); PDF itself returned 403 when opened, so catalog lead only.
- [Alexander Sergeev — Brown Laboratories of Chemistry, photo 91-16](https://www.asergeev.com/pictures/archives/compress/1999/91/16.htm), accessed 2026-10-30; dated historic exterior photograph. The page’s original `brown_exterior_1999.jpg` is retained in the audit folder.
- [Esri World Imagery map service](https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer), retrieved 2026-10-30. Provider attribution: “Source: Esri, Vantor, Earthstar Geographics, and the GIS User Community.” Acquisition date for the Brown tile is not exposed; request parameters and extent are saved alongside the image.
- `research/second_pass/shared/official_purdue_buildings_wgs84_snapshot.json`, FID 247; source provenance and measurement caveats in `research/second_pass/shared/location_source_provenance.json`.
- Existing asset context only: `audit/brown_laboratory_of_chemistry/QA.md`, `independent_review.md`, and six saved Purdue plan sheets. These model/QC notes are not accepted as independent exterior evidence.

## Research-only disposition

Focused exterior pass complete with major gaps retained. No building geometry, master Blender file, placement, owner assignment, or grade was changed. The legacy facade source is 1999 and the aerial capture date is unknown; the dossier does not authorize or certify a new asset build.
