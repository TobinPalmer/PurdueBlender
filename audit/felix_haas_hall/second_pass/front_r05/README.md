# Haas front revision r05 — October 31, 2026

User-requested rework of the front brick accents and related exterior details. This is a new candidate, opened for the user before its independent review. It is not accepted at9.9 and is not integrated into the campus master.

Exact saved SHA256: `0acacaa642066f5c426dff246ceec1d3c1f69902d77048ce769946dfca7bd8de`. The candidate, canonical library and `Felix_Haas_Hall_front_reworked_r05.blend` preview are identical. A fresh-open technical check found no nonmanifold/zero-area meshes, live modifiers, external libraries or unpacked images. Technical checks are not visual acceptance.

## Evidence and discrepancy

The user's front photo and the existing official Purdue Events image show predominantly pale stone with six narrow keyed brick strips, isolated upper brick tablets, shallow red fields above the flank arches and a pale central portal/frieze. R04 instead cut six broad brick panels out of the stone skin. The independent [source audit](reference_audit/README.md) identifies that mechanism and distinguishes visible composition from uncertain metric dimensions. The original photo pixels, provenance and enlargement limits are retained; crops are not extra independent views.

R04's [historical independent review](../review_r04/README.md),7.95/10, was recovered from `codex/physics-exterior-second-pass` with its exact-file hash. R04 remains historical; its grade does not apply to this revision. The primary supplied front and April2026 west/northwest photographs are in `../sources/`, with the existing source index. An attempted larger Events CDN photo and a Statistics newsletter returned403; `additional_sources.json` records these failures, and neither was treated as inspected evidence.

## Changes

- Replace broad upper/lower brick panels with continuous narrow keyed lower strips, small upper tablets, shaped flank spandrels and larger pale stone fields. Preserve opening heights pending matched-perspective evidence rather than changing dimensions from an oblique pixel ratio.
- Add head/sill molding layers and small sill supports. Preserve the independent audit's caution that exact linked cornice profiles still require comparison.
- Add dark recessed glazing above the low oak door inside the portal, retaining its deep stone reveals. Fine door/transom pane count remains uncertain at the source resolution.
- Move the close paired front handrails off the outer cheeks, following the supplied photo. Their dimensions/offset are estimates.
- Reproportion west basement windows and deepen/divide the rear transom using the April2026 close view. Exact leaf/hardware details remain estimated.
- Replace XY roof masonry mapping with elevation-aligned horizontal tile courses, small modeled tile-lap edges and hip/ridge caps. No speculative historical roof penetrations were added.
- Add subtle variation to reflective glazing without invented image textures. Materials remain uncalibrated visual estimates, not measured reflectance.

## Validation and limits

`geometry_input.json` records the source polygon, fixed manifest origin, facade/opening schedule and construction geometry. `mesh_validation.json` records build checks. `reopen_validation.json` was generated after reopening the saved candidate without saving it. Existing hidden schematic interiors retain589 objects in a recovery archive and were not redesigned. All exterior geometry was newly generated; the previous library supplies only the hidden interior archive.

Fourteen neutral daylight renders include four principal elevations, two obliques, roof, window/front/rear details and three low perspective views. `render_settings.json` identifies the exact file and cameras. Comparisons are approximate because the source camera calibration and metric facade dimensions are unknown. The south, pavilion returns and some east/north openings remain incompletely observed; sculptural/incised frieze details and tiny pane profiles remain uncertain. No claim of complete coverage is made.

The October31 workflow is a full independent review, application of its findings, a shorter independent review, application of those findings, and human-review marking. Below9.9 stays unaccepted. The latest direct user request reopens Haas despite its prior-work exclusion from the remaining-building queue. No other building or the Tobin-owned master is edited.
