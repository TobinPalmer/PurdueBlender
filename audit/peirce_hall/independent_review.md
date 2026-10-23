# Independent review — Peirce Hall

**Reviewed:** 2026-10-23  
**File:** `modular/buildings/peirce_hall.blend`  
**Review scope:** standalone asset, evidence notes, rendered exterior/front/interior views, Blender reopen/portability, and current manifest presence. No model, master, or manifest changes made.

## Ratings

- **Standalone asset / visual fidelity: 7.2/10.** Recognizable, cleanly organized, and materially differentiated, but the photo-supported front elevation has a visibly incorrect window/bay count and the interior reads as a schematic blockout.
- **Footprint and identity confidence: 9/10.** The saved structural shell has local bounds X −19.6488…19.6488 m, Y −12.7478…12.7478 m, Z 0.35…11.35 m, matching the bounds reported for the simplified official GIS footprint. The root is at local zero with unit scale and the placement origin is stored as [−115.170644, −85.321301] m. The build script uses Purdue GIS feature FID 216, code PRCE, and the local project frame. It represents the surviving Peirce Hall footprint, not the demolished original 1905 Physics building.
- **Elevation and interior evidence confidence: limited.** Three levels are documented, but the 11.7 m roof height, exact floor elevations, room plan, partitions, stairs, and furniture positions remain inferred. The project correctly labels these uncertainties. The reported 2022 third-floor lounge/mural is a supported interior cue; its exact room shape and furniture arrangement are not verified.

## What is working

- Blender 5.2.3 reopened the saved file successfully. The scene is `Building_peirce_hall`, the asset collection contains 1,275 objects, and the root is `[0,0,0]` / unit scale. The file has no linked Blender libraries and no external image dependencies, so it is self-contained.
- Brick, glazing, dark metal, stone, roof, and interior materials are separated and readable. The brick material uses a procedural running-bond texture. The roof is flat and the GIS-based shell is closed with no non-manifold edges according to the saved verification report.
- Historical identity is handled carefully: the model is the remnant present today after the south end was removed in 1989–90; it does not depict the demolished original 1905 portion. Purdue Archives documents the 1935 structure and 1983 connection to Psychological Sciences.
- The interior is explicitly marked interpretive. Purdue handbook evidence supports offices/labs and a third-floor break lounge is reported in the cited 2022 article, but no verified current dimensioned floor plan was found.

## Required fixes to approach 9/10

1. **Rebuild the photographed north façade bay schedule from the Purdue Events photo.** The reference photo shows about six upper sash groups and six tall middle recessed bays. The current front render shows about eight upper groups and eight recessed bays. Use the photographed spacing and count instead of applying the generic 4 m rhythm to this elevation.
2. **Add the lower inset/glazing detail within the middle bays.** The photo shows a small horizontal opening or inset near the base of each tall recess; the current model renders each as one uninterrupted dark brick-colored panel. Match the visible division and sill placement.
3. **Recheck ground-floor openings and entry composition against the same image.** The model has a repeated four-per-side ground window rhythm and two similar north entry doors. The photo’s frontage has a different grouping around its central entry. Use the photo-supported arrangement and keep any unverified side entrance clearly identified as inferred.
4. **Make the illustrative interior physically legible.** Interior partitions currently run continuously through the supposed doorway positions, with door leaves placed into the walls. Cut actual doorway gaps, align doors, make the three floor/circulation levels coherent, and improve the stair/landing transitions. Replace some repeated block furniture with more varied desks, chairs, storage, and room boundaries. Keep the plan labelled schematic until a measured plan is found.
5. **Improve the review views.** The exterior and interior renders are washed out and low contrast, which hides material response and makes it hard to judge depth. Adjust lighting/exposure and camera framing, and provide a close front-elevation view for bay-count review.
6. **Complete integration before claiming master placement is verified.** The current `modular/manifest.json` has the Peirce massing entry (`massing_pierce_hall_prce_e5f59eb`) but no `peirce_hall.blend` detailed-asset entry. Thus, the standalone local origin is well documented, but this review cannot verify the detailed collection’s placement marker or appearance in the master. Add/update the detailed manifest/master placement in the integration pass, then compare it against the GIS center and adjacent Psychological Sciences connection.

## Source checks and limits

- Purdue GIS snapshot and layer metadata are cited in `audit/peirce_hall/RESEARCH.md`; official service: [Purdue campus FeatureServer](https://mapsweb.lib.purdue.edu/arcgis/rest/services/Purdue/campus/FeatureServer).
- Photo comparison: [Purdue Events Peirce Hall page](https://events.purdue.edu/peirce_hall) and its [building photo](https://localist-images.azureedge.net/photos/40102458412925/card/dcd8f86af992cb56cc847a7bbf16fdaae69d1eff.jpg). The front render matches broad red-brick/three-level character and recessed middle bays, but not their observed count/detail.
- Historical check: [Purdue Archives Peirce Hall history](https://archives.lib.purdue.edu/agents/corporate_entities/673).
- Interior-use evidence: [Purdue Psychological Sciences graduate handbook](https://hhs.purdue.edu/wp-content/uploads/2023/04/PSY-Graduate-Handbook.pdf).
- Google Maps satellite is cited in the project research notes at [the Peirce Hall campus pin](https://www.google.com/maps/@40.42675,-86.91515,163m/data=!3m1!1e3). Its direct page could not be independently opened through this review browser, so satellite details here rely on the existing audit’s inspection and the project GIS snapshot.

**Recommendation:** keep the asset as a strong GIS-aligned first pass, but do not rate it 9/10 until the photographed north façade rhythm and recess detail are corrected, the interior doors/circulation are made coherent, and detailed placement is verified in the master.

## Independent final-pass review — 2026-10-23

**8.8/10.** The final revision corrects the north bay schedule, adds six lower inset slots, clarifies entry openings, removes the unsupported secondary-door canopy/plaque, and improves the lounge cutaway. The reopened asset contains 1,236 objects; the shell is closed without non-manifold edges, and it has no external dependencies. No clear visible defect remained in the supplied final renders. Remaining uncertainty is in unsupported side/rear openings, exact heights, and room plans; these features remain interpretive. This final score supersedes the earlier review scores.
