# Zeta Psi / Chi Psi address recheck


> **Correction note — 2026-10-27:** Earlier wording in this audit incorrectly attributed a 2022 house move to Tau Gamma. The official May 15, 2023 *Zeta Psi Circle* report lists Tau Gamma / Purdue with “Chapter update not available at press time”; the adjacent “This year we moved our chapter house” paragraph is for Tau Theta / University of Ontario Institute of Technology. Source: `sources/zetapsi_tau_gamma_2023_chapter_report.pdf`, printed p. 9 (PDF page 10); see also `occupancy_recheck_2026-10-27_addendum10.md`. This note records the prior misreading for provenance; it must not be used as evidence.

**Review date:** 2026-10-26  
**Building:** Purdue GIS FID 748; stable asset `massing_house_301841600_c1351aa`; 950 David Ross Road  
**Disposition:** Do not edit or grade the asset as a Zeta Psi model. Current evidence ties the physical 950 David Ross building to Chi Psi's Lodge announcement and also shows an undated Tau Gamma self-reported address at 950. Purdue lists both groups as active chapters, but available evidence does not resolve occupancy. Treat FID 748 as an unresolved address conflict, not a confirmed Zeta Psi completion.

## Dated primary-source evidence

1. **Purdue's current IFC chapter roster.** The preserved Purdue page `sources/purdue_ifc_current_chapters.html` is marked “Last modified: August 26, 2026.” It lists both Chi Psi and Zeta Psi and links each to its own Instagram account. It does not list house addresses, so it establishes current chapter presence, not shared occupancy of 950 David Ross.

2. **Chi Psi's address-specific Lodge announcement.** The official Alpha Epsilon Tau newsletter, preserved as `sources/chipsi_alumni_newsletter_summer_2024.pdf`, labels a photo “The new Chi Psi Lodge at Purdue University,” gives “Epsilon Tau Lodge: 950 David Ross Rd,” and announces the Lodge opening ceremony for September 14, 2024. The event text describes the Lodge as newly secured and says the chapter expected to move into it. This is affirmative evidence for Chi Psi Lodge use at the address by fall 2024.

3. **The 2023 report does not establish a Tau Gamma house move.** The official Tau Gamma chapter report, `sources/zetapsi_tau_gamma_2023_chapter_report.pdf` (printed p. 9; PDF page 10), lists Tau Gamma / Purdue and says “Chapter update not available at press time.” The nearby house-move paragraph is under Tau Theta / Ontario Tech. It does not establish whether Tau Gamma vacated, occupied, or shared 950 David Ross.

4. **The Zeta Psi David Ross reference is older.** The official Zeta Psi alumni profile saved as `sources/zetapsi_alumni_david_ross_bio_recheck_2026-10-26.html` says Zach Ruyle helped lead the chapter's move from Grant Street to its then-current home on David Ross Road. The profile identifies him as recognized in 2020; it has no house number and predates the 2023 report, which provides no Tau Gamma housing update. It cannot establish a current Zeta Psi address.

5. **Current official pages add no second Zeta Psi address.** The Zeta Psi Indiana chapter-location page is preserved as `sources/zetapsi_indiana_chapter_page_recheck_2026-10-26.html`; it names Tau Gamma at Purdue without a street address. Chi Psi's current Purdue homepage is preserved as `sources/purduechipsi_official_homepage_recheck_2026-10-26.html` and presents an active Lodge/recruitment operation but no street address. The detailed address evidence remains Chi Psi's 2024 official newsletter.

## Crosswalk finding and action

The spatial match remains as documented in `crosswalk_resolution.md`: FID 748 and its stable asset map to the single structure on the 950 David Ross parcel. The conflict is semantic. Chi Psi's 2024 Lodge-opening announcement associates it with the structure, while Tau Gamma's undated self-reported bio also lists 950. The 2023 Zeta Psi report provides no Tau Gamma housing update and cannot order or resolve these claims. Purdue's August 2026 roster lists both groups as active but does not establish that Zeta Psi shares the property or where it now resides.

Therefore leave `modular/buildings/massing_house_301841600_c1351aa.blend`, its geometry, manifest, README, and shared tracker untouched. Ask the coordinator to reassign this physical asset to Chi Psi/Tobin if the existing Chi Psi assignment is the same building, and keep Rossen's Zeta Psi assignment unresolved until Purdue or Zeta Psi supplies a dated post-2023 address. This finding is not an independent grade and does not count the Rossen assignment as complete.

## Snapshot inventory

Relevant preserved evidence under `sources/`:

- Purdue IFC chapter roster HTML (page footer says last modified August 26, 2026).
- Chi Psi's official Summer 2024 newsletter PDF and page-3 image preview.
- Zeta Psi's official 2023 Tau Gamma chapter report PDF.
- Zeta Psi official 2020-recognized alumni bio and Indiana chapter-location page, both re-fetched on 2026-10-26.
- Chi Psi official Purdue homepage, re-fetched on 2026-10-26, plus the previously saved JavaScript bundle.
- Original crosswalk's Purdue FID 748 query, county parcel query, LiDAR footprint snapshots, and comparison measurements.
