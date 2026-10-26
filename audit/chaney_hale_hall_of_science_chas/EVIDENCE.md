# Chaney-Hale Hall of Science (CHAS) evidence

## Assignment and stable asset

- Owner: Rossen (confirmed in the root pending-building table, retrieved 2026-10-26).
- Stable ID: `massing_chaney_hale_hall_of_science_chas_6bb9ef7`.
- Asset: `modular/buildings/massing_chaney_hale_hall_of_science_chas_6bb9ef7.blend`.
- Exported collection: `Asset_massing_chaney_hale_hall_of_science_chas_6bb9ef7`.
- Scene: `Building_massing_chaney_hale_hall_of_science_chas_6bb9ef7`.
- Coordinate mode: campus coordinates in the manifest's approximate local frame; identity transform. The massing asset is linked directly, with no `Placement_<id>` marker.

## Source evidence

The raw feature response for Purdue GIS FID 945 is saved in `sources/purdue_gis_fid945_live.json`; a compact feature copy is in `sources/purdue_gis_fid945_feature_only.json`. The live query returned a one-ring WGS84 polygon with CHAS name, code, address, owner and building number. After the documented project conversion, it spans approximately 74.62 m east-west and 58.90 m north-south, with area 2,219.65 m² in the local approximation. These are map-footprint measurements, not a structural-wall survey. The source date and positional accuracy are not published.

Purdue's 2020 opening article and official photo are saved as `sources/purdue_opening_article_2020.html` and `sources/purdue_chaney_hale_2020_exterior.jpg`. Purdue reports four stories and 111,000 gross square feet. The photograph shows red brick volumes, large glazed facades, pale horizontal bands, a darker ground floor, and a wide flat roof edge. The Purdue ECN rooftop webcam image (`sources/purdue_webcam_cam45_2020-09-22.jpg`) supplies a second photographic view of the curtainwall bays and brick end zones. The architect's Ennead project page (`sources/ennead_project_page.html`) independently describes transparent east and west facades and entrances serving campus traffic from multiple directions. FRP's project gallery image (`sources/frp_chaney_hale_view01.jpg`) confirms the linked wings, brick, glazing, horizontal bands, dark base, and wood-tone roof soffit.

All image comparisons are qualitative. No perspective-photo dimensions were measured. Full provider URLs, feature identifier, retrieval dates, CRS, method and uncertainty are in `evidence.json`.

## Geometry and uncertainty

The footprint ring was converted using X=(longitude+86.9137)×111412.84×cos(40.4274°), Y=(latitude−40.4274)×111040.0, matching the repository's local-frame approximation. The ground outline follows the GIS ring. The model uses a 16 m total height (four floors at about 4 m per floor) and 0.72 m roof overhang as estimates; Purdue's public GIS height fields are zero and there is no surveyed elevation source. Brick, glazed bays, pale belt courses, dark ground glazing, and the flat roof soffit follow photographs, while exact bay dimensions, entrance placement on every face, facade orientation at each wing, roof datum, interior, and hidden elevations remain unverified.

## Build and preview

Rebuild with Blender 4.5 from the repository root:

```powershell
blender -b --python modular/buildings/build_massing_chaney_hale_hall_of_science_chas_6bb9ef7.py
```

The script writes the stable asset and photo-based preview files. `preview.png` is an oblique model view; `topdown.png` supports visual comparison with the GIS outline. Reopen validation passed in Blender 4.5.15. The independent grade passed at 8.15/10; see `audit/chaney_hale_hall_of_science_chas_independent_grade/result.json` and `REPORT.md`.

## Fresh Blender reopen check

`reopen_validation.json` records a successful open of the saved asset in Blender 4.5.15. The expected scene, collection, and named CHAS mesh reopen as a one-object library; the evaluated mesh has 2,116 vertices and 517 polygons, no modifiers, no external image paths, and identity object transform. All 52 points in the official ground ring are present within 0.000011 m after Blender float conversion. Evaluated bounds include the estimated roof overhang and facade overlays: X −191.673..−115.633 m, Y 102.185..162.303 m, Z 0..16 m. `preview.png` shows the facade massing; `topdown.png` shows the GIS-derived roof outline. Independent grade passed at 8.15/10; criterion-level evidence is in `../chaney_hale_hall_of_science_chas_independent_grade/`.
