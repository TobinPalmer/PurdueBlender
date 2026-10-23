# Niswonger Aviation Technology Center — batch 4 standalone pass

## Status
Saved-file modeling pass complete; **not scored 9/10 or declared finished**. The closer view confirmed the sloped connector/clerestory roof is in place and renders without a camera clipping through it, but the exterior render still exposes substantial roofless areas over the inherited building shell. The underlying roof coverage appears incomplete; this pass did not invent room-by-room roof elevations or a full roof plan without a reliable current source. Independent reviewer slot is pending root.

## Asset boundary and preservation
- Edited only `modular/buildings/niswonger_aviation_tech.blend` and files in `audit/batch4_niswonger/`.
- Preserved the existing export collection `Asset_niswonger_aviation_tech`, building marker and local root transform: location/rotation `[0,0,0]`, scale `[1,1,1]`.
- Reopened in a fresh Blender 5.2.3 process. Saved asset has 2,298 objects / 2,212 mesh objects; no missing external image paths, no unmaterialed mesh objects, and no review rig objects left in export collection.

## Changes
- Rebuilt the long sloped connector roof as a compact span over the photo-supported clerestory zone. Added end glazing, steel mullions/rails, roof fascia, purlins and repeated rafters. The prior roof's oversized cross-span is corrected. See `exterior.png` and `atrium.png`.
- Added continuous lecture-room desk rows, beveled chair seat/back geometry, recessed light panels, framed screen, and supply/return grille detail. See `classroom_eye.png`.
- Added two generic instructional single-engine aircraft silhouettes and hangar roof framing / lighting. The silhouettes are scaled from published SR20 dimensions as a visual scale reference only; they do not identify aircraft that are actually housed there. See `hangar_eye.png` and `top_cutaway.png`.
- Improved selected roof, tile, desk and lighting materials. The interior inspection images show the changes. Materials remain procedural/basic rather than a photogrammetric material match.

## Geometry checks (fresh reopen)
- The four room rectangles carried over from the earlier plan-based model have zero pairwise overlap area; each rectangle corner is inside the official ground-floor mesh triangles. This validates the existing modeled room set, not a complete current room inventory or a verified egress route.
- Both aircraft mesh footprints were tested vertex by vertex against the official ground-floor triangulation. After moving each model center inward by 2.0 m from the preceding placement, **zero vertices are outside** the floor polygon. Aircraft centers remain 13 m apart; each silhouette has a published 11.7 m wingspan scale.
- The mesh bounds and all validation results are in `reopen_verification.json`.

## References and limits
- [MSKTD project photos and description](https://msktd.com/project/purdue-university-niswonger-aviation-technology/) support the brick base, pale metal fascia, sloped glazed clerestory, steel-framed corridor roof, terracotta-colored panels and reflective terrazzo. The exposed framing and furniture interpretation follow available photos; dimensions not called out in a published drawing are estimates.
- [Purdue 2016 facility manual](https://old.polytechnic.purdue.edu/sites/default/files/files/TCO%20and%20S%26P%20Manual%20Final%20Copy.pdf) supplied the historical plan used for the four existing room rectangles. Room placement is estimated to roughly ±1.5 m; the manual is not a current as-built or current room inventory.
- [Purdue Alumnus Hangar One article](https://www.purduealumnus.org/a-day-at-the-airport/features/) supports the presence of instructional aircraft at the facility, but not the illustrated aircraft types or exact parking arrangement.
- [Cirrus SR20 dimensions sheet](https://cirrusaircraft.com/wp-content/uploads/2024/01/NorthAmerica_SR20_PriceList_2026.pdf) provides only a scale reference for generic silhouettes.
- [Purdue Events building listing](https://events.purdue.edu/niswonger_aviation_technology_building) corroborates building identity and address.
- Google Maps was attempted at [the building search](https://www.google.com/maps/search/Niswonger+Aviation+Technology+Building+Purdue+University), but this subagent's embedded browser could not render Google Maps (subagent browser visibility unsupported). No map imagery or Street View verification is claimed. No image capture date was available for the cited architect photos.

## Remaining work before a 9/10 claim
1. Verify roof plan, roof heights and coverage from an authoritative current plan or direct map/photo review, then close the exposed shell without obscuring the clerestory or hangar openings.
2. Verify current room/corridor inventory, egress, stairs and elevator; the existing room-footprint test cannot certify these.
3. Revisit final material response and exterior camera after roof completion. The current exterior composition exposes missing roof coverage, so the asset remains below the requested bar.

## Review images
- `exterior.png` — full shell and roof coverage inspection.
- `atrium.png` — sloped roof underside, steel framing, clerestory and lights.
- `classroom_eye.png` — seating, continuous desks, lights, screen and grilles.
- `hangar_eye.png` — generic aircraft and hangar interior.
- `top_cutaway.png` — interior placement overview.
