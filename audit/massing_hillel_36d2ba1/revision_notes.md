# Hillel revision notes

## Identity and scope

- Stable ID: `massing_hillel_36d2ba1`; root README assigns the building to Rossen.
- The manifest path, scene, collection, source object name `Hillel`, and campus-world coordinate frame are retained.
- ArcGIS feature `SOHIL` / FID 803 identifies Hillel Foundation at 912 W. State Street. County documentation identifies the 912 State/Waldron corner.

## r2 source-backed revision

- Added the official Purdue Hillel Spring 2022 newsletter PDF and page 1 photo snapshot. The photo shows the low single-storey form, light buff masonry, broad shallow flat/low-slope roof edge, repeated tall framed window bays, and a prominent masonry/signage panel. See `source_record.json` for source method and limits.
- Replaced the old muted red/charcoal look with light buff masonry and a pale roof edge. Added taller, multi-pane window bays and entry glazing. The 2019 minutes establish the front faces west toward Waldron; the newsletter image has no compass registration, so the entry location and opening dimensions remain illustrative.
- Kept feature 803's 12-vertex pre-addition wall footprint unchanged. County records document a proposed 845 sq ft addition and approved variances, but no permit, as-built, or completion evidence was found. Its completion remains unresolved, and the 2022 newsletter is not treated as proof.
- Kept 3.6576 m as a display placeholder only. It is numerically based on the prior interpretation of GIS `Extrution=12`, whose units are undocumented; this is not a measured or source-verified height.
- The roof overhang is a visual approximation (about 0.7 m) from the photograph; no measured pitch, height, or eave dimension is available.

## Validation

- `hillel_exterior_oblique_r2.png`, `hillel_waldron_front_r2.png`, and `hillel_roof_top_r2.png` show the updated asset.
- `reopen_validation.json` records direct reopen checks, evaluated geometry, collection, bounds, mesh counts, and portability. The updated asset was rebuilt and reopened with Blender 4.5.15 because no Blender 5.2 executable was available locally; the starting asset had been saved by Blender 5.2. This is a file-version downgrade and should be checked for compatibility in the project's Blender 5.2 environment.
- The independent r1 review remains untouched. No shared indexes, master scene, placement marker, or other building files were edited. Fresh independent grading is pending.
