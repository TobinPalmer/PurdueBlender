# Independent grade revision 3 — Beta Theta Pi

**Score: 7.8/10 — BELOW 8.0**
**Exact asset SHA-256:** `18c78795b8e52b4d3566450745bb448d1116f7ded56c4312802a8e5f52fa5b25`
**Fresh-open:** passed in Blender 5.2.3 LTS.

| Criterion | Score | Evidence and findings |
|---|---:|---|
| Correct identity and source-backed footprint | 2.00/2 | Identity and GIS footprint are directly supported and geometrically faithful. |
| Position, orientation, and scale/dimensions | 1.90/2 | Campus placement and plan scale are strong; photographed facade bearing remains uncertain. |
| Evidence-backed height, floors, and roof form | 0.75/2 | The main roof silhouette and facet joins remain visibly incorrect. Roofs need contiguous, outward-facing surfaces with closed seams and the photographed gable/dormer profile. |
| Facade, entrances, and distinctive architecture | 1.45/2 | The main facade is recognisable and source-informed, though entry details and secondary elevations remain generic. |
| Modular export, portability, and complete evidence | 1.70/2 | The modular file opens and is portable, with broad provenance. Correct the evidence hash and degenerate shell face; interior remains intentionally unmodeled pending a plan. |

## Required revisions
- Do not bridge or cap the roof using mismatched planes. Rebuild a contiguous roof shell whose silhouette matches the photographed long slate wings, front gable, and dormers; remove the visible black gaps and spikes.
- Unify winding across all roof faces so normals point outwards; verify with a fresh-open normal audit and review from east, north, south, and 45-degree aerial cameras.
- Replace the duplicate closing point in the source wall-cap face to remove its zero-area polygon while preserving the 19 unique GIS vertices.
- Correct validation.sha256 in evidence.json to the actual asset SHA reported here; rerun the evidence/hash check after any rebuild.
- Improve the visible entry door/shield and finish secondary elevations where chapter imagery supports it.

See `result.json` and `geometry_validation.json` for the structured evidence and mesh measurements.
