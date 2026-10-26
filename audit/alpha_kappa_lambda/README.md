# Alpha Kappa Lambda evidence notes

Asset stable ID: `massing_alpha_kappa_lambda_88dda6c` (Rossen assignment).

The Purdue ArcGIS feature FID 784 identifies Alpha Kappa Lambda (SOAKL), 417 Waldron St. The saved feature geometry is EPSG:4326 and was transformed with the campus README's local lon/lat approximation. The model is one closed massing mesh in campus coordinates, with the expected scene, collection, object, and relative asset path retained.

The GIS source has `NUM_LEVELS=1`, `CountOfFLO=1`, and `Extrution=12`, but the extrusion units are not documented. The reported `Shape__Area` (822.76 m²) is inconsistent with the ring area from the documented approximate conversion (475.96 m²). The discrepancy is retained as unresolved. Height is therefore only a provisional 12 m interpretation; it is not measured. Roof, facade, openings, materials, and entrance remain unverified, and no such architectural details were invented.

Historical records confirm the chapter's use of 417 Waldron and document photographs of members outside the house in 1946-47. Those records establish historical identity/context only. They do not prove the current facade or building continuity. The 1950 Logos issue and J.C. Allen photo inventory are saved locally; the Purdue archive catalog record itself returned HTTP 403 to a local snapshot request. Catalog and source URLs, providers, dates, CRS, methods, and uncertainties are listed in `evidence.json`.

`build_result.json` records projected geometry bounds. `portability_check.json` records that Blender reopened the saved `.blend`, found the expected named collection, and linked that collection into a fresh empty file with no external image dependencies. The preview is `alpha_kappa_lambda_preview.png`.
