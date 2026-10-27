# Zeta Psi / Chi Psi occupancy recheck — fourth pass


> **Correction note — 2026-10-27:** Earlier wording in this audit incorrectly attributed a 2022 house move to Tau Gamma. The official May 15, 2023 *Zeta Psi Circle* report lists Tau Gamma / Purdue with “Chapter update not available at press time”; the adjacent “This year we moved our chapter house” paragraph is for Tau Theta / University of Ontario Institute of Technology. Source: `sources/zetapsi_tau_gamma_2023_chapter_report.pdf`, printed p. 9 (PDF page 10); see also `occupancy_recheck_2026-10-27_addendum10.md`. This note records the prior misreading for provenance; it must not be used as evidence.

**Review date:** 2026-10-26 (America/Indiana/Indianapolis)  
**Question:** Does newly found Zeta Psi evidence resolve occupancy or identity at 950 David Ross Road (Purdue GIS FID 748)?  
**Disposition:** No. A Zeta Psi Fraternity profile published for a 2020 honoree says Tau Gamma's “current home” was on David Ross Road, supporting a historical connection to the road. It gives no house number and predates the 2023 report, which provides no Tau Gamma housing update, and Chi Psi's documented 2024 lodge-opening announcement for 950. The evidence does not resolve which group occupied 950 in 2024–25 or 2025–26, whether the groups shared the property, or whether Tau Gamma later moved elsewhere. Keep the crosswalk spatial only and do not build or grade the assigned Zeta Psi model yet.

## New primary-source evidence

Zeta Psi Fraternity's official [40 Under 40 profile for Zach Ruyle](https://zetapsi.org/alumni/40-under-40/recipient/zach-ruyle/) labels the honoree “Tau Gamma, 2009 — Recognized in: 2020” and says he helped lead the chapter's transition from Grant Street to its “current home on David Ross Road.” The page was retrieved on 2026-10-26 and its HTML snapshot is `sources/zeta_psi_zach_ruyle_40_under_40_recheck_2026-10-26.html`.

This makes it more likely that Tau Gamma's historical David Ross Road home was an actual chapter facility, not merely an unsubstantiated social-profile address. However, the profile describes a transition associated with the 2009 alumnus and was recognized in 2020; “current” is relative to that profile, not a current-occupancy statement. The road has multiple addresses, so the page cannot crosswalk the historic facility to FID 748/950. It also does not resolve the address conflict; Tau Gamma's entry in the official 2023 report says no update was available, while the adjacent move paragraph concerns Tau Theta / Ontario Tech.

## Identity and geometry status

- **Stable physical site:** Purdue GIS FID 748 and Tippecanoe County parcel GIS identify the physical address as 950 David Ross Road. The 2018 Indiana LiDAR outline spatially matches the existing massing shell (IoU 0.829; centroid separation 1.61 m), while the shell matches the Purdue FID 748 polygon less closely (IoU 0.422; centroid separation 6.24 m). The LiDAR source is dated and may represent a roof outline; it does not settle structural wall geometry. See `crosswalk_resolution.md` and `footprint_comparison.json` for the reproducible comparison and projection limitations.
- **Historical Zeta Psi identity:** The new 2020 profile supports a Tau Gamma facility somewhere on David Ross Road. The Purdue-linked Tau Gamma profile captured on 2026-10-26 self-reports the exact 950 address, but its bio has no update date. Zeta Psi's 2023 report says no Tau Gamma update was available; it gives no move or destination information.
- **Chi Psi identity:** Chi Psi's official July 2024 newsletter calls the pictured structure at 950 David Ross Road its new Lodge and announces a September 2024 opening ceremony, with move-in expected in the coming months. This directly associates Chi Psi with the physical site but does not independently verify continuous or exclusive occupancy after opening.
- **Current arrangement:** Purdue currently lists both chapters. The FY2025 Indiana Association of Zeta Psi IRS return reports a Purdue student-housing program but gives no facility address. Chi Psi's 2024–25 and 2025–26 national fee schedules classify its Purdue Alpha as rental housing but likewise give no address. These facts remain consistent with co-occupancy, leasing, stale/still-associated addresses, or distinct facilities; the sources do not distinguish among them.

## Build decision

The physical candidate and broad historical location are better supported than before, but the Zeta Psi assignment still cannot be tied uniquely to FID 748. A neutral physical model would avoid a false exclusive occupant label, yet the project assignment is specifically Zeta Psi and the current asset's roof/footprint, facade coverage, and height evidence remain inadequate for the required independent pass. A model build is therefore **not justified**. Keep stable ID `massing_house_301841600_c1351aa` and path `modular/buildings/massing_house_301841600_c1351aa.blend` unchanged pending dated evidence that identifies Tau Gamma's 2024–26 facility or explicitly confirms a shared arrangement at 950, plus sufficient exterior/vertical evidence to meet the grading rubric.

No person was contacted. No building geometry, asset, manifest, shared tracker, or campus master was edited.
