# Independent Kappa Delta Rho rerating — 2026-10-26

**Asset:** `modular/buildings/massing_house_1089876362_14ecd2c.blend`  
**Exact SHA-256 reviewed:** `c871289baa956e828d607fe7065b8b0e001ef39acc147fbb3318ee4a4655758e`  
**Fresh open:** Blender 5.2.3 LTS in a separate background process  
**Result:** **7.9/10 — below the 8.0 acceptance threshold**

## Independent checks

- The file reopened and retained the expected scene (`Building_massing_house_1089876362_14ecd2c`), export collection, stable house mesh, and expected KDR-specific detail/interior collections.
- Asset SHA matches the builder's reported `c871289baa956e828d607fe7065b8b0e001ef39acc147fbb3318ee4a4655758e` exactly.
- Purdue GIS FID 801 names Kappa Delta Rho at 1134 Northwestern Avenue. Its 20-ring lower outline still matches all 20 model base vertices within **0.000057 m maximum** and **0.000032 m RMS** using the project's stated local lat/lon-to-meter approximation. This supports footprint/placement but does not validate vertical dimensions.
- Independently rechecked each of the 10 mesh objects. All report **0 boundary edges, 0 nonmanifold edges, and 0 loose edges**. The reported roof closure fix passes.
- The file has nine procedural, embedded materials, including a noise/brick/bump network, slate variation, limestone relief, stained wood, and glazing. No unpacked external image paths were found. The stable collection contains the house, architectural trim, limestone, glazing, woodwork, roof, chimneys, and clearly named schematic partitions/floor/furnishings.
- Visual review of the saved exterior preview finds a legible, coherent two-story brick fraternity-house massing with repeated divided-light windows, a centered entry surround, hipped roof, and three dormers. The repeated regular fenestration and roof/window styling still read as a generic period-house interpretation; no direct, identified KDR-at-1134 facade photo is available to verify those choices.
- The interior preview is an explicitly labeled diagram, **“SCHEMATIC INTERIOR | NOT SURVEYED.”** It conveys a partitioned plan and furniture blocks, but it is sparse and not based on a verified/registered floor plan. It should not be represented as actual interior architecture.

## Rubric

| Category | Score | Rationale |
|---|---:|---|
| Identity and source attribution | 1.5 / 1.5 | Exact GIS name/FID/address checked; separate Kappa Delta Sorority is not substituted. |
| Footprint, placement, and orientation | 2.0 / 2.0 | Exact 20-vertex GIS match within numeric tolerance; identity/address supported. |
| Massing and roof form | 1.2 / 1.5 | Coherent roof planes, chimneys and dormers with roof plan/tone informed by aerial imagery. Heights remain estimated; aerial cannot verify facade roof profile. |
| Facade fidelity | 0.8 / 2.0 | Clean, detailed model, but brick color, window rhythm, portico, trim, shutters/dormers lack a direct identified facade reference and remain estimates. |
| Geometry, materials, portability | 1.5 / 1.5 | Topology fix passes across every mesh; procedural materials are embedded; no unpacked external images. |
| Interior and labeling | 0.9 / 1.5 | Honest visible “not surveyed” caveat and schematic objects; sparse generic layout with no registered plan evidence. |
| **Total** | **7.9 / 10** | **Below threshold** |

## Decision and remaining work

The roof topology remediation is verified. Do not integrate as an accepted ≥8/10 building yet under the project threshold: the independent grade remains 0.1 below it, primarily because the architecture is not supported by a clearly identified facade source and because the interior diagram is generic. Stronger KDR-specific imagery or an official elevation could justify evidence-led facade work and a higher grade. Do not borrow imagery from another chapter or the Kappa Delta Sorority. Heights and interior remain unresolved estimates.

## Evidence files

- `fresh_open_probe.json` — exact-SHA open, scene/collection identity, source crosswalk, footprint error, material/dependency inventory, and per-mesh topology.
- `fresh_open.log` — separate Blender process output.
- `../previews/kappa_delta_rho_exterior.png` and `../previews/kappa_delta_rho_schematic_interior.png` — visually reviewed previews.
- Prior grade baseline: `../independent_grade/grade_report.md` (graded previous SHA, not this one).
