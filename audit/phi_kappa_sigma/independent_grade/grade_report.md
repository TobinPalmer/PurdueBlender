# Independent Grade — Phi Kappa Sigma (FID 829)

**Asset SHA-256 graded:** `B5F590CA2DEBC61C7F58E4FB6D9E9CA575D4C2957387C6BB54243F74C23305C5`  
**Result:** **7.6/10 — does not yet meet the 8.0 target**  
**Review basis:** Fresh-open report, independent visual inspection of the saved exterior render and source photographs, aerial GIS overlay, evidence record, build script, and a read-only Blender 5.2.3 inspection of the saved file.

## Score breakdown

| Category | Score | Findings |
| --- | ---: | --- |
| Building identity and source match | 1.0 / 1.0 | Strong: Purdue FID 829, the 234 Littleton address, chapter site, and chapter photographs all agree. |
| GIS footprint and campus coordinates | 1.9 / 2.0 | The footprint mass uses the transformed FID 829 ring and its bounds overlay the pale multi-wing roof. The documented local transform is appropriate for this campus model. The imagery is not survey-grade. |
| Massing, story count, and roof | 1.3 / 2.0 | Three-storey height is supported by the photographs and is labeled estimated. The main and attached wings are extruded to one uniform height, losing visible roof-height distinctions. More seriously, the “low roof and parapet” is a second full-height extrusion of the entire footprint from ground level, overlapping the shell rather than forming a roof cap. |
| Facade and architectural details | 1.35 / 2.0 | White masonry, dark shutters, repeated sash windows, and a central pediment capture the broad character. The facade remains too uniform: openings follow a repeated grid, and the entry lacks the photographed entrance pavilion depth, full-height classical framing, and surrounding wall articulation. The roofline balustrade/upper terrace visible in the chapter photos is absent. |
| Materials and texturing | 1.15 / 1.5 | Portable procedural painted brick, trim, roof, glazing, shutters, and door materials are present. In the render, the wall texture reads as a faint, noisy diagonal pattern rather than clearly scaled painted masonry; roof equipment/material variation is also missing. No external texture dependency is a strength. |
| Interior / interior decision | 0.35 / 0.75 | No interior is modeled. The evidence explains that no reliable plan was found, which avoids inventing a layout; the interior requirement nevertheless remains unmet if this asset is expected to be a complete building model. |
| Evidence and file validation | 0.55 / 0.75 | Sources, uncertainty notes, and a fresh-open validation report are unusually complete. The report confirms expected scene/collection names, 483 objects, 482 meshes, no external images, and the saved bounds. The asset has not yet been integrated into the master or checked there. |
| **Total** | **7.6 / 10.0** | **Below the 8.0 acceptance target.** |

## Blocking corrections before regrade

1. Replace the duplicate full-height roof extrusion with a true roof slab/parapet cap so the file has no coincident duplicate wall shells.
2. Model the roof-height steps visible in the aerial image instead of giving every attached wing the same elevation; add the photographed terrace/parapet treatment where supported.
3. Refine the front entry and window spacing from the chapter photos. Keep inferred dimensions labeled as estimates.
4. Tune the procedural brick scale/mapping so the render reads as white painted masonry at building scale.
5. Preserve the interior as explicitly unmodeled unless a usable plan is found; if a source-backed schematic can be added without guessing, document its limitations.
6. Reopen and render the revised asset, update its evidence/validation, and request a new independent grade against the revised SHA.

## Limits

The GIS source is strong evidence for identity and plan outline, not wall heights, roof construction, facade dimensions, or interior layout. Chapter photos support a three-storey classical facade but do not provide a measured elevation. This grade is for the standalone asset only; it does not certify master placement or integration.
