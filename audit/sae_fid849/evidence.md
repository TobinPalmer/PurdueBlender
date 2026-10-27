# Sigma Alpha Epsilon (Purdue FID 849) — evidence and reconciliation

Retrieved 2026-10-26. Proposed stable ID: `massing_sigma_alpha_epsilon_fid849`; asset: `modular/buildings/massing_sigma_alpha_epsilon_fid849.blend`; exported collection: `Asset_massing_sigma_alpha_epsilon_fid849`.

## Identity and footprint reconciliation

The assignment table names Sigma Alpha Epsilon, FID 849, but has no existing asset crosswalk. The Purdue GIS feature itself identifies `BUILDING_N=Sigma Alpha Epsilon`, `BLDG_ABBR=SOSAE`, `OWNER=GREEK`, `ADDRESS=406 N Littleton St`, and GlobalID `{17BDAFEA-EFDB-49E9-972D-9369A3ADC90E}`. The chapter website retrieved on this date identifies its house as 406 Littleton St. Tippecanoe County's parcel layer independently identifies parcel `79-07-20-107-017.000-026` at 406 LITTLETON ST. The county parcel is a site/ownership envelope, not a building polygon.

The 16-vertex Purdue FID 849 outline was overlaid with Esri World Imagery and the county parcel boundary. The FID outline falls on the visible house roof within that parcel. This orthophoto check resolves the missing crosswalk sufficiently for a new massing asset; no claim is made that a legacy detailed building asset has been found. The saved overlay is `fid849_orthophoto_parcel_overlay.png`; raw imagery tiles and the tile manifest are in `sources/world_imagery_tiles/`.

The Nominatim address result is at 40.4279403, -86.9030086, roughly 70–80 m west of the FID polygon center and outside the parcel footprint. It was excluded from placement and treated as an address/geocoder mismatch. The chapter site's written address and GIS/parcel labels, plus visual roof alignment, were preferred.

## Plan geometry and campus coordinates

Purdue FID 849 raw feature is WGS 84 / EPSG:4326. The project local approximate geographic conversion was applied exactly: `X=(longitude+86.9137)*111412.84*cos(radians(40.4274))`; `Y=(latitude-40.4274)*111040`; Z is modeled above grade. This is a local approximation, not a surveyed projected CRS. The transformed GIS ring is valid, area 683.166 m², perimeter 152.256 m, bounds X 984.009–1016.364 m and Y 49.240–99.252 m. County parcel geometry was returned as GeoJSON/EPSG:4326 and transformed with the same approximation for the overlay; it contains the entire FID polygon (100% intersection). The GIS source's Shape__Area 1180.941 and Shape__Length 200.265 are retained as raw service attributes; their units/semantics are not assumed to equal the local-meter calculations.

The modeled asset preserves the FID roof/plan outline and campus coordinates. Its measured geometry bounds, including a small entry projection, are X 983.809–1016.562 m, Y 49.038–99.454 m, Z 0–11.95 m. The underlying roof outline dimensions are approximately 32.354 × 50.013 m. Orthophoto tile capture date is not published in the tile response; imagery is supporting visual reconciliation, not a dated survey.

## Facade and roof evidence

The architect Kevin Murphy Sullivan's project page identifies Sigma Alpha Epsilon renovations and an addition in West Lafayette and describes an entry vestibule, president's wing, second-floor addition above the dining room, kitchen/dining work. Its three supplied images are architectural renderings, not construction documents or as-built photographs. They support the broad composition used here: brick lower facade, pale upper wall surfaces, central gabled entry/arched surround, repeated window rhythm, and low pitched roof forms. They do not establish exact built colors, window counts, heights, or final post-renovation dimensions.

The SAE Purdue Spring 2018 newsletter documents the multi-phase house renovation and a dedication weekend Oct. 19–21, 2018. The Spring 2025 newsletter describes a front porch, a roughly 105-year-old house, and a south wing added decades earlier. This is contextual evidence only; it does not provide measured elevations. Purdue GIS properties report `NUM_LEVELS=1` and `Extrution=12`, while the architect's design renderings show a composition with multiple visible facade bands and describe a second-floor addition. To avoid silently treating those as equivalent, the model uses three visible facade strata as a rendering-derived estimate; vertical dimensions and roof silhouette remain schematic/estimated, not verified as-built facts.

## Reopen validation

Saved asset was freshly opened in Blender 5.2.0 LTS and inspected. `fresh_open_inspection.json` records PASS: expected scene and collection; 520 mesh objects; 4,586 vertices; 3,310 polygons; zero modifiers, external image dependencies, linked libraries, or material-less collection objects. The candidate asset SHA-256 at freeze is `9756B5AE39B3070918DEBBE6E3F0A07913F79E1EAB04B956BA4F1D0AAEBDD20D`. It is a simple massing library and should be linked directly at campus coordinates. No placement marker or master file has been edited.

## Source register

See `source_record.json` for provider, URLs, raw-snapshot paths, source dates, retrieval date, CRS/method and uncertainties. All raw snapshots are preserved under `sources/`; Esri tile timestamps are unavailable. The model and evidence retain the identity reconciliation and the uncertainty around as-built elevations explicitly.
