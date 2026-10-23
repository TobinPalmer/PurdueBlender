# Brown Laboratory of Chemistry — independent review

**Review date:** 2026-10-23  
**Asset reviewed:** `modular/buildings/brown_laboratory_of_chemistry.blend`  
**Independent asset-quality score:** **8.3/10** (target: 9/10)  
**Survey-dimension confidence:** **Unverified**; the score is for the crafted asset, not a claim of survey-grade dimensions.

## Findings

- **Reopen and portability pass.** Reopened the saved file in Blender 5.2.3 LTS using the supplied audit. It contains 63 collection objects, 49 meshes and 17 used materials. All objects are parented to the asset root; every mesh has material slots; no linked libraries or unpacked external images were reported.
- **Local origin and placement basis pass.** Root translation is `(0, 0, 0)` and scale is `(1, 1, 1)`. The asset metadata origin `(145.5986824, -90.6512413)` matches the center of the source massing XY bounds recorded in `modular/manifest.json` for BRWN feature 247. This supports consistent local-to-campus placement relative to the supplied massing; it is not an independent survey of the campus coordinate reference system.
- **Exterior is coherent and materially strong.** The render reads as red-brown running-bond brick, pale projecting concrete piers, dark narrow glazing, a flat roof and a central entry. Procedural brick and concrete shaders give the facade useful color and surface variation without external texture dependencies. The historical 1999 reference photo supports this broad vocabulary, while not establishing present-day condition.
- **Google Maps supports broad footprint and orientation only.** The satellite view centered near Brown shows a long east–west roof mass and pedestrian access on the south side, consistent with the asset's long-axis orientation and south entry. It does not establish facade detail, exact footprint dimensions, height, or imagery capture date. The map attribution visible during review named Airbus/Maxar; that attribution does not identify when the imagery was captured.
- **Interior is a convincing representative vignette, not a verified as-built layout.** The basement NMR room render has recognizable cryostats, control displays, benches, sink and safety markings. Above-grade interiors use one repeated generic lab/corridor module on all five floors. The official first-, second- and fourth-floor plans show a shared corridor and recurring lab bays, but also floor-specific room divisions, cores and end spaces; the model does not reproduce those distinct layouts closely enough to claim plan-level accuracy.
- **Basement-plan evidence is incomplete in the audit folder.** The QA notes say basement, first-, second- and fourth-floor images were saved. The folder contains only first-, second- and fourth-floor plan images. Purdue's official plan index currently provides a Brown basement link, so the missing reference can be retrieved and compared before the B124 NMR room is described as plan-verified.

## Fixes needed to reach 9/10

1. Retrieve the official Brown basement plan and adjust the NMR vignette's room footprint, access and equipment placement to match what that plan actually documents. Keep specific magnet models/capacities marked as illustrative unless independently sourced.
2. Replace the identical above-grade interior module with floor-specific partitions and service-core/end-wing layouts traced from official plans. Preserve the current repeated lab furniture as representative only where the plans do not specify fit-out.
3. Add a current, dated exterior reference set or Google Maps street-level views for the entry, facade and roof. Reconcile the window rhythm, pier spacing, entry details and rooftop equipment against those views; the available aerial and historical photo cannot verify those present-day details.

## Limits on dimensional claims

The model retains the supplied massing footprint and its placement origin is internally consistent with the manifest massing bounds. The provided sources do not independently establish a surveyed campus coordinate reference, exact exterior dimensions, floor-to-floor heights, roof height or current facade condition. The massing is 16 m high while inferred rooftop elements raise the asset's maximum to 18.81 m. Treat those as source-model/inference dimensions until checked against a survey or authoritative measured drawing.

## References checked

- [Purdue Chemistry building plans](https://www.chem.purdue.edu/building/) — official index exposes Brown basement and floors 1–5. The supplied folder contains plan images for floors 1, 2 and 4 only.
- [Historical 1999 Brown exterior photograph](https://www.asergeev.com/pictures/archives/compress/1999/91/16.htm) — supports the brick/concrete/window vocabulary visible in that historical view.
- [Google Maps satellite view near Brown](https://www.google.com/maps/@40.426584,-86.911984,18z/data=!3m1!1e3) — inspected for footprint orientation and broad roof/site context; no capture date or facade survey was established.
- Local evidence: `QA.md`, `brown_exterior.png`, `brown_interior_lab.png`, `brwn-1-floorplan.jpg`, `brwn-2-floorplan.jpg`, `brwn-4-floorplan.jpg`, `reopen_audit.py`, and the BRWN source-massing entry in `modular/manifest.json`.

## Integration note

At review time, `modular/manifest.json` contains the BRWN source-massing entry but no detailed `brown_laboratory_of_chemistry` asset entry. This report does not change the master blend or manifest; the master orchestrator should handle integration after review.

## Independent final-pass review — 2026-10-23

**8.8/10.** The final saved revision reopens in Blender 5.2.3, contains 72 objects and 57 meshes, and passes interior containment for all 50 interior meshes (17,560 vertices) and all 3,224 partition vertices. The NMR cryostat seam and floating white panel were corrected. Two entrance stair/landing projections are explicitly tagged as exemptions. No material visible defect remained in the final review. The remaining limitations concern approximate plan registration and unavailable evidence for some exact dimensions/details; the interior remains an informed reconstruction. This final score supersedes the earlier review scores.
