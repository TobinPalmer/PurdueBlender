# Second-pass exterior workflow

**Use the Second-pass exterior agent below for buildings on the root [README second-pass exterior ranking](../README.md#second-pass-exterior-ranking).** That queue and its `Second-pass owner` column are the authority for second-pass scope, work order, and assignment. Ranks 1–90 are Rossen-owned; remaining entries are unassigned until the coordinator assigns them. Do not infer permission from an old first-pass owner or a `Finished` status. A building's existing first-pass grade is not its second-pass visual grade.

For second-pass work, this section takes precedence over the older first-pass workflow's 8/10 threshold and rubric. The default second-pass threshold is **9.9/10**, independently assessed for exterior accuracy. A lower building-specific threshold requires explicit user approval through the protest process below. Existing ownership, coordinate, portability, master-file, synchronization, and handoff rules still apply. The original instructions are preserved below for first-pass work and general asset handling.

## Second-pass exterior agent

**Role:** refine the assigned completed building so its exterior closely matches the real building from multiple viewpoints. Use this agent for every building selected from the second-pass ranking list. Work on one assigned building at a time, in queue order; confirm its stable manifest ID, asset path, exported collection, current owner, and any identity conflicts before editing. Do not start unassigned buildings or redo unrelated interiors, site assets, or neighboring buildings.

### Research the actual exterior before modeling

1. Read the current audit, prior grader findings, builder, and saved model. Establish the correct building, wings, additions, facade orientations, and reference date. Resolve current-versus-historic imagery and renovation differences explicitly; do not combine incompatible eras into one facade. An unresolved identity or shared-structure conflict must be documented and escalated to the coordinator.
2. Collect and inspect real exterior photographs from multiple angles. Seek all four principal elevations (or every distinct facade on an irregular building), at least two corner/oblique views, a roof/aerial view, and close-ups of entrances and signature details. Record the facade/direction and feature shown by each image. Several crops of one photo do not count as independent views. Use available authorized street-view captures or published photos; do not claim to have taken on-site photographs. Never use AI-generated images as evidence of the real building.
3. Cross-check imagery with other useful sources: Purdue facilities and departmental pages, architect/project portfolios, preservation or historical records, elevations, floor plans where they clarify exterior openings, GIS footprints, aerial imagery, and measured dimensions when available. Plans and footprint agreement alone cannot establish window placement or facade accuracy. Prefer current, correctly identified evidence, and use historic material only for features still present or a documented historical target.
4. Preserve source snapshots or permitted screenshots in `audit/<building_id>/second_pass/sources/`. Record URL, provider/photographer, retrieval date, image/source date if known, facade/view direction, relevant feature, source identifiers and CRS where applicable, measurement method, and uncertainty. For sources that cannot be saved, retain a reproducible citation/view location and explain the limitation. Label photo-derived dimensions as estimates. Keep a reference index and a facade-by-facade coverage matrix marking observed, estimated, conflicting, and unseen features.
5. Produce an exterior discrepancy checklist before editing. Compare actual reference images with baseline renders at similar camera angles, framing, and focal length. Include every visible elevation and roof; a flattering front render alone is insufficient. List missing evidence explicitly and search for alternate viewpoints rather than inventing hidden architecture.

### Model the details that determine visual identity

- **Windows and glazing:** verify count and placement per floor and facade, bay spacing, alignments, sizes/aspect ratios, setbacks, reveals, sills/lintels, mullions, frame thickness/color, glass tint, curtain-wall divisions, and solid-versus-glazed areas. Do not apply one repeated window grid across elevations that differ in the references.
- **Distinctive architecture:** match arches and their profiles/depth, arcades, columns/pilasters, entrance portals, canopies, stairs/ramps, balconies, cornices, parapets, stone bands, ornament, clock faces, towers, spires, inscriptions, and other building-specific features. Include only features supported by evidence; keep adjacent monuments or landscaping within the existing ownership boundary and ask the coordinator to handle shared assets.
- **Overall exterior:** preserve or correct evidence-backed proportions, floor heights, setbacks, wings, courtyards, roof slopes/ridges, dormers, rooftop volumes, chimneys, and the recognizable silhouette. Preserve verified footprint and campus placement; do not move or rescale an entire building merely to make one photograph line up.
- **Materials and facade composition:** match brick/stone/concrete/metal distribution, panel and masonry scale, trim, color, roughness, glazing, entrance positions, and depth relationships under neutral daylight. Model architectural depth where it changes the silhouette, shadows, or oblique appearance; textures must not conceal missing geometry.

Edit only the assigned source library, dedicated build script, and building-specific evidence. Preserve the stable ID, asset path, collection name, local coordinate frame, and portable dependencies. Keep the builder consistent with the saved library, document intentional manual edits, and avoid changes to unrelated assets. The campus master remains Tobin-owned.

Save and reopen the exact `.blend` after each revision. Render a consistent review set: all principal elevations, two oblique views, roof/top view, and close-ups of windows, entries, and distinctive details. Use comparable neutral lighting and cameras across iterations; do not hide defects with shadows, foliage, depth of field, cropping, or low resolution. Store before/after comparisons, revision ID and asset SHA-256, camera/render settings, the change log, and known uncertainties under `audit/<building_id>/second_pass/`.

## Independent second-pass visual review agent

**Role:** independently judge the saved building's exterior against real source evidence. Once a revision is ready, spawn a separate reviewer subagent that did not author or edit that revision. The modeler must not self-approve. Give the reviewer the stable building ID, exact saved asset path and SHA-256, source index/coverage matrix, prior findings, and review renders. The reviewer must open the asset, inspect the sources directly, verify the hash, and generate or request additional views when needed. Assess the current revision before consulting the modeler's proposed score; neither queue importance, current first-pass score, mesh density, nor the builder's claims may influence the visual grade.

The reviewer may write only its building-specific review/evaluator outputs; it must not repair the geometry it is grading. Inspect all principal elevations, roof silhouette, and distinctive details, using side-by-side source/render comparisons at matched viewpoints. Check window counts and bay spacing explicitly and identify concrete discrepancies by facade, floor, and feature. Review the asset as saved, not an earlier render or unsaved Blender state.

Implement and run an evaluator that sums independently assessed criterion points. Each award/deduction must cite source evidence and a model view; automated geometry checks may support, but cannot replace, visual inspection. Save the evaluator and its result in `audit/<building_id>/second_pass/review_rNN/`.

| Exterior visual criterion | Maximum points |
| --- | ---: |
| Window/opening placement, counts, rhythm, proportions, frames and glazing divisions on all elevations | 3.0 |
| Signature architecture: arches, entrances, columns, towers, ornament and other defining details | 2.5 |
| Overall proportions, wings/setbacks, roof form and silhouette | 2.0 |
| Material/color fidelity, surface scale, trim and facade depth | 1.5 |
| Whole-building visual consistency across all elevations and matched oblique views | 1.0 |
| **Total** | **10.0** |

Do not award points for adding interiors or increasing polygon counts. If a feature category does not exist on this building, judge fidelity to its actual simpler architecture within that category; do not add fictional ornament or change the weights. Missing or contradictory reference coverage reduces the supported points in the affected criteria. State precisely what remains unverified; lack of evidence is not evidence of accuracy.

The result must include `{ building_id, revision, asset_path, asset_sha256, reviewer, reviewed_at, score, max_score: 10, criteria, evidence, reviewed_views, findings, uncertainties, gates, acceptance_threshold, threshold_approval, accepted }`. Each criterion records its maximum, awarded points, citations, and deductions; findings identify facade/feature and required correction. `score` is the sum of awarded points, not a hard-coded target or the queue priority. `acceptance_threshold` defaults to 9.9 and `threshold_approval` to null; record the explicit user approval if a lower target is authorized. Compare the unrounded total to the applicable threshold; never round a lower result up to a passing score.

In addition to the visual score, record pass/fail gates for correct identity, adequate exterior-reference coverage, no unresolved material exterior discrepancies, saved-file reopen, expected collection/export, portable dependencies, and no regression to verified footprint/orientation/scale. A known wrong window pattern, missing defining arch, or other material exterior mismatch must be corrected even if the numerical total reaches 9.9. Unsupported or unseen elevations cannot be silently treated as verified. Master integration is a separate coordinator/Tobin gate, not visual bonus points.

## Second-pass iteration and completion

1. **If the independent score is below 9.9/10, iterate** unless the user has explicitly approved a lower building-specific target under the protest process below. The exterior agent addresses the reviewer’s concrete findings, gathers additional references when needed, rebuilds/saves/reopens, and submits the new hashed revision for another independent visual review. Reuse or spawn an independent reviewer; it must remain separate from the modeler. Repeat until the applicable threshold is met and all applicable review gates pass. A change after review invalidates acceptance until that new saved revision is reviewed.
2. Retain each round's evidence, renders, evaluator, score, and findings so improvement and remaining uncertainty are inspectable. Do not overwrite failures with a passing result, change criterion weights to inflate a grade, fabricate details, or stop at the older 8/10 threshold. If missing evidence or access prevents responsible progress, record the exact blocker and needed source; leave the second pass incomplete for the coordinator rather than manufacture a 9.9.
3. After the source asset passes, commit/push only assigned building files. Follow the existing root `TODO.md` handoff rule for non-Tobin contributors, including the exact revision, asset path, second-pass score, review path, and integration needed. Only Tobin edits/saves the master. Tobin verifies the reviewed revision is integrated and fresh-opens the master to check links, placement, and affected close views.
4. Report the final independent visual score, review path, reviewed asset hash, before/after comparisons, and remaining non-blocking uncertainty to the coordinator. The coordinator records completion and the separate second-pass visual grade in the README queue only after visual acceptance and master-integration verification. Preserve first-pass history and original scores; do not present a priority index as a grade or silently reassign the remaining queue.

### Protest process after more than two attempts

If 9.9 appears impractically high **after more than two genuine, independently reviewed attempts** (the third or any later unsuccessful attempt), the exterior agent or independent reviewer may protest and ask the user for a lower acceptance bar. An attempt consists of an actual modeling/evidence revision followed by an independent review of that saved revision; rerunning the same evaluator or unchanged model does not count as another attempt.

Submit the request through the coordinator with the building/asset ID, each attempt's hash and score, changes made and score improvement, remaining visual discrepancies and missing evidence, the independent reviewer's assessment, why further work is unlikely to reach 9.9 responsibly, and a proposed lower threshold with the tradeoff explained. Save this record as `audit/<building_id>/second_pass/threshold_protest.md`. The modeler and reviewer may disagree; preserve both assessments instead of pressuring the reviewer to raise a score.

**The agents may request a lower bar, but cannot approve their own exception.** Until the user explicitly agrees, 9.9 remains in force and the building stays incomplete. Continue useful supported revisions where possible; otherwise report that the threshold decision or specific evidence is pending. If approved, record the user's decision, date, building scope, new threshold, and accepted limitations in the review metadata and README completion record. Apply the exception only to the named building unless the user explicitly changes the global policy. Independent review, honest scoring with the same rubric, and the other acceptance/integration gates remain required. If the request is declined, continue toward 9.9 or document the concrete blocker without claiming completion.

---


# Building asset work rules

These rules apply to this directory and its building files. Read the README and the generated building manifest before editing.

## File ownership and merge-conflict prevention

- Use the owner assignment in the root `README.md`. An agent may edit only the assigned building's source library, dedicated build script, and building-specific evidence/audit folder whose names identify that building. Do not edit any unassigned building file.
- The root campus master `../purdue_campus_master.blend` is Tobin Palmer-owned. Only Tobin may edit, save, or commit that master file. Contributors may commit and push their assigned building work. After pushing, each non-Tobin contributor must add an entry to the repository-root `TODO.md` describing the building, pushed commit or branch, asset path, and master-blend integration needed. When Tobin merges that work into the master blend, Tobin removes its entry from `TODO.md`.
- `README.md`, `AGENT.md`, `modular/AGENTS.md`, `BUILDINGS.md`, `manifest.json`, shared placement data, and integration scripts are shared coordinator-owned files. Request changes through the coordinator rather than editing them in parallel.
- Contributors may commit and push only their assigned building files. Shared files remain coordinator-owned. Keep each task's write set limited to its assigned paths.

## Assigned building agent

- Own one manifest building at a time. Edit only its asset and its evidence record. Ask the coordinating agent to assign adjacent assets when a shared feature needs changes.
- Keep the manifest asset path, building ID, and exported collection name stable. Do not rename the exported collection or add unrelated buildings to it.
- Coordinates are meters: X east, Y north, Z up. Geographic origin is latitude 40.4274, longitude -86.9137. Detailed building libraries use local geometry coordinates. Their `Placement_<id>` collection-instance marker in the master supplies campus XY placement from `manifest.json`; keep the marker and manifest origin in sync. Do not change the campus origin. Simple massing libraries still use campus coordinates and are linked directly.
- Use the project's conversion for compatibility: X = (longitude + 86.9137) * 111412.84 * cos(radians(40.4274)); Y = (latitude - 40.4274) * 111040.0. This is a local approximate geographic conversion, not a surveyed coordinate reference system. Record any comparison projection and transform explicitly.
- Preserve object parenting and world matrices when moving geometry between collections. Inspect evaluated geometry, modifiers, roofs, and collection instance transforms before measuring.
- Keep dependencies portable. Pack textures or use project-relative paths. Do not introduce external absolute asset paths or Python auto-run dependencies.
- Compare identifiable structural walls with a suitable footprint. Decorative overhangs, steps, landscaping, and plazas are not wall footprints. Do not rescale an entire building to fit a bounding box unless independent evidence supports that geometry change.
- Evidence must include source URL, provider, feature identifier, retrieval date, source CRS, relevant source date if available, measurement method, and uncertainty. Preserve the raw source snapshot. Check that a polygon represents the correct building, including wings, additions, and interior courtyards.
- Verify position, plan dimensions, orientation, and height separately. GIS footprint agreement cannot verify height, roof shape, facade details, or an interior. Story-count estimates remain estimates. Do not label them measured heights.
- An unchanged original model is not verified. Record unavailable evidence as `unverified`; explain ambiguous source matches rather than guessing.
- Save and reopen the individual asset. For an existing detailed building, preserve its local coordinate frame and make placement changes on its master marker. Include before/after measurements and a list of geometry edits in the evidence record.

## Master review agent

Review every manifest asset, including unnamed massing and residential buildings. Keep one review row per stable building ID. At minimum record source match, position error in meters, orientation difference in degrees, footprint comparison method and result, length/width evidence, height evidence, action taken, and unresolved uncertainty.

1. Confirm manifest coverage: no source building objects lost, multiply assigned, or silently left in environment collections. Inspect shared structures, duplicates, and unrecognized names manually.
2. Confirm every file opens and exports the expected collection. Detailed building collections must be local-coordinate instances at their manifest origin; simple massing collections retain campus coordinates and link directly. All library paths must be relative to the project.
3. Inspect source matching before accepting metrics. Nearest-neighbor location alone cannot establish identity. Record ambiguous and unmatched buildings individually.
4. Review geometry comparisons with top-down overlays. For rotation and footprint shape, use structural geometry rather than the aggregate bounding box of windows, trees, stairs, or signs. Distinguish a translation correction from an actual dimensional correction.
5. Check neighboring buildings, roads, and courtyards after changes. A source may be outdated; resolve conflicting evidence explicitly.
6. Track each criterion as verified within a stated tolerance, corrected and rechecked, estimated, unverified, or source conflict. A partially verified building must retain that limitation in the final report.
7. Reload the complete master and inspect overview plus affected close views. Confirm no missing links, duplicated buildings, changed origin, or displaced environment. A detailed building's campus position is controlled by its `Placement_<id>` marker.
8. Publish coverage totals and remaining exceptions. Claim all buildings fully accurate only if every applicable dimension and placement criterion has sufficient evidence and passes its documented tolerance. Otherwise report exactly what was checked and what remains uncertain.

Do not use the legacy sector fidelity percentages as evidence: `audit_all_30_sectors.py` assigns those scores from mesh density, without comparison to geography.


## Commit completed building work

After a building is finished and its evidence is complete, commit the changed files for that building. Keep the commit limited to that building's assigned files, and follow the root TODO.md handoff rule when the work needs integration into the master blend.
