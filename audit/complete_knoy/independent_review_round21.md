# Knoy Hall — Independent R21 Full-Building Review

**Review date:** 2026-10-24  
**Asset:** `modular/buildings/knoy_hall.blend`  
**Grade:** **7.8/10 — below the 8.0 threshold.**  
**Scope:** Read-only review of the saved R21 asset, round-21 evidence and validation, retained 2019 emergency-plan PDF, R20 independent review/scorecard, and current exterior and cutaway renders. No Knoy, master, or shared files were edited.

## Scorecard

The established six-category rubric allocates two points to each of the first five categories and one point to technical/evidence quality. R21 remains **8.6/11 = 7.8/10** after normalization.

| Category | Score | Assessment |
|---|---:|---|
| Identity and footprint | 1.7/2 | Purdue GIS/campus context and the existing stepped plan support the building identity and footprint. The local conversion is approximate rather than survey control; R21 adds no footprint evidence. |
| Placement, orientation, and scale | 1.6/2 | Prior placement evidence remains applicable. R21 has no transform or master-placement change and supplies no survey control. |
| Height, floors, and roof | 1.2/2 | No new measured height, elevation, roof plan, or source resolving the L5 and 48-foot GIS discrepancy was added. R21 changes no geometry. |
| Exterior and entrances | 1.4/2 | The existing archive photo and Street View evidence support brick-heavy masses and interrupted horizontal glazing on the pictured faces, but the model retains broad continuous glazing ribbons. R21 adds no face-registered elevation or opening schedule. |
| Interior and circulation | 1.7/2 | The emergency plan confirms distinct lower- and upper-basement shelter areas for different departments and lists room identifiers. This supports the level labels and use references only. It does not locate either area on a plan, identify slab elevations, or establish stairs, elevators, connections, accessibility, or route continuity. The same emergency-plan source was already documented in R14/R15 and cited in R20, so R21 does not add new spatial or circulation confidence. |
| Technical and evidence quality | 1.0/1 | R21 validation reopened the saved asset, found 191 objects and 169 meshes, and reports identical R20/R21 hashes for all mesh geometry and object world matrices. No unpacked external images are reported. |
| **Total** | **8.6/11 = 7.8/10** | **Below target** |

## Emergency-plan check

The retained official Purdue Polytechnic *Knoy Hall Condensed Building Emergency Plan*, revised March 14, 2019, was visually checked. Page 4 lists separate tornado/severe-weather refuge groups: a lower-basement area for Administration, Business Office, CMT, and ECN, and an upper-basement area for CGT, CIT, and SOET. Page 1 lists KNOY G-011 and KNOY 457; those labels are room references, not mapped geometry. Page 3 is a campus assembly-location map, not a building floor plan.

This operational evidence confirms the building uses two named basement zones. It cannot be registered to the single schematic `KNOY_FloorSlab_Basement` object or resolve whether a second modeled slab, basement plan boundaries, or connecting circulation is correct. R21 appropriately leaves the model unchanged. Because this same plan was already part of earlier reviews, the R21 annotation makes the evidence record more explicit but does not raise the full-building grade.

## Remaining evidence limits

- The R20 sightline correction remains internally consistent, but its image is perspective and partly occluded; it does not justify exact window segmentation.
- No measured elevation resolves overall height, the L5 interpretation, roof/penthouse form, or the 48-foot GIS attribute conflict.
- The official emergency plan is not an as-built floor plan. The modeled basement representation and continuity from basement through upper floors remain unverified.
- The model geometry, materials, transforms, and placement are byte-for-byte equivalent at the recorded R20/R21 geometry-and-world-matrix hash level; therefore no architectural fidelity change is demonstrated by R21.

## Decision

R21 is a valid evidence-record update, but its emergency-plan finding does not supply spatial interior or circulation evidence, and the source was already known in earlier rounds. The score remains **7.8/10**, below the requested 8.0 threshold. An authorized as-built plan with basement/floor registration and stair/elevator information, plus a measured elevation or calibrated roof evidence, is needed for a defensible increase.

## Sources and reviewed records

- [Purdue Polytechnic — Knoy Hall Condensed Building Emergency Plan (revised 2019-03-14)](https://polytechnic.purdue.edu/sites/default/files/files/BEP%20March%2015%202019.pdf), especially pp. 1, 3, and 4; retained locally as `BEP_2019.pdf`.
- [Purdue Archives — Knoy Hall historical photo record](https://collections.lib.purdue.edu/campus/buildings/75).
- [Purdue Engineering — 2018 Gateway Formation Study, existing Knoy elevations](https://engineering.purdue.edu/~frosch/Renderings/Gateway/2018-05-31%20MASSING%20STUDIES%20DRAFT%20INCLUDING%20LANDSCAPE.pdf).
- `audit/complete_knoy/evidence_round21.json`, `validation_round21.json`, the R20 report/scorecard, the R20 sightline diagram, and R17 exterior/cutaway renders.
