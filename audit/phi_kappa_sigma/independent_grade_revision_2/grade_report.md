# Independent Grade — Phi Kappa Sigma, Revision 2

**Asset:** `modular/buildings/massing_phi_kappa_sigma_fid829.blend`  
**SHA-256 confirmed before review:** `4392D2BDD1F2D51F81F730DAEBFE12FBD160D4A0A3A406003D1495E8F18C97C5`  
**Result:** **8.55/10 — passes the 8.0 threshold**  
**Reviewed:** 2026-10-26  
**Evaluator:** `evaluate.py`, run in Blender 5.2.3 against a fresh open. It independently checked the shell against the GIS ring, asset/collection contract, roof cap planes, facade UV link, and unpacked texture dependencies. Visual findings come from direct comparison of the revision renders with the archived chapter photos and aerial/GIS sources.

## Required five-criterion rubric

| Criterion | Score | Source-backed assessment |
| --- | ---: | --- |
| Correct identity and source-backed footprint | 2.00 / 2.00 | Purdue BuildingShapesZip4 FID 829 names Phi Kappa Sigma at 234 Littleton Street. The chapter's official Alpha Xi site independently identifies that address, and the GIS overlay places its ring over the matching pale multi-wing roof. |
| Position, orientation, and scale/dimensions | 1.90 / 2.00 | The shell base reproduces all 13 GIS ring vertices within **0.000024 m maximum nearest-vertex error** using the project's documented campus transform. The selected southwest-facing main facade is consistent with the official chapter photographs. The project conversion is approximate local XY rather than surveyed control, and this grade does not verify master placement. |
| Evidence-backed height, floors, and roof form | 1.30 / 2.00 | The photographs show three principal facade rows and a lower terrace wing; the revision models three stepped roof planes and the low wing. Heights of 10.1 m, 9.5 m, and 6.7 m are estimates, not measured elevations. The front photo shows an upper roof-edge baluster treatment that the model simplifies to a solid parapet on the main roof. |
| Facade, entrances, and distinctive architecture | 1.35 / 2.00 | The revision adds a seven-bay rhythm, three floor bands, painted brick relief, shutters, sidelights, pilasters, canopy, steps, and an upper pediment. The close render shows the small pediment overlapping the centered second-floor window; the reference photo has a more integrated, prominent entrance pavilion. Exact openings and finish details remain uncertain. |
| Modular export, portability, and complete evidence | 2.00 / 2.00 | Fresh-open passed with the expected scene and collection, 654 objects, and 653 meshes. The asset has three planar roof caps, 104 terrace-railing meshes, a physical-metre UV layer connected to the procedural brick shader, and no unpacked images. Building-specific audit files preserve the GIS/metadata, chapter page and photos, aerial imagery, transform assumptions, renders, and explicit uncertainty notes. |
| **Total** | **8.55 / 10.00** | **Pass.** |

## Findings and limits

Revision 2 removes the overlapping full-height roof solids and replaces them with one GIS-shaped shell and three planar roof caps. The lower terrace and its open balustrade are visible in the oblique render. The front facade render shows the new mortar/brick scale and revised window rhythm.

The main roof edge still needs a baluster treatment closer to the chapter photo. The small upper pediment intersects the central window in the close view; adjust that composition if the model is refined further. The evidence is strong for identity, footprint, broad facade style, and floor count, but not for exact heights, roof elevations, hidden sides, or exact colors. No reliable floor plan was found, so an interior was not invented.

This is an asset-only grade. It does not establish that the model has been placed or integrated correctly in the campus master.

## Source files reviewed

- `audit/phi_kappa_sigma/evidence.md`
- Purdue GIS FID 829 raw feature and layer metadata in `audit/phi_kappa_sigma/sources/`
- Official chapter page snapshot and `chapter_photo_4.jpg` / `chapter_photo_5.jpg`
- Esri imagery tiles and `fid829_footprint_overlay.png`
- Revision-2 front, roof-terrace, and facade-detail renders
- Exact-SHA fresh-open validation and revision summary
