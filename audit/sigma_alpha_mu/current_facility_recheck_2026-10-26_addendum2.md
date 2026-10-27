# Sigma Alpha Mu / Sigma Eta current-facility recheck — addendum 2

**Research date:** 2026-10-26 (America/Indiana/Indianapolis)  
**Assignment:** Rossen — determine whether Sigma Eta has a currently identifiable dedicated house and establish its street address, parcel, and building-footprint crosswalk.  
**Disposition:** no address or building identity found; no GIS feature or model assigned.

## Result

Fresh checks of current national, Purdue, foundation, campus-GIS, and county-parcel sources still do not establish an address for Sigma Eta's facility or identify a building footprint. The evidence supports current chapter activity and a Purdue-specific SAM property-management account. It does not connect that management account to a street address, a property entity, a parcel, or a particular building. Do not model the historical Littleton house or any other candidate from this record.

## Fresh primary-source checks

| Source and provenance | Current result | Limit |
| --- | --- | --- |
| [SAM active chapter roll](https://sam.org/fraternity/chapter-roll/), Sigma Alpha Mu; fetched 2026-10-26; raw snapshot `sources/live_sam_chapter_roll_2026-10-26.html` | Lists Sigma Eta — Purdue in its active chapter roll. | No facility or address information. The page also says its roll records chapter location by school and does not imply university recognition. |
| [SAM National Properties & Property Management](https://sam.org/fraternity/housing/), Sigma Alpha Mu; fetched 2026-10-26; page metadata says published 2020-02-26 and modified 2026-04-21; raw snapshot `sources/live_sam_property_management_2026-10-26.html` | Lists “Purdue — Manage Property” under current ownership and management accounts. Its general description says SAM Property Management leases chapter houses to chapters. This supports a Purdue-specific management relationship. | Gives no street address, property legal entity, parcel, or current occupancy. It cannot identify the physical property for GIS matching. |
| [SAM Sigma Eta chapter page](https://sam.org/chapter/sigma-eta-purdue-university/), Sigma Alpha Mu; fetched 2026-10-26; page metadata says published 2023-08-22 and modified 2023-08-23; raw snapshot `sources/live_sam_sigma_eta_profile_2026-10-26.html` | Calls Sigma Eta an “Interest Group.” | This page is stale since August 2023 and conflicts with the newer active-roll listing. Treat it as old status language, not evidence of present status or housing. It gives no house address. |
| [Purdue IFC Organizations roster](https://www.purdue.edu/fscl/councils/ifc/chapters.php), Purdue University; fetched 2026-10-26; raw snapshot `sources/live_purdue_ifc_roster_2026-10-26.html` | Lists Sigma Alpha Mu and links `@purdue.sammy`. | No chapter website, house address, or building identity. |
| [SAM Foundation 2025–26 grant recipients](https://sam-fdn.celect.org/grant-recipients), Sigma Alpha Mu Foundation; fetched 2026-10-26; raw snapshot `sources/live_sam_foundation_grant_recipients_2026-10-26.html` | Lists Sigma Eta/Purdue participating in Chabad's campus-wide Seder and hosting a booth at its Jewish festival. | Corroborates current chapter activity only; no housing or address information. |
| [Purdue FSCL assessment and semester reports](https://www.purdue.edu/fscl/resources/reports.php), Purdue University; fetched 2026-10-26; raw snapshot `sources/live_purdue_fscl_assessment_reports_2026-10-26.html` | Spring 2026 summary states that 64 FSCL organizations maintain privately owned or leased residential facilities. | The public page has no organization-level facility table. The aggregate count cannot be used to assign a house to Sigma Eta. It directs readers to request the full report; no request was sent. |

## Fresh GIS and parcel searches

1. **Purdue campus BuildingShapes layer:** queried the current official layer 0 for exact name/abbreviation/owner text matches containing `SIGMA ALPHA MU`, `SIGMA ETA`, or `SAM`; requested FID, building name, abbreviation, address, owner, polygon geometry, and EPSG:4326 output. Result: **0 features**. Raw response: `sources/purdue_sigma_eta_exact_query_live_2026-10-26.json`. The query can only test the campus building inventory; it is not a complete off-campus rental or occupancy registry.
2. **Tippecanoe County public Parcels layer 58:** queried the current county parcel service for parcel address text containing `SIGMA ETA` or `SIGMA ALPHA MU`; requested all exposed fields, geometry, and EPSG:4326 output. Result: **0 features**. Raw response: `sources/tippecanoe_sigma_address_search_live_2026-10-26.json`. The layer exposes parcel identifiers, address, and assessment fields but no owner/occupant field. A chapter with a normal street address would not be found by a fraternity-name address query, so this is not evidence that no Sigma Eta parcel or lease exists.

Neither search yields an address or a footprint to crosswalk. The earlier address-based check for the historic 172 Littleton location remains limited to that parcel and does not establish present occupancy.

## Updated disposition

- **Chapter activity:** supported by the current SAM roll, current Purdue IFC roster, and the Foundation's 2025–26 chapter activity listing.
- **Purdue property-management relationship:** supported by SAM's page, whose page metadata reports an April 21, 2026 modification and which lists Purdue under its current management accounts.
- **Dedicated current house:** plausible from the management account and SAM's general lease description, but not tied to an identified current property or confirmed occupant by address-level evidence.
- **Address, parcel, and building footprint:** unresolved. No suitable address or parcel can be assigned from the new or prior sources.
- **Model decision:** no new asset or FID. Building identity and footprint remain insufficiently supported; do not infer a model from chapter membership, a general management account, or a stale historical address.

## Source/query metadata

The live webpages are source snapshots retrieved on 2026-10-26. The Purdue GIS and county parcel responses preserve the complete raw JSON response, including the query result, source fields, and returned spatial-reference information. The campus query requested EPSG:4326. The parcel layer's native spatial reference is EPSG:2245 (latest WKID 2966); the response was requested in EPSG:4326. These conversions describe source geometry only; no candidate building was selected or measured.
