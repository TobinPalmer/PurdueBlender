# Modular Purdue campus

Each building has its own Blender library so different agents can edit separate buildings. The project root file `../purdue_campus_master.blend` is a lightweight linked master; `purdue_campus_linked.blend` is its modular workspace counterpart. Both use the same building libraries. The generated manifest indexes asset paths, exported collections, source objects, placements, and building IDs; consult it for the actual filenames.

Open a building's `.blend` file to work on that building. Detailed building geometry is stored around a local origin and linked through a `Placement_<id>` empty in the master. Move that empty to adjust campus placement. Save the source library and reopen the master to load its changes. Avoid editing linked geometry in the master: geometry changes belong in the source building file. Simple massing assets remain directly linked in campus coordinates. The pre-modular master and source snapshot are retained for recovery.

All assets use meters, X east, Y north, Z up, with geographic origin 40.4274, -86.9137. Detailed assets use local geometry coordinates; the master placement empty supplies the XY campus position. Simple massing assets retain campus coordinates. The master file uses relative library links so the project folder can move as a unit.

## Accuracy review

The master reviewer assigns building IDs to individual agents, validates their evidence and changes, and keeps a complete checklist. See [AGENTS.md](AGENTS.md) for the editing contract and review procedure. Partitioning the scene makes this work practical; partitioning alone does not establish accuracy.

Use official Purdue GIS or other identifiable authoritative footprint sources when available, supplemented by current imagery and published building information. Record the actual source and feature match for every building. Public footprints can support horizontal positioning and plan shape. Exact roof heights, facade dimensions, and elevation often need plans or measured survey data that public maps do not supply. Record these as unverified or estimated when necessary.

For each review record, include:

| Field | Required content |
| --- | --- |
| Identity | Manifest building ID, asset, collection, source feature ID |
| Provenance | Source URL/provider, retrieval date, source date if known, CRS |
| Placement | Before/after horizontal position error and measurement method |
| Plan geometry | Rotation, structural length/width, footprint comparison, tolerances |
| Vertical geometry | Ground reference, wall/roof height evidence, uncertainty |
| Change | Translation, rotation, dimension or geometry edits actually made |
| Review | Per-criterion status, reviewer, unresolved discrepancies |

## Known limitations inherited from the source project

- `../scripts/building_tools/audit_all_30_sectors.py` scores mesh density rather than geographic agreement. Existing sector percentages and architectural superlatives are not validation results.
- `../scripts/building_tools/build_campus_base.py` uses a local degrees-to-meters approximation. Comparisons in other coordinate systems need an explicit transform; Blender units alone do not define a surveyed CRS.
- The original massing generator uses fallback heights (including 7.5 m houses and 16 m campus buildings) and estimates 3.8 m per story. These are not measured dimensions.
- Legacy generation scripts contain absolute paths to an older workspace. Do not rerun them on modular files without reviewing their paths, deletion behavior, and placement assumptions.
- A decorative object's overall bounding box can include steps, roof overhangs, and signs. It is not automatically comparable to a ground footprint.

When reporting completion, give counts of verified, corrected, ambiguous, and unverified buildings and separate horizontal validation from height validation. Keep remaining uncertainty visible.

## Files to start with

- `purdue_campus_linked.blend`: assembled campus with relative library links.
- `BUILDINGS.md`: clickable index of 195 unique detailed and massing building assets.
- `manifest.json`: complete index including every simple background building and house.
- `verification.json`: file/link/object-count checks and documented transform changes.
- `rebuild_linked_master.py`: rebuilds detailed placement markers and removes matching massing blocks when a detailed library replaces them.
- `localize_building_asset.py`: converts a new detailed source library from campus coordinates to its local frame. Back up the file before running it.
- `source_backups/buildings_world_coordinates/`: recovery copies from the local-coordinate conversion.
- `../audit/MASTER_AUDIT.md` and `master_building_audit.csv`: exhaustive master review ledger.
- `../audit/official_footprints_reference.blend`: 508 official Purdue footprint outlines. Link collection `Official_Purdue_Footprints_Reference` into a working scene for a visual comparison; the outlines use campus world coordinates and do not render.
- `../audit/placement_corrections.json`: changes actually applied, their evidence, and remaining limitations. Wiley's gross hall/dining-court location mix-up was corrected using official hall envelope-center placement; exact wall registration and dimensions remain unresolved.

The original master is preserved as `../purdue_campus_master_before_modular_linking.blend`. Open `../purdue_campus_master.blend` for current work. Do not rerun legacy generators against the modular master. `../scripts/building_tools/split_buildings.py` is an initial migration utility, not the everyday update workflow: it retains existing exported files rather than overwriting agent edits. Building file saves followed by reopening the master are the everyday workflow.

