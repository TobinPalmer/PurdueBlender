# Psi Upsilon / Delta Omicron current-facility recheck addendum

**Research date:** 2026-10-26  
**Assignment:** Rossen  
**Scope:** Current official Purdue roster, linked chapter sources and social profile, address lead, and Purdue GIS crosswalk. No one was contacted.

## Conclusion

Current public sources still do not establish a dedicated Psi Upsilon / Delta Omicron chapter house address. Keep this as a facility-identity research assignment, not a confirmed building model. This is **unverified facility status**, not evidence that the chapter has no house.

The Purdue IFC Organizations page currently lists Psi Upsilon as an organization (marked co-ed) and links its national website and the Instagram handle `@psiupsilonatpurdu`. The link is evidence of Purdue-recognized chapter affiliation; the roster gives no address. Instagram throttled automated access during this review, so no individual post or image is used as facility evidence. The roster also contains a visibly mismatched Instagram label under Sigma Alpha Epsilon; the Psi Upsilon row's actual link target was checked in the saved HTML.

The chapter's current website has no street address or map pin. Its contact form and alumni email are not facility evidence. Psi Upsilon's current national news describes the active Delta Omicron chapter and 2026 activity, but publishes no house address.

## Address and GIS crosscheck

The chapter's IRS-derived mailing-address listing at **1198 Third Street** is not a chapter-house lead. Purdue identifies this exact address as the **Krach Leadership Center**, a Purdue-owned campus building. Purdue's BuildingShapesZip4 GIS feature **FID 902**, abbreviation `KRCH`, names Krach Leadership Center, gives address `1198 3rd Street`, and lists owner `PURDUE`. That building already has its own manifest entry and detailed asset. Do not reassign FID 902 to Psi Upsilon.

The repository's Purdue GIS target inventory contains no Psi Upsilon / Delta Omicron identity match, and no current chapter address supports selecting another FID or parcel. The old 400 Northwestern Avenue lead remains ruled out by the previously documented Delta Tau Delta evidence. No new physical facility or asset path can responsibly be proposed.

## Sources checked

| Source | Provider / date | Result | Saved evidence |
|---|---|---|---|
| [IFC Organizations](https://www.purdue.edu/fscl/councils/ifc/chapters.php) | Purdue FSCL; accessed 2026-10-26 | Lists Psi Upsilon and links national site and chapter Instagram; no address. Instagram page access was throttled. | [`purdue_ifc_organizations_2026-10-26.html`](sources/purdue_ifc_organizations_2026-10-26.html) |
| [Psi Upsilon at Purdue](https://psiupsilonatpurdue.com/) | Chapter website; accessed 2026-10-26 | Contact form and alumni email; no street address, facility claim, or map pin found. | [`psi_upsilon_chapter_site_2026-10-26.html`](sources/psi_upsilon_chapter_site_2026-10-26.html) |
| [Psi Upsilon chapter roll](https://psiu.org/chapter-roll/) and [2026 national news](https://psiu.org/category/news/) | Psi Upsilon Fraternity; accessed 2026-10-26 | Confirms Purdue chapter presence/activity; no house address. The 2026 activity details are in the latest Delta Omicron news entry. | Existing [`psi_upsilon_news_2026-10-26.html`](sources/psi_upsilon_news_2026-10-26.html) |
| [Krach Leadership Center](https://events.purdue.edu/krach_leadership_center) | Purdue University events directory; accessed 2026-10-26 | Identifies 1198 3rd Street as Krach Leadership Center. | [`purdue_krach_leadership_center_2026-10-26.html`](sources/purdue_krach_leadership_center_2026-10-26.html) |
| [Purdue campus BuildingShapesZip4 layer 0](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query?where=FID%3D902&outFields=FID%2CBUILDING_N%2CBLDG_ABBR%2CADDRESS%2COWNER&returnGeometry=true&outSR=4326&f=pjson) | Purdue University campus GIS; query retrieved 2026-10-26; response CRS EPSG:4326 | FID 902 is Krach Leadership Center / KRCH, 1198 3rd Street, owner PURDUE. | [`purdue_krach_gis_fid902_2026-10-26.json`](sources/purdue_krach_gis_fid902_2026-10-26.json) |
| [IRS-derived Delta Omicron organization profile](https://www.causeiq.com/organizations/psi-upsilon-fraternity-delta-omicron-chapter%2C881616239/) | Cause IQ summary, accessed 2026-10-26; not a primary facility source | Shows the 1198 3rd St mailing address; Purdue's official records identify that address as Krach, so it does not establish a chapter house. | Search result retained in this dated note; no raw snapshot claimed. |

## Next step

Only a dated post-installation chapter statement, national housing record, or Purdue FSCL record identifying a dedicated address (or confirming no dedicated house) can resolve the assignment. If an address is later established, crosswalk it to the current Purdue GIS polygon and parcel, confirm chapter occupancy independently, then model that single physical structure under the matching FID. Until then, do not create or relabel an asset.
