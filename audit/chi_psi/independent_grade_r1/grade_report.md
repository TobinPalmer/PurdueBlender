# Independent grade — Chi Psi Epsilon Tau Lodge R1

**Asset:** `modular/buildings/chi_psi.blend`  
**SHA-256:** `2b6ff1154b245fbe6b8a4c600f3aeadb3b0a0c238825e204ab275e69f84eba04`  
**Score:** **8.1/10 — PASS** (8.0 minimum)

| Criterion | Score |
|---|---:|
| Identity and site placement | 1.6/2 |
| Footprint and form | 1.8/2 |
| Facade, material, and source fidelity | 1.8/2 |
| Interior | 0.9/2 |
| Portability and fresh-open validation | 2.0/2 |
| **Total** | **8.1/10** |

## Findings

I verified the requested SHA and opened the saved blend directly in Blender 5.2.3 LTS. The file contains the expected `Building_chi_psi` scene and `Asset_chi_psi` export collection. Direct inspection confirmed 225 recursively included objects (216 meshes), 11 schematic interior objects, differentiated procedural material assignments, and no external image dependencies. The separate fresh-open validation record passes for the same hash and includes an evaluated render.

The best identity evidence is Chi Psi's own Summer 2024 newsletter: it calls the pictured building the new Chi Psi Lodge at Purdue and gives Epsilon Tau Lodge as 950 David Ross Rd. Its photo closely supports the modeled two-storey red-brick facade, twin gables, paired tall arched windows, repeated sash openings, dark roof, and offset entrance. Current chapter listings support Epsilon Tau's Purdue identity. The parcel and Purdue GIS support the site address. The model correctly uses the 2018 Indiana LiDAR quadrilateral for its shell because the Purdue GIS FID 748 outline fits poorly.

**The occupancy conflict remains unresolved:** Purdue GIS FID 748 labels the address Zeta Psi, and a Zeta Psi profile reportedly also lists it. The specific Chi Psi newsletter is strong evidence that Chi Psi uses the lodge, but it does not establish current exclusive occupancy. I preserve that uncertainty and make no exclusivity claim. No current Street View or current dated facade image was available, so exterior fidelity is evaluated against the official 2024 newsletter photo.

The interior is explicitly schematic: floor plates, partitions, common-room furniture cues, and a dining counter. No authoritative interior plan was found, so this is only limited interior massing rather than a verified layout.

## Limitations

- The Purdue FID 748 area field and Indiana LiDAR area field each conflict with areas computed from their rings using the repository's approximate local conversion. The builder uses the spatial geometry, not those area attributes, as the footprint reference.
- The local coordinate conversion is not a surveyed CRS and source data provide no positional tolerance.
- Exact heights, roof pitch, window dimensions, trim, entrance coordinates, current facade condition, and interior layout are not verified by measured plans/elevations.
- Current Chi Psi/Zeta Psi occupancy at 950 David Ross Rd remains a material crosswalk question.

No changes are required to reach the 8/10 threshold. Higher confidence would require resolving the occupancy crosswalk, finding current georegistered images or measured elevations, and sourcing an interior plan.

## Reproducibility artifacts

- `result.json`: full scores, evidence, rationale, and limitations.
- `asset_probe.json`: direct read-only inspection of the saved blend.
- `probe_asset.py`: script used for that inspection.
