# 4. R. B. Wetherill Laboratory of Chemistry: exterior research

Prepared 2026-10-28 local time (some download timestamps are October 29 UTC). **Prepared with explicit coverage gaps; no model changed or accepted.** Stable ID `wetherill_laboratory_of_chemistry`, asset `modular/buildings/wetherill_laboratory_of_chemistry.blend`, modeling owner Rossen. Research order continues with rank 5 after this dossier; unresolved evidence remains listed below.

## Identity and defining features established so far

The building is at **560 Oval Drive**, WTHR, Purdue GIS **FID257**. Purdue's [department history](https://www.chem.purdue.edu/about_us/facts-history.html) describes a first wing completed in 1930 and subsequent expansion; its [landmark page](https://www.chem.purdue.edu/wetherill/) places construction across 1928–1955. Brown Laboratory is an adjacent separate asset, not another Wetherill wing to duplicate.

The [Purdue archival description, UA136](https://archives.lib.purdue.edu/repositories/2/resources/1483) identifies red brick with Indiana limestone and five chemistry relief subjects above the main doors: analytical balance, biological rat/leaf, inorganic periodic-table portion, organic tetrahedron, and physical phase diagram/thermodynamics equation. These are distinctive facade details that require close references; generic rectangular panels will not reproduce their appearance.

The inspected [full-resolution Purdue front photograph](sources/purdue_front.jpg), [original source](https://www.chem.purdue.edu/admissions/admissions/WTHR.JPG), shows a low ground-level upward oblique of the main entrance facade. Its capture date is unspecified. Defining observations include a tall central stone composition with Ionic-style capitals and attached columns/pilasters, multiple rectangular entrance recesses, broad steps and pale metal handrails. Larger multi-light windows sit above entrances; the uppermost window row is shorter. Stone quoin-like corner bands, belts, carved panels and engraved scientist names interrupt the brick fields. Several window-mounted air conditioners are visibly present in this photograph; their current positions must be verified rather than repeated across every bay. The projecting dark/greenish cornice differs from the pale stone trim. Complete opening counts have not yet been recorded.

## Sources and viewpoint coverage

| Reference | Perspective / source date | Current use and limits |
| --- | --- | --- |
| [Purdue front photograph](sources/purdue_front.jpg) | Near/medium ground-level low oblique; capture date unknown | Main entrance, window/mullion patterns, limestone relief and sunlit brick/stone. One camera position, not all-face coverage. Original 6016×4016 file retained for details. |
| [Esri overhead](sources/aerial_world_imagery.png), [successful export metadata](sources/aerial_export_wide.json) | Orthographic overhead; acquisition date unknown | Perimeter roof, inset roof/service zones and nearby buildings. Initial narrow export returned no image; wider export supplied the actual saved image. |
| [Purdue elevated campus reference](../bell_tower/sources/purdue_elevated_ese.webp), [published photo essay](https://purduenews.exposure.co/happy-birthday-purdue-bell-tower) | Elevated oblique facing east-southeast; published 2020, WALC plaza still under construction | Wetherill appears behind/right of tower; useful contrasting roof/context evidence, not a complete frontal elevation or current landscape reference. |
| [Purdue history snapshot](sources/purdue_history.html) and [landmark snapshot](sources/purdue_landmark.html) | Department source pages | Identity/construction sequence; historical photo candidates identified but not yet downloaded or counted as inspected viewpoints. |

[Requested sources](sources/requested_sources.json) and [download/access index](sources/reference_download_index.json) retain original URLs, providers, resolved URLs, timestamps and hashes. The [Quantum Optics exterior photograph](sources/purdue_optics_exterior.jpg) has now been downloaded and inspected: a very close upward oblique resolves the five relief panels, window mullions, Ionic capitals, portal scrollwork and building-name frieze. The [Alexander Sergeev winter photograph](sources/sergeev_1999_winter.jpg), author-captioned January 3, 1999, supplies a separate distant corner view with roof stacks and two facades; its exact compass registration is unverified. **The page's AI-generated narrative is not factual evidence.** A small [historical entrance photograph](sources/purdue_historical_front.jpg) is retained for chronology, not current window/color confirmation. [Additional download results](sources/additional_download_index.json) record a Flickr HTTP403 and ACS booklet non-PDF response; neither is claimed as inspected imagery. ACS's article was readable through the web research service, but its direct download returned a small anti-bot challenge, explicitly labeled in the index. It is not a saved article snapshot. Source pages retain provider copyrights; no texture-reuse license is inferred.

## Roof and material notes

The actual overhead image shows brown/red pitched perimeter roof sections surrounding extensive flat/inset service areas, ducts and many repeated ventilation stacks. Do not create one simple hip or fit a solid roof over all interior setbacks. Segment primary roof, lower roofs, raised enclosures and service equipment separately when modeling is later authorized. The aerial's acquisition date is unknown, so every large service feature needs date reconciliation.

The front daylight photograph supports red-brown brick, light warm limestone, dark frames and a weathered greenish cornice, but not fixed measured RGB values. Facade shade, pale sky reflections and glass transparency affect color. Obtain opposite faces in multiple daylight conditions before choosing final materials; neither night views nor a single sunlit patch establishes the building-wide color.

## GIS and LiDAR already acquired

[Saved official feature](sources/purdue_footprint.json) retains FID257 in WGS84, with [shared cached-source provenance](../../shared/location_source_provenance.json). It is not a new survey. Confirm courtyard/roof offsets and attached links against this ring before deriving a simplified mass. No manifest or placement changes were made.

The [Indiana tile query](sources/lidar_delivery_tiles.json) selected **in2018_29951885_12** and **in2018_30001885_12**, dated **April 20, 2018**. Actual full-resolution COPC spatial queries produced portable [LAZ crops](data/lidar/) totaling **43,592 points**: 2,230 west-context points and 41,362 body-envelope points. The context clip has no points inside the footprint; the body clip has 23,607 inside. [Crop/source statistics and hashes](sources/lidar_crop_summary.json), tile COPC metadata and [request index](sources/site_download_index.json) are preserved.

The source compound CRS is **NAD83(HARN) / Indiana West (ftUS) + NAVD88 height, Geoid12B (ftUS)**, with full WKT retained; horizontal source EPSG:2968 inside a bound CRS and vertical EPSG:6360. All native axes use **US survey feet**, converted by **0.30480060960121924 m/ftUS**. Scene Z is not automatically NAVD88 elevation. Indiana's public archive is [documented as CC0](https://registry.opendata.aws/in-elevation/).

No class-6 building classification exists in these clips. Classes 1, 2 and 7 are unclassified, ground and noise. In the body tile, outside-footprint class-2 ground median is **620.0 ft NAVD88**. A 1 m eroded footprint contains 21,319 class-1 returns; p50/p90/p99 heights above that reference are **17.514 / 19.205 / 22.098 m**. These are mixed return statistics, not measured eave/ridge/floor levels. Segment roofs and roof equipment, reject non-building objects and inspect registration before using heights. Airborne cloud density cannot resolve relief carvings or facade window placement.

## Added independent ground views and face coverage

The [Maps source index](sources/maps_download_index.json) records the exact reproducible URLs, photograph/panorama IDs, capture months, attributions, screenshot hashes and limits. All screenshot credits are retained. Near, medium and far are descriptive distances; camera heights and metric distances were not measured. These captures are public-source research, not photographs taken on site.

| Face / detail | Added evidence | Observed features and remaining uncertainty |
| --- | --- | --- |
| South entrance, near frontal | [Ludomir B, September 2022 capture](sources/maps_front_ludomir_2022.png), [metadata](sources/maps_front_ludomir_2022.txt) | Five central window/relief bays separated by six Ionic-style pilasters; three recessed door groups below, three decorated overdoors, barred low openings flanking doors, broad stairs/handrails. Photo label is October 2022 while footer says capture September 2022; both retained. |
| South name/window detail | [Ludomir B detail](sources/maps_south_names_ludomir_2022.png) | FARADAY, GIBBS, PASTEUR and RAMSAY inscriptions over multi-light windows; distinct stone panels and sill/reveal depth. A distinct photo ID alone does not prove another camera position rather than a crop. |
| South full frontage, far | [Georgeon Winsley, February 2017](sources/maps_far_front_georgeon_2017.png) | Full stepped silhouette, red roof, upper short windows and roof vents; tree branches obscure several bays. Independent distant position supplements close upward views. |
| North recessed service wall | [Google Street View, September 2017](sources/streetview_north_service_2017.png) | Large rectangular drive-under/loading opening, irregular mixture of ground-level glazing and blank panels, visible AC units, stacked rectangular louvers interrupting upper window rows, steps and rails. Do not extend the ornate south front or a uniform window grid onto this wall. |
| Northwest / west return | [Different September 2017 panorama](sources/streetview_northwest_2017.png) | Two exterior faces, lower infill panels, deep basement/retaining edge, tall window rows and shorter top row, dark cornice and pale belts. West opening counts need a more frontal bay sequence; this view is oblique. |
| Northeast / connection | [September 2017 camera](sources/streetview_northeast_connection_2017.png) | Corner stone bands and glazed connector toward Brown; adjoining Brown brick is separate. Sun flare and trees obscure portions. |
| Southeast / east return | [Andrew Huang, January 2019](sources/maps_southeast_andrew_2019.png) | Long east face with pale vertical stone divisions, multi-light windows and ground-level dark openings; a tall glazed connection to Brown on pale supports. Lower connector is blurred and cannot establish door geometry. Contributor panorama is titled Catalyst Cafe; actual exterior is identified from facade and neighboring context. |

The north-service, northwest and northeast sources have **different panorama IDs and camera locations**, rather than rotations of a single panorama. Requested Maps viewpoints were not always usable: a west request resolved inside Stanley Coulter and an initial south request showed mostly unrelated/obscured campus context. Their text records are retained as rejected attempts, not accepted exterior views. The useful northern Google imagery is September 2017, not 2026. Gallery access is limited and predominantly contains interiors, which were excluded from exterior counts.

## Detail and color checklist for a future modeler

Inspect the [Quantum Optics close-up](sources/purdue_optics_exterior.jpg) beside the frontal 2022 image: the pilasters have actual projection and capital/base profiles, each chemistry relief has its own subject and labeled band, and the three door recesses have sculpted scroll/crown details. Window frames divide glazed lights within a stone/brick reveal; they are not flat colored rectangles. Engraved scientist-name panels on the side fields and ironwork at the low flanking openings are visually significant. Do not create fictional arches at these rectangular portals.

Compare the sunlit original front, close-up, shadowed north wall and January 2019 east return when matching materials. Old/new exposure, pane reflections, wet/snowy ground and low sun materially affect apparent brick/stone/cornice colors. The northeast frame's sun flare is a poor color reference. Identify which roof stacks, louvers and window AC units still exist in more recent views before a current-date model pass. No calibrated color target was obtained.

## Remaining evidence gaps

There is now useful evidence of all principal face directions, close entrance details, opposing corners, different ground distances, elevated context, overhead imagery and actual LiDAR. **A complete current per-face window count, recent post 2019 service/east views, west frontal bay sequence, roof-equipment updates and measured facade/roof profiles remain unverified.** Photosphere positions and orientation can be approximate; facade identification uses visible geometry/context as well as labels. Do not infer invisible details from symmetry. Newer imagery or plans are still needed before claiming current whole-building accuracy, and this dossier is not independent model acceptance.

## Focused depth pass — October 29, 2026

This pass converts inspected frontage and rear-service photographs into an opening/detail schedule and adds an actual historical plan. It advances with the remaining gaps recorded, following the user's request to cover the list without exhaustive delays on one building. No model work or new acceptance score is implied.

### Plan and chronology additions

The [Purdue 19th BCCE program](sources/purdue_bcce_program_historical.pdf), [original PDF](https://www.chem.purdue.edu/bcce/BCCE_Program_book_white_pages.pdf), is **34 PDF pages**. Its metadata identifies Bill Robinson as author and May 31, **2006** creation/modification; this is a file date, not a survey date. **PDF page 24** was rendered and visually inspected: it labels Wetherill and Brown separately, their second-floor circulation, the entrance between them, wheelchair routes and changes to first/third-floor rooms. It is useful historical connection/layout evidence; it is neither a current as-built plan nor an exterior elevation. The two laboratories must remain separate assets even where linked.

[Purdue Chemistry's 2024 anniversary account](sources/purdue_chemistry_150_2024.html), [original](https://www.chem.purdue.edu/media/news/2024/chemistry150.html), independently distinguishes the first phase beginning in 1928/dedicated in 1930 from the 1955 Wetherill naming. These milestones do not establish every wing's current exterior. Searches also located auditorium/classroom and utility renovation references, but no current dimensioned exterior drawing set was inspected; interior work is not proof that the facade was replaced. The 2018 planning recommendation for renovation is not a completed project record.

### South frontage schedule

Index the **five stone relief bays left to right when looking at the south front**; use `purdue_front.jpg`, the Quantum Optics close view and the registered 2022 front together. The high-resolution original was inspected in a closer analytical crop; that crop is not an independent camera position. The five bay labels read **ANALYTICAL, BIOLOGICAL, INORGANIC, ORGANIC, PHYSICAL** in that order. These are not interchangeable decorative panels.

| Zone / IDs | Observed opening layout | Defining detail / limits |
| --- | --- | --- |
| S-C1 through S-C5 | Five stacked central window/relief bays, bounded by six projecting Ionic-style stone pilasters | Each relief lies between main window levels. Capitals have carved scrolls; shaft/base profiles project and cast shadows. No full depth/dimension survey. |
| S-C main window family | Clear central samples show four narrow vertical glass columns with stacked sash/grid divisions and a heavy intermediate horizontal rail | Preserve smaller panes and frame/reveal thickness; upper and lower sashes are distinct. A single undivided rectangle omits the visible rhythm. Some bays are occluded or have blinds; do not assume identical infill/transparency everywhere. |
| S-C attic row | Shorter divided windows above the long engraved building-name frieze | The original photo shows window-mounted AC units in several openings; these interrupt glazing and must be date-checked, not copied to every bay. Exact full-height light counts are not certified. |
| S-D1, S-D2, S-D3 | Three separate rectangular door recesses under the central composition | Deep stone reveals, individual carved scroll/crown overdoors, broad common stair approach with pale handrails. Do not turn the openings into rounded arches. Door-leaf details at the darkest recesses remain insufficiently clear. |
| S-LB / S-RB | Low barred openings flanking the entrance group | Dark metal grilles with scrollwork along the top; pale surrounds. Keep separate from the three doors and larger upper windows. Planting/perspective obscures parts. |
| S-R named fields | In the right-hand field of the full original, name panels **BERZELIUS, BUNSEN, CURIE, DALTON** are legible across the visible sequence | Names sit in pale spandrel fields between larger window rows; outer continuation is cropped. This is an observed run, not the complete inscription inventory. |
| S-L named fields | The separate 2022 detail resolves **FARADAY, GIBBS, PASTEUR, RAMSAY** | Confirm their exact placement against the full front rather than alphabetizing or repeating them arbitrarily. |
| South flank windows | Larger dark divided main-story openings below shorter attic lights, with pale heads/sills and irregular AC insertions | Full flank counts, all mullion exceptions and current units remain incomplete. Use each visible bay, not a mirrored central block. |

The chemistry panels combine different shallow scientific motifs with a repeated lower botanical/scroll decoration and engraved subject label. Analytical shows a balance motif; biological combines organism/plant motifs; inorganic includes a periodic-table grid; organic uses a tetrahedral motif; physical includes thermodynamic/diagram symbolism. Preserve the source's actual carving outlines; these descriptions are identification cues, not substitute sculpting references. Stone corner bands, fine masonry joints, greenish weathered cornice, repeated underside blocks and pale course projections are separate elements with visible depth.

### North service-wall schedule, dated September 2017

Use [the saved north service image](sources/streetview_north_service_2017.png), looking at the recessed rear wall. Start **immediately right of the large drive-under opening** and move right through the exposed ground-level span. This describes the photographed run, not the whole north elevation or verified 2026 state.

| ID, image order | Ground-level opening | Evidence and exception |
| --- | --- | --- |
| N-G1 | Divided glazing with a low projecting AC unit | First narrow opening immediately beyond the loading opening |
| N-G2 | Opaque/blank rectangular infill | Do not make it transparent glazing |
| N-G3 | Divided glazing with a low AC unit | Second obvious AC-bearing opening in this span |
| N-G4 | Opaque/blank rectangular infill | Same outer opening family, different contents |
| N-G5 | Opaque/blank rectangular infill | Keep the exposed masonry pier spacing |
| N-G6 | Opaque/blank rectangular infill | Do not replace the row with seven identical windows |
| N-G7 | Taller narrow door-like opening near the stairs | Exact leaf/glazing layout is not readable enough to certify |

Above this span, the source shows several distinct window/light groupings, darker infill/louver-like openings and a large square louver near the right-hand return. The source resolves broad differences but not every grille blade/pane. The loading opening has depth, an overhead edge, yellow protective elements and a drive/passage beyond; it is not another window. Blue coverings and movable objects at the bottom of the image are temporary site conditions. This utilitarian rear differs substantially from the stone south composition.

The [northwest oblique](sources/streetview_northwest_2017.png) provides an opposing return and basement/retaining relationship; [northeast](sources/streetview_northeast_connection_2017.png) and [southeast](sources/maps_southeast_andrew_2019.png) show the distinct glazed link toward Brown, pale structural divisions and supports. Full west/east bay counts and lower link-door geometry remain unresolved. Do not assign all of Brown's visible wall to Wetherill.

### Construction brief, material comparison and next pass

For later authorized modeling: register the primary footprint and wing/connection boundaries; establish separate roof zones and service roofs; lay out the five central south bays and three entry recesses first; add each named flank and dated rear opening run separately; then match actual cornice, pilasters, relief panels, sills, window frames, rainwater elements and stairs. Keep the rear service opening and bridge as distinct conditions. Reconcile the 2006 plan, 2017 rear, 2019 east and 2022 front with any newer references before claiming one current-date facade.

Material sources to compare are the high-resolution south original and close Optics view for stone/brick relief, shaded north for darker recess/frame behavior, and the winter east view for overall pale band distribution. Warm sunlit limestone, cooler shaded limestone and reflective glass must not become different arbitrary stone colors. Conversely, the greenish weathered cornice is not the same material as the pale limestone bands. No calibrated RGB/roughness or roof manufacturer finish is established.

Remaining high-impact gaps: complete current opening counts outside the central composition, newer rear/east condition, west frontal coverage, full roof plane/equipment segmentation and exact profile dimensions. The saved schedule makes the visible runs actionable without filling those gaps by symmetry. **Advance to rank 5, University Hall**, preserving these follow-up needs and the original source history.
