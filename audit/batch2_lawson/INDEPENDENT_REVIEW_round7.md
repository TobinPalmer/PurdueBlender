# Lawson Hall — independent R7 review

**Grade: 7.8/10 — below the 8/10 minimum.** I reopened the exact saved asset in Blender 5.2.3 LTS and independently recomputed the GIS boundary fit. SHA-256: `efd340e3977f1140686dccb48ab714b273e2d79a1fe8de83efe71b02ddb583b0`.

| Rubric criterion | Score |
| --- | ---: |
| Correct identity and source-backed footprint | 1.9/2 |
| Position, orientation, and scale/dimensions | 1.7/2 |
| Evidence-backed height, floors, and roof form | 0.9/2 |
| Facade, entrances, and distinctive architecture | 1.5/2 |
| Interior, materials, modular export, and evidence | 1.8/2 |
| **Total** | **7.8/10** |

## Findings

- **Identity and footprint:** The project asset is Lawson Hall and its horizontal outline corresponds closely to Purdue GIS BuildingShapes FID 59. I reopened the model and sampled 21 points on each of the 54 GIS edges against the saved lower shell/vestibule linework: all 1,134 points were within 0.10 m; maximum nearest-line distance was 0.0000152 m. This is strong evidence for the 2D footprint, not for height or all exterior surfaces.
- **Placement and scale:** The asset root has an identity transform. Plan/GIS control points and the PDF scale bar support the north-up L1 layout at approximately 0.0921 m/pixel X and 0.09234 m/pixel Y, with about 0.3 m image-pick uncertainty. An existing master-marker record reports `[-282.5, 44.0, 0.0]`, zero rotation and unit scale; I did not freshly reopen the master for this evaluation.
- **Height and roof:** The file bounds reach Z=21.30 m. Purdue GIS reports five levels, but no measured roof/elevation drawing or complete upper-floor plan was found. Roof/penthouse heights and the north closure height remain estimates; no verified continuous stair route is shown. This is the largest source-fidelity gap.
- **Facade and entrance:** The new entrance location and plan perimeter are better tied to the registered plan/GIS shape. The inspected Purdue photo supports the curved light-stone entrance canopy, named fascia, glazed entry, steps, and handrails. The exterior render also reads as brick with horizontal pale bands, repeated windows, and a curved glazed Commons volume. However, the façade rhythm, roof silhouette, glazing dimensions, and much of the upper mass remain schematic. The entrance measurements are visual estimates, not taken from an elevation drawing.
- **Interior and export:** The cutaway includes broad L1 zoning, circulation, seating and the Commons wall. Purdue's 2011 article says the historical wall was 16 by 9 feet and consisted of 16 displays in a 4-by-4 grid; the detail render shows 16 modules. The reopened export has 615 objects / 612 meshes, identity root, material slots on all meshes and no missing external image files. Upper-floor spaces and stair continuity remain unverified, and some furniture/layout details are illustrative.

## Reason for the score

R7 materially improves the prior 7.0 grade: the southeast vestibule and north-edge closure were corrected, the plan registration was recomputed, and the full 2D GIS outline now matches. The asset earns 7.8, but it does not yet reach 8 because vertical form and roof remain unsupported and the exterior/interior are still visibly schematic. A successful 2D footprint comparison cannot establish those missing dimensions.

## Evidence files and sources

- Independent reopen and geometry check: `independent_reopen_r7.json` and `independent_reopen_r7.py`.
- Builder's R7 validation, evidence and renders: `validation_round7.json`, `evidence_round7.json`, `exterior_round7.png`, `interior_cutaway_round7.png`, `entry_lobby_round7.png`, `commons_wall_round7.png`, `gis_shell_plan_overlay_round7.png`.
- Purdue CS first-floor plan: https://www.cs.purdue.edu/resources/docs/lawson_1.PDF
- Purdue 2024 entrance photo page: https://www.purdue.edu/science/about/news/articles/2024/celebrating-2024-top-20-stories-from-the-college-of-science.html
- Purdue 2011 video-wall article: https://www.cs.purdue.edu/news/articles/2011/harris-video-wall.html
- Purdue 2006 Echo Spiral article: https://www.cs.purdue.edu/news/articles/2006/echo-spiral.html
- Purdue GIS FID 59 query: https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query?where=FID%3D59&outFields=*&returnGeometry=true&outSR=4326&f=json
