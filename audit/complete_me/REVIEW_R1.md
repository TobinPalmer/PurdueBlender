# Mechanical Engineering — R1 Evidence and Build Review

**Updated:** 2026-10-24  
**Asset:** `modular/buildings/mechanical_engineering.blend`  
**Export collection:** `Asset_mechanical_engineering`  
**Baseline independent grade:** 4.5/10 (`reviewer.md`)  
**Scope:** Dedicated Mechanical Engineering asset and `audit/complete_me/` only. The master, manifest, shared indexes, and other buildings were not edited.

## R1 improvements

The prior review found a blank solid facade, no useful entrance model, weak visual texture, and an unfinished interior. R1 addresses the highest-confidence exterior gaps using current Purdue facade photography and the documented entrance direction:

- Cut 208 window openings through the main FID 857 masonry shell across its long plan edges. Added inset dark blue-gray glazing, dark frames/mullions, pale sills and lintels, and thin story bands. The repeated window rhythm and four visible above-grade window rows are visual approximations from photographs and floor levels, not a measured elevation schedule.
- Added a limestone arched entrance surround and glazed double doors with lettering. The front was selected from the long GIS perimeter edge whose outward normal faces the Engineering Fountain, consistent with Purdue's stated Gatewood entrance direction. The portal's exact along-wall position is estimated at the edge midpoint because the photo is not georeferenced.
- Replaced the weak shell shader with a warm red-brown, meter-scaled procedural running-bond brick and subtle mortar relief. Color is qualitative, not calibrated. No external texture images were added.
- Added a clear-day world and saved standalone hero/entrance cameras. These are settings in the building asset scene; no master lighting was changed.

The work is visualized in [the R1 hero render](mechanical_engineering_r1_hero.png) and [the R1 entrance render](mechanical_engineering_r1_entrance.png). The build is reproducible through `build_mechanical_engineering_r1.py`; the read-only saved-file check is `validate_mechanical_engineering_r1.py`.

## Evidence used

1. **Purdue ME renovation notice.** Purdue states the new main entrance is through the Gatewood Wing and faces the Engineering Fountain. This supports the direction of the entrance, not exact wall coordinates or dimensions. [Purdue ME renovation notice](https://engineering.purdue.edu/ME/News/2023/me-building-renovation-brings-changes)
2. **Purdue 2025 exterior and history photography.** The official 2025 article says the historic exterior was kept while the interior was modernized. Its exterior photo qualitatively shows brick, dark multi-level window openings, pale stone entry surround, name lettering, and planting. The image has no supplied capture date, scale, or viewpoint registration. [Purdue ME history article](https://engineering.purdue.edu/ME/News/2025/purdues-mechanical-engineering-building-represents-more-than-a-century-of-history)
3. **2024 exterior photograph.** The Wikimedia Commons photo page records a June 20, 2024 capture and EXIF time. It provides a clear view of tall windows, a pale arched entry, brickwork, sills, and horizontal stone bands. It has no GPS/camera direction or metric scale and is under CC BY-SA 4.0; the image was only inspected temporarily and is not embedded in the model. [Wikimedia Commons photo record](https://commons.wikimedia.org/wiki/File:Purdue_Mechanical_Engineering_Building.jpg)
4. **Purdue Engineering Emergency Plan.** The current Purdue page describes the five-phase complex, floor-level discontinuities, and a photograph looking east from the Gatewood entrance toward the main ME building. It does not publish a measured elevation. Its east-wing construction dates differ from the 2015 planning study, so the year discrepancy remains open. [Purdue ME emergency plan](https://www.purdue.edu/operations/emergency-preparedness/me/)
5. **Purdue 2015 ME–RAIL–HAMP planning study.** The archived local PDF includes existing basement through fourth-floor plans on pages 40–46 and explicitly excludes Gatewood from its study scope. It establishes the older building's complex floor layout but is not used as a current as-built plan or a measured facade/height source. [Original study PDF](https://engineering.purdue.edu/~frosch/Renderings/Masterplans/ME-RAIL-HAMP%20Study.pdf)
6. **Purdue campus GIS.** FID 857 in the retained source snapshot supports the horizontal footprint envelope. R1 boolean openings leave the shell's local XY AABB at the GIS envelope to recorded precision. This is an approximate project transform and envelope check, not survey control or a wall-by-wall validation. [Purdue BuildingShapes FeatureServer](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0)
7. **Purdue phase aerial illustration.** A Purdue renovation illustration labels five phases (1929, 1932, 1942, 1948, 2012) and shows both tiled roof sections and flat roof areas with rooftop equipment. It is oblique, uncalibrated, and not tied to the GIS coordinate frame. R1 deliberately leaves the existing roof plane unchanged. [Purdue ME renovation page](https://engineering.purdue.edu/ME/Giving/Renovation)

Full provider, URL, feature/date/CRS, method, and uncertainty records are in `mechanical_engineering_r1_evidence.json`. The cached GIS source is `audit/official_building_references.json`.

## Validation

Blender 5.2.3 reopened the saved source after the build. The exported collection is present with 58 direct objects, and the root remains at identity transform. The main shell's local XY bounds match the FID 857 envelope with zero delta at recorded precision. The boolean operation is applied, no temporary cutters remain, both preview renders exist, and no unpacked image dependencies are present. Validation result: `mechanical_engineering_r1_validation.json` (**passed**).

R1 preserved the source asset's 18.5 m modeled top, estimated slabs/partitions, FID 108 shell, and placement origin `[66.30000114440918, 86.5]`. No master placement check was performed in this asset-only pass.

## Remaining gaps and requested grading

- No source in the reviewed package provides measured wing heights, roof elevations, exact window/door schedules, or reliable roof geometry. The source imagery depicts varied pitched and flat roofs, but it is not georeferenced well enough to place those sections accurately.
- The entrance face is selected from the fountain direction and GIS, but its exact along-wall location is still an estimate.
- Repeated windows are evidence-informed, not independently verified for count and location on every wing. An independent reviewer should compare them directly to the images and mark uncertain facades accordingly.
- The current shell still combines multiple historical wings at one modeled height. Interior floors and partitions remain schematic; the plans are old and do not document Gatewood's current as-built rooms or finishes.
- FID 108's relation to the full FID 857 footprint requires separate review.

**No R1 grade is claimed.** Request an independent score against the project’s five criteria using the asset, evidence JSON, validation result, and both renders. Do not describe the building as complete until a fresh grade is recorded.
