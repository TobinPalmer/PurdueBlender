# Neil Armstrong Hall — R8 source revision

## Roof reconciliation

R8 removes the two large rooftop penthouse boxes and their louver skins from the R7 source. They were each about 22–24m by 12–14m, and neither footprint aligns with the two 2018 5-ft NDHM cells above 22m inside the registered Purdue GIS footprint. The two cells fall together near local X = −13.53m, Y = 5.75–7.27m.

FRP confirms that the real building includes a structural-steel mechanical penthouse, but its public project page gives no measured footprint or location. The LiDAR cells may represent a small rooftop element or classification residual; they do not justify reconstructing the penthouse. R8 leaves the feature unresolved rather than preserving two unsupported end masses or inventing a replacement.

All common R7 mesh geometry and transforms were compared against the saved R7 backup. Only the four named penthouse/louver objects were removed. The asset root and R5/R7 GIS/LiDAR envelope coordinates remain unchanged.

## New official source material

Purdue College of Engineering’s artwork guidelines include a cropped first-floor plan excerpt with room labels and stair linework. It has no north arrow, scale, or registration controls, so it is not used to reposition bridges, stairs, or other geometry. Purdue’s current building emergency plan confirms four levels: one lower level, grade, and two upper floors. The Purdue 360 tour names the atrium and second-floor skywalk, but its panoramas are not position-registered.

A geotagged 2016 Commons photo provides a clearer qualitative check of the red ACM wing roof, brick fields, and curtain glazing. Its camera pose is not known, so it cannot assign measured facade details to an exact side.

## Review files

- Source registry: [sources_r8.json](sources_r8.json)
- Geometry/source record: [evidence_r8.json](evidence_r8.json)
- LiDAR cell check: [roof_height_reconciliation_r8.json](roof_height_reconciliation_r8.json)
- Reopen validation: [validation_r8.json](validation_r8.json)
- R8 exterior views: [renders_r8](renders_r8)

## Remaining limits

The cantilevered truss profile, exact roof edges, facade stationing, and mechanical penthouse outline remain unverified. Bridges and stairs remain schematic because available floor-plan and panorama sources cannot be registered to the local GIS frame. R8 does not claim a higher story/floor count than official sources support.
