# Zeta Psi / Chi Psi occupancy and evidence sufficiency recheck — 2026-10-26


> **Correction note — 2026-10-27:** Earlier wording in this audit incorrectly attributed a 2022 house move to Tau Gamma. The official May 15, 2023 *Zeta Psi Circle* report lists Tau Gamma / Purdue with “Chapter update not available at press time”; the adjacent “This year we moved our chapter house” paragraph is for Tau Theta / University of Ontario Institute of Technology. Source: `sources/zetapsi_tau_gamma_2023_chapter_report.pdf`, printed p. 9 (PDF page 10); see also `occupancy_recheck_2026-10-27_addendum10.md`. This note records the prior misreading for provenance; it must not be used as evidence.

**Review date:** 2026-10-26 (America/Indiana/Indianapolis)  
**Question:** Do current official chapter listings, current geospatial acquisition records, or other new evidence resolve exclusive occupancy at 950 David Ross Road (Purdue GIS FID 748), or justify a detailed Zeta Psi model?  
**Disposition:** No. The current official directories list both Purdue chapters but do not provide a house address. The strongest dated address-specific source remains Chi Psi’s July 2024 announcement identifying 950 David Ross as its new lodge. Zeta Psi’s exact-address social bio has no dated update; its 2023 report says no Tau Gamma update was available (the nearby move text is for Tau Theta / Ontario Tech). The current geospatial acquisition index points to 2018 data, which is useful for plan footprint comparison but does not establish present occupancy or building height. The exclusive crosswalk and asset sufficiency remain unresolved; no model or grade is justified.

## Current organization listings

The Zeta Psi national collegiate directory currently lists Tau Gamma at Purdue University in West Lafayette. The Purdue IFC roster likewise lists Zeta Psi, while Chi Psi’s national chapter directory lists Purdue’s Alpha Epsilon Tau. None of the three current listings gives a street address or says who occupies 950. The captured Zeta Psi directory’s nearby “Inactive (2025)” text belongs to another chapter, not Tau Gamma. Raw page snapshots are retained as `sources/zeta_psi_national_collegiate_page2_current_2026-10-26.html`, `sources/purdue_ifc_current_chapters_recheck_2026-10-26.html`, and `sources/chi_psi_national_chapters_current_2026-10-26.html`.

These listings confirm present organizational affiliation at Purdue, not a shared or exclusive building arrangement. They do not resolve whether Tau Gamma’s undated 950 bio is current, whether Chi Psi continues at the site after its planned opening, or whether either organization has moved or shares space.

## Geospatial acquisition and model evidence

A point query at the FID 748 coordinate (-86.924604, 40.434486) against the Indiana Geographic Information Office’s statewide 3DEP LiDAR acquisition-date layer intersects `OBJECTID 14469`, tile `in2018_29951885_12`. The returned project year is 2018 and acquisition timestamp converts to 2018-04-20 UTC. The raw query and service metadata are retained at `sources/indiana_lidar_acquisition_fid748_2026-10-26.json` and `sources/indiana_lidar_dates_layer_metadata_2026-10-26.json`.

This date is tile-level metadata, not a site-specific survey date. The layer’s average elevation attribute is an average over the tile and is not a building height measurement. The 2018 footprint remains useful for the existing plan-view comparison: prior evidence reports IoU 0.829 and centroid separation 1.61 m against the candidate shell, versus IoU 0.422 and 6.24 m against the Purdue FID 748 polygon. That comparison does not verify current walls, facade, floors, or roof height. No newer point-cloud capture or elevation evidence for this address was found in the official acquisition-date layer.

## Decision

Keep the assignment spatially associated with the physical candidate while leaving occupant identity unresolved. Do not label FID 748 as exclusively Zeta Psi, and do not build or grade the current massing candidate. A future build decision requires dated evidence tying Tau Gamma to its 2024–26 facility (or confirming a shared arrangement at 950), plus sufficient source-backed perimeter, height, roof, and facade information to meet the project rubric. Existing detailed geometry must not be treated as verified solely because it resembles the 2018 roof-outline proxy.

No geometry, asset, manifest, shared tracker, or campus master was edited. Source register updated with the new snapshots and acquisition query.
