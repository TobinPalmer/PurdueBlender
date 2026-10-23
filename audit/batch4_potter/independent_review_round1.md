# Potter Engineering Center — Independent Review, Round 1

**Asset reviewed:** `modular/buildings/potter_engineering.blend`  
**Review date:** 2026-10-23  
**Reviewer scope:** independent inspection of saved asset, round evidence, official current-use and planning references, GIS envelope, and Blender reopen health. No model edits made.

## Rating

**Overall: 6.1/10**

The pass improves the red brick/precast palette, window framing, and a historically sourced Room 205 lab vignette. The GIS shell and asset organization are technically stable. The model remains a simplified exterior shell with a blanket roof slab and incomplete circulation and rooms, so it does not yet meet a 9/10 building-detail target.

| Category | Score |
|---|---:|
| Footprint, placement, and massing | 7.0/10 |
| Exterior form and facade fidelity | 5.8/10 |
| Materials and surface detail | 6.3/10 |
| Interior completeness and circulation | 4.2/10 |
| Architectural details and rooftop | 5.5/10 |
| Technical health and modular export | 9.0/10 |
| Evidence and source discipline | 8.0/10 |

## What is working

- **GIS shell and modular structure:** the export collection is present; the asset root is at local origin; the envelope is about 58.45 × 67.43 × 15.5 m. A fresh Blender 5.2 background reopen found 462 objects, all expected material families, and no missing external image dependencies.
- **Facade language:** the render reads as Potter’s broad red-brick piers, light precast panels, small recessed square windows, and brown ground-level treatment. The exterior photograph linked from Purdue’s official Potter page is consistent with that general material vocabulary.
- **Window pass:** the report documents 208 openings and the close view shows a repeated framed inset-window treatment with projecting shades. This is meaningful progress over a blank shell, although the regularity and facade distribution remain approximate.
- **Historical room treatment is labeled honestly:** the Room 205 vignette draws on the 2016 renovation study’s existing-condition lab photographs and is not presented as current. Purdue’s facilities page currently documents Room 160’s library across three floors, Room 114, and Room 127, among other spaces. The 2016 study is suitable as historical evidence, not a complete current layout.
- **Future renovation is kept separate:** Purdue’s Aug. 7, 2026 capital-plan article describes a planned Potter renovation of the first floor and basement, including a new main entrance and student collaboration space. Those future changes should remain distinct from the existing-state model.

## Blocking findings toward 9/10

1. **Roof and upper silhouette are unfinished.** The exterior render is dominated by one smooth, bright, nearly featureless roof surface extending across the entire footprint. No measured penthouse, parapet articulation, roof drainage, or supported rooftop equipment is visible. The current roof is an estimate and its plan outline is inherited from the GIS envelope; distinguish the actual roof profile from the ground footprint and support any rooftop features with dated imagery or plans.

2. **The facade still reads as a repeated prototype.** The close view has a regular sequence of large pale panels, brick piers, dark horizontal bands, and tiny windows. The whole-building view repeats similar bays across long elevations and has little readable entrance/stair composition. The Purdue-linked exterior photo and the batch report both caution that the photo’s capture date and elevation are unknown; use it for material vocabulary but do not infer an exact elevation layout from it. Add photo-matched facade variation only where an elevation is identified, and document unresolved sides.

3. **Interior circulation is not yet a usable building interior.** The current evidence shows a staged Room 205 cabinet/sink vignette by itself. The asset still contains historic raster-traced partition sets from 2016, but the report itself notes unresolved stairs, elevator, doors, entry, and mezzanine, with duplicated or uncertain plan traces from prior reviews. Add connected floor-by-floor corridors, stair/elevator cores, doors, and coherent room boundaries. The Room 160 library spans three floors according to Purdue’s current page; it is a high-value current-use anchor. Keep Room 205 explicitly historical and don’t extrapolate its photo into unverified current spaces.

4. **Evidence supports materials better than exact geometry.** The report cites approximate plan registration (75.7–85.5% IoU) and an estimated historic lab placement. At roughly 1–2 m plan uncertainty, room boundaries, window bay positions, entrance allocation, and facade panel rhythm should not be represented as measured precision. Add a dated, elevation-identified reference for each facade and preserve source uncertainty in object names or the evidence ledger.

5. **Rendered fidelity needs another close inspection pass.** In the exterior view, the window glass is almost black and the facades have little depth or weathering variation; the uniform open studio makes the model read as a CAD study rather than a finished campus building. Improve glazing/transmission and reflections, refine panel/brick transitions and ground contact, and render oblique street-level and entrance views with context. The current closeup supports brick courses and shade geometry but not realistic material response at ordinary viewing distance.

## Evidence and limits

References independently checked:
- Purdue’s current Potter facilities page: https://engineering.purdue.edu/Engr/AboutUs/Facilities/PotterEngineeringCenter . It documents the building’s current multipurpose role and named rooms/use cases including Room 160, Room 114, and Room 127.
- Purdue’s 2016 Potter Engineering Center Renovation Study: https://engineering.purdue.edu/~frosch/Renderings/Masterplans/POTR%20Study.pdf . The model report identifies existing-condition plans and Room 205 lab photos in this source. Its proposed renovation schemes are not existing geometry.
- Purdue’s Aug. 7, 2026 capital-plan notice: https://www.purdue.edu/newsroom/2026/Q3/trustees-approve-10-year-capital-plan/ . Potter’s first major renovation since opening in 1977 is planned for its 39,000-square-foot first floor and basement, including a main entrance and collaboration space.
- Purdue College of Engineering Vision 2030 page: https://engineering.purdue.edu/Engr/AboutUs/MeetDean/Vision-2030/space-master-plan . It marks Potter as early ideation and lists future workspace/lab intentions, not surveyed current conditions.

The builder’s batch report records that its Google Maps imagery had no verified acquisition date or identified elevation. I did not treat it as dated geometry evidence. I inspected the three saved batch renders and fresh-reopened the standalone blend in Blender 5.2 without saving changes. Reopen results: 462 objects in `Asset_potter_engineering`, root at (0,0,0), structural envelope 58.45 × 67.43 × 15.5 m, 13 material families, no missing image files. Builder-provided topology checks report closed shell/basement/partition meshes; these checks do not establish architectural accuracy.

## Next revision criteria

For a 9/10 review, prioritize: (1) resolve roof silhouette and entrance/stair composition from identifiable references, (2) finish connected circulation and current-use interiors using authoritative floor plans, keeping the Room 205 2016 vignette historically labeled, (3) vary facade bays only where supported by elevation evidence, and (4) provide street-level material renders that show glass, panel depth, and ground contact convincingly. Re-run save/reopen and export checks after geometry changes.

