# Windsor Halls asset evidence

Retrieved 2026-10-26. This record applies only to `massing_windsor_halls_80aeb51`.

## Identity and component boundary

Purdue Housing describes Windsor as five connected residence halls: Duhme, Shealy, Warren, Wood, and Vawter, with Windsor Dining Court below Vawter and Warren. The stable asset assigned here represents the subset covered by Purdue GIS FIDs 63–66:

| FID | Purdue GIS name / abbreviation | Included geometry |
| --- | --- | --- |
| 63 | Martha E. & Eugene K. Warren Residence Hall / WARN | Warren shell, roof, facade details |
| 64 | Elizabeth G. & William R. Wood Residence Hall / WOOD | Wood shell, roof, facade details |
| 65 | Everett B. Vawter Residence Hall / VAWT | Vawter shell, roof, facade details |
| 66 | Windsor Dining Court / WDC | Separate low service-volume schematic |

The adjacent Shealy hall (FID 277) is owned in the asset list by Arjav, and Duhme (FID 278) is represented by its separately finished asset. Both are intentionally excluded here to avoid duplicates. The complete source snapshot also preserves their polygons for context.

## GIS source and footprint method

- Provider: Purdue University ArcGIS Online, `BuildingShapes` feature layer (`BuildingShapesZip4`, FeatureServer layer 0).
- Query URL: [Purdue GIS query for FIDs 63–66 and 277–278](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0/query?where=FID%20IN%20(63%2C64%2C65%2C66%2C277%2C278)&outFields=*&returnGeometry=true&outSR=4326&f=geojson).
- Layer metadata: [FeatureServer layer metadata](https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/BuildingShapesZip4/FeatureServer/0?f=pjson); metadata reports a last data edit of 2026-08-31 16:13:41 UTC. The layer reports geometry area and length in meters, but does not publish units for its `Elevation`, `NUM_LEVELS`, or `Extrution` attributes.
- Snapshot: [purdue_gis_windsor_fids_63_66_277_278_2026-10-26.geojson](sources/purdue_gis_windsor_fids_63_66_277_278_2026-10-26.geojson), retrieved 2026-10-26; CRS EPSG:4326.
- Measurement transform: project local campus meters, X east and Y north, using `X=(longitude + 86.9137) * 111412.84 * cos(radians(40.4274))`; `Y=(latitude - 40.4274) * 111040`. This is the repository's local approximate transform, not a surveyed projection.
- Structural walls use the complete GIS exterior rings with no vertex simplification. Their XY footprints therefore match those rings after the stated transform; facade, roof, trim, and door details are overlays and are not included in the wall-footprint comparison.
- GIS ring winding is reversed to counter-clockwise before generating geometry so facade details face outward.

## Official architectural references

- [Purdue Housing — Windsor Halls](https://housing.purdue.edu/my-housing/options/residence-halls/windsor.html): five connected named halls, construction period, room amenities, generic Windsor room illustrations, and Dining Court below Vawter and Warren. Captured 2026-10-26. Room drawings are generic and are not used as building-specific interior plans.
- [Purdue Office of Emergency Preparedness — Warren Hall](https://www.purdue.edu/operations/emergency-preparedness/warn/) and [Vawter Hall](https://www.purdue.edu/operations/emergency-preparedness/vawt/): current plans describe both as four-story buildings with a ground floor and partial basement. Vawter plan revision date: 2026-10-13. This informed the four visible facade rows; it does not establish exact floor-to-floor heights.
- [Purdue Archives — Warren Hall](https://archives.lib.purdue.edu/agents/corporate_entities/671) and [Vawter Hall](https://archives.lib.purdue.edu/agents/corporate_entities/779): historic entries state that the lobby doors in Duhme, Shealy, Warren, and Vawter align on a straight axis. That supports the estimated south-facing, aligned Warren/Vawter entrances; their exact offsets are not surveyed.
- [RGCollaborative — Purdue Wood Hall renovation](https://www.rgcollaborative.com/projects/Education/purdue-university-wood-hall) and [project exterior image](https://www.rgcollaborative.com/projects/purdue-university-wood-hall/93/Image1-optimized.jpg): renovation architect's project documentation for Purdue's Wood Hall and historic-feature work, viewed 2026-10-26. The projecting central entrance bay is a visual interpretation of project imagery; it is not a measured elevation.
- [RGCollaborative — Wood Hall exterior image, alternate view](https://www.rgcollaborative.com/projects/purdue-university-wood-hall/96/Image4-optimized.jpg): viewed 2026-10-26. The image supports a symmetrical central bay, carved stone emphasis, steep gable, window rhythm, balustrade, arched entrance and lanterns for Wood. The modeled details are interpretive and not measured from a calibrated elevation.
- [Warren Hall renovation project description](https://schooldesigns.com/Projects/purdue-university-warren-hall-renovation/): viewed 2026-10-26. This Purdue-client renovation account identifies Warren's restored woodwork, limestone fireplace mantels, polychrome tile flooring, and lounge/public-space finishes. Those cues inform only the labeled Warren schematic interior palette; they do not supply a floor plan or exterior elevation.
- [Purdue StarRez housing portal image](https://purdue.starrezhousing.com/StarRezPortalXConference/File/GetImage?dateCreatedTicks=638309106832699833&hash=3B0DB762&imageName=52483840151_ea5f2e6ade_k.jpg&tableID=13617&tableName=PortalPageWidget): official residence-hall exterior reference, viewed 2026-10-26. It supports red-brown masonry, pale stone trim, dark slate roof, and historic collegiate-residence character. It is not labeled by individual hall, so it does not support hall-specific doorway placement or exact roof details.
- [Purdue Archives — Windsor Dining Court](https://archives.lib.purdue.edu/agents/corporate_entities/989): campus historic database entity reference, viewed 2026-10-26.

## Footprint and overlap findings

The attached [GIS polygon overview](previews/windsor_gis_footprints.png) identifies FIDs by color. Source footprints for all four included records are used as their own mesh boundaries; the comparison metrics are recalculated against the fresh-open asset in `validation.json`.

The GIS reports distinct polygons for FIDs 63–66. FID 66 has zero shared area with FIDs 63, 64, and 65, while its boundary touches all three. Purdue Housing says the Dining Court is under Vawter and Warren, but the GIS polygons alone do not show that vertical relationship. The model consequently keeps FID 66 as a separate low shell placed below the halls' inferred grade level; the exact subsurface outline and elevation are not verified. It does not merge or enlarge FID 66 to manufacture a horizontal overlap.

## Geometry, textures, and uncertainty

The asset has distinct component object groups within the stable parent collection: structural footprint shells, separate hall roof meshes, hall-specific gabled roof accents, limestone courses, recessed sash windows, entry portals, and schematic interior furniture. The structural walls retain the exact GIS XY rings. Warren, Wood, and Vawter roof plans are inset 0.3 m and simplified by 0.55 m only to smooth GIS digitization steps; the structural shells are unchanged. Their constrained roof meshes are refined and follow a near-linear distance-to-boundary profile to peak along estimated ridges, removing the previous broad flat caps. Roof rise varies by hall and remains estimated because no measured hall-specific roof elevations were located. Dining Court retains its separate low service roof and exact FID 66 shell. Wood's central bay, gabled roof cue, arched entry, balustrade rhythm, and lanterns draw from the renovation architect's exterior imagery. Warren's restoration-derived color cue appears only inside the explicitly schematic slice. Warren and Vawter entry silhouettes remain estimates based on the documented straight lobby alignment, not verified photographed elevations.

Brick uses UV-mapped procedural running-bond courses and mortar with a shallow bump; slate and limestone use procedural surface variation; glazing has bronze sash muntins and stone surrounds. All materials are packed procedurally with no external image-texture dependencies.

Warren, Wood, and Vawter use four visible facade levels and approximate roof volumes. Current Purdue plans substantiate four above-ground stories for Warren and Vawter. Wood is assigned the same visible count by visual consistency with the GIS `NUM_LEVELS` field; a Wood-specific official story description was not located. GIS `Elevation` values around 600 are treated as feet only by inference to establish relative grade offsets; their units are undocumented. GIS `Extrution` values inform only rough wall-height estimates and are not treated as verified meters. Roof geometry, decorative details, door positions, facade bay count, and all vertical dimensions remain estimates.

Each residence has a clearly named low-wall schematic cutaway slice with two generic 14 ft × 16 ft room modules, corridor, beds, desks, storage, and shared lounge furniture. An isometric preview makes the walls and furniture readable. Purdue Housing supports the generic room dimension and room/lounging amenities; the Warren renovation description supports a muted tile/oak accent, and the Wood renovation project supports its color cue. Neither source establishes an exact floor plan or these interior objects' campus coordinates. Dining Court has schematic serving counter and tables; no actual dining floor plan was located. Interior objects are explicitly tagged `SCHEMATIC INTERIOR (not a surveyed floor plan)` and `SCHEMATIC DINING INTERIOR (not a surveyed floor plan)`.

Preview files: [overall exterior](previews/windsor_halls_overview.png), [Warren frontage](previews/warren_frontage.png), [Wood frontage](previews/wood_frontage.png), [Vawter frontage](previews/vawter_frontage.png), [residential room/lounge schematic](previews/windsor_schematic_interior.png), and [Dining Court schematic](previews/windsor_dining_schematic.png).
