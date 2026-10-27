# Independent grade — Kappa Delta / Theta Nu, 358 Northwestern Ave (revision 2)

**Result: 8.3/10 — PASS**  
**Evaluated asset SHA-256:** `46e35043eba672024ee1919473f936764755c2f253ce2108ce13b80ec09c6f67`

## Evidence reviewed

- Reopened the exact asset in Blender 5.2.3 and independently confirmed scene `Building_kappa_delta`, export collection `Asset_kappa_delta`, 1,216 objects (1,215 meshes), 18 used materials, and zero external file-backed images. See [`fresh_open_probe.json`](fresh_open_probe.json).
- Independently compared all four base vertices of `KappaDelta_OSM_Footprint_Foundation` with the saved OSM way 860903232 ring after applying the documented project transform and placement origin. Maximum nearest-vertex error was **0.0000014 m**. The source way and its 2022 edit date, project origin, and 34.51 × 22.44 m plan are documented in [`../evidence.md`](../evidence.md) and [`../build_summary.json`](../build_summary.json).
- Visually reviewed the r2 front, oblique, aerial, and interior renders against the architect/builder photo package, including the frontal aerial image, the oblique facade photos, and the stair/living-room images.
- Confirmed the reviewed asset SHA matches the revised builder evidence and the exact SHA requested for this review.

## Scores

| Category | Score | Review |
| --- | ---: | --- |
| Identity and site evidence | 2.0 / 2 | Official chapter, address, parcel, and imagery identify the Kappa Delta / Theta Nu building at 358 Northwestern. The local placement origin is documented from the OSM footprint centroid. |
| Footprint, form, and orientation | 1.9 / 2 | The foundation ring matches the four-point mapped footprint to about 1.4 micrometers in the project coordinate transform. Three occupied levels and the central gabled bay are supported by photos; exact roof/eave elevations and roof pitch remain estimates. |
| Facade and material fidelity | 1.4 / 2 | The front and oblique renders show the pale brick, limestone bands, arched lower glazing, sash windows, rails, central entry and paired dormers. The revision improves dormer balance, removes stray ridge-end caps, and narrows the center bay. The roof still reads as a broad, relatively plain plane in the aerial view, and the canopy, facade rhythm, and some dormer/roof proportions remain simplified versus the source photos. |
| Interior | 1.0 / 2 | The revised view now identifies a lounge, dining arrangement, kitchen with cabinetry/appliances, and a detailed switchback stair/lobby. These improve on the previous box-and-partition diagram, but the rooms remain sparse and schematic compared with the furnished source images; no measured floor plan is claimed. |
| Portability and fresh-open validation | 2.0 / 2 | Exact asset hash, scene and collection are verified after a fresh Blender reopen. Materials are present and no external images are required. |
| **Total** | **8.3 / 10** | **Passes the 8/10 gate** |

## Remaining limits

- The precise room plan, wall thicknesses, elevations, roof framing, and concealed sides remain unverified.
- The roof surface and its pitch/dormer details could be closer to the architect aerial; those uncertainties are included in the facade score.
- The interior is an illustrative photo-informed layout, not an as-built plan.
