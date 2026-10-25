# Neil Armstrong Hall — R9 source revision

## Roof appearance

R9 applies a pale neutral appearance to the existing low and high LiDAR-zone top faces. The registered 2023 orthophoto shows pale surfaces across the side wings and central high roof area, with an elongated red perimeter band in between. The existing mid-height band keeps its Mayflower red appearance. The roof-zone overlay is in [roof_zones_ortho_r9.png](roof_zones_ortho_r9.png).

This is a color-family correction only. It does not identify the roof substrate or establish exact construction. The 5-ft LiDAR classes still describe broad height zones, not precise architectural edges. No geometry or placement moved.

## Saved asset validation

The R9 file was reopened in Blender and compared against the saved R8 `.blend1` snapshot. All 445 collection objects match in mesh vertices, polygon indices, and transforms at the recorded comparison precision. The source root remains at `[0,0,0]`. See [validation_r9.json](validation_r9.json) for the asset hash and reopened material record.

## Review views

- [Exterior massing](renders_r9/exterior_lidar_silhouette_r9.png)
- [Roof appearance from above](renders_r9/roof_registered_plan_r9.png)
- [Geotag-side facade diagnostic](renders_r9/facade_geotag_approx_r9.png)
- [Northwest facade diagnostic](renders_r9/facade_nw_local_front_r9.png)
- [Atrium context](renders_r9/atrium_bridges_enclosure_r9.png)

The two eye-level views are diagnostic camera placements, not recovered photo bearings or facade registration. The orthophoto does not resolve elevations, facade stationing, atrium bridge endpoints, or stair paths. Those remain schematic or uncertain and were not altered in R9.

## Scope

Only the Neil Armstrong Hall source asset and dedicated audit files were changed. The master blend, shared indexes, manifest, README, and other building files were not edited.
