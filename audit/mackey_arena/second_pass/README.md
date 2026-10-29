# Mackey Arena — second-pass exterior record

Stable ID `mackey_arena` · asset `modular/buildings/mackey_arena.blend` · collection `Asset_mackey_arena` · root `AssetRoot_mackey_arena` · local frame preserved (placement origin `(-209.590, 671.837)` m unchanged). Rank 1 of Rossen's second-pass batch 1–30.

Builder: [`modular/buildings/build_mackey_arena_second_pass.py`](../../../modular/buildings/build_mackey_arena_second_pass.py) (idempotent; run headless on the saved library). The older `build_mackey_arena_north_wing.py` is first-pass history and is superseded for the exterior.

## Files

| Path | Content |
| --- | --- |
| `sources/` | Saved reference photos, aerial export (+ grid + transform JSON), WJE roof profile, Commons metadata, colour samples |
| `reference_index.json` | Every source: URL, provider/author, licence, image date, retrieval date, view direction, features, uncertainty, SHA-256 |
| `coverage_matrix.md` | Facade-by-facade evidence coverage (observed / estimated / conflicting / unseen) |
| `discrepancy_checklist.md` | Baseline (r0) vs. reference discrepancies identified before editing, with r1 disposition |
| `change_log.md` | Revision history, dimensions/estimates, colour calibration |
| `baseline/` | r0 (first-pass asset, SHA `b8d5c120…`) rendered with the same cameras/lights |
| `r1/` | r1 review renders, render settings, close-up camera list, reopen validation |
| `comparisons_r1/` | Reference / before / after strips at matched viewpoints |
| `review_rNN/` | Independent reviewer outputs (written only by the reviewer) |
| `review_render.py`, `validate_reopen.py`, `compare.py` | Render, validation and comparison tools used |

## Revision status

| Rev | Asset SHA-256 | Independent score | Review |
| --- | --- | --- | --- |
| r0 (first pass) | `b8d5c120004b189892a48a1bdae8b018e1ca190206f1ce0feaa573b435784e44` | — (first-pass 8.0, other rubric) | `../INDEPENDENT_REVIEW_round3.md` |
| r1 | see `r1/validation_r1.json` | pending | `review_r01/` |
