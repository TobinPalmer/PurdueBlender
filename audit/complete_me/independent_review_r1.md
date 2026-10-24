# Mechanical Engineering R1 — Independent Full-Building Review

**Review date:** 2026-10-24  
**Revision reviewed:** R1  
**Asset:** `modular/buildings/mechanical_engineering.blend`  
**Reviewer:** Independent reviewer; did not build or edit R1  
**Score:** **7.0/10**  
**Decision:** Below the project's 8.0/10 acceptance target; continue revision.

## Scorecard

| Criterion | Score | Review |
| --- | ---: | --- |
| Identity and footprint | 1.6/2.0 | Correct Mechanical Engineering identity and Purdue GIS FID 857 envelope. The exact relation of the separate FID 108 shell and five historic wings to the combined model remains unresolved. The saved shell AABB matching the GIS AABB is a useful envelope check, not wall-by-wall registration. |
| Placement and orientation | 1.6/2.0 | Asset root remains at identity and the retained local origin is consistent with the project placement. The fountain-facing entrance direction is supported by Purdue's renovation notice. No read-only master-marker audit was included in R1, and the campus conversion is approximate rather than survey control. |
| Form, height, and roof | 0.7/1.5 | R1 retains the prior 18.5 m top and flat, continuous roof. Purdue describes a five-phase complex; its phase illustration shows a mixture of pitched tile roofs and flat roof areas. R1 gives no wing-specific heights or roof geometry. This is a major accuracy gap. |
| Facade, materials, and entrance | 1.5/2.0 | The 208 applied openings, dark glazing/mullions, sills, horizontal bands, qualitative running-bond brick, and arched stone entrance address clear baseline omissions. The Purdue photographs support these feature types and the general brick/stone character. The repeated four-row window schedule and its mapping to individual wings are estimates; the render presents long, regularly repeated bands without enough source evidence to establish each elevation. The entrance is on the evidence-supported fountain-facing edge, but its midpoint location is an estimate. |
| Interior and circulation | 0.6/1.5 | R1 leaves the existing approximate floor plates and partitions unchanged. The 2015 plans are historical and exclude Gatewood, while Purdue documents mismatched floor levels and multiple connected wings. Current post-renovation stairs, elevators, accessible routes, atrium connections, and room layout are not established by the model or the reviewed floor-plan evidence. |
| Technical integrity | 1.0/1.0 | Reopen validation passes in Blender 5.2.3; the export collection, applied Boolean, root transform, preview files, and lack of external image dependencies are confirmed. No temporary cutters or validation errors are reported. |
| **Total** | **7.0/10** | **Below target** |

## Findings

R1 is a substantial exterior improvement over the 4.5/10 baseline. The chosen entrance direction has documentary support: Purdue says the main entrance faces the Engineering Fountain through Gatewood. Purdue's exterior photographs support the broad brick, dark window, and pale arched-stone vocabulary. R1 also keeps its uncertainties explicit and avoids treating the GIS envelope or perspective photos as a measured elevation.

The rendered model still reads as one continuous, largely uniform mass. Its roof has no supported phase breaks or varied roof forms, despite Purdue's own renovation illustration showing distinct wings and both pitched and flat roof areas. The new window openings use a repeated schedule across long faces, but the evidence package does not register the photos to those faces or verify the opening count, spacing, story alignment, or correspondence to the historic wings. The portal's exact along-wall location is likewise unverified.

The 18.5 m single-height shell and approximate floors/interior partitions do not yet represent the documented five-phase complex and its floor discontinuities. The model lacks verified current circulation through the Gatewood connection and the renovated interior. The full-building hero render also leaves broad roof surfaces and elevation differences visually indistinct; it is useful for checking the overall mass, but it does not resolve those architectural gaps.

## Priority work before a pass

1. Register source photographs or drawings to specific GIS edges before revising the window rhythm, portal position, or wing-to-facade assignment.
2. Obtain evidence that resolves at least the distinct wing heights and roof forms; do not distribute the roof height across the complex by assumption.
3. Reconcile FID 108 with FID 857 and record whether it is a separate structure, connected wing, or overlapping footprint.
4. Add a read-only master check for the placement marker, linked source path, and source-library reload.
5. Represent current circulation and significant interior connections only where post-renovation sources support them; retain historical-plan differences as uncertainty.

## Sources reviewed

- [Purdue 2023 ME renovation notice](https://engineering.purdue.edu/ME/News/2023/me-building-renovation-brings-changes) — main-entrance direction and current entrance context.
- [Purdue 2025 ME history article](https://engineering.purdue.edu/ME/News/2025/purdues-mechanical-engineering-building-represents-more-than-a-century-of-history) — exterior retained during renovation; five-phase complex and Gatewood history.
- [Purdue ME renovation phase illustration](https://engineering.purdue.edu/ME/Giving/Renovation) — qualitative evidence for distinct wings and mixed roof forms; not georeferenced or metric.
- [Purdue ME emergency plan](https://www.purdue.edu/operations/emergency-preparedness/me/) — unequal floor alignment, isolated level segments, and Gatewood/main-wing connections.
- [Wikimedia Commons 2024 facade photo](https://commons.wikimedia.org/wiki/File:Purdue_Mechanical_Engineering_Building.jpg) — dated but not georeferenced; supports broad exterior features, not measurements.
- The model's R1 evidence and validation records, both saved preview renders, and the prior independent R0 review at `audit/complete_me/reviewer.md`.

No model, master, manifest, README, or shared index was changed during this review.
