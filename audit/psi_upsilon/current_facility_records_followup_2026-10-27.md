# Psi Upsilon / Delta Omicron — facility records follow-up (2026-10-27)

## Question and result

Does the installed Delta Omicron Chapter at Purdue have a current, dedicated residential facility with a traceable address and a parcel/building footprint that can be modeled? This records pass did not establish one. No address or property entity was found in the current primary sources checked below. **No building model is justified from the available evidence.** This is an evidence gap, not proof that the chapter has no housing.

## Chapter status versus facility status

The national fraternity’s 2026 Impact Report confirms Delta Omicron’s Purdue petition was accepted and its installation officiated on October 18, 2025 (report’s chapter update; the 2026 report notes this retrospectively). This resolves the former status ambiguity: Delta Omicron is a current installed chapter. It supplies no residence address, property owner, lease, or house claim.

The national fraternity’s Winter 2025 account identifies **648 Bourbon and Cigar Lounge** as the after-dinner venue for installation weekend. That is an event venue and is not evidence of a chapter residence. The earlier 2024 expansion petition says members arranged their own, mostly off-campus housing and that the colony was saving for permanent housing / exploring rentals. That is petition-time context only; it is not a current address or proof that later housing was acquired.

## New records checked

1. **IRS Exempt Organizations Business Master File (Indiana), retrieved 2026-10-27.** The IRS describes its BMF as an extract of exempt organizations, with an Indiana file updated through the IRS page’s latest posting date of 2026-10-13. A filter of the current Indiana CSV for names containing `PSI UPSILON` or the previously suggested local EIN `88-1616239` returns three records: Psi Upsilon Foundation Inc. (Indianapolis), Psi Upsilon Fraternity (Indianapolis), and a separately listed Psi Upsilon Fraternity record (Fort Wayne). No row matches the suggested EIN. No Delta Omicron/Purdue housing entity appears among those hits. The addresses are BMF filing addresses, not property records. Chapters may be covered under a group exemption or absent from the extract, so this does not prove no local entity or facility exists.
   - Source page: https://www.irs.gov/charities-non-profits/exempt-organizations-business-master-file-extract-eo-bmf
   - Downloaded CSV: https://www.irs.gov/pub/irs-soi/eo_in.csv
   - Filtered dated source rows: `sources/irs_eo_bmf_psi_upsilon_matches_2026-10-27.json`

2. **Tippecanoe County GIS parcel layer metadata**, retrieved 2026-10-27 from the county-linked Schneider/ArcGIS Parcels layer (`MapServer/58`). The polygon layer includes parcel identifiers, street address, valuation, and geometry (spatial reference WKID 2245; latest WKID 2966), but no owner/name field. Without an independently established street address or legal entity, it cannot support a parcel crosswalk. Existing audit evidence already records that the known 1198 Third Street lead is Purdue’s Krach Leadership Center (FID 902), and 400 Northwestern is Delta Tau Delta; neither is a Psi Upsilon candidate.
   - Layer: https://wfs.schneidercorp.com/arcgis/rest/services/TippecanoeCountyIN_WFS/MapServer/58
   - Dated metadata snapshot: `sources/tippecanoe_parcel_layer_metadata_2026-10-27.json`

3. **West Lafayette Building Department public reports archive.** The city describes this as an archive of monthly and annual building activity reports and its indexed 2025 folder lists monthly reports through December 2025. The city’s official permit page says permits are issued for new construction and certain structural/electrical work. Direct retrieval of the archive page from this research environment returned HTTP 403, so the underlying report PDFs could not be inspected here. Exact indexed searches for `Psi Upsilon` and `Delta Omicron` with the city’s document domain returned no chapter-specific permit match. Since permits are not a comprehensive residence registry and there is no candidate address to query, this avenue remains inconclusive.
   - Archive: https://www.westlafayette.in.gov/government/building-rental-housing/building-department-reports/-folder-242
   - Permit information: https://www.westlafayette.in.gov/services/permits/building-permits

4. **Indiana Secretary of State entity search.** The official state search is available through INBiz / the Secretary of State portal. Exact web-index searches for Psi Upsilon and Delta Omicron did not surface a local West Lafayette housing association. Direct portal retrieval was denied (HTTP 403), preventing a reliable interactive entity search. This is a source-access limitation, not a negative entity determination.
   - Official portal: https://bsd.sos.in.gov/publicbusinesssearch
   - Modern INBiz search: https://inbiz.in.gov/bos/businesssearch/businesssearch

5. **Purdue Archives.** The official Fraternities/Sororities/Cooperative Life collection (UA 172) covers 1873–2010, which predates the modern Delta Omicron colony at Purdue. The catalog did not identify a chapter-specific present-day facility record. This historical collection cannot resolve current housing.
   - Collection: https://archives.lib.purdue.edu/repositories/2/resources/1563

## Build decision / dead end

The strongest housing evidence remains the 2024 petition’s statement that the then-colony was saving for and exploring permanent housing; the newest national evidence establishes installation and an event venue, not a residence. The current Purdue roster and local chapter site likewise provide no house address. The newly checked IRS, county GIS, city permit, state entity-search, and Purdue archive sources did not bridge that gap. There is therefore no defensible current address, parcel ID, or building footprint to model. Keep the Psi Upsilon build at zero until a current primary source identifies a residence or property and it can be crosswalked to an official parcel/building footprint.
