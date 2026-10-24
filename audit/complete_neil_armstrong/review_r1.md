# Neil Armstrong Hall source review — R1

## What changed

- Replaced the unsupported 21.5 m atrium height with the documented 53 ft ceiling height (16.1544 m). The curtain wall, atrium south wall, skylight, trusses, high-bay fixtures and exhibit suspension now follow that height. The 19.2 m transom row is hidden because it sat above the supported ceiling.
- Replaced the generic cylindrical Apollo object with a 3.0 m truncated-cone command-module silhouette. The service module and engine nozzle are hidden from the rendered source because Purdue identifies the atrium object as a replica Apollo I command module, not a full command/service spacecraft. Their original object names remain in the collection to preserve manifest compatibility. The command-unit dimensions are illustrative; current display status is unverified.
- Applied source-named Mayflower Red ACM to the high-roof slabs and Sea Wolf ACM to the entrance canopy/fascia. The current roof slabs remain flat proxies; the source describes the real roof as a warped, wing-like cantilever, but no dimensioned elevation was found to register its shape.

## Evidence and remaining limits

The project case history reports a 53 ft atrium and identifies the high roof as Mayflower Red ACM and the canopy/vestibule cladding as Sea Wolf ACM. It also describes the roof as a warped wing-like cantilever. [Design and Build With Metal project case history](https://designandbuildwithmetal.com/featured-projects/neil-armstrong-hall-of-engineering)

Purdue's October 17, 2007 announcement identifies a full-scale Apollo I command-module replica moved into the atrium for the hall dedication. This confirms the historical command-unit type, but does not confirm it is still displayed in 2026. [Purdue News Service](https://www.purdue.edu/uns/x/2007b/071017P-ApolloModule.html)

Purdue's March 27, 2026 emergency-preparedness page describes the facility as four levels: lower, at grade, and two upper floors. It does not provide floor plates or elevations. [Purdue ARMS building page](https://www.purdue.edu/operations/emergency-preparedness/arms/)

The current ArcGIS feature 642 snapshot is saved under `sources/`; its layer metadata identifies EPSG:3857. The existing project audit's screened source bounds are about 36.3 m wider and 30.3 m deeper than the selected shell bounds, with AABB IoU 0.3623. Those are screening bounds, not wall-error measurements; the project comparison uses its campus-local approximation rather than raw Web Mercator lengths. The feature's `NUM_LEVELS`/`CountOfFlo` attributes are 6, while Purdue's current facility page describes four levels. Their field meanings are not documented, so floor geometry remains unmodified. The plan, orientation, exact roof-wing form and facade opening cadence remain unverified. No footprint or XY geometry was changed from the bounding-box mismatch alone.

## Validation

The source asset was saved and reopened. The stable scene, collection, 444 object count, root origin and local bounds were checked. The atrium wall reopens at 16.1544 m; source-supported material names are assigned; hidden service-module/nozzle objects remain hidden. Temporary review cameras and lights were not saved into the library.

Review outputs:

- Exterior front: [exterior_r1.png](renders_r1/exterior_r1.png)
- Roof oblique: [exterior_roof_oblique_r1.png](renders_r1/exterior_roof_oblique_r1.png)
- Atrium cutaway: [atrium_interior_r1.png](renders_r1/atrium_interior_r1.png)

The cutaway render temporarily hides the facade glazing/mullions, north wing walls, skylight and roof slabs to expose the atrium. Those render-only visibility changes are not saved to the source asset.

Structured source notes: [evidence_r1.json](evidence_r1.json). Reopen measurements: [validation_r1.json](validation_r1.json). The asset-edit/render script is [revise_source_r1.py](revise_source_r1.py).

## Review status

This is a source-backed R1 candidate awaiting the coordinator's independent grade. It is not marked complete. Footprint registration, exact roof-wing geometry, current exhibit persistence, facade cadence and detailed floor plans remain review targets.
