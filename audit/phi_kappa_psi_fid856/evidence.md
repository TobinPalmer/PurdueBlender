# Phi Kappa Psi (Indiana Delta) — source and build evidence

## Identity and source resolution

- The current official chapter contact page identifies Indiana Delta and lists **1307 Tower Dr, West Lafayette, IN 47906**: <https://purdue.phikappapsi.com/contact> (retrieved 2026-10-27; snapshot `sources/official_chapter_contact_2026-10-27.html`).
- The official national fraternity magazine *The Shield of Phi Kappa Psi*, Summer 2010, page 28, says Indiana Delta had a new chapter house at **1307 Tower Drive**. The print-ready page is preserved as `sources/national_phipsi_page174.jpg`; page 174 of the available all-issues PDF bundle is printed page 28, Summer 2010. PDF: <https://www.phikappapsi.com/wp-content/uploads/2019/07/pages-13.pdf>.
- C.F. Jones Group lists “Phi Kappa Psi Fraternity at Purdue University” as a completed construction-management project in West Lafayette (24,000 sq ft; $3.2m): <https://www.projectpresenter.com/cf-jones-group/projects/phi-kappa-psi-fraternity-at-purdue-university/30006/show>. Its photos show the current red-brick Greek Revival / Georgian-inspired residence, white central portico and pediment, rear central light-painted bay, repeated double-hung windows, rear stair/service level, and interior lobby/common spaces. Eight downloaded reference photos and a contact sheet are in `sources/contractor_photos/` with original source URLs in `source_register.json`.
- C.F. Jones Group's campaign history independently describes the Indiana Delta House Corporation purchasing a lot in Tower Acres and building a new chapter house: <https://www.penningtonco.com/campaigns/phi-kappa-psi-purdue-university>.

The Purdue GIS FID 856 record is labeled “Phi Kappa Tau” but carries address `1307 TOWER DR` and owner `GREEK`. That organization label is stale/conflicting; the exact address is independently established as Phi Kappa Psi by both current official chapter contact and contemporary national-magazine evidence. The local OSM building way 301841257 is generically tagged `building=school` and is not used as the wall footprint. The existing massing candidate stays unmodified.

## Footprint, pose, and height

- Structural wall ring: Purdue ArcGIS FID 856 in native Web Mercator (EPSG:3857), snapshot `sources/purdue_gis_fid856_2026-10-26.json`. Converted through inverse Web Mercator to lon/lat then to the repository's approximate local East/North conversion from `modular/AGENTS.md`; model geometry is local meters centered on the polygon area centroid (`-1116.752906, 605.237879` in repository campus-local coordinates).
- FID 856 source outline: 12 non-closing vertices, 421.960 m² in local projection, dimensions approximately 34.74 × 28.28 m. The Esri World Imagery export `sources/esri_aerial_1307_tower.jpg` and overlay `sources/aerial_footprint_overlay.jpg` show the red Purdue structural outline within the larger roof/eave outline traced by cyan OSM way 301841257. This explains much of their overlap mismatch. Aerial export query bounds were `[-9676750, 4928990, -9676580, 4929110]` in EPSG:3857; the imagery mosaic acquisition date was not exposed in the retrieved service response.
- GIS `Extrution=53` is interpreted only as an approximately 53 ft campus-map height field. The source's `NUM_LEVELS=2` conflicts with the project photographs, which visibly show three to four window levels. The model uses 12.7 m of wall, a 16.1 m main-roof ridge, and a photo-guided rear gable/stack rising to about 18.2 m. The rear stack height is an estimate, not a surveyed elevation; the 53 ft GIS value may omit the roof feature or reflect a different map generalization.
- The plan shape follows GIS, while the OSM candidate's roof/eave outline, 40.67 × 32.67 m bounds and 561.27 m² base are intentionally not substituted for the structural footprint. `gis_crosswalk.json` records the exact projected measurements and mismatch.

## Modeling decisions and remaining uncertainty

- The red-brown brick running bond, charcoal pitched roof, pale stone trim, central four-column portico, balcony, triangular pediment with ΦΚΨ mark, and repeated double-hung openings follow C.F. Jones Group's project photos. The rear now has the broad projecting white central bay, three paired upper window courses, lower openings, a raised cross-gable with dark shingle infill, and a tall central roof stack based on photo 3. Bay depth and exact roof geometry remain estimates.
- The `Interior_Schematic` child collection now includes a divided lounge, arched stair-hall opening, longer stair flight with landing and guardrail, layered sofas/chairs/coffee and dining tables, built-in bookcases, and schematic partitioned upper rooms/corridors. The lounge perspective and elevated open-ceiling cutaway correspond to contractor photos 5-6. No georegistered architectural plan was found, so room boundaries, furniture arrangement, and upper-floor layout are explicitly schematic and not exact dimensions.
- Exact height/story count, roof framing/pitch, trim dimensions, window sizes, and exact rear/service-door location are estimates from photos and legacy GIS attributes. The C.F. Jones Gallery gives credible project photographs but no stated photo capture dates, architectural drawings, or image copyright/reuse terms. This model uses those images only as visual evidence; none are embedded in the blend.
- Assessor record has no reliable year/grade/area values (`sources/tippecanoe_assessor_1307_tower.json`).

## Asset and checks

- Proposed stable ID: `phi_kappa_psi_fid856`.
- Asset: `modular/buildings/phi_kappa_psi_fid856.blend`, collection `Asset_phi_kappa_psi_fid856`, scene `Building_phi_kappa_psi_fid856`.
- Dedicated deterministic builder: `audit/phi_kappa_psi_fid856/build_phi_kappa_psi_fid856.py`.
- Last builder run writes front, aerial, rear, lounge-eye, and lounge-cutaway previews to `renders/`. A separate fresh-open check writes `renders/fresh_open_front.png` and `fresh_open_validation.json` after reopening the saved blend, verifies its collection, procedural-only materials, object count and geometry bounds, and hashes the exact saved asset.

Independent visual grading has not yet been done.

## R1 revision and validation handoff

- R1 findings addressed in the dedicated builder: rear bay now projects from the rear wall with paired three-course fenestration, a raised cross-gable and shingle infill, and central roof stack; the interior collection now has room boundaries, an arched stair opening, extended stair run/landing/guard, lounge seating, coffee and dining tables, bookcases, and schematic upper room divisions.
- Updated review images: `renders/phi_kappa_psi_rear.png`, `renders/phi_kappa_psi_lounge_cutaway.png`, and `renders/phi_kappa_psi_lounge_eye.png`. The cutaway omits the upper schematic room fitout and floor plates for visibility; these objects remain in the asset.
- Fresh-open/re-render from the exact saved file succeeded (Blender 5.2.3): 969 collection objects, local evaluated bounds X[-17.792, 17.774], Y[-14.614, 15.165], Z[-0.520, 18.150] m; no external image textures. Exact SHA-256: `70ebe6333250a2266005ca6d72983a7dbd709ed187ee82a96642099e7e4c5ba9` (`fresh_open_validation.json`).
- No independent R2 grade has been performed yet. Interior plan and height/story remain estimates; the new rear stack pushes the modeled top above the legacy 53 ft GIS extrusion, so that dimension remains explicitly unresolved.
