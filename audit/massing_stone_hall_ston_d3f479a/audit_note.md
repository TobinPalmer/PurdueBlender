# Stone Hall (STON) source review and build notes

## Identity and assignment

- Root `README.md` assigns `stone hall ston` to Rossen and lists the asset `modular/buildings/massing_stone_hall_ston_d3f479a.blend`.
- The manifest stable ID is `massing_stone_hall_ston_d3f479a`, exported collection `Asset_massing_stone_hall_ston_d3f479a`, expected scene `Building_massing_stone_hall_ston_d3f479a`, object `Stone Hall (STON)`.
- Purdue GIS FID 240 identifies `BLDG_ABBR=STON`, `BUILDING_N=Winthrop E. Stone Hall`, address `700 Mitch Daniels Blvd`; identity was checked by exact code and name, not nearest-neighbor position alone.

## Evidence and supported geometry

- The raw official GIS feature and layer metadata are preserved in `sources/`. The feature's single polygon ring was transformed from WGS84 to campus XY using the exact approximation in `modular/AGENTS.md`; this is not a surveyed CRS transformation.
- The raw feature's `Shape__Area=3834.203125` and `Shape__Length=299.5811154716871` conflict with the ring-derived campus XY area (~2218.175 m²) and perimeter (~227.855 m). The builder uses the feature ring, not those inconsistent summary fields. The discrepancy is preserved as a source-quality limitation.
- GIS supports a source-linked plan outline, not a certified wall survey. The original massing file's rectangular envelope was only an AABB match; this build uses the GIS outline itself, preserving its jogs and overall form.
- Purdue Archives record 71 and linked Purdue eArchives photos 1371-1374 were visually inspected. The 1959 views support a brick-faced institutional block, light stone/concrete pilasters and bands, repeated rectangular windows, central formal entrance, and a simple low roof edge. The model uses these as a stylized interpretation; it is not a measured facade replica.
- The official GIS feature gives `NUM_LEVELS=6`, `Extrution=45`, `B`, `G`, and `F01`-`F04` values. The four `F` fields drive four facade bands; the source's two additional `B`/`G` values are retained in metadata but are not drawn as separate visible stories because the source does not explain their datum, units, or above/below-grade relationship. For a visualization only, the builder interprets `Extrution=45` as feet (13.716 m) and labels the height uncertain/estimated. No elevation/surveyed top-of-roof source was located.

## Limitations

- Exact roof height and floor-to-floor elevations remain unverified. `Elevation=622.4` is not used as building height or ground-relative Z.
- The photo-derived window and trim rhythm is qualitative, historical evidence. No detailed measured elevations or current facade survey were found.
- R2 responds to the 1959 archive images by using taller window openings, a wider three-panel entrance surround, and broad shallow entry steps visible in the entrance photo. These dimensions remain photo-informed estimates.
- The feature polygon is the official Purdue campus GIS footprint. It may represent a mapped building envelope rather than structural wall lines; exact wall registration, courtyards, and overhangs remain uncertain.

## Validation status

The builder records its run output in `build_validation.json` and renders `preview/stone_hall_isometric.png`. A separate Blender reopen validation must be run after the build, and an independent grader must assess the asset and evidence before it is accepted. No geometry or facade dimension should be reported as a measured value unless supported by a new primary source.
