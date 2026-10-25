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
