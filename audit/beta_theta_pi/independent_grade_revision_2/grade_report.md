# Independent grade revision 2 — Beta Theta Pi

**Score: 7.65/10 — BELOW 8.0**
**Reviewed asset SHA-256:** `4E45D55F49DB9796F8C3780CD29AB83B3D27B4C3E1ABA6FD6140AFE3CD2455B1`
**Review:** Blender 5.2.3 fresh-open; east/west/north/south/aerial renders; official Beta Mu chapter photos 1, 11, 14, 15, 16; FID 826 GIS/aerial overlay.

| Criterion | Score | Evidence and findings |
|---|---:|---|
| Correct identity and source-backed footprint | 2.00/2 | Purdue BuildingShapesZip4 FID 826 and both Purdue/official chapter address records identify Beta Theta Pi at 150 Littleton Street. The wall shell follows the official GIS polygon; the saved GIS/aerial overlay supports the property match. |
| Position, orientation, and scale/dimensions | 1.70/2 | The project geographic transform and full GIS polygon are used without box rescaling. Evaluated asset bounds in Blender are [[805.983, 827.11], [-417.268, -375.652], [-0.12, 15.0]]. Aerial overlay supports plan placement, but the photo facade has no surveyed compass bearing and the roof/facade alignment to individual GIS edges is interpretive. |
| Evidence-backed height, floors, and roof form | 0.80/2 | Three facade levels now match the official front photographs, and the housing directory reports four floors plus a basement; above-grade count remains an interpretation. Roof bands and the tower are now differentiated, but the east/west/aerial views still show oversized intersecting facets, abrupt roof seams, and exposed triangular wall-top areas. The roof silhouette/pitch does not yet read like the photo's discrete slate gables. The GIS height fields remain contradictory/unusable. |
| Facade, entrances, and distinctive architecture | 1.35/2 | The revision adds the tall pale bay with three arched glazed levels, a separate central brick gable, and an arched stone entry with plaque, all recognizable in chapter photos 1, 11, 14, 15 and 16. Brick tone and pale stone/window trim are source-consistent. Several west/east windows still appear partly occluded by or set into roof planes, while secondary elevations use a repeated generic sash layout; exact facade bearing and openings remain unregistered to GIS. |
| Modular export, portability, and complete evidence | 1.80/2 | Fresh-open check is this independent Blender 5.2.3 process: expected scene and collection loaded; 339 collection objects/339 meshes, five materials (['Beta Theta Pi | charcoal slate roof', 'Beta Theta Pi | dark reflective window glass', 'Beta Theta Pi | painted cream window frames', 'Beta Theta Pi | pale limestone trim', 'Beta Theta Pi | warm red-brown brick']), and no missing external image paths ([]). The evidence record includes raw GIS, layer metadata, official chapter gallery and address sources, aerial overlay, source-derived decisions and uncertainties. No public interior plan is available, so the interior is correctly omitted but remains unmodeled. |

## Required revisions

- Rebuild the roof panels so they follow each concave GIS cross-section instead of spanning between only the global minimum and maximum X intersections; the current rendered roof still has bridged/overlapping facets and exposed wall-top triangles.
- Align upper-floor windows and the pale bay/portal to the roof eaves so they remain visible and do not intersect or disappear behind the roof surfaces.
- Retain the improved three-level central bay, central gable, and entry, while using additional source views to resolve roof bearings and hidden elevations.
- No reliable floor plan was found; interior remains unmodeled rather than invented.

## Detailed file inspection

- Scene: `Building_massing_beta_theta_pi_fid826`; exported collection: `Asset_massing_beta_theta_pi_fid826`.
- Objects/meshes: 339/339; materials: Beta Theta Pi | charcoal slate roof, Beta Theta Pi | dark reflective window glass, Beta Theta Pi | painted cream window frames, Beta Theta Pi | pale limestone trim, Beta Theta Pi | warm red-brown brick.
- Missing external image dependencies: 0.
- Roof-named objects inspected: North_end_gable_roof, North_wing_roof, West_central_wing_roof, Central_tower_roof, East_central_wing_roof, South_end_gable_roof.
- The identity and footprint are well supported. The score remains below threshold because roof geometry and roof-to-facade intersections are visibly inaccurate in the saved views.
