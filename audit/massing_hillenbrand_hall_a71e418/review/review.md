# Hillenbrand Hall — build checkpoint r1

## Identity and scope
README assigns Hillenbrand Hall to Rossen. Stable ID `massing_hillenbrand_hall_a71e418`; expected asset, scene, collection and object names are preserved. The asset remains a campus-coordinate massing library with identity transform.

## Source-to-model comparison
Purdue Facilities GIS BuildingShapesZip4 feature FID 259 identifies “Hillenbrand Residence Hall” at 1301 3rd Street. Its 62-vertex shell is used for the rebuilt footprint after the modular project’s stated WGS84-to-campus-meter conversion. GIS shell bounds are X -1161.3981 to -1043.9688 m and Y -137.0147 to -19.5937 m. The transformed footprint overlay matches the current Esri image roof outline closely. This validates a source match and horizontal shape against map imagery, but is not survey registration.

Purdue Residences confirms the building name, address, 1993 opening, suite-style residential function and dining court on the ground floor. Its 2018 page photo documents a red-brick entrance with glazing and a green standing-seam roof pavilion. The official GIS feature has level/extrusion fields, but they do not establish a consistent roof elevation; the 30.4 m top remains an unverified visual estimate retained from the starting asset.

## Geometry and validation
The prior white, featureless extrusion has been replaced by the GIS shell and a single mesh with schematic red-brick facade, repeated dark window bays, pale level courses, flat roof massing and a small green entrance canopy. The scene, collection, object identity, campus frame, and one-object export contract remain unchanged. Direct reopen in bundled Blender 5.2.0 passed all checks (one mesh object, identity transform, no modifiers, no external images). Final render: `review/preview_r1.png`. Direct reopen facts: `review/direct_reopen_r1.json`.

## Remaining uncertainty
No measured elevation or confirmed story count was found. Roof articulation and rooftop details are simplified. Window rhythm and the entry canopy dimensions/location are illustrative; the source image does not provide a compass orientation. The GIS feature includes connected wings, represented as a continuous source shell. The bundled Blender 5.2.0 warned that the original file was authored in Blender 5.2.45; its simple mesh/material structure reopened and rendered, but an independent current-version check remains useful.

Source URLs, CRS, retrieval dates, methods and limitations are recorded in `sources/source_record.json`.
# Hillenbrand Hall — iteration r3 (after independent r1 review)

## Evidence-led correction
The independent r1 reviewer scored the asset 7.5/10 and flagged unsupported 30.4 m height/story count, missing roof articulation, and schematic facade/entry geometry. The 30.4 m top and speculative entry canopy have been removed. Purdue's 2019 Treasurer project summary (saved as `sources/purdue_treasurer_hillenbrand_two_towers_2023.pdf`, page 3 rendered to `sources/treasurer_hillenbrand_page-3.png`) identifies two towers of eight floors each, each with two wings, connected at first floor and basement by common areas and dining hall. The two upper masses now show approximate intersecting wings, based on that statement and the distinct aerial roof masses. Facade bays and roof caps remain schematic; exact dimensions are not claimed.

## Plan and height limits
The full ground-level shell still follows Purdue Facilities GIS BuildingShapesZip4 FID 259. The upper tower positions and wing proportions are interpreted from the Esri orthophoto overlay, not measured from a design plan. The GIS height fields have undocumented units and conflicting values (`R=83.2`, `Extrution=108`). For a provisional visual scale only, the model interprets 83.2 as feet, setting the roof peak at 25.35936 m; this is explicitly an estimate, not a verified building height. GIS floor-level increments are likewise used only as an approximate vertical rhythm. The official PDF supports eight floors, but its project documents are proposed-project evidence rather than as-built confirmation.

The entry canopy/door is omitted because the official entrance photograph does not establish its compass-facing wall or dimensions. Brick color and glazing are photo-informed. Window count, size, rhythm, roof pitch and top equipment remain unverified.

## Final reopen and render
Rebuilt with local Blender 5.2.0 from `modular/buildings/build_massing_hillenbrand_hall_a71e418.py`; final preview is `review/preview_r3.png`. Direct reopen validation is recorded in `review/direct_reopen_r3.json` and `review/reopen_validate_r3.log`: expected scene, collection, object and asset ID retained; one mesh; identity transform; zero modifiers; no external image dependencies; all checks passed. Mesh has 8,714 vertices and 2,133 polygons. World bounds are X -1161.3981 to -1043.9688 m, Y -137.0147 to -19.5937 m, Z 0 to 25.35936 m. Render was visually inspected after rebuild.

The model intentionally stays within the proposed design evidence and GIS shell. Parcel placement is still sensitive to the local GIS transformation and aerial registration; floor count is documented in a project summary, while absolute elevation, exact facade geometry and as-built status remain uncertain.
