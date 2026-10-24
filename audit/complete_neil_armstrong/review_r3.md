# Neil Armstrong Hall source review — R3

## R3 evidence pass

I searched again for building-specific plans and compared the GIS footprint with the saved model using an official Indiana orthophoto. Purdue Archives' finding aid still identifies the September 2004 development-plan set (Box 348, item 5), but the online finding aid does not contain the drawings. Web-accessible search did not surface dimensioned as-built elevations or floor plans. No plans were inferred from a student project, rendering, or unrelated archive record.

The Indiana Geographic Information Office catalog identifies the covering source image tile as `in2023_29971887_06`, acquired in 2023 at six-inch pixel size. I overlaid the Purdue building polygon (FID 642) and the source model's wall edges in the tile's EPSG:3857 extent. The result is [gis_ortho_shell_comparison_r3.png](gis_ortho_shell_comparison_r3.png); the raw imagery and catalog metadata are preserved in `sources/`.

## What the comparison resolves

The GIS source is one continuous building polygon, not several unrelated feature polygons or obvious detached canopy features. The 2023 imagery shows the large connected building with several wings/roof volumes arranged around an atrium/courtyard. The model's current structural wall edges form only a narrow central bar. Its 126.0 × 26.5 m wall bounds remain substantially smaller than the 162.3 × 56.8 m GIS ground footprint. The likely cause is omitted wings and depth in the modeled shell, rather than a GIS aggregate of unrelated buildings.

The aerial is useful for identity and broad plan composition. Although supplied by an orthophoto service, elevated roofs and cantilever edges can be displaced relative to the ground footprint; the image cannot supply exact wall lines or vertical positions. The GIS polygon also does not expose the individual floor plans, courtyard opening at every level, vertical circulation, or elevations.

## Geometry decision

I did not stretch the current shell or extrude new wings in R3. The evidence now confirms a significant missing-plan-coverage problem, but it does not give the registered floor-by-floor wall boundaries and heights needed to build those wings faithfully. The FRP project description supports three stories and an elaborate cantilever roof, not exact floor elevations or outer-wall heights. The two atrium bridges remain schematic for the same reason. Adding uniform volumes would hide the mismatch while inventing floor geometry.

The strongest next step is to inspect the September 2004 Box 348 item 5 drawings or obtain a current registered as-built plan/elevation. Until then, the ground GIS trace should remain explicitly a footprint reference, and the shell/roof/circulation remain incomplete or schematic.

## Validation

The saved source asset was reopened read-only in Blender 5.2.3 to extract wall edges and confirm the scene, exported collection, 444-object count, and local root. The local shell bounds remain [−63, 63] m X, [−29.689, −3.189] m Y, and [0, 19.5] m Z; no object was moved, scaled, or saved in R3. The R2 model review renders remain valid but unchanged. The new comparison plate is a source/evidence render, not an updated architectural render.

- [R3 evidence](evidence_r3.json)
- [R3 validation](validation_r3.json)
- [Registered GIS/orthophoto/model comparison](gis_ortho_shell_comparison_r3.png)
- [Orthophoto tile catalog snapshot](sources/ortho_catalog_item_neil_2023_r3.json)
- [Orthophoto extent export](sources/indiana_current_ortho_neil_extent.png)
- [Read-only shell-edge extraction](sources/shell_wall_edges_r3.json)
- [Validation script](validate_r3.py)
- [Shell-edge extraction script](export_shell_edges_r3.py)
