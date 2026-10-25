# Independent grade — Purdue Memorial Union

**Result: 7.3 / 10 — does not meet the 8/10 pass threshold.**

Reviewed the saved asset directly after a fresh reopen. Asset SHA-256: `b1afa1dcffd08626c7508153b3c4d3a59cac86d605b6553d7f3477a01d972a25`. The evaluator function and machine-readable result are in `independent_evaluator.py` and `independent_grade.json`. Views are in `oblique.png`, `south.png`, `west.png`, and `top.png`; source/method notes are in `source_evidence.md`.

| Criterion | Score | Independent finding |
|---|---:|---|
| Correct identity and source-backed footprint | 1.7 / 2 | Recognizable PMU tower-and-wings identity; official historical Purdue GIS phase outline aligns the main shell closely. GIS is phase history, not a current survey. |
| Position, orientation, and scale/dimensions | 1.9 / 2 | One expected master placement marker points to the asset at the manifest location with zero rotation and unit scale. Geographic comparison is approximate and historical. |
| Evidence-backed height, floors, and roof form | 1.0 / 2 | Asset is 29.5 m tall with multiple levels and roofs, but no measured height/floor/elevation evidence was present. Roof profiles remain simplified. |
| Facade, entrances, and distinctive architecture | 1.2 / 2 | Central clock tower, wings, brick/stone treatment and Gothic cues are present. Many windows read as rectangular, and the entrance, masonry detail and roof treatment are visibly generic compared with Purdue imagery. |
| Modular export, portability, and complete evidence | 1.5 / 2 | Fresh reopen succeeds; expected collection/root exist, all mesh objects have materials, no external image dependencies. No builder source/evidence package or validation log was supplied before this review. |
| **Total** | **7.3 / 10** | **Below pass** |

## Required work to reach a passing grade

1. Refine the south/front facade using source imagery: make the major openings tall and arched where evidenced, improve the central portal and surrounding limestone/masonry articulation, and vary the facade rhythm so the tower and wings read as the actual PMU rather than repeated generic wall panels.
2. Rework the broad wing roofs and tower transitions against dated photos or another credible roof/elevation source. Use more accurate silhouettes and restrained, source-consistent roof materials; avoid presenting inferred roof details as verified.
3. Add source-backed height and floor evidence (or clearly retain them as estimates). Obtain current elevation/roof imagery or measured documentation before claiming these dimensions are verified.
4. Add a building-specific source/build record and validation log covering the saved library, footprint comparison, dimensions and remaining uncertainty. Preserve raw evidence metadata and a preview.
5. Reopen after changes and rerun an independent grade. Current historic GIS match and marker placement are strengths to preserve; do not rescale the whole library from decorative aggregate bounds.

## Limitations

The supplied historic GIS records represent construction phases (1929, 1935–36, 1938–40, and a 1953–55 club/hotel extension). I excluded the hotel/club polygon from the main PMU asset match. The approximate local coordinate transform and historic map polygons support broad alignment only. They do not validate height, roof profile, facade details, interior layout, or present-day additions. The master marker’s stored `matrix_world` in the read-only data-block snapshot is identity despite its nonzero `location`; this grade relies on its explicit location/rotation/scale fields and does not rely on that matrix field.
