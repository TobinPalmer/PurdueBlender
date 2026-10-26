# Independent grade: St. Thomas Aquinas R2

**Asset:** `modular/buildings/massing_st_thomas_aquinas_5535390.blend`  
**Exact SHA-256:** `9fea60330e434dc184d19c3397187c1171a47cbce23e624dbf39ca944a85b94a`  
**Result: 7.3/10 — below the 8.0 acceptance threshold.**  
**Review date:** 2026-10-25  
**Blender:** 5.2.3 LTS

## Exact-file reopen and scope

I opened the saved asset in a fresh Blender 5.2.3 process and independently recalculated its SHA before inspection. It matches the requested R2 hash. The exported collection has 922 objects (920 meshes, one empty, and one text object), an identity root, no materialless meshes, no invalid material indices, no missing external images, and no linked libraries. Its evaluated bounds are about 43.5 x 70.9 x 20.1 m in local coordinates. The independent integrity record is in [independent_grade_r2_reopen.json](independent_grade_r2_reopen.json); the reopen script and Blender log are alongside it.

This is a standalone-asset grade. I did not open or change the campus master.

## Identity and plan evidence

The source identification is strong. The saved GIS feature is FID 852, named St. Thomas Aquinas Center, and the saved OSM way 117396617 is named St. Thomas Aquinas. The projected GIS polygon is 2,173.6 m², with bounds X 1.59–44.42 m and Y −445.87 to −380.63 m in Purdue's approximate local projection. GIS and OSM plan outlines have IoU 0.922. The asset's plinth and continuous wall shell are generated from the GIS ring. That is a close match to the map outline by construction, not an independent measurement of the as-built wall line; the source is not a survey.

The parish describes three connected components: the original church, new church addition, and office/classroom addition. The model makes those broad massing zones legible. Their exact boundaries, heights, and roof pitches are not verified. See the [projected footprint evidence](projected_footprint_evidence.json).

## Visual and program review

The north-entry and southeast renders read as a brick Catholic center with a gabled sanctuary, a taller bell tower and cross, connected lower wings, a sign, stone trim, windows, and an accessible entry. These are useful improvements over the single massing block. The broad roof hierarchy and the sign/tower combination match the available public descriptions and photographs at a recognizable level.

Several elements remain schematic. The long additions are mostly flat-roofed blocks with repeated narrow openings, and the main roof has repetitive ribs/edges that read as graphic lines. The tower, nave roof, parapets, and connections between the three components need more specific forms from the architect's exterior and entry photographs. Brick surfaces show repeated vertical bands and have limited tonal/depth variation; glazing, stone, and roof materials look flat in the inspection renders. The model has 24 distinct material names, but material count alone does not establish a convincing textured finish.

The sanctuary cutaway contains pews, a raised altar, ambo, cross, baptismal font, and ceiling trusses. Its columns and overhead lines read as a sparse schematic and do not make a verified structural arrangement clear. The classroom cutaway contains a few tables, chairs, and bookcases but leaves the space largely empty; partitions, doors, circulation, and actual room arrangement are unverified. The model correctly labels the interior as schematic, but the current images do not yet communicate a fully resolved interior.

Inspection views: [north entry](exterior_north_entry_r2.png), [southeast](exterior_southeast_r2.png), [plan](topdown_footprint_r2.png), [sanctuary](interior_sanctuary_cutaway_r2.png), and [classroom](interior_classroom_cutaway_r2.png).

## Scorecard

| Category | Weight | Score | Assessment |
|---|---:|---:|---|
| Identity and plan evidence | 20% | 9.0/10 | FID 852 and OSM way 117396617 agree closely. The shell follows GIS by construction; the map outline is not surveyed wall evidence. |
| Massing and architectural silhouette | 20% | 7.5/10 | Three connected zones, nave gable, and tower are recognizable; addition forms and roof relationships remain approximate. |
| Facade and architectural detail | 15% | 6.7/10 | Sign, brick, trim, windows, and entry are present, but repeated bays and simplified junctions lack photo-level detail. |
| Materials and surface finish | 15% | 6.7/10 | Distinct portable materials are assigned; brick banding, flat shading, and simplified glass/roof finish reduce fidelity. |
| Interior and program | 15% | 6.3/10 | Sanctuary furnishings are readable; classroom furnishings are sparse and structural/circulation logic is not established. |
| Technical integrity and integration readiness | 10% | 5.5/10 | Fresh reopen is clean, but this local-coordinate asset is still indexed as `kind: massing` with no manifest origin. A direct massing link would place it at the campus origin. |
| Evidence and uncertainty | 5% | 9.0/10 | GIS/OSM snapshots, official architect/parish sources, retrieval date, conversion, and limits are recorded. |
| **Weighted total** | **100%** | **7.3/10** | **Does not pass.** |

## R3 priorities

1. Resolve the coordinate-frame mismatch before integration. The manifest still lists this file as `kind: massing` with no `placement_origin_xy_m`, while the asset geometry is local (about X −20.2 to 23.3 m, Y −33.8 to 37.0 m) and the campus origin is stored only as an object custom property: `(21.328237, −412.214145) m`. Under the project rules, a massing asset is linked directly in campus coordinates. Either the coordinator must convert it to a detailed-library placement with a master marker, or the asset must be reauthored in campus coordinates. Do not integrate it as-is.
2. Compare the gabled sanctuary, bell tower, narthex, and additions with the architect's 46th Street and narthex photographs; refine roof edges and the three-component transitions. Roof heights and pitches remain estimates without registered elevations.
3. Improve the brick/roof/stone material response and lighting so the surfaces have depth without repeated stripe artifacts.
4. Rework the sanctuary and classroom review views so columns, roof framing, seating, partitions, and circulation have clear relationships. Add no unsupported exact room-plan claims.
5. Reopen and independently grade the next exact SHA; keep the building unfinished until a new score reaches 8.0/10 and placement is checked in the master.

## Sources reviewed

- [J.W. McQuiston Architecture — St. Thomas Aquinas](https://www.jwmcq.com/st-thomas-aquinas) — architect project description and photographs labeled “View from 46th St.,” “Narthex entry,” and “Chapel exterior.” The page dates the design to 2001 and says it connected the church, school, and parish-center buildings while respecting Evans Woollen's 1965 sanctuary.
- [St. Thomas Aquinas Catholic Center — Project Renewal](https://www.boilercatholics.org/project-renewal) — parish description of the three connected buildings and recent access/ramp work.
- [Purdue BuildingShapesZip4 FID 852](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/852) — campus map outline; retrieved 2026-10-25. Source CRS EPSG:3857; queried geometry EPSG:4326; transformed with the project's approximate local conversion, not a survey CRS.
- [OpenStreetMap way 117396617](https://www.openstreetmap.org/way/117396617) — named building outline used as a corroborating plan source.
- [Parish accessibility and facilities updates](https://www.boilercatholics.org/project-renewal) — 2026 ramp/confessional work; current entry accessibility details may differ from the earlier design photographs.

The renders are inspection images, not photorealistic final outputs. Exact heights, interior partitions/furnishings, component boundaries, and roof dimensions remain unverified.
