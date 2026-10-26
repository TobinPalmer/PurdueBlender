# Independent grade: St. Thomas Aquinas R3

**Asset:** `modular/buildings/massing_st_thomas_aquinas_5535390.blend`  
**Exact SHA-256:** `ec8ba6235c6a356ad81ab8b7ad8fcbe3bcc75c4071a310287ea3bb517ad5b7db`  
**Result: 7.7/10 — below the 8.0 acceptance threshold.**  
**Review date:** 2026-10-25  
**Blender:** 5.2.3 LTS

## Scope and exact-file check

I reopened this exact saved asset in a fresh Blender 5.2.3 process and recalculated its SHA-256 before grading. The hash matched. The exported collection has 1,204 objects (1,201 meshes, two empties, and one text object), an identity root, no materialless meshes, no invalid material indices, no missing external images, and no linked libraries. Its local bounds are approximately 43.5 × 70.9 × 20.1 m. Nineteen named materials are used. The root records the local-coordinate frame and campus origin `(21.3282375, -412.2141453) m`.

The GIS identity is Purdue BuildingShapes FID 852, St. Thomas Aquinas Center, 535 State St.; the corroborating OSM way is 117396617. The GIS/OSM plan IoU is 0.922. The footprint is a strong map-outline fit, but the polygon is not a wall survey. The parish and architect sources support three connected parts, while their exact boundaries and interior layouts remain interpretive. Source and uncertainty details are preserved in [R3 design evidence](r3_design_evidence.json) and [projected footprint evidence](projected_footprint_evidence.json).

Master placement is coordinator-verified separately and is excluded from this grade. This review assesses the standalone asset, its local origin metadata, and its technical portability; it does not assess neighboring master-scene geometry.

## Visual review

The exterior reads as a connected brick Catholic center with lower flat-roofed wings, a prominent pitched sanctuary volume, tower/cross, entry, repeated windows, and stone bands. R3's metre-based UV work improves the brick course orientation over R2, and the facade has more consistent material assignments. However, the brick pattern still reads as conspicuous repetitive bands, and the large roofs and roof-to-sanctuary junction remain simplified. The window rhythm and stone trim are clear but uniform.

The sanctuary cutaway includes pews, altar, ambo, cross/choir-like rear feature, brick side piers, and a central aisle. In the current view, the rear arch and several architectural fragments look detached from the seating space, while overhead structure pieces float. The classroom cutaway establishes four rooms and a central stair, but the white box-like partitions and sparse repeated furniture do not yet communicate convincing finished rooms or circulation.

Inspection renders: [north entry](exterior_north_entry_r3.png), [southeast](exterior_southeast_r3.png), [footprint](topdown_footprint_r3.png), [sanctuary](interior_sanctuary_cutaway_r3.png), and [classroom](interior_classroom_cutaway_r3.png). The images are review views, not photorealistic deliverables.

## Scorecard

| Category | Weight | Score | Assessment |
|---|---:|---:|---|
| Identity and plan evidence | 20% | 9.0/10 | GIS and OSM identify the site and closely agree on plan shape; source limits and approximate component division are documented. |
| Massing and architectural silhouette | 20% | 7.6/10 | The pitched sanctuary, cross/tower, and connected additions read clearly; roof transitions and addition forms remain approximate. |
| Facade and architectural detail | 15% | 7.0/10 | Brick, window bays, stone bands, entry sign, and canopy are present, but repetitions and simplified junctions limit likeness. |
| Materials and surface finish | 15% | 7.2/10 | Improved UV orientation and portable material assignments; brick pattern remains overly stripe-like and other finishes are simple. |
| Interior and program | 15% | 6.2/10 | Sanctuary furnishings are legible, but detached/floating fragments undermine it; classroom layout is schematic and sparse. |
| Technical integrity and portability | 10% | 9.0/10 | Fresh reopen is clean, the root is identity, local bounds and campus origin are recorded, and no external dependencies are missing. Master placement is reviewed separately by the coordinator. |
| Evidence and uncertainty | 5% | 9.0/10 | GIS/OSM snapshots, architect/parish references, dates, conversion assumptions, and uncertainty are documented. |
| **Weighted total** | **100%** | **7.7/10** | **Does not pass.** |

## Highest-impact fixes

1. Reconcile the sanctuary cutaway: attach or remove the detached arch and side fragments, and make the overhead structure read as supported and connected.
2. Refine the pitched sanctuary and flat-roof addition transitions against the architect's entry and street-facing photographs.
3. Retune the brick procedural scale and relief so it reads as masonry courses rather than repeated stripes; keep tonal variation subtle.
4. Add evidence-supported classroom finishes and clearer doors/circulation, and enrich the room beyond a few repeated furniture blocks.
5. Recompose the inspection views and lighting so cutaway geometry is easy to interpret and unrelated fragments are not presented as connected fabric.

## References

- [J.W. McQuiston Architecture — St. Thomas Aquinas](https://www.jwmcq.com/st-thomas-aquinas) — project description and photographs of the center, entry, and chapel.
- [St. Thomas Aquinas Catholic Center — Project Renewal](https://www.boilercatholics.org/project-renewal) — parish description of the connected church/addition/classroom components.
- [Purdue BuildingShapesZip4 FID 852](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/852) — map outline; not an as-built survey.
- [OpenStreetMap way 117396617](https://www.openstreetmap.org/way/117396617) — corroborating named outline.

The detailed machine-readable score is in [independent_grade_r3.json](independent_grade_r3.json), and the independent fresh-process Blender record is in [independent_grade_r3_reopen.json](independent_grade_r3_reopen.json).
