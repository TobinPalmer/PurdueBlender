# Felix Haas Hall — independent grade, round 11

**Score: 7.7/10 — below 8/10**

**Exact asset SHA-256:** `e333a99e9b7bbb3288329afad7af177be62d73d9077146a4a579c4b123cb1ec1`

I independently verified the current asset hash against the round-11 reopen record and inspected the saved exterior/entrance renders against Purdue's preserved exterior image. The arch and stonework now capture important facade cues that were missing in round 10. The exaggerated roof silhouette and uncertain dimensional claims remain the main fidelity limits.

| Criterion | Score | Evidence and findings |
|---|---:|---|
| identity and source-backed footprint | 1.8/2 | Official Purdue Events imagery identifies Felix Haas Hall and supports its red roof and signature front; Purdue Archives dates the former Memorial Gymnasium to 1908. The GIS shell was unchanged from the earlier shell review. Round-11 evidence still treats photo-derived form as qualitative. Identity and plan envelope are well supported; no new round-11 pointwise GIS overlay was run. |
| position, orientation, and dimensions | 1.5/2 | The saved local frame and placement origin are reported unchanged; the existing shell bounds are retained. The round-11 exported extent reaches X=19.136 m while the cited shell reaches X=12.981 m, so roof projection extends about 6.15 m beyond the shell on that side. Location continuity is supported, but facade bearing/dimensions are estimates and the roof overhang/projection is conspicuously large relative to the unchanged wall envelope. |
| height, floors, and roof | 1.1/2 | The historical Purdue timeline supports 17 entrance steps. The official photo supports a red-clay roof, but has no calibration. The round-11 edit raised roof rise by 1.8x; export top is Z=15.84 m versus cited shell top Z=11.5 m. The roof reads much taller and broader than its facade in the saved overview. Roof rise/profile and upper floor heights lack measurable source evidence; the increase is explicitly estimated. |
| facade, entrance, and distinctive architecture | 1.6/2 | Round 11 adds segmented stone portal voussoirs, pilasters/capitals, an arched transom, and two lower arched window surrounds. These address signature arches visible in the official exterior photo; brick/stone palette and roof tile color are improved. The render remains simplified and heavily planar compared with the photo; masonry hierarchy and the roof-to-facade proportion still need refinement. Opening dimensions and detailing are estimated from perspective imagery. |
| modular export, portability, and evidence | 1.7/2 | Exact SHA matched; the exact asset reopened in Blender 5.2.3. Stable export collection is Asset_felix_haas_hall with 919 objects / 879 meshes; round-11 BVH report found no new-to-existing surface intersections; no external images or image-texture nodes were reported. Builder provides official source links, uncertainty, renders, and intersection evidence. The shared manifest is stale: it still records 879 objects and local max Z=14.0, versus reopened export 919 objects and max Z=15.84000015258789. Interior is explicitly schematic. |

## Priority revisions

- Recheck the broad/tall roof silhouette and X-positive overhang using additional elevations, aerial/LiDAR, or a better-calibrated source; reduce unsupported projection/height if evidence warrants.
- Refine the large facade fields and stone/brick hierarchy to better match the official photograph without inventing unsupported dimensions.
- Update manifest count/bounds only after this exact asset version is accepted and integrated.

## Files reviewed

- `audit/batch3_haas/round11_evidence.md`
- `audit/batch3_haas/round11_validation.json`
- `audit/batch3_haas/round11_intersections.json`
- `audit/batch3_haas/exterior_round11.png`
- `audit/batch3_haas/entrance_round11.png`
- `audit/batch3_haas/interior_plan_round11.png`
- `audit/batch3_haas/exterior_reference.jpg`
- `audit/batch3_haas/independent_review_round10.md`
- `modular/manifest.json`

The report is read-only; the building asset and shared master/indexes were not changed.
