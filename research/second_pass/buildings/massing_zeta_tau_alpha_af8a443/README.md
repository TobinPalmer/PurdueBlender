# Zeta Tau Alpha, Alpha Theta — second-pass exterior research

**Queue rank:** 54 · **Stable asset ID:** `massing_zeta_tau_alpha_af8a443` · **Model owner:** Unassigned
**Reference condition:** chapter house at 118 Waldron Street; official chapter photo from September 2022 and mapped Street View panorama recorded April 2026. Purdue FSCL lists the chapter in October 2026.
**Review date:** 2026-10-30 · **Status:** Provisional facade brief; three elevations, exact openings, roof intersections, measured heights, material specifications and primary 1952 photo remain unresolved.
**Phase:** Research only. No builder, asset, placement or master-scene edit was made.

## Identity, chronology, location, and source limits

Purdue’s official BuildingShapesZip4 FID 773 identifies `SOZTA / Zeta Tau Alpha` at **118 Waldron St** (G1). Purdue Fraternity, Sorority and Cooperative Life’s Panhellenic roster currently lists Zeta Tau Alpha and its chapter site (I1). Alpha Theta’s official September 24, 2022 article documents its 101-year celebration at Purdue and says the photographed chapter house has been home to the chapter since the 1950s (V1, I2). Separately, Purdue Archives’ MSP19 News Service inventory lists one photograph titled “Zeta Tau Alpha Sorority — 118 Waldron St. For: PRF,” dated April 26, 1952 (H1). This makes the chapter/address identity strong and adds a historical phase marker, but the underlying archive photo was not retrievable from the public inventory. I therefore do not claim that the visible 2022 facade was already present in 1952 or that 1952 is the construction year.

The target reference is the chapter residence at 118 Waldron as seen in the official 2022 near-front photo and the April 2026 mapped Street View panorama. The later Street View physically shows the address frontage, but has a large tree, neighboring buildings and parking between camera and facade. Chapter activity is supported by the university roster; building condition is supported by the 2026 panorama only at distant street-view resolution. A prior model/audit is not building evidence.

The fresh October 30, 2026 GIS feature contains the same 15-coordinate closed ring as the October 26 raw query (14 unique vertices; maximum coordinate difference is 0 in the provider coordinate system). Under the project’s documented inverse Web Mercator and local approximation, the shape is about **28.03 m east-west × 36.71 m north-south** and **744.71 m²** in area (G1–G3; transformation is fully described in the prior [source record](../../../../audit/zeta_tau_alpha/source_record.md)). These are transformed map-polygon metrics, not surveyed wall lines or facade bearings. The feature’s `NUM_LEVELS=1` and `CountOfFLO=1` conflict with the visible multi-level wall bands and dormered roof. `Extrution=12` has no documented unit or measured-elevation semantics. The candidate’s 11.91 m maximum Z is an asset dimension/height estimate, not a building survey.

## Actual viewpoints and coverage

Original images, fresh GIS records, prior raw feature and page snapshot are retained in `sources/`; [source_register.json](source_register.json) gives URLs, dates, page/view IDs, camera metadata, hashes and specific limitations. The official image has no camera pose. Only the Street View source has map camera coordinates and a provider heading.

| ID | Position, direction, date and distance | What is visible | Limitations |
|---|---|---|---|
| V1 — Alpha Theta official photo | Event on 2022-09-10; near-frontal from the front lawn; camera location, direction and height not supplied; 1024×681. | Broad central front composition in color, brick wings, portico and pediment inscription, entry zone, repeated window runs and low dark roof edges. | People cover most of the lower front; overhanging branches cover pediment and roof. Single face, no scale, and no close structural details. |
| V2 — Google Street View | Pano 8sVKIehKbcyb50bjkmpU1Q, camera at 40.4255967, −86.91789, heading 65.04872° and pitch 0°. Imagery date recorded as April 2026 in the prior audit source review; retained original thumbnail 900×600. | Wider oblique street context, central portico, repeated front windows, broad roof and several dormers, multiple roofed volumes, and adjacent buildings that can be separated from the red-brick target. | One camera station (not a walkaround), distant perspective; a large foreground tree masks the central facade/roof. Cars and neighboring structures hide the base, corners and side-wall junctions. |
| H1 — Purdue Archives catalog | MSP19.008.154, one photograph dated 1952-04-26, explicitly titled for ZTA at 118 Waldron St. | Historical address and chapter association. | No visual content available in the inventory PDF; it is not a second facade view. |
| G1–G3 — Purdue GIS | Current named FID773 and official layer metadata, compared against prior saved FID773. | Address/identity and a 14-corner plan constraint; the returned coordinates are unchanged. | No facade labels, elevations, roof plan or field accuracy statement. |

This is not a complete walkaround. We have the central street-facing side in two partially obstructed views and a limited glimpse along its oblique side/roof context. The opposite long facade, both ends, rear/service wall, all corners, porch underside, roof from above and every secondary return remain unseen. The neighboring buildings in V2 are not part of the target unless a footprint/connection source confirms it.

## Facade organization and opening schedule

Photo-relative labels are used because the official image has no registered compass bearing and no GIS edge is labeled “front.” In V1 the front is broad and approximately centered on the portico; V2 shows the same street frontage obliquely. The source quality does not support a complete exact bay count across the full wall, so partial runs stay partial.

| Face/run | Source-backed arrangement | Confidence and unknowns |
|---|---|---|
| F-A — central portico and entry | Centered projecting pale portico, with a row of full-height columns supporting a projecting entablature and triangular pediment. Raised `ZTA` letters sit high on the pediment front. A single central entrance zone aligns below; its door leaves/frame are concealed by the 2022 group and foliage. | High for composition, centering, inscription and entry alignment. The photo supports several columns but does not safely resolve the total, capital/base shape, spacing or projection. Step count and accessible path are unknown. |
| F-B — street-front wall, left of portico | Red brick side run with repeated light-trimmed rectangular windows on an upper and lower wall band. Multiple bays are visible, but several are obscured by leaves and attendees. | High for material appearance and repeated rhythm; exact per-floor opening count, bay widths and any concealed/blank bays unresolved. |
| F-C — street-front wall, right of portico | Similar brick wall continues on the right with multiple pale-trimmed rectangular window openings in upper/lower runs. Portions nearest the entry are obscured by people and the portico. | Medium for repeated openings and color; no reliable total or exact matching with F-B. Do not assume mirror symmetry. |
| F-D — roof and upper wall | V2 shows a broad dark pitched roof with several small dormer windows and a taller/raised roof section behind portions of the front roofline. V1 sees dark roof edges to either side of the pediment. | Medium for multiple pitches and dormered silhouette; tree and perspective prevent a reliable dormer count, ridge direction or assignment to separate footprints. |
| F-E — partial side/return | V2 reveals a long side/return mass and changing roof/eave heights around the front; substantial portions overlap the neighboring buildings and tree. | Low; target/neighbor boundaries, wall openings and exact wing connections are uncertain. |
| F-F — opposing long face, opposite end and rear/service | No direct target elevation. | Unknown. No opening, door, blank-wall or symmetry assumptions. |
| Window and door typology on visible faces | Rectangular windows with light casing and divided/multi-light appearance; one central entry zone under portico; smaller rectangular windows in roof dormers. | Medium for categories only. Exact sash lights, pane counts, frame setback, sill/head, exterior storm panels, door leaves, and floor assignment are too occluded/distant for a build schedule. |

The images establish more than one horizontal wall/window band below a dormered roof, but not a verified storey count or floor-to-floor heights. Exact front-window counts should not be fabricated from foliage and people or inferred from the prior model. A perpendicular or measured elevation is needed to complete the schedule.

## Massing, signature details, materials, and vertical limits

The main recognition feature is the pale classical portico centered on a long red-brick frontage, with a triangular pediment and raised chapter letters. The portico projects from the wall, but its depth and entablature profile are not measured. The house extends laterally into offset/returned sections and its dark pitched roof has several dormers and at least one raised ridge/volume visible in V2. The 14-corner mapped ring is irregular and supports a multi-part plan, but the images cannot map each return to a specific wing or prove that adjacent visible buildings attach to the target. No roof plan, roof survey, section, point cloud or datum-tied elevation was found.

V1 supports red/warm-brown brick, pale column/trim and window casing, dark lettering, and a dark roof appearance. V2 corroborates dark roofing and exterior brick but is distant and overcast. No calibrated color, brick bond/mortar, stone versus painted portico material, roof covering, window frame product, shutter use, drainage path or trim specification is established. Event clothing, balloons, temporary signs and landscaping are not architecture. The `ZTA` lettering is visibly attached to the pediment and is a permanent recognition feature in V1.

## Evidence-led future brief and audit comparison

A later, separately authorized model task should preserve the source polygon only as a plan-position constraint pending survey; retain a brick, multi-volume house with a central pale columned portico, triangular lettered pediment, grouped front window bands and dark dormered roof. Use the photos to preserve the broad asymmetrical front/side relationship while leaving hidden sides open for evidence rather than mirroring. Obtain a registered walkaround or archival drawings before finalizing edge-to-face mapping, openings, roof components or heights.

Against prior asset/audit findings (the model remains a check target, not truth):

* The fresh GIS polygon exactly matches the earlier source geometry; the previous independent-grade IoU verifies geometry transfer, not surveyed footprint accuracy.
* The 2022 official house photo supports the red-brick facade, pale trim, centered columned portico, triangular pediment and ZTA letters; it does not establish hidden opening schedules or measured column geometry.
* V2 resolves a mapped public frontage and visible dormered roof sections but cannot tie each dormer and ridge to a specific GIS return because the large tree and adjacent houses conceal the intersections.
* One-floor GIS counts and undocumented `Extrution=12` remain in conflict with observed multiple window bands and roof dormers. The model’s 11.91 m peak remains an estimate.
* The 1952 archive inventory and chapter “home since the 1950s” claim reinforce this address’s long use, while the archive image remains uninspected. Do not represent the 2022 front as proven 1952 fabric.

## Specific gaps and resolution path

| Face/feature | Gap and sources checked | Resolving evidence | Effect |
|---|---|---|---|
| 1952 photo and building phase | Purdue Archives lists one photo at this address/date but provides no image in the finding aid. | Request or digitize MSP19.008.154; compare roof/portico/windows to current views; inspect verso and accession context. | Current building’s construction/alteration chronology and survival of historic fabric are unresolved. |
| All faces and compass registration | Two views cover a tree-obscured front and one limited oblique; only V2 supplies a camera pose. | Dated daylight walkaround at every corner with camera coordinates/headings, or mapped multi-station street imagery. | No full elevation coverage, rear schedule or compass-edge mapping. |
| Entry/portico | Lower front blocked; no close column/door images or elevation. | Straight-on close photo, measured landing/stairs and original/as-built front elevation. | Column count, profiles, entry leaves, depth and stair geometry remain uncertain. |
| Openings | Partial repeated window bands; no per-face/per-floor totals or pane details. | Orthogonal photographs of every face plus dimensioned elevations/sash schedule. | Full bay spacing and hidden opening locations cannot be defended. |
| Roof and height | Street view only; no overhead roof plan, section or reliable vertical point data. | Roof/elevation drawings or georeferenced classified LiDAR with CRS, vertical datum and reproducible building-point selection. | Ridge/eave heights, slopes, dormer positions and wing junctions remain estimated. |
| Materials and current physical state | One 2022 color event photo and distant April 2026 pano; no specifications or close views. | Daylight detail photos and house-corporation/Facilities repair or materials records. | Masonry, trim, roof, window products/colors and post-2026 condition are not verified. |

**Package:** [source register and SHA-256 hashes](source_register.json); originals and current query snapshots are in `sources/`; prior audit, grade, asset and GIS conversion notes remain at `../../../../audit/zeta_tau_alpha/`. Research only; no model readiness or model edit is implied.
