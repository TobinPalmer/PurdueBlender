# Independent grade — Kappa Delta Rho (Purdue)

**Exact asset reviewed:** `modular/buildings/massing_house_1089876362_14ecd2c.blend`  
**SHA-256:** `865dcc2717698a66de76aa7592b2741b444074866337576aa974feb8e6571f3f`  
**Fresh-open environment:** Blender 5.2.3 LTS, separate background process  
**Grade:** **7.7 / 10**

## Rubric and result

| Category | Points | Evidence and rationale |
|---|---:|---|
| Correct building identity and source use | 1.5 / 1.5 | The linked Purdue GIS record is FID 801, “Kappa Delta Rho,” at 1134 Northwestern Avenue. The model scope and notes do not confuse it with Kappa Delta Sorority at 358 Northwestern. Purdue's public notice independently identifies KDR at 1134 Northwestern ([Purdue](https://www.purdue.edu/uns/x/2007b/070817PendletonSuspend.html)). |
| Footprint, placement, and orientation | 2.0 / 2.0 | After a clean Blender open, all 20 lower wall vertices match the 20-vertex FID 801 ring within 0.000057 m maximum XY error (0.000032 m RMS) under the documented campus-local projection. Bounds also agree. This is strong GIS placement and plan evidence. See `fresh_open_probe.json`. |
| Building and roof massing | 1.2 / 1.5 | The orthophoto supports a dark roof and long ridge, and the rendered roof arrangement is broadly compatible. The 7.5 m wall height and 10 m ridge are estimates rather than measured elevations; the GIS record's one-level field does not resolve the vertical form. Dormer profile/count remain only partly verifiable from overhead imagery. |
| Facade and architectural fidelity | 0.8 / 2.0 | The brick facade, regular sash windows, portico, trim, shutters, and dormers make a coherent Greek-house model, and the NPS nomination characterizes the district's early Northwestern Avenue houses broadly as Period Revival. However, the NPS Photo 37 reference is an index entry, not a facade photograph. Searches did not locate a usable, clearly identified current KDR facade image. Most facade details therefore remain plausible estimates without building-specific visual verification. Do not use imagery of Kappa Delta Sorority or other KDR chapters as a substitute. |
| Geometry, materials, and portability | 1.3 / 1.5 | Stable asset and object names, metric UVs, coherent procedural brick/slate/trim materials, and no unpacked external image dependencies make the asset portable. The primary wall mesh is manifold. The combined roof-detail mesh has 68 boundary/non-manifold edges, so its surfaces are not a closed solid even though the current preview renders acceptably. The exterior preview is visually readable, though the brick repetition and broad roof surface look somewhat procedural. |
| Schematic interior and labeling | 0.9 / 1.5 | The interior objects are explicitly named `KDRInterior_Schematic_*`, and the documented build notes say the partitions are not an as-built plan. This correctly limits the claim. The interior preview reads as a sparse partition/furniture diagram, but it has no visible on-image “schematic / not surveyed” annotation and little room-specific structure. |
| **Total** | **7.7 / 10** | **Below the 8.0 acceptance threshold.** |

## Verification record

- The exact requested SHA was present before and after reopening; Blender reported **5.2.3 LTS** and loaded the expected scene, export collection, and stable `House_1089876362` mesh.
- The asset contains 10 scene objects, including 9 asset mesh objects; the house shell has 40 vertices and 22 faces, and its `KDR_Wall_UV_Metric` UV layer is present.
- The external-image probe found no unpacked file textures. Material nodes are embedded in the `.blend`.
- Source references inspected: local Purdue GIS FID 801 GeoJSON; Indiana 2023 orthophoto crop; NPS Hills & Dales nomination pages that list Photo 37; and Purdue's public KDR address reference. The NPS form's Photo 37 listing describes a photograph but does not supply that photograph in the local 42-page nomination PDF.
- The saved builder exterior and interior previews are under `audit/kappa_delta_rho/previews/`; the GIS overlay in the builder audit was not used as proof because it traces an older probe outline rather than the current mesh.

## Fixes to reach 8+

1. Find and cite a house-specific facade image (preferably current street-level front and side views). Then revise the entry, window rhythm, dormer form, trim, and brick color against that reference. Keep excluding the Kappa Delta Sorority at 358 Northwestern and other schools' KDR houses.
2. Use a measured elevation or well-oriented street view to resolve wall/eave/ridge heights and confirm the dormer count/profile. Preserve the GIS-exact wall footprint while correcting the vertical dimensions.
3. Close or cap the roof-detail surfaces that currently produce 68 boundary edges, then recheck the modular export and render.
4. Add a visible annotation to the interior preview saying it is a schematic, unsurveyed layout; improve the diagram's room/circulation differentiation only where it does not imply an actual floor plan.

## Source links

- Purdue address reference: https://www.purdue.edu/uns/x/2007b/070817PendletonSuspend.html
- Hills & Dales National Register nomination (includes the Photo 37 index and general Period Revival context): https://npgallery.nps.gov/GetAsset/8fbecfac-a7c8-46c8-a6e5-999d5e77906f
- Exact GIS record and orthophoto used for geometry/roof-plan checks: `../sources/purdue_gis_fid801.geojson` and `../sources/indiana_2023_orthophoto_kdr_crop.png`
