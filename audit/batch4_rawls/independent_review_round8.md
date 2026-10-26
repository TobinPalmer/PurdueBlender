# Rawls Hall independent review — round 8

## Result

**Independent score: 7.1/10. Does not meet the 8.0/10 completion threshold.** Round 8 successfully fixes the stale parent-inverse transforms: the saved cameras, sidewalk apron, and south bronze mullions now evaluate in the Rawls-local frame, and the apron/mullion bounds no longer sit hundreds of metres away. The exact supplied asset independently reopened in Blender 5.2.3 at the expected SHA-256 with 722 objects and 714 meshes, without missing images or external linked libraries. The saved R8 renders are usable and not black. The repair does not change the structural shell geometry, and the south exterior still contains conspicuous flat opaque-looking panels. Interior and source-accuracy limits remain.

| Category | Score | Findings |
|---|---:|---|
| Exterior form and detail | 7.7/10 | The overall four-storey massing, brick pattern, floor bands, entrance, curved end and roof glazing are readable. North elevation windows are consistently framed. The south render still shows many large flat brown-gray recesses without visible panes, making the facade treatment inconsistent. Roof equipment, base, and some transitions remain simplified. |
| Materials and texturing | 7.0/10 | Brick course scale and lower mortar contrast improve the close-up, and the render set has coherent warm masonry and blue-gray glass. The south full view makes the unglazed-looking panels prominent. The south aperture close-up shows two convincing glass panes, but does not establish that the repeated facade recesses are glazed. Glass still reads as muted opaque/reflective surface in broader views, without clear interior depth. |
| Interior completeness | 6.1/10 | The plan overlay is a useful way to check the first-floor organization against Purdue's 2024 plan. Room 1086 is furnished with generic tables and chairs, but is sparse and shown only as a cutaway. The atrium section communicates a multilevel void, columns and railings; verified circulation, stairs/bridges, upper-floor partitions and current finishes remain absent or unverified. |
| Technical integrity and placement | 9.1/10 | Independent fresh reopen matched the expected asset hash, scene and counts. Root is identity; all eight named repaired objects have identity parent-inverse matrices. Six cameras are back at authored local positions, and the sidewalk/mullion meshes are back within the expected local extent. No mesh world-bound outliers over 120 m, materialless meshes, external images, or linked libraries were found. Shell geometry is unchanged. This is a strong transform/portability result; it does not independently prove survey-grade campus registration. |
| Evidence and source fit | 6.8/10 | The before/after transform evidence is specific and reproducible, and the audit includes current R8 renders. The plan supports the first-floor plan only; the archived interior photo is dated 2003 and cannot establish current finishes. The documented GIS conversion remains approximate by about 1–2 m. There is no saved, dated, head-on current exterior reference or dimensioned control tying the model to the facade. |

Weighted with the established 30/20/30/10/10 category weights: **7.13/10, rounded to 7.1/10**.

## R8 repair assessment

- **Parent-inverse repair: pass.** The independently reopened asset SHA-256 is `613174849a753f73aef4299d72223adeb0ceed01cf0fbc7aba4068d05bdf8088`. It contains 722 scene objects and 714 meshes in `Building_rawls_hall` / `Asset_rawls_hall`. The six camera transforms and two mesh transforms all have identity `matrix_parent_inverse`. The apron now spans approximately X -31.346 to 50.321 m, Y -26.226 to 22.610 m; the south mullions span X -10.732 to -5.066 m, Y -24.367 to -24.241 m. No mesh exceeded the ±120 m outlier check. The north, south, south-detail and sidewalk R8 images render as ordinary shaded views; none is black. This validates the saved repair and presented render outputs, not every possible renderer/camera configuration.
- **Geometry preservation: pass, with scope limitation.** R8 states and records that the structural shell mesh hash is unchanged. Thus the repair corrects object transforms and tunes shader values rather than correcting remaining facade aperture geometry.
- **Glazing consistency: not yet adequate.** In `south_exterior_round8.png`, most broad south recesses remain flat brown-gray blocks. `south_aperture_detail_round8.png` shows two actual looking glass panes, but the close-up does not establish glazing across the visible south elevation. The north elevation reads more consistently glazed than the south.
- **Interior readability: partial.** The R8 set does not add a new through-glass interior view. The available plan overlay and classroom/atrium cutaways remain useful supplemental illustrations, not evidence of a complete or current interior. No unsupported upper-floor/circulation details should be inferred from them.
- **Portability: pass.** Fresh reopen found no linked libraries, file-backed external images, or materialless meshes. This agrees with the supplied validation record.

## Prioritized refinements

1. Finish the repeated south apertures with source-supported glazing and consistent frame/reveal geometry; verify the complete elevation from a normal camera, not only a two-pane close-up.
2. Demonstrate one real exterior-to-interior sightline with the pane and plan-supported partitions visible; improve room context and finishes only where references support them.
3. Preserve a dated, location-identified current facade reference and provide measurable plan/map control points with residuals before claiming tighter registration than the stated 1–2 m.
4. Refine the simplified base and roof/equipment details against reproducible evidence; keep estimated upper-floor and atrium circulation clearly labeled.

The R8 repair resolves the specified stale-transform defect and is technically sound. The repeated opaque-looking south facade and limited interior/source verification keep the building below the project threshold.

## Reviewed artifacts

- `modular/buildings/rawls_hall.blend` (independently opened read-only)
- `audit/batch4_rawls/north_exterior_round8.png`
- `audit/batch4_rawls/south_exterior_round8.png`
- `audit/batch4_rawls/south_aperture_detail_round8.png`
- `audit/batch4_rawls/sidewalk_southwest_round8.png`
- `audit/batch4_rawls/2024_plan_geometry_overlay_round6.png`
- `audit/batch4_rawls/north_1086_room_sightline_cutaway_round6.png`
- `audit/batch4_rawls/atrium_void_clear_section_round6.png`
- `audit/batch4_rawls/core_plan_detail_round7.png`
- `audit/batch4_rawls/round8_final_evidence.md` and `.json`
- `audit/batch4_rawls/round8_final_reopen_validation.json`
- `audit/batch4_rawls/round8_transform_material_change.json`
- `audit/batch4_rawls/independent_review_round4.md` and `.json` (6.6/10 prior review)
- `audit/batch4_rawls/independent_review_round6.md` (7.0/10 prior review)
- `audit/batch4_rawls/photo_metadata.json`

Asset modified: **no**. Master/shared index modified: **no**. Commit created: **no**.
