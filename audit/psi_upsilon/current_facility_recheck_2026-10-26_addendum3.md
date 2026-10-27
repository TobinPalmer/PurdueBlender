# Psi Upsilon / Delta Omicron GIS and chapter-status recheck

**Research date:** 2026-10-26 local time (raw GIS and report capture files record retrieval timestamps)
**Assignment:** Rossen
**Scope:** Fresh Purdue campus building-layer crosscheck and current national-source chapter-status follow-up.

## Verified chapter status

Psi Upsilon's 2025–26 Impact Report identifies Delta Omicron at Purdue as an official Psi Upsilon chapter. It says the chapter's petition was accepted and that the Psi Upsilon Executive Council officiated its installation ceremony on October 18. This resolves the earlier provisional-versus-full-chapter status conflict in favor of full chapter status. The report passage does **not** state the year of October 18; its subsection heading is labeled “Purdue University (2025),” and the report's printed production date is September 24, 2026. Do not describe the ceremony as occurring October 18, 2026 based on this source.

The Impact Report passage reports current chapter activity and membership but gives no house address and makes no claim that Delta Omicron operates a dedicated facility. Chapter recognition and facility identity are separate questions.

## Fresh Purdue GIS crosscheck

A live query of Purdue University's `BuildingShapesZip4` layer 0 searched `BUILDING_N`, `BLDG_ABBR`, and `OWNER` for `PSI`, `UPSILON`, and `OMICRON`. The broad substring results included unrelated Greek properties, including Zeta Psi (FID 748, 950 David Ross Road), but no feature identifies Psi Upsilon / Delta Omicron. Exact request URLs, responses, requested attributes, EPSG:4326 response setting, and retrieval timestamp are in [`purdue_gis_name_crosscheck_2026-10-26.json`](sources/purdue_gis_name_crosscheck_2026-10-26.json).

This is a campus building layer. A non-match cannot exclude a facility outside its coverage, an asset recorded under a different name, or a chapter-operated residence not represented as a Purdue campus building.

## Evidence snapshots

- Psi Upsilon / Foundation, [2025–26 Impact Report](https://embed-rech-01.dialog.cm/psiupsilon/docs/2026_impactreport_9.24.26_1348_singles), printed report page 15, viewer lines 709–710: official chapter acceptance and installation passage; raw page snapshot at [`psi_upsilon_2026_impact_report_live_2026-10-26.html`](sources/psi_upsilon_2026_impact_report_live_2026-10-26.html), with a structured excerpt and source-date caveat in [`psi_upsilon_2026_impact_report_excerpt_2026-10-26.json`](sources/psi_upsilon_2026_impact_report_excerpt_2026-10-26.json).
- Purdue FSCL, [IFC Organizations](https://www.purdue.edu/fscl/councils/ifc/chapters.php), snapshot `purdue_ifc_organizations_live_recheck_2026-10-26.html`.
- Psi Upsilon, [Chapter Roll](https://psiu.org/chapter-roll/), snapshot `psi_upsilon_national_chapter_roll_live_recheck_2026-10-26.html`.
- Delta Omicron, [Purdue chapter website](https://psiupsilonatpurdue.com/), snapshot `psi_upsilon_chapter_site_live_recheck_2026-10-26.html`.

## Modeling decision and blocker

The chapter-status conflict is resolved: Delta Omicron is a full Psi Upsilon chapter. **Facility status remains unverified.** No current dedicated-house address, parcel, authoritative footprint, or independent occupancy confirmation has been identified. The prior leads at 400 Northwestern Avenue and 1198 Third Street remain ruled out in [`current_facility_recheck_2026-10-26_addendum2.md`](current_facility_recheck_2026-10-26_addendum2.md).

No source-backed building/FID can yet be assigned, so no model is justified. Resolve this by finding a current chapter or Purdue FSCL record that confirms whether Delta Omicron operates a dedicated facility and, if so, names its address. Then confirm occupancy and crosswalk the address to a parcel/building footprint before modeling.
