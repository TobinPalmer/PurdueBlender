# Zundo Family Dentistry source and model record

Retrieved/inspected: 2026-10-26. Candidate: `modular/buildings/zundo_family_dentistry.blend`.

## Identity and location

- Official office-location page: https://www.zundodental.com/office-location — provider: Zundo Family Dentistry; identifies Erik Zundo, D.D.S., Sarah Sautter, D.D.S., and 1827 Northwestern Avenue, West Lafayette, Indiana 47906. This verifies the business/address, not architectural form.
- Official home page: https://www.zundodental.com/ — repeats the address and practice identity.
- OSM raw snapshot: `osm_way_887558318_raw.json`; source feature: OpenStreetMap way 887558318, `name=Zundo Family Dentistry`, `building=yes`, `amenity=dentist`, `healthcare=dentist`, address 1827 Northwestern Avenue. Provider/license: OpenStreetMap contributors, ODbL 1.0; snapshot contains geometry and node metadata, way timestamp 2020-12-22. Source CRS EPSG:4326 (WGS84). The polygon is a mapping footprint, not a survey.
- Google Maps address / Street View lookup: https://www.google.com/maps/place/1827+Northwestern+Ave,+West+Lafayette,+IN+47906/@40.4458,-86.9220,18z/data=!4m2!3m1!1s0x0:0x0 — visually inspected the available address preview from street level on 2026-10-26. It shows a low, single-storey-looking, light-colored elongated building behind lawn/sidewalk and mature deciduous trees. No capture date was visible on the address preview; date is therefore unverified. The earlier nearby panorama URL is not used as building evidence because it opened at 1109 Lindberg Road, not at Zundo.
- Purdue GIS: no corresponding campus building feature/FID was returned in the prior query of Purdue's BuildingShapesZip4 layer. This building is outside/at the edge of the queried campus coverage; GIS height/elevation attributes are unavailable. Do not infer a FID.

## Coordinate transform and footprint

- Source footprint: all 8 OSM way vertices, including the step/notch, kept in the same order. Transform used exactly as `modular/AGENTS.md`: X=(lon+86.9137)*111412.84*cos(radians(40.4274)); Y=(lat-40.4274)*111040. This is a local approximate projection, not a surveyed CRS.
- The candidate geometry is local; the intended campus placement origin is the transformed OSM polygon shoelace centroid, `[-702.407752, 2039.751270]` meters, Z=0. The master `Placement_massing_zundo_family_dentistry_f840e2b` marker should use this point when switching the manifest to the detailed file. Marker/manifest/master are deliberately untouched in this candidate task.
- OSM footprint plan: projected envelope X [-708.7707,-693.5133], Y [2027.3017,2051.9526] m from the raw polygon; footprint vertices and project transform are reproducible from the snapshot/build script. The pre-existing massing object's envelope is X [-708.7707,-693.5132], Y [2027.3016,2051.9526] m, closely matching the same broad polygon. Shape agreement is moderate/good for the mapped plan, but the source polygon's edge accuracy is unknown; allow about 1-2 m uncertainty for exact wall edges and treat porch/entry details as inferred.
- Orientation: coordinate axes are east/north/up. The OSM polygon fixes plan orientation. The model treats its easternmost edge as street-facing because the business fronts Northwestern Avenue; exact door location is not independently surveyed.

## Geometry and uncertainty

- Exterior massing is a compact, low-profile, single-storey form, with a flat/low-parapet roof inferred from the street-level view. The previous generic massing height of 16 m was not supported; the candidate uses about 3.9 m to top, an estimate from the low street profile, with at least ±1 m uncertainty. No measured elevations, permit drawings, story tags, or roof survey were found.
- Exterior light neutral cladding, dark glazing, fascia, accessible entry walk, small entry planters, and freestanding practice sign are modeled with procedural, packed-in-file materials. Exact cladding, window spacing, signage, roof membrane, and planting species are not verified; they are restrained visual approximations rather than claims of surveyed details.
- Interior is explicitly schematic: reception/waiting area, corridor, four operatories, generic dental chairs, casework, equipment and partitions. No source floor plan or interior photography was found. Layout/equipment counts must not be treated as an as-built survey.
- The low-res street-level image supports the general low, light-colored profile and leafy frontage. It does not resolve facade material, roof construction, exact window count, entrance position, interior, or height. The address/site identity is verified, while these architectural details remain estimated or unverified.
- Preview-only trees and ground plane are in a separate `Preview_only_site_context_exclude_from_master` scene collection, outside the exported stable asset collection. Import only `Asset_massing_zundo_family_dentistry_f840e2b` into the master to avoid a site ground-plane collision.

## Candidate-to-source changes

- Replaced one campus-coordinate cuboid (about 15.26 x 24.65 x 16 m) with a local footprint-derived shell using the OSM eight-node outline, low parapet/roof, window groups, entry elements, interior partitions/equipment, and site approach. No original massing file was edited.
- Stable exported collection name retained: `Asset_massing_zundo_family_dentistry_f840e2b`.
- Build/re-render: `build.py`; raw OSM snapshot: `osm_way_887558318_raw.json`; exterior and schematic interior renders alongside this report.

