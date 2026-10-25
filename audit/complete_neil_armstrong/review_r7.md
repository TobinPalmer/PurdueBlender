# Neil Armstrong Hall — R7 review candidate

## Exterior massing

R7 retains the same R5 GIS footprint masks and X/Y vertices. Instead of a single flat median-height cap on each coarse envelope, the saved caps follow smoothed local medians from the registered 5-ft normalized-height raster. Each top vertex uses a 5x5 same-band median blended 35% local and 65% R5 zone median to suppress cell-scale noise. The low, middle, and high surfaces span 15.25–16.52m, 19.06–19.61m, and 21.50–21.60m respectively. The raster's two cells above 22m remain excluded from roof shaping, so they do not become unsupported towers. Red ACM is applied across the upward roof faces of all three height zones; vertical envelope sides remain brick.

This gives the broad wing masses a joined roof/wing reading while keeping their coarse plan envelope. It does not recover roof slope, the exact wall line beneath the overhang, the truss/cantilever profile, or architectural details. The resulting caps are low-resolution generalized surfaces, not measured planes.

## Atrium context

The new feature render places both modeled bridge levels within the existing curved curtain glazing, roof glazing, and roof trusses. Three central curtain bays are temporarily hidden as a camera reveal while the side glazing remains visible. Display materials, a neutral staging plane, and object visibility are temporary render setup only; the plane is not a floor-plan claim. The view makes the two bridges legible in an enclosed spatial context, but it does not certify the bridge termini or circulation route.

FRP documents two bridge levels with glass rails and three stairs. Available FRP images and Purdue's 360-tour listing do not provide a local-frame registered plan; the modeled bridge endpoints and stair placement remain schematic. R7 does not add or connect stairs. The render-only staging plane is not a surveyed atrium floor outline.

## Review files

- Exterior silhouette: [renders_r7/exterior_lidar_silhouette_r7.png](renders_r7/exterior_lidar_silhouette_r7.png)
- Atrium enclosure view: [renders_r7/atrium_bridges_enclosure_r7.png](renders_r7/atrium_bridges_enclosure_r7.png)
- Final smoothed source samples: [roof_surface_samples_r7_smooth.json](roof_surface_samples_r7_smooth.json)
- Change/source record: [evidence_r7.json](evidence_r7.json)
- Reopen validation: [validation_r7.json](validation_r7.json)

The asset keeps the original local frame and master marker. Registered GIS/LiDAR support the broad wing envelope and roof-height trend. The available sources still do not support exact facade stations, roof edges, the cantilever/truss shape, or continuous interior circulation.
