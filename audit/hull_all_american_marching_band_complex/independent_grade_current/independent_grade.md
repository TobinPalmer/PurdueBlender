# Independent grade: Hull All-American Marching Band Complex

**Score: 8.4/10 — PASS**  
**Candidate SHA-256:** `4d525feb45716cab403a20181bb9486b8973e34212b548efb5e7c4bd5d7f8c08` (matches the submitted candidate hash).  
**Reviewed asset:** `modular/buildings/massing_hull_all_american_marching_band_complex_665bcb7.blend`

I opened the saved candidate in a separate Blender 5.2.3 background process and inspected the saved scene, collection, world-space geometry, material assignments, and external image references. I compared the saved slab outline to the raw Purdue GIS FID 431 polygon, transformed using the documented campus coordinate approximation. I also inspected the exterior render, interior cutaway, aerial overlay, source snapshots, evidence record, and fresh-open validation.

| Criterion | Score | Assessment |
| --- | ---: | --- |
| Identity and source-backed footprint | 1.9/2 | Purdue GIS FID 431 is labeled HULL; official band schedules identify the Hull complex/garage and distinguish it from the field. The model slab matches the GIS ring at IoU 0.999997 and Hausdorff 0.000040 m. The exact polygon-to-named-subcomponent link is not shown in an as-built plan. |
| Position, orientation, and scale | 2.0/2 | Model stays in the documented campus XY frame with zero instance offset; slab plan matches the GIS source. Fresh-open bounds are about 14.20 x 21.59 m. |
| Height, floors, and roof | 1.2/2 | Aerial and distant April 2026 Street View support a low single-story building with a flat/low-slope pale roof. The 5.36 m top and roof build-up are estimates; no elevation, height measurement, or floor plan is available. |
| Facade, entrances, and distinctive features | 1.3/2 | Repeated service bays and a high window band follow the visible Street View rhythm; the cutaway includes storage, open handling/practice, changing, and restroom elements consistent with documented uses. Exact bay count, facade materials, room placement, and fixtures are schematic or unverified. |
| Modular export, portability, and evidence | 2.0/2 | Expected scene and collection reopen successfully; 404 collection objects, 403 meshes, zero materialless meshes, zero unpacked external images, and all objects remain in the designated asset collection. The building-specific builder, provenance, validation, and preview evidence are present. |

## Findings

- The revised asset is a strong GIS-faithful plan and a plausible low service/garage massing for the Hull band facility.
- Height, exact facade construction, service-door count, and interior layout remain estimates due to the lack of close-range imagery or as-built plans.
- Coordinator follow-up is required before declaring full master integration: `modular/manifest.json` still stores the pre-rebuild 7.6 m bounds and `accuracy_status: unverified`; update the shared manifest and rerun whole-master checks after integrating the new 5.36 m asset.

## Evidence reviewed

- `audit/hull_all_american_marching_band_complex/evidence.json`
- `audit/hull_all_american_marching_band_complex/fresh_open_validation.json`
- `audit/hull_all_american_marching_band_complex/sources/purdue_gis_fid431.json`
- `audit/hull_all_american_marching_band_complex/sources/esri_world_imagery_fid431_z20_mosaic.jpg`
- `audit/hull_all_american_marching_band_complex/sources/google_streetview_apr2026.json`
- `audit/hull_all_american_marching_band_complex/gis_footprint_overlay.jpg`
- `audit/hull_all_american_marching_band_complex/exterior_preview.png`
- `audit/hull_all_american_marching_band_complex/interior_cutaway_preview.png`
- Independent fresh-open inspection: `audit/hull_all_american_marching_band_complex/independent_grade_current/blender_probe.json`

Purdue's 2024 Alumni Band schedule directly references check-in at the Hull “All-American” Marching Band Complex garage: https://www.purdue.edu/bands/wp-content/uploads/2024/09/Alumni-Band-2024-Schedule.pdf
