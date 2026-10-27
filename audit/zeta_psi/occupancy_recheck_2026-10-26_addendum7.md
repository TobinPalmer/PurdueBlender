# Current Tau Gamma status and address recheck — 2026-10-26

**Review date:** 2026-10-26 (America/Indiana/Indianapolis)  
**Question:** Do new primary Zeta Psi sources establish a current Tau Gamma residence or support assigning a defensible Purdue building FID/footprint?  
**Disposition:** No. Recent fraternity publications and award pages confirm ongoing Tau Gamma student affiliation, but do not name a residence. The Spring 2025 magazine classified Tau Gamma/Purdue as a provisional chapter with seven members (all seven reported as associates) as of April 1, 2025, and described it as a new Interest Group. The newer 2026 issue does not name Tau Gamma in its short lists of provisional and interest groups, but does not state the group’s status or whether those lists are exhaustive. An August 2026 award page and October 2026 fraternity post list Tau Gamma members, confirming current affiliation without establishing housing. The best current conclusion remains: no defensible current Zeta Psi building crosswalk.

## New primary status evidence

Zeta Psi’s *The Circle*, Spring 2025 issue (published July 3, 2025), says its chapter statistics reflect MyZete data as of April 1, 2025. Under the “PROVISIONAL CHAPTERS” heading, it lists “TΓ TAU GAMMA CHAPTER — Purdue University — T 7, F n/a, S n/a, A 7.” Its expansion story also calls Tau Gamma/Purdue one of the fraternity’s “new Interest Group[s].” This is direct evidence that the group existed at Purdue with seven reported associates at that time. It is not evidence of a house or exact address. The relevant browser-captured excerpt is `sources/zeta_psi_circle_spring_2025_tau_gamma_excerpt_2026-10-26.txt`.

The fraternity’s digital *The Circle* issue published August 3, 2026 labels its cover “Summer 2026 Edition” and page 5 “Spring 2026 Edition.” Its page 4 status box names provisional groups and interest groups but does not include Tau Gamma. The issue does not state that the lists are exhaustive or explicitly classify Tau Gamma, so its omission cannot establish either rechartering or inactivity. It also provides no residence address. This nuance is preserved in `sources/zeta_psi_circle_2026_tau_gamma_status_excerpt_2026-10-26.txt`.

Two newer fraternity sources confirm Tau Gamma affiliation: Zeta Psi’s August 12, 2026 Convention Awards page lists Sebastian Ramirez, Tau Gamma ’28, as an Outstanding Undergraduate Award recipient; its October 20, 2026 Flanders Fellows announcement lists Dan Luby as Tau Gamma (Purdue). The current online collegiate directory also includes Tau Gamma, but the page is labeled “Collegiate Archives” and supplies no address. Raw HTML snapshots are retained under `sources/` and indexed in `source_register.json`. These sources establish a continuing student connection; none is an occupancy or property source.

## Address leads re-evaluated

- **237 South Grant Street:** The Columbia Alpha Chapter’s undated chapter roll lists this as Tau Gamma’s house. The page itself says inactive chapters remain listed and invites corrections. The official Tau Gamma report published in 2023 says the chapter moved its house during 2022 but omits the destination. The crosswalk to 237 resolves to a county parcel with zero improvement valuation, no Purdue BuildingShapes feature, no Indiana footprint-layer feature, and served imagery showing parking; the imagery date is unavailable. This address is best treated as historical/stale, not as a current building.
- **950 David Ross Road / Purdue GIS FID 748:** Purdue GIS identifies the physical site as “Zeta Psi,” but the Zeta Psi local social profile’s exact-address bio has no update date. Chi Psi’s official July 2024 newsletter identifies the pictured building at 950 as its new lodge and announces its planned opening. Current national lists confirm both organizations are affiliated at Purdue, but none of the newly reviewed sources explains whether Tau Gamma later used, shared, or left 950. The 2024 Chi Psi source does not alone prove exclusive occupancy through 2026.

The Spring 2025 “new Interest Group” framing makes it especially unsafe to treat older address directories or an undated social bio as proof of present house occupancy. Neither address can presently be assigned to Tau Gamma with adequate confidence.

## Building and model decision

There is no defensible current Zeta Psi building FID or footprint to use for a new or corrected Tau Gamma model. Keep the existing `massing_house_301841600_c1351aa` / FID 748 association as an unresolved spatial candidate only; do not assert that it is Tau Gamma’s current house. The 237 S Grant parcel is not a supported current building candidate. Independently, neither site has sufficient identity, structural-perimeter, height, roof, and facade evidence for a passing model grade.

No geometry, asset, manifest, shared tracker, or campus master was edited.
