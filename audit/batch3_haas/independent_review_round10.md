# Felix Haas Hall — independent review round 10

**Reviewed:** saved `modular/buildings/felix_haas_hall.blend` via the round-ten reopen record and saved exterior, entrance, interior, and four elevation renders. I compared the renders with Purdue's preserved exterior photograph and the official first-floor plan. I made no model, master, or script edits.

## Score: 7.4/10 — below 9/10

Round ten does remove the named north/west belt-course objects from the export and increases the depth/width of the east facade inlay bars. The saved file reopens, the GIS shell bounds are unchanged, and the 17 entrance treads remain. The roof material now has metric UV mapping and no broad triangular color breaks. In the actual render, though, the roof reads as a nearly featureless black-brown slab: the tile pattern is not legible at building scale, and the roof is far darker than the red clay roof in Purdue's photo. The model still misses major visual cues in that photo, especially the large arched front openings and deeply modeled stone portal. The interior remains a useful labeled first-floor diagram, not a convincing interior model. The 9/10 bar is not met.

| Area | Score | Findings |
|---|---:|---|
| Massing and GIS envelope | 8/10 | Reopen check reports the unchanged wall envelope `[-26.2203, -25.9795, 0]` to `[12.9812, 26.7597, 11.5]` m, and the roof meshes preserve unit scale and zero rotation. Basic plan footprint and major wing massing read clearly. Roof profile and height (~14 m) remain estimates; the roof edge projects beyond the shell and appears unusually broad/flat in the overview. This check confirms continuity, not architectural accuracy. |
| East/front facade | 6.8/10 | The paired brick/stone fields are clearer at close range, but the 26 and 18 relief groups still read as rectangular graphic trim around flat pale panels, not integrated masonry. The reference photo shows large arched lower windows with substantial stone surrounds, a pronounced arched central portal, and stronger floor/bay hierarchy. Those signature forms are absent or rendered as small rectangular openings. Entrance composition and fenestration therefore diverge from the primary reference. Exact dimensions remain unverified. |
| Side elevations | 7/10 | The four elevations are cleaner after removing unsupported overlays, but remain sparse and heavily planar. The west elevation shows a blank brick expanse with a short row of low windows; the north view retains a pale projecting line at the roof edge. No source supports adding a speculative side window schedule, so the sparse treatment is preferable to invented windows, but the residual line needs object-level identification. |
| Roof and materials | 6.5/10 | Large facet shading has been evened, but the output is too dark to read as the photo's red-clay tile roof. At overview scale, the tile pattern disappears and the roof reads as a single flat dark plane. A bright thin edge line remains on the roof perimeter and reads detached in the orthographic views. The procedural material settings alone do not demonstrate visual success; compare in neutral lighting and tune until tile relief/color is visible without faceting. |
| Entry and stairs | 8/10 | Seventeen treads remain and form a coherent approach to the centered door. Count has historical support, while rise, run, and accessibility are not established. The reference entry has a much taller/deeper stone arch and flanking architectural details than this simplified rectangular door bay. |
| Interior and texture | 6.5/10 | The plan view has partitions, labeled rooms, desks, stairs, and lift, and explicitly warns that sizes and openings are schematic. It is an understandable adjacency visualization based on a nondimensional plan, but has no convincing room volumes, finish/material variation, circulation detail, or verified door/vertical connections. Texture work is mostly exterior; the interior is not yet a detailed textured interior. |
| File integrity and evidence | 9/10 | The reopen record says the saved file loaded with 879 direct export objects, unchanged GIS bounds, both roof objects at unit scale/zero rotation, all 17 treads, and no side estimate overlays. The evidence clearly identifies the unresolved pale line, roof darkness, and plan limitations. These checks do not independently establish modeled-building fidelity. |

## Priority fixes

1. Rebuild the visible east/front facade around the photo-supported forms: the large arched lower openings, deep arched central entrance surround, stone piers/lintels, and more legible floor/bay hierarchy. Keep unmeasured extents and relief depths marked as estimates.
2. Tune the roof against the saved Purdue exterior reference under neutral lighting. Raise the red/brown value and ensure tile courses are visible from the overview render; inspect roof normals/material assignment and the bright perimeter edge line. Do not infer a precise roof profile from this one perspective photo.
3. Identify the remaining pale north roof-edge projection by object name and determine whether it is supported eave trim or a stray belt-course. Remove unsupported geometry or integrate supported trim cleanly; rerender the north elevation.
4. Improve the brick inlays as shallow masonry panels with coherent boundaries, returns and restrained coursing, rather than adding more isolated bars. Do not make unsupported exact claims about brick panel extents.
5. If a verified interior remains unavailable, retain the clear schematic label. For the requested interior quality, add readable wall thickness, door openings only where the plan supports them, stronger room/floor material differentiation, and coherent circulation/vertical connections without presenting the nondimensional plan as metric.

## Evidence and limits

- Purdue's [Felix Haas Hall page](https://events.purdue.edu/felix_haas_hall) provides the official building image; the preserved local `audit/batch3_haas/exterior_reference.jpg` makes the arched facade and red roof directly comparable. This perspective does not establish dimensions or unseen elevations.
- Purdue CS's [HAAS first-floor plan](https://www.cs.purdue.edu/resources/docs/HAAS_first.pdf) supports room names and broad adjacency only. It does not verify room dimensions, door positions/swings, metric registration, or upper stories.
- Purdue's historical timeline supports the 17-step entrance count, not tread dimensions.
- The GIS shell bounds support plan envelope and location only, not facade, height, roof, or interior accuracy.

**9/10 decision: No.** File integrity and the evidence trail are strong, but the signature front architecture, roof appearance, and textured interior still require substantial work.
