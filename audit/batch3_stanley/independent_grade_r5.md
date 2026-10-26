# Independent grade — Stanley Coulter Hall R5

**Result: 7.8/10 — below the 8.0/10 pass threshold.**  
**Asset SHA-256:** `d453ca6e1dacfaa3c6c23791396260e9101a5683ddab22d5cd81aaebbcd67c2c`  
**Independent fresh reopen:** Blender 5.2.3; 773 objects/763 meshes in the exported collection, identity root, zero materialless meshes, zero invalid material slots, and zero missing external images. The R5 asset hash matches `reopen_verification_r5.json`.

R5 addresses several high-impact R4 findings: it removes the unsupported oversized portico, varies the east window widths, gives the low hip roof a warmer surface, changes the bright entry fixtures, labels the interior diagram as unverified, and archives the 47 high roof options outside the exported collection. The foundation outline remains an exceptionally close match to Purdue GIS feature 56. The changes improve the asset, but the current reference still shows visible entrance, facade rhythm, and upper-glazing differences. The current roof silhouette/height and room layout remain unverified, and the master placement marker has not been checked. Those gaps keep this below the requested pass threshold.

## Scorecard

| Criterion | Score | Findings |
|---|---:|---|
| Identity and full GIS footprint | 1.9/2.0 | The 12-point foundation ring agrees with the official Purdue campus-map polygon: IoU 0.999999899, symmetric difference 0.000286 m², and Hausdorff distance 0.0000045 m. This is an approximate local-meter comparison and validates the foundation outline only. |
| Placement, orientation, and scale | 1.6/2.0 | The standalone library reopens with the expected collection and identity local root. Its report preserves the existing manifest origin. The master `Placement_stanley_coulter_hall` marker and assembled neighborhood were not reopened in this review. |
| Floors, height, and roof form | 1.35/2.0 | The 3-story mass and low hipped roof are plausible, and the procedural roof tone is improved. The broad roof surface still reads nearly blank. No current measured roof profile or height is available. The active all-geometry top is 15.87 m, while render-visible top is 15.7828 m; neither is a surveyed height. |
| Facade, entrance, and materials | 1.45/2.0 | R5 improves the entrance proportions and window-width hierarchy. The current Purdue photo still shows a deeper stone-framed entrance with a legible inner arch/transom, paired supports, broad stairs and railings. The model reads as a shallow blocky canopy, with two conspicuous square wall fixtures. The east facade remains more regular than the photographed window groupings and upper glazed band. Procedural materials are complete, but lack photo-scale surface detail. |
| Interior, saved asset, evidence, and portability | 1.5/2.0 | Fresh reopen verifies the exact saved asset. The 52 unsupported options are preserved in a hidden sibling archive, and the active collection has complete material assignments. The interior is an explicitly labeled furniture/use schematic, not a readable connected circulation/core or room-partition model. Evidence clearly separates verified outline from estimated roof/facade/interior. |
| **Total** | **7.8/10** | **Does not meet the 8.0/10 pass threshold.** |

## Corrections for the next review

1. Have the coordinator verify the master placement marker and neighborhood alignment before integration.
2. Deepen and refine the entrance to match the current Purdue photo: show the recessed doors, inner arched soffit/transom, paired supports, stairs, and rails distinctly. Slim the heavy cap and remove or reshape the two unsupported square fixtures.
3. Adjust the facade rhythm toward the observed grouped openings and stronger continuous upper glazing band without changing the verified foundation ring.
4. Add restrained readable roof-surface/eave detail while leaving current roof construction and height labeled as unverified. Do not restore unsupported dormers, HVAC, or high roof options.
5. If the interior diagram is meant to evidence an interior model, add a schematic connected corridor/core, readable partitions and floor relationship; retain the explicit uncertainty notice.

## Evidence and limits

- The current Purdue CLA exterior image was inspected from `source_cla_stanley_coulter.jpg`. It supports the entrance and facade composition but has no exposed capture date and covers only part of the facade. [Purdue CLA image](https://www.cla.purdue.edu/academic/english/images/stanleycoulterhall.jpg)
- Historic image PPBUC01117 supports low hipped-roof context only; it is undated and does not prove the current roof. [Purdue Archives record](https://earchives.lib.purdue.edu/digital/collection/pbuildings/id/1310/)
- The GIS outline is Purdue ArcGIS FID 56, snapshot dated 2026-10-22; it is a campus-map polygon and not a certified survey. The metric comparison is in `full_polygon_comparison_r3.json`.
- `SC_hero_r5.png`, `SC_entry_r5.png`, `SC_interior_schematic_r5.png`, and `SC_footprint_overlay_r3.png` were inspected. The overlay is useful for plan outline only; it does not validate roof, facade, or height.
- The master blend and campus marker are outside this standalone asset review and need a separate coordinator check.
