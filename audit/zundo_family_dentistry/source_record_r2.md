# Zundo Family Dentistry — accepted R2 asset record

Date: 2026-10-26. R2 passed independent review at 8.04/10 and is the accepted detailed asset. The original R1 library is preserved as `audit/zundo_family_dentistry/zundo_family_dentistry_r1_candidate.blend`; the canonical library and R2 review copy are in `modular/buildings/`. The master links the canonical library through `Placement_massing_zundo_family_dentistry_f840e2b`.

## Source and confidence

- Official identity/address: [Zundo office location](https://www.zundodental.com/office-location), which names Zundo Family Dentistry and gives 1827 Northwestern Avenue, West Lafayette, IN 47906. The [official home page](https://www.zundodental.com/) repeats the office identity/address. These official pages do not publish measured facade or interior imagery.
- Plan/location source: OSM way 887558318 in `osm_way_887558318_raw.json`, tagged for Zundo Family Dentistry at 1827 Northwestern Avenue. Provider OpenStreetMap contributors, ODbL 1.0, source CRS WGS84 / EPSG:4326; feature timestamp 2020-12-22. The eight-node polygon was transformed via the local approximation specified by `modular/AGENTS.md`, not a survey CRS. Projected envelope is X [-708.770700,-693.513272], Y [2027.301696,2051.952576] m. The stable massing bounds independently match to about 0.03 m, supporting source/identity correspondence but not survey-grade edge accuracy.
- Street-level review: [Google Maps address preview](https://www.google.com/maps/place/1827+Northwestern+Ave,+West+Lafayette,+IN+47906/@40.4458,-86.9220,18z/data=!4m2!3m1!1s0x0:0x0), visually reviewed 2026-10-26. The available preview supports a light-colored, low, elongated office behind a sidewalk/lawn and mature deciduous trees. No capture date was visible. Searches for a closer, attributable building facade or plan image found no additional reliable source. Do not borrow unrelated dental-office photos as evidence.
- Purdue campus GIS lookup did not produce a matching feature/FID, so no height/permit attributes are available.

**Verified:** business address and name; the mapped polygon and broad local position/orientation. **Estimated/inferred:** height, low-parapet roof shape, facade materials/joints, window layout, street-facing door position, sign panel position/design, accessible approach detail. **Schematic:** interior room layout, room count, furnishings and clinical equipment. There is no measured floor plan or interior photo. The model labels these limits rather than implying a survey.

Placement origin remains the projected OSM footprint shoelace centroid: X -702.407752 m, Y 2039.751270 m, Z 0. Geometry stays local to this origin. Preserve the stable export collection `Asset_massing_zundo_family_dentistry_f840e2b`; only the master `Placement_massing_zundo_family_dentistry_f840e2b` marker should supply that origin if R2 is accepted.

## R2 revisions from the 7.6/10 R1 review

- Reworked the street entrance as a framed glazed door, projecting canopy, two posts, clearer landing/walk, an address plaque, and a readable wall-mounted “ZUNDO FAMILY DENTISTRY” sign. The practice name is official; the sign form/placement/wording as facade sign is an illustrative inference.
- Removed preview trees from the export geometry. All preview trees are in the separate `Preview_only_site_context_exclude_from_master` collection and hidden in the R2 evidence views, leaving the entry/sign unobstructed.
- Added varied window groups to the road-facing side, corner piers, narrow horizontal reveal bands, facade returns, and trim. These additions articulate a plausible low office shell; exact pattern and materials remain unverified due the low-resolution public view.
- Made exterior wall/roof/concrete procedural variation visible at building scale; increased glazing brightness and blue-gray reflectance. All materials are procedural and portable.
- Refined the still-schematic interior with an interrupted corridor opening and door leaf/vision lite, operatory door leaves, seating backs/legs, reception drawers/keyboard/credenza, dental chair arm pads/head cushions/foot supports, upper/base cabinets, sinks/faucets, and ceiling task diffusers. The brighter overhead roof-off view makes four modeled treatment bays and reception legible.
- Added three separate evidence views: `zundo_r2_front.png` (street-facing), `zundo_r2_side_rear.png`, and `zundo_r2_roof_off.png`.

Build source: `build_r2.py`. Fresh-reopen evidence: `fresh_reopen_validation_r2.json` and `fresh_reopen_validate_r2.py`. Build metrics: `build_metrics_r2.json`. Raw OSM snapshot: `osm_way_887558318_raw.json`.

## R2 validation

Blender 5.2.3 fresh-open check passed. Export collection has 275 objects: 273 meshes and 2 font objects. Fourteen materials are assigned to export objects; 15 material datablocks are used in the file, including preview-only context. Asset-local bounds including entry/approach elements are X [-6.5382,12.5404], Y [-12.6248,12.3765], Z [-0.05,3.94] m. No preview tree is in the export collection, and no missing external texture dependency was found.
