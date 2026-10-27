# Independent grade — Phi Gamma Delta (FID 787)

**Score: 8.5/10 — pass**  
**Exact asset SHA-256:** `9ECBCED89189735DC00E1DD93D5B63B36DABEEEC8B18AEF040D0D810B545E101`  
**Blender:** 5.2.3 LTS; independently opened from the saved asset.

## Score breakdown

| Category | Score | Findings |
| --- | ---: | --- |
| Site identity and source confidence | 9.0 | Purdue GIS FID 787 names Phi Gamma Delta at 640 Russell St. Official chapter material confirms the house and Lyles Addition. The GIS capture date is unavailable, and legacy level/height fields conflict with current images. |
| Footprint, orientation, and placement | 9.0 | The retained 10-point outline is within approximately 0.21–0.45 m nearest vertex of FID 787 after projecting EPSG:3857 coordinates to lon/lat and then to the project’s approximate local coordinates. The aerial overlay shows the east-side inset. This checks roof/footprint proxy alignment, not surveyed wall placement. |
| Massing and architectural details | 7.7 | The model has three-level main-house masses, lower connector/addition, separate shallow hip roofs, asymmetric opening groupings, arched entrances, and arched addition glazing. Photos/renderings support the general character. Facade proportions, opening positions, roof pitch, and the addition-to-GIS-arm mapping remain estimated; rendered facades are still simplified relative to the sources. |
| Materials and texturing | 8.4 | Portable procedural buff-brick coursing/mortar and slate variation are visible. Limestone, frames, glass, doors and metal are separated into node materials. Surface treatments are plausible and source-aligned, not calibrated as-built material measurements. |
| Interior and evidence handling | 7.5 | No interior geometry is present. The official plans are not registered to the GIS/site plan, so room placement could assign spaces to the wrong wing. Omitting an invented interior is sound evidence handling, though interior modeling remains incomplete. |
| Blender integrity and portability | 9.8 | Exact file opens in Blender 5.2.3 LTS with stable scene/collection/root names. Independent topology probe: 216 mesh objects, 1,842 vertices, 2,769 edges, 1,359 faces, and zero boundary, nonmanifold or wire edges. No missing linked libraries or external images. |

**Weighted total: 8.515/10, reported as 8.5/10.**

## Remaining limits

The GIS outline is a roof/footprint proxy rather than a surveyed wall perimeter. The nearest-vertex transform comparison has sub-half-meter differences and uses the project’s approximate local conversion. Heights, openings, roof pitch, hidden elevations, and the exact boundary between the historic house and Lyles Addition are estimated. The floor plans have room labels but no proven georeferenced registration, and do not establish upper floors. Do not treat the model as having a finished interior.

The exact-hash fresh-open result and materials inventory are in `fresh_open_probe.json`; the run log is `fresh_open.log`.
