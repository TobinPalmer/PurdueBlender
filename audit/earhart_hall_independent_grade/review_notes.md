# Earhart Hall independent grade

Candidate: `modular/buildings/massing_earhart_hall_0f14209.blend`  
Expected SHA-256: `4a5e0da6703f732583ffffc7a8697cd9515f84c6b9be1e0afa0a0b1ec5f9994`  
Actual SHA-256 rechecked during review: `4a5e0da6703f732583ffffc7a8697cd9515f84c6b9be1e0afa0a0b1ec5f9994`.  
Owner listed in root README: Brady.

## Review method

- Read root `AGENT.md`, `README.md`, and `modular/AGENTS.md`.
- Opened the candidate in a fresh Blender 5.2.3 background process and rendered a new overview. Candidate SHA-256 is recorded in `independent_fresh_open.json`.
- Independently compared the saved floor outline with the archived Purdue BuildingShapes feature 61 (ERHT) after applying the documented local geographic conversion. See `gis_footprint_comparison.json`.
- Inspected saved exterior and entrance views, and locally saved Pinola Photo reference. The independent isolated-room render is a fresh-open, in-memory preview only; the candidate file was not saved after adding the review camera or hiding objects.
- Rubric score is in `result.json`; the implementation is `evaluator.py`.

## Source notes

- Purdue GIS FeatureServer, `BuildingShapes` feature 61, feature abbreviation ERHT; source snapshot/metadata are in `../earhart_hall/sources/`. CRS is EPSG:4326. Coordinate conversion uses project origin (40.4274, -86.9137) and its stated local meter approximation. This is not a surveyed projection.
- Purdue University Residences official Earhart page supports building identity, residence-hall use, shared lounge/kitchen and on-site dining court, plus a representative standard double-room plan. [Official Earhart page](https://www.housing.purdue.edu/my-housing/options/residence-halls/earhart.html)
- Purdue move-in directions refer to floors 6–8. [Official move-in directions](https://housing.purdue.edu/move-in/west-lafayette/move-in/directions/earhart.html)
- AECME describes a bathroom renovation on floors 1–8 of the west tower. [AECME project description](https://aecme.com/project/purdue-university-earhart-residential-renovation/)
- Pinola Photo's 2026-10-12 exterior photograph shows the entry canopy, dark glazed doors, dining-court lettering and Earhart statue/pedestal. [Photo article](https://pinolaphoto.com/2026/10/12/designed-by-scholer-earhart-hall/)
- These sources support identity/footprint and story count better than absolute roof elevation. The saved GIS metadata exposes no unit/field description for F01–F08 or R, and the building's `NUM_LEVELS`/`CountOfFLO` values are 10. Therefore roof height and floor elevations are treated as estimated/unverified.

## Coordinator handoff

No building, master, manifest, index, or shared project file was modified. The only writes are files under this independent-grade directory. The manifest is coordinator-owned and its current Earhart cache metadata still describes the previous 16 m, one-object asset; refresh it during integration.
