# Purdue Village Administration Building (PVAB)

Stable ID: `massing_purdue_village_administration_building_3faae6c`  
Asset: `modular/buildings/massing_purdue_village_administration_building_3faae6c.blend`  
Exported collection: `Asset_massing_purdue_village_administration_building_3faae6c`

## Build

From the repository root, run with Blender 4.5 or later:

```powershell
blender --background --python modular/buildings/build_massing_purdue_village_administration_building_3faae6c.py
```

The builder validates Purdue-linked ArcGIS FID 524 / PVAB, transforms its footprint into the project's approximate local meter frame and rebuilds the single mesh object. The archival Purdue Archives building 74 photograph provides the brick, pale ribbed cladding, glazing, entrance and canopy evidence. Its viewing bearing is unknown, so the long frontage alignment is a documented best-fit assumption. Height is estimated at 4.2 m; roof surface is unverified.

## Evidence and validation

- `evidence_record.json` summarizes provenance, source comparisons, geometry changes and uncertainty.
- `sources/arcgis_fid524_raw.json` preserves the official map feature response; `sources/osm_way_283274993_raw.json` is the independently named OSM footprint snapshot.
- `sources/historic_database_record74.html` and `sources/historic_database_record74_payload.json` preserve the official archival building record. `sources/purdue_archives_building74.jpeg` is its associated building-specific photograph.
- `sources/purdue_archives_photo_evidence.json` records direct visual observations and photo limits. `sources/ua149_archival_slide_inventory.json` documents a separate cataloged slide holding; those slides were not digitized or used as geometry evidence.
- `reopen_validate.py` freshly opens the saved library and checks the one-object export, GIS-ring agreement, structural footprint, evaluated bounds, and external image dependencies. Results are in `reopen_validation.json`.
- `preview_facade.png` shows the photo-informed frontage, `preview_oblique.png` shows the shell and parapet line, and `preview_top.png` shows the plan.

The original 16 m generic block has been replaced with the official 14-vertex GIS boundary (2,481.327 m²) and a 4.2 m estimated shell. Photo-backed facade details are shallow overlays on the same mesh. Height and floor count remain unverified measurements; roof surface, photograph date and compass orientation remain unknown. This revision is ready for a fresh independent grade; it is not yet accepted as finished.
