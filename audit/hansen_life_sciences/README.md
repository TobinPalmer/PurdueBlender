# Arthur G. Hansen Life Sciences Research Building (HANS)

## Audit result — 2026-10-27

Asset `modular/buildings/hansen_life_sciences.blend`, stable ID `hansen_life_sciences`, was opened in Blender 5.2.3 and inspected without changing its geometry. It contains the expected `Asset_hansen_life_sciences` collection and `Building_hansen_life_sciences` scene. A fresh-open render is saved as `preview_oblique.png`.

### Footprint and placement check

Purdue Campus GIS BuildingShapesZip4 FID 237 identifies HANS by name, abbreviation and address. The WGS84 ring was transformed into project campus coordinates using the project’s documented local approximation, then offset by manifest origin `[-288, -570]` to compare with the local structural slab outline. The evaluated basement slab perimeter has 26 vertices, matching the 26 unique GIS vertices. The polygon IoU is 0.99999899 and symmetric Hausdorff distance is 0.000030 m. This confirms that the asset’s structural plan shape, orientation and local frame reproduce the GIS feature. This is a consistency check, not independent survey validation; GIS building-shape data is not a surveyed wall line.

The transformed plan bounds are approximately 59.779 x 46.049 m. The model includes a basement, four above-grade floor plates, a flat roof/penthouse, rooftop mechanical details, and brick/glazing facade treatment. It has detailed openings, window mullions, bandcourses, entrance/loading elements, roof plant and material assignments. See `evidence.json` for raw-source URL, provider, feature ID, retrieval date, CRS, transform, measurements and uncertainty.

### Source conflicts and limitations

Purdue’s historic database describes four stories. The 2013 Purdue emergency plan lists basement and levels 1 through 4, while the GIS feature has `NUM_LEVELS=6`, `CountOfFLO=6`, `Extrution=60`, and `R=67` without documented units. The asset models basement plus four above-grade floors. Exact grade-to-roof height remains unverified: the model’s roof deck is at z=17.5 m and penthouse/parapet reaches z=20.572 m; roof exhaust stacks reach z=24.147 m. No evidence supports treating those rooftop details as the building’s height.

Purdue’s GIS floorplan attribute points to a restricted internal server location. No room layout has been invented or claimed. Published as-built elevations/sections were not located, so facade details and exact height remain estimates where listed in the evidence record. The Purdue-hosted events location page includes a 2022 photo attributed to a user post; it is only a visual cross-check, not measured or authoritative architectural evidence.

No geometry edit was warranted from the available evidence: the structural footprint already matches the official GIS outline at sub-millimeter precision. The asset SHA256 is recorded in `evidence.json` for grading against the frozen version.
## Source availability note

The official 2013 Purdue emergency-plan PDF is discoverable in Purdue search with floor-level text, but its indexed URL currently returns a Purdue “Page Not Found” response when fetched directly. The source is recorded in the evidence file with this retrieval limitation; no copy of the PDF was fabricated or included.

Purdue Archives' entity record dates the building from 1983, while Purdue's campus historical timeline lists completion in 1984. The manifest uses 1983. This date conflict does not change the modeled geometry and remains unresolved.


## Independent grade

R1 independently passed at 8.0/10 for exact SHA-256 `fe0bc4834a9a14f3300587fff02d75171a7a54cc25ba6a12fd99f6c44526e552`; report: `independent_grade_r1/grade_report.md`. The score confirms the FID 237 structural plan, while roof/equipment heights, the GIS/archive floor-count conflict, facade details and interior CAD remain uncertain or unavailable. Master marker/link validation is recorded separately by the coordinator.


The coordinator confirmed the `Placement_hansen_life_sciences` marker, expected source library, 816 objects and manifest bounds in the fresh-open master audit `../master_integration_2026-10-27_r5.json`.
