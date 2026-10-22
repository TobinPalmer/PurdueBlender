# Armory material upgrade evidence (2026-10-22)

Owned asset: modular/buildings/armory.blend; export Asset_armory. Backup: armory_before.blend.

Sources inspected:
- https://archives.lib.purdue.edu/agents/corporate_entities/571 — Purdue Archives, entity Armory 1918-current, establishes identity. Historical roof fire description does not certify present roof finish.
- https://earchives.lib.purdue.edu/digital/collection/pbuildings/id/140/ — Purdue e-Archives, pbuildings/140. Official monochrome exterior photograph downloaded as reference.jpg and visually inspected. Brick wall fields, pale trim, industrial windows are visible. Photograph date unknown in retrieved page; historical source, not current color measurement. Image pixel coordinates only, no geographic CRS.
- https://archives.lib.purdue.edu/repositories/2/archival_objects/5953 — Purdue descriptive archive record identifies brick and stone exterior in historical image; this record is circa 1920s, not current color evidence.

Limitations: current source geometry is an approximate AI reconstruction. Reference differs in window layout, roof profile and architectural detailing. Material upgrades cannot make those discrepancies photorealistically accurate. No coordinate, dimension, parenting or structural edits are authorized in this pass. Interior furnishings retain their unverified provenance. New material colors are artistic approximations, not measured samples.

Material changes:
- Purdue_Red_Brick: replaced uniform color with Poly Haven brick_wall_001 CC0 2K scan diffuse, roughness, OpenGL normal and height. 30 actual brick meshes receive face-projected metric UVs, 1.1m per scan repeat (representative approximately 0.21m by 0.065m brick module; no survey validation). 4mm bump depth plus restrained normal. Scan: https://polyhaven.com/a/brick_wall_001 .
- Bedford_Indiana_Limestone / Armory_Barre_Granite: subtle color variation and millimetre/submillimetre pores, matte roughness.
- Armory_Roof_Copper: restrained patina variation and partial metallic response; current finish not independently verified.
- Armory_Dark_Bronze, Armory_Dark_Oak, Campus_Teak_Wood_Bench: fine rough surface variations.
- Solar_Ribbon_Glass: glass IOR 1.5, 0.85 transmission, 0.12 roughness, opaque alpha avoids alpha sorting artifacts.

Validation: 967 exported objects retained, all world matrices equal before/after. No geometry position/dimension/topology changes; only added UV data. Four texture images packed, relative texture paths retained. Saved source asset reopened successfully and collection/object/image checks passed. Preview camera, light and world are scene-only; camera and light in Armory_Material_Preview outside Asset_armory, so they do not pollute linked campus export. Render settings: actual reopened asset, Cycles 32 samples denoised, AgX, 1400x1000 daylight; no generated-image retouching.

Visual review completed: hero.png and closeup.png (both 1400x1000) viewed directly. Metric coursing stays horizontal across walls/piers and masonry relief is visible without heavy geometric displacement. Scanned aged bricks show darker flecks and repeating variation; this is representative weathered masonry, not a unique facade scan. Hero exposes major inherited limitations: disconnected roof slabs/gaps and black-looking strips at corners (all meshes have assigned materials; possible inherited geometry/shading issue), simplified openings, and white trim. These require a separate geometry/architectural audit before any photorealistic-standard claim. Final result improves surface realism but is not a photorealistic or fully accurate Armory reconstruction.

## Follow-up visual blocker repair (supersedes materials-only preservation statements above)
Master expanded authorization to obvious geometry defects. Saved materials-only checkpoint armory_materials_only.blend before repairs.
- Added continuous interpolated roof skin using original roof segment center/eave positions; original 14 slabs retained but hidden for render/viewport. This closes visible gaps without inventing a new roof height or footprint. New skin is not a surveyed roof reconstruction.
- Main wall and tower shaft outer faces coincided exactly, causing black coplanar artifacts. External tower shaft vertices offset outward by 15mm; all object transforms retained. Overall scene envelope remains controlled by larger existing cornices.
- Existing east/west glass panels were buried inside solid walls (window front 25.55m vs wall front 25.75m). Moved only those existing window panels to x=+/-25.80m and added pale metal perimeter/cross muntins following industrial-window reference character. No new bays or interiors invented. This approximates a shallow dark recess with reflective opaque backing rather than claiming genuine openings through walls.
- Glass now mostly dark reflective (transmission .04), preventing false brick-through-glass appearance.
These corrections intentionally change geometry/selected window transforms; original assertions of every matrix unchanged apply only to the preceding materials pass. Footprint/local frame/export collection remain stable.
