# Independent Niswonger review

Reviewed 2026-10-22: build.py, changes.json, rotated plan.png and architect photof.jpg/photo3.jpg. Provisional score 5.6/10 (exterior 16/30, materials 12/20, interior 14/30, technical 7/10, evidence 7/10). This is a source/code review pending saved-file render inspection; it does not certify completed geometry.

Concrete blockers:
- Room157 extends west beyond the replacement roof and new north ground slab: center X -27.3m, width10.0584m rotated -13 degrees; roof starts X -24 and slab X -27. Quantify containment against structural footprint and ensure occupied rooms are enclosed and supported.
- Room149 and157 potentially overlap because their rotated room envelopes were independently registered. Require polygon intersection checks; capacity matching alone cannot verify placement.
- Rooms187/184 also need pairwise intersection review and circulation clearances.
- The new north roof is a rectangular four-vertex plane with approximate slope. Architect corridor image shows steel beams, roof decking, glazed clerestory, frequent horizontal rails, and partition panels. The simplified roof/columns/benches do not fully reproduce these.
- Classroom photo shows a complete ceiling, recessed lighting, ventilation grilles, tier side handrails, wall sconces, lectern, continuous desks and chairs with pedestals. Current script creates ceiling panels only, isolated desk blocks and unsupported chair seats/backs. These differences materially affect interior fidelity.
- New floor noise is bump only; photograph shows visible reflective tile grid and contrasting borders. Add correctly scaled grout/grid and tile variation, with meter-scale inspection render.
- Mullion edit changes viewport diffuse_color only; check its Principled shader base color separately before accepting rendered color.
- Four classrooms are partial interior coverage. Source plan contains substantial circulation, support rooms and a large central volume; current model should retain partial status.

Evidence limitations: 2016 manual is historical, room registration uncertainty stated +/-1.5m; height9.6m is a photographic estimate. No surveyed elevation, full current interior coverage, or Google Maps comparison reviewed here. Exterior/roof and interior categories cannot receive near-full marks from footprint agreement.

Next review requires saved/reopened exterior shader image, classroom shader image and top-down cutaway; exact room polygon intersection/containment measurements; source URLs and retrieval dates. No master/library files edited by reviewer.

## Saved-file follow-up, 2026-10-23

Revised independent score **6.7/10**: exterior19/30, materials14/20, interior18/30, technical8/10, evidence8/10. Reviewed refreshed exterior00:02 and classroom/atrium00:03 images, details.py, geometry_checks.json and source notes. Later00:04 roof closure change reported by builder is not independently rendered in this score.

Resolved or improved: source-sized four room polygons report zero mutual intersection and zero outside-envelope area; full floor/foundation correction; shader mullion color corrected; visible floor grout; chair support components, lectern, handrails and sconces; closed classroom ceiling; corridor beams and panel seams. Retained west historic roof means original concern about room157 roof coverage by the raised roof rectangle alone is withdrawn. Approximate registration remains a limitation.

Remaining visible defects: classroom chairs are square blocks rather than photographed curved upholstery; separated desk slabs differ from continuous photographed rows; screen above board is not visible; ceiling lacks photographed recessed fixtures/grilles and wall panels lack horizontal seams. Atrium is substantially darker and broader than the bright photographed corridor; windows appear as dark bands, floor/wall bright strips remain visible and need junction inspection. Its steel members remain simple bars instead of the detailed photographed framing, roof decking is absent, and terrazzo lacks photograph's aggregate/reflection richness. Exterior has broad generic blank walls, simplified glazing and uncertain roof dimensions. Confirm later roof closure fixes actual enclosure without obscuring source windows.

Full current interior, room116/hangar, offices/support spaces and accurate circulation remain incomplete; 2016 plan and approximate photograph proportions cannot establish current completeness. Score reflects substantive improvement, not achievement of requested9/10. Parent-provided Google Maps review is recorded evidence, not an independently performed map inspection by this reviewer.
