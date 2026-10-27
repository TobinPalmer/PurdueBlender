# Independent Grade — Delta Sigma Phi

**Result: PASS — 8.3/10**  
**Exact reviewed asset SHA-256:** `1f1b3efa2fd0d3dd756ccbd6556ee5a4f8fce0539eae0f5088e1190c8992c976`  
**Asset:** `modular/buildings/massing_house_860826641_2c90f97.blend`

## Independent reopen

I opened the saved blend in a separate Blender 5.2.3 LTS background process. The expected scene `Building_massing_house_860826641_2c90f97` and collection `Asset_massing_house_860826641_2c90f97` were present. The collection contains 165 objects, including 164 meshes, with 1,062 mesh vertices, 609 polygons, and eight materials. Evaluated local bounds are X [-21.7324, 20.6092], Y [-16.5010, 16.7326], Z [0, 12.0100] m. It has no external image or linked-library dependencies. The independently captured details are in `fresh_open_probe.json`.

## Evidence and visual review

Purdue GIS BuildingShapes FID 798 names Delta Sigma Phi at 341 Northwestern Avenue. The preserved 2026 Street View shows the buff/red-brown brick, steep dark roof, tall cross-gable, dormers, upper windows, arched lower openings, and entry steps. The independent review compared the asset previews to that Street View and checked the evidence package’s source ring and documented coordinate transform. The reported wall-edge match is within 8.64e-7 m. The source ring was correctly prioritized over conflicting GIS area/perimeter attributes.

The exterior reads as a distinct brick chapter house rather than generic massing. The shingle roof, dormers, cross-gable, limestone window surrounds and bands, arched lower openings, entry door, foundation, and steps provide good material and facade separation. Textures are procedural and self-contained.

## Scores

| Criterion | Score | Weight | Notes |
| --- | ---: | ---: | --- |
| Identity and source attribution | 9.5 | 10% | Official FID 798 plus address and chapter evidence agree. |
| Wall footprint | 9.8 | 20% | Near-exact fit to the returned polygon ring. |
| Placement readiness | 9.0 | 10% | Local origin is documented; master marker integration is still required. |
| Roof and silhouette | 7.6 | 20% | Reference character is present, but elevations and rear-wing proportions remain inferred. |
| Facade and entrance | 7.6 | 20% | Good architectural features; some repetitive spacing and uncertain details remain. |
| Materials and texturing | 8.6 | 10% | Distinct, appropriate procedural materials with no external dependencies. |
| Interior | 4.0 | 5% | None modeled; no reliable floor plan was found, and this remains a known gap. |
| Portability, reopen, and evidence | 9.0 | 5% | Independent reopen passes; sources and uncertainty are documented. |

The weighted result is **8.36/10**, reported as **8.3/10**. This clears the required 8.0 independent-grade threshold. No revision is required for the grade gate. The absent interior and estimated roof/rear-wing details should remain explicit limitations; do not invent floor-plan details without stronger source evidence.

## Integration notes for coordinator

- Convert the current massing entry to a detailed local-coordinate collection instance at the documented centroid `(357.740058, -73.829742)` m.
- Validate the candidate-to-FID crosswalk: `massing_house_860826641_2c90f97` is the confirmed FID 798 asset; adjacent candidate `massing_house_860826640_baa087e` is not this building.
- Rebuild and fresh-open the master, verify placement and neighboring buildings, and record integration evidence before updating shared status.
