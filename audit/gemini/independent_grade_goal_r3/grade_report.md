# Independent Grade — Gemini Cooperative (FID 825)

**Score: 8.15/10 — meets threshold.**

| Criterion | Score | Assessment |
|---|---:|---|
| Identity and official footprint | 2.00/2.00 | The FID 825 source record names Gemini and the reopened lower-floor slab reproduces all 14 official GIS XY vertices within rounding precision. This confirms plan outline only, not elevation or walls above the slab. |
| Scale and placement | 1.25/1.50 | The 14-vertex footprint, local metric geometry, and overall plan proportions are consistent. Wall/story and roof elevations are image-based estimates, and the standalone asset does not include the master placement marker, so campus placement and surveyed vertical scale are not established here. |
| Roof form and height evidence | 1.45/2.00 | Three separately named roof ranges, two cross-gables, three pitched dormers, and chimneys create a more articulated profile. The current official photo still shows deeper, more legible intersecting gable wings; in the model several roof planes merge into broad shallow bands and the gable/valley relationships are not fully convincing. Roof and chimney elevations remain estimates. |
| Facade, raised entry, and materials | 1.55/2.00 | Brick base, pale lap siding, contrasting sash, multiple window rhythms, porch piers, a raised landing, broad stairs, and guardrails address the main photo cues. The entry is clearly elevated and legible. Its porch roof and facade remain schematic compared with the official photo's deep recessed central porch, broad continuous porch railing, and more distinct wing projections; openings are still somewhat regular. |
| Interior and portability | 1.90/2.50 | The fresh-open asset contains a schematic interior rather than an authoritative plan, so room arrangement remains unverified. Portability is strong: all mesh objects have material slots, and no linked libraries or unpacked external image dependencies were found. Geometry is a self-contained standalone collection. |

Asset SHA-256 was `035cadd549309370dd2fdf67791bbb0e2919132e797a3dcc74819e00a897dff6` before, immediately after fresh open, and after evaluation. Blender 5.2.3 LTS opened the exact requested standalone blend. The target file was not saved.

## Evidence and limits

The official Purdue GIS feature FID 825 is named Gemini at 172 Littleton Street. Its EPSG:4326 polygon was transformed with the project's documented approximate local conversion and compared vertex-by-vertex with the reopened slab. This establishes horizontal outline agreement only; it does not establish floor elevations, above-grade wall positions, or master placement.

The current official [Gemini home page](https://www.geminicooperative.com/) still presents an Our Gallery section and identifies 172 Littleton Street; the [official About page](https://www.geminicooperative.com/about) confirms the organization and address. Architectural comparison used the official exterior snapshot `audit/gemini/official_home_exterior.jpg` (Wix image URL and retrieval date recorded in `result.json`). The photo provides no calibrated dimensions.

The interior is schematic. GIS level-count attributes conflict with the visible multi-level photo and are not treated as measured evidence. Roof/story heights remain estimates. Portability results are from the fresh-open scene.

## Required revisions

No threshold-driven revision list: the asset meets the 8/10 threshold, with the limits above retained in the record.

Runnable evaluator: `evaluator.py`. Machine-readable measurements and criterion evidence: `result.json`.
