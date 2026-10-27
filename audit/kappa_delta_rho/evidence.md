# Kappa Delta Rho (GIS FID 801)

## Model

Asset: `modular/buildings/massing_house_1089876362_14ecd2c.blend`  
Exact location verified from Purdue's 2007 campus report: **1134 Northwestern Avenue, West Lafayette**. This is the Kappa Delta Rho fraternity house, not the Kappa Delta sorority at 358 Northwestern.

The stable scene, collection, and house-object names were preserved. The placeholder shell follows the full 20-vertex Purdue GIS footprint. The 7.5 m wall and 11.4 m roof-peak heights are estimates, not surveyed measurements. The 2023 Indiana orthophoto informs the roof plan and dark tone. NPS Photo 37 is direct facade evidence: it shows pale wall fields with dark Tudor half-timber framing on the upper facade and gable, a steep roof with three dormers, a chimney, and an entrance near the right end of the long elevation. The image is monochrome, so modeled color and exact wall/roof materials remain estimates. Procedural materials are embedded in the blend file and use no external image paths.

## Evidence and limits

| Claim | Evidence | Confidence |
|---|---|---|
| Building identity and address | Purdue News Service names Kappa Delta Rho at 1134 Northwestern Avenue: <https://www.purdue.edu/uns/x/2007b/070817PendletonSuspend.html> | High |
| GIS parcel and footprint | Purdue BuildingShapesZip4 layer, FID 801; raw GeoJSON and layer metadata in `sources/` | High for footprint attribution; building-outline fit remains subject to screening uncertainty |
| General roof plan and dark roof tone | Indiana 2023 orthophoto in `sources/indiana_2023_orthophoto_2026.jpg` | Medium; aerial imagery supports plan/tone, not exact roof material |
| Visible facade form and Tudor framing | NPS Hills & Dales nomination supporting PDF, asset `d392afd2-253a-41d8-a3f6-d8faaf7d0c14`, image page 71 and caption page 72; caption identifies Kappa Delta Rho, Northwestern Ave, N, photo facing southeast, Jane Evans, June 2001. Local source scan and page renders are in `sources/`. | High for the features visible in this view; hidden elevations and exact dimensions remain unknown |
| Entry placement, three dormers, chimney, steep roof, broad window groupings | Same identified NPS Photo 37 | Medium to high for visible count/placement and silhouette; exact joinery and roof material are not resolved |
| Wall/roof color, finish, exact window sash divisions and non-visible elevations | Photo 37 is monochrome and shows one oblique elevation; orthophoto supports only roof plan/tone | Low; explicitly estimated |
| Interior | No KDR floor plan or interior imagery was located; included only as a schematic circulation/common-room layout | Very low; not an as-built representation |

Do not use Kappa Delta Sorority imagery for this model: that separate Purdue building is at 358 Northwestern. Some elevations and the interior remain schematic pending direct imagery or plan evidence. The facade concept uses restrained, regular sash windows and brick/limestone-like materials as estimates, not verified facts.

## Saved previews

- Exterior: `previews/kappa_delta_rho_exterior.png`
- Interior diagram: `previews/kappa_delta_rho_schematic_interior.png` (schematic, not surveyed)

## Validation

`fresh_open_validate.py` opens the saved blend in a separate Blender process and checks the stable identity, footprint mesh, UV layer, material slots, detail and schematic interior content, and absence of preview rig objects or external texture dependencies. Its result and exact SHA are stored in `fresh_open_report.json`.

## Post-grade topology and preview remediation

The earlier exact-SHA review found 68 open boundary edges in the combined roof-detail mesh and requested a visible caveat on the interior diagram. The roof planes are now closed thin slabs, and the schematic floor is a shallow slab; `topology_report.json` records per-mesh results after a separate Blender reopen. The interior preview carries a camera-facing “SCHEMATIC INTERIOR | NOT SURVEYED” annotation. This note is limited to the preview; no chapter signage or unverified label was added to the building asset. `build_report.json` documents the exact asset SHA and retained uncertainties. Photo 37 is the identified facade evidence; it does not establish colors, measured heights, hidden sides, or the interior plan.

## Photo 37 evidence-led refinement (2026-10-26)

The supported PDF scan is preserved at `sources/nps_national_register_attachments_7.3mb.pdf`; its repaired, readable copy is `sources/nps_national_register_attachments_repaired.pdf`. Photo 37 is PDF page 71 (1-based), caption page 72. The caption names “Kappa Delta Rho, Northwestern Ave, N,” says the view faces southeast, credits Jane Evans, and gives June 2001. The caption date is recorded as stated; the exact exposure date has not been independently confirmed. A rendered image and caption are preserved as `sources/nps_photo37-071.png` and `sources/nps_photo37-072.png`.

Refinement follows only visible evidence: pale wall infill, dark half-timbering across the upper visible facade and gable, three dormers on the visible roof slope, a chimney, steep roof silhouette, and the entrance near the right end of the long facade. A simple gabled roof closure and facade details on concealed sides are provisional. The model does not claim measured height, exact color/material, a surveyed window schedule, or a known interior plan.
