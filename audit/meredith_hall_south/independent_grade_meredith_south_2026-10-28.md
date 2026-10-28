# Independent review — Meredith Hall South

- **Result:** 6.45/10 — **does not pass** the requested 8.0/10 bar.
- **Reviewed asset:** `modular/buildings/massing_meredith_hall_south_ffbc444.blend`
- **SHA-256:** `FDE6897067E878BB48E0BCDB42E828070E958426937E5F558DD76D2E595C7A70`
- **Review date:** 2026-10-28
- **Method:** Read-only fresh open in Blender 5.2.3, visual inspection of the supplied oblique preview and the official Purdue photo embedded in the saved accommodations page, plus direct inspection of Purdue GIS FID 410, the current Purdue emergency plan, and architect/project sources. The asset hash matched before and after review.

## Score

| Criterion | Weight | Score | Weighted points |
| --- | ---: | ---: | ---: |
| Identity and provenance | 20% | 9.5/10 | 1.90 |
| Plan geometry and placement | 25% | 9.0/10 | 2.25 |
| Exterior silhouette and openings | 25% | 4.0/10 | 1.00 |
| Materials and facade | 10% | 5.5/10 | 0.55 |
| Interior / cutaway | 10% | 0.5/10 | 0.05 |
| Presentation and technical quality | 10% | 7.0/10 | 0.70 |
| **Total** | **100%** |  | **6.45/10** |

## Findings

FID 410 is a strong identity match: the official Purdue BuildingShapes snapshot names the feature “Virginia C. Meredith Residence Hall South,” gives abbreviation MRDS and address 1225 1st Street. The saved check reports a 0.000022 m maximum discrepancy between transformed GIS and shell axis-aligned bounds. That verifies the bounds closely, but I did not independently compare every polygon edge or inspect the master placement. The campus coordinate transform is an approximation, not survey control.

The strongest issue is the exterior model’s six-band, near-uniform treatment. Purdue’s emergency plan (revision 2026-10-16) states the west A section has eight floors, while middle B and east C have six floors. The preview does not show that height transition. The official Purdue photo shows large multi-story glazed vertical bays and a glazed ground-floor base. Mackey Mitchell’s project page describes “ample glass” at ground level and dining venues at the east end. The current preview shows repeated small punched windows to grade; the distinguishing glazed volumes and retail base are missing or too weakly represented.

The current brick reads pale pink in the supplied render compared with the dark red-brown brick in the Purdue photo. Materials exist, but their color and facade composition are not yet convincing. No interior or cutaway appears in the reopened asset.

The asset reopens and contains the expected 8-object collection. BMesh reports open boundaries on the wall shell (120 edges), parapet (120), and roof slab (30). These could be intentional surface-shell construction; they matter if the asset is expected to behave as a closed solid or support cutaways. Referenced image paths are relative and resolve from the project root, but image loading/use was not verified.

## Sources inspected

- Purdue BuildingShapes FID 410 snapshot: `audit/official_purdue_buildings_wgs84.json` (feature name, address, polygon; positional accuracy unpublished).
- Purdue Office of Emergency Preparedness, [Meredith South BEP](https://www.purdue.edu/operations/emergency-preparedness/mrds/) (A/B/C sections, 8/6/6 floors, east retail; revised 2026-10-16).
- Mackey Mitchell Architects, [Meredith South project](https://www.mackeymitchell.com/projects/meredith-residence-hall-south/) (ground-floor glass, east-end dining, project size).
- MSKTD, [Meredith South project](https://msktd.com/project/purdue-university-meredith-south-residence-hall/) (ground-floor glass and program).
- Corvias image URL supplied by the coordinator: [Purdue Meredith exterior night photo](https://www.corvias.com/sites/default/files/2023-06/Purdue_Meredith_Exterior_Night_27-1500x1055-68ce50f.jpg). The coordinator identified it as the same image embedded in the Purdue page; direct fetch timed out, so I treated it only as qualitative corroboration and did not independently verify Corvias-host metadata.
- Purdue Residences, [conference accommodations](https://housing.purdue.edu/visit/conferences/accommodations.html), local snapshot `audit/meredith_hall/sources/purdue_conference_accommodations.html` (embedded photo labeled “MEREDITH SOUTH RESIDENCE HALL – MSKTD”; photo date not stated).

A coordinator-supplied Corvias image URL was reported to be the same photo; direct fetch timed out, and I did not independently verify that host attribution. Only the official Purdue-embedded oblique image was directly viewed for comparison; other elevations, exact window counts, roof configuration, and interior are unverified. This is not a master integration review.

The machine-readable criterion breakdown and gate results are in [`independent_grade_meredith_south_2026-10-28.json`](independent_grade_meredith_south_2026-10-28.json).
