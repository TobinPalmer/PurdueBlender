# Asian American and Asian Resource and Cultural Center independent review

Fresh independent review of the current canonical asset and its builder against `AGENT.md`, `modular/AGENTS.md`, the official GIS record, current Purdue facility photos/page, and manifest. The result is in `result.json`; evaluator code is `evaluate.py` and Blender asset/master probes are in `blender_probe.py` and `master_placement_probe.json`.

The independent collection-only export was written and reopened under Blender 4.5.15. No building asset, build script, or shared index was changed by this review. All new files are confined to this folder.

Run `python evaluate.py` to regenerate the score from the saved probes/source snapshots. The Blender probe can be rerun from the PurdueBlender repository using Blender 4.5.15 with `--background --python-exit-code 1 --python audit/asian_american_resource_and_cultural_center_independent_grade/blender_probe.py`.
