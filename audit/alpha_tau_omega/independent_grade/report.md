# Independent grade — Alpha Tau Omega (FID 785)

**Result: 8.5/10 — PASS** (minimum 8/10)

**Candidate:** `modular/buildings/massing_house_301840870_c45a5f4.blend`  
**SHA-256 verified independently:** `99C798326ED74F49BC635308EEAC1A962906BDFD74D71E240B4C9A8B895A78B4`

## Criterion scores

| Criterion | Score | Findings |
|---|---:|---|
| Identity and source-backed footprint | 2/2 | Purdue GIS FID 785 identifies SOATO / Alpha Tau Omega; the National Register packet and historic photos support the historic house identity and Tudor Revival description. The GIS polygon compared with the five structural footprint components yields IoU 0.942 (566.91 m² GIS; 593.03 m² model; 562.72 m² intersection). |
| Position, orientation, and dimensions | 2/2 | Candidate extents closely match GIS, with correct campus-world positioning/orientation. Coordinate conversion is a documented local approximation, not a survey. |
| Height, floors, and roof | 1.5/2 | The documented 2.5-story form and photos support the dormers, steep roof, and chimneys. Measured vertical drawings were not found; roof and facade heights are estimates. Fresh-open extent reaches 13.89 m at the chimney cap. |
| Facade, entrance, and distinctives | 1/2 | Brick, stone, dormers, leaded windows, tower, pointed entry, porch, slate-like roof, and interior cues are represented. Historic photo 9 shows a more articulated light-stone tower and a more complex roof/wings; the current model regularizes those forms and the bay/window rhythm. |
| Modular export, portability, and evidence | 2/2 | Blender 5.2.3 freshly opened the asset. Stable scene/collection/root names and identity root transform are preserved; 126 objects, node materials, no unassigned mesh materials, and no external image dependencies. Evidence, source snapshots, GIS overlay, and exterior/interior previews are present. |

## Concrete remaining refinements

- For a closer historic-photo match, revise the central tower material/proportions, roof-wing silhouette, and front bay/window rhythm.
- Exact heights and roof dimensions remain unverified without an authoritative section or elevation.
- The interior representation is clearly schematic; evidence supports named rooms/features but does not establish measured room dimensions or partition layout.

## Review evidence

- Fresh-open inspection: [fresh_open.json](fresh_open.json)
- GIS calculation: [gis_comparison.json](gis_comparison.json)
- Evaluator and machine-readable score: [evaluator.py](evaluator.py), [result.json](result.json)
- Candidate exterior previews: [front](../previews/ato_exterior_front.png), [three-quarter](../previews/ato_exterior_three_quarter.png)
- GIS overlay: [candidate footprint vs source](../previews/gis_candidate_footprint_overlay.jpg)
- Historic reference: [NPS photo 9](../previews/nps-photos-19.png)

Review was read-only for the candidate and shared files; the only new files are inside `audit/alpha_tau_omega/independent_grade/`.
