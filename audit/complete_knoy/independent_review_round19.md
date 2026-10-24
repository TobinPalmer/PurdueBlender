# Knoy Hall — Independent R19 Full-Building Review

**Review date:** 2026-10-24  
**Asset:** `modular/buildings/knoy_hall.blend`  
**Grade:** **7.7/10 — below the 8.0 threshold.**  
**Scope:** Reopened saved asset and R19 validation/evidence, inspected the facade-glazing sightline SVG, compared the R17 exterior and entrance renders with the Purdue Archives photograph, and reviewed the cutaway render and prior R18 scorecard. No Knoy, master, or shared project files were changed.

## Scorecard

Scores retain the prior six full-building categories. The first five categories are on a 2-point scale; technical/evidence quality is on a 1-point scale. The 8.5/11 raw score is normalized to 7.7/10.

| Category | Score | Assessment |
|---|---:|---|
| Identity and footprint | 1.7/2 | Purdue GIS and campus context support the identity and stepped footprint. R19 adds a useful candidate-face sightline but the approximate local conversion is not survey control. |
| Placement, orientation, and scale | 1.6/2 | Prior manifest and placement evidence remain applicable. R19 changes no placement or transform and provides no new survey control. |
| Height, floors, and roof | 1.2/2 | The 2018 DSM offers a broad roof-surface check but does not establish roof slab, parapet, L5 occupancy, penthouse geometry, or the conflicting GIS 48-ft attribute. No geometry changed in R19. |
| Exterior and entrances | 1.4/2 | Purdue Archives imagery supports brick-heavy massing with narrow, interrupted glazing bands on photographed faces. The model still renders continuous glazing ribbons across large elevations. R19 appropriately makes no unsupported facade edit, but it adds no visible fidelity improvement. |
| Interior and circulation | 1.7/2 | The cutaway and plan traces show substantial modeled interior organization, doors, fixtures, and stairs. These remain illustrative; R19 located no new digitized as-built circulation plan or stair drawing, and vertical accessible-route continuity remains unverified. |
| Technical and evidence quality | 0.9/1 | Blender 5.2.3 reopened the asset; four facade mesh fingerprints match R18 and there are no unpacked images. R19's evidence package contains an inconsistent camera position and ray intersection between its JSON record and sightline diagram, which needs correction. |
| **Total** | **8.5/11 = 7.7/10** | **Below target** |

## R19 sightline check

The source record and SVG are not internally consistent for the same Street View pano and GIS segment:

- `evidence_round19.json` gives camera XY `[260.38, 78.59]`, intersection `[234.472, 66.136]`, segment parameter `u = 0.69`, and range `28.74 m`.
- `facade_glazing_assignment_r19.svg` plots camera XY `[261.607, 77.251]`, intersection `[235.921, 64.898]`, and says `u ≈ 0.91` and range `~28.5 m`.
- The SVG camera is about 1.82 m from the JSON camera and its plotted intersection is about 1.91 m from the JSON intersection. Each pair is internally consistent with the same approximate heading, but they cannot both represent the same source position and ray.

The evidence narrative should preserve this as an unresolved registration mismatch until the diagram is regenerated from the authoritative JSON input and the corrected values are checked. Even a corrected ray only selects a candidate footprint edge; tree cover, perspective, and partial occlusion still prevent measuring slit count, spacing, or dimensions. No facade changes should be made from this sightline alone.

## Model and evidence findings

The model's large-scale form and technical structure remain stable in R19. The validation confirms all four tracked exterior mesh fingerprints match the R18 baseline, so this revision is evidence-only. The R17 exterior render still shows regular, continuous ribbon glazing and broad brick bands; the official archive image shows a more interrupted, brick-heavy appearance on its visible portions. The photo does not provide a calibrated or georeferenced elevation, so the previous decision not to assign a precise window pattern to a particular model face remains reasonable.

The roof DSM values remain ambiguous, and no current digitized roof or vertical-circulation plan was found. The official archive finding aids identify potentially useful physical drawings/photos, but their catalog records do not verify the geometry. These uncertainties remain material to the score.

## Files reviewed

- `audit/complete_knoy/evidence_round19.json`
- `audit/complete_knoy/validation_round19.json`
- `audit/complete_knoy/facade_glazing_assignment_r19.svg`
- `audit/complete_knoy/knoy_exterior_full_r17.png`
- `audit/complete_knoy/knoy_entrance_facade_r17.png`
- `audit/complete_knoy/reviewer_cutaway.png`
- `audit/complete_knoy/independent_review_round18_scorecard.json`
- `audit/complete_knoy/roof_spatial_check_r18.json`
- Purdue Archives Knoy photo: https://collections.lib.purdue.edu/campus/buildings/75
- Purdue Archives UA 141 finding aid: https://archives.lib.purdue.edu/repositories/2/resources/1490
- Purdue 2018 existing-elevations study: https://engineering.purdue.edu/~frosch/Renderings/Gateway/2018-05-31%20MASSING%20STUDIES%20DRAFT%20INCLUDING%20LANDSCAPE.pdf

R19 does not raise the full-building grade. The model remains below the requested 8.0 threshold; the new evidence should be corrected before it is reused to justify facade edits.
