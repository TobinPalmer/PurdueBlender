# AGENT.md — Add a detailed building

Follow this workflow for each new building. The project-specific rules in [modular/AGENTS.md](modular/AGENTS.md) and [modular/README.md](modular/README.md) apply as well.

## 1. Scope the work

1. Choose one backlog building. Confirm its stable ID, asset path, footprint, and campus placement in `modular/manifest.json` and `modular/buildings/target_buildings_gis.json`.
2. Create a dedicated module at `modular/buildings/build_<building_id>.py`. Keep this building's geometry and export logic in that module; do not fold it into a shared campus assembly script.
3. Preserve the manifest asset path, ID, exported collection name, local coordinate frame, and placement marker.

## 2. Gather evidence from varied sources

Use multiple independent source types where available: official Purdue maps, facilities pages and plans; GIS or survey footprints; current aerial and street-level imagery; published elevations, photographs, and building descriptions. Prefer authoritative sources for identity and dimensions. Verify that the footprint represents the correct building, including wings and courtyards.

Save raw source snapshots in a building-specific evidence folder. Record URL, provider, feature ID, retrieval date, source date, CRS, measurement method, and uncertainty for each source. Label estimated heights as estimates, never measurements.

## 3. Build and export the modular library

Build only this building in its dedicated module, using the documented local coordinate frame. The module should create geometry from the collected sources, including the footprint, orientation, floors, roof silhouette, facade rhythm, entrances, and distinctive features supported by evidence. Keep the campus position controlled by the corresponding `Placement_<id>` marker and manifest entry. Use portable relative paths or pack textures.

Export the expected named collection to the manifest asset path. Include a preview render and structured evidence record. Do not alter the campus origin or unrelated assets.

## 4. Validate

Reopen the saved `.blend` and inspect evaluated geometry, modifiers, and collection transforms. Check footprint, placement, orientation, dimensions, height, roof, facade, and neighboring context separately. Confirm the master links the detailed asset once at the intended location and removes/replaces any corresponding massing block. Record checks, edits, results, and remaining uncertainty.

## 5. Spawn an independent grader subagent

Once the first complete model and evidence are ready, spawn a separate subagent whose task is to grade the building against the source evidence and rubric below. The grader must implement and run an evaluator function returning a score from 0 to 10, criterion-level evidence, and findings. Give it the model path, source/evidence paths, and rendered views. The grader must assess evidence directly rather than repeat the builder's claims.

| Criterion | Points |
|---|---:|
| Correct identity and source-backed footprint | 2 |
| Position, orientation, and scale/dimensions | 2 |
| Evidence-backed height, floors, and roof form | 2 |
| Facade, entrances, and distinctive architecture | 2 |
| Modular export, portability, and complete evidence | 2 |

The evaluator function must return at least `{ score, max_score: 10, criteria, evidence, findings }`. **Minimum passing standard: 8/10.** Mark unsupported criteria uncertain and deduct the corresponding points; appearance alone is not evidence.

## 6. Iterate and finish

If the grade is below 8/10, address the findings, rebuild, and request a fresh independent grade. Repeat until the evaluator returns at least 8/10. Save the final evaluator result with the building evidence. Then remove the building from the pending table in `README.md` and update `modular/BUILDINGS.md` and other applicable indexes. Report the score and any unresolved uncertainty.
