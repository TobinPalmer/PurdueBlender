# Second-pass agents — use for the ranked completed-building queue

**Current phase — research only (user direction 2026-10-28).** Follow the reordered central-campus research queue in the root README, starting at new rank 1 and working down all buildings that have not yet received a modeled second pass. Produce one substantive research document per building in `research/second_pass/buildings/<stable_id>/README.md`, with many distinct real viewpoints/heights/distances, all faces and defining details, source snapshots/dates, footprints, available LiDAR/elevation datasets with CRS/units/acquisition dates and limitations, and explicit evidence gaps. Do not create or revise building models, builders, placements or the master during this phase. Resume modeling only after user direction. Existing second-pass work and its independent review history remain preserved; research completion does not imply visual acceptance. The original 90 Rossen assignments are preserved by building/asset ID; a new rank does not reassign ownership. Research-only authorization covers all rows, including unassigned future modeling assets.


For every building selected from the [README second-pass exterior ranking](README.md#second-pass-exterior-ranking), use the [Second-pass exterior agent](modular/AGENTS.md#second-pass-exterior-agent) and a separate [Independent second-pass visual review agent](modular/AGENTS.md#independent-second-pass-visual-review-agent). Follow the full research, modeling, review, iteration, and handoff instructions at the top of `modular/AGENTS.md`.

- **Second-pass exterior agent:** work on one assigned queue building at a time, in rank order. Research real exterior photographs from multiple angles and additional authoritative sources, then refine window placement, arches, entrances, roof silhouette, materials, and defining architectural details. Preserve source evidence, matched before/after renders, and uncertainty.
- **Independent second-pass visual review agent:** a separate subagent independently inspects the exact saved asset against real references from all sides and scores exterior fidelity on a 0–10 rubric emphasizing windows and distinctive architecture. The default acceptance threshold is **9.9/10**; below it, revise and independently regrade. After more than two genuine independently reviewed attempts (the third or a later unsuccessful attempt), agents may [protest and ask the user for a lower bar](modular/AGENTS.md#protest-process-after-more-than-two-attempts) with score history, remaining discrepancies, and a justified proposed target. Only explicit user approval changes the threshold; agents cannot self-approve an exception.

Use the queue's `Second-pass owner` column for second-pass assignments: the original 90 building assignments belong to Rossen and remain attached to those assets after reordering; all other modeling assignments remain unassigned. The older first-pass rubric and 8/10 threshold below do not accept a second pass. Existing file ownership, sync-before-commit, portability, Tobin-only master editing, and TODO handoff rules remain in effect. Independent review, all applicable review gates, and master-integration verification are still required under an approved threshold exception.

The original first-pass instructions follow unchanged.

For second-pass research and review, emphasize as many useful distinct real viewpoints as available: different camera heights/elevations, near/medium/far distances, frontal and oblique perspectives, all building faces, and different positions along and around each facade. Follow the viewpoint coverage log and matched-view requirements in `modular/AGENTS.md`; four principal elevations alone are not sufficient evidence of complete visual accuracy. Repeated crops or rotations of one image/panorama do not replace distinct camera positions. Keep all missing or occluded coverage explicit.

---

# AGENT.md — Add a detailed building

Follow this workflow for each new building. The project-specific rules in [modular/AGENTS.md](modular/AGENTS.md) and [modular/README.md](modular/README.md) apply as well.

## 0. File ownership and shared-file boundaries

- Follow the building owner shown in `README.md`. Before editing, confirm the assignment and stable building ID. Modify only files explicitly associated with your assigned building: its dedicated source/build script and its building-specific evidence or audit folder. Do not edit other buildings' files, even to make a seemingly related improvement; ask the coordinator to reassign or handle shared work.
- The master Blender file `purdue_campus_master.blend` is owned by Tobin Palmer. Only Tobin may edit, save, or commit changes to the master `.blend` file. Contributors may commit and push their assigned building work. After pushing, each non-Tobin contributor must add an entry to the root `TODO.md` describing the building, pushed commit or branch, asset path, and master-blend integration needed. When Tobin merges that work into the master blend, Tobin removes its entry from `TODO.md`.
- Shared files—including `README.md`, `AGENT.md`, `modular/AGENTS.md`, `modular/BUILDINGS.md`, `modular/manifest.json`, placement markers, and integration/verification scripts—are coordinator-owned. Subagents should report proposed changes instead of editing these files.
- Contributors may commit and push only their assigned building files. Shared files remain coordinator-owned. Before pushing, keep edits confined to the assigned file set so parallel work cannot overlap.

## Sync the master branch before each commit

The coordinating/master agent must pull the latest `origin/master` before every commit, including commits that contain only shared indexes or the master Blender file. Use `git pull --rebase --autostash origin master` after the intended files are ready. Review the result and resolve any conflicts according to file ownership; preserve other contributors' changes. If the pull cannot complete cleanly, stop before committing and resolve the conflict first. Never force-push shared history.

## 1. Scope the work

1. Choose one backlog building. Confirm its stable ID, asset path, footprint, and campus placement in `modular/manifest.json` and `modular/buildings/target_buildings_gis.json`.
2. Create a dedicated module at `modular/buildings/build_<building_id>.py`. Keep this building's geometry and export logic in that module; do not fold it into a shared campus assembly script.
3. Preserve the manifest asset path, ID, exported collection name, local coordinate frame, and placement marker.

## 2. Gather evidence from varied sources

Use multiple independent source types where available: official Purdue maps, facilities pages and plans; GIS or survey footprints; current aerial and street-level imagery; published elevations, photographs, and building descriptions. Prefer authoritative sources for identity and dimensions. Verify that the footprint represents the correct building, including wings and courtyards.

Save raw source snapshots in a building-specific evidence folder. Record URL, provider, feature ID, retrieval date, source date, CRS, measurement method, and uncertainty for each source. Label estimated heights as estimates, never measurements.

## 3. Build and export the modular library

Build only this building in its dedicated module, using the documented local coordinate frame. The module should create geometry from the collected sources, including the footprint, orientation, floors, roof silhouette, facade rhythm, entrances, and distinctive features supported by evidence. Keep the campus position controlled by the corresponding `Placement_<id>` marker and manifest entry. Use portable relative paths or pack textures.

Export the expected named collection to the manifest asset path. Include a preview render and structured evidence record. Do not alter the campus origin or unrelated assets. After the building is finished and its evidence is complete, commit the changed files for that building.

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
