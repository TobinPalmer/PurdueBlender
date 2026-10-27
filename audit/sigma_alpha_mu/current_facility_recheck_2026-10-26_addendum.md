# Sigma Alpha Mu / Sigma Eta current-facility recheck addendum

**Research date:** 2026-10-26  
**Assignment:** Rossen — current chapter facility/address and GIS crosswalk  
**Disposition:** facility-management evidence strengthened; address and building identity unresolved. No asset or FID assigned. No people contacted.

## Conclusion

The current official national SAM property page lists **Purdue — Manage Property** under “Current Ownership and Management Accounts.” It explains that SAM Property Management enters a lease agreement with each chapter for its chapter house. This is stronger primary evidence that the Purdue chapter has a SAM-managed housing relationship than the earlier addressless founder statement alone. The page still gives no address, property entity, parcel, or building name. The founder/former president's early-2025 lease claim likewise contains no address and does not establish that a particular lease is current.

No candidate building can be assigned from this evidence. The only surfaced historical SAM address, **172 Littleton St**, is now listed by Purdue as Gemini Cooperative. County GIS returns parcel geometry for that address but has no owner/occupant attribute in the queried public parcel layer. The county permit layer returns no permit detail for the address and no text match for “SIGMA” in its permit detail, notes, or assigned-to fields. The IRS-directory address **1165 W Stadium Ave** has no matching county parcel/permit record and is independently identified by Purdue as Tarkington Residence Hall's mailing address; it is not a supported chapter-house location.

## Current chapter and housing evidence

| Source | Retrieval/context | Result | Snapshot |
| --- | --- | --- | --- |
| [SAM current chapter roll](https://sam.org/fraternity/chapter-roll/) | Retrieved 2026-10-26 | Lists Sigma Eta — Purdue among active recognized chapters. No house address. | `sources/sam_chapter_roll_2026-10-26.html` |
| [SAM National Properties & Property Management](https://sam.org/fraternity/housing/) | Retrieved 2026-10-26; current management list | Lists Purdue — Manage Property. The same page says SAM PM leases chapter houses to chapters. No address or property entity. | `sources/sam_property_management_2026-10-26.html` |
| [Purdue IFC roster](https://www.purdue.edu/fscl/councils/ifc/chapters.php) | Retrieved 2026-10-26 | Lists Sigma Alpha Mu and links the chapter Instagram as `@purdue.sammy`; it provides no website or address. The linked public account could not be fetched by the available web reader, and indexed searches for the handle/posts returned no address-bearing result. | `sources/purdue_ifc_roster_2026-10-26.html` |
| [Sigma Alpha Mu Foundation — 2025–26 grant recipients](https://www.sam-fdn.org/about-programs) | Retrieved 2026-10-26 | Lists Sigma Eta/Purdue in 2025–26 activities, corroborating current chapter activity, but says nothing about housing or location. | No additional local snapshot; live page linked above. |
| [Neal Singh public profile](https://www.linkedin.com/in/neal-ssingh) | Public profile indexed/retrieved 2026-10-26; founder/president role shown as Nov. 2023–Present | Claims that he negotiated and secured a chapter-house lease by early 2025. A personal claim with no property address, lease document, or current-term confirmation. | Prior snapshot/context: `current_facility_recheck_2026-10-26.md` |

## County assessor, parcel, permit, and GIS review

The [Tippecanoe County Assessor GIS information page](https://www.tippecanoe.in.gov/1048/Assessor-GIS) describes the public GIS as a source for property location and physical property information and warns that it is reference data rather than a substitute for a survey. Its public ArcGIS service's [Parcels layer (58)](https://wfs.schneidercorp.com/arcgis/rest/services/TippecanoeCountyIN_WFS/MapServer/58) exposes `Address`, `PIN`, `ParcelID`, and `ParcelNo`, but no owner or occupant field. Its [Permits layer (76)](https://wfs.schneidercorp.com/arcgis/rest/services/TippecanoeCountyIN_WFS/MapServer/76) exposes address and permit descriptors, but no applicant/owner field.

| Query | Result | Local raw response |
| --- | --- | --- |
| Parcels where `Address LIKE '%172 LITTLETON%'` (geometry returned in EPSG:4326) | Two geometry rows, same parcel identifier `79-07-20-155-002.000-026`, PIN `164027000313`, address `172 LITTLETON ST`. This establishes the parcel crosswalk only; it does not establish current SAM occupancy. | `sources/parcels_172_littleton_2026-10-26.json` |
| Parcels where `Address LIKE '%1165%STADIUM%'` | No result. This is consistent with Purdue's Tarkington mailing-address explanation; it does not alone establish why the county parcel address is absent. | `sources/parcels_1165_stadium_2026-10-26.json` |
| Permits where `Address LIKE '%172 LITTLETON%'` | Two rows for the address, but the exposed permit type, issue date, details, notes, and visit date are all null. No useful current construction/occupancy evidence. | `sources/permits_172_littleton_2026-10-26.json` |
| Permits where `Address LIKE '%1165%STADIUM%'` | No result. | `sources/permits_1165_stadium_2026-10-26.json` |
| All permit records where `PermitDetail`, `Notes`, or `AssignedTo` contains `SIGMA` | No result. This search is limited to those exposed public text fields and is not a comprehensive property-owner search. | `sources/permits_sigma_text_search_2026-10-26.json` |

Raw layer metadata snapshots documenting the field lists and spatial reference are `sources/tippecanoe_parcels_layer_58_metadata_2026-10-26.json` and `sources/tippecanoe_permits_layer_76_metadata_2026-10-26.json`.

## Excluded address leads

- **172 Littleton St:** [Alpha Chi Theta's historical page](https://alphachithetas.org/our-story/) says its house there was sold to Sigma Alpha Mu in 1956. Purdue's current [Gemini Cooperative listing](https://boilerlink.purdue.edu/organization/gemini) identifies Gemini at 172 Littleton St. Do not treat the historic sale or parcel as a present Sigma Eta building assignment.
- **1165 W Stadium Ave:** A third-party nonprofit directory lists this as a Sigma Alpha Mu Fraternity mailing address. Purdue identifies 1165 West Stadium Avenue as [Tarkington Residence Hall's mailing address](https://www.housing.purdue.edu/my-housing/options/residence-halls/tarkington.html). Neither source supports chapter occupancy there.

## Modeling decision and next evidence

There is no defensible current street address, parcel, Purdue building FID, or source footprint for Sigma Eta. Do not create a model or attach the chapter to FID 172 or to 1165 W Stadium. The official national page now makes an address-level facility search more promising: locate a current property name/address or property-owning entity in a public SAM, Purdue, county, planning, or chapter source, then verify that address against a current building footprint before modeling. The addressless lease claim cannot be used as a geometric crosswalk.

**CRS and measurement:** County parcel geometry snapshot returned in EPSG:4326. No dimensional measurements were made because no current Sigma Eta candidate was identified. Building footprint, orientation, dimensions, height, floors, roof, and facade remain unverified.

## Additional official GIS cross-check (2026-10-26)

A direct query was run against Purdue Libraries' current public `Purdue/campus/FeatureServer/0` building layer. The query searched `Name`, `ADDRESS`, and `OWNER` for the term `Sigma`, returned geometry in EPSG:4326, and returned zero features. The raw response is saved as `sources/purdue_campus_building_sigma_query_2026-10-26.json`; the layer metadata is saved as `sources/purdue_campus_building_layer_metadata_2026-10-26.json`. The layer metadata identifies the fields queried and its public layer identity. This result confirms that the campus building inventory contains no name/address/owner text identifying Sigma Alpha Mu. It does not rule out an off-campus chapter rental: the service is the Purdue campus inventory, not a Lafayette-wide property or chapter-occupancy registry.

The chapter roll, property-management page, Purdue IFC roster, chapter-affiliated public lease claim, BoilerLink Gemini listing, Tippecanoe parcel/permit review, and this GIS query still produce no defensible present-day Sigma Eta address. No stable building ID, address, parcel, or footprint can be assigned. A model build remains unjustified until a current chapter, property-management, house-corporation, or Purdue source identifies an address or parcel that can be matched to an actual footprint.

## Live primary-source and GIS recheck (2026-10-26)

The current SAM National Properties page was fetched again on 2026-10-26. Its “Current Ownership and Management Accounts” list includes **Purdue — Manage Property**. In the same page, SAM explains that its Property Management subsidiary enters lease agreements with each chapter for the chapter house. This is current, organization-specific support for a Purdue property-management relationship and makes a chapter facility plausible. The entry does not name an address, legal property entity, parcel, building, or occupant; the general lease description does not itself identify which property is managed for Sigma Eta. The page's own `article:modified_time` metadata is 2026-04-21T20:33:10Z. Raw capture: [`sam_property_management_live_recheck_2026-10-26.html`](sources/sam_property_management_live_recheck_2026-10-26.html).

SAM's current undergraduate FAQ says housing varies by campus and that the national property entities support chapters looking for housing. This is general policy, not a Purdue-specific address or occupancy confirmation. Raw capture: [`sam_undergraduate_faq_live_recheck_2026-10-26.html`](sources/sam_undergraduate_faq_live_recheck_2026-10-26.html). Current chapter roll, Purdue IFC roster, and Tippecanoe County's property-records access page were also fetched again; snapshots are [`sam_chapter_roll_live_recheck_2026-10-26.html`](sources/sam_chapter_roll_live_recheck_2026-10-26.html), [`purdue_ifc_roster_live_recheck_2026-10-26.html`](sources/purdue_ifc_roster_live_recheck_2026-10-26.html), and [`tippecanoe_assessor_public_records_live_recheck_2026-10-26.html`](sources/tippecanoe_assessor_public_records_live_recheck_2026-10-26.html). The county page directs the public to Beacon for current assessor records. A direct request to Beacon returned HTTP 403 in this environment; no owner search result is claimed. The attempt and limit are recorded in [`beacon_public_records_access_attempt_2026-10-26.json`](sources/beacon_public_records_access_attempt_2026-10-26.json).

A fresh query of Purdue University's `BuildingShapesZip4` campus layer searched the `BUILDING_N`, `BLDG_ABBR`, `OWNER`, and `ADDRESS` fields for `SIGMA` or `SAM`. It returned 17 substring matches for Sigma, including **Sigma Alpha** at 230 Russell Street and unrelated Sigma fraternities, but none for **Sigma Alpha Mu / Sigma Eta**. The exact query, response, requested attributes, CRS, and retrieval timestamp are recorded in [`purdue_campus_buildings_sigma_live_recheck_2026-10-26.json`](sources/purdue_campus_buildings_sigma_live_recheck_2026-10-26.json). This is the campus building inventory, not a full Tippecanoe County property or chapter-occupancy registry; it cannot exclude an off-campus rental or a property recorded under a different owner/name.

### Updated disposition

The current national source supports a Purdue-specific SAM management account and indicates that the management program concerns chapter-house leases. It still does **not** establish an address-level current facility/occupancy or a parcel crosswalk. The old Littleton and Tarkington mailing-address leads remain excluded. No stable Purdue FID, county parcel, footprint, or asset can be assigned. A source-backed model remains unjustified until an address or property entity is identified and current chapter occupancy can be tied to a specific parcel and footprint.
