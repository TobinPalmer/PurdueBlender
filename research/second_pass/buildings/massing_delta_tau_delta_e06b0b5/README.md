# Delta Tau Delta, Gamma Lambda — second-pass exterior research

**Queue rank:** 51 · **Stable asset ID:** `massing_delta_tau_delta_e06b0b5` · **Model owner:** Unassigned
**Review date:** 2026-10-30 · **Status:** Exterior brief prepared with all-face registration, exact addition seam, measured heights, and detailed current-condition gaps retained; provisional, not build-ready.
**Phase:** Research only. No builder, asset, placement, or master-scene edit was made.

## Identity, site, and building phases

The Gamma Lambda chapter's official chapter site uses “400 Northwestern” for its online chapter home. Tippecanoe County's April 15, 2021 Z-2826 staff report identifies the Purdue Delta Tau Delta Association property at **400 Northwestern Avenue** and describes its existing 1928 building as Tudor Revival in character. This cross-check, the chapter sign in the official chapter profile image, and the spatial match to Indiana building-footprint feature object ID 409940 establish the identity of the modeled house (I1, C1, V3, G1). The chapter location is commonly described as the triangle of Grant Street, Northwestern Avenue and Fowler Avenue, but the visual source camera positions are not recorded.

The chronology changes the visible outline over time:

* The Indiana Historical Society finding aid associates the 1928 project with architect Bishop, Knowlton & Carson of Indianapolis and Hall Construction Company. It lists related plans/photographs, but those archival records have not been inspected directly (I2).
* A 1961 *Rainbow* cover presents the chapter's Shelter before the later documented expansion. The near-frontal photograph shows a left gabled block, a smaller central entrance gable, a long lower wing, and a steep shared roof with dormers (V1).
* The Fall 1970 *Rainbow* says the Woodson C. Immel Shelter addition was dedicated May 3, 1970; it says the addition cost $330,000 and approximately doubled the building's size. Its page 26 photograph shows the post-addition exterior from an oblique position (H1, V2). The image documents the combined house after expansion, but neither text nor photo locates the precise construction joint or names the addition architect.
* The undated official Purdue_Delts X profile image shows a snowy, later exterior with red brick, several front-facing gables, rows of rectangular windows, a masonry arched entry and chimney stacks. Its date and camera position are unknown; it supports broad continuing form but does not establish which details remained unchanged after 1970 (V3).

The second-pass reference is therefore the post-1970 expanded chapter house represented in V2 and the official chapter profile image, with V1 retained as a pre-addition phase record. Do not interpret the earlier front elevation as the complete later envelope, or treat the chapter image as proof that every 1928/1961 detail survived unaltered.

Indiana's 2016–2020 LiDAR-derived building-footprint service returns an unnamed polygon, object ID 409940, with `LidarYear=2018`. The polygon has six unique corners (seven including closure), source area **1,203.75 m²**, and source perimeter **155.12 m**. The project's documented campus-local approximation gives a bounding envelope of about **24.77 × 43.34 m**. The match is geographic and address-context based, not a named-building record or legal wall survey; the automated outline may not include small projections or later edits (G1, G2; see also `../../../../audit/delta_tau_delta_e06b0b5/sources/indiana_lidar_building_footprint_oid409940_2026-10-30.json`). A fresh October 30 query returned the same polygon as the October 26 snapshot.

## View register and face coverage

Original publications, page renders, the profile image, data snapshots, and local hashes are in [source_register.json](source_register.json). The 1961 photograph is a color printed reproduction in a fraternity magazine, while the 1970 post-addition image is a monochrome printed photograph. Neither has a measured scale, EXIF position, or compass bearing. The `front` labels below are relative to the photographed presentation; the facade bearing is not independently surveyed.

| View | Position, bearing, date | Observations | Limits |
|---|---|---|---|
| V1 — pre-addition | *The Rainbow*, Fall 1961, cover photograph; near-frontal oblique with part of one flank visible. Camera location/bearing unknown. | Clear, near-full view of the pre-1970 front composition, brick pattern/color, arches, dormers, gables, window rows and landscape relationship. | Tree branches obscure roof/wall regions; printed reproduction has halftone and no scale. This is the earlier, smaller building, before the Immel addition. |
| V2 — post-addition | *The Rainbow*, Fall 1970, printed p.26 / PDF p.28; front/side oblique, capture date not stated but published with the May 3, 1970 dedication report. Camera location/bearing unknown. | Establishes the joined post-addition mass, multiple steep gables, a second long side plane with repeated windows, and at least two tall roof stacks/chimneys. | Distant monochrome image, tree obscures the center and junctions; exact bay count and addition seam remain unknown. |
| V3 — chapter profile | Purdue_Delts account profile image retrieved through public image proxy on 2026-10-26, 400×400; snowy partial oblique, capture date unknown. | Confirms the chapter identity sign at 400 Northwestern and broad red-brick / multi-gable / rectangular-window / arched-entry features in a later house image. | Small square crop, snow, branches and foreground wall obscure lower details; no verified date, camera position, face registration or scale. |
| V4 — current GIS outline | Indiana GIO 2018 LiDAR-derived footprint feature 409940, query snapshots 2026-10-26 and 2026-10-30. | Six-corner plan and approximate envelope; current query matches saved prior ring. | Unnamed automated LiDAR-derived polygon, not a survey; source says reference data; no facade or height evidence. |
| H1 — addition account | *The Rainbow*, Fall 1970, PDF p.28, text and caption adjacent to V2. | Places the addition at 400 Northwestern, identifies it as Woodson C. Immel Shelter addition, records May 3 dedication and says it approximately doubled the Shelter. | No dimensioned plan, elevations or construction-seam map. |

### Pre-addition front schedule (V1; left-to-right in the photograph)

This is an image-relative schedule of the visible 1961 front, not a current all-face schedule. It is the reproducible baseline for distinguishing the pre-addition facade from the later mass.

| Run | Visible arrangement in V1 | Confidence / detail |
|---|---|---|
| Left gabled block | Tall steep front gable with a small attic-level window; a broad upper band of three narrow rectangular openings; at ground level three contiguous round-headed openings in a recessed arcade. A low basement-level run is partly visible below the projecting sill/course. | High for the visible arrangement and three arches; medium for total floor relationship and lower openings because landscape and print resolution obscure the base. |
| Central entrance block | Smaller front-facing gable between the left block and long right wing; upper gable has a compact multi-light window beneath a pale triangular inset; main entrance is a single dark door set within a broad pale masonry round arch with a rectangular plaque/sign above. A narrow adjoining lower opening appears immediately to its left. | High for one arched entry and gable/door relation; plaque text and trim profiles not legible. The entry surround is not evidence of a Gothic pointed arch. |
| Right low wing | Long horizontal wall below a lower roof edge, with three windows at the upper visible band and three rectangular openings beneath. It joins the central block; tree/shrub masks some base and the exact corner. | Medium for the visible count/order; exact story levels, sash divisions, and extension length not measured. |
| Main roof behind the facade | Steep shingled roof with at least two low shed dormers visible in the front plane and one tall brick chimney stack. | High for those visible features, low for hidden valleys, ridge length and exact stack attachment. The later V2 view, not V1, shows a second prominent stack. |

The front is asymmetrical: the left arcade block, central arched entry, and longer lower wing are distinct compositions. The 1961 photograph shows bed planting, hedges, and walk surfaces, which are site/landscape elements and not part of the brick building envelope.

### Post-addition observations and unobserved faces

V2 confirms that the 1970 house is substantially larger than the V1 form. Its visible profile has several connected steeply gabled masses, dormer openings in the large sloped roof, and a long wall plane with repeated vertical windows. Two substantial chimney stacks rise above separate roof zones. The tree and distance hide the central transitions, so the image does not prove whether any pictured front gables belong to the original block or the addition. V3 shows at least three front-facing gable peaks in a snowy later view; snowfall and cropping prevent a reliable one-to-one mapping to V1/V2.

No current full view or plan establishes all four faces. The known photographic `front` cannot be assigned a reliable cardinal bearing; the opposing long wall, both ends, rear/service side, entrance accessibility path, and all-face window/door totals remain unregistered. There is no source basis for mirroring the V1 front pattern onto the rear or transferring its opening schedule to the 1970 addition. The 2018 GIS polygon does not identify which edge corresponds to any photographed facade.

## Materials, profiles, roof, and dimensional constraints

V1 color reproduction and V3 support a red-to-warm-red brick exterior. V1 shows some lighter masonry around the central entry arch and small pale details at the gable/window surrounds; trim extent, masonry type, bond and joint profile are not verified. V2 is grayscale and cannot add color evidence. Exposure, snow and the printed color process affect the apparent brick hue; no calibrated color is claimed. Frames appear dark in V2/V3 and varied in V1, but their exact material and muntin patterns cannot be distinguished consistently.

The defining depth features are the recessed three-arch arcade in the pre-addition left block, the separate central entry set into a broad masonry arch, projecting front gables, deep sloped roof edges, low dormers, and multiple tall chimney stacks. The post-addition combined mass adds further gabled roof volumes and window runs. The profiles and projections matter to silhouette and shadows, but the publications do not supply sections or dimensions. Removable chapter signs and foreground brick sign piers are separate from the house unless site-scope evidence says otherwise.

The 2018 polygon provides plan position/outline only. No building-height point-cloud analysis is stored for this asset, no roof survey or floor plan was found, and the source polygon's LiDAR provenance must not be mistaken for measured eave/ridge elevations. The candidate's **10.4 m eaves, 15.2 m principal ridge, 17.4 m chimney tops and three window/floor bands are estimates**. The two archival photographs show steep roof slopes and multiple levels, but perspective and lack of scale cannot validate those numbers. A nearby 1992 intersection/lot-change claim appears in a secondary chapter-history flashcard and was not adopted as a geometry fact.

## Evidence-led brief and discrepancy review

The available images support a red-brick Tudor Revival composition assembled from the 1928 house and a major 1970 addition. A future, separately authorized exterior pass should preserve the irregular six-corner plan, the distinction between the left arcade block, separate arched entry and lower long wing visible in the 1961 phase, and the larger connected gabled roof mass shown after the 1970 expansion. The post-addition source supports several roof volumes, dormers, chimneys and repeated window runs. It does not support an exact all-face shell, three identical front bays, precise dormer/chimney counts across the entire current roof, or datum-tied height.

Against existing audit/build evidence:

* The revised asset's six ground-level vertices now agree with the 2018 source polygon within **0.000013 m** maximum nearest-vertex error. Keep that coordinate/footprint result separate from facade certainty.
* The audit's photo-guided broad character (red brick, gables, roof slope, window rows and arched masonry entrance) is consistent with V1–V3. V1 resolves that the pre-addition facade's arcade has three round arches and the main entry is a distinct additional arch, but V1 is not the post-1970 complete front.
* The audit's three modeled front gables are visible in V3 and broadly compatible with the expanded post-1970 form, but V1 shows a different earlier arrangement. Do not infer that the same gables, window totals, and floor bands belong to every wing.
* The 1970 article establishes a major addition of about equal size to the prior Shelter; the existing evidence does not map the seam. A single continuous, uniform roof/elevation assumption would erase a real construction phase.
* Audit eave, ridge, stack heights and floor count remain estimates. No dimensional source was found in this research pass.

## Specific gaps and conflicts

| Area | Gap and sources already checked | What would resolve it | Effect on accurate exterior |
|---|---|---|---|
| Current post-1970 condition and phase seam | 1961 pre-addition cover, 1970 post-addition photo/text, and undated current chapter profile. | House-corporation renovation records, dated current all-corner photos, or the actual 1928/1970 plans and addition drawings in Indiana Historical Society records. | Cannot assign every wing, gable, opening or finish to original versus addition construction. |
| Facade orientation and all faces | Archive photo camera poses are unknown; only two old views and one cropped snowy profile exist. | Mapped current walkaround with corners tied to compass/site survey; image archive with documented shooting direction. | Front direction and three hidden faces remain unresolved; opening layouts cannot be completed. |
| Opening schedule, floors and entry | V1 gives one pre-addition front but no scale; V2 is distant; V3 is small and snow-covered. | Dimensioned elevations/sections and interior/egress plans, or high-resolution current face photographs with mapped positions. | Counts, floor-to-floor levels, window dimensions/mullions, lower openings and door details remain approximate. |
| Roof and vertical scale | Steep gables, dormers, and stacks are visible, but no roof plan, section or point-level 2018 roof analysis is available. | Archival roof/elevation sheets, measured survey, or raw georeferenced LiDAR with classified building returns and vertical datum. | Ridge/eave heights, pitch, valleys, parapets, stack locations and equipment stay estimates. |
| Materials and detail sections | Color reproduction supports red brick; no specifications or current close views. | Original/new-addition specifications; close daylight photos or facilities maintenance records. | Brick bond, joint, stone/metal trim, window frame, roof material/color and weathering cannot be specified. |
| Historical records | Finding aid lists 1928 photographs/plans and Purdue Archives list 1945–46 house/construction images, but contents were not directly inspected. | Request or digitize the specified Indiana Historical Society Box 9 Folder 31 and Purdue Archives J.C. Allen items 25.7.107–25.7.112. | Could establish earlier facade phases and entrance location more exactly. |

**Package:** [source register, original URLs, page/view IDs and SHA-256 hashes](source_register.json). PDFs and full-page rendered reference images are retained in `sources/`; existing audit, GIS metadata, footprint query and prior independent visual grade remain at `../../../../audit/delta_tau_delta_e06b0b5/`. This dossier records the evidence and unresolved questions; it is not a new model or a readiness declaration.
