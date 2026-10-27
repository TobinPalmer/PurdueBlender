# Ernest C. Young Hall master integration review

**Result: 8.35/10 — PASS**  
**Review date:** 2026-10-26  
**Scope:** Independent, read-only review of the freshly opened `purdue_campus_master.blend`, its linked YONG library, and the saved source evidence.

| Criterion | Grade |
|---|---:|
| Correct identity and source-backed footprint | 2.00/2 |
| Position, orientation, scale and plan dimensions | 1.90/2 |
| Evidence-backed height, floors and roof form | 1.30/2 |
| Facade, entrance and distinctive architecture | 1.45/2 |
| Modular export, portability and evidence completeness | 1.70/2 |
| **Total** | **8.35/10** |

## Integration checks

- The fresh-open master contains exactly one `Placement_massing_young_hall_yong_cae1b95` marker and one linked instance of `Asset_massing_young_hall_yong_cae1b95`.
- The marker is at `(260.9057, -503.5166, 0.0)` with identity rotation and unit scale. Its library path matches the manifest. The asset collection is not also linked directly under the scene root.
- Manifest and linked collection both report 23 objects (21 meshes, one font, one asset root empty); all required objects are present.
- The integrated world bounds match the standalone pre-localization fresh-open bounds with a maximum difference of **0.000 m**. The GIS-derived shell bounds also match. Purdue GIS FID 70's 34-vertex footprint matched the standalone shell ring within **0.000032 m**.
- The linked asset has no external image dependencies. Other external images in the master belong to unrelated buildings and were excluded from the YONG dependency result.

## Accuracy findings and limitations

Purdue Archives record 656 identifies Ernest C. Young Hall and states ten stories. GIS FID 70 reports eleven levels; the discrepancy is unresolved. The modeled shell is about 31.09 m tall, interpreting GIS `R=102` as feet, but the GIS unit is undocumented. Historical Archives photos support the slab form, pale panel facade, repeated vertical window bays, and flat roof; they are undated. The current Purdue reference supports the red-brick sign wall but is only a close crop. The exterior render is bright and some facade/entrance details remain schematic. The interior is a small schematic lobby/corridor slice without a source floor plan. Campus registration is project-coordinate based rather than survey controlled.

The building meets the requested 8/10 threshold. See `result.json` for per-criterion evidence, findings, and machine-readable checks.
