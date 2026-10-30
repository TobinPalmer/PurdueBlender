# Beering Hall — exterior research checkpoint

2026-10-29. Rank 11; stable ID `beering_hall`; modeling owner Rossen. **In progress: incomplete face coverage, no modeling readiness or new visual score.** Research only.

## Identity and boundary

Use `modular/buildings/beering_hall.blend`, collection `Asset_beering_hall`. The existing [source record](../../../../audit/beering_hall/source_record.json) identifies Purdue GIS FID251, BRNG, 100 N University Street, and placement origin (-201.3499984741211, -206.14999389648438) project metres. Its approximate local GIS bounding box is X -36.503..38.732, Y -33.925..41.404 m. These are cached footprint calculations, not surveyed facade dimensions. Preserve the existing origin. The duplicate BRNG massing asset is excluded; this research does not authorize reinstating it.

The cached GIS has nine levels and undocumented vertical attributes. The contractor calls the building seven stories. Neither establishes nine identical visible floors. The older source record also retains conflicting 1992/1993 completion descriptions. Resolve floor naming, basement and rooftop levels separately from physical elevation bands; do not turn GIS extrusion or roof attributes into measured heights.

## Source and viewpoint log

The six contractor photographs below were downloaded and visually inspected on 2026-10-29 from the [project gallery](https://bcrmco.com/projects/beering-hall-purdue/), preserved as [HTML](sources/contractor_project.html). Buckeye Construction & Restoration is the project participant/provider. Photographer, capture date, camera coordinates, camera elevation and distance are unknown for this set. Upload directory dates (July/August 2024) are not capture dates. Construction equipment, temporary fences and people are transient. The independent Purdue College of Education view B07 is logged separately; its retained image is linked under `audit/beering_hall`, since the exact same bytes are already archived there.

| ID / saved original | View and useful coverage | Limits |
| --- | --- | --- |
| B01 [0529](sources/DJI_0529-scaled.jpg) | Elevated oblique across landscaped frontage; long tall glazed bar, rounded corner/drum, low wing and roofs | Trees hide lower openings; far side/service court incomplete |
| B02 [0543](sources/DJI_0543-scaled.jpg) | Opposing elevated street-corner oblique; two low-wing faces, entrance, tower above | Trees and lifts obscure portions; rear tall bar mostly hidden |
| B03 [0561](sources/DJI_0561-scaled.jpg) | Near frontal entrance detail | Workers hide parts of door frame and hardware; one doorway only |
| B04 [0527](sources/DJI_0527-1024x768.jpg) | More frontal landscaped-front view; tall glazing runs and low curved volume | Similar subject to B01 but different position; lower floors obscured |
| B05 [0528](sources/DJI_0528-1024x768.jpg) | Elevated view along rounded end; drum, adjacent stair/service block, setback terrace | End not fully frontal; foliage hides base |
| B06 [0558](sources/DJI_0558-1024x768.jpg) | Elevated near detail of upper strip and brick window surrounds | Cropped run; cannot supply whole-building counts |
| B07 [official Purdue College of Education image](../../../../audit/beering_hall/purdue_college_of_education_beering_exterior.jpg) | Independent ground-level oblique; long brick elevation, six tall glazed bays, curved return, rooftop annular room, upper tower mass and low roof; 1000×750 retained web image (EXIF original dimensions 2048×1536) | EXIF GPS position 40.4252556°N, 86.9154583°W; embedded timestamp 2020-09-30 00:02:02 (EXIF software says Photoshop, so capture time is unverified); GPS direction 319.1° true north. Embedded altitude 193.2 m is GPS altitude, not camera height above ground. Vegetation blocks lower wall, perspective compresses far bays, and full face boundaries need GIS registration. Official page does not state image capture date. |

Cardinal face registration remains provisional. B07 supplies a camera coordinate and recorded viewing direction, but the camera point is not matched against a surveyed building boundary or a current oriented aerial in this pass. Use reproducible visual zone names below until footprint registration confirms face labels.

## Partial opening and detail schedule

| Zone / anchor | Observed sequence or family | Construction implication / remaining gap |
| --- | --- | --- |
| Tall landscaped-front bar, B04/B07, from projecting low-roof end toward curved return | Six tall dark glazed vertical bays are visible in both views, separated by brick piers; B07 confirms the run continues beside the rounded corner. Smaller openings form a separate upper row above the tall bays | Cross-view agreement strengthens the six-bay count for this visible run. B07 trees obscure the base and perspective foreshortens the far end; exact floor divisions, mullion counts and boundary termination remain unmeasured. Do not model uninterrupted blue rectangles |
| Upper pale strip, B06, read left-to-right from tower junction | Ten window openings visible in this crop, the leftmost foreshortened; some broader openings show a central division. Pale vertical cladding joints and projecting eave/downpipe rhythm are distinct from window spacing | Ten is a cropped visible count, not a complete elevation total. Separate recessed strip, terrace, gutter, downpipes and brick face below |
| Brick paired opening family, B06 | Recessed dark windows separated by brick center panels; pale horizontal heads and sills with projecting edges. Jamb treatment is not a continuous pale rectangular frame on every pair | Record paired groups and tall-strip heads separately; exact surround profiles and stone type unmeasured |
| Curved end, B05 | Three clear middle rows each expose five dark opening groups across the visible arc; upper arc has taller windows, lower row is partly hidden | Counts describe the visible projection only, not the full circumference. Do not copy the same five-window run around the hidden return |
| White drum, B01/B05 | Dark vertical fields separated by pale projecting ribs, with substantial continuous top/bottom rims. Top includes an open/recessed feature behind the near rim | Cylindrical/curved room geometry and rim depth need measured plans or closer overhead evidence; no solid white cylinder or featureless flat cap |
| Low hipped wing, B02 | Two upper window rows over a lower banded base; opening widths and groupings vary near corners and entrance | Trees prevent reliable complete per-row counts. Preserve family differences rather than imposing the tall-bar grid |
| Entrance B03 | Two central dark glazed leaves, dark side fields and transom/name panel, deep brick reveal; two black lantern fixtures on broad pale entablature. Square brick piers carry repeated pale bands; projecting canopy has a substantial underside | Two leaves visible. Workers obscure hardware and side-field extent. Broad pale head has a recessed rectangular panel and stepped lower edge; retain depth rather than a flat white sign texture |

## Roof and material brief

B01/B04/B05 distinguish a low hipped red tiled-looking roof, a narrow pitched red roof above the recessed upper bar, and a taller square tower with a pyramidal red roof over a dark ventilated/glazed-looking band. White/gray flat setback roofs and parapets connect these forms. B06 reveals individual tile-like courses, pale eave/gutter and downpipes, terrace membrane seams and small roof penetrations. Roof pitches, tile specification, drainage sizes, equipment and hidden valleys remain unmeasured.

Brick appears red/brown with pale mortar in B03/B06; compare these near images with the darker overcast B02 before choosing a future material. Pale rough-faced horizontal masonry bands alternate with smoother trim/canopy surfaces. Dark window frames/glass vary with reflections and blinds. No calibrated color, roughness, glazing tint or stone identification is claimed.

The contractor's page reports exterior sealant replacement and masonry repairs (paraphrase). Treat it as evidence of envelope maintenance, not proof of wholesale window replacement or an as-built elevation specification.

## Existing-model discrepancy checks for future authorized work

The [first-pass review](../../../../audit/beering_hall_independent_grade_r2/result.json) scored 8.0 and explicitly retained footprint approximation. Recheck curved structural frontage against FID251, then register these photographs to each face. Verify separate low hipped wing, tall glazed strips, recessed roof strip, square roof tower and white ribbed drum. Existing model renders are not photographs of the building and cannot resolve these features.

## Gaps and next evidence

1. Register every view to cardinal faces using FID251 and current orthophoto; obtain opposite tall-bar/service elevations, low-wing lower rows and unobstructed ground entrances. Current counts cannot cover hidden runs.
2. Seek dimensioned original/as-built elevations and roof plans. The Purdue archive catalogue lead [1990 design-development outline specifications](https://archives.lib.purdue.edu/repositories/2/archival_objects/50259) returned HTTP403 in this pass; catalogue search discovery is not inspection of the specifications. The corporate-entity record also returned HTTP403. The [Purdue Office of Marketing and Media finding aid](https://archives.lib.purdue.edu/fa/UA62_Series3.pdf) indexes two artistic Beering Hall photographs among 1993–1994 Campus Development and Physical Plant building negatives (Box 81, Folder 23); the images were not inspected and are only an archive-access lead. Preserve the 1992/1993 conflict until documentary dates are inspected.
3. Acquire and inspect current aerial and suitable LiDAR/elevation metadata, including acquisition, CRS, units and vertical datum. No point cloud was acquired or segmented in this checkpoint; no eave/ridge/drum height is measured.
4. Complete per-floor opening schedules and facade material comparisons from additional independent providers and conditions. Current six images are one contractor package and do not establish 2026 unchanged condition.
5. Check recent renovation drawings for exterior changes separately from reported interior renovations. Keep shared landscape, fountains and neighboring assets outside building ownership until resolved.

Next action remains Beering evidence acquisition and registration; this initial checkpoint does not advance the execution cursor to rank 12.
