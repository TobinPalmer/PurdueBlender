# Independent review — Alpha Xi Delta, FID 788

**Grade: 7.6/10 — below the 8.0/10 completion threshold.** This review is read-only and applies to the exact saved asset SHA-256 `ADD1D794C1B973BA330EEBB72DA09122188600DA8E3F5A19FAD7A4E107114028` at `modular/buildings/massing_house_301841248_fe939c7.blend`.

## Rubric

| Category | Weight | Score | Evidence and limitations |
| --- | ---: | ---: | --- |
| Identity and provenance | 20% | 8.0 | Saved GIS snapshot identifies FID 788 as Alpha Xi Delta, address 519 University St, with 4326 geometry. Saved facade photos and the chapter illustration identify a matching Tudor-style house, but the audit folder does not record image URLs, capture dates, or source context for those references. |
| Plan geometry and placement | 25% | 7.5 | The structural base is about 23.50 × 27.64 m, close to the converted FID envelope of about 23.65 × 27.78 m, and it retains campus coordinates. The model uses a 16-point outline while the GIS feature has 24 distinct vertices. Comparing the base ring with the README local approximation gives about 3.72 m maximum symmetric vertex-to-boundary error, 530.35 vs 528.77 m² area, and 120.84 vs 129.02 m perimeter. No saved top-down overlay, orientation check, or independent placement check was found. |
| Exterior silhouette and openings | 25% | 7.5 | The model has a multi-level Tudor reading, repeated windows, dormers, entrance and stairs. It captures the photographed dark-timber/cream wall and brick base language. The roof remains one broad, simplified gable with two dormers; the saved facade references show a more articulated roofline and more dormers. Some window/frame assemblies read as projecting or detached in the main render. Roof/profile and several elevations remain inferred. |
| Materials and facade | 10% | 8.0 | Red-brown lower brick, cream upper wall, dark Tudor timber, slate roof, light trim and chapter marks broadly match the saved photo and illustration. The main preview is strongly overexposed and cyan-tinted, which makes material colors less dependable; the workbench preview is more readable. |
| Interior and legibility | 10% | 7.0 | The cutaway makes the two schematic floors, partitions, stair and furniture visible. The builder labels room layout as schematic and not a recovered floor plan. No source-derived interior plan was supplied, and the preview has no room labels or source overlay. |
| Presentation and technical | 10% | 7.0 | Blender 5.2.3 opened the exact saved file in background without error. It contains the expected scene and stable asset collection, no image datablocks or external image dependencies, and the stable `House_301841248` mesh has 32 vertices / 18 faces. The asset collection contains 267 objects and the scene contains 272 objects, versus the manifest's original one-object record; four preview camera/light objects remain in the scene. The render artifacts and this collection-count change need integration review. |

Weighted total: **7.55/10, rounded to 7.6/10 — FAIL (threshold 8.0)**.

## Source and inspection evidence

- Raw GIS snapshot: [`source_fid788.json`](source_fid788.json), FID 788 / Alpha Xi Delta / 519 University St; query CRS EPSG:4326. `NUM_LEVELS=1` and `Extrution=12` are GIS attributes; the unit for `Extrution` is undocumented, so this review does not treat it as measured height.
- Saved visual references: [`facade_reference_0.png`](facade_reference_0.png), [`facade_reference_1.png`](facade_reference_1.png), and [`illustrative_house_art.jpg`](illustrative_house_art.jpg). The former two contain property exterior imagery; the illustrated house is useful as a style/silhouette cue but should not be treated as a survey.
- Previews: [`exterior_preview.png`](exterior_preview.png), [`exterior_preview_workbench.png`](exterior_preview_workbench.png), and [`interior_cutaway_preview.png`](interior_cutaway_preview.png).
- Fresh-open inspection: loaded `modular/buildings/massing_house_301841248_fe939c7.blend` directly with Blender 5.2.3 in background. Observed scene `Building_massing_house_301841248_fe939c7`, asset collection `Asset_massing_house_301841248_fe939c7`, 267 collection objects, 272 scene objects, no images, plus the four preview camera/light objects. No file was saved during review.
- The official Purdue Panhellenic listing includes Alpha Xi Delta / Alpha Eta: <https://www.purduepanhellenic.com/cost/alpha-xi-delta>. GIS snapshot is the identity/address source; the Panhellenic page is not evidence for the parcel geometry.

## Required revisions before a passing grade

1. Add provenance for each facade image and illustration (source page or direct URL, provider, retrieval date, and any known capture date). Distinguish current property photos from the illustrative drawing.
2. Save a GIS-versus-structural-footprint overlay and explain or correct the roughly 3.72 m maximum boundary deviation and perimeter difference. Record orientation and absolute placement checks separately from the outline match.
3. Rework the roof massing and visible roof-to-facade transitions to better match the saved property photos; document the dormer/gable count and which details are supported by photographs versus illustration.
4. Improve the exterior preview exposure/color and resolve window assemblies that appear to float or protrude in the rendered view.
5. Keep the cutaway explicitly labeled schematic; do not present its room layout as an as-built interior without a floor-plan source. Reconcile the 267-object collection and preview camera/lights with the manifest/integration expectations through the coordinator.

**Disposition:** identity is credible and the exterior direction is promising, but the source traceability, footprint boundary agreement, roof silhouette and presentation details leave it short of the independent pass threshold. No changes were made to the asset or shared files.
