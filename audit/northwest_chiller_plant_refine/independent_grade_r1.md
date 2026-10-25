# Northwest Chiller Plant — independent asset grade

**Grade: 8.3 / 10 — meets the 8/10 threshold, with documented evidence limits.**

Reviewed 2026-10-25. This grade applies to the asset hash below and the current reconciled manifest. It is an independent review of identity, placement, form, visible detailing, materials, and file portability. It does not certify as-built architectural accuracy.

## Evidence and reopen checks

- Asset: `modular/buildings/northwest_chiller_plant.blend`
- SHA-256: `f764c63493bdf3258cfe3783e79f022a0dd48ce337aafa4a0486bf06ac29b5b6`
- Reopened in Blender 5.2.3 LTS from disk.
- `Asset_northwest_chiller_plant` contains 572 objects (571 meshes, 1 font), 29 distinct materials, and no materialless meshes.
- Manifest has 572 names and 572 objects; the reopened object-name inventory matches exactly (no missing or extra names). Reopened full asset bounds match the manifest bounds exactly at the saved precision.
- GIS shell bounds are `[-17.004774, 20.493732] × [-18.566463, 21.454014] × [0.3, 10.5] m`. The six-vertex authoritative GIS shell is retained. The shell measurements are internally consistent with the GIS-derived source asset and are distinct from the full asset bounds, which include roof equipment up to 13.77 m.
- Master blend resolves the linked asset to the expected file and collection, with 572 linked objects. Its placement marker is `(-994.953003, 200.167007) m`, within 0.000009 m of the manifest coordinates; scale is `(1,1,1)` and rotation is zero.
- No external image textures are referenced, so no missing-image paths were found. Materials are portable procedural/node materials.
- Reopen evidence: `independent_reopen_r1.json`. The initial builder-side reopen record is `reopen_validation.json`.

## Rubric

| Category | Score | Basis |
|---|---:|---|
| Identity and footprint | 1.9 / 2.0 | Correct utility plant identity and official GIS shell retained; exact footprint trace is consistent. Minor deduction because exterior architectural reference imagery/drawings were not available to independently validate the modeled facade. |
| Position and scale | 2.0 / 2.0 | Master marker agrees with the manifest to under 0.00001 m; unit scale and zero rotation; linked collection resolves to the expected asset. |
| Height, levels, and roof form | 1.7 / 2.0 | GIS source describes a two-level, 10.2 m shell; the building reads as a low industrial plant, with roof equipment extending above the shell. The five cooling-cell enclosures and their exact configuration are explicitly typological and not verified against as-built plans. |
| Facade and visible equipment | 1.5 / 2.0 | Legible industrial facade with framed acoustic-louver bays, panel joints, service doors, rooftop screen, and cooling-cell detailing. Exact louver rhythm, equipment quantity/placement, pipe routing, and service-yard arrangement lack source verification; the visible mechanical composition remains interpretive. |
| Materials, interior, and export | 1.2 / 2.0 | Procedural concrete, metal, louver, membrane, and equipment finishes are assigned and portable; no broken image dependencies. Interior is schematic rather than evidenced or functionally detailed. Some surfaces would benefit from finer material variation and verified details. |
| **Total** | **8.3 / 10** | **Pass (>=8.0)** |

## Main gaps

1. Obtain a verified exterior photo set or construction/equipment drawings before claiming exact facade, rooftop layout, or piping accuracy.
2. Validate the five cooling-cell units and screen proportions, and replace typological equipment placement with evidence-based positioning.
3. Improve the interpretive service-yard pipe/cable composition and provide more meaningful interior equipment only where documentation supports it.
4. Current official source set confirms the plant's utility function and pump/support-equipment upgrade scope, but it does not establish the exact visible architecture. The visual finish is therefore better supported than the as-built detail.

## Sources consulted

- [Purdue GIS BuildingShapes FeatureServer](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0) — footprint/elevation evidence.
- [Purdue Board project record (2022)](https://www.purdue.edu/bot/meetings/past-meetings/2022/07.%20aug/pfc/Northwest%20Chiller%20Plant.pdf) — confirms chiller-plant function and pump/support-equipment work.
- [Purdue Northwest Chiller Plant System Improvements](https://www.purdue.edu/treasurer/finance/wp-content/uploads/2023/04/Northwest-Chiller-Plant-System-Improvements-B-1-23-2-04.pdf) — project scope and utility systems context.
- [Purdue Athletics traffic notice](https://purduesports.com/utility-project-altering-baseball-softball-track-traffic) — plant location context.

## Review limits

This assessment is based on the reopened Blender asset, its overview/detail renders, the GIS record, project notes, and the official documents above. The available official documents do not provide sufficiently detailed exterior views or as-built equipment plans to support a higher claim of exact visual fidelity. The grade should be revisited if those references become available.
