# Robert E. Heine Pharmacy Building — second-pass exterior research

**Queue rank:** 37 · **stable ID:** `heine_pharmacy` · **asset owner:** Rossen
**Identity:** Robert E. Heine Pharmacy Building (RHPH), Purdue GIS FID 606
**Review date:** 2026-10-30 · **Status:** focused pass saved; major side/rear, roof and vertical-datum gaps retained. Provisional, not build-ready.

This pass inspected the original 2023 Wikimedia Commons photo at full resolution and a Purdue Events exterior photo, which provides a more distant, nearly frontal view of the same monumental entrance facade. The pair confirms a long red-brick wall with seven slender vertical glazed stacks, pale stone spandrels/courses, and a deep ground-level stone arcade with round arches. The Purdue emergency plan provides a current level/use inventory: Floors 1–5 above grade, lower Floor G and a basement. The photos do not constitute a full building walkaround, and no measured elevations or roof plan were found.

## Identity, phase and footprint

The named Purdue GIS feature FID 606 identifies the Robert E. Heine Pharmacy Building, abbreviation RHPH. Its 22-vertex simplified source ring is preserved in the prior audit; the simplification tolerance was 0.25 m in the project-local mapping, not a survey tolerance. The original map service has no published survey accuracy or source date. Project campus placement origin is approximately (-193.842, 259.605) m relative to the project origin and local bounds are about 72.34 × 67.98 m; those values are source-transform computations, not surveyed dimensions. Overhangs and facade wall lines are not independently mapped.

Purdue Archives evidence cited in the prior audit places the pharmacy facility's completion/move-in in 1970 and the Robert E. Heine name dedication in 1985. These dates identify the facility but do not establish facade alteration chronology. The current Purdue emergency plan (2026-03-13) describes five above-ground floors, lower Floor G and a basement, with pharmacy, labs, offices and classrooms. GIS level-coded attributes enumerate eight values and include a roof value around 61 (units/datum undocumented); that conflicts with the published six-story description when interpreted as physical stories. Use the emergency plan's explicit above-ground floor inventory provisionally and retain the GIS field conflict.

## Viewpoint and source register

| ID | Source and view | Evidence / limitations |
|---|---|---|
| **H1** | Nothda, [Wikimedia Commons photo](https://commons.wikimedia.org/wiki/File:Purdue_University_Robert_E_Heine_Pharmacy_Building.jpg), original retained as `audit/heine_pharmacy/heine_exterior_2023.jpg`. Capture: 2023-10-18 10:25, 4,000 × 3,000 px, Samsung Galaxy Z Flip5, 24 mm-equivalent lens; author Nothda; CC BY-SA 4.0. | Low upward oblique at close/medium distance of the signed entry elevation. Resolves brick bond, seven narrow window stacks, pale stone inserts, arcade arches, rooftop parapet/plant and entrance. Tree branches mask the left edge, the lower facade is partly hidden, and wide-angle perspective distorts bay spacing. No GPS/compass azimuth. |
| **H2** | Purdue Events exterior image, downloaded as `sources/purdue_events_heine.jpg`; [place page](https://events.purdue.edu/robert_e_heine_pharmacy_building). Page/photo activity posted 2022-10-15; capture date/photographer not stated. | More distant, nearly frontal image of the same tall arcade frontage, including the full upper wall, central arch arcade, surrounding lawn and side return. Helps corroborate the seven-stack rhythm and parapet. Trees obscure some ground-floor bays; source has no camera pose or scale. |
| **H3** | Purdue Office of Emergency Preparedness, [RHPH emergency plan](https://www.purdue.edu/operations/emergency-preparedness/rhph/), revision 2026-03-13; retained HTML at `audit/heine_pharmacy/purdue_oep_rhph.html`. | Current story/use inventory; no facade elevations. Floor G/basement are not shown in H1/H2 and their exposed grade relationships remain unknown. |
| **H4** | Official Purdue GIS FID 606 saved in `audit/heine_pharmacy/heine_pharmacy_gis_feature.json`; layer date unavailable. | Identity and footprint only; no surveyed accuracy, wall/overhang separation or documented vertical datum. |
| **H5** | Purdue pharmacy level-one plan (`https://legacy.pharmacy.purdue.edu/sites/default/files/inline-images/RHPH_level1.png`) and school/archive records cited in `audit/batch_b_buildings/heine_pharmacy_evidence.json`. | Plan is a ground-floor program lead, not exterior elevation evidence; its current registration/scale against GIS has not been established. |

H1 and H2 are distinct photographic framings and distances but appear to show the same facade. No current photograph of the opposing long wall, end walls or rear/court elevation was located in the retained source pack. H1 crops are not counted as additional viewpoints. Google Street View was noted but not directly inspected in the prior packet. No building-specific LiDAR clip or aerial roof plan is retained here.

## Entrance facade schedule (H1/H2; source-relative)

Read H2 from left to right across the near-frontal wall; H1 supplies detail for the center and stonework. Compass face remains unregistered. The previous audit identifies this as the southeast/entry elevation, but the camera itself has no geolocation to verify that cardinal assignment.

| Zone | Observed sequence | Detail / confidence |
|---|---|---|
| Upper brick facade | **7** narrow vertical glazing stacks across the principal wall. Each stack presents dark vertical glass above and below a pale rectangular stone-like panel/spandrel; narrow pale jamb strips and light horizontal courses connect the rhythm. | Seven are consistently visible in H1/H2. The photo supports five above-grade window rows described in prior audit/BEP, but individual floor boundaries and exact mullion count per opening are not dimensioned. |
| Brick fields | Broad red/orange running-bond panels between stacks; horizontal pale belt courses pass behind/around the windows. | Strong visual repetition, but mortar type, brick blend and band material are unverified. |
| Ground arcade | A continuous pale stone-like frame supports a sequence of round-headed arches at the base. H1 clearly resolves **at least five arch openings** across the visible run; H2 reveals the arcade continuing across the frontage. | Count of the complete run is not secure because trees and image edge mask its ends. The arch frames project forward from brick; their inner reveals and thickness create deep shadows. No dimensioned section. |
| Public entry | Dark glazed doors set behind the arcade, near the center; flanking brick/spandrel zones continue above. | Door leaf count, exact portal bay, pharmacy retail windows/sign, threshold and accessibility layout are not resolved by the exterior view. |
| Roof edge | Pale vertical-panel parapet/coping line; a compact raised mechanical enclosure is visible above it in H1/H2. | Supports low flat/parapet silhouette with at least one localized rooftop screen. No roof plan, equipment schedule or height datum. |
| Returns | H2 shows part of a side return at far right; H1 shows the wall extending out of frame at left. | No complete end elevation, return length or opening schedule. Do not copy seven stacks to other sides. |

The principal architectural identifier is the combination of tall narrow vertical window bands with intermittent pale stone-like spandrels over a deep round-arch entry arcade. Model research should preserve separate front-to-back depth: outer arcade legs/arches, brick wall behind, window strips and inset glass, and projecting horizontal bands. H1's low viewpoint makes the upper wall feel taller; use H2 to check whole-wall proportions, not to infer exact dimensions.

## Material/color, roof and dimensional constraints

Both images show red/orange brick with dark charcoal or bronze-looking frames, pale warm gray/buff stone-like trim and darker reflective glass. H1's direct daylight and H2's brighter frontal exposure differ; color remains photographic, uncalibrated. The arch frame looks pale stone or cast stone, but neither source provides a specification. The upper parapet has vertical panel divisions, possibly metal or stone; identity unresolved. Do not use prior model shader names as material evidence.

The visible entry wall is tall, with five above-grade levels suggested by the repeated vertical glazing stacks and confirmed as program levels by the emergency plan. The lower G level and basement may be partly below grade or exposed on another face; neither photo resolves that. Purdue GIS's roof/level numeric fields have undocumented units and vertical datum; they cannot establish a 61 m building height. Prior modeling used an approximately 22 m wall estimate and a compact mechanical penthouse, both provisional. No surveyed eave, story, parapet or roof-service elevations were found.

The available image set has no orthographic roof view. H1/H2 expose only parapet top and localized equipment; hidden roof membrane, drain slopes, terrace/lightwell topology and equipment positions remain unknown. No exact tile-level LiDAR/raster metadata or returns were inspected in this pass. Regional Indiana 3DEP availability is not building-specific evidence until tile/date/CRS/vertical datum and class filtering are documented.

## Builder-facing brief and inherited-asset checks

- Keep FID 606 and the 22-vertex source ring as the plan source with its 0.25 m simplification and non-survey caveat. Verify wall versus roof edge before using it as a shell boundary.
- Use five above-grade rows provisionally, with lower Floor G/basement kept distinct from the street facade until a grade walkaround resolves exposure.
- Reproduce the principal wall as seven slim vertical glazing stacks with pale spandrels/bands over the projected round-arch arcade. Keep the arch frame and background brick wall separate in depth.
- Keep entrance signage, doors, retail pharmacy interior cues and accessible approach unresolved where not visible; the ground-floor plan may guide interior program but does not identify the exterior entry by itself.
- Do not repeat H1/H2 counts on hidden faces, set total height from GIS `R=61`, or treat the old approximately 22 m height/roof penthouse as verified.
- Discrepancy checklist against prior asset: seven stacks and arcade now have two real photo framings; other facades remain generalized; roof shape/equipment and absolute heights remain estimates; GIS and published level data still conflict.

## Gap register

| Gap | Evidence tried and limit | Needed evidence | Consequence |
|---|---|---|---|
| Opposite and end elevations | H1/H2 show the same entry wall; only a partial right return. | Current four-face street-level sequence, corner-to-corner shots and court/service-side views. | Other openings, blank bays, doors, loading, and corner details remain unknown. |
| Facade orientation and camera registration | H1 EXIF has camera/date/lens but no GPS; H2 has no pose. | Geotagged camera position/bearing matched to the FID 606 ring. | The strong schedule could be assigned to the wrong cardinal face. |
| Exact opening count/profile per level | Seven stacks are clear; individual mullions/floor breaks are not fully resolved. | Frontal high-resolution elevations or as-built facade drawings and close bay details. | Window dimensions, spandrel profile, frame depth and floor datum remain approximate. |
| Arcade geometry and entry configuration | Arch rhythm visible but complete count, section and door layout are partly occluded. | Front/oblique close entry photos, accessible-entry drawings and stone/arcade sections. | Arch count, voussoir/soffit depth, portal relation and approach cannot be measured. |
| Roof plan/equipment and vertical datums | Parapet and one compact raised volume visible only; GIS R/Extrution are undocumented. | As-built roof/elevation plans and current high-angle images; datum-tied survey if available. | Roof silhouette and height remain estimates. |
| Floor-count semantic conflict | OEP lists Floors 1–5, G and basement; GIS has eight coded levels and R=61 without units. | GIS field dictionary plus current sections/plan set and surveyed vertical datum. | Above/below-grade levels and overall height may be misrepresented. |
| Phase/material/current condition | History fixes 1970 completion and 1985 naming, but not facade alteration phases; images are 2022–23. | Renovation/as-built history, current close material photos, finish schedule and archive imagery. | Original/current differences and material identities unresolved. |
| LiDAR availability | No RHPH-specific point/raster clip retained in existing audit. | Identify tile and acquisition date, preserve metadata/CRS/units/classes, isolate roof and ground returns. | No independent vertical constraint. |

## Provenance and retained files

`source_register.json` records URLs, dates, provider, limitations and SHA-256 hashes for the two inspected local image/page sources and points to the existing GIS/emergency-plan records. The original 2023 CC BY-SA 4.0 image and metadata remain preserved at `audit/heine_pharmacy/heine_exterior_2023.jpg` and its Commons page. The new Purdue Events image and HTML are in `sources/`. This research-only pass did not edit any model, builder, placement, manifest or master file.
