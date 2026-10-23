# Wetherill Laboratory of Chemistry — standalone asset review

**Asset:** `wetherill_laboratory_of_chemistry`  
**Source massing ID:** `massing_r_b_wetherill_laboratory_of_chemistry_wthr_1577024`  
**New library:** `../../modular/buildings/wetherill_laboratory_of_chemistry.blend`  
**Export collection / scene:** `Asset_wetherill_laboratory_of_chemistry` / `Building_wetherill_laboratory_of_chemistry`  
**Review date:** 2026-10-23  
**Rating:** **8.9 / 10** (visual fidelity: **8.9 / 10**) — improved after independent review; detailed appearance still has inferred geometry and simplified interior, so the 9/10 evidence threshold is not supported.

## Changes built

- Replaced the one-object massing shell with a separate local-coordinate building library. The original massing file was restored byte-for-byte from `massing_before.blend` and remains a separate source asset.
- Modeled five above-grade stories, five interior floor plates, a 14-edge perimeter, a flat roof and varied central roof plant, entrance stairs/doors, five inset chemistry-field plaques, a verdigris roof cornice, repeating red-brown brick bays, strengthened Indiana-limestone pilasters/portico, and gridded blue-grey windows.
- Added a schematic laboratory interior with central circulation, stairs/lift cores, casework, benches, fume hoods and corridor lights. Added a second-floor Leighty Commons interpretation with study seating, café counters, charging/display wall and an LED caffeine sculpture with its fused-ring and three-methyl branch topology. It contains 14 heavy-atom nodes and reopens at exactly 6.096 m (20 ft) X span; hydrogens are omitted and the visual geometry is not a measured bond model.
- Used procedural brick, limestone, glass, copper, terrazzo, metal and interior finishes. The saved library has **no external image textures or linked libraries**.
- Kept the presentation cameras and lights in `WTHR_Presentation_Only`, outside the exported asset collection.

## Geospatial check

The 14 wall outside faces reproduce Purdue Campus GIS feature **FID 257 / WTHR**. Reopen validation measured the maximum endpoint deviation from the saved ring at **0.0000084 m** (Blender float precision). Ring dimensions from the source are approximately **77.328 m east-west × 62.258 m north-south**. The local root is at `(0, 0, 0)` with unit scale. The campus placement origin for the master marker is **(51.040279, −103.148346) m** in the project’s local approximation from **(40.4274° N, −86.9137°)**, X east / Y north / Z up. The marker and manifest are intentionally left for the master agent to update.

**Source / transform:** [Purdue public campus building layer](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0), raw WGS84 snapshot retrieved 2026-10-22 and preserved at `../official_purdue_buildings_wgs84.json`; converted record is `../official_building_references.json`. Source CRS is EPSG:4326. The project uses its existing local linear approximation (origin above, 111040 m/degree latitude and 111412.84·cos(latitude) m/degree longitude); this is not a surveyed projected CRS. Purdue’s GIS metadata does not provide survey accuracy or a source edit date. The official layer lists seven levels, while Purdue’s 2014 emergency plan says five above-grade floors plus one basement; the modeled five floors follow the emergency plan, and the exact building height remains unverified.

## Visual references and decisions

- [Purdue Chemistry exterior photograph](https://www.chem.purdue.edu/admissions/admissions/WTHR.JPG), retrieved 2026-10-23; photo capture date unknown. Used for brick/limestone contrast, classical vertical piers, repeated multi-pane windows, carved panels, entrance stairs and dark green roof edge.
- [Purdue Chemistry Leighty Commons page](https://www.chem.purdue.edu/commons/) and [Commons photograph](https://www.chem.purdue.edu/commons/images/Leighty%20Commons%20Photos/commons1.jpg), retrieved 2026-10-23; image capture date unknown. Purdue places the Commons outside Room 200 and says the suspended caffeine LED sculpture is 20 ft wide and weighs more than 400 lb. The model uses the documented span; lounge furniture and layout remain interpretive.
- [PubChem caffeine record, CID 2519](https://pubchem.ncbi.nlm.nih.gov/compound/caffeine), retrieved 2026-10-23. The listed formula and SMILES support an 8 C / 4 N / 2 O heavy-atom graph with a fused ring system, two carbonyls and three methyl branches. Hydrogens and measured atom positions are omitted from the stylized sculpture.
- [Purdue University Archives Wetherill records](https://archives.lib.purdue.edu/repositories/2/resources/1483), retrieved 2026-10-23. Historical description identifies red brick trimmed with Indiana limestone and five chemistry-related carved designs above the main doors; those motifs are simplified in the asset.
- [Purdue Department of Chemistry emergency plan (July 2014)](https://www.chem.purdue.edu/docs/chemsafety/bep/BEPJuly2014.pdf), retrieved 2026-10-23. Supports five above-grade floors and a basement. The model does not claim a measured 16 m eave height; 3.2 m per story is an estimate.
- [Wetherill and Brown floor-plan PDF](https://www.chem.purdue.edu/bcce/BCCE_Program_book_white_pages.pdf), retrieved 2026-10-23, printed pages 24–25 (PDF pages 23–24). This is an event floor-plan diagram, not a complete current architectural plan. It supports room/corridor context only.
- [Google Maps satellite view centered on Wetherill](https://www.google.com/maps/place/Wetherill+Laboratory+of+Chemistry/@40.42685,-86.9141,19z/data=!3m1!1e3), visually reviewed 2026-10-23 at zoom 19 (50 ft scale bar). It identifies Wetherill and shows the surrounding campus placement, articulated flat-roof envelope and rooftop service equipment. Google does not display the imagery capture date in this view, and this review did not measure the roof edge from the pixels. The roof equipment layout and the entrance-side interpretation are visual inferences, not verified construction drawings.

The project’s converted polygon is the exact horizontal geometry reference. The façade proportions, window sizes, 16 m eave, roof equipment dimensions, story spacing and room partitions are estimates inferred from photographs, the level count and public diagrams. The Commons interior has a public photograph, while research-lab arrangements are schematic. A current measured floor plan, surveyed elevations and dated orthographic imagery were not available here. The 20 ft sculpture width and topology are source-backed, while its LED node colors/geometry are a visual interpretation.

## Reopen / export QA

`reopen_verification.json` was generated by opening the saved `.blend` in a fresh Blender 5.2.3 process. Result: **PASS**. It confirms the expected scene and export collection, 362 collection objects / 338 mesh objects, 23 assigned materials, origin-root at zero/unit scale, exact wall-ring registration within float tolerance, no unassigned mesh materials, no external image files or linked libraries, and a measured 6.09599996 m molecular sculpture span. Re-rendered views are `exterior_hero.png`, `building_overview.png`, `entrance_detail.png`, and `interior_commons_cutaway.png`.

## Rating rationale

| Criterion | Score | Evidence |
|---|---:|---|
| Footprint / local frame | 2.0 / 2.0 | Official WTHR ring; wall endpoints reopen within 0.0000084 m; local origin is explicit. |
| Exterior architecture | 2.3 / 3.0 | Limestone piers, portico, inset panels, brick bays and windows improved; overall elevation, window rhythm and exact carving remain inferred and visually simplified. |
| Materials / portability | 1.5 / 1.5 | Procedural, correctly differentiated materials; no external image or library dependency. |
| Interior | 1.6 / 2.0 | Source-backed Commons program and 20 ft caffeine sculpture topology/span; room furniture and lab partition layout remain schematic. |
| Roof / height | 1.0 / 1.5 | Varied central plant follows satellite appearance; eave height and equipment geometry are unmeasured. |
| Standalone verification | 0.5 / 1.0 | Reopened asset passes; master manifest/marker integration is the coordinating agent’s pending work. |
| **Total** | **8.9 / 10** | 9/10 would require measured elevation/roof evidence, current floor plans, and an entrance close-up review confirming plaque legibility after integration. |

## Changed paths

- `../../modular/buildings/wetherill_laboratory_of_chemistry.blend`
- `build_wetherill_detailed.py`
- `reopen_verify.py`
- `reopen_verification.json`
- `evidence.json`
- `exterior_hero.png`
- `building_overview.png`
- `entrance_detail.png`
- `interior_commons_cutaway.png`
- `reference_exterior.jpg`
- `reference_commons.jpg`
- `massing_before.blend` (byte-for-byte copy of the original massing asset)
No master blend, manifest, placement transform, or shared project script was edited.






## Final visual refinement pass (2026-10-23)

Reframed `exterior_hero.png` around the entrance to enlarge the central building name and five evenly spaced discipline labels; retained a separate `building_overview.png` for whole-building context. Reduced relief depth/size, moved the support piers into clear gaps, and shortened the stair rails to the stair run. Added four slim vertical Commons sculpture cables based on the documented suspended installation; their ceiling attachment points are an inference. The Commons cutaway includes the Nobel/research screens, one café sign, numbered cubbies, seating and the molecule with cast shadows disabled. Renders were rerun and visually inspected. Fresh Blender 5.2.3 reopen QA passes: 362 asset objects, 338 meshes, 23 materials, no external images or linked libraries, root at zero/unit scale, footprint error 0.0000084 m, and sculpture span 6.096 m. Candid score: 8.9/10. The remaining shortfall is due to inferred elevations/structural supports and schematic lab interiors; no roof detail was added without evidence.


