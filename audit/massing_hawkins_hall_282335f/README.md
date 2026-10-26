# Hawkins Hall model evidence

Asset: `modular/buildings/massing_hawkins_hall_282335f.blend`  
Stable collection: `Asset_massing_hawkins_hall_282335f`  
Scene: `Building_massing_hawkins_hall_282335f`

## Geometry and sources

- **Footprint and campus position:** Purdue BuildingShapes FeatureServer, layer 0, FID 83 (`HAWK`, George A. Hawkins Hall), queried 2026-10-26. Service layer metadata reports WGS84 (EPSG:4326). The raw feature is retained in `sources/purdue_building_shapes_fid83_full_2026-10-26.json`; the relevant selected fields and ring are also in `sources/purdue_building_shapes_fid83_2026-10-26.json`. The polygon ring was converted to campus meters using the approximation in `modular/AGENTS.md`: X=(longitude+86.9137)*111412.84*cos(40.4274°), Y=(latitude-40.4274)*111040. This is a local approximation, not a surveyed CRS. Near-duplicate drafting vertices within 0.025 m were removed; 65 footprint vertices remain. The original ring orientation and campus placement are retained.
- **Wing heights and circulation:** Purdue Operations & Maintenance Emergency Preparedness, [Hawkins Hall Building Emergency Plan](https://www.purdue.edu/operations/emergency-preparedness/hawk/), revision displayed 2026-03-26. It describes a 13-floor east wing, 10-floor west wing and a connecting central area, plus exits from the central/east/west areas. A local HTML snapshot is retained in `sources/purdue_oep_hawkins_emergency_plan_2026-10-26.html`.
- **Residential use:** Purdue University Residences, [Hawkins Hall](https://housing.purdue.edu/my-housing/options/residence-halls/hawkins.html), retrieved 2026-10-26; local snapshot retained. It identifies Hawkins as a 13-floor co-ed residence hall.
- **Facade character:** Purdue University Residences, [Accommodations](https://housing.purdue.edu/visit/conferences/accommodations.html), retrieved 2026-10-26; local page and its Hawkins exterior photo are retained under `sources/`. The photo supports red/orange brick, regular windows, pale trim and a flat roof. It is a visual reference, not a dimensioned elevation.
- **GIS height:** the official feature snapshot reports `Extrution=140` (interpreted by the source/model workflow as feet, or 42.672 m). The GIS floor attributes also report 15 levels and a roof value that do not align cleanly with the OEP's 13-floor east / 10-floor west description. The 140-ft field is modeled as the nominal top of the taller wing; its units/meaning and date are not independently confirmed in the layer metadata.
- **Aerial context:** Indiana current imagery is saved as `sources/indiana_current_aerial_hawkins.jpg`. The imagery service does not expose an acquisition date in the saved response. `site_alignment_overlay.png` and `site_alignment_crop.png` compare the converted GIS footprint (red) with the previous asset outline (cyan); comparison is sensitive to the local geographic approximation and aerial georeferencing.

## Model decisions and checks

The model uses the complete GIS outline for the lower 10-floor volume and an approximate traced portion of the east wing for the upper three floors. It adds repeated window frames/glazing, brick courses, pale trim and a simple flat roof based on the official photo. A small central glazed entry is inferred; its exact door location is not verified. These facade elements are illustrative and do not claim plan-level accuracy.

The nominal GIS extrusion height is 42.672 m. The 10-floor shared/west volume is estimated at 32.8246 m by dividing 42.672 m evenly across the east wing's 13 floors and applying 10 floors; this assumes uniform floor-to-floor heights. The independent asset reopen validation measures the finished collection bounds at X 150.4306–201.0531 m, Y -557.2613–-461.2058 m, Z 0–42.7370 m. The 42.7370 m maximum includes a 0.065 m top facade course above the nominal 42.672 m structural extrusion. The evaluated bounds are about 50.6226 x 96.0555 x 42.7370 m.

The asset was saved and reopened in Blender 4.5.15. Validation confirms the expected scene and collection, seven mesh objects, stable campus-coordinate placement, and four project-relative brick texture images whose paths resolve in this repository. Results are recorded in `final_validation.json`; the saved hero render is `preview_exterior.png`. The earlier asset render is retained as `preview_before.png`.

## Remaining uncertainty

The public evidence found no dimensioned Hawkins floor plans or elevations. The GIS polygon and official emergency plan substantiate identity, footprint, wing count relationship, and general split massing, but they do not resolve exact upper-wing boundary, facade bay spacing, floor-to-floor heights, roof construction, or door locations. The GIS's `15` level count conflicts with the current official emergency plan's 13/10 wing counts; this conflict is preserved rather than silently treated as resolved. Sources are operational/current web pages and a GIS snapshot retrieved 2026-10-26, not as-built construction documents.
