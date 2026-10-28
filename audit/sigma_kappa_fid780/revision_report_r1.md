# Sigma Kappa FID 780 — revision report R1

## Current candidate

- Asset: `modular/buildings/massing_house_301840869_1b80ace.blend`
- SHA-256: `74DE8B51A91D6BAD5F8B40EB9282D77E221EC4EDB0AAABE82F08BCFE335C1430`
- Blender: 5.2.3 LTS

## Model and evidence

- Retained the 21-unique-vertex GIS footprint as the building's lower-story base. The modeled base ring has 21 vertices at Z=0; nearest-vertex deviation from the locally projected GIS ring is 0.000015 m. This is a by-construction match, not independent survey validation.
- Added estimated red-brown brick stories, restrained pale base/story courses, repeated light-trimmed windows, a light portico and entrance steps, a charcoal roof field, and four dormers. Their form is a qualitative interpretation of the cited secondary illustration, not a measured elevation.
- Added a one-level schematic interior insert with an intact floor plate, low partitions, and generic furniture blocks. Partitions and furniture have stronger contrast in the plan preview; the camera scale was corrected so the entire GIS outline is visible. No room uses, dimensions, or as-built layout are claimed.
- Exterior, west-facing interpretation, and cutaway previews are captioned with the evidence limits. `source_footprint_diagnostic.png` displays the numbered source GIS ring.

## Validation

Fresh-open validation passed in Blender 5.2.3 LTS. The expected scene and asset collection each contain one mesh object, `House_301840869` (2,724 vertices, 4,083 edges, 2,017 faces; 10 materials). There are no saved camera or light objects and no unpacked external image dependencies. The report is in `fresh_open_validation.json`.

The resulting bounds include portico/step and roof projections beyond the source ring: X [-513.762, -482.447] m, Y [162.716, 201.270] m, Z [0, 13.287] m. GIS footprint-only metrics from the local approximation are area 623.97 m² and perimeter 133.40 m. The source service attributes (area 1078.621 m² and perimeter 175.430 m) do not match that approximation and were not used as geometry controls.

## Limits and review request

`NUM_LEVELS=1` conflicts with the two-level secondary illustration; `Extrution=12` has no documented units or definition. The upper story, roof, dormers, materials, window rhythm, chimney, and west-facing entry are interpretive. The interior is schematic and the cited historic archival item is a catalog listing without the scanned image. The unrelated Panhellenic image is excluded. Please assess identity/footprint integrity, exterior/source fidelity, material/render readability, interior legibility with honest uncertainty, and library cleanliness. Do not treat the shell match as independent survey validation.
