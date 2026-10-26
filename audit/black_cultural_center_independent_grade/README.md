# Black Cultural Center independent review

Fresh independent review of `modular/buildings/black_cultural_center.blend`, the canonical builder, the current `black_cultural_center` manifest entry, Purdue GIS FID 645, Purdue facility/location pages, and official campus exterior imagery.

The evaluator result is `result.json`; the rerunnable score function is `evaluate.py`. `probe_asset_and_export.py` measures the saved asset and writes an independent collection-only export. `probe_export_reopen.py` reopens that export. `probe_master.py` checks the master placement marker. The canonical builder was copied into `builder_smoke_project/`, run with the raw GIS snapshot, and its output was reopened and compared with the current asset.

The builder smoke comparison checks every object name, transform, mesh vertex stream, polygon count, and material list; the `.blend` files are not byte-identical because Blender serializes file metadata. All writes made by this audit are contained in this folder. No assigned building file or shared index was changed, and no commit was made.

Run `python evaluate.py` to regenerate `result.json`. Blender probes were run with Blender 4.5.15 LTS from the project root.
