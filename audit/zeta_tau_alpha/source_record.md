# Zeta Tau Alpha (Alpha Theta) — source and modeling record

## Candidate

- Stable building ID: `massing_zeta_tau_alpha_af8a443`.
- Candidate library: `modular/buildings/zeta_tau_alpha.blend`.
- Export collection: `Asset_massing_zeta_tau_alpha_af8a443`.
- Candidate review image: [candidate_front_review_r2.png](candidate_front_review_r2.png) (R2 frozen render; R1 render retained for comparison).
- Build script: [build_zeta_tau_alpha.py](build_zeta_tau_alpha.py).
- Current source snapshots: [Purdue GIS feature FID 773](gis_fid773_raw.json), [GIS layer metadata](gis_layer_metadata.json), and [official ZTA 2022 house photograph](official_2022_centennial_house_photo.jpg).

## Sources and provenance

1. **Purdue building footprint** — ArcGIS service `BuildingShapesZip4`, layer 0, feature/FID 773, `BLDG_ABBR=SOZTA`, `BUILDING_N=Zeta Tau Alpha`, `ADDRESS=118 Waldron St`. Retrieved 2026-10-26 from [feature JSON](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/773?f=pjson) and [layer metadata](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0?f=pjson). Layer metadata identifies WKID 102100/latest WKID 3857 (Web Mercator). The candidate outline uses the feature geometry `rings[0]` with 14 non-closing vertices. The CRS is verified by service metadata, not inferred.
2. **Purdue chapter identity and exterior** — Zeta Tau Alpha’s [Alpha Theta 101-year celebration article](https://zetataualpha.org/news/alpha-theta-celebrates-101-years-at-purdue), published 2022-09-24; the article says the chapter has called this house home since the 1950s. The page’s official [chapter-house group photograph](https://zetataualpha.org/uploads/card-images/AlphaThetaWeb2.jpg) shows the brick façade, white central portico with columns and triangular pediment, white window trim, dark roof, and raised `ZTA` pediment lettering. A local copy is retained in this audit folder.
3. **Street frontage and recent appearance** — Google Maps place record for [118 Waldron Street](https://www.google.com/maps/place/118+Waldron+St,+West+Lafayette,+IN+47906) resolves to the same Zeta Tau Alpha address and coordinate. Google Street View at the location displayed imagery dated April 2026; the viewed capture shows the brick residence, dark dormered roof, white entry columns, and mature street tree. The Street View capture URL is included in `build_report.json`.

## Footprint and coordinate method

- Source feature: Purdue ArcGIS `FID=773`, local source layer, `Shape__Length=169.8067` (service units) and `Shape__Area=1287.2773` (service-reported area field). The latter does not equal the area calculated from the Web Mercator ring after conversion; this discrepancy is not treated as dimensional evidence.
- Geometry transform: inverse spherical Web Mercator using `R=6378137 m` (`lon=x/R`, `lat=2 atan(exp(y/R))-pi/2`), then the repository campus approximation `X=(lon+86.9137)*111412.84*cos(radians(40.4274))`, `Y=(lat-40.4274)*111040.0`.
- Local placement origin: polygon centroid **(-320.51444 m, -187.07450 m)** in the project campus frame. Candidate geometry is centered at local (0,0); the master placement marker should use this origin when the coordinator registers the detailed asset.
- Transformed plan ring: 14 non-closing points; calculated local planar area **744.7062 m²**; local bounds are about **28.03 m east-west × 36.71 m north-south**. This is a converted map-outline measurement, not surveyed wall faces.
- The shared source/master audit recorded this feature as a near-match to the existing massing (reported residuals near 1 m, IoU about 0.92); that establishes likely identity but does not validate the upper walls or roof.

## Modeling choices and limits

- The continuous exterior shell follows the transformed GIS ring. Façade bay spacing, floor bands, window proportions, white classical portico, pediment sign, slate roof and dormers are interpreted from the official chapter-house photo and 2026 street imagery. In R2 the raised `ZTA` lettering and plaque are positioned on the outward-facing (+Y) pediment plane, and text orientation is set to read from the front review view.
- The GIS `Extrution` attribute is 12 m and the service `NUM_LEVELS`/`CountOfFLO` fields are both 1. Those attributes do not establish actual roof height or story count. The R2 model's complete asset bounding-box maximum is **11.91 m** (measured from this model); this is treated as an estimate of the building peak, not as a surveyed elevation. The prior 12.5 m estimate was unsupported and has been removed.
- Three interior floor plates and residence/common-room furniture are explicitly schematic. No measured floor plan or chapter-house construction drawing was available in the sources reviewed.
- Windows are layered façade assemblies over the shell; they are not cut-through openings. The current interior is therefore intended for schematic/cutaway review and is not visible through the façade at normal viewing angles.
- Landscaping is restrained and illustrative. Individual trees, shrubs and site furniture have not been verified against a dated survey.

## Review status

R2 passed independent grading at 8.2/10 and is integrated in the campus master through the stable-ID placement marker. The marker uses the GIS-derived campus origin documented above, with identity rotation and unit scale. The building is in the finished list; its GIS roof/wall interpretation, height, and schematic interior limitations remain documented below.

## R2 revision

- Raised the chapter letters and stone plaque onto the exterior face of the portico pediment, with a front-facing orientation. See `candidate_front_review_r2.png` and `build_report_r2.json`.
- Reconciled height wording to the candidate's measured 11.91 m maximum Z and retained estimate status because no elevation survey was found.
- Kept the GIS footprint/origin, exterior interpretation, packed materials, and expressly schematic interior unchanged.
- R2 fresh Blender reopen and independent grade pass at SHA `1e9b54a032ac508e3e473e1757b6edce6ee8724b581c884d54e984572ed8a7af`; see [`independent_grade_r2.md`](independent_grade_r2.md) and [`master_sync_r29.json`](../master_sync_r29.json). The saved master places the local-coordinate candidate at the documented source-derived origin using `Placement_massing_zeta_tau_alpha_af8a443`.
