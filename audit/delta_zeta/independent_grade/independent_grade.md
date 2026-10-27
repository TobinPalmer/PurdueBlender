# Delta Zeta independent grade — latest asset

**Result: 8.25 / 10 — pass (minimum 8 / 10).** This grade replaces the earlier inspection and uses a fresh Blender 5.2.3 reopen of the current asset, the current preview, and the saved official sources.

| Criterion | Score | Findings |
|---|---:|---|
| Identity and source-backed footprint | 2.00 / 2 | Purdue GIS FID 752 and Xi Omega history support the identity/address. All 11 GIS ring vertices match the mesh base within 0.000032 m. |
| Position, orientation, dimensions | 1.75 / 2 | Identity transform and campus placement are intact. Current evaluated roof bounds exceed GIS bounds by only 0.145 m west and 0.229 m south (effectively ordinary eave overhang). The official photo has no geolocation, so frontage bearing remains unverified. |
| Height, stories, roof | 1.25 / 2 | The photo supports a multi-level house with several steep gables; the model has two main facade levels and is 14.65 m tall. Height and story count are not measured. GIS `NUM_LEVELS=1` conflicts with the photo's apparent multi-level facade, and `Extrution=36` has no documented units or meaning. Roof intersections remain simplified. |
| Facade and distinctive architecture | 1.25 / 2 | The preview includes the source's brick, dark shingles, pale trim, arched upper entry glazing, dark doors, and repeated windows. Entrance placement along the shown facade differs from the photo's near-end placement; because the photo is oblique and unlocated this is concerning but cannot be definitively mapped. Window rhythm and roof geometry are simplified. |
| Modular export, portability, evidence | 2.00 / 2 | Expected collection contains one mesh; identity transform, all footprint vertices, and no external image dependencies confirmed. Current evaluated mesh has 6,820 vertices and 1,686 faces. |

The previous grade's roughly 7.4 m roof overrun is stale. The current version's roof silhouette now stays within about 0.23 m of the GIS perimeter. Story count, exact heights, and facade orientation remain uncertain because no measured elevation, floor plan, or georeferenced image is available.

Sources inspected: [official Xi Omega history](https://www.dzxiomega.org/history) · [official Delta Zeta 2023 house photo](https://www.deltazeta.org/blog/featured-house-xi-omega-purdue-university/). Raw GIS source and current preview are included in the building audit.

Evaluator: `evaluate.py` · result: `result.json` · fresh Blender reopen data: `blender_probe.json`.
