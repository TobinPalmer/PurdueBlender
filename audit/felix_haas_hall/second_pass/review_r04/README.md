# Independent Haas r04 exterior review

**7.95/10; not accepted.** The unchanged default threshold is 9.9. Preview approval was not a numerical waiver. The evaluator uses unrounded decimal arithmetic and individual evidence-based deductions. All seven applicable gates are separate from the score. Master integration is not reviewed or scored.

Reviewed asset: `../detail_color_r04/candidate.blend`.
SHA-256: `7c608ff383548bfb2159fba7734d4cf461813f06ab024117a7d3201d4ba045fb`.

| Criterion | Award | Maximum |
|---|---:|---:|
| Windows/openings | 2.40 | 3.0 |
| Signature architecture | 1.95 | 2.5 |
| Proportions/roof/silhouette | 1.75 | 2.0 |
| Materials/color/depth | 1.15 | 1.5 |
| Whole-building consistency | 0.70 | 1.0 |
| Total | **7.95** | **10** |

The total is calculated by `evaluate.py` in `evaluation.json`. No points were given for interiors, polygon counts or GIS footprint alone.

The front three six-light upper groups, two lower arches, recessed oak door, lanterns and quoined stone piers are recognizable. The west nine-bay rhythm and change from triple upper lights at the north/door end to paired lights farther south are supported by the real photographs. The saved model now has a substantial source-backed exterior, while its close details and unseen faces prevent acceptance.

Concrete remaining corrections are the squat west basement openings beside the rear door, shallow rear transom, omitted rear approach step run, front handrail arrangement, blank front frieze/relief proxies, simplified linked upper-window/cornice moldings, and roof surface reading as a masonry grid rather than horizontal overlapping tile courses. Exact camera matching and detail photography are needed before changing uncertain fine features. See per-finding source citations and model views in `evaluation.json`.

Coverage remains incomplete for the south, pavilion returns, east wings and concealed north openings. The elevated 2016 west photograph supports the broad roof shape but is not a complete roof/aerial source. Small roof penetrations visible then are unverified for 2026. Colors are qualitative estimates because photographic white balance/exposure is uncalibrated. `viewpoint_coverage.json` logs camera position, height/distance limits, perspective, dates, repeated-panorama groups and missing views; additional sources were requested from the coordinator.

Independent verification opened the exact file using background Blender 5.2.3, inspected collection/transforms/dependencies and generated four additional perspective views without saving or touching the GUI. All 22 supplied daylight/standard images and all 15 saved real source images were directly inspected, followed by those four new views. Source/render matching is approximate; supplied cameras are orthographic, and their obliques sit 38 m above model ground. `additional_view_settings.json` records the independent cameras.

Pass: correct identity, saved-file reopen, expected export collection, portable dependencies, and no regression to verified structural-wall XY extent/orientation/scale. Fail: adequate exterior-reference coverage, no unresolved material exterior discrepancies. Separate: master integration unevaluated.

Reproduce the score with `python audit/felix_haas_hall/second_pass/review_r04/evaluate.py` from the repository. `independent_saved_inspection.json` contains the reopened saved-file inventory; `inspect_and_render.py` documents how those checks and the four new views were made. No previous evaluator was opened or reused. The historical score mentioned in the revision README was disregarded while judging the current revision.

The coordinator subsequently redirected work to research only. Rendering had already finished before that instruction arrived. No further views or asset changes were made. These findings preserve this reviewed historical revision; the building's second pass remains incomplete.
