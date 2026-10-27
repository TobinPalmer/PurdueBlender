# Kappa Delta Rho (GIS FID 801)

## Model

Asset: `modular/buildings/massing_house_1089876362_14ecd2c.blend`  
Exact location verified from Purdue's 2007 campus report: **1134 Northwestern Avenue, West Lafayette**. This is the Kappa Delta Rho fraternity house, not the Kappa Delta sorority at 358 Northwestern.

The stable scene, collection, and house-object names were preserved. The placeholder shell was rebuilt against the full 20-vertex Purdue GIS footprint. Its vertical dimensions preserve the source massing's 7.5 m walls and 10.0 m roof peak. The roof has a long north-south ridge and dark roof tone guided by the 2023 Indiana orthophoto. The facade includes estimated brick coursing, sash windows, trim, entry surround, portico and dormers. The procedural materials are stored in the blend file and require no external texture paths.

## Evidence and limits

| Claim | Evidence | Confidence |
|---|---|---|
| Building identity and address | Purdue News Service names Kappa Delta Rho at 1134 Northwestern Avenue: <https://www.purdue.edu/uns/x/2007b/070817PendletonSuspend.html> | High |
| GIS parcel and footprint | Purdue BuildingShapesZip4 layer, FID 801; raw GeoJSON and layer metadata in `sources/` | High for footprint attribution; building-outline fit remains subject to screening uncertainty |
| General roof plan and dark roof tone | Indiana 2023 orthophoto in `sources/indiana_2023_orthophoto_2026.jpg` | Medium; aerial imagery supports plan/tone, not exact roof material |
| Historic district context | NPS Hills & Dales nomination photo index lists photo 37 as “Kappa Delta Rho Fraternity and markers,” facing southeast | High for the index caption; the index PDF did not provide an accessible facade photograph |
| Facade style, colors, window spacing, door/portico and dormers | No current direct facade image or measured elevation was located during this pass | Low; modeled conservatively as labeled estimates |
| Interior | No KDR floor plan or interior imagery was located; included only as a schematic circulation/common-room layout | Very low; not an as-built representation |

Do not use Kappa Delta Sorority imagery for this model: that separate Purdue building is at 358 Northwestern. Some elevations and the interior remain schematic pending direct imagery or plan evidence. The facade concept uses restrained, regular sash windows and brick/limestone-like materials as estimates, not verified facts.

## Saved previews

- Exterior: `previews/kappa_delta_rho_exterior.png`
- Interior diagram: `previews/kappa_delta_rho_schematic_interior.png` (schematic, not surveyed)

## Validation

`fresh_open_validate.py` opens the saved blend in a separate Blender process and checks the stable identity, footprint mesh, UV layer, material slots, detail and schematic interior content, and absence of preview rig objects or external texture dependencies. Its result and exact SHA are stored in `fresh_open_report.json`.

## Post-grade topology and preview remediation

The earlier exact-SHA review found 68 open boundary edges in the combined roof-detail mesh and requested a visible caveat on the interior diagram. The roof planes are now closed thin slabs, and the schematic floor is a shallow slab; `topology_report.json` records per-mesh results after a separate Blender reopen. The interior preview now carries a camera-facing “SCHEMATIC INTERIOR | NOT SURVEYED” annotation. This note is limited to the preview; no invented chapter signage or unverified label was added to the building asset. `build_report.json` documents the latest SHA and retained uncertainties. A direct, clearly identified KDR facade image remains unavailable; the NPS Photo 37 index is not treated as a photograph.
