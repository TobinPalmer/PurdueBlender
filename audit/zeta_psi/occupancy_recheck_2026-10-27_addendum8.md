# FID 748 occupancy conflict recheck — 2026-10-27

**Question:** Has a dated first-party Zeta Psi, Chi Psi, Purdue, property, or permit source after Chi Psi's July 2024 lodge announcement resolved who occupies the building at 950 David Ross Road or identified a different current Tau Gamma address?

**Disposition:** No. FID 748 remains a useful spatial match to a real building at 950 David Ross Road, but it is not usable as a verified *current Zeta Psi facility*. No later official source found in this pass explicitly places Tau Gamma at 950, confirms that Chi Psi moved in, states that the chapters share the facility, or names a different Tau Gamma address. The new Chi Psi local website, linked from the national fraternity's current “Where We Are” page, confirms Chi Psi's active Purdue Alpha and uses the section title “Life at the Lodge,” but gives no lodge street address. It therefore maintains the housing conflict without resolving its location or exclusivity.

## New first-party source check

Chi Psi's official national directory lists Epsilon Tau (Purdue University) among its active Alphas and links the Purdue Alpha's local website, `https://purduechipsi.com/`. The local website identifies Alpha Epsilon Tau as a Purdue chapter, says Purdue is its home, and has a “Life at the Lodge” section. Its gallery reports that there are no photos yet. The website has no street address or facility photograph. The raw HTML and current JavaScript bundle retrieved October 27, 2026 are retained as `sources/purdue_chi_psi_local_site_home_2026-10-27.html` and `sources/purdue_chi_psi_local_site_bundle_2026-10-27.js`.

This new source is current first-party evidence that Chi Psi represents itself as an active Purdue Alpha associated with lodge life. It does **not** establish that Chi Psi currently occupies 950 David Ross. The earlier, dated Chi Psi Summer 2024 newsletter remains the only first-party source found that ties Chi Psi's Purdue Lodge to that exact address. No later Chi Psi directory, local-site page, or national property page gives a street address for Epsilon Tau.

The current Zeta Psi national Indiana listing and Collegiate Archives directory still list Tau Gamma at Purdue but give no house address. Zeta Psi's 2023 chapter report said the chapter moved its house during 2022 without naming its destination; the self-reported 950 address remains undated. The latest national Zeta Psi membership/award notices confirm Purdue affiliation but say nothing about housing. These sources do not resolve whether the old 950 claim is stale, whether the two groups share a building, or whether Tau Gamma moved again.

## Current property, GIS, and permit checks

- **Purdue BuildingShapes FID 748:** A live query again returns `BUILDING_N=Zeta Psi`, `ADDRESS=950 David Ross Rd`, and `OWNER=GREEK`. `NUM_LEVELS=1`, `Extrution=12`, and the edit-date fields are blank. This is an undated campus GIS label, not current occupant evidence or measured height.
- **Tippecanoe County parcel and assessor:** The live parcel query returns parcel `79-06-13-476-005.000-029` at `950 DAVID ROSS RD`. The Improvements AV record lists a 2007 build year, C+2 grade, and 7,840 sq ft finished living area, with current improvement assessed value $611,500. Public fields in these returned rows do not identify an owner or occupant and do not supply a building perimeter. County parcel and assessor raw responses are saved under `sources/`.
- **Indiana Building Footprints:** The live service returns the same `OBJECTID 409718` footprint from 2018 LiDAR. It corroborates the physical building outline for its source date, not its 2026 occupant or current structural wall line.
- **Permits:** The County's public GIS exposes a permit layer, but a parcel query returns the parcel record with all permit-specific fields blank; the layer is not a complete city permit-history source. West Lafayette's official permits page describes permit types but provides no public address result. Searches of indexed official city/FSCL pages and permit-report results for the parcel and exact address surfaced no later occupancy or move record. Absence from these sources is not proof that no permit or move occurred.

## Why FID 748 remains unusable for the Rossen Zeta Psi assignment

The spatial evidence supports **one physical structure at 950 David Ross Road**: Purdue's GIS polygon, the county parcel/assessor data, and the historical Indiana LiDAR outline all point to that site. The unresolved issue is identity and occupancy. Purdue's campus label and a stale-looking Zeta Psi self-report point to Zeta Psi; Chi Psi's first-party 2024 newsletter explicitly identifies the one mapped structure at 950 as its new Lodge, and the current Chi Psi national directory links an active Purdue Alpha whose local site still describes Lodge life. No primary record after the 2024 announcement resolves those claims or establishes dual occupancy.

Consequently, FID 748 cannot currently be claimed as an exclusively Zeta Psi house, nor can the Zeta Psi assignment be closed by modelling it as Tau Gamma's current facility. Its spatial match does not repair the missing semantic crosswalk. The 237 South Grant lead remains unsupported as a current facility, and this pass found no alternative current Tau Gamma address with a Purdue GIS FID or defensible footprint. Do not detail or reassign FID 748 for Zeta Psi until a dated source resolves occupant(s); the present evidence supports zero new Zeta Psi model work.

No geometry, asset, manifest, README, master blend, or shared tracker was edited.
