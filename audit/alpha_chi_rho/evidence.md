# Alpha Chi Rho massing evidence

**Asset:** `massing_alpha_chi_rho_0cb591a`  
**Owner:** Rossen (per root README assignment)  
**Asset file:** `modular/buildings/massing_alpha_chi_rho_0cb591a.blend`  
**Collection / scene:** `Asset_massing_alpha_chi_rho_0cb591a` / `Building_massing_alpha_chi_rho_0cb591a`

## Sources and measurements

1. **Purdue University BuildingShapes ArcGIS FeatureServer, layer 0, feature 775.** The saved query snapshot is `sources/purdue_gis_FID775_alpha_chi_rho_2026-10-26.json`; layer metadata is `sources/purdue_gis_building_shapes_metadata_2026-10-26.json`. Query URL: <https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query?where=FID%3D775&outFields=*&returnGeometry=true&outSR=4326&f=pjson>. Retrieved 2026-10-26. The feature identifies `Alpha Chi Rho`, abbreviation `SOACR`, address `27 Russell St`, one level, Greek ownership. Query geometry is WGS84 longitude/latitude (EPSG:4326); the layer itself is Web Mercator (EPSG:3857). It supplies a 14-vertex closed outline, shape length 144.642 m, and Web Mercator shape area 854.402 m². The latter is distorted at this latitude and is not used for local plan area.
2. **Purdue Libraries Archives and Special Collections, *1978 Debris*, item PUD00092 / item 46421.** Record: <https://earchives.lib.purdue.edu/digital/collection/debris/id/46421>. Saved item metadata and OCR are in `sources/purdue_archives_debris_item_46421_2026-10-26.json`. The archive names the Alpha Chi Rho chapter and dates the yearbook to 1978. The accompanying historic house photo informed only the illustrative horizontal siding and window language, not current facade dimensions. The archive's rights notice makes reuse subject to the user's copyright responsibilities; the photo itself is not included in this deliverable.
3. **Purdue GIS feature metadata.** A source snapshot includes layer schema and service item ID `500b3d06f76944b6a280906371fc97eb`; its `Extrution=12` field has no documented unit or measurement method in the layer schema. It is not treated as a measured height.

The GIS ring was transformed to campus coordinates with the project approximation: `X=(lon+86.9137)*111412.84*cos(40.4274°)`, `Y=(lat-40.4274)*111040`, Z up, meters. This is a local approximation, not a surveyed projected CRS. Approximate GIS ring area after this transform is 494.291 m². The modeled shell uses the same 14 plan vertices; the saved-file check finds a maximum vertex difference of about 0.000016 m (single precision mesh storage). Horizontal plan position, shape, and orientation therefore follow the matched official feature. Source ground elevation `625` is recorded but no vertical datum is specified, so the model's local ground is Z=0 and elevation is not applied.

## Build and checks

- `../..` manifest confirms the stable ID, expected asset path, one named object, collection, scene, and `kind: massing`; simple massing remains in campus coordinates.
- Builder: `../../modular/buildings/build_massing_alpha_chi_rho_0cb591a.py`. It rebuilds a single mesh object and writes the preview and build stats. Blender 4.5.15 LTS completed the build and render successfully; see `build.log` and `build_result.json`.
- The shell is extruded 3.8 m above local ground and capped with a 0.35 m flat roof, for a 4.15 m maximum height. Both heights are modeling estimates; the one-level attribute is the only vertical source evidence. Roof form, current openings, porch dimensions, exact materials, and facade rhythm remain illustrative/unverified. Decorative siding courses, windows, door, and porch slightly extend outside the GIS wall outline.
- `validate_asset.py` reopened the saved asset and checked the expected scene, collection, one mesh object, material slots, external image dependencies, and all GIS shell vertices. Result: `reopen_validation.json` (`PASS`).
- `export_reopen_probe.py` appended the named collection into a clean Blender scene, saved a standalone probe, reopened it, and confirmed one `Alpha Chi Rho` mesh with seven materials and no external image dependencies. Result: `export_reopen_probe.json` (`PASS`). Probe file: `clean_scene_import_probe.blend`.
- Preview render: `alpha_chi_rho_preview.png`.

## Remaining uncertainty

No dimensioned current elevation or roof plan was found in the evidence saved here. One GIS story is a source attribute, not a verified height. The historic 1978 image does not establish current facade condition. Confirm exterior appearance, roof, floor-to-eave height, and exact entrance placement against current site imagery or measured drawings during independent grading. The intentionally neutral roof and simplified windows/porch are not presented as verified architectural facts.
