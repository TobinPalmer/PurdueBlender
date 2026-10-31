# Current user-directed rework — October31,2026

The user reopened Haas for front brick/stone and detail corrections. [Front r05](front_r05/README.md) replaces the broad brick-panel composition and includes source-led portal/window/rail/roof work. Its independent review is separate. The older r04 review scored7.95/10, below9.9. The historical notes below are retained; they do not describe the newest candidate or establish acceptance.

---

# Felix Haas Hall — exterior second pass

Rank 61 in Rossen's assigned queue. Stable ID `felix_haas_hall`; source `modular/buildings/felix_haas_hall.blend`; collection `Asset_felix_haas_hall`. The manifest origin `[-214.84998321533203, -64.0199966430664]` and local coordinate frame are preserved. No campus master edits are part of this work.

**Current state: [detail and color revision r04](detail_color_r04/README.md), opened in Blender for the user's inspection before independent review.** The exterior is newly built from official footprint data and real photographs. r04 refines front lighting fixtures, portal, relief borders, windows and stairs; rear service features; and brick/stone/roof/frame/door colors using the supplied photo and additional north, west and southwest street views. No current visual grade or second-pass completion is claimed. The first-pass 8.4/10 is historical; the second-pass target remains 9.9/10.

r01 independently scored 5.2/10. r02 review was interrupted without a final score. r03 was opened for the user, who requested the additional detail/color work now represented by r04. Neither r03 nor r04 has been independently graded. The current facade coverage, limitations, source links and discrepancy checklist are in the r04 record. The older r01-focused coverage and revision notes below are historical, not current claims about r04.

## Exact starting state

- Git LFS starting SHA-256: `0de3417c6cc3af247b2100242720d39871bc8ed188dcf06bfbb96d9bead2c067`, 753,200 bytes. Download verified against the pointer before opening.
- Original source collection: 919 objects; no linked image dependencies. Detailed baseline is in `baseline_inspection.json`.
- Fresh baseline renders: `baseline/renders/`; lighting/cameras are recorded in `baseline/render_settings.json` and shared with revision renders. The renderer does not save the source library.

## Reference index

All new sources were retrieved or observed on 2026-10-28. Ground photographs have no surveyed CRS or scale. Image-based dimensions and colors remain estimates; panorama coordinates establish a viewing location, not surveyed building dimensions. Keep source credits and copyright overlays on screenshots.

| ID / local snapshot | Provider and source | Observed date / feature | Limits |
| --- | --- | --- | --- |
| `purdue_events_front.jpg`, `purdue_events.html` | [Purdue Events](https://events.purdue.edu/felix_haas_hall) | Official place identity and front oblique, arched windows and doorway, stair and pale stone/brick pattern; actual capture date unknown | Small image, perspective, incomplete facade coverage |
| `haas_hall_today_2017.jpg`, `purdue_libraries_2017.html` | [Purdue Libraries article](https://blogs.lib.purdue.edu/news/2017/10/08/from-the-archives-student-recreation/) | Article 2017-10-08; contemporary front image and historical identity | Trees obscure much of the facade; capture date not supplied |
| `maps_front_mike_a_2016.png` | [Google Maps Felix Haas gallery](https://www.google.com/maps/place/Felix+Haas+Hall/) — Mike A | UI says Photo Jul 2016; image capture Mar 2016. East/front elevation, roof, entrance | Obscured by bare branches; publication and capture labels differ and are retained |
| `maps_side_jay_discovery_2016.png` | Same gallery — Jay’ Discovery, photo ID `CIHM0ogKEICAgIC4nbeRuAE` | May 2016. Elevated west facade, roof pitch, grouped upper windows, narrow middle windows, basement and double-door bay | Perspective; corners partly cropped; count and dimensions require independent checking |
| `maps_corner_mike_a_2015.png` | Same gallery — Mike A, photo ID `CIHM0ogKEICAgICEwJT3xAE` | UI publication Jul 2016; capture Jan 2015. Southeast/front corner and partial south elevation | Distant, tree-obscured; not a complete south elevation |
| `streetview_university_entry_apr2026.png`, `streetview_west_upper_apr2026.png` | [Google Street View panorama](https://www.google.com/maps/@?api=1&map_action=pano&pano=F4m7ya0MXAz0LkjEAIJB5g&heading=87.23), Google | Apr 2026; view position 40.4269451, -86.9166441, heading approximately 87 degrees. West doorway, dark frames, narrow middle windows, projecting sills, stepped upper stone surrounds and keystones | Wide-angle perspective; upper/lower details are separate views of the same panorama, not independent photographs |

Machine-readable download URLs, snapshots, hashes, and failures are in `sources/reference_index.json`. Corbin Design's project page and image returned 403 to snapshot requests; browser/web evidence supports its existence, but no missing snapshot was fabricated or used to claim a measurement. Purdue Archives identifies this as the former Memorial Gymnasium; the archive snapshot request also returned 403. Prior roof/footprint evidence remains in `audit/batch3_haas/`.

## Facade coverage matrix and discrepancy checklist

| Area | Coverage | Baseline discrepancy | Current treatment / remaining work |
| --- | --- | --- | --- |
| East / principal entrance | Several Purdue and gallery views; trees obscure parts | Simplified window divisions, broad pale panels, approximate arches, missing inscription/detail fidelity | Unchanged in revision 1; detailed source-to-model comparison still required |
| West / University Street | Elevated 2016 image plus close 2026 panorama | Only five low window proxies and six tall pale posts; upper groups and narrow middle row absent; stone pattern differs | Revision 1 introduces a nine-bay candidate rhythm with dark mullions, narrow middle windows, basement windows and double door, stepped stone surrounds, sills and keys, and brick pilasters. Bay count near cropped corners, dimensions and door location remain estimates for independent review |
| South | Partial winter oblique and front-corner views | Blank/simplified infill and tall pale strips; likely missing openings | Unchanged; do not mirror west windows without a reliable source |
| North | No adequate current elevation yet | Baseline blank/simplified articulation cannot be called verified | Additional imagery required; remains unverified |
| Roof | Oblique views and prior footprint/roof checks | Roof rise/eaves unmeasured; exact tile/edge treatment uncertain | Prior reviewed geometry retained; no invented height correction |

The first revision adds geometric frames, reveals, sills, lintels and mullions to the west facade. Glazing panels currently sit in front of the retained structural wall rather than cutting all inherited wall layers; this is a known depth limitation for review, not a claim of reconstructed wall openings. No unseen architecture or verified interior is claimed. No score is supplied by the modeler.

## Revision and verification records

- Builder: `modular/buildings/refine_felix_haas_hall_second_pass.py` applies a hash-guarded delta to the exact starting source.
- `revision_r01/change_record.json` records actual removals/additions and the saved SHA-256.
- `revision_r01/renders/` and `revision_r01/render_settings.json` are produced by reopening the saved file.
- Independent review results belong in `review_r01/`; the reviewer must inspect the exact revision and record criterion deductions and coverage gates.

This candidate is incomplete until the independent visual threshold and all required gates pass. A source library is integrated into the master only by Tobin after the required TODO handoff and fresh-open verification. The project manifest is not edited to claim acceptance for a candidate revision.
