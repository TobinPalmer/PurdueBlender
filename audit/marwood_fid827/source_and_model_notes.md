# Marwood Cooperative — Purdue GIS FID 827

## Identity and address mapping

The current README has no direct Marwood asset mapping, so this build uses Purdue GIS `FID=827` as its source identity. The saved feature attributes identify `BUILDING_N=Marwood`, `BLDG_ABBR=SOM`, `OWNER=COOP`, and `ADDRESS=136 Littleton St`. The official Marwood site identifies its house as Marwood Cooperative and its homepage describes it as being at “136 Little Street” (the word `Littleton` appears shortened on that page). A City of West Lafayette permit report names “Marwood Cooperative” at `136 Littleton St` and lists parcel `79-07-20-304-004.000-026`, corroborating the GIS address. This is a documented site-text/address-format discrepancy, not an alternative feature match. No independent parcel-to-GIS overlay has been produced.

The official Marwood page’s saved house photo shows the “MARWOOD” name and a cream-and-brown Tudor-style residence, supporting the FID-to-house identity qualitatively. The GIS feature itself is also directly labeled Marwood. No other building/asset has been reassigned to this FID.

## GIS provenance and footprint

- Provider: Purdue University campus GIS, ArcGIS `BuildingShapesZip4`, FeatureServer layer 0.
- Layer metadata URL: `https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0?f=pjson`
- Exact FID 827 query: `https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query?where=FID%3D827&outFields=*&returnGeometry=true&outSR=4326&f=pjson`
- Raw snapshots retrieved 2026-10-28: `sources/purdue_gis_fid827_2026-10-28_4326.json`, `sources/purdue_gis_fid827_2026-10-28_3857.json`, and `sources/purdue_gis_layer0_metadata_2026-10-28.json`.
- Primary geometry is requested in EPSG:4326 (WGS 84). The comparison response uses ArcGIS WKID 102100 / latest WKID 3857 (Web Mercator). The model uses the approximate campus transform from `modular/AGENTS.md`: `X=(lon+86.9137)*111412.84*cos(40.4274°)` and `Y=(lat-40.4274)*111040`. This is a project compatibility approximation, not surveyed georeferencing.
- The FID 827 ring has 12 unique vertices. Its approximate local bounds are 24.293 m × 31.132 m; projected local shoelace area is 386.612 m² and perimeter is 93.983 m. The raw service `Shape__Area=668.265625` and `Shape__Length=123.589841` agree closely with the 3857 ring area/perimeter; their difference from the local values reflects projection scale at this latitude. These are source-polygon calculations, not survey measurements.
- The exact GIS ring is used as the model’s base wall perimeter. Fresh-open extracted ring error is 0.00002924 m after Blender float storage. The overlay and metric in `footprint_overlay.svg` / `footprint_comparison.json` explicitly label the match as by construction; they do not independently check placement or actual structural wall locations.

## Visual evidence

- Provider: Marwood Cooperative official website, `https://www.marwoodcooperative.org/` (raw page saved to `sources/marwood_official_homepage_2026-10-28.html`). The page image named `IMG_4999_Original.jpg` is saved at full resolution as `sources/marwood_official_house_photo.jpg`; direct image URL: `https://static.wixstatic.com/media/d1c9c7_ac607255dd844d78aca331fe74bc8045~mv2.jpg`.
- The photo supports a broad brown gabled roof, a central front-facing gable with an attic window and `MARWOOD` name, cream stucco, dark brown Tudor timber, dark-framed windows, a covered entry, brick foundation/basement, and a chimney. It is a single oblique facade view; its capture date, camera bearing, dimensions, roof pitch, and hidden elevations are unknown.
- The official Marwood “About” page HTML is preserved at `sources/marwood_official_about_2026-10-28.html`. Address reconciliation is further supported by the saved City of West Lafayette permit PDF `sources/west_lafayette_permits_2024_excerpt.pdf`, originally published at `https://d3n9y02raazwpg.cloudfront.net/westlafayette/b975d993-a8bd-45d0-9d8e-88abb0a20c41-4bbe3b86-c376-409e-a687-0c9d2429f6c9-1707151412.pdf`; its January 2024 entry names Marwood Cooperative at 136 Littleton St and includes the parcel identifier above.
- No floor plan, interior photo, roof survey, or verified facade bearing was located. Online/official prose and the single photo have not been used as dimensional evidence.

## Modeling method and estimates

The new standalone massing library is `modular/buildings/massing_marwood_cooperative_fid827.blend`, with stable scene `Building_massing_marwood_cooperative_fid827`, collection `Asset_massing_marwood_cooperative_fid827`, and root `House_Marwood_Cooperative`. It uses campus-local coordinates as required for simple massing libraries. Its bottom wall perimeter retains the 12-vertex FID 827 ring.

The main volume is a one-main-story house with a raised foundation/basement band, broad gabled roof, projecting central front gable, upper gable window, name lettering, entrance canopy/steps and chimney. Cream stucco, dark Tudor timber, dark brown shingles, brown brickwork and dark multi-pane windows follow the official photo’s general appearance. These details are approximate interpretations. The GIS `NUM_LEVELS=1` is consistent with one full main story but does not resolve the partly exposed basement or attic; `Extrution=12` is undocumented and was not used as a height. Roof pitch/ridge (7.35 m), chimney top (9.23 m), wall height, front orientation, window rhythm, entry sizes, basement exposure and all unseen elevations are estimates.

Interior geometry includes a single floor plate, generic room dividers, a stair placeholder and modest table/bed-like furniture blocks. The interior is schematic, not an as-built layout; room count, usage, circulation and dimensions are unverified. The fresh-open top-down cutaway is captioned “INTERIOR SCHEMATIC - NOT AS BUILT.”

## Fresh-open technical validation

Blender 5.2.3 LTS reopened the saved file and passed `fresh_open_validate.py` on 2026-10-28. The exact asset SHA-256, one scene object / one named collection object, mesh counts, source ring error, materials and dependency checks are recorded in `fresh_open_validation.json`. The root mesh has 8,657 vertices and 7,965 faces, with 12 procedural materials, zero saved cameras/lights, and no external image dependencies. Exterior, roof-oblique, top and captioned interior views are in `fresh_open_*.png`.

## Review status

The asset and evidence are ready for a separate read-only independent grade. Keep the asset frozen at the SHA recorded in `fresh_open_validation.json` during review. Do not mark the building finished or integrated until the grade is at least 8/10 and the coordinator completes master integration.
