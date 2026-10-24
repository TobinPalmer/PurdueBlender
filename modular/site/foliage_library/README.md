# Project-local foliage and site asset library

`engineering_foliage_library.blend` is a packed, reusable Blender Asset Browser library built by `build_engineering_foliage_library.py`. Place this folder under `modular/site/foliage_library`; the Engineering Mall patch links it using a project-relative path.

## Included assets

- Poly Haven CC0 1.0: `tree_small_02`, a material-delimited LOD2 mesh at a fraction of the source LOD1 face count. It preserves the textured broadleaf canopy and shares mesh data across placements.
- Poly Haven CC0 1.0: `shrub_02` variants A–D and `shrub_04` variants A–D, selected at LOD2. `shrub_04` is very small (groundcover scale), so the Engineering patch currently uses `shrub_02` for mapped shrub records.
- Poly Haven CC0 1.0: `fir_sapling` variants A–C. A baked 24% decimation is saved as LOD2 for the mapped evergreen records.
- Poly Haven CC0 1.0: `fern_02` variants A–D and selected small/mid/tall `grass_medium_01` LOD2 tufts. They are available for future evidence-based plant beds; the Engineering patch does not scatter them over lawns.
- Poly Haven CC0 1.0: `grass_ground` 1K PBR material used on OSM grass parcels and `asphalt_01` 1K PBR material used on OSM asphalt/service paths. Both are packed, and their shader coordinate links and visual scale are checked in the comparison render.
- Existing PurdueMap source materials: walkway concrete, plaza concrete, brick pavers, lawn, landscape green, asphalt and curb from `modular/site/campus_site.blend`.
- Existing PurdueMap prop assets extracted from `campus_site.blend`: fountain bench segment, granite bollard, bollard nozzle cap, and an assembled lamp-post shaft/base. These are catalogued for reuse and are not placed by this patch; they retain PurdueMap project provenance and are not labeled CC0.

## Source prerequisites and provenance

The reproducible builder expects the source `.blend` files and texture directories below in `source/`. These were supplied in the project workspace and are kept beside the output so the library can be rebuilt. Poly Haven assets are CC0 1.0; source pages:

- [tree_small_02](https://polyhaven.com/a/tree_small_02)
- [shrub_02](https://polyhaven.com/a/shrub_02)
- [shrub_04](https://polyhaven.com/a/shrub_04)
- [fern_02](https://polyhaven.com/a/fern_02)
- [grass_medium_01](https://polyhaven.com/a/grass_medium_01)
- [fir_sapling](https://polyhaven.com/a/fir_sapling)
- [grass_ground](https://polyhaven.com/a/grass_ground)
- [asphalt_01](https://polyhaven.com/a/asphalt_01)

The builder packs every referenced texture into the library. `blender_assets.cats.txt` defines stable Asset Browser catalogs; collections and reusable materials are marked as assets with their source/license recorded in custom properties. The index uses mixed-license wording; CC0 applies only to Poly Haven assets, while PurdueMap site props/materials retain provenance to `campus_site.blend`.

## Engineering Mall patch use

The patch keeps each mapped plant object's name, inventory ID, species, provenance, measured/inferred fields, and project XY. A plant Empty instances a source collection at the same location; only the explicit visual instance scale and rotation affect the rendered asset. Deciduous broadleaf trees use the shared tree composite, mapped evergreen trees use the decimated fir variants, and shrubs use the shrub LOD2 variants. Turf remains a single OSM parcel surface rather than a dense grass scatter.

The broadleaf LOD2 contains 148,509 faces; fir variants contain about 31,880–37,477 faces each. Collection instances share mesh datablocks, but each placement still adds geometry to the evaluated/rendered scene, so the broadleaf proxy has a meaningful render cost at campus scale. Consider adding distance-based lower LODs before using this same tree asset across the full campus master. Other large source LODs and geometry-node source objects are excluded from the working library. The broadleaf source silhouette is naturally airy; it is a shared generic deciduous proxy, not a species-specific reconstruction.

