# Psi Upsilon / Delta Omicron live facility recheck

**Research date:** 2026-10-26 (live pages fetched 2026-10-26 local / 2026-10-27 UTC)
**Assignment:** Rossen
**Scope:** Recheck current chapter identity/status, published address, and Purdue GIS crosswalk. No one was contacted.

## Finding

No current chapter-house address, parcel, Purdue GIS feature ID, or defensible building identity can be assigned from the sources reviewed. This does not establish that Delta Omicron has no facility; public evidence leaves current facility status unverified. A building model is not justified, and there is no proposed stable building ID or asset path to hand to a builder.

## Current primary-source check

- Purdue's live IFC organization roster lists Psi Upsilon as a co-ed organization and links `psiupsilonatpurdue.com` plus the Instagram account `@psiupsilonatpurdu`. The roster gives no street address. Its Sigma Alpha Epsilon Instagram link is visibly mislabelled with the Psi Upsilon handle, so the Psi Upsilon-specific row link was checked directly; no address evidence was taken from Instagram.
- The chapter's live home page has a rush-schedule link, photos, contact form, and alumni email, but no street address, facility statement, or map pin. The schedule's campus event venues are not evidence of a chapter house.
- Psi Upsilon's live national chapter roll lists Delta Omicron at Purdue (2025) and links the chapter site. It gives no facility/address.
- The national site's live “Current & Future Planned Expansion Opportunities” page still lists “Purdue University (Provisional Chapter).” This conflicts with the national chapter roll and the 2025 installation record already saved in the prior audit. Treat that page's status label as stale or inconsistent; it does not establish whether the local chapter has a house.
- The repository's `modular/buildings/target_buildings_gis.json` has no `Psi Upsilon` or `Delta Omicron` entry. The current `modular/manifest.json` likewise provides no chapter identity crosswalk. No address exists to query against Purdue GIS.

## Rejected address leads

- **400 Northwestern Avenue:** prior source review identifies this as Delta Tau Delta's Gamma Lambda chapter house, so it must not be reassigned to Psi Upsilon.
- **1198 Third Street:** Purdue's live events directory and saved Purdue BuildingShapesZip4 feature FID 902 identify Krach Leadership Center (`KRCH`), address 1198 3rd Street, owner `PURDUE`. It is a separate Purdue campus facility, not a Psi Upsilon house. The prior Cause IQ mailing-address hit is not facility evidence.
- The Fall 2024 petition's individual off-campus housing and fundraising for future permanent housing are historical, pre-installation statements, not proof of the chapter's current housing status.

## Evidence snapshots

All four live pages were fetched on 2026-10-26 local time and preserved under this building-specific folder:

| Provider | Page and result | Snapshot |
|---|---|---|
| Purdue FSCL | [IFC Organizations](https://www.purdue.edu/fscl/councils/ifc/chapters.php): Psi Upsilon listed, no address | [`purdue_ifc_organizations_live_recheck_2026-10-26.html`](sources/purdue_ifc_organizations_live_recheck_2026-10-26.html) |
| Delta Omicron | [Psi Upsilon at Purdue](https://psiupsilonatpurdue.com/): no published address or facility claim | [`psi_upsilon_chapter_site_live_recheck_2026-10-26.html`](sources/psi_upsilon_chapter_site_live_recheck_2026-10-26.html) |
| Psi Upsilon Fraternity | [Chapter Roll](https://psiu.org/chapter-roll/): Delta Omicron, Purdue (2025); no address | [`psi_upsilon_national_chapter_roll_live_recheck_2026-10-26.html`](sources/psi_upsilon_national_chapter_roll_live_recheck_2026-10-26.html) |
| Psi Upsilon Fraternity | [Expansion and Growth](https://psiu.org/expansion-and-growth/): calls Purdue provisional, status conflict noted above | [`psi_upsilon_national_expansion_page_live_recheck_2026-10-26.html`](sources/psi_upsilon_national_expansion_page_live_recheck_2026-10-26.html) |

Additional existing snapshots document the [Krach Purdue events listing](sources/purdue_krach_leadership_center_2026-10-26.html), [Purdue GIS FID 902](sources/purdue_krach_gis_fid902_2026-10-26.json), [the 2024 chapter petition](sources/psi_upsilon_delta_omicron_petition_2025-01.pdf), and prior address leads.

## Concrete evidence gap / next step

A current, dated statement from Delta Omicron or Purdue FSCL must say whether the chapter operates a dedicated facility and, if so, give its street address. Then verify occupancy independently and match that address and footprint to a Purdue GIS feature (or an authoritative parcel/footprint if it is off-campus). Until that exists, do not infer a house from member residences, event locations, mailing addresses, or neighboring chapter facilities; do not create or relabel an asset.
