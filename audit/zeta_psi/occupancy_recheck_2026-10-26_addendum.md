# Zeta Psi / Chi Psi current-address recheck — second pass

**Review date:** 2026-10-26 (America/Indiana/Indianapolis)  
**Scope:** Current Tau Gamma / Zeta Psi physical facility and the conflicting Chi Psi Lodge claim at 950 David Ross Road.  
**Disposition:** FID 748 is a strong spatial candidate for a building at 950 David Ross Road, but exclusive current chapter occupancy remains unresolved. Do not create another asset or treat `massing_house_301841600_c1351aa` as an independently verified Zeta Psi completion.

## New current local-source evidence

Purdue's current IFC roster (`sources/purdue_ifc_current_chapters.html`, page footer last modified August 26, 2026) lists both **Chi Psi** and **Zeta Psi** and links their respective chapter Instagram accounts. It links Zeta Psi to `@zetapsipurdue` and Chi Psi to `@purduechipsi`.

A direct profile snapshot retrieved from Instagram on October 26 local time (HTTP Date: October 27, 2026 UTC) shows the Zeta Psi-linked Tau Gamma account's bio as:

> “950 David Ross Rd” — “Est. 1968 - Rechartered 2024”

The profile is titled “The Tau Gamma Chapter at Purdue University.” This is current first-party chapter self-report of **950 David Ross Road**, stronger than the older undated/stale address listings. Raw response: `sources/zetapsipurdue_instagram_profile_2026-10-26.html`.

The same direct capture of Purdue's Chi Psi-linked profile (`@purduechipsi`) identifies “Chi Psi Purdue,” “Alpha Epsilon Tau,” and “est. 2023,” but gives no street address in its bio. Raw response: `sources/purduechipsi_instagram_profile_2026-10-26.html`.

## Conflict and crosswalk

Chi Psi's own July 2024 Alpha Epsilon Tau newsletter (`sources/chipsi_alumni_newsletter_summer_2024.pdf`, page 3) identifies the pictured building as “The new Chi Psi Lodge at Purdue University,” lists **950 David Ross Rd**, and announced a September 14, 2024 Lodge opening after the chapter had secured the property and was preparing to move in. This is dated, address-specific evidence of Chi Psi use, and it conflicts with Tau Gamma's current self-reported address at the same street number.

Purdue GIS FID 748 is labeled `Zeta Psi` with address `950 David Ross Rd` in `sources/purdue_gis_FID748_2026-10-26.json`. The building candidate is on Tippecanoe County parcel `79-06-13-476-005.000-029`; the 2018 Indiana LiDAR footprint comparison in `footprint_comparison.json` strongly matches the physical building. The current evidence therefore supports **FID 748 → the physical structure at 950 David Ross Road** spatially. It does not explain how the same address is associated with both active chapters. The prior parcel/LiDAR review finds only one mapped building footprint on this 950 parcel, so two separately mapped chapter houses at that address are not supported.

A search-indexed chapter-run complete chapter list hosted by Columbia's Alpha Chapter gives Tau Gamma a different address, **237 South Grant Street**. The host returned HTTP 403 when I attempted to preserve it, and the listing's date/currency is unclear. Because it conflicts with the newer Purdue-linked chapter profile and the prior 2020-recognized Zeta Psi alumni bio that described a move from Grant Street to a then-current David Ross house, do not use 237 South Grant as a current facility or GIS match without a dated confirmation. The official Tau Gamma 2023 chapter report says it moved its house “this year” (report dated May 15, 2023; see `sources/zetapsi_tau_gamma_2023_chapter_report.pdf`) but does not state either the vacated or new address.

## Finding and exact missing evidence

The new current Tau Gamma bio makes **950 David Ross Road / FID 748** the best current address and GIS candidate for coordinator review. It is not enough to assign exclusive physical occupancy because Chi Psi has its own dated address-specific Lodge announcement at that same sole mapped building, and Tau Gamma's report records a house move in 2022/2023 without giving the destination. The chapters' current social profiles confirm both identities remain active but do not explain the shared address.

The exact missing source is a dated statement from Purdue FSCL, the Tau Gamma chapter/Indiana Association of Zeta Psi, or Chi Psi's Alpha Epsilon Tau House Corporation that clarifies whether: (a) both chapters share the 950 facility, (b) one chapter left after the September 2024 Lodge opening, with the other remaining, or (c) the Tau Gamma Instagram bio or Chi Psi newsletter address is stale and identifies the actual current address. If Zeta Psi moved to a different property, the source must give its street address; then match that address to a current parcel/building footprint before assigning a new FID or asset.

No asset geometry or shared tracker file was edited. No duplicate building asset was created.

## Source/provenance notes

- Purdue IFC roster URL: https://www.purdue.edu/fscl/councils/ifc/chapters.php — Purdue University, roster page; last-modified footer August 26, 2026; snapshot `sources/purdue_ifc_current_chapters.html`.
- Tau Gamma account URL: https://www.instagram.com/zetapsipurdue/ — first-party chapter profile linked from the Purdue IFC roster; raw response captured October 26 local / October 27 UTC.
- Chi Psi account URL: https://www.instagram.com/purduechipsi/ — first-party chapter profile linked from the Purdue IFC roster; raw response captured October 26 local / October 27 UTC.
- Chi Psi newsletter URL: https://chipsi.org/wp-content/uploads/2025/07/Chi-Psi-Alumni-Newsletter-Summer-2024-1.pdf — source publication date July 17, 2024; page 3; raw PDF and rendered evidence already preserved.
- Zeta Psi report URL: https://zetapsi.org/wp-content/uploads/2023/05/ZetaPsi-Circle-FAR-5.15.23-1.pdf — source date May 15, 2023; p. 10; raw PDF already preserved.
- GIS FID: 748 (`BUILDING_N=Zeta Psi`, `ADDRESS=950 David Ross Rd`); source layer metadata is already preserved under `sources/purdue_gis_buildings_metadata_2026-10-26.json`.
- Map comparison CRS/conversion, metrics, parcel identifier, and limitations are recorded in `footprint_comparison.json` and `crosswalk_resolution.md`; no new geometry measurements were made in this pass.