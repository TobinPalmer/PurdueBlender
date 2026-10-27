# Sigma Eta residence identity — fresh research addendum (2026-10-27)

**Scope:** Freshly test whether the earlier 930 N Grant St rush-event location can be tied to Sigma Eta / Sigma Alpha Mu Purdue's leased chapter residence. No direct outreach. No candidate asset or shared index was edited.

## Updated assessment

The new evidence makes a current Purdue chapter-house lease **credible**, and 930 N Grant is a **plausible candidate**, but the address-to-lease crosswalk remains **unverified**. Do not hand the address to a builder as established identity yet.

This is stronger than an event-only record: a public profile belonging to a Sigma Alpha Mu Purdue founding president claims that he negotiated and secured a chapter-house lease, and official SAM Property Management currently lists Purdue among its property-management accounts. Separately, the chapter's official public account used 930 N Grant St as its Aug. 24, 2026 rush-event location, while local property records classify the parcel as residential rental stock. Together these facts support the inference that 930 may be the leased chapter house. None says that the lease or management account is for 930 N Grant St. A rush event can also be held at a rented or borrowed location.

**Identity status:** house lease in Purdue plausibly corroborated; 930 N Grant as the leased/current residence not established. **Footprint handoff:** not justified yet.

## Fresh evidence

| Source | New evidence | Limit |
| --- | --- | --- |
| [Public profile for a Sigma Alpha Mu founding president](https://www.linkedin.com/in/neal-ssingh); structured search-index excerpt saved as `sources/linkedin_sam_purdue_house_lease_search_snapshot_2026-10-27.json` | The profile dates his Sigma Alpha Mu Founding Father and President role from Nov. 2023 to Present, and self-reports that he negotiated and secured a chapter-house lease as membership grew by early 2025. | No address, lease term, current occupant record, or legal lease entity. The claim is self-reported, not a lease record. Direct page retrieval returned HTTP 999; the dated search result excerpt is preserved. |
| [SAM National Properties & Property Management](https://sam.org/fraternity/housing/); fresh raw snapshot `sources/sam_housing_live_2026-10-27.html` | Current page describes SAM Property Management lease agreements with chapters and lists “Purdue – Manage Property.” | Does not publish the managed property address, property entity, or chapter-specific tenancy. |
| [SAM active chapter roll](https://sam.org/fraternity/chapter-roll/); fresh raw snapshot `sources/sam_chapter_roll_live_2026-10-27.html` | Lists Sigma Eta at Purdue as active in SAM's roll. | No housing information. |
| [Purdue IFC roster](https://www.purdue.edu/fscl/councils/ifc/chapters.php); fresh raw snapshot `sources/purdue_ifc_roster_live_2026-10-27.html` | Current Purdue roster lists the organization and links the account `@purdue.sammy`. | No facility address. |
| [Official chapter Instagram profile](https://www.instagram.com/purdue.sammy/); fresh raw snapshot `sources/purdue_sammy_profile_2026-10-27.html` | Bio identifies Sigma Alpha Mu / Sigma Eta, states “Reestablished 2023,” and advertises Fall 2026 rush. This ties the account presenting the 930 address post to current chapter activity. | Bio has no chapter-house address. The Aug. 11, 2026 post still frames 930 N Grant St as the place to join rush, not as a residence. The post snapshot is `sources/purdue_sammy_2026-08-11_post_public_page.html`. |
| [County property parcel query for 930 N Grant St](https://wfs.schneidercorp.com/arcgis/rest/services/TippecanoeCountyIN_WFS/MapServer/58); previously saved `sources/parcels_930_n_grant_2026-10-27.json` | Confirms parcel number 79-07-18-431-002.000-026 and its boundary. | Parcel service exposes no tenant/occupancy field. |
| Fresh [county parcel/permit layer 76 query](https://wfs.schneidercorp.com/arcgis/rest/services/TippecanoeCountyIN_WFS/MapServer/76); raw response `sources/permits_930_n_grant_2026-10-27.json` | Address/parcel match returned a property row with all permit columns (`Completed`, `PermitType`, `IssueDate`, `PermitDetail`, etc.) null. | This produces no permit/occupancy corroboration. It is not evidence that the property has never been occupied or permitted; the layer's permit fields may be unpopulated for the parcel. |
| [Indiana INBiz official business search guidance](https://faqs.in.gov/hc/en-us/articles/360033794752-How-can-I-search-for-a-business); access record `sources/inbiz_sigma_eta_house_corp_search_attempt_2026-10-27.json` | Official guidance identifies INBiz as the public entity-status/address/agent search. The SAM Foundation's [2018 scholarship list](https://celectcdn.s3.amazonaws.com/files/0043/5558/2018_Master_List_Endowed_Scholarships_Undergrad_only__Jan_18_update_.pdf) names the Sigma Eta (Purdue) House Corporation. | INBiz direct requests were blocked with 403 and client-side anti-bot checks; no current entity details were retrieved. The 2018 House Corporation reference is historical and does not tie an entity or property to 930 N Grant. |

## Identity judgment

The crucial missing edge is still **Sigma Eta/SAM lease or occupancy → 930 N Grant St**. The self-reported chapter-president lease claim is meaningful corroboration for a chapter house somewhere in Purdue, but must not be merged with the rush-post address as if it were a single statement. The county record that the parcel is an R1 rental and its historical single-family rental listing support ordinary residential rental use, not the named chapter tenant.

Fresh exact-address and organization-name web searches surfaced no competing Greek-letter chapter claiming 930 N Grant St. That limited search does not prove exclusive use. No new direct source identifies another chapter or confirms SAM occupancy.

## Exact evidence that would resolve it

One dated source explicitly pairing **Sigma Eta / Sigma Alpha Mu (or its house corporation/SAM Property Management) + 930 N Grant St + residential tenancy/use** would establish the crosswalk: a redacted current lease, Purdue FSCL facility roster, current chapter/house-corporation statement, or SAM Property Management property confirmation. A registered/leased-property or rental-inspection record that names both the tenant and address would also resolve it. Until such a crosswalk is found, keep 930 as a probable lead only; no builder handoff.

## Snapshot inventory

- New current-page snapshots: `sources/sam_housing_live_2026-10-27.html`, `sources/sam_chapter_roll_live_2026-10-27.html`, `sources/purdue_ifc_roster_live_2026-10-27.html`, `sources/sam_foundation_programs_live_2026-10-27.html`, and `sources/purdue_sammy_profile_2026-10-27.html`.
- New parcel/permit query: `sources/permits_930_n_grant_2026-10-27.json`.
- New public-index/access snapshots: `sources/linkedin_sam_purdue_house_lease_search_snapshot_2026-10-27.json` and `sources/inbiz_sigma_eta_house_corp_search_attempt_2026-10-27.json`.
- The earlier addendum `identity_challenge_930_n_grant_2026-10-27.md` captures the property-roll excerpt and Zillow listing evidence; this addendum extends it with the lease corroboration and fresh official-page checks.
