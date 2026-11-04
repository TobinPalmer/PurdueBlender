# Mechanical Engineering exterior upgrade

User direction November 3, 2026: upgrade the most-needed buildings with separate independent evaluation agents and continue toward 9.5/10. Rank 2 Mechanical Engineering is the first active asset; WALC remains user-handled. Campus master ownership and placement remain unchanged.

The baseline independently scored **2.45/10** on the second-pass exterior rubric. It had a uniform 18.5 m flat extrusion, repeated small windows, a roof orthophoto used as appearance, and one generic portal mislabeled Gatewood. Its inherited first-pass grade does not measure whole-building exterior fidelity.

| Round | Exact saved asset SHA-256 | Independent score | State / review |
| --- | --- | ---: | --- |
| Baseline | `06dd926bcd5c71edcb54a9f7a2073f88048b31664e7e423b9b64bcfed54d561b` | 2.45 | [Rejected baseline](review_baseline_2026-11-03/result.json) |
| r01 | `5249198727edf3220ffc791233a2bfd2c58a40f78853feacc3513260e3277272` | 3.05 | [Unaccepted checkpoint](review_r01_2026-11-03/result.json); committed/pushed `7dcc0dc5` |

| r02 | `e8439df6be091ad681ee535df571e692758734c0f6e50d8cfba9bda6ba569bc9` | 2.80 | [Rejected for regressions](review_r02_2026-11-03/result.json); material/UV and low-wing junction repairs required |

r01 changed the 1932 historic bar from a flat roof to a photo/point-data-constrained hipped red perimeter and raised flat centre, with estimated 15.8 m eave / 18.9 m high seam. It corrected the portal identity and added layered arch stonework, gridded fanlight and name-panel geometry. Its review found remaining roof-cap deformation and obstructed fanlight, in addition to major unchanged wings and facade schedules. The r01 model is a partial revision, not an accepted exterior.

[Baseline and r01 review renders](review_r01_2026-11-03/source_comparisons.jpg) show the saved assets under consistent cameras. The dedicated builder and its retained baseline input can reproduce the bounded revision. [LiDAR support](source_analysis/README.md) records units, transformed point data and height limitations. [New dated photo evidence](additional_sources_2026-11-03/README.md) distinguishes current historic-entry shots from duplicated exposures and unseen faces. The official [Faculty Onboarding image](source_analysis/purdue_onboarding_gatewood.jpg), with [provenance](source_analysis/onboarding_source_index.json), adds clear Gatewood row and historic-junction detail but has unknown capture date.

Acceptance remains false until the independent score reaches the user-approved 9.5 target and all applicable gates pass. Needed work includes distinct wing heights/roofs, current source-backed opening schedules, complete portals and profiles, material/UV consistency, exposed junctions and concealed-face evidence. Separate saved-file reviews retain all failures; no inherited score, mesh count or missing view establishes fidelity.
