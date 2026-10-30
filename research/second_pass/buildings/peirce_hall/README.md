# Peirce Hall — second-pass exterior research

**Queue rank:** 34 · **stable ID:** `peirce_hall` · **asset owner:** unassigned for modeling  
**Existing asset reference:** `modular/buildings/peirce_hall.blend` · Purdue GIS FID 216 / PRCE  
**Review date:** 2026-10-30 · **Status:** focused exterior pass saved with major coverage and dimension gaps; provisional.

This pass re-inspected the Purdue Events facade photograph at full size and cross-checked its visible elevation against the existing first-pass notes, official GIS identity and archival building chronology. The view gives a useful reproducible north-front schedule: six upper sash groups over six tall recessed brick panels with low horizontal inset windows, with a separate lower window/entry tier. It does not document the other facades, roof surface or measured elevation. This is a more reliable north-front description, not a claim that the complete building is ready to model.

## Identity, historic phases and current boundary

Purdue GIS FID 216 identifies Peirce Hall (PRCE), address 701 3rd Street, and a three-level record. Purdue Archives describes the current Peirce Hall as the remaining north end of a 1935 building, with a small addition in 1980 and Psychological Sciences attached on the north in 1983; the south end of the older combined building was removed in 1989–1990 for Class of 1950 Lecture Hall. Purdue Physics independently explains that the 1905 Physics Building was a different, 75 × 130 ft building on the site now occupied by Class of 1950, and that the current Physics Building (PHYS) is at another location. Therefore, do not extend Peirce's present footprint south into the Class of 1950 site or identify the adjacent north connector/wing as Peirce without a wall-boundary source.

The intended appearance is the surviving contemporary Peirce Hall facade in the Purdue Events image (P1). That event listing shows the present name/address, with the image posted May 30, 2022 according to the previously retained audit notes. The actual photo capture date is unstated. Archived names (“Biology Annex,” “Stanley Coulter Annex,” and “Physics”) describe earlier usage; they do not independently date the visible brick facade or establish which portions of the current facade predate the 1980 addition.

## Footprint and campus relationships

The prior audit identifies the exact Purdue building-map feature FID 216 and records its source snapshot and map attributes in `audit/official_purdue_buildings_wgs84.json` and `audit/official_building_layer_metadata.json`. Its source ring is reproduced in the existing asset. The first-pass record gives campus-frame bounds X −134.8194 to −95.5219 m and Y −98.0691 to −72.5735 m, with origin at the midpoint of those projected bounds (-115.170644, -85.321301) m. The corresponding local footprint bounds are about 39.30 × 25.50 m. The official map reports `NUM_LEVELS=3`, `Shape__Area=1555.84` and `Shape__Length=170.12`; GIS map summaries are not an independent field survey and the level field's definition is not documented here.

The site is tightly joined to larger campus buildings. Current aerial context referenced in the prior record shows a flat-roofed, compact volume between the Class of 1950 Lecture Hall to the south and Psychological Sciences to the north. The GIS feature and historical record do not define connector ownership, shared wall depth, or whether any links are above-grade enclosed connections. Keep those adjacent assets and any connector as separate identities until a registered plan confirms their seams.

## Inspected source viewpoints

Camera GPS, bearing and height were not available for the retained ground photo. Its frontal appearance permits counting the pictured facade, but not assigning that image to a compass side solely by the feature name; its north/front assignment follows the previous photo-to-site identification and needs a registered camera position.

| ID | Source and capture/publication date | View actually inspected | What it supports / limits |
|---|---|---|---|
| **P1** | Purdue Events, [Peirce Hall](https://events.purdue.edu/peirce_hall), facade image direct source URL listed in `source_register.json`; posted 2022-05-30 per prior audit; photographer and capture date unstated. Original retained as `sources/purdue_events_facade_2022.jpg` (478 × 318 px). | Near-frontal, eye-level-to-slightly-raised view of the principal brick facade, with central approach, bicycles and trees in the foreground. | Strong opening/panel rhythm and parapet silhouette; exact camera station/height unknown. Trees partly cover both lower corners; foreground bikes, racks, paths and hydrant are not facade elements. No close roof or return view. |
| **P2** | Prior audit's Google Maps satellite inspection, pinned at 40.42675, −86.91515; [map view](https://www.google.com/maps/@40.42675,-86.91515,163m/data=!3m1!1e3). | Overhead map view previously described as supporting flat roof and neighboring context. | No raw image or imagery acquisition date is retained in the second-pass folder. Use as a lead only; it does not document roof equipment or wall openings. |
| **P3** | Purdue Archives, [Peirce Hall history](https://archives.lib.purdue.edu/agents/corporate_entities/673), current online finding-aid page; raw HTML retrieval was blocked by a Cloudflare challenge and is not treated as a local evidence snapshot. | Textual historic chronology, not a photographic viewpoint. | Supports building phases, former uses and demolition boundary; provides no facade schedules or measured drawings. |
| **P4** | Purdue Physics, [The Early Years](https://www.physics.purdue.edu/about/history/early_years.html). | Historical identity/context page. | Distinguishes the demolished 1905 Physics building from current Peirce and PHYS; not exterior-image evidence. |

P1 is the only actual ground-level facade image newly inspected in this pass. Crops of P1 are not separate viewpoints. Search results did not produce an additional clearly identified Peirce exterior view, and the Archives raw-page challenge prevented capture of its finding-aid page; these limitations stay open.

## P1 facade schedule (image-relative)

For reproducibility, read from image-left to image-right along the pictured wall. This schedule is limited to P1's apparent full facade plane, not the whole building perimeter.

| Tier / feature | Count and sequence visible in P1 | Observed form | Limit |
|---|---|---|---|
| Upper window row | **6** spaced groups across the brick field. | Dark rectangular multi-light sash, each group appearing as paired vertical units within a pale lintel/sill frame. The spacing is regular but not equal to the wider central panel bays below. | Small image; individual sash mullions are only partly resolved. Exact group widths/sash divisions and corner offsets are unknown. |
| Middle blind/recessed row | **6** tall brick-colored recessed panels, aligned approximately below the upper groups. | Narrow pale vertical margins/returns define deep, tall rectangular recesses; each has a small horizontal slit-like glazed opening near its lower part. These are not ordinary full-height windows and should retain their strong shadow/reveal depth. | The photo shows apparent recess shading but no section/profile. It cannot establish whether every panel is an original opening, later infill, or a consistent material change. |
| Ground-level openings | Several visible smaller windows and door-sized openings; lower corners are partially obscured. | Narrow vertical sash openings and light-toned wall/entry surrounds break the darker brick base. A primary entrance is near the middle of the wall, aligned with the central approach. | Exact door/window count and door operation are not confidently distinguishable at this resolution; do not convert the full apparent opening group to a measured count. Need close frontal view. |
| Head/parapet | One nearly level flat/parapet edge with a narrow pale coping strip. | Flat-roof silhouette; brick wall rises to simple coping, with slight overhang/cap visible against the sky. | P1 shows only the skyline, not rooftop area, roof membrane, slope/drainage, mechanicals or hidden steps. |
| Corners and adjacent context | Both facade edges partly visible; a white/dark adjacent volume at image-left and a ribbed light-colored adjoining surface at right. | The wall is a compact rectangular brick plane attached to taller/different neighboring campus fabric. | Image does not settle property/wall ownership or reveal either end elevation. |

### Defining facade details and material comparison

The dominant visual signature is the six-by-six hierarchy: six small upper window groups above six tall, mostly brick-filled recessed bays, each with a narrow low inset, then a smaller ground-floor opening band. The bays create the strongest facade shadows and should be researched as actual depth, not represented as flat color stripes. P1 supports red/orange brick with pale mortar, pale stone/precast-looking panel edges and coping, dark window frames, and dark blue-gray reflective glass. These remain photographic identifications; there is no finish schedule, mortar specification, calibrated color image or confirmed stone-versus-precast source.

P1 is bright daylight and one exposure. It cannot separate intrinsic brick color from sun/shadow and cannot validate current material aging. The prior model audit's material names are interpretive shader choices, not evidence. A shaded/current side-by-side image and a facade/finish specification would be needed to confirm material families and color differences across the 1935 and 1980 work.

## Massing, height and roof evidence

The existing research record describes a small, low, flat-roofed rectangular north-end remnant joined between two larger buildings; P1 supports a horizontal parapet and compact front plane but does not show the roof top. The official historic chronology establishes that a 1980 addition occurred but does not locate it on the current polygon. The prior asset used an estimated 11.7 m roof and 3.6–3.7 m floor spacing; the 3-level GIS attribute and P1 do not independently measure those heights. The inherited GIS field `Extrution=21` has unknown units/meaning and was correctly excluded as a height constraint in the prior audit.

No Peirce-specific point cloud or raster elevation clip was inspected or retained in this second pass. Indiana 3DEP statewide and county products may provide regional vertical context, but an exact tile, collection date, horizontal/vertical CRS, units and point class selection must be established before use. Do not use an unverified statewide product description as the building's metadata and do not equate top returns with eave height.

## Evidence-led construction brief

- Preserve FID 216's single compact footprint and current boundary; distinguish it from the demolished 1905 Physics structure, the Class of 1950 Lecture Hall to the south, and Psychological Sciences to the north.
- On the pictured principal wall, maintain six upper sash groups and six deeper middle recess panels with lower inset slots. Keep the ordinary ground openings/entrance tier separate; exact ground count remains unresolved.
- Preserve the simple parapet edge and compact flat-roof mass as provisional silhouette cues only. Roof equipment, membrane, drainage, slopes and height need new evidence.
- Do not copy P1's six upper groups or six recessed panels onto any side or rear wall. No opposing facade schedule is available.
- Treat the apparent 1935 core / 1980 small addition as a phase question, not a visual inference. Do not add former 1905 building fabric or an above-grade connector based solely on history/aerial context.
- Use the old model as an audit checklist only. It reproduces GIS position well but its side/rear counts and height are generalized/estimated, and its exterior assessment cannot substitute for new real-world viewpoints.

## Concrete gaps and evidence sought

| Gap | Existing attempt and why it is insufficient | Evidence that would resolve it | Modeling consequence |
|---|---|---|---|
| Compass registration of P1 | The official photo is frontal but has no GPS/EXIF camera bearing; its mapping to north/front is inherited from earlier work. | Geotagged Street View/Mapillary/campus photography station registered to FID 216. | The six-by-six schedule could be assigned to the wrong side. |
| South, east, west and rear/courtyard faces | One identified facade photograph and an unretained satellite inspection do not show those walls. | Current distinct ground/street views around both ends and rear, with close/medium/distant and low/elevated positions where available. | Major openings, entries, blank/service walls and corner transitions would be fabricated if mirrored. |
| Lower entrance/window run | P1 is only 478 px wide; plants and bikes occlude the base. Existing model's secondary door is recorded as an inference. | Close level frontal/oblique entry photographs and accessible current plans. | Door count, approach steps/ramp, lintels, reveals and ground openings remain uncertain. |
| Recess section and panel construction | P1 indicates depth through shadow but has no scale or oblique close view. | A near oblique bay detail, facade section or original construction detail. | The signature deep-reveal shadow pattern may be under- or over-modeled. |
| 1935 / 1980 facade phases and joints | Archives history identifies phases, but the page contains no documented exterior boundary; image color alone cannot date brick. | Archive photographs and as-built/project drawings for 1980 addition, plus registered current corner views. | Phase seam and roof/level offsets remain speculative. |
| Roof plan, services, heights and datum | P1 only shows parapet; GIS level/Extrution attributes have undocumented semantics; no LiDAR clip was inspected. | As-built roof plan/elevations/sections or inspected local 3DEP/IndianaMap point/raster tile with full metadata and class-specific surface analysis. | Roof edge, height, rooftop units, drainage and connections remain unknown. |
| Brick, trim and glazing specification | Only one date-uncertain bright daylight photo; model material names are not source specifications. | Current shade/sun comparison and architectural finish schedules or close calibrated photo. | True material boundaries, stone/precast identity, frame and mortar color cannot be claimed measured. |
| Archive raw image retrieval | Purdue Archives page returned a Cloudflare challenge to direct download; its indexed history text is readable through search/web access but not preserved as a clean local page snapshot. | Browser-accessible archive finding aid or direct catalog export / image request. | Historical photos may expose opposite faces and phases but remain unused until inspected. |

## Sources and retained files

Newly downloaded source files are in `sources/`; `source_register.json` includes original URLs, capture/publication-date distinctions, resolutions, SHA-256 values and limitations. The local event image is the original JPEG linked by Purdue Events (124,587 bytes); its small dimensions limit profile measurements. The prior first-pass asset audit remains at `audit/peirce_hall/RESEARCH.md` and is not overwritten. This second-pass research did not edit any builder, blend, placement, manifest or master-scene file.
