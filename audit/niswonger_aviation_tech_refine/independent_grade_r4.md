# Independent grade — Niswonger Aviation Tech R4

**Score: 8.0/10** (minimum pass: 8.0/10).  
**Asset SHA-256:** `9f98941ce097226c3fe677aed3a2f18f5b482359eff5256710a9f13880db96b4`

## Rubric

| Criterion | Score | Evidence and finding |
|---|---:|---|
| Correct identity and source-backed footprint | 1.7/2 | The [MSKTD project page](https://msktd.com/project/purdue-university-niswonger-aviation-technology/) names the Purdue Niswonger Aviation Technology Classroom Building addition and renovation. OSM way 256667242 and the Esri z20 tile support the campus identity and show a classroom/hangar complex with separate roof zones. R4 depicts its main volumes. The saved centroid-based overlay shows source/model-outline misalignment; neither GIS nor OSM is an as-built survey, so exact wall footprint is not verified. |
| Position, orientation, and scale/dimensions | 1.9/2 | My fresh reopen confirmed local root `[0,0,0]` and mesh bounds `[-50,50] × [-65.5,65.5] × [-0.15,10.2006] m`. The prior independent R3 master probe recorded `Placement_niswonger_aviation_tech` at `(-1325,-1229.5,0) m`, zero rotation, and unit scale; R4 preserves that coordinate frame. No surveyed control point proves sub-meter geographic registration, and I did not reopen the master for this R4 grade. |
| Evidence-backed height, floors, and roof form | 1.5/2 | R4 renders all four roof shells and adds the source-visible rooftop service zone as an illustrative HVAC cluster. Esri z20 imagery supports dark/light roof zones and a concentration of equipment; Purdue's [2019 Airport HVAC project record](https://www.purdue.edu/bot/meetings/past-meetings/2019/06.%20aug/pfc/508_Airport-HVAC-Window-Overhead-Door.pdf) confirms an AHU replacement project. This addresses the R3 omission of rooftop equipment. Roof plates remain broad and simplified; exact perimeter, slope, elevations, unit count/type and coordinates are unverified. |
| Facade, entrances, and distinctive architecture | 1.6/2 | MSKTD exterior photos support brick walls, a glazed entrance/connector, metal overhang, and pitched clerestory; interior photos support the steel framing and roof glazing. The R4 oblique render represents these distinctive volumes and materials. Facade bay rhythm and door placement are not reconciled against a georeferenced elevation set, and the neutral preview does not establish photo-real texture accuracy. |
| Modular export, portability, and complete evidence | 1.3/2 | My fresh Blender 5.2.3 reopen confirmed `Asset_niswonger_aviation_tech` has 2,314 objects / 2,228 meshes, root at origin, no materialless meshes, no missing external image files, and the R4 cluster inside the export. The asset is self-contained. The shared manifest and `modular/BUILDINGS.md` still list 2,300 objects, leaving 14 added objects unindexed; the master has not been independently checked against R4. The Esri tile endpoint exposes no image acquisition date. |
| **Total** | **8.0/10** | **Pass at threshold; integration and source limits remain open.** |

## Fresh reopen evidence

I reopened the saved asset independently with Blender 5.2.3. The digest matched R4 exactly, the named export collection contained 2,314 objects (2,228 meshes), the root remained at local origin, every mesh had a material, and no external image paths were missing. The HVAC cluster object is present. Probe output: `independent_reopen_r4.json`; evaluator: `independent_grader_r4.py`; machine-readable result: `independent_grade_r4.json`.

## Findings and unresolved limits

- R4 adds a plausible rooftop service cluster in the approximate east/northeast zone visible in the aerial. Its shape, count and placement are illustrative, not measured.
- The broad wing roof plates still lack a precise plan match; the overlay documents registration mismatch. No public as-built roof/mechanical plan was found.
- Roof elevations, slopes, exact perimeter and detailed facade rhythm remain uncertain.
- Coordinator follow-up is required to reconcile the shared manifest/index to the 2,314-object asset and verify the R4 master link/placement. I did not edit shared files.

## Sources inspected

- [MSKTD — Purdue University Niswonger Aviation Technology](https://msktd.com/project/purdue-university-niswonger-aviation-technology/), including the downloaded exterior/interior project photos.
- [Purdue Board of Trustees — Airport HVAC, Window Replacement and Overhead Door Repair (2019)](https://www.purdue.edu/bot/meetings/past-meetings/2019/06.%20aug/pfc/508_Airport-HVAC-Window-Overhead-Door.pdf).
- [Esri World Imagery MapServer](https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer); local z20 mosaic and registered overlay inspected. The tile service does not provide an acquisition date for this image.
- [OpenStreetMap way 256667242](https://www.openstreetmap.org/way/256667242); saved snapshot includes the OSM timestamp and WGS84 coordinates.
