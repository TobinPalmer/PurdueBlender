# WALC independent grade — R5

**Result: 8.25/10 — meets the 8.0/10 review threshold.** R5 resolves the dominant R4 roof mismatch in the presentation and makes the glazed entry pavilion legible. It remains an image-guided model rather than a measured roof/façade survey.

**Reviewed asset SHA-256:** `71dd7f551168b9940db616c2bdde548f4df0835a8bf496037e8100e3f0f6cd5e`  
**Fresh reopen:** Blender 5.2.3 LTS reopened the exact hash. `Asset_walc` contains 969 objects / 897 meshes. `AssetRoot_walc` remains identity. All meshes have material slots; the relative foliage library resolves; no external images are missing. The GIS roof trace remains 156 vertices with unchanged bounds and is hidden in render and viewport. Detailed output: [independent_grade_r5_reopen.json](independent_grade_r5_reopen.json).

## Scorecard

| Category | Score | Findings |
|---|---:|---|
| Identity and plan footprint | 2.0/2.0 | Same WALC identity and plan geometry as R4. The source outline is retained; this is not an independent building survey. |
| Local frame and structure | 0.9/1.0 | Root remains identity and the foliage link resolves. Standalone review does not validate campus placement or neighboring alignments. |
| Exterior architecture | 1.5/2.0 | Low sloping wing and transition roofs, dark eaves, and a tall glazed south entry pavilion improve the roof silhouette and entry from R4. The long elevations still read as regular small windows. Roof transitions and the raised atrium monitor are approximations; the monitor is not clearly verified by the single official exterior image. |
| Materials and surface finish | 1.15/1.5 | Darker roof and deeper eaves improve silhouette and shadow. Brick, stone, glass and paving remain mostly flat under Workbench inspection lighting; the trees read unusually translucent in these renders. |
| Interior and program | 1.45/2.0 | Interior is unchanged from R4 and remains useful as a schematic program model. Public plans support room-program context but are not registered to verify as-built positions or finishes. |
| Reopenability and evidence | 1.25/1.5 | Exact-hash fresh reopen passed with four new views, relative library resolution, valid mesh materials and no missing external images. Roof pitch and height remain estimates, and no master scene was inspected. |
| **Total** | **8.25/10** | **Meets threshold.** |

## Visual comparison

I compared the R5 eye-level southwest and three oblique renders against Purdue's official 2018 exterior image, [Then & Now: Wilmeth Active Learning Center](https://www.purdue.edu/newsroom/archive/purduetoday/releases/2018/Q4/then-and-now-wilmeth.html), including its [official photo](https://www.purdue.edu/uns/images/2018/pt-wilmeth-6446.jpg), retrieved 2026-10-25. The reference clearly shows a broad, shallow roof with deep overhangs, distinct lower roof masses, a tall glazed pavilion, substantial masonry fields and varied window groups. R5's new eaves and lower transitions create a closer silhouette than R4's flat gray plane. The tall south-front pavilion is now visible in the eye-level view.

Remaining differences: the eye-level roof edge still reads almost horizontal from this particular camera angle; the north and southeast obliques show more of the new roof slopes. The long window bands remain more repetitive and smaller than the reference's grouped/tall window rhythm. The central raised monitor is a plausible but unverified interpretation, not something the cited image clearly establishes. The current Workbench renders do not show realistic brick/grout or glazing reflections, and site trees look translucent in the studio setup.

## Remaining work and limits

This score clears the stated visual threshold, but the asset should retain these limits in future integration/review:

- Confirm roof pitch, eave depth, ridge positions and roof transitions against a registered architectural roof plan/elevation or more authoritative oblique imagery. Do not use the GIS outline as roof-form or height evidence.
- Compare the raised monitor against additional roof imagery before treating it as verified; it currently remains a modeling interpretation.
- If further façade refinement is wanted, vary the long-elevation window groups and improve pedestrian-scale brick, limestone and glazing response without losing the deeper piers.
- Review `Placement_walc` with neighboring buildings in the master scene; the standalone asset review does not cover it.
- Keep interior geometry labeled schematic until scale-registered plans or survey evidence are available.

Reviewed renders: [eye-level southwest](eye_level_r5.png), [southwest](southwest_r5.png), [southeast](southeast_r5.png), and [north](north_r5.png). The R5 change log and modeling estimates are in [r5_change_log.md](r5_change_log.md).

**Scope:** Only this independent report and reopen report were written under `audit/walc_refine/`. No asset, master, shared file, or commit was changed.
