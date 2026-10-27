# Independent grade — Village Bottle Shoppe

**Score: 7.8/10 — revise and regrade**  
**Exact asset SHA-256:** `5990CF81AF8BDA79474BD97D9CB727FBCA195CFF0B7DE21C73F7C1AF26A38A3F`  
**Fresh-open probe:** `fresh_open_probe.json`  
**Graded in:** Blender 5.2.3 LTS; saved file was reopened from disk.  
**Reference images inspected:** project exterior preview, Indiana GIO 2023 aerial crop, and the saved Google Street View panorama.  

## Score breakdown

| Category | Score | Findings |
| --- | ---: | --- |
| Site identity and source confidence | 7.0 | Official business listing and 2025 FSSA record support the 1832 Northwestern address. Indiana 2018 footprint objectid 409442 is plausible and its outline matches the modeled plan. The saved Street View panorama is explicitly adjacent context, captioned 1110 Lindberg Road; it cannot verify the building's own facade. The current audit does not visually reconcile the footprint to the subject photos in the county appraisal's Hi-ViNE report, which specifically identifies a Village Bottle Shoppe space. |
| Footprint, orientation, and placement | 9.0 | The building follows the 4-corner footprint; projected dimensions are about 26.89 × 17.59 m and plan area 472.92 m². Placement is consistent with the source conversion and the asset's bounds. Raw service area/perimeter fields conflict with computed polygon dimensions, correctly documented as unused. Height is estimated, not measured. |
| Massing and architectural details | 7.0 | The gabled, one-story volume, chimney, fascia, gutters, stoop, windows, and shutters read as a small converted house. The model's facade is very regular and the preview does not show a clear shop sign or distinctive storefront treatment. The direct subject photo set in the assessor report was not compared against the model, so facade geometry is not sufficiently substantiated. |
| Materials and texturing | 7.5 | Ten procedural materials are portable and include horizontal siding, roof shingles, trim, glass, brick, and concrete. The large roof shingle pattern is legible but looks uniformly repeated; siding relief is subtle and the viewport render is flat. No external image dependencies. |
| Interior / evidence handling | 8.5 | No floor plan was found, and the asset audit explicitly avoids inventing an interior. That is good evidence discipline. This category does not award points for an interior that could not be verified; a clearly labeled schematic interior could be added only if the scene needs one. |
| Blender integrity and portability | 9.5 | Exact file reopened with stable scene, collection, object, material nodes, and no issues. No external libraries or image paths. The mesh reports 34 non-manifold edges; this is not proven to be a visible defect, but the shell/roof joins should be checked before calling it production-clean. |

## Required revisions before 8/10

1. Resolve whether footprint objectid 409442 is the exact Village Bottle Shoppe structure or a neighboring/building-space association. The official business and FSSA location support the address, but the current image evidence is not a direct photo of the modeled facade.
2. Inspect and document the county appraisal report's `SUBJECT PHOTOS` (PDF pages 33–34, including the labeled Village Bottle Shoppe space) against the correct roof outline and elevations. The report is at `https://tippecanoe.in.gov/DocumentCenter/View/39966/Hi-ViNE---West-Lafayette`.
3. Revise facade openings, entrance/storefront, signage, and roof breaks only where the subject photos or imagery confirm them. Do not infer these details from the neighboring Street View panorama.
4. Produce a camera/render view comparable to the source elevation and check the 34 non-manifold edges for gaps or accidental internal faces.
5. Save a new asset revision, independently reopen it, and request a fresh grade against the new exact SHA.

## Evidence reviewed

- `audit/village_bottle_shoppe/README.md`: traceability and source limitations.
- `audit/village_bottle_shoppe/fresh_open_verification.json`: builder's fresh-open record.
- `audit/village_bottle_shoppe/independent_grade_r2/fresh_open_probe.json`: this grader's fresh-open measurement of the exact SHA.
- `audit/village_bottle_shoppe/preview_village_bottle_shoppe.png`: current exterior appearance.
- `audit/village_bottle_shoppe/sources/esri_world_imagery_near_1832_northwestern.jpg`: 2023 aerial footprint/roof context.
- `audit/village_bottle_shoppe/sources/google_streetview_1832_northwestern_pano.jpg`: adjacent context only.
- County appraisal report text identifies subject photos and a labeled Village Bottle Shoppe space; online source above, pages 33–34.
