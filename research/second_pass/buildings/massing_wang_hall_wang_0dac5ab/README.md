# Seng-Liang Wang Hall — second-pass exterior research

**Queue rank:** 35 · **stable asset ID:** `massing_wang_hall_wang_0dac5ab` · **asset owner:** Tobin
**Identity:** Seng-Liang Wang Hall (WANG), Purdue GIS FID 895, 516 Northwestern Avenue
**Review date:** 2026-10-30 · **Status:** focused exterior pass saved; significant footprint, face-schedule, roof-datum and material gaps retained. Provisional, not build-ready.

This pass inspected the saved architect project images, the Esri aerial, nine plan/rendering sheets, and the existing independent GIS/OSM comparison. Wang is a four-story long mixed-use academic/research building with a brick-and-glass envelope, pale horizontal bands and a prominent vertically glazed atrium volume. One elevated oblique provides useful multi-level facade and roof-edge evidence; the aerial gives a separate overhead view of roof segmentation and rooftop plant. The evidence still does not establish every side or the exact structure/roof outline: GIS and OSM disagree by several metres, and the architect sheets mix proposed renderings with plan diagrams.

## Identity, location and phase

Purdue ECE's dedication article (2014-09-19) identifies Seng-Liang Wang Hall at 516 Northwestern Avenue and describes a four-story, 147,000-square-foot facility. Purdue's LEED Gold announcement also identifies the building and area. OSM way 301932787 tags four levels and 14.8 m height; it is community-mapped and the height is not a survey. The subject is the current WANG building, distinct from neighboring Physics, Forney and Armstrong halls.

The prior audit's OSM outline has 17 unique vertices and projected area about **3,370 m²**. Purdue GIS FID 895 computes to about **3,032 m²**, with outline IoU about 0.812, centroid separation 5.32 m and Hausdorff distance 5.54 m. Existing work selected OSM because it matched the retained aerial roof edge better and aligned more plausibly with the published gross area. That is a reasoned source choice, not a survey finding. Keep both rings and their conflict visible; clarify whether the intended model boundary is roof perimeter or facade wall line before claiming exact geometry.

The CSO site plan and context renderings locate the building in the existing campus block. A north arrow is present on the plans. Because outlines conflict, register photo views against the current ground footprint before assigning facade sides or phase boundaries. Street, sidewalks, plaza, parking, landscaping and bicycle racks are site context, not shell geometry. No confirmed shared enclosed connector or structural wall boundary was resolved in this pass.

## Source/view register

Local originals remain in `audit/wang_hall/sources/`; provenance and hashes are listed in `audit/wang_hall/evidence.json`. The CSO image set lacks consistent camera and capture metadata. Some images are explicitly design renderings; others appear to show the completed building. Keep the two evidence classes separate.

| ID | Source and actual inspected view | Observations and limitations |
|---|---|---|
| **W1** | CSO project image `cso_wang_photo_08.jpg`; [architect project page](https://www.csoinc.net/projects/seng-liang-wang-hall). Retrieved 2026-10-26; capture date/photographer unknown. Elevated oblique down the street. | Shows a long facade, one corner/return, ground entrances, upper window rows, roof edge, raised atrium volume and a tall gray metal service enclosure. A white dish/radome-like object appears above the enclosure; identity unknown. Perspective compresses the far bays; no GPS, bearing or scale. |
| **W2** | Esri World Imagery crop `wang_hall_esri_aerial_2026-10-26.jpg` and outline overlay `footprint_overlay_on_aerial.png`; acquisition date not retained. Near-overhead. | Reveals long light roof, a longitudinal raised/mechanical strip, localized boxes, a raised volume, one roof interruption/notch and neighboring streets/parking. Trees/shadows and bright roof hide edges; not a surveyed roof or wall plan. |
| **W3** | `wang-hall-finished.jpg`, CSO project image; ground-level oblique. Image status/capture date unclear. | Shows a prominent tall curved/elliptical glazed volume between brick wings, glass divisions and lower canopy/entry zone. Treat as architectural intent until confirmed against as-built photos. |
| **W4** | `Wang_plans16.jpg` labeled “View from Northwest,” plus context views `Wang_plans12.jpg` and `14.jpg`. Design renderings. | NW oblique and north/south streetscape intent; supports massing and facade family, not exact current-condition details or independent as-built viewpoints. |
| **W5** | Site plan `Wang_plans2.jpg`, site/landscape plan `3.jpg`, floor diagrams `4/6/7/8.jpg`. | North arrow and level-specific arrangement; plans show a central atrium/circulation core. These are not verified dimensioned as-builts and include no exterior elevations or sections. |
| **W6** | CSO photos `cso_wang_photo_02.jpg`–`07.jpg`, inspected as a set. | Interior study, office, lab, corridor and teaching-room views; not exterior viewpoints. No facade counts are taken from them. |

Only W1 provides strong completed-looking elevated facade evidence; W2 is a separate overhead view. No clean current frontal, rear/court, opposite-end or roof-detail walkaround was found. Repeated renderings are not counted as additional real camera stations. The exact type/date of W3 and several CSO project images remains unresolved.

## Source-relative facade schedule

For W1, start at the near/right corner and read left along the long frontage toward the far end. Because W1 is elevated and oblique, it supports partial sequences but not reliable full-elevation totals.

| Zone | Observed pattern | Construction reading | Confidence and gap |
|---|---|---|---|
| Long upper frontage | Repeated rectangular dark-glazed groups in two upper tiers, separated by brick piers; atrium interrupts the run. | Multi-light window groups set within pale trim/reveals; horizontal pale floor bands align with story divisions. | Overall rhythm is visible; exact per-floor bay counts, widths, mullions and corner offsets need frontal current photographs/elevations. |
| Base/frontage | Repeated ground-level glazed units/door-sized bays and pale horizontal canopies or ledges. | Ground floor alternates light base panels and glass beneath brick upper stories. Do not assume every glazed unit is an entry. | Door versus window count and accessible entry/threshold levels are unresolved. |
| Near corner/return | W1 exposes one end turn with vertically organized glazing and continued bands. | The facade wraps a real corner; the return is not just a flat end cap. | No square-on end view or complete return count. Opposite end remains unknown. |
| Atrium volume | Tall projecting curved/crowned pavilion with a broad glazed face; more explicit in W3. | Distinct multi-story atrium mass, with glass and a raised crown affecting silhouette and depth. | W1 is oblique and W3's as-built status is uncertain; radius, crown profile, mullion schedule and exact height need elevation/section. |
| Roof/service block | Predominantly low flat roof with localized raised strips/plant and a tall gray metal-clad enclosure; dish/radome-like object above. | Segmented roof, localized screens and tall service volume; avoid one uniform roof plate. | Equipment identity, screen height, drainage, roof datum and current plant layout unverified. |
| Opposite long wall and end | No current ground-level image inspected. | Unknown. | Do not mirror W1; openings, loading/service areas and wall joints require evidence. |

## Materials, color and signature detail

W1 shows warm tan/light-brown brick, pale gray/white floor bands and base trim, dark blue/green reflective glazing, and silver-gray metal panels/screens. W2's high-reflectance roof is bright in overhead illumination; that is not a calibrated material color. W3/W4 suggest intended red/brown brick and pale trim but should not override built-looking W1. No facade specification or calibrated color reference was found. Brick blend, mortar, panel composition (precast, limestone or metal), frame finish, glazing type and weathering remain photographic identifications, not measured material properties.

The signature forms with depth are the projecting multi-story atrium/crown, broad bands wrapping corners, deep window surrounds, lower entry/canopy zones and tall rooftop service enclosure. The rooftop white object is described only by its visible shape. Plants, cars, people, paths and street fixtures remain site context. Resolve depth/profile from close oblique photos and architect as-built sections rather than rendering appearance alone.

## Roof, levels and dimensional constraints

Official ECE material provides four floors and 147,000 ft² gross area. The OSM 14.8 m tag is unsurveyed; the prior saved asset reached 14.81 m including equipment, within that tag only to rounding precision. Neither provides datum-tied floor heights, eave/parapet levels or equipment tops. The Esri aerial shows a long light roof with localized service bands and boxes; acquisition date and image scale are unavailable. A roof plan, wall/roof section and current high-angle imagery are needed to distinguish skylight/atrium, roofwell, parapet, mechanical enclosures and drainage.

Indiana 3DEP QL2 regional products are available, but no Wang-specific point/raster clip was inspected in this pass. Exact tile, acquisition date, horizontal/vertical CRS, units and class distribution must be established from the chosen file metadata. Roof returns mixed with vegetation and equipment cannot be called eave measurements. No measured elevation drawing was found in the retained packet.

## Builder-facing research brief and inherited-asset discrepancies

- Preserve the elongated plan but reconcile FID 895 with OSM way 301932787 before setting a shell boundary; the current 5.3 m center/5.5 m edge differences are material.
- Use four stories as official program context; preserve the long brick wing, pale horizontal bands, dark window runs, distinct ground-level glazed/entry tier and projecting tall atrium.
- Treat the roof as segmented with localized plant/screens and one tall metal-clad service volume. Do not invent equipment identity or duplicate units from one oblique.
- Keep unphotographed facade schedules unknown. Do not mirror window patterns or treat W3/W4 rendering details as surveyed.
- Audit the existing asset against source constraints: OSM is selected for plan; height derives from unsurveyed OSM; opening totals/materials are generalized; atrium crown, end elevations, roof services and wall/roof boundary still need evidence. The existing model/audit is not truth about the real facade.

## Unresolved evidence and next actions

| Gap | What was tried and why it falls short | Evidence needed | Consequence |
|---|---|---|---|
| GIS vs OSM outline | Two retained rings and one dated-unknown aerial checked; roof and facade-wall lines may differ. | Surveyed campus/site plan or georeferenced as-built wall/roof line. | Several metres of possible plan shift/scale error. |
| Complete long facade schedule | W1 is elevated and oblique; W3/W4 include uncertain render status. | Current frontal photos with multiple stations along the wall and floor-by-floor annotation. | Bay count and proportions remain unverified. |
| Opposite facade/courtyard/service wall and opposite end | No current image from those positions in the reviewed packet. | Street View/Mapillary or Purdue/architect photo archive walkaround, plus as-built elevations for inner faces. | Would otherwise require fabricated/mirrored openings. |
| Atrium/crown geometry | W1 oblique; W3/W4 may be design images; no section. | As-built elevations/sections and close frontal/side images. | Defining curved crown, mullion rhythm and glass depth remain estimated. |
| Roof plant, screen and dish-like object | Shapes visible in W1/W2 but no equipment schedule; date unknown. | Current roof plan, equipment key and higher-resolution roof photography. | Roof silhouette and object identity remain uncertain. |
| Story/eave/roof datums | Four-story description and 14.8 m OSM tag only. | Datum-controlled elevations or full LiDAR/photogrammetry metadata and isolated roof/ground returns. | Absolute height and floor stack remain estimates. |
| Material identities | One daylight oblique plus design images; no specifications. | CSO/Purdue finish schedule and current close details in sun and shade. | Brick, trim, panel and glass colors remain visual classes. |
| Image phase/capture date | CSO page image set lacks consistent captions/EXIF; several plan sheets are explicit renderings. | Source-captioned completed-condition photographs, original EXIF, or image schedule from architect. | Rendering-only features cannot be silently treated as existing. |

## Provenance

Detailed source URLs, source dates, CRS, methods, limitations and SHA-256 values are preserved in `audit/wang_hall/evidence.json`; source files are under `audit/wang_hall/sources/`. The second-pass dossier and queue record are research-only: no model, builder, placement, manifest or master scene was edited.
