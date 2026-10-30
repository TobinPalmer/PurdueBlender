# Agricultural Administration Building — second-pass exterior research

**Queue rank:** 38 · **stable ID:** `agricultural_administration_building` · **asset owner:** Rossen
**Identity:** Agricultural Administration Building (AGAD), Purdue GIS FID 267, 615 Mitch Daniels Boulevard
**Review date:** 2026-10-30 · **Status:** focused pass saved; all-face, current-roof, phase and measured-height gaps retained. Provisional, not build-ready.

This pass directly inspected the current Purdue photograph (Rebecca McElhoe, 2023) and the paired archival facade image credited to Purdue Archives. The current image establishes the accessible entrance composition, tall narrow glazed portal, pale masonry base and horizontal bands, dark red/brown brick, and varied vertical window groupings on the entrance wall. The historic photo shows an earlier two-story-plus-basement building with a pitched tile roof and different upper cornice/window treatment. Purdue Archives records later renovations; the old roof and facade arrangement must not be projected onto the current building without phase-specific evidence.

## Identity, phases and boundary

Purdue GIS FID 267 identifies Agricultural Administration Building, abbreviation AGAD, address 615 Mitch Daniels Blvd. Its one-ring footprint is preserved in `audit/agricultural_administration_building/sources/agricultural_administration_gis_feature_267_current.json`. The official map ring is not a certified survey; positional accuracy and relationship between outline, wall face and roof overhang are undocumented. The project used the repository's approximate geographic meter transform, not a survey CRS. GIS attributes include `Level_=4`, `NUM_LEVELS=5`, `CountOfFLO=5`, `Extrution=34`, `F01=8.2`, `F02=24.7`, `F03=40.95`, and zero F04/F05 values. The data service supplies no units, vertical datum or field semantics; preserve them as raw fields, not measured elevations.

Purdue Archives states the building opened in 1908 as the Agricultural Experiment Station, with two stories plus a basement, brick/stone trim and a tile roof. The Archives record also notes later renovations. Purdue's March 2023 article explicitly contrasts an archival facade photograph with a contemporary entrance photograph, showing that accessibility upgrades have changed the approach/entry. The present wall height, floor count and roof silhouette are not determined by the opening-era description. Treat historic and current sources as separate conditions until intermediate renovation records explain the transitions.

## Viewpoint and source register

| ID | Source/view | Inspected evidence | Date and limitations |
|---|---|---|---|
| **A1** | Purdue University photo by Rebecca McElhoe, [2023 entrance photograph](https://stories.purdue.edu/app/uploads/2023/03/AGAD-entrance-2023.jpg), retained as `audit/agricultural_administration_building/sources/agad_entrance_2023.jpg`; article [Purdue’s path toward a thriving Disability Resource Center](https://stories.purdue.edu/early-advocacy-paved-way-for-purdues-thriving-disability-resource-center/). | Near-frontal entrance crop at pedestrian height: central stacked-glass portal, brick fields, upper windows, pale foundation/stringcourses, inset ground-level openings and accessible paved approach/low retaining walls. | Article dated 2023-03-09. Camera GPS/height/bearing unavailable; image crop omits complete wings, roof and corners. Tree branches shade the upper right and a seated visitor/landscape masks part of approach detail. |
| **A2** | Archival photograph credited to Purdue Archives and Special Collections, displayed alongside A1 in the same Purdue story; retained as `agad_archival_facade_2023.jpg`. Original photograph date unknown. | Historical oblique corner showing the earlier brick mass, upper window groups, deep cornice with repeated bracket-like detail, pitched tile roof and arched/stone lower openings. | It depicts a historical state, not the present roof/facade. Perspective, tree occlusion and low-resolution reproduction prevent dimension or complete window counts. |
| **A3** | Purdue Archives corporate history, [Agricultural Administration Building](https://archives.lib.purdue.edu/agents/corporate_entities/569), raw structured JSON snapshot retained in prior audit. | Text source for 1908 opening, initial two stories plus basement, brick/stone trim, original tile roof and later renovation history. | Does not provide as-built drawings or date/describe each later facade/roof change. |
| **A4** | Purdue GIS FID 267 and FeatureServer layer metadata, retained in prior audit. | Exact map identity and footprint ring. | GIS attribute units/vertical datum and feature survey accuracy unavailable. |

The two photographs supply two genuinely different periods and camera angles, but only A1 is current-condition facade evidence. They do not complete an exterior walkaround. No current rear/east/west/south full elevation, corner sequence, roof plan or georegistered aerial was inspected in this pass. Crops of A1/A2 are not separate viewpoints.

## Current entrance wall schedule (A1, source-relative)

The source is a close crop rather than a full elevation. Describe the visible wall sequence without treating partial windows as whole-building counts.

| Zone, image-left to right | Visible arrangement | Architectural/material observation | Limit |
|---|---|---|---|
| Upper brick fields | Dark red/brown running-bond brick; tall window groups occur on either side of the central portal and toward both image edges. | Several window groups are vertically organized, with dark metal-looking frames, reflective blue-gray glass, pale stone-like sill/head pieces and occasional horizontal pale course bands. | A1 crops the sides/top and tree branches obscure portions. No full facade count or per-floor opening schedule is defensible. |
| Central upper portal stack | Tall, narrow glazed composition centered over the main doorway, with visible horizontal divisions and an upper stone lintel/marker. | The portal extends above the ground entry as a vertical glass stack within pale stone jambs; one central stone block projects at its head. The glass has poster/graphic panels in the photo, which are changeable display content. | Exact number of transoms, glass bays, portal height and depth are not dimensioned. Posters are temporary, not permanent architecture. |
| Ground masonry band | Broad pale gray/buff stone-like base and continuous projecting belt spanning the visible wall. | The band runs behind/along the portal and frames recessed ground-floor panels. Weathering and mottled color are visible but lighting and processing are uncalibrated. | Material could be limestone, cast stone or concrete; no specification found. Exact section and projection unknown. |
| Flanking ground openings | To both sides of portal are wide dark/recessed panels and narrow vertical windows. Two smaller arched-head dark openings are visible on the image-right; another arched/round form appears image-left. | Recessed infill/panels sit within pale masonry frames. Small round-headed openings create a distinct lower-level rhythm. | These appear to be lower openings, but whether they correspond to basement, Floor G or an at-grade lower level is unresolved. A1 does not show the whole base. |
| Accessible approach | Straight paved walk aligns with the portal; low brick/stone planters and bench/rail elements frame the near approach. | Contemporary approach is integrated with a level entrance route; do not mistake retaining walls, bench, handrail, people or plantings for the building facade. | Exact slope, ramp/landing lengths and handrail location are outside the photo's scale/crop. Need current site plan and side view. |
| Cornice/roof | Current upper wall reaches out of frame; A1 does not show the roof. | No current roof shape can be inferred. | Historical A2 tile roof/cornice is not current-condition proof. |

### Historical comparison (A2)

A2 shows the earlier building as an angled two-story-plus-basement masonry block: pale stone course/base, brick upper wall, grouped rectangular sash openings, a substantial projecting cornice with repeated dentil/bracket-like elements, and a large pitched tile roof. The image also suggests arched lower openings and a raised stone/brick entry composition. It is low-resolution, shaded and partly hidden by a tree. The 1908 archival description corroborates brick/stone and tile roof, but neither text nor photo proves that these exact features remain on any current face. Do not carry the historical roof, cornice or old opening count onto A1's modernized facade.

## Materials, massing, levels and evidence limits

A1 supports dark red/brown brick with visible horizontal courses; pale gray/buff masonry at the base, entry surround, sills and stringcourses; dark frames; blue-gray reflective glazing. A2 shows aged pale masonry and tile-like roof covering in the archival condition. Neither provides calibrated color/specification. The current parapet/eave type, roof membrane/pitch, service screens, rooftop machinery and current roof plant are unknown.

GIS `NUM_LEVELS=5` and `CountOfFLO=5` are only diagrammatic level evidence. Archives describes the original building as two stories plus basement; this does not establish current heights after renovation. GIS `F01`–`F05`, `Extrution` and roof/level fields are not interpretable as metric heights without the service data dictionary, units and vertical datum. The first-pass massing uses five equal 3.44 m facade bands to a 17.2 m envelope, explicitly as a diagram, not a measured section. No current exterior-wide photo establishes the number of visible floors around the whole building, and no measured elevation/section or point-cloud clip was retained.

## Builder-facing brief and inherited-asset checks

- Retain the official FID 267 ring and campus placement as a map-derived footprint, with survey accuracy and wall/roof edge distinction open.
- Use A1 for current facade evidence: brick-and-pale-masonry composition, narrow vertically grouped windows, prominent stacked-glass portal, pale projecting base/belts and accessible paved entrance approach.
- Treat A2 as a historical condition only: two stories plus basement, tile roof and deep decorative cornice are documented for the original building, not necessarily current.
- Keep currently unseen roof, all other sides and their openings unresolved. Do not use the GIS five-level/vertical fields as measured floor elevations or set the roof to the historical tile form.
- Against the previous asset, retain the source-supported front portal and masonry/window palette as partial evidence. Its even five-band vertical envelope, entry location and neutral flat cap are diagrammatic placeholders; no current photo verifies the opposite elevations, roof or total height.

## Specific unresolved evidence

| Gap | Evidence tried / limitation | What would resolve it | Accuracy impact |
|---|---|---|---|
| All-face contemporary walkaround | A1 is a cropped current entrance view; A2 is archival and no current aerial/Street View was calibrated. | Current geotagged photos of each face, corners, entrance and service areas at near/medium/far distances, plus a north-up roof view. | Major mass and facade layout beyond the entrance are unknown. |
| Current roof form and services | A1 omits roof; A2 tile roof is explicitly historical; GIS vertical fields are undocumented. | Recent elevated imagery, as-built roof plan/sections and facilities mechanical/equipment records. | Roof silhouette and mechanical screen placements cannot be supported. |
| Present floor count and grade | Original archive says two stories + basement; GIS level fields say five; no current elevation. | Current measured facade elevations/sections and grade survey tied to floor datums; resolve FID attribute semantics. | Equal modeled story bands and lower-floor exposure may be wrong. |
| Phase chronology | 1908 opening and “later renovations” identified; no detailed change record inspected. | Renovation permits, Archives photographs by date, and capital project as-builts. | Original vs altered wall, cornice and roof boundaries remain unknown. |
| Opening schedule and profiles | A1 cropped front photo and A2 low-resolution historic corner view. | Full-resolution square-on current images of each facade plus close window/stone/portal profile views. | Bay totals, frame divisions, recess depth and infill states remain uncertain. |
| Current material identities | Two uncalibrated photos from different eras and exposures. | Current shaded/sunlit detail photography and finish schedule (brick, mortar, stone/cast-stone, roof, glazing). | Exact material identity/color and weathering remain unverified. |
| Vertical survey data | No building clip; GIS level/Extrution units and datum absent. | Identify exact Indiana 3DEP/IndianaMap tile, capture date, horizontal/vertical CRS, units and class counts; isolate ground and roof returns. | No independent eave/ridge/ground heights. |
| Accessibility/site relationship | A1 shows a walk and low retaining walls only; no measured accessible route plan. | Current accessibility site plan or registered side views of walk, ramps, slopes and entrance threshold. | Approach geometry could be confused with facade and level changes. |

## Provenance

New Purdue story HTML is saved in `sources/purdue_story_2023.html`; original A1/A2 image files, GIS record, Archive history JSON, and build evidence remain in `audit/agricultural_administration_building/sources/`. `source_register.json` records source IDs, dates, local paths and SHA-256 values. The archived facade is credited to Purdue Archives; the current entrance image is credited to Purdue University by Rebecca McElhoe. No building geometry, builder, placement, manifest or master scene was edited in this research-only pass.
