# Independent review — American Railway Building

**Asset reviewed:** `modular/buildings/american_railway_building.blend`  
**Evidence reviewed:** revised exterior, ground-floor, upper-floor, and eye-level interior renders; updated `REVIEW.md`, `verification.json`, and the reproducible build script.  
**Final independent rating:** **7.9/10**

## What is working

- The asset has a useful two-storey silhouette, brick and limestone palette, glazed openings, parapet/coping, and visible entry. The exterior render reads as a small campus building rather than the original single extrusion.
- The reported origin and campus bounds are internally consistent with the stored local bounds. The source polygon is retained, and the revised verification record reports a successful reopen, 604 material-assigned meshes, and no unpacked image dependencies.
- The added eye-level cutaway makes the stair, glazing, furniture, and first-floor organization much easier to inspect. Ground and upper floors show visibly different workstation densities and some usable circulation.
- The official architect project page confirms the two-storey, 1926 building and a renovation intended for open graduate workspaces and teaming on both floors. [American Structurepoint project page](https://www.structurepoint.com/product-page/purdue-university-american-railway-building-renovations)

## Remaining defects

1. **The focus booth intersects the exterior envelope.** A large blank, off-white rectangular box is visible outside the ground-floor right side of the building in the new exterior render. It also protrudes past the slab edge in the floor-plan renders. The booth geometry appears outside the source footprint; move it fully inside, model an actual exterior projection supported by source evidence, or omit it. Re-render exterior and floor plans after correcting it.
2. **Exterior details still read as a procedural model.** The brick bond is clear but uniformly bright and repetitive. Window reveals are shallow and the upper windows read as rectangular openings with straight heads rather than segmental arches. The lettering is improved and legible, though pale against the brick. Further material and light tuning would improve depth and realism.
3. **Roof and elevation accuracy remain unverified.** The broad flat roof, restrained HVAC curb, parapet, and window schedule are plausible but still generic; the audit calls the height an estimate and says the architect's plan sheets and live aerial view were not inspected. Avoid claiming full exterior accuracy without verifying the remaining elevations and roof.
4. **The interior is clearer but still illustrative.** The eye-level cutaway is a useful improvement, but the workstations, cafe corner, focus booth, stair and circulation have not been matched to construction plans. In the eye-level view, the prominent foreground partition blocks a large portion of the scene, and the stair/landing connection is difficult to read. Consider another interior angle with the partition cut down or hidden and show the stair landing clearly.
5. **Source-area discrepancy remains unresolved.** The inherited GIS footprint yields roughly 3,074 square feet over two floors, while the cited 2015 study is reported as approximately 2,500 gross square feet. Retaining the mapped footprint is reasonable, but the asset's scale needs a note or confirmation before using it as survey-grade geometry.

## Targeted next changes

- Move the focus booth within the footprint and confirm that it is not visible through or outside the facade in any normal exterior view.
- Verify opening/head details, roof/parapet profile, equipment and facade orientation against current photos or plans; keep unknown features explicitly labelled as illustrative.
- Add a second exterior angle showing the other elevation and the entry/grade relationship.
- Reduce the foreground partition in the eye-level view and expose the stair landing/circulation. Verify room placement against plans if the sheets become accessible.
- Slightly soften brick repetition and improve glazing/limestone response; the revised materials are less blown out but remain strongly graphic.

## Review limits

I inspected the rendered evidence and source/build QA on disk. I did not reopen the `.blend` in the live Blender session because that would replace the user's active scene. The supplied `verification.json` records a successful reopen check. I did not modify the asset, master blend, or manifest.

## Final follow-up review — 2026-10-23

The revised asset addresses key prior comments: the exterior label is readable, corner and coping profiles are less heavy, the window rhythm varies on the secondary elevation, and an eye-level interior view supplements the plan cutaways. The verification record reports a successful reopen, 604 meshes with materials, no unpacked image dependencies, preserved placement origin, and an unchanged source massing hash. Visual review found one new, clear geometry defect: the focus booth protrudes outside the building envelope. That issue and unresolved source accuracy keep this asset below 9/10.

The current revision scores **7.9/10**. The previous 7.6 score is superseded. This is an independent review of saved renders and audit material; I did not modify the asset, master blend, or manifest. I did not reopen it in the live Blender session, to avoid replacing the user's active scene.

## Builder correction after final review — 2026-10-23

The builder moved the focus booth to the southwest interior zone and rebuilt the asset. Blender 5.2.3 reopened the saved file successfully. The reproducible QA now tests every vertex in all five booth meshes against the retained source polygon: **40 vertices checked, zero outside**. The four review images were refreshed under the `*_footprint_fix.png` names, and visual inspection confirms the booth no longer appears beyond the facade or slab edge. The builder also shortened the low partitions and added a stair landing.

The **7.9/10 independent score above applies to the pre-correction revision**. This defect-specific follow-up confirms the reported correction and reopen/geometry checks; it is not a new independent overall score. A new independent score for the corrected asset remains pending. Roof/elevation and interior-plan evidence gaps remain.

## Independent final-pass review — 2026-10-23

The corrected asset scores **8.5/10**. The brick UV banding is resolved, the arched heads read clearly, and the eye-level cutaway no longer has floating arches or ceiling discs. Saved-file QA reports 693 material-assigned meshes, zero unpacked images, and all 2,916 vertices from 291 interior meshes plus the 40 booth vertices inside the source footprint. The placement origin is preserved. Remaining limits are the unresolved 3,074 vs 2,500 sq ft area discrepancy, unverified roof/window/room details, illustrative interiors, and a graphic repetitive material style. Those evidence gaps keep it below 9/10. Independent review only; no edits made.
