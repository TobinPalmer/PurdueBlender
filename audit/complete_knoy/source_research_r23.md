# Knoy Hall — R23 candidate plan source review

**Date:** 2026-10-24  
**Scope:** Verify the provenance of the “Berglund Project Overview and Plans” Scribd lead and compare its purported Knoy drawings with authoritative footprint, floor-height, and photo evidence. Knoy-only; no source model, builder, master, or shared files changed.

## Decision

Do not use the Scribd drawings as Knoy as-built evidence. Their title blocks and project metadata identify a 2019 CGT 462 student project for “Berglund Construction Office” at 126 Venturi Dr, Chesterton, Indiana. Although “Knoy Hall of Technology, 401 Grant St” repeats in the Revit sheet title blocks, that conflicts with the document's project/site identity and is not enough to establish that the drawings document Knoy. Their overall footprint and elevations also conflict strongly with the official GIS outline and Purdue's existing L1–L4 planning elevations. The drawings are therefore rejected for editing the Knoy asset. No measurable, source-backed correction emerged in R23; no geometry changed.

## Candidate source provenance

- **Record:** Scribd document ID `455649939`, [“Berglund Project Overview and Plans”](https://www.scribd.com/document/455649939/document); provider: Scribd; retrieved 2026-10-24. The page reports 24 pages and identifies the uploader as account `api-501278243`, with no primary institutional or owner attribution. Treat the copy as user-uploaded and secondary.
- The drawing sheets name Allison Wolf and Dallas Brown, include a `CGT 462 Project 1` label and Revit timestamps on 2019-12-09. The title page/site material identifies `Berglund Construction Office`, `126 Venturi Dr`, Chesterton, IN 46304, and a project number/date. These are strong signs of a student design exercise rather than a commissioned Knoy as-built drawing set.
- The repeated `Knoy Hall of Technology, 401 Grant St` title-block text creates a superficial Knoy association, but it conflicts with the named Berglund office/site and does not provide a verified Knoy drawing revision, architect, owner, Purdue facility number, archive provenance, or as-built status.

## Measurable conflict check

| Measure | Candidate student sheets | Official/project evidence | Result |
|---|---:|---:|---|
| Overall plan extents | A100-D dimension strings give approximately 101 ft 4 in × 68 ft 10¾ in = 30.89 m × 21.00 m | Project GIS boundary in `build_knoy_hall.py` spans 44.925 m × 93.162 m; shoelace area is 2,632.7 m² | Student plan's bounding rectangle is only about 649 m² and its aspect ratio is 1.47, versus 2.07 for the GIS envelope. It is not the whole Knoy footprint (even before considering that the actual student outline is smaller than its rectangle). |
| Vertical profile | A200 labels T.O. Roof 19 ft 2 in (5.84 m) above first floor; structural sheets show a different low-rise level scheme | Purdue's 2018 Gateway study labels existing Knoy Levels 1–4 at 14 ft 8 in (4.4704 m) floor-to-floor; the retained model follows those intervals to within 0.011 m each | The candidate's one low roof datum cannot represent the documented L1–L4 height stack. Its inconsistent structural and architectural level labels further disqualify it as measured as-built evidence. |
| Exterior composition | Student elevations depict a low, simple project volume | Official Purdue archive items PPBUC01785/01786 show tall stepped brick masses, multiple coping levels and interrupted slit glazing. The R20 Aug 2025 Street View panorama (`37BzxutMJc4KJ68n5M55xw`, camera 40.4281078, -86.9106299, heading 244.316°) shows a tall brick-heavy wall with thin horizontal glazing; the R20 ray only approximates GIS edge 18. | The candidate elevations do not correspond to the historic/current Knoy massing or the observed facade vocabulary. The panorama is qualitative and perspective-based; it does not resolve the model's exact window interruptions. |

The student plan includes a `North` marker, but that only orients the student's proposed sheets; it does not make their geometry applicable to Knoy. No coordinate tie, survey datum, measured control, or relation to Knoy's GIS polygon is supplied.

## Geometry decision and remaining blocker

No change is justified from this source. The existing L1–L4 datums are already supported by Purdue's 2018 planning study; the 2019 Scribd drawings are rejected as a different student-project design. The known Knoy roof/L5/penthouse, exact facade interruption positions, and full basement-to-roof circulation remain unverified because no accessible, provenance-controlled as-built roof plan, oriented elevation set, or multi-level floor plans were found. Purdue Archives UA 141 and UA 62 remain physical archive leads; their finding aids are not drawings themselves.

This pass makes no claim that the source search proves no such records exist. It establishes that the Scribd lead is unsuitable and that the currently accessible sources do not justify an architectural edit. Future measurable changes need owner/architect/Purdue-issued as-built or record drawings with level labels and compass orientation, or imagery that can be calibrated and assigned to a specific GIS facade edge.
