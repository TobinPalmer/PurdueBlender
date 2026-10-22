# Purdue Bell Tower reconstruction evidence

Retrieved 2026-10-22. Asset: `../buildings/bell_tower.blend`; exported collection `Asset_bell_tower`; scene `Building_bell_tower`.

## Sources and authority

- Purdue University News, 2020-10-12: https://www.purdue.edu/newsroom/archive/releases/2020/Q4/university-to-mark-25th-birthday-of-purdue-bell-tower.html — published overall height 160 ft (48.768 m), red brick and limestone, Heavilon bells. Raw snapshot `purdue_2020_source.html`.
- Purdue News Service, 1995 dedication release: https://www.purdue.edu/uns/html3month/1990-95/9510.Zawisza.BellTower.html — four historic bells, memorial plaque and time capsule. Raw snapshot `purdue_1995_source.html`. Lists blueprints in the time capsule; it does not provide accessible construction drawings.
- Purdue Archives UA116: https://archives.lib.purdue.edu/repositories/2/resources/1456 — 1994–1995 collection, approximately160ft, four bells. Browser search readable; direct download blocked by access challenge. No bypass attempted.
- Purdue published campus GIS: https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0 — BELL / FID290; source snapshot in `../../audit/official_purdue_buildings_wgs84.json`, extracted campus-coordinate polygon in `official_BELL_reference.json`. Source CRS WGS84 EPSG4326; project uses documented approximate conversion X=(lon+86.9137)*111412.84*cos(40.4274°), Y=(lat−40.4274)*111040. Polygon is a map envelope, not certified structural survey; acquisition date and precision unspecified.
- Original photographer Tstuddud, 2006-08-20: https://commons.wikimedia.org/wiki/File:Purdue_BellTower_1.jpg — full tower exterior; public-domain photograph. Raw `reference_2006.jpg`; `photographer_commons_source.html` records provenance. Used for visible architecture only.
- Purdue University official homecoming photograph: https://www.purdue.edu/homecoming/downloads/MobileWallpapers-3.jpg ; linked from https://www.purdue.edu/homecoming/show-your-spirit.php . Raw `reference_official_full.jpg`. Decisively establishes continuous limestone arched base, projecting pier capitals, central raised brick strips and limestone cap blocks. These replace the inherited unsupported brick-pier interpretation. Photograph date unspecified.
- Wikimedia original photographer images: https://commons.wikimedia.org/wiki/File:Purdue_Bell_Tower_Purdue_University_2016_02.jpg (`reference_2016.jpg`); https://commons.wikimedia.org/wiki/File:Bell_tower_at_Purdue_University_on_a_fall_day.jpg (Shocksingularity,2025-09-18,CC0; `reference_2025.jpg`); https://commons.wikimedia.org/wiki/File:Purdue_BellTowerTimeCapsule.jpg (`reference_base.jpg`). Used for visible features and plaque form; no building dimensions inferred from image EXIF elevation. Wikipedia image index retained only as discovery provenance; factual claims derive from primary sources.
- Photographic reference compilation: https://dearchitectura0.wordpress.com/2025/05/05/the-purdue-bell-tower-a-monument-of-brick-limestone-and-legacy/ — close clock and belfry views; one image attributed there to Purdue University Marketing and Media / Smith Donovan. Raw page and images retained. Used only as visual reference; unsupported descriptive material claims not adopted. Clock photo shows black Roman markings on ivory dial, not gold bars.

## Measurements and limitations

Official envelope centroid: X−31.1215926334m, Y−12.9836274195m. Minimum rotated rectangle:5.487901×5.484725m; equivalent square modeled5.486313m. Local face rotation39.360982° east-CCW (129.360982° rectangle edge minus90°). Official polygon is slightly irregular, so centroid and equivalent square are a deliberate approximation, not exact surveyed wall registration.

Original asset155 objects; bounds36×36×50.6m including a large plaza. Original shaft6.2m square at(−31.2,−12.5), unrotated. Shaft center discrepancy0.490m against official polygon centroid; orientation differs39.36° modulo90°. Original shaft width about13%larger than official map envelope. Original top50.6m differs1.832m from published160ft. Original source backup `original.blend`, per-object original measurements `original_metrics.json`.

Reconstruction uses overall published48.768m, official mapped envelope and orientation; photographic proportions for subordinate elevations and features. No measured construction plan, current survey, ground elevation, detailed clock diameter, roof geometry or bell-size specifications found. Ground level0m is retained campus convention, not measured elevation. Architectural subdimensions are estimates. No hidden interior rooms, access ladder or mechanism is claimed accurate. Memorial plaque has representative perimeter markers and abbreviated identifying inscriptions; it is not a facsimile of the historical plaque or university seal.

Edits: reconstruct continuous open limestone arch base and shaft, central brick pilasters, limestone string courses/cornices, four limestone clock faces with Roman numerals/minute marks/hands, vents, open arched belfry, four profiled hollow bells with supports/clappers, pyramidal standing-seam roof and finial. Removed unsourced stone quoins and oversized36m plaza from this asset. Preview ground/camera/light are outside exported collection and do not link into master.

Accuracy categories: official identity supported; mapped horizontal center/orientation/envelope aligned within model representation; absolute geographic accuracy unverified; published overall height supported as approximate160ft; individual facade, arch, roof and bell dimensions estimated; vertical ground datum unverified; exact interior unverified. No100%claim.

## Implementation attempt log (five maximum, including preflight)

1. Initial reconstruction and image QA. Detected dial local-transform evaluation issue (stacked markings/hands) and reflected clock basis. No independent score.

2. Corrected dial transforms and basis. Save/reopen and identity-library-link tests passed. Four clocks,48Roman labels and four bells verified. No independent score.

3. Additional primary photo search found official complete base photograph. Corrected all base masonry to limestone, closed unintended upper corner gaps, replaced corner brick pilasters with central raised panels, and balanced shaft courses using photographic proportions. These subordinate dimensions remain estimated. Base closeup revealed an inherited global string-course slab blocking walk-through at1.1m. No independent score.

4. Removed the blocking1.1m slab; clear passage now extends to ground. Added representative plaque perimeter markers and abbreviated identifying inscriptions from primary photo and official1995release. Final independent review requested; attempt5 reserved for actionable review corrections.

Independent grading pending available concurrency slot. Maximum five implementation attempts total; stop at9/10 if evidence supports it. Do not inflate accuracy to reach threshold. Build logs1–4 preserve the actual sequence.
