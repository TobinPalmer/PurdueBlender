# John T. McCutcheon Residence Hall — R3 Evidence and Review Notes

**Updated:** 2026-10-24  
**Asset:** `modular/buildings/mccutcheon_hall.blend`  
**Collection:** `Asset_mccutcheon_hall`  
**Scope:** Dedicated McCutcheon asset and `audit/mccutcheon_hall/` only. No master, manifest, README, shared script/index, other building, commit, or push.

## R3 work

R3 prioritizes the newly available authoritative facade photo and the evidence gap around height. No building geometry or interior was changed. I did not create rooms or circulation from a generic housing description.

- Added a procedural clear-day sky to the standalone `Building_mccutcheon_hall` scene, made `Cam_Hero_Perspective` active, and set its lens to 30 mm so the entire building fits in the saved hero frame. The exterior collection's existing sun object parameters were preserved. The daylight world belongs to the asset's standalone scene; it is not a master-scene edit.
- Rendered a campus-scale hero view and an entrance/screen view from the saved/reopened asset. The entrance view has a blue daylight sky and clearer context than the previous flat-gray-background renders. The high hero angle still sees the sky near the horizon and appears muted; a master-scene sky/lighting setup remains outside this asset task.
- Kept the R2 qualitative grass/asphalt materials and render-hidden/viewport-visible GIS diagnostic line.
- Left shell height, window placement, roof/penthouses, screen geometry, entrance geometry, and the explicitly unverified interior shells unchanged because the available images are not direction-registered elevations and no measured roof or as-built floor plan was found.

## Newly reviewed facade source

**Purdue University Residences — official McCutcheon exterior image**  
Page: https://www.housing.purdue.edu/visit/conferences/accommodations.html  
Direct image originally inspected: https://www.housing.purdue.edu/images/_hero/mccutcheon-exterior-640x360.jpg  
Provider: Purdue University Residences. Retrieved 2026-10-24. Image capture date, camera position/orientation, dimensions in the scene, and color calibration are not supplied. The 640×360 JPEG was viewed for this review and then removed from the project audit; its SHA-256 while inspected was `2EE562D3EA26CAFCBBDCC177161396FD96EF3011925DECEBB1322263B3CA11DF`.

The photo visibly supports qualitative features at the pictured entry: red brick, blue-gray glazing, a prominent perforated concrete-block screen, a low glazed entry, light-colored concrete/base, the wall name sign, and nearby lawn/planting. It also shows roof-level mechanical equipment behind the roof edge. The photo is oblique and partially screened by trees; it does not identify the building's cardinal facade, show the whole vertical extent, or provide measurements. It supports the modeled feature categories but cannot verify exact screen dimensions/location, all elevations, floor count, or roof/penthouse height.

**Purdue University Residences — McCutcheon residence hall page**  
https://www.housing.purdue.edu/my-housing/options/residence-halls/mccutcheon.html — retrieved 2026-10-24. This official page states the hall opened in 1963 and describes standard rooms, shared bathrooms, and common study/social spaces. Its standard room plan is explicitly approximate. It is not a measured exterior elevation or as-built interior plan.

**Purdue Archives photo finding aid MSP19**  
https://archives.lib.purdue.edu/fa/MSP19_News_Service.pdf — retrieved 2026-10-24. It lists historical proposed/construction/exterior photo holdings for McCutcheon (including 1961–1982 records), but those catalog entries are not digitized, direction-identified images and were not used to assign facade openings in R3.

## Height and footprint status

- The retained Purdue GIS FeatureServer snapshot is FID 57 (`MCUT`), source coordinates EPSG:4326 transformed using the project's approximate local tangent-plane method. The transformed GIS envelope still matches the saved base-plinth AABB to less than 0.0001 m at recorded precision. This is an envelope-coordinate check, not survey control or proof of every structural wall edge.
- The GIS snapshot's `num_levels_attribute: 10` is explicitly marked unverified in the source record. The official housing page does not provide story count or metric elevation. The new official photo crops the building and cannot establish total height. No shell or floor-height adjustment is justified.
- The modeled top is about 30.35 m in the existing asset. This remains unverified; do not treat the GIS level field, visual photo, or model render as a surveyed height.

## Interior status

The official housing page confirms shared bathrooms and common spaces, and gives approximate standard-room dimensions. It does not publish an as-built floor plan or locate rooms, stairs, elevators, or corridors within the towers. R3 therefore makes no interior geometry claims or changes. The existing tower/pavilion interior shells remain explicitly marked unverified; a whole-building interior/circulation grade should retain that limitation.

## Saved-file validation

`mccutcheon_r3_validation.json` records a Blender 5.2.3 reopen and render pass:

- `Asset_mccutcheon_hall` is present with one direct root and 235 objects including children; root origin and scale remain unchanged.
- Active standalone camera is `Cam_Hero_Perspective` at 30 mm. Scene world uses a procedural Hosek–Wilkie sky. Existing `Sun_Purdue_Daylight` energy/angle were not changed.
- The GIS diagnostic curve remains `hide_render=true`, `hide_viewport=false`, FID 57.
- R2 grass and asphalt materials reopen; all ten foliage-library image textures remain packed, with no unresolved unpacked dependencies.
- Saved-file renders: `mccutcheon_r3_hero.png` and `mccutcheon_r3_entrance.png`.

No independent R3 grade is claimed; request a fresh full-building review. No master placement check was performed in this pass.
