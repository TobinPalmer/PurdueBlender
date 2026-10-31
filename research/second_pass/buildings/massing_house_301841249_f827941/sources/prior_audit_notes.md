# Glenwood Cooperative — FID 794

## Identity and address reconciliation

The assigned GIS feature is `FID=794`, `BUILDING_N=Glenwood`, `BLDG_ABBR=SOGL`, `OWNER=COOP`, and `ADDRESS=503 University St`. This is consistent with Glenwood Cooperative. The historic Glenwood page says it moved to its current 503 University Street location in 1969; its contact page gives the fuller postal form `503 N University Street`. The differing street suffix detail is a normal address-format difference, not evidence that FID 794 is another building. The official Purdue Agriculture feature photo also labels the pictured house as Glenwood Cooperative.

## GIS provenance and plan method

- Provider: Purdue University campus GIS, ArcGIS `BuildingShapesZip4`, feature layer 0.
- Layer metadata: `https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0?f=pjson`
- Query used: `https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query?where=FID%3D794&outFields=*&returnGeometry=true&outSR=4326&f=pjson`
- Raw snapshots saved at retrieval on 2026-10-28: `sources/purdue_gis_fid794_2026-10-28_4326.json`, `sources/purdue_gis_fid794_2026-10-28_3857.json`, and `sources/purdue_gis_layer0_metadata_2026-10-28.json`.
- The feature response requested in EPSG:4326 (WGS 84). The 3857 response uses ArcGIS WKID 102100 / latest WKID 3857 (Web Mercator). The project compatibility transform is the approximate local campus conversion documented in `modular/AGENTS.md`: `X=(lon+86.9137)*111412.84*cos(40.4274°)`, `Y=(lat-40.4274)*111040`.
- The 8-vertex GIS polygon is used as the lower wall perimeter by construction. Fresh-open validation finds a maximum nearest outline vertex error of 0.0000163 m. That is an internal source-to-model check, not independent placement or survey verification. The model bounds include porches and stairs, so they are deliberately larger than the polygon bounds.
- `Shape__Area` is 471.3789 square metres and `Shape__Length` is 100.9425 metres per the ArcGIS feature response. They are retained as GIS attributes and are not treated as surveyed facade measurements. `NUM_LEVELS=1` conflicts with the visible multi-level source photograph. `Extrution=12` is undocumented and was not used as a measured height.

## Visual sources

- Purdue FSCL official hero image, downloaded as `sources/purdue_fscl_glenwood_hero.jpg`; source image URL: `https://www.purdue.edu/fscl/images/_hero/fscl-glenwood-hero.jpg`. It supports light horizontal siding, dark shutters, repeated windows, a prominent entry portico/sign, dormer-like upper roof forms and a low masonry foundation. It does not provide measured elevations or all-side coverage.
- Purdue Agriculture story “Cooperation is Key”, `https://ag.purdue.edu/department/agecon/undergraduate-program/success-2025-26/cooperation-is-key.html`; the saved house photograph is `sources/purdue_ag_success_glenwood_house.jpg`. This is an additional identity/context image but is tree-obscured and not used for dimensions.
- Glenwood Cooperative historic about page: `https://web.ics.purdue.edu/~glenwood/about.html` (page indicates move to 503 University Street in 1969). Contact page: `https://web.ics.purdue.edu/~glenwood/contact.html` (503 N University Street).
- A 2008 Indiana Connection view is saved as `sources/glenwood_house_2008_indiana_connection.jpg`; its small resolution supports the broad white-house identity only.
- `glenwood_legacy_history.jpg` and `glenwood_legacy_media.jpg` are old house-site media/graphics, not reliable building elevations; they were excluded from shape/material evidence.

## Modeling choices and limitations

The mesh preserves the stable asset path, scene, collection and root object. Its bottom perimeter follows the source ring. Siding, charcoal roof, brick foundation, dark shutters, blue-grey glazing, white trim, purple Glenwood entry sign, portico and multiple dormer/window forms are photo-supported at the level of general appearance. Window count/spacing, front orientation, story interpretation, roof pitch, dormer dimensions, total height (9.15 m), porch/steps, and all hidden elevations are illustrative. No compass bearing or verified elevation/roof measurement was found. The GIS record's `NUM_LEVELS=1` is kept as an explicit source conflict; the visible photograph suggests a taller multi-level form. The 40-foot GIS extrusion is not asserted.

Interior floorplates, room dividers, stairs, generic furniture and circulation are schematic placeholders, not as-built. There is no sourced floor plan or interior image. `schematic_interior_plan.png` labels this status and uses the GIS outline solely as the drawing perimeter.

## Fresh-open technical validation

Blender 5.2.3 LTS reopened the saved `.blend` and passed `fresh_open_validate.py` on 2026-10-28. The exact asset SHA-256, stable scene/collection/object names, one-mesh object count, materials, footprint check and dependency check are recorded in `fresh_open_validation.json`. The saved library contains one mesh object (17,364 vertices, 15,735 faces), 12 procedural materials and no external image dependencies. Fresh-open exterior, roof-oblique, top, and schematic interior renders are included in this folder. Preview cameras/lights are temporary and are not retained in the asset.

## Independent grade status

Separate read-only independent review passed at **8.6/10** on asset SHA-256 `d0b2fa56be3b5db1352eddc202b83204012cf18c21b3ce3db9866e793e0e6319`. See `independent_grade_codex_2026-10-28.md` for the scorecard. The reviewer retained the limitations above; the pass does not convert estimated roof, height, facade, placement or interior details into verified measurements. The coordinator still owns master integration.
