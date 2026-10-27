# Felix Haas Hall — independent grade, round 12

**Score: 8.4/10 — PASS (8/10 threshold met)**

**Exact evaluated SHA-256:** `0de3417c6cc3af247b2100242720d39871bc8ed188dcf06bfbb96d9bead2c067`

I verified the saved asset SHA against the fresh-open record, checked roof bounds numerically against the unchanged GIS shell, and inspected the reopened exterior and entrance renders against the preserved Purdue exterior reference. The R11 roof concern was based on the overall asset bounds, which included the long entrance stairs and cheek walls; object-specific roof bounds confirm a 0.25 m eave projection on all four sides.

| Criterion | Score | Evidence and findings |
|---|---:|---|
| identity and source-backed footprint | 1.8/2 | Official Purdue Events and archival sources identify Felix Haas Hall/former Memorial Gymnasium. The unchanged GIS shell bounds are reused from the documented earlier FID comparison; current asset preserves the shell and placement origin. Identity and plan-envelope basis are strong. The official exterior photo is qualitative and the R12 evidence does not repeat a pointwise GIS overlay. |
| position, orientation, and dimensions | 1.8/2 | R12 validation was recomputed against shell bounds: roof margins X−=0.250001, X+=0.250000, Y−=0.250000, Y+=0.250001 m. All equal 0.25 m within 1e-5. Placement origin and GIS shell were not changed. This corrects R11: the far-X asset bounds belong to entry stair treads/cheek walls, not the roof. Facade bearing and detailed dimensions remain estimates from uncalibrated perspective photography. |
| height, floors, and roof | 1.4/2 | Reopen report gives main roof eaves Z=11.7 m and ridge Z=14.0 m (2.30 m rise); entry roof peak is Z=13.2 m. Official image and 1922 Purdue publication support a red-tile, broad low-pitched roof, not an absolute elevation. Evidence explicitly labels 2.30 m and eaves as estimates; no scaled elevation was found. The R12 roof is materially less exaggerated than R11 and the 2.30 m rise is clearly uncertain. Absolute roof/floor heights and upper-storey/floor interpretation remain unverified. |
| facade, entrance, and distinctive architecture | 1.6/2 | Direct comparison of round-12 exterior/entrance renders with the preserved Purdue photo shows the red tile roof, arched central entry, two arched lower openings, segmented pale stone surrounds, masonry palette, and entrance stair retained after roof correction. The main photo-supported architectural cues hold. The facades remain simplified/stylized, with opening dimensions, detailing, and unseen elevations estimated; the interior plan is schematic, not a verified interior. |
| modular export, portability, and evidence | 1.8/2 | Exact saved SHA matched and reopened in Blender 5.2.3 LTS; stable collection `Asset_felix_haas_hall` contains 919 objects / 879 meshes. No external images or material-image nodes. The current manifest now has 919 object entries with the matching bounds/count. Source URLs, uncertainties, and fresh-open renders are recorded. The library is portable and the manifest count/bounds now match. Roof-specific geometry is validated; the schematic interior is deliberately not asserted as factual. |

## Roof bound verification

| Side | Projection beyond GIS shell |
|---|---:|
| x_minus | 0.250000674 m |
| x_plus | 0.250000218 m |
| y_minus | 0.249999817 m |
| y_plus | 0.250000775 m |

## Remaining uncertainty

The 2.30 m roof rise is expressly an estimate; no calibrated elevation or surveyed roof surface was found. The source photo supports the broad, low-pitched red-tile profile but not absolute dimensions. Upper floor heights, unseen elevations, and interior room geometry remain estimated or schematic.

## Evidence reviewed

- `audit/batch3_haas/round12_evidence.md`
- `audit/batch3_haas/round12_validation.json`
- `audit/batch3_haas/exterior_round12.png`
- `audit/batch3_haas/entrance_round12.png`
- `audit/batch3_haas/exterior_reference.jpg`
- `audit/batch3_haas/independent_grade_round11/grade_report.md`
- `modular/manifest.json`
