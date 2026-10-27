# Psi Upsilon / Delta Omicron county and current-roster follow-up

**Research date:** 2026-10-26 local time (UTC retrieval crossed midnight to 2026-10-27)
**Assignment:** Rossen
**Scope:** Independent repeat of official chapter-roster checks and review of Tippecanoe County's official property/GIS lookup path.

## Finding

The current official Purdue IFC page lists Psi Upsilon as a co-ed organization and links to Psi Upsilon's national website; it does not publish a chapter-house address. The national chapter roll identifies Delta Omicron at Purdue as chapter 50 (2025), and the official chapter website likewise publishes no physical address. These sources establish the chapter identity/status, not a facility.

The official Tippecanoe County assessor pages confirm that current property information is available through the County's Beacon assessor database and public GIS tools. Those pages do not return parcel records themselves. The web reader returned a `402 Payment Required` when following the official Beacon link, and no candidate address or legal property-owner name was established to search there. This was therefore a source-path check, not a completed owner-name or parcel query. County property records cannot identify a building until a reliable address or owner entity connects a parcel to Delta Omicron.

No new source ties Delta Omicron to a dedicated facility, address, parcel, or building footprint. The fresh official checks leave the existing decision unchanged: current facility status is **unverified**, no parcel/FID can be assigned, and a speculative model is not justified. The 2024 petition's statements about individual off-campus housing and a future housing fund describe the situation and plans at petition time; they do not prove the chapter's present-day housing status.

## Source details and preserved captures

- **Purdue FSCL, IFC Organizations**, <https://www.purdue.edu/fscl/councils/ifc/chapters.php>. Live page retrieved 2026-10-26; the `Psi Upsilon*` roster entry and chapter-site link appear at lines 33 and 197–201 in the web rendering. The raw HTTP snapshot is [`purdue_ifc_organizations_2026-10-26.html`](sources/purdue_ifc_organizations_2026-10-26.html). Provider CRS/feature ID: not applicable; no address or spatial feature is published.
- **Psi Upsilon Fraternity, Chapter Roll**, <https://psiu.org/chapter-roll/>. Live page retrieved 2026-10-26; entry 50 is Delta Omicron, Purdue University (2025). A fresh raw HTTP capture is [`psi_upsilon_national_chapter_roll_followup_2026-10-26.html`](sources/psi_upsilon_national_chapter_roll_followup_2026-10-26.html); the previously preserved live recheck contains the same relevant entry. Provider CRS/feature ID: not applicable; no address or spatial feature is published.
- **Delta Omicron at Purdue, chapter website**, <https://psiupsilonatpurdue.com/>. Live page retrieved 2026-10-26; it offers recruitment, photos, contact form, Discord, and an alumni contact, but no street address or facility claim. The previously saved raw capture is [`psi_upsilon_chapter_site_live_recheck_2026-10-26.html`](sources/psi_upsilon_chapter_site_live_recheck_2026-10-26.html). Provider CRS/feature ID: not applicable.
- **Tippecanoe County Assessor, Access Property Tax & Assessment Records**, <https://tippecanoe.in.gov/151/Access-Property-Tax-Assessment-Records>. Live page retrieved 2026-10-26; it directs the public to Beacon for the latest assessor data. Raw snapshot: [`tippecanoe_assessor_property_lookup_info_2026-10-26.html`](sources/tippecanoe_assessor_property_lookup_info_2026-10-26.html). No address or parcel was queried because no candidate facility address/entity was identified.
- **Tippecanoe County GIS, Metadata**, <https://tippecanoe.in.gov/560/GIS-Metadata>. Live page retrieved 2026-10-26; county layers use NAD83 Indiana State Plane West Zone in U.S. Survey Feet, and the County warns its property lines are not survey-accurate. Raw snapshot: [`tippecanoe_gis_metadata_2026-10-26.html`](sources/tippecanoe_gis_metadata_2026-10-26.html). This metadata is contextual only and supplies no Psi Upsilon feature.
- The prior Purdue `BuildingShapesZip4` campus-layer query and its extent/limitations are preserved in [`current_facility_recheck_2026-10-26_addendum3.md`](current_facility_recheck_2026-10-26_addendum3.md) and [`purdue_gis_name_crosscheck_2026-10-26.json`](sources/purdue_gis_name_crosscheck_2026-10-26.json). A campus-layer non-match does not rule out a chapter property outside campus inventory or under another name.

## Modeling gate

Do not model Psi Upsilon / Delta Omicron yet. The next decisive evidence must explicitly connect the active chapter to a current dedicated facility (or confirm it has none) and give an address or parcel identifier. Only then can the corresponding building polygon be checked for identity, footprint, CRS, and suitable architectural sources. The two ruled-out leads documented earlier—400 Northwestern Avenue and 1198 Third Street/Krach Leadership Center—remain rejected.
