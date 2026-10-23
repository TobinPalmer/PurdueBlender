# Independent Potter review

Score: **3.0/10 (30/100)**. This is an initial reconstruction, not a completed building.

Rubric: exterior 12/30; textures 5/20; interior 2/30; technical 7/10; source fidelity 4/10.

Inspected build.py, after.png and extracted 2016 renovation assessment. No asset changes made.

Blocking findings:

1. Interior contains four slabs only. There are no rooms, corridors, stairs, elevator, doors, ceilings or furniture. This fails the requested interior completion.
2. Floor elevations .61,4.1,7.6,11.1 conflict with explicit published floor-to-floor dimensions of 14 feet (4.2672m) above the first floor. Full basement, partial mezzanine and penthouse described on page46 are missing. This is a fixable source-supported discrepancy.
3. Brick shader projects Object X,Z on every wall. On walls perpendicular to X, X is constant, producing stripes rather than bricks. Object coordinates without a common mapping object also do not guarantee meter scale under arbitrary object transforms. Use explicit per-face wall UVs in meters or correctly scaled triplanar mapping.
4. Render uses Workbench material colors, so it does not demonstrate procedural texture scale, bump or glass. Render is severely off center and cropped at the right. Obtain complete exterior views and a material-render closeup.
5. Glass is an opaque Principled material with no transmission. Window boxes sit in front of an uncut continuous wall. This cannot support believable interior views or real openings.
6. Assessment page49 gives 5.4 square feet per typical window; implemented .61*.69=.4209m2 is about4.53 square feet. The comment citing4.5sf is inconsistent with source. The characteristic1-foot4-inch (0.4064m) deep overhang is absent; flat0.12m panels cannot reproduce it.
7. Panel allocation applies repetitive windows to every perimeter edge longer than8m, without matching documented blank brick regions or seven large first-story south windows. Main entrances, stairs/ramps and roof penthouse are absent.
8. Source is a2016 historical study; current exterior/interior changes require dated photographs and Maps verification. No claim of current full accuracy is supported by the supplied evidence.

Required before9/10: reconstruct source-supported story heights and partial levels; trace room/circulation plans with dated status; model entrance and window openings; map panel vs blank brick walls from photographs; add deep panel geometry and source-sized glazing; fix all wall texture axes; provide complete material renders and interior cutaways. Independent score must remain below9 until these are resolved and supported by evidence.

## Iteration 2 review

Updated build.py inspected after corrective edits. Revised provisional score: **3.8/10 (38/100)**: exterior14/30, textures7/20, interior3/30, technical8/10, source fidelity6/10.

Source-supported floor elevations now use basement-4.064m, first0.6096m, second4.8768m, third9.144m. Typical glazing now0.71x0.7066m, approximately5.4sf, and0.4064m overhang objects have been added. Normal-based selection now uses X on Y-facing walls and Y on X-facing walls, addressing the cardinal-wall projection defect; curved/noncardinal surfaces still require material-render inspection. These changes improve source fidelity.

At review time after.png still displayed the old cropped composition and three panel tiers. Render confirmation remains pending; do not represent the image as validating iteration2. The new camera target references a reacquired roof object after reopening; check the live file/render result rather than code intent alone.

Major blockers remain: no traced rooms/corridors, real door/window openings, stairs/elevator or finished interior; partial mezzanine and penthouse absent; no current Google Maps comparison; facade allocation remains estimated; opaque glass; Workbench cannot validate actual shader appearance. No9/10 certification is warranted.

## Final render confirmation

The refreshed after.png was inspected. Building is now fully framed, two upper panel tiers and small window representations/overhangs are visible. The stale/cropped image blocker is resolved. Final score remains **3.8/10**, since no material render or finished interior establishes the much larger remaining requirements. The exposed basement floor slab appears outside the above-grade envelope; basement walls and a cutaway/terrain treatment are required to avoid a floating floor/skirt appearance.

Parent-reported reference evidence (not independently browsed by this reviewer): Google Maps Potter Engineering Center,500Central Drive, Jan2024 photograph attributed to Alan Cesar; reddish brick rounded stair corner, pale deeply recessed small square windows in vertically ribbed precast panels, brown ground level. Parent also observed a stair interior with wooden handrail, black balusters and white walls. Reference: https://www.google.com/maps/place/Potter+Engineering+Center/@40.4273195,-86.9121142,17z . This establishes a Maps reference was consulted by the parent, but does not establish dimensional or full interior verification. Model currently represents only part of this observed vocabulary.

## Iteration 3 material and interior review

Independently inspected materials_after.png, interior_historic2016.png and plan_registration.json. Revised score **5.2/10 (52/100)**: exterior18/30, textures10/20, interior10/30, technical8/10, source fidelity6/10. This supersedes earlier scores.

Real progress: complete material render now exists; the dense precast pattern appears on the long wall; historical room partition reconstruction replaces empty slabs; basement walls enclose the previously exposed lower level. Parent reports actual apertures and transmission glazing, which require a closer interior/window render to confirm visually.

Remaining blockers: duplicated parallel walls and fragments are clearly visible throughout the interior cutaway. Source registration IoU is only75.7% basement and85.4% upper floors, so automatic silhouette fitting does not justify precise room positions or orientation. Check known stairs and asymmetrical room anchors manually against plan pages. Interior still lacks furnished functional rooms, connected stairs/elevator, finished doorways and ceilings. Current exterior material render is very bright, washing brick to pale pink and roof/precast almost white; mortar and physical texture scale cannot be judged at this distance. Provide neutral-lit closeups and a ground-height reference-matched exterior view. Existing historic plan partitions cannot establish a current2026 interior, especially after renovation. Current Maps evidence remains parent-observed rather than independently checked by reviewer. No9/10 completion is supported.

## Final iteration assessment

Latest exterior material render and interior cutaway inspected. Final score **5.4/10 (54/100)**: exterior18/30, textures11/20, interior11/30, technical8/10, source fidelity6/10. Improved lighting and temporary ground provide a clearer above-grade presentation. Parent reports merged wall meshes and a historically photo-supported room205 cabinet/bench reconstruction. Cabinet detail is not discernible in the supplied cutaway and receives limited credit pending a room closeup.

Union of traced solids does not remove duplicated parallel raster-wall lines when the spacing exceeds the closing radius. Several parallel narrow strips remain clearly visible in the final cutaway, especially top-left perimeter and central-left room cluster. These still require manual centerline cleanup against the source plan; reducing mesh count to4 is not proof of corrected wall topology. Also ensure morphological closing has not sealed door gaps.

Concrete remaining work before9/10: manually anchor and verify each plan orientation/scale; clean parallel walls and fragments; provide usable connected doors/stair/elevator circulation; model partial mezzanine/penthouse and characteristic entrance glazing/ramps; furnish and finish documented interior spaces; render closeups establishing brick scale, precast recess depth and glass transmission; verify architectural arrangement against dated current photos. Historical2016 interiors must retain their labels. A facade/interior completion claim is not warranted by the current evidence.
