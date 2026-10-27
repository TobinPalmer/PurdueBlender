# Independent asset grade: Kappa Alpha Theta (FID 786)

**Result: 8.2/10 — pass.** This is an independent review of the saved modular asset, not a claim that its placement has already been integrated into or verified in the master scene.

## Identity and file verification

- File: `modular/buildings/massing_house_301840865_cbf7de2.blend`
- Expected SHA-256: `20dc22e31a3fa189e258b1d22084cbbc646dbdfdc4b643c30a9510f61652bdcd`
- Actual SHA-256: `20dc22e31a3fa189e258b1d22084cbbc646dbdfdc4b643c30a9510f61652bdcd` — exact match.
- Independently reopened with Blender 5.2.3 LTS in a fresh background process. The file opens and identifies `Building_massing_house_301840865_cbf7de2` / `Asset_massing_house_301840865_cbf7de2`; 430 objects, 429 meshes, 15 materials, no linked libraries, and no missing external images.
- FID 786 raw GIS attributes identify Kappa Alpha Theta (`SOKAT`, 607 Russell St). Official chapter/facility sources further identify the 607 N Russell chapter house.

## Category scores

| Category | Score | Evidence and limits |
|---|---:|---|
| FID 786 identity | 1.9/2 | Stable asset naming and independent GIS record agree on Kappa Alpha Theta. |
| GIS anchor and shell envelope | 1.6/2 | Asset is modeled around the documented polygon-centroid anchor. Its local bounds (27.85 × 33.69 m) fit inside the transformed GIS envelope (31.94 × 40.07 m). The local projection is approximate; the GIS outline is not a surveyed wall line, and the master-scene instance/transform was not part of this saved-asset inspection. |
| Exterior and courtyard match | 1.7/2 | Official photos support the multi-wing brick form, white trim, dark shutters, planted courtyard and columned entry. These are recognizable in the asset. Precise wing geometry, planting layout and window spacing remain interpretive. |
| Roof, stories and facade | 1.2/2 | Three-level entrance volume and repeated sash-window facade read credibly. Compared with the official entry photos, the model’s broad roof planes understate the prominent gabled entrance silhouette; pale stone/arched lintels and some entry details also need stronger definition. GIS `NUM_LEVELS=1` / `Extrution=12` are inconsistent with visible photo evidence and were not used to overrule the photos. |
| Packaging and interior treatment | 1.8/2 | Fresh open succeeds, materials are present, and no linked libraries or missing external images were found. Interior geometry is correctly labeled schematic rather than represented as a verified floor plan. |
| **Total** | **8.2/10** | **Pass** |

## Highest-value follow-up changes

1. Make the south/entry roof read as the photo’s pronounced gable, with a clearer ridge and pitched roof silhouette instead of the current dominant continuous roof plane.
2. Add or sharpen pale stone/arched lintels at the entry and prominent windows; strengthen the central entrance and sign details to match the official photos.
3. Before treating placement as verified, instance this asset in the master and check its translation/orientation against FID 786. The centroid is a documented anchor, but the source ring is generalized and the south-facing facade bearing is inferred.
4. Keep the interior labeled schematic unless a reliable floor plan is obtained.

## Evidence consulted

- Raw Purdue ArcGIS FID 786 response: `../fid786.json` and the source endpoint documented in `../evidence.md`.
- Official chapter home/gallery and official facility material, including the archived official photos `../house_2019.jpg`, `../house_2021.jpg`, and `../official_facility_1990.jpg`.
- Independently opened asset probe: `fresh_open_probe.json`; Blender log: `probe_asset.log`.

The report is limited to this grade folder; the `.blend` asset and shared project files were not modified.
