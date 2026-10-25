# Neil Armstrong Hall — R10 source revision

## Slab roof appearance

R9 applied the pale/red height-zone colors to the LiDAR meshes, but an independent reviewer found the separate East and West Roof Slab objects still showed broad red tops over areas that appear pale in the orthophoto. R10 corrects those top-face appearances by sampling each registered top-face centroid against Indiana's 2023 imagery: 83 of 96 faces per slab receive the pale neutral appearance, and 13 faces per slab with clear red-family imagery retain red ACM. Side faces and all geometry stay as they were.

The pixel classifications are recorded in [roof_slab_material_samples_r10.json](roof_slab_material_samples_r10.json); [roof_slab_footprints_ortho_r9.png](roof_slab_footprints_ortho_r9.png) compares their projected top faces with the aerial. This does not identify roofing material.

The two slab footprints only overlap about 56–57% with official GIS footprint FID 642. The GIS polygon is not an architectural roof plan and cannot alone justify trimming the possible cantilever/overhang, so R10 makes no geometric cut. Their exact extents remain unresolved.

## Validation and review

Blender reopened R10 and compared all 445 collection objects against the R9 backup. Mesh vertices, polygon indices, transforms, and root local position `[0,0,0]` match. Only roof slab top-face material assignments changed. See [validation_r10.json](validation_r10.json) and [evidence_r10.json](evidence_r10.json).

- [Exterior massing](renders_r10/exterior_lidar_silhouette_r10.png)
- [Roof appearance from above](renders_r10/roof_registered_plan_r10.png)
- [Geotag-side facade diagnostic](renders_r10/facade_geotag_approx_r10.png)
- [Atrium context](renders_r10/atrium_bridges_enclosure_r10.png)

The eye-level camera is diagnostic only; no recovered photo bearing or calibrated facade registration is available. Facade stationing, roof structure, atrium bridge endpoints, and continuous stair circulation remain unsupported by the available registerable sources. R10 addresses color appearance only.

## Scope

Only the Neil Armstrong Hall source asset and its dedicated audit files were edited. The master blend, shared indexes, manifest, README, and all other building assets remain untouched.
