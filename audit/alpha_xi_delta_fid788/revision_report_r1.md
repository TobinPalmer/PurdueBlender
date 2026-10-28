# Alpha Xi Delta — revision 1 response

**FID 788 | Asset:** `modular/buildings/massing_house_301841248_fe939c7.blend`  
**Revision SHA-256:** `95AAF80107165DFCF9EF43FBA15835B995F78949FCA71AF4A956715229AC989A`  
**Prior independent review:** [7.6/10 FAIL report](independent_grade_2026-10-28.md) for SHA `ADD1D794C1B973BA330EEBB72DA09122188600DA8E3F5A19FAD7A4E107114028`. The original scorecard is preserved unchanged.

## Responses to the review

- **Visual-source provenance:** added local copy of the official Purdue Panhellenic image and the 2008 Wikimedia recruitment photo. Recorded providers, URLs, retrieval date, capture date (where known), photographer, and the Wikimedia camera metadata in `model_evidence.json`.
- **GIS boundary and orientation:** replaced the simplified 16-vertex shell outline with all 24 unique FID 788 vertices after the project-local approximate conversion. Added `footprint_overlay.svg` and `footprint_comparison.json`. Both outlines coincide to 0.000016 m by construction. Their PCA vertex-axis headings differ by 0.000052 degrees by construction. This comparison is not independent validation or a survey; the project conversion is approximate and no separate placement/orientation source was found.
- **Roof and dormers:** rebuilt a stepped gabled roof with front, north, east and northwest wings and three front dormers, aligned with the facade cues in the available official image/photo packet. Roof shape, heights, and unseen elevations remain estimated.
- **Exposure, color, and facade:** retained a neutral mid-gray Workbench background and toned materials for legibility. The exterior preview now shows brick, cream plaster, dark timber, dark roof, blue-gray windows and entry treatment without the prior bright cyan cast.
- **Window alignment:** placed assemblies against the corresponding straight GIS boundary runs and merged them into one facade assembly; visual alignment is improved but opening locations remain inferred from photographs, not measured drawings.
- **Collection and camera cleanup:** grouped repeated elements into a 37-object/37-mesh asset collection. Saved scene contains exactly those 37 mesh objects, with no preview camera, lights, or image texture dependencies.
- **Interior/cutaway:** kept the plan schematic and unverified. Updated the cutaway script to fresh-open the saved file and show ground-floor partitions/furniture with roof, exterior and upper slabs hidden. The cutaway is illustrative and is not an as-built room plan.

## Fresh-open evidence

Blender 5.2.3 LTS opened the saved asset in a separate background process. `fresh_open_validation.json` records PASS: stable scene, collection and root object present; root shell has 48 vertices representing the 24-point extrusion; all 37 asset meshes are linked in the named collection; scene object count is 37; no saved camera/light or external image dependency.

Previews: [exterior](exterior_preview.png) and [ground-floor cutaway](interior_cutaway_preview.png). Source outline comparison: [SVG overlay](footprint_overlay.svg).

## Remaining limits

GIS supports identity and the plan boundary, but cannot verify structural wall lines, height, roof form, story count, window spacing, or room layout. The shell boundary match is by construction. The GIS `NUM_LEVELS` and `Extrution` fields have no documented units/semantics for this use. All heights, facade details and interior plan remain estimates or schematic.

**Review status:** requesting a read-only independent regrade of exact SHA `95AAF80107165DFCF9EF43FBA15835B995F78949FCA71AF4A956715229AC989A`.
