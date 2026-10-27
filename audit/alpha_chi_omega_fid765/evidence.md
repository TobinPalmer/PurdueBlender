# Alpha Chi Omega (Alpha Beta Chapter) — FID 765

## Source identity and coordinate placement

The model is tied to Purdue University BuildingShapesZip4 FeatureServer feature FID 765, code `SOACO`, name Alpha Chi Omega, address 851 David Ross Rd, owner code GREEK. The layer’s native CRS is EPSG:3857; the archived query returned the geometry in EPSG:4326. The source polygon has 19 ring coordinates, 639.716 m² shoelace area, and a centroid at approximately 40.4347598672° N, 86.9264470681° W. Under the project’s required local approximation (origin 40.4274° N, 86.9137° W; X east, Y north), the placement is X=-1081.0865 m, Y=817.2397 m. The detailed geometry is centered on that GIS centroid and uses the GIS polygon for its ground plan. The source massing file remains untouched.

The GIS geometry and source artifacts are archived in `sources/fid765_arcgis_4326.json`, `sources/purdue_gis_layer_metadata.json`, `gis_crosswalk.json`, and `fid765_footprint_overlay.png`. The source massing comparison is recorded in `gis_crosswalk.json`; its footprint is a rough location candidate, not used for the detailed shell because its outline diverges from the GIS polygon.

## Exterior reference and interpretation

- Purdue Panhellenic’s Alpha Chi Omega page identifies the Purdue chapter and includes a chapter photo collage: https://www.purduepanhellenic.com/cost/alpha-chi-omega. The captured HTML and image are in `sources/purdue_panhellenic_axonchapter.html` and `sources/panhellenic_alpha_chi_omega.png`.
- The Alpha Beta Home Corporation’s Spring 2016 newsletter identifies the Alpha Chi Omega house at 851 David Ross Road, states it was built in 1964–65, and presents a renovation rendering with a red-brick, three-level facade, dark dormered roof, central Greek-letter gable, upper balcony and three arched entrance bays. The front image on page 1 (locally archived as `sources/newsletter_spring2016_page2.jpg`, following the archive downloader’s zero-based page numbering) is a renovation proposal/rendering, not an as-built survey. The newsletter also describes the planned renovation. Source: https://www.epageflip.net/i/656683-spring-2016-newsletter.
- The Fall 2015 Home Corporation newsletter contains an existing-house photo with facade partly obscured by mature trees and reports ongoing landscaping and interior work. It helps establish the pre-renovation red-brick exterior and mature site landscape, but does not resolve hidden facade details. Source: https://www.epageflip.net/i/590316-fall-2015-newsletter; local pages `sources/newsletter_fall2015_page*.jpg`.
- Purdue GIS has a `Floorplans` attribute pointing to an internal `G:\GIS\web_pages\html_pages\SOACO.html` path; no publicly accessible dimensioned/georegisterable plan was found.

The prominent facade features, roof dormers, entry arcade, limestone trim, Greek-letter sign, balcony, brick tone and approximate window rhythm follow the chapter-owned 2016 rendering. After R1 review, the roof profile was revised to a steep lower mansard band with a smaller upper cap while retaining the 12.8 m estimated peak; the six dormers were narrowed and made taller; and the entry bays were rebuilt as semicircular portal arches with thicker limestone supports. The current render is `render_r2_candidate.png`. Roof type/dimensions, exact story heights, window spacing and front bearing are inferred rather than surveyed. The facade bearing (about 133.7°) is inferred from the GIS polygon and nearby access/road context. GIS fields `NUM_LEVELS=1` and `Extrution=33` conflict with the three visible levels in chapter imagery and have undocumented semantics, so they were not used as height truth.

## Model contents and portability

Proposed integration metadata: stable ID `alpha_chi_omega_fid765`; asset `modular/buildings/alpha_chi_omega_fid765.blend`; scene `Building_alpha_chi_omega_fid765`; collection `Asset_alpha_chi_omega_fid765`; local placement origin X=-1081.0865 m, Y=817.2397 m. The model contains the GIS-plan shell, procedural packed brick/limestone/roof/glass/metal/wood materials, window and entry geometry, arched portal stones, balcony, dormers, gable text, one chimney and a schematic interior. The interior is explicitly nondimensional and schematic; only the newsletter’s mention of basement common/dining functions was used. No external images, texture paths, or linked Blender libraries are needed for the asset.

## Validation artifacts

- Fresh-open/render visual QA image for this revision: `render_r2_candidate.png`.
- Fresh-open inventory/bounds/hash: `fresh_open_validation.json`.
- GIS-to-massing comparison and proposed manifest metadata: `gis_crosswalk.json`.
- Builder: `build_alpha_chi_omega.py`.
- Original spatial massing asset: `../modular/buildings/massing_house_301841602_8190d79.blend` (preserved).

The building asset is a review-ready visual approximation based on primary chapter references and the official footprint. It is not a measured architectural survey, and detailed internal room geometry is not verified.
