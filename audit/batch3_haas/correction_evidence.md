# Felix Haas Hall — round ten evidence

Updated 2026-10-23. Source asset: `modular/buildings/felix_haas_hall.blend`; export collection: `Asset_felix_haas_hall`. Independent round-nine review scored 7.8/10. Round ten is ready for review; no new rating is claimed.

## Round-ten changes and checks

- Expanded existing east-facade brick inlay relief bars: 26 prism groups in the main field and 18 in the wing (156 and 108 faces respectively). This improves relief/readability but still does not establish exact masonry coursing or depth.
- Archived the two named north/west beltcourse projection candidates outside the export collection and render-hidden them. A pale line remains visible at the north elevation end; its generating object/source is not resolved, so the artifact is still open.
- Rebuilt the roof material with per-face metric UV coordinates and a procedural red-clay tile pattern on both roof objects. The estimated tile repeat is 0.62 × 0.25 m. Latest exterior render shows much less broad facet color variation, but the roof is very dark compared with the local exterior reference; final color/brightness remains unresolved and should be judged in independent review. Roof profile and top height (~14 m) are estimates.
- Reopened the saved asset in Blender 5.2.3. `Asset_felix_haas_hall` contains 879 direct objects. GIS wall envelope remains `[−26.2203, −25.9795, 0]` to `[12.9812, 26.7597, 11.5]` m; all 17 documented entrance treads remain present. Both roof objects remain unit scale/zero rotation. See `reopen_check_round10.json`.
- Rendered updated `exterior_final.png`, `entrance_final.png`, `interior_plan_final.png`, and all four `elevation_*.png` views from the saved source. The exterior and interior remain schematic, not a dimensionally verified survey model.

## Evidence and limits

- [Felix Haas Hall](https://events.purdue.edu/felix_haas_hall) and the preserved local `exterior_reference.jpg` support qualitative pale limestone/red-brick facade language, the entrance, arched lower windows, and red roof. Perspective photography does not establish exact wing boundaries, side elevations, roof profile, or dimensions.
- [HAAS Hall — First Floor](https://www.cs.purdue.edu/resources/docs/HAAS_first.pdf) supports room names and broad adjacency only. It is nondimensional and does not verify room dimensions, metric registration, door positions/swings, or upper floors. Interior dimensions and placement are estimates; treat the cutaway as an adjacency visualization.
- [Purdue University Historical Timeline](https://collections.lib.purdue.edu/timelines/puhistorical) supports the 17-step entrance count, not tread dimensions.
- GIS supports plan envelope and campus placement only, not building heights, roof pitch, side window schedule, facade details, or interior dimensions. Roof bounds extend slightly past the wall envelope as eaves; the GIS wall-shell bounds themselves are unchanged.

The master Blend, manifest, `BUILDINGS.md`, and campus marker were not edited.
