# Independent exterior review: PMU r01

**4.25/10; not accepted against 9.9.** Exact saved asset SHA-256: `65f7a027c6b9ecf7e53b6d4706e83c850db2276a53f8baaa9f8d351cc8214533`.

I independently fresh-opened the file in Blender 5.2.3, inspected all eight supplied current views, compared the actual Purdue/REA photographs and north/aerial evidence, and generated an uncropped [entry view](entry.png) and [full roof view](roof.png). No model or builder was edited. [Evaluator](evaluator.py), [machine-readable scorecard](result.json), [fresh reopen](fresh_reopen.json), and [independent camera settings](render_settings.json) retain the review evidence.

| Criterion | Award / maximum | Main finding |
| --- | ---: | --- |
| Windows/openings | 0.90 / 3.0 | Some south five-bay/triple-light vocabulary is represented. North/east/west are largely blind; the newly saved June2009 north photograph clearly shows tall multi-light groups absent from the model. Tower small-light rows and panel divisions differ. |
| Signature architecture | 1.10 / 2.5 | Recognizable tower/arched entrance and relief locations, but mostly glazed grid doors replace the photograph's four mostly solid leaves. Tracery is too simple, reliefs are schematic, and the front apron obscures the exposed stair geometry. |
| Proportions, wings, roof | 1.15 / 2.0 | Current footprint and separate tower/flat/slate masses are present. North pitched roof/dormers are missing, central roof remains broadly simplified, and chosen heights are estimates constrained by return distributions rather than fitted planes. |
| Materials/depth | 0.95 / 1.5 | Warm brick, cream stone and charcoal roof are plausible material families. Slate course relief and ornate trim are underdeveloped; dark coincident patches occur at east/west bases. |
| Whole-building consistency | 0.15 / 1.0 | Front articulation does not extend to most other elevations, and full current reference coverage/cardinal opening schedules are incomplete. |
| **Total** | **4.25 / 10.0** | **Material exterior discrepancies and evidence gates fail.** |

The most useful next corrections are:

1. Build the north opening families and pitched roof/dormers supported by the dated north view, then obtain current west/east/service evidence. Missing source coverage must remain explicit; blank walls cannot be called verified.
2. Rebuild the tower window rows, four door leaves, nested curved tracery, stone spandrels and surround depth from the 2024 Purdue and REA details. The photos show small upper lights above the large middle lights, curved central divisions and mostly opaque door lower panels, which the r01 grid loses.
3. Correct the entry apron/stair classification: the independent front view shows a tall blank stone face at the approach where the photographed exposed steps should read.
4. Remove coplanar base artifacts. The builder offsets every base face only in Y; on X-facing walls this does not separate stone from the brick wall plane. Use outward edge-normal separation/thickness and inspect all corners under grazing light.
5. Register roof transitions and voids to the oriented aerial, including the north pitched roof. The large uniform plate and sparse roof details are not equivalent to the actual segmented overhead appearance. Do not substitute point percentiles for eave/ridge measurements.

The saved-file, identity/export and portability checks pass. All 262 inventory wall first vertices match the independent FID644 project-coordinate calculation within **0.00000215 m**, and the root remains identity in metres. This verifies registration to the cached source, not survey accuracy, roof heights or facade truth. The file contains 187 preserved first-pass interior objects in a hidden child collection; this review neither edits nor awards exterior points for them. Master integration remains a separate Tobin-owned gate and was not performed.

No threshold exception is requested at this first reviewed revision. Known wrong/missing facade and roof features require correction regardless of numerical threshold.
