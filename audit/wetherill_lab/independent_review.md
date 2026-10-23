# Independent second-pass review — Wetherill Laboratory of Chemistry

**Reviewed:** 2026-10-23  
**Asset:** [modular/buildings/wetherill_laboratory_of_chemistry.blend](../../modular/buildings/wetherill_laboratory_of_chemistry.blend)  
**Independent current score:** **8.3 / 10 overall**  
**Visual/reference fidelity:** **8.0 / 10**  
**Standalone file integrity:** **10 / 10**  
**9/10 integration gate:** **Not met yet.**

The revision makes clear progress: the Commons sculpture now has the documented 20-foot width and a branching caffeine topology; roof equipment varies in size and type; the façade has a larger limestone entrance composition; and the cutaway is brighter and readable. The work remains below 9 because some of the new façade details are occluded or too pale to read, and the Commons/roof render still leaves major visual content generic. I am not deducting visual points for unmeasured eave height or unknown room dimensions; those remain appropriately marked as estimates.

## Independent checks performed

- Inspected the revised exterior hero, entrance detail, and interior Commons cutaway alongside the stored Purdue exterior and Commons reference photos.
- Reopened the saved asset in a fresh Blender 5.2.3 background process using reopen_verify.py. **PASS:** expected scene and export collection; 339 objects (331 meshes); 21 materials; no unassigned mesh materials, external images, linked libraries, or missing libraries; zero-location/unit-scale root.
- Rechecked the supplied GIS-wall verification: 14 wall outside-face edges match the saved Purdue WTHR polygon within **0.0000084 m** in the project's converted local coordinates. This validates tracing to that GIS input, not survey precision.
- Confirmed the molecule's fresh-reopen X-span is **6.095999956 m** (the published 20 ft target). Its saved note correctly says hydrogens are omitted and atom positions are stylized.
- Viewed the cited Google Maps satellite tile at the Wetherill location. The revised equipment grouping looks more varied than the previous array, but the imagery date is not exposed and the tile is not a dimensioned roof plan.
- Checked modular/manifest.json read-only: it still names only the original WTHR massing asset. The detailed library's position/replacement in the assembled master therefore remains pending.

## Score breakdown

| Area | Score | Finding |
|---|---:|---|
| GIS footprint and local frame | 1.9 / 2.0 | Excellent match to the 14-edge project-converted GIS polygon and a clean local root. The input conversion is a local approximation, not a surveyed CRS; the master marker has not been verified. |
| Exterior architecture and reference likeness | 2.2 / 3.0 | The entrance portico, pilasters, bases/capitals, cornices, and five inset plaque objects improve the façade. In the renders, their proportions and pale stone contrast still differ from the richly articulated reference; most plaque labels and relief are not legible. Other elevations remain repetitive. |
| Materials and presentation | 0.8 / 1.0 | Procedural materials and brick relief are intact and portable. The exterior still renders with pink/pale brick and almost-white stone; the photo's deeper red-brown brick, warm stone, and dark sash contrast are not quite reproduced. The entrance close-up is over-bright. |
| Commons and lab interior | 1.5 / 2.0 | The cutaway is much clearer; furniture, cubby wall, café counters, and branching molecule communicate the Commons. The view still reads as a sparse white room, with blank display surfaces and little visual indication of the public-facing café/Nobel display. Lab partition geometry remains a useful schematic. |
| Roof plant and roof presentation | 0.9 / 1.0 | The changed equipment has varied footprints and heights, an improvement over repeated identical boxes. The model's broad blank roof still understates the busy aerial roof field; equipment positions are visual approximations. |
| Standalone structure and dependencies | 1.0 / 1.0 | Fresh reopen succeeds with the full export collection and no external file or library dependencies. |
| **Overall** | **8.3 / 10** | Technically clean and substantially improved, but the visible reference details still need a pass before the 9/10 gate. |

The visual/reference score is **8.0/10** apart from packaging and file-health criteria. No score deduction is assigned for the estimated 16 m eave, five 3.2 m story intervals, or schematic room partitions: their actual measured values are unavailable in the evidence and should remain identified as inferred.

## Concrete fixes still needed for 9/10

### Required visual fixes

1. **Make the chemistry plaque labels and relief visible.** In the current builder, the label text plane is placed at n * 0.205, while the backing box extends outward to n * 0.25 (depth 0.26 m centered at n * 0.12). That puts the label behind the stone backing face. The small relief emblems are also centered at n * 0.24, so most of their thickness intersects that backing. Move the text and raised emblems beyond the face, or build true recessed/engraved plaque geometry; then verify the five titles and motifs in the entrance-detail render. Use the documented motif set: analytical balance; biological rat-and-leaf; inorganic periodic-table section; organic tetrahedron; physical phase diagram/thermodynamics.
2. **Tune the entrance composition and render.** Compare a near-frontal view against the Purdue façade photo. The new limestone frame is strong enough to establish the architectural focus, but it currently reads as bulky stacked bands and pale blocks at close range. Adjust the pier/capital/cornice widths and levels to the reference, keep them clear of adjacent window openings, use lower exposure, and ensure the incised name and panel design remain readable at both detail and hero distances.
3. **Give the Commons wall displays recognizable content.** Keep the view as an explanatory cutaway, but make the current blank panels identify the multimedia/story display and Nobel display/bust feature documented by Purdue. Distinguish the café counter from generic small counters with a service face/equipment and clearer material contrast. The furniture need not claim an exact present-day plan.
4. **Polish the roof composition.** Preserve the newly varied equipment, but frame a roof-focused view against the current aerial and group plant into believable service zones. Avoid claiming precise equipment sizes or exact positions from undated satellite pixels.

### Assembly check, separate from visual score

After the visual fixes, replace the old massing entry in the manifest/master with this detailed library, transfer the saved GIS-derived placement origin, reopen the master, and compare the WTHR placement/neighborhood against the current map. This is not a flaw in the standalone model geometry, but it must pass before calling the integrated campus result complete.

## Evidence and limits

- Purdue's [Leighty Commons page](https://www.chem.purdue.edu/commons/) documents the café, open study lounge, multimedia display, Nobel display, charging cubbies, dry-erase walls, and a **20-foot** caffeine-molecule LED sculpture above the entrance. The sculpture span is now source-backed; exact atom-node positions and Commons furniture placement remain stylized.
- Purdue Archives' [Wetherill records description](https://archives.lib.purdue.edu/repositories/2/resources/1483) documents five chemistry-related designs above the main doors and the red brick/Indiana limestone treatment.
- The Purdue [exterior photograph](https://www.chem.purdue.edu/admissions/admissions/WTHR.JPG) supports the façade materials and strong limestone entrance/pilaster hierarchy. It does not provide measured elevation dimensions.
- The Purdue [July 2014 emergency plan](https://www.chem.purdue.edu/docs/chemsafety/bep/BEPJuly2014.pdf) supports five above-grade floors, not the modeled floor heights.
- The current [Google Maps satellite view](https://www.google.com/maps/place/Wetherill+Laboratory+of+Chemistry/@40.42685,-86.9141,19z/data=!3m1!1e3) supports broad roof and neighborhood context. Its capture date and dimensioned roof measurements are unavailable.
- No current measured exterior elevations or complete current architectural plans were found. Treat height and interior partitions as explicit estimates; they are not necessary corrections for the visual issues listed above.

## Recommendation

**Hold detailed-master integration for this asset until its visual/reference score reaches 9/10.** The size-correct branching molecule, varied roof plant, and revised façade/cutaway are real improvements. First fix the occluded plaque details and improve the entrance and Commons features' contrast/readability; then review new renders against the same sources. Keep all unknown surveyed dimensions labeled as unknown rather than using them to inflate or depress the visual score.

## Independent final review — 2026-10-23

After the final entrance and Commons pass, I rate the saved asset **9.0/10 overall** (8.7/10 visual/reference). The entrance-focused hero makes the building name and five field labels legible; the thinner relief reduces clutter; the separate overview preserves the full silhouette; and four thin cables support the Commons sculpture. Reopen checks pass with 362 objects, 338 meshes, no external image/library dependencies, footprint-ring deviation under 0.000009 m, and a 6.096 m sculpture span.

The Commons remains sparse, the portico is stylized, and the roof has a small equipment cluster on a mostly open surface. Heights, roof positions, and detailed interior layouts remain inferred or schematic. For a modular illustrative campus model, the latest independent review considers the asset at the 9/10 integration threshold. This supersedes earlier recommendations to hold integration.
