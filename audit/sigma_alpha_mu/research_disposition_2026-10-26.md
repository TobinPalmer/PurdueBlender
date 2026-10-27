# Sigma Alpha Mu (Sigma Eta) facility crosswalk review

**Reviewed:** 2026-10-26  
**Assignment:** Rossen — determine whether Purdue's Sigma Alpha Mu chapter has a current, identifiable physical chapter house and a supported campus-map/GIS crosswalk.  
**Disposition:** unresolved; no building asset was created.

## Conclusion

The public sources establish that Purdue's Sigma Eta chapter is active and that Sigma Alpha Mu's national property-management page lists Purdue under properties it manages. They do not identify the current property address or chapter-house footprint. The historically documented Sigma Alpha Mu house at **172 N. Littleton Street** is currently listed by Purdue BoilerLink as **Gemini Cooperative**, so that former location is not a supported current SAM assignment. The repository manifest has no Sigma Alpha Mu asset or source feature, and the scoped GIS/target-building inventories provide no verified Sigma Alpha Mu match. Do not build an asset at FID 172 / the old Littleton location on this evidence.

This does not prove the current Sigma Eta chapter lacks a facility: SAM's management roster makes an address-level physical property plausible. It leaves its identity/crosswalk unresolved.

## Source findings

| Source | Date/context | Finding | Local snapshot |
| --- | --- | --- | --- |
| [Sigma Alpha Mu active chapter roll](https://sam.org/fraternity/chapter-roll/) | Live page retrieved 2026-10-26 | Lists **Sigma Eta — Purdue University** among currently active and recognized chapters; gives no house/address. | `sources/sam_active_chapter_roll.html` |
| [SAM National Properties & Property Management](https://sam.org/fraternity/housing/) | Live page retrieved 2026-10-26 | Lists **Purdue — Manage Property**. The page explains the property-management relationship but gives no property address or building identity. | `sources/sam_property_management_housing.html` |
| [Purdue IFC chapter roster](https://www.purdue.edu/fscl/councils/ifc/chapters.php) | Live page retrieved 2026-10-26 | Lists Sigma Alpha Mu and its current chapter Instagram link; no chapter website, address, or house location is given. | `sources/purdue_ifc_roster.html` |
| [Alpha Chi Theta chapter history](https://alphachithetas.org/our-story/) | Historical account, live page retrieved 2026-10-26 | States its 172 Littleton house was sold to Sigma Alpha Mu in 1956. This supports historical occupancy only. | `sources/alpha_chi_theta_172_littleton_history.html` |
| [Purdue BoilerLink — Gemini Cooperative](https://boilerlink.purdue.edu/organization/gemini) | Live Purdue organization listing retrieved 2026-10-26 | Lists Gemini Cooperative at **172 Littleton St, West Lafayette, IN 47906** and describes it as a current cooperative house. This conflicts with treating 172 Littleton as SAM's current house. | `sources/purdue_gemini_boilerlink.html` |

## Repository and map review

- `modular/manifest.json` (1,981 assets) contains no Sigma Alpha Mu / Sigma Eta asset, feature ID, source address, or placement marker.
- `modular/buildings/target_buildings_gis.json` contains only five curated target entries, none for Sigma Alpha Mu. It is not a comprehensive GIS inventory and cannot prove absence of a footprint.
- The existing current Purdue GIS metadata snapshot under `audit/zeta_psi/sources/purdue_gis_buildings_metadata_2026-10-26.json` describes a `BuildingShapes` layer, but its service endpoint is not exposed in the saved metadata. No Sigma Alpha Mu feature ID or address-level geometry was available in the assignment's authoritative indexed crosswalk.
- A historical public `Purdue/campus/MapServer/0` query was also saved as `sources/purdue_historic_campus_building_layer_response.json`; it returned 730 campus features and no Littleton address. Its service is time-bounded through 2015 and does not cover this off-campus Littleton property, so it is not usable to match Sigma Eta's present facility.

No current physical house address and no GIS feature ID/outline can therefore be assigned with adequate evidence. No geometry, asset path, ID, or build script was invented or changed.

## Evidence still needed

Request or locate a current source from **Sigma Eta's chapter/property contact, SAM Property Management, or the Sigma Eta House Corporation** that states the chapter's current house street address (or explicitly confirms it has no chapter house). Then match that address against current parcel/building footprint data or current aerial imagery and save a source snapshot with the GIS feature ID and geometry. A current chapter page or recruitment announcement giving an address could also resolve occupancy; the address must still be crosswalked to a specific building footprint before modeling.

## Provenance notes

- Retrieval date for downloaded pages and GIS response: 2026-10-26.
- Coordinates/CRS and geometry metrics: not applicable; no current GIS candidate was established.
- Height, floors, facade, roof, and footprint: not modeled; all remain unknown for the present Sigma Eta facility.

## Dated addendum — public address leads (2026-10-26)

The current public evidence strengthens the case that Sigma Eta may have a physical facility, but still does not support a building assignment:

- **Source-backed fact — active chapter:** SAM's [active chapter roll](https://sam.org/fraternity/chapter-roll/) lists Sigma Eta at Purdue. Its [property-management page](https://sam.org/fraternity/housing/) lists **Purdue — Manage Property**, without an address or building identity.
- **Source-backed public claim — lease:** Sigma Eta's founder and former president states on his [public profile](https://www.linkedin.com/in/neal-ssingh) that he negotiated and secured a chapter-house lease by early 2025. The profile does not give the leased property's address. This is a named individual's account, not an address-confirming SAM or Purdue property record.
- **Address ruled out:** **1165 W Stadium Avenue** is the mailing address for Purdue's [Tarkington Residence Hall](https://www.housing.purdue.edu/my-housing/options/residence-halls/tarkington.html), as also identified in Purdue's [building emergency plan](https://www.purdue.edu/operations/emergency-preparedness/tark/). It is therefore not evidence of Sigma Eta's chapter facility and should not be used as its address or GIS crosswalk.

**Unresolved inference:** The lease statement and SAM's property-management listing make a current or recently secured chapter facility plausible, but neither identifies the property; the lease's present status is also unconfirmed. No address, GIS feature ID, or building asset can be assigned from these sources. A current address from Sigma Eta, its house corporation, SAM Property Management, or Purdue FSCL—and a parcel/footprint match—remains necessary.
