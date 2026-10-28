# Alpha Xi Delta — source and review handoff

**FID 788 | Source asset:** `modular/buildings/massing_house_301841248_fe939c7.blend`  
**Asset SHA-256:** `ADD1D794C1B973BA330EEBB72DA09122188600DA8E3F5A19FAD7A4E107114028`  
**Status:** Ready for independent grade; grade pending. Pass bar: 8/10.

## What the evidence supports

The [official Purdue GIS FeatureServer record](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query?where=FID%3D788&outFields=*&returnGeometry=true&outSR=4326&f=pjson) directly identifies FID 788 as **Alpha Xi Delta**, address **519 University St**, owner category `GREEK`, and supplies a footprint polygon in EPSG:4326. The raw response is preserved in `source_fid788.json`. Applying the project's documented local approximate coordinate conversion yields a footprint about **23.65 m × 27.78 m**. The candidate structural outline is **23.50 m × 27.64 m**; the dimensions differ by about **0.15 m** on each axis. The candidate keeps the existing campus-coordinate frame and simplified 16-vertex outline. This does not verify detailed wall placement, openings, wings, or courtyards.

The [official Purdue Panhellenic chapter page](https://www.purduepanhellenic.com/cost/alpha-xi-delta) image provides a current, partial view of the house and chapter marker. A separate [Purdue recruitment photo on Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Alpha_Xi_Delta_sorority_rush.png) and a [local artist's stylized drawing](https://twotulips.com/products/purdue-sorority-custom-house-drawing) provide supporting exterior context. The drawing is secondary and was not used for measurements. West Lafayette permit listings for [2022](https://d3n9y02raazwpg.cloudfront.net/westlafayette/1d8683f3-a0a9-11ec-8a90-0050569183fa-cff30912-cddf-4b95-ab44-f6b7a2c8f869-1654624900.pdf) and [2025](https://d3n9y02raazwpg.cloudfront.net/westlafayette/a287052e-b24c-11ef-ab4b-005056a89546-cff30912-cddf-4b95-ab44-f6b7a2c8f869-1744643225.pdf) confirm work involving the basement/third floor and second floor at the same address; neither describes an as-built plan or measured height.

## Model changes

The saved library now includes a brick lower story, Tudor-style plaster-and-timber upper story, dark pitched roof and two dormers, windows and trim, entry porch and steps, and chapter signage. The library also includes floor plates, partitions, stairs, and generic furniture to make a ground-floor cutaway view possible. The interior plan is **schematic and unverified**; no recoverable floor plan was found.

Modeled roof ridge height is **13.25 m**, an estimate based on exterior proportions. GIS `NUM_LEVELS=1` and `Extrution=12` have unclear units and are not treated as authoritative height measurements. The permits confirm multi-level renovations but do not provide measured height.

## Previews and validation

- Exterior: `exterior_preview.png`
- Schematic ground-floor cutaway: `interior_cutaway_preview.png`
- Fresh-open report: `fresh_open_validation.json`
- Source and measurement record: `model_evidence.json`
- Rebuild script: `build_alpha_xi_delta.py`
- Fresh-open and cutaway script: `fresh_open_and_cutaway.py`

Blender 5.2.3 LTS opened the saved asset in a separate background process. The expected scene, named asset collection, and stable root object were present; the root mesh retained 32 vertices; all 267 building-collection objects were linked to the named collection; and no external image texture dependencies or preview-only objects were found inside that collection. The separate cutaway render hides the opaque exterior shell and upper floor plates to show the schematic ground floor.

## Independent review requested

Alpha Gamma Delta has been asked for a read-only review of this exact asset SHA. The review should score identity/source match, footprint/placement, exterior form/materials, interior/cutaway clarity, and documentation; report concrete remediation if the result is below **8/10**. No independent grade has been received yet.

