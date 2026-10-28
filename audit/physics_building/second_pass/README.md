# Physics Building — second pass started

Rossen queue rank 62. Started 2026-10-28 after the user approved the Haas preview and explicitly directed moving to the next building. This is a research/baseline checkpoint, not a completed exterior revision or a visual acceptance claim.

Stable manifest ID: `physics_building`; asset: `modular/buildings/physics_building_phys_3bf42f3.blend`; export: `Asset_physics_building`; manifest origin: `[20.732372, 300.324127]` metres. Some older evidence uses the legacy massing ID; the current manifest and assignment control. The source baseline was recovered from a local cache only after verifying its SHA-256 against the Git LFS pointer: `7dc4f484c84cb0f7c5e6c5c676cf4d3e0e7fb80f434fe4862c1efd4fb342a7f5`, 476,108 bytes. Fresh Blender reopen found 319 exported objects and no external library or unpacked image dependencies. See `baseline/inspection.json` and `inspect_baseline.py`. The source model, footprint, manifest and campus master have not been revised in this checkpoint.

The old 8.4/10 grade in `../independent_report_r2.md` used the first-pass rubric, including footprint, placement and interiors. It is not a second-pass exterior score. The current second-pass score is null, target 9.9, accepted false.

## Instructions read and synchronization

The coordinator committed the expanded viewpoint requirements, published them on `origin/master` as `67fedb8`, pulled, and reread `AGENT.md` and `modular/AGENTS.md`. Older content remains intact. Physics follows the new viewpoint log requirements. Haas remains saved/pushed as its own user-approved preview with independent review and master-integration gates unresolved; the user's instruction to move on is not recorded as an invented 9.9 or a lower numeric threshold.

## Source-backed discrepancies identified before edits

1. **Northwestern Avenue entrance character:** the official department facade photo and two distinct gallery photographs show three narrow, very tall glass-block bays above the doors, extending through the two lower main-storey zones to the PHYSICS panel. The current model's sign/three-door treatment sits near the bottom with ordinary repeated sash windows above. Reconstruct these tall bays and their brick piers, heads, door hoods and stone sign composition after verifying their correct facade position.
2. **Facade orientation must be checked again:** `../correct_northwestern_front.py` labels GIS vertices 0–2 the avenue frontage. That segment runs approximately northeast–southwest and faces northwest. The map shows Northwestern Avenue running northwest–southeast beside the building's northeast side. The long opposite-direction GIS edges around vertices 9–12 are a candidate for the actual avenue facade. This is a material inconsistency to resolve with matched map/photo viewpoints before moving any entrance geometry. Do not inherit an old facade label as evidence.
3. **Whole-building window grids are unsupported:** the end/corner photo shows a substantial low blank brick volume and a taller section with sparse narrow windows, different from the repeated three-storey grid. Identify each wing, addition and face; do not mirror the avenue windows around the entire GIS ring.
4. **Secondary historic entry:** the official campus-resources photo shows a different arched stone-and-brick portal, large subdivided upper arch, stair piers and lights. This belongs to a distinct part of the building and needs its own correctly located detail study. Night lighting is unsuitable as a calibrated color sample.
5. **Materials, cornices and roof:** study the dark window frames, glass-block color/scale, pale horizontal bands, inset corner/square stone motifs, sign-panel crest details, deep dark eave brackets, and the roof forms of different wings. The prior broad roof and equally repeated belts should not be assumed accurate merely because the GIS footprint fits.

## Initial viewpoint coverage

The machine-readable source index and viewpoint log are in `sources/reference_index.json` and `viewpoint_log.json`. All new browser observations were made 2026-10-28. Photo dimensions, camera heights and distances are estimates only when supported; otherwise unknown. Gallery/map pin coordinates identify the place, not the photographer's exact camera position.

| Area / view type | Available evidence | Remaining search |
| --- | --- | --- |
| Avenue, medium-distance frontal | Official Purdue departmental facade image; Julian Herzog Oct 2016 gallery photograph | Current foliage-free frontal view and independent bay counts matched to the correct GIS edge |
| Avenue entry, close low oblique | Frank Salek Oct 2017 gallery photo; tall glass-block bays, hoods and sign details | Opposite-side oblique, closer crest/door/stone details, current condition |
| Different end/corner, medium low oblique | Yifan Zhang Jul 2018 gallery photo; blank low brick wing, taller sparse-window end, roof and belt profiles | Match exact wing/face in GIS; reverse-corner view and concealed rear |
| Historic arched entry | Official Purdue campus-resources night image | Daytime frontal and both oblique directions; exact face mapping |
| Elevated avenue facade | Sarthak Walia Apr 2024 gallery photograph, taken from across the road near upper-storey level; roof edge, chimneys and facade rows visible | Metric camera position/height remains uncalibrated. Glazing reflections and sunset exposure limit color inference. Seek reverse elevated and full roof/aerial views. |
| Roof / courtyards | Full roof and courtyard coverage not established in this checkpoint | Seek aerial/roof views, courtyard/rear perspectives and multiple distances; record unavailable evidence without inventing hidden details |

Two coordinate-based Google panorama searches returned an Armstrong-area street view and an unrelated interior. They were rejected as Physics exterior evidence. The verified Physics place gallery was used instead. The current limited Google Maps place view reported no Street View imagery at that selection. This is a source-access limitation, not proof that suitable imagery does not exist elsewhere. Several crops or rotations of a single image will not fill the missing coverage.

## Next modeling gate

Resolve the avenue-versus-old-entry face mapping and wing identities, extend the viewpoint/coverage log, compare fresh baseline renders from matched camera positions, then edit only the Physics source, its dedicated builder and this evidence folder. Preserve the exact verified footprint and placement. A new source revision must be saved/reopened and independently visually reviewed before acceptance; no TODO master handoff or completion count is due for this research checkpoint.
