# Independent Lambertus Hall grade

**Score: 8.0/10 — PASS**

| Criterion | Score | Evidence / limitation |
|---|---:|---|
| Correct identity and source-backed footprint | 2.0/2 | Purdue GIS feature FID 433 identifies LMBS / Lambertus Hall at 363 N Grant St.. The GIS ring has 39 distinct perimeter vertices; candidate shell has 39 per level. Independent paired local-vertex comparison max error=1.88110211e-06 m; mean=6.5310384e-07 m. Adjacent FID 432 is recorded as DUDL / Dudley Hall, reducing risk of selecting the neighboring GIS polygon.  |
| Position, orientation, and scale/dimensions | 2.0/2 | Fresh-open shell is at local origin with unit scale; shell local bounds are [[-4.33110237121582, 21.982175827026367], [-34.17417907714844, 35.69482421875], [0.0, 16.0]] m. Evidence placement origin differs from independent conversion by 0 m. After applying that origin, shell bounds differ from source-derived global bounds by at most 9.57682914e-07 m. The model uses the project's documented local approximate lon/lat conversion; no independent survey CRS or survey control is available.  |
| Evidence-backed height, floors, and roof form | 1.0/2 | The asset is five levels and 16 m high, consistent with the cited fifth-floor Nuclear Engineering use and overall project imagery. The top is modeled as a flat roof with parapet and a small screened plant; render 02 exposes the roof footprint. The 16 m height and 3.1 m story spacing are explicitly estimates; no Lambertus-only elevation or measured height was found. Height and floor elevations remain estimates, and the rooftop plant has no Lambertus-specific source confirmation. |
| Facade, entrances, and distinctive architecture | 1.0/2 | The model includes glazed panels, brick-colored areas, concrete-colored piers/belts, terracotta-colored sunshades, and entry canopies. The Ennead massing diagrams support a transparent ground level and multiple entry points; the BSA exterior photo supports glass, horizontal screening, and pale vertical structure. The strongest exterior photo visibly labels Dudley Hall; the packet itself says exact Lambertus-vs-Dudley facade allocation is unclear. Facade rhythm/material mapping is only partly attributable to Lambertus; the render's repeated vertical shade fins and entrances are not checked against a Lambertus-only elevation. |
| Modular export, portability, and complete evidence | 2.0/2 | Independent fresh-open found scene 'Building_lambertus_hall', collection 'Asset_lambertus_hall', 102 mesh objects, and 14 assigned materials. SHA-256 2DFE8E5EA016A29F5EE11228D8B0BA62C654BE7661DD103452BCCF56165FD7B4; expected hash matches: True. No linked libraries; missing external texture paths: 0. Evidence includes raw FID 433 and FID 432 snapshots, design diagrams, project photography, three renders, coordinate method, and explicit uncertainty notes.  |

## Overall findings

- Height and floor elevations remain estimates, and the rooftop plant has no Lambertus-specific source confirmation.
- Facade rhythm/material mapping is only partly attributable to Lambertus; the render's repeated vertical shade fins and entrances are not checked against a Lambertus-only elevation.

## Remaining uncertainties

- Exact Lambertus-vs-Dudley allocation of facade photographs
- No published Lambertus-only elevation or floor plan located
- Story elevations and top-of-roof height estimated
- Geographic conversion is not a survey-grade projection
