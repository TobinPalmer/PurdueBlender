# Class of 1950 independent grade r2

Fresh review of `modular/buildings/class_of_1950.blend` using the criteria in `AGENT.md` and `modular/AGENTS.md`. The evaluator directly opens the current asset and current master read-only, compares the official ArcGIS footprint to the shell, checks the placement marker and manifest contract, and runs the current builder against a copied isolated project to exercise package-copy/reopen behavior.

The builder smoke test writes only inside `builder_smoke_project/`. The final asset was not modified. The current asset SHA-256 is recorded in `result.json`.

Evidence includes raw GIS and layer metadata snapshots, source provenance, current builder snapshot, official Purdue photos and floor-map PDF, Blender asset/master probes and logs, package smoke report, and saved model views. The two model views were produced for the asset revision whose file timestamp is 2026-10-25 19:57:09; the saved close render timestamp is 2026-10-25 19:57:08.

Run the evaluator with Python from this directory:

```powershell
python evaluate.py
```
