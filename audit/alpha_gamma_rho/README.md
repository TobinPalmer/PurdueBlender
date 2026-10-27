# Alpha Gamma Rho, Purdue Delta Chapter

## Assignment and asset identity

- Root README assignment: Tobin; row lists FID 792 and `massing_house_301841253_f0b3be3`.
- Stable asset ID and library path preserved: `massing_house_301841253_f0b3be3` at `modular/buildings/massing_house_301841253_f0b3be3.blend`.
- Exported collection and scene names preserved: `Asset_massing_house_301841253_f0b3be3` and `Building_massing_house_301841253_f0b3be3`.
- Builder source: `modular/buildings/build_massing_house_301841253_f0b3be3.py`.

## Identity, footprint, and orientation

The official Alpha Gamma Rho Delta chapter site lists 607 N University St, West Lafayette. Purdue Agriculture's 2025–26 Greek Life story identifies Alpha Gamma Rho and includes a current chapter-house photograph: the exterior shows the same 607 entry, brick facade, white columned entrance, arched transom, blue fascia/shutters, and green ΑΓΡ sign as the KJG project image. The chapter is a current fraternity-house project at Purdue, corroborated by the KJG Architecture project page.

The raw OSM full-way snapshot records way 301841253 at 607, last edited 2022-02-27 (OSM `building=school`; no name tag). Its 20-node closed ring was converted using the project's local approximation (origin 40.4274, -86.9137; X east and Y north). Resulting plan bounds are 25.036 m east-west by 36.821 m north-south, with approximate plan area 687.06 m². The existing campus-space massing asset had identical bounds. This is a strong geometric match, not a surveyed registration: horizontal position and orientation relative to official Purdue survey control remain unverified. The long axis is north-south; the documented main entrance is on the east-facing University Street side.

## Model

The source builder creates the source-traced footprint, brick shell, four occupied levels (including basement-level plate), stone base/belts, dark gabled shingle roof with four front-facing dormers, blue shutters, repeated sash windows, and the east-facing white portico with blue fascia, fluted columns, arched glazed entry, and raised green ΑΓΡ lettering. The four-level count and approximately 24,100 sq ft interior renovation are from KJG Architecture (2018). The wall height (10.35 m), roof ridge height (13.8 m), precise floor spacing, dormer geometry, and room layout are modeled estimates; no dimensioned plan or measured elevation was found. Interior furniture and partitions provide a visible first-floor plan review, but room locations are illustrative.

## Evidence and validation

Raw snapshots and reference images are in `sources/`. `renders/alpha_gamma_rho_facade.png` is the brighter facade-level preview; `renders/alpha_gamma_rho_oblique.png` shows a second angle; `renders/alpha_gamma_rho_hero.png` is the initial hero view; `renders/alpha_gamma_rho_first_floor_interior.png` is a stripped-back first-floor plan view. `reopen_validation_2026-10-26.json` records an independent fresh-open check of the saved library, including evaluated bounds, exported collection, object count, modifiers, and relative image references.

The legacy manifest entry is coordinator-owned and still describes this asset as a one-object massing library. The updated library retains the manifest path, collection, scene, and campus-world coordinates, but its exported collection now contains detailed multi-object geometry. The manifest object count therefore needs coordinator review during integration; it was not edited here.

## Sources

1. OpenStreetMap way 301841253, retrieved 2026-10-26; source timestamp 2022-02-27; WGS84 lat/lon; full raw response saved as `sources/osm_way_301841253_2026-10-26.json`; footprint measured by converting the 20 ordered nodes to the project's local XY approximation and using polygon extents/area. [Way link](https://www.openstreetmap.org/way/301841253)
2. Alpha Gamma Rho Delta official chapter site, retrieved 2026-10-26; address on contact/donate page; raw HTML saved as `sources/agr_delta_official_site_2026-10-26.html`. [Chapter site](https://agrpurdue.com/donate.html)
3. Purdue Agriculture, “Greek Life Leadership On Campus,” page last modified 2026-06-08, retrieved 2026-10-26; identifies Alpha Gamma Rho and current chapter president; photograph at `sources/purdue_ag_article_house_2026.jpg`; raw page saved alongside it. Photo capture date is unspecified. [Purdue article](https://ag.purdue.edu/department/agecon/undergraduate-program/success-2025-26/greek-life-leadership-on-campus.html)
4. KJG Architecture, “Alpha Gamma Rho Fraternity,” project year 2018, retrieved 2026-10-26; documents Purdue project, four levels, and approximately 24,100 sq ft interior renovation. Page snapshot and project rendering are saved as `sources/kjg_agr_project_page_2026-10-26.html` and `sources/kjg_agr_project_render.jpg`. [KJG project](https://www.kjgarchitecture.com/portfolio-1/alpha-gamma-rho-fraternity)
5. Purdue Campus MapServer layer metadata and an address query (`ADDRESS LIKE %607%`) were saved. No Alpha Gamma Rho/607 N University feature was returned from the public campus-building query; the chapter site and Purdue Agriculture source provide the identity/address and facade corroboration instead. [Purdue Campus MapServer](https://mapsweb.lib.purdue.edu/arcgis/rest/services/Purdue/campus/MapServer)


